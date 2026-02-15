"""Account schemas for request/response validation."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AccountBase(BaseModel):
    """Base account schema."""

    account_name: str
    account_type: Optional[str] = None
    institution_name: Optional[str] = None
    last_four: Optional[str] = None


class AccountCreate(AccountBase):
    """Schema for creating an account."""

    plaid_account_id: str


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    account_name: Optional[str] = None
    last_sync_timestamp: Optional[datetime] = None


class AccountRead(AccountBase):
    """Schema for reading an account."""

    id: str
    plaid_account_id: str
    last_sync_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
