from typing import Optional

from pydantic import BaseModel, Field


class CommentClassificationRequest(BaseModel):
    comment_text: str = Field(..., description="Customer feedback text to classify.")
    rating: Optional[int] = Field(None, description="Optional customer rating, usually 1 to 5.")
    use_ai: bool = Field(False, description="Use AI classifier if OPENAI_API_KEY is available.")


class CommentClassificationResponse(BaseModel):
    category: str
    sub_category: str
    sentiment: str
    severity: str
    risk_type: str
    owner_team: str
    recommended_action: str
    summary: str
    classification_method: str


class BatchCommentItem(BaseModel):
    source: Optional[str] = None
    company: str
    product_name: str
    rating: Optional[int] = None
    comment_text: str
    comment_date: Optional[str] = None
    product_version: Optional[str] = None


class BatchClassificationRequest(BaseModel):
    comments: list[BatchCommentItem]
    use_ai: bool = False


class TicketStatusUpdateRequest(BaseModel):
    ticket_id: str
    new_status: str
    note: Optional[str] = ""


class AlertStatusUpdateRequest(BaseModel):
    alert_id: int
    new_status: str
    note: Optional[str] = ""