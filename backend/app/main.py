import pandas as pd
from fastapi import FastAPI

from app.schemas import (
    BatchClassificationRequest,
    CommentClassificationRequest,
    CommentClassificationResponse,
)
from app.services.action_tickets import generate_action_tickets
from app.services.ai_classifier import classify_comment_ai_ready
from app.services.clustering import build_issue_clusters, detect_spikes, detect_version_impact

app = FastAPI(
    title="PulseRisk AI API",
    description="Voice-of-Customer Risk Intelligence API for classifying feedback, detecting issue clusters, and generating action tickets.",
    version="2.0.0",
)


@app.get("/")
def root() -> dict:
    return {
        "app": "PulseRisk AI",
        "version": "2.0.0",
        "status": "running",
        "message": "Voice-of-Customer Risk Intelligence API",
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "version": "2.0.0",
    }


@app.post("/classify", response_model=CommentClassificationResponse)
def classify_comment(request: CommentClassificationRequest) -> dict:
    return classify_comment_ai_ready(
        text=request.comment_text,
        rating=request.rating,
        use_ai=request.use_ai,
    )


@app.post("/batch-classify")
def batch_classify(request: BatchClassificationRequest) -> dict:
    records = []

    for item in request.comments:
        result = classify_comment_ai_ready(
            text=item.comment_text,
            rating=item.rating,
            use_ai=request.use_ai,
        )

        records.append(
            {
                **item.model_dump(),
                **result,
            }
        )

    return {
        "count": len(records),
        "results": records,
    }


@app.post("/clusters")
def generate_clusters(request: BatchClassificationRequest) -> dict:
    records = []

    for item in request.comments:
        result = classify_comment_ai_ready(
            text=item.comment_text,
            rating=item.rating,
            use_ai=request.use_ai,
        )

        records.append(
            {
                **item.model_dump(),
                **result,
            }
        )

    classified_df = pd.DataFrame(records)
    clusters_df = build_issue_clusters(classified_df)

    return {
        "count": len(clusters_df),
        "clusters": clusters_df.to_dict(orient="records"),
    }


@app.post("/tickets")
def generate_tickets(request: BatchClassificationRequest) -> dict:
    records = []

    for item in request.comments:
        result = classify_comment_ai_ready(
            text=item.comment_text,
            rating=item.rating,
            use_ai=request.use_ai,
        )

        records.append(
            {
                **item.model_dump(),
                **result,
            }
        )

    classified_df = pd.DataFrame(records)
    clusters_df = build_issue_clusters(classified_df)
    tickets_df = generate_action_tickets(clusters_df)

    return {
        "count": len(tickets_df),
        "tickets": tickets_df.to_dict(orient="records"),
    }


@app.post("/insights")
def generate_insights(request: BatchClassificationRequest) -> dict:
    records = []

    for item in request.comments:
        result = classify_comment_ai_ready(
            text=item.comment_text,
            rating=item.rating,
            use_ai=request.use_ai,
        )

        records.append(
            {
                **item.model_dump(),
                **result,
            }
        )

    classified_df = pd.DataFrame(records)
    clusters_df = build_issue_clusters(classified_df)
    tickets_df = generate_action_tickets(clusters_df)
    spikes_df = detect_spikes(classified_df)
    version_impact_df = detect_version_impact(classified_df)

    return {
        "classified_count": len(classified_df),
        "cluster_count": len(clusters_df),
        "ticket_count": len(tickets_df),
        "spike_count": len(spikes_df),
        "classified_comments": classified_df.to_dict(orient="records"),
        "clusters": clusters_df.to_dict(orient="records"),
        "tickets": tickets_df.to_dict(orient="records"),
        "spikes": spikes_df.to_dict(orient="records"),
        "version_impact": version_impact_df.to_dict(orient="records"),
    }