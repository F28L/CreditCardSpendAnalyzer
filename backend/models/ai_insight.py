"""AI Insight model for storing LLM-generated insights."""
from sqlalchemy import Column, String, Date, Text
import uuid
from .base import Base, TimestampMixin


class AIInsight(Base, TimestampMixin):
    """Represents an AI-generated insight about spending patterns."""

    __tablename__ = "ai_insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    insight_type = Column(
        String(50), nullable=False
    )  # 'monthly_summary', 'anomaly', 'category_breakdown'
    date_range_start = Column(Date, nullable=True)
    date_range_end = Column(Date, nullable=True)
    content = Column(Text, nullable=False)
    model_used = Column(String(50))  # e.g., 'llama3', 'gpt-4o-mini'

    def __repr__(self):
        return f"<AIInsight(id={self.id}, type={self.insight_type}, model={self.model_used})>"
