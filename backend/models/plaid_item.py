"""Plaid Item model for storing Plaid access tokens."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from .base import Base, TimestampMixin


class PlaidItem(Base, TimestampMixin):
    """Represents a Plaid Item (a user's connection to a financial institution)."""

    __tablename__ = "plaid_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    access_token = Column(String(255), nullable=False)
    item_id = Column(String(255), unique=True, nullable=False, index=True)
    institution_id = Column(String(255))

    # Relationships
    user = relationship("User", back_populates="plaid_items")

    def __repr__(self):
        return f"<PlaidItem(id={self.id}, item_id={self.item_id}, institution={self.institution_id})>"
