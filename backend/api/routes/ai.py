"""AI-powered insights API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import logging

from database import get_db
from services.llm.factory import get_llm_provider
from models.transaction import Transaction
from models.ai_insight import AIInsight
from schemas.ai_insight import AIInsightRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AnalyzeRequest(BaseModel):
    """Request for AI analysis."""

    date_range_start: Optional[str] = None  # ISO date
    date_range_end: Optional[str] = None
    account_ids: Optional[List[str]] = None
    insight_type: str = "spending_analysis"


class AnalyzeResponse(BaseModel):
    """Response for AI analysis."""

    insight: str
    insight_id: str
    model_used: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_spending(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger AI analysis on transactions.
    Generates insights about spending patterns, categories, and anomalies.
    """
    try:
        # Parse dates
        start_date = (
            datetime.fromisoformat(request.date_range_start).date()
            if request.date_range_start
            else None
        )
        end_date = (
            datetime.fromisoformat(request.date_range_end).date()
            if request.date_range_end
            else None
        )

        # Build query
        query = select(Transaction)

        if start_date:
            query = query.where(Transaction.date >= start_date)
        if end_date:
            query = query.where(Transaction.date <= end_date)
        if request.account_ids:
            query = query.where(Transaction.account_id.in_(request.account_ids))

        # Fetch transactions
        result = await db.execute(query)
        transactions = result.scalars().all()

        if not transactions:
            raise HTTPException(
                status_code=404, detail="No transactions found for the specified criteria"
            )

        # Convert to dict format for LLM
        txn_data = [
            {
                "date": str(txn.date),
                "merchant_name": txn.merchant_name,
                "amount": txn.amount,
                "category": txn.category,
                "description": txn.description,
            }
            for txn in transactions
        ]

        # Get LLM provider
        llm = get_llm_provider()

        # Generate insight based on type
        if request.insight_type == "spending_analysis":
            prompt = """Analyze these transactions and provide:
1. Top 3 spending categories with amounts
2. Any unusual spending patterns or anomalies
3. One actionable recommendation to reduce spending"""
        elif request.insight_type == "category_breakdown":
            prompt = "Categorize and summarize spending by category. Provide a clear breakdown with percentages."
        elif request.insight_type == "reimbursement_analysis":
            prompt = "Identify any transactions that might be reimbursements or refunds. List them with confidence scores."
        else:
            prompt = "Provide a comprehensive spending analysis."

        insight_text = await llm.generate_insight(prompt, txn_data)

        # Save insight to database
        model_name = (
            llm.model if hasattr(llm, "model") else llm.__class__.__name__
        )
        ai_insight = AIInsight(
            insight_type=request.insight_type,
            date_range_start=start_date,
            date_range_end=end_date,
            content=insight_text,
            model_used=model_name,
        )
        db.add(ai_insight)
        await db.commit()
        await db.refresh(ai_insight)

        return AnalyzeResponse(
            insight=insight_text,
            insight_id=ai_insight.id,
            model_used=model_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing spending: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", response_model=List[AIInsightRead])
async def get_insights(
    limit: int = 10,
    insight_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve stored AI insights.
    Optionally filter by insight type.
    """
    try:
        query = select(AIInsight).order_by(AIInsight.created_at.desc()).limit(limit)

        if insight_type:
            query = query.where(AIInsight.insight_type == insight_type)

        result = await db.execute(query)
        insights = result.scalars().all()

        return insights

    except Exception as e:
        logger.error(f"Error fetching insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categorize-transaction/{transaction_id}")
async def categorize_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Use AI to categorize a specific transaction.
    Updates the ai_category field.
    """
    try:
        # Get transaction
        result = await db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Get LLM provider
        llm = get_llm_provider()

        # Categorize
        txn_data = {
            "merchant_name": transaction.merchant_name,
            "amount": transaction.amount,
            "description": transaction.description,
        }
        category = await llm.categorize_transaction(txn_data)

        # Update transaction
        transaction.ai_category = category
        await db.commit()

        return {"transaction_id": transaction_id, "ai_category": category}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error categorizing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-categorize")
async def bulk_categorize_transactions(
    background_tasks: BackgroundTasks,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger bulk AI categorization for uncategorized transactions.
    Runs in background to avoid timeout.
    """
    try:
        # Get uncategorized transactions
        result = await db.execute(
            select(Transaction)
            .where(Transaction.ai_category == None)
            .limit(limit)
        )
        transactions = result.scalars().all()

        if not transactions:
            return {"message": "No uncategorized transactions found", "count": 0}

        # Run in background
        background_tasks.add_task(
            categorize_transactions_background, [txn.id for txn in transactions], db
        )

        return {
            "message": "Bulk categorization started",
            "count": len(transactions),
        }

    except Exception as e:
        logger.error(f"Error in bulk categorization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def categorize_transactions_background(
    transaction_ids: List[str],
    db: AsyncSession,
):
    """Background task to categorize transactions."""
    try:
        llm = get_llm_provider()

        for txn_id in transaction_ids:
            result = await db.execute(
                select(Transaction).where(Transaction.id == txn_id)
            )
            transaction = result.scalar_one_or_none()

            if not transaction:
                continue

            txn_data = {
                "merchant_name": transaction.merchant_name,
                "amount": transaction.amount,
                "description": transaction.description,
            }

            try:
                category = await llm.categorize_transaction(txn_data)
                transaction.ai_category = category
            except Exception as e:
                logger.error(f"Error categorizing transaction {txn_id}: {e}")
                continue

        await db.commit()
        logger.info(f"Categorized {len(transaction_ids)} transactions")

    except Exception as e:
        logger.error(f"Background categorization failed: {e}")
        await db.rollback()
