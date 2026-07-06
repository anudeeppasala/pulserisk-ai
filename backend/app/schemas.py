"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel


class ReviewBase(BaseModel):
    text: str
    rating: int | None = None


class ReviewCreate(ReviewBase):
    pass


class ReviewOut(ReviewBase):
    id: int
    sentiment: str | None = None
    risk_score: float | None = None
    risk_level: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
