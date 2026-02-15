"""AI Insight schemas for request/response validation."""
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class AIInsightBase(BaseModel):
    """Base AI insight schema."""

    insight_type: str
    content: str
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


class AIInsightCreate(AIInsightBase):
    """Schema for creating an AI insight."""

    model_used: Optional[str] = None


class AIInsightRead(AIInsightBase):
    """Schema for reading an AI insight."""

    id: str
    model_used: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
