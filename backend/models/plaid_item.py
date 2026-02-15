"""Plaid Item model for storing Plaid access tokens."""
from sqlalchemy import Column, String
import uuid
from .base import Base, TimestampMixin


class PlaidItem(Base, TimestampMixin):
    """Represents a Plaid Item (a user's connection to a financial institution)."""

    __tablename__ = "plaid_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    access_token = Column(String(255), nullable=False)
    item_id = Column(String(255), unique=True, nullable=False, index=True)
    institution_id = Column(String(255))

    def __repr__(self):
        return f"<PlaidItem(id={self.id}, item_id={self.item_id}, institution={self.institution_id})>"
