"""AI Insight model for storing LLM-generated insights."""
from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from .base import Base, TimestampMixin


class AIInsight(Base, TimestampMixin):
    """Represents an AI-generated insight about spending patterns."""

    __tablename__ = "ai_insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    insight_type = Column(
        String(50), nullable=False
    )  # 'monthly_summary', 'anomaly', 'category_breakdown'
    date_range_start = Column(Date, nullable=True)
    date_range_end = Column(Date, nullable=True)
    content = Column(Text, nullable=False)
    model_used = Column(String(50))  # e.g., 'llama3', 'gpt-4o-mini'

    # Relationships
    user = relationship("User", back_populates="ai_insights")

    def __repr__(self):
        return f"<AIInsight(id={self.id}, type={self.insight_type}, model={self.model_used})>"
