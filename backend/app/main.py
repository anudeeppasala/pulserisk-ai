from fastapi import FastAPI

from .schemas import CommentClassificationRequest, CommentClassificationResponse
from .services.risk_rules import classify_comment_rule_based

app = FastAPI(
    title="PulseRisk AI API",
    description="Voice-of-Customer Risk Intelligence API for classifying customer feedback into risk signals.",
    version="1.0.0",
)


@app.get("/")
def root() -> dict:
    return {
        "app": "PulseRisk AI",
        "version": "1.0.0",
        "status": "running",
        "message": "Voice-of-Customer Risk Intelligence API",
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
    }


@app.post("/classify", response_model=CommentClassificationResponse)
def classify_comment(request: CommentClassificationRequest) -> dict:
    return classify_comment_rule_based(
        text=request.comment_text,
        rating=request.rating,
    )