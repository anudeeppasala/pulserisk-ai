from pydantic import BaseModel, Field
from typing import Optional


class CommentClassificationRequest(BaseModel):
    comment_text: str = Field(..., description="Customer feedback text to classify.")
    rating: Optional[int] = Field(None, description="Optional customer rating, usually 1 to 5.")


class CommentClassificationResponse(BaseModel):
    category: str
    sub_category: str
    sentiment: str
    severity: str
    risk_type: str
    owner_team: str
    recommended_action: str
    summary: str