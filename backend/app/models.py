"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
