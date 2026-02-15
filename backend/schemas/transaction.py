"""Transaction schemas for request/response validation."""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class TransactionBase(BaseModel):
    """Base transaction schema."""

    amount: float
    date: date
    merchant_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_reimbursement: bool = False


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    external_id: str
    account_id: Optional[str] = None
    source: str  # 'plaid', 'venmo', 'manual'


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    category: Optional[str] = None
    is_reimbursement: Optional[bool] = None
    ai_category: Optional[str] = None


class TransactionRead(TransactionBase):
    """Schema for reading a transaction."""

    id: str
    external_id: str
    account_id: Optional[str] = None
    source: str
    ai_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
