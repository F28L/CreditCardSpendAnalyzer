"""Transaction model for financial transactions."""
from sqlalchemy import Column, String, Float, Date, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
import uuid
from .base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """Represents a financial transaction."""

    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(
        String(255), unique=True, nullable=False, index=True
    )  # Plaid or Venmo ID
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)
    merchant_name = Column(String(255))
    description = Column(Text)
    category = Column(String(100))  # Plaid category
    source = Column(String(20), nullable=False)  # 'plaid', 'venmo', 'manual'
    is_reimbursement = Column(Boolean, default=False)
    ai_category = Column(String(100))  # LLM-generated category

    # Relationships
    account = relationship("Account", back_populates="transactions")

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_account_date", "account_id", "date"),
        Index("idx_date_desc", "date"),
        Index("idx_category", "category", "date"),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, merchant={self.merchant_name}, amount={self.amount}, date={self.date})>"
