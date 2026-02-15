"""Analytics API routes for spending data."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from collections import defaultdict
import logging

from database import get_db
from models.transaction import Transaction
from models.account import Account
from models.user import User
from api.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class SpendingByCard(BaseModel):
    """Spending aggregated by card/account."""

    account_id: str
    account_name: str
    institution_name: Optional[str]
    total_spent: float
    transaction_count: int


class SpendingOverTime(BaseModel):
    """Spending over time data point."""

    date: str
    amount: float
    transaction_count: int


class CategorySpending(BaseModel):
    """Spending by category."""

    category: str
    amount: float
    percentage: float
    transaction_count: int


class ReimbursementItem(BaseModel):
    """Reimbursement transaction."""

    transaction_id: str
    date: str
    merchant_name: str
    amount: float
    description: Optional[str]
    confidence: Optional[float] = None


@router.get("/spending-by-card", response_model=List[SpendingByCard])
async def get_spending_by_card(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get spending aggregated by credit card/account for the current user.
    Optionally filter by date range.
    """
    try:
        # Build query with user filter via Account join
        query = (
            select(
                Transaction.account_id,
                func.sum(Transaction.amount).label("total_spent"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(Transaction.account_id != None)
            .where(Account.user_id == current_user.id)
            .group_by(Transaction.account_id)
        )

        # Apply date filters
        if start_date:
            query = query.where(
                Transaction.date >= datetime.fromisoformat(start_date).date()
            )
        if end_date:
            query = query.where(
                Transaction.date <= datetime.fromisoformat(end_date).date()
            )

        result = await db.execute(query)
        spending_data = result.all()

        # Get account details (filter by user_id)
        account_result = await db.execute(
            select(Account).where(Account.user_id == current_user.id)
        )
        accounts = {acc.id: acc for acc in account_result.scalars()}

        # Format response
        response = []
        for account_id, total, count in spending_data:
            account = accounts.get(account_id)
            if account:
                response.append(
                    SpendingByCard(
                        account_id=account_id,
                        account_name=account.account_name,
                        institution_name=account.institution_name,
                        total_spent=float(total),
                        transaction_count=count,
                    )
                )

        return response

    except Exception as e:
        logger.error(f"Error getting spending by card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spending-over-time", response_model=List[SpendingOverTime])
async def get_spending_over_time(
    granularity: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    account_ids: Optional[str] = Query(None),  # Comma-separated
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get spending over time with configurable granularity for the current user.
    Returns aggregated data by day, week, or month.
    """
    try:
        # Build query with user filter via Account join
        query = select(Transaction).join(Account, Transaction.account_id == Account.id).where(Account.user_id == current_user.id)

        # Apply filters
        if start_date:
            query = query.where(
                Transaction.date >= datetime.fromisoformat(start_date).date()
            )
        if end_date:
            query = query.where(
                Transaction.date <= datetime.fromisoformat(end_date).date()
            )
        if account_ids:
            acc_list = [aid.strip() for aid in account_ids.split(",")]
            query = query.where(Transaction.account_id.in_(acc_list))

        result = await db.execute(query.order_by(Transaction.date))
        transactions = result.scalars().all()

        # Aggregate by granularity
        spending_dict: Dict[str, Dict] = defaultdict(lambda: {"amount": 0.0, "count": 0})

        for txn in transactions:
            if granularity == "daily":
                key = str(txn.date)
            elif granularity == "weekly":
                # Get start of week (Monday)
                start_of_week = txn.date - timedelta(days=txn.date.weekday())
                key = str(start_of_week)
            else:  # monthly
                key = txn.date.strftime("%Y-%m")

            spending_dict[key]["amount"] += txn.amount
            spending_dict[key]["count"] += 1

        # Format response
        response = [
            SpendingOverTime(
                date=date_key,
                amount=data["amount"],
                transaction_count=data["count"],
            )
            for date_key, data in sorted(spending_dict.items())
        ]

        return response

    except Exception as e:
        logger.error(f"Error getting spending over time: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[CategorySpending])
async def get_category_breakdown(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    use_ai_category: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get spending breakdown by category for the current user.
    Can use either Plaid categories or AI-generated categories.
    """
    try:
        # Determine which category field to use
        category_field = Transaction.ai_category if use_ai_category else Transaction.category

        # Build query with user filter via Account join
        query = (
            select(
                category_field.label("category"),
                func.sum(Transaction.amount).label("amount"),
                func.count(Transaction.id).label("count"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(category_field != None)
            .where(Account.user_id == current_user.id)
            .group_by(category_field)
        )

        # Apply date filters
        if start_date:
            query = query.where(
                Transaction.date >= datetime.fromisoformat(start_date).date()
            )
        if end_date:
            query = query.where(
                Transaction.date <= datetime.fromisoformat(end_date).date()
            )

        result = await db.execute(query)
        category_data = result.all()

        # Calculate total for percentages
        total_amount = sum(amount for _, amount, _ in category_data)

        # Format response
        response = [
            CategorySpending(
                category=category or "Uncategorized",
                amount=float(amount),
                percentage=round((float(amount) / total_amount * 100), 2)
                if total_amount > 0
                else 0.0,
                transaction_count=count,
            )
            for category, amount, count in category_data
        ]

        # Sort by amount descending
        response.sort(key=lambda x: x.amount, reverse=True)

        return response

    except Exception as e:
        logger.error(f"Error getting category breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reimbursements", response_model=List[ReimbursementItem])
async def get_reimbursements(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get transactions marked as reimbursements for the current user.
    Includes both manually marked and AI-detected reimbursements.
    """
    try:
        # Build query with user filter via Account join
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Transaction.is_reimbursement == True)
            .where(Account.user_id == current_user.id)
        )

        # Apply date filters
        if start_date:
            query = query.where(
                Transaction.date >= datetime.fromisoformat(start_date).date()
            )
        if end_date:
            query = query.where(
                Transaction.date <= datetime.fromisoformat(end_date).date()
            )

        result = await db.execute(query.order_by(Transaction.date.desc()))
        reimbursements = result.scalars().all()

        # Format response
        response = [
            ReimbursementItem(
                transaction_id=txn.id,
                date=str(txn.date),
                merchant_name=txn.merchant_name or "Unknown",
                amount=txn.amount,
                description=txn.description,
            )
            for txn in reimbursements
        ]

        return response

    except Exception as e:
        logger.error(f"Error getting reimbursements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_spending_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get overall spending summary with key metrics for the current user.
    """
    try:
        # Build base query with user filter via Account join
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == current_user.id)
        )

        # Apply date filters
        if start_date:
            query = query.where(
                Transaction.date >= datetime.fromisoformat(start_date).date()
            )
        if end_date:
            query = query.where(
                Transaction.date <= datetime.fromisoformat(end_date).date()
            )

        result = await db.execute(query)
        transactions = result.scalars().all()

        if not transactions:
            return {
                "total_spent": 0.0,
                "transaction_count": 0,
                "average_transaction": 0.0,
                "reimbursements_total": 0.0,
                "unique_merchants": 0,
            }

        # Calculate metrics
        total_spent = sum(txn.amount for txn in transactions)
        transaction_count = len(transactions)
        reimbursements_total = sum(
            txn.amount for txn in transactions if txn.is_reimbursement
        )
        unique_merchants = len(
            set(txn.merchant_name for txn in transactions if txn.merchant_name)
        )

        return {
            "total_spent": round(total_spent, 2),
            "transaction_count": transaction_count,
            "average_transaction": round(total_spent / transaction_count, 2)
            if transaction_count > 0
            else 0.0,
            "reimbursements_total": round(reimbursements_total, 2),
            "unique_merchants": unique_merchants,
            "date_range": {
                "start": str(min(txn.date for txn in transactions)),
                "end": str(max(txn.date for txn in transactions)),
            },
        }

    except Exception as e:
        logger.error(f"Error getting spending summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
