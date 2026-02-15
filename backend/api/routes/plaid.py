"""Plaid API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from database import get_db
from services.plaid_service import PlaidService
from models.plaid_item import PlaidItem
from models.account import Account
from models.transaction import Transaction
from models.user import User
from api.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plaid", tags=["plaid"])


class LinkTokenResponse(BaseModel):
    """Response for link token creation."""

    link_token: str


class ExchangeTokenRequest(BaseModel):
    """Request for exchanging public token."""

    public_token: str


class ExchangeTokenResponse(BaseModel):
    """Response for token exchange."""

    success: bool
    item_id: str
    accounts_synced: int


class SyncTransactionsRequest(BaseModel):
    """Request for syncing transactions."""

    item_id: str
    start_date: Optional[str] = None  # ISO format date string
    end_date: Optional[str] = None


class SyncTransactionsResponse(BaseModel):
    """Response for transaction sync."""

    success: bool
    transactions_synced: int
    message: str


@router.post("/create-link-token", response_model=LinkTokenResponse)
async def create_link_token(current_user: User = Depends(get_current_user)):
    """Create a Plaid Link token for account connection."""
    try:
        plaid_service = PlaidService()
        link_token = await plaid_service.create_link_token(user_id=current_user.id)
        return LinkTokenResponse(link_token=link_token)
    except Exception as e:
        logger.error(f"Error creating link token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exchange-public-token", response_model=ExchangeTokenResponse)
async def exchange_public_token(
    request: ExchangeTokenRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Exchange public token for access token and fetch accounts.
    This initiates the initial 24-month transaction sync in the background.
    """
    try:
        plaid_service = PlaidService()

        # Exchange token
        access_token, item_id = await plaid_service.exchange_public_token(
            request.public_token
        )

        # Save Plaid item
        plaid_item = PlaidItem(
            user_id=current_user.id,
            access_token=access_token,
            item_id=item_id,
            institution_id=await plaid_service.get_institution_name(access_token),
        )
        db.add(plaid_item)
        await db.commit()

        # Get accounts
        accounts_data = await plaid_service.get_accounts(access_token)

        # Save accounts
        for acc_data in accounts_data:
            account = Account(
                user_id=current_user.id,
                plaid_account_id=acc_data["plaid_account_id"],
                account_name=acc_data["account_name"],
                account_type=acc_data["account_type"],
                institution_name=plaid_item.institution_id,
                last_four=acc_data.get("mask"),
            )
            db.add(account)

        await db.commit()

        # Schedule background sync for 24 months
        background_tasks.add_task(
            sync_transactions_background, item_id, current_user.id, None, None, db
        )

        return ExchangeTokenResponse(
            success=True, item_id=item_id, accounts_synced=len(accounts_data)
        )

    except Exception as e:
        logger.error(f"Error exchanging token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-transactions", response_model=SyncTransactionsResponse)
async def sync_transactions(
    request: SyncTransactionsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger transaction sync for a specific item.
    Supports custom date ranges or defaults to 24 months.
    """
    try:
        # Get Plaid item (filter by user_id)
        result = await db.execute(
            select(PlaidItem).where(
                PlaidItem.item_id == request.item_id,
                PlaidItem.user_id == current_user.id,
            )
        )
        plaid_item = result.scalar_one_or_none()

        if not plaid_item:
            raise HTTPException(status_code=404, detail="Plaid item not found")

        # Parse dates if provided
        start_date = None
        end_date = None
        if request.start_date:
            start_date = datetime.fromisoformat(request.start_date)
        if request.end_date:
            end_date = datetime.fromisoformat(request.end_date)

        # Run sync in background
        background_tasks.add_task(
            sync_transactions_background,
            request.item_id,
            current_user.id,
            start_date,
            end_date,
            db,
        )

        return SyncTransactionsResponse(
            success=True,
            transactions_synced=0,  # Will be updated by background task
            message="Transaction sync started in background",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def sync_transactions_background(
    item_id: str,
    user_id: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    db: AsyncSession,
):
    """Background task to sync transactions."""
    try:
        # Get Plaid item (filter by user_id)
        result = await db.execute(
            select(PlaidItem).where(
                PlaidItem.item_id == item_id, PlaidItem.user_id == user_id
            )
        )
        plaid_item = result.scalar_one()

        plaid_service = PlaidService()

        # Fetch transactions
        transactions_data = await plaid_service.sync_transactions(
            plaid_item.access_token,
            start_date=start_date,
            end_date=end_date,
        )

        # Get account mappings (filter by user_id)
        result = await db.execute(select(Account).where(Account.user_id == user_id))
        accounts = {acc.plaid_account_id: acc.id for acc in result.scalars()}

        # Save transactions with deduplication
        new_count = 0
        for txn_data in transactions_data:
            # Check if transaction already exists
            existing = await db.execute(
                select(Transaction).where(
                    Transaction.external_id == txn_data["external_id"]
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicates

            # Create transaction
            transaction = Transaction(
                external_id=txn_data["external_id"],
                account_id=accounts.get(txn_data["plaid_account_id"]),
                amount=txn_data["amount"],
                date=txn_data["date"],
                merchant_name=txn_data["merchant_name"],
                description=txn_data["description"],
                category=txn_data["category"],
                source="plaid",
            )
            db.add(transaction)
            new_count += 1

        # Update last_sync_timestamp for all accounts (filter by user_id)
        for account_id in accounts.values():
            result = await db.execute(
                select(Account).where(Account.id == account_id, Account.user_id == user_id)
            )
            account = result.scalar_one()
            account.last_sync_timestamp = datetime.now()

        await db.commit()
        logger.info(f"Synced {new_count} new transactions for item {item_id}")

    except Exception as e:
        logger.error(f"Background sync failed: {e}")
        await db.rollback()


@router.get("/accounts")
async def get_connected_accounts(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all connected accounts for the current user."""
    result = await db.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()

    return [
        {
            "id": acc.id,
            "account_name": acc.account_name,
            "account_type": acc.account_type,
            "institution_name": acc.institution_name,
            "last_four": acc.last_four,
            "last_sync": acc.last_sync_timestamp.isoformat()
            if acc.last_sync_timestamp
            else None,
        }
        for acc in accounts
    ]
