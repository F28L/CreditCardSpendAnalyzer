"""Account model for financial accounts."""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
import uuid
from .base import Base, TimestampMixin


class Account(Base, TimestampMixin):
    """Represents a financial account (credit card, checking, savings)."""

    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plaid_account_id = Column(String(255), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50))  # 'credit', 'checking', 'savings'
    institution_name = Column(String(255))
    last_four = Column(String(4))
    last_sync_timestamp = Column(DateTime, nullable=True)

    # Relationships
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Account(id={self.id}, name={self.account_name}, type={self.account_type})>"
