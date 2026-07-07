import pandas as pd
from fastapi import FastAPI

from app.schemas import (
    AlertStatusUpdateRequest,
    BatchClassificationRequest,
    CommentClassificationRequest,
    CommentClassificationResponse,
    TicketStatusUpdateRequest,
)
from app.services.action_tickets import generate_action_tickets
from app.services.ai_classifier import classify_comment_ai_ready
from app.services.clustering import build_issue_clusters, detect_spikes, detect_version_impact
from app.storage import (
    create_alerts_from_tickets,
    fetch_action_tickets,
    fetch_alerts,
    fetch_audit_events,
    fetch_classified_comments,
    get_database_summary,
    init_db,
    save_action_tickets,
    save_classified_comments,
    update_alert_status,
    update_ticket_status,
)

app = FastAPI(
    title="PulseRisk AI API",
    description="Enterprise Voice-of-Customer Risk Intelligence API.",
    version="3.0.0",
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/")
def root() -> dict:
    return {
        "app": "PulseRisk AI",
        "version": "3.0.0",
        "status": "running",
        "message": "Enterprise Voice-of-Customer Risk Intelligence API",
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "version": "3.0.0",
    }


@app.get("/db-summary")
def database_summary() -> dict:
    return get_database_summary()


@app.post("/classify", response_model=CommentClassificationResponse)
def classify_comment(request: CommentClassificationRequest) -> dict:
    return classify_comment_ai_ready(
        text=request.comment_text,
        rating=request.rating,
        use_ai=request.use_ai,
    )


@app.post("/insights")
def generate_insights(request: BatchClassificationRequest) -> dict:
    classified_df = _classify_batch_to_dataframe(request)
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


@app.post("/persist-insights")
def persist_insights(request: BatchClassificationRequest) -> dict:
    classified_df = _classify_batch_to_dataframe(request)
    clusters_df = build_issue_clusters(classified_df)
    tickets_df = generate_action_tickets(clusters_df)

    comments_saved = save_classified_comments(classified_df)
    tickets_saved = save_action_tickets(tickets_df)
    alerts_created = create_alerts_from_tickets(tickets_df)

    return {
        "comments_saved": comments_saved,
        "tickets_saved": tickets_saved,
        "alerts_created": alerts_created,
    }


@app.get("/comments")
def get_comments() -> dict:
    df = fetch_classified_comments()
    return {
        "count": len(df),
        "comments": df.to_dict(orient="records"),
    }


@app.get("/tickets")
def get_tickets() -> dict:
    df = fetch_action_tickets()
    return {
        "count": len(df),
        "tickets": df.to_dict(orient="records"),
    }


@app.post("/tickets/status")
def change_ticket_status(request: TicketStatusUpdateRequest) -> dict:
    update_ticket_status(
        ticket_id=request.ticket_id,
        new_status=request.new_status,
        note=request.note or "",
    )

    return {
        "ticket_id": request.ticket_id,
        "new_status": request.new_status,
        "status": "updated",
    }


@app.get("/alerts")
def get_alerts() -> dict:
    df = fetch_alerts()
    return {
        "count": len(df),
        "alerts": df.to_dict(orient="records"),
    }


@app.post("/alerts/status")
def change_alert_status(request: AlertStatusUpdateRequest) -> dict:
    update_alert_status(
        alert_id=request.alert_id,
        new_status=request.new_status,
        note=request.note or "",
    )

    return {
        "alert_id": request.alert_id,
        "new_status": request.new_status,
        "status": "updated",
    }


@app.get("/audit")
def get_audit_events() -> dict:
    df = fetch_audit_events()
    return {
        "count": len(df),
        "audit_events": df.to_dict(orient="records"),
    }


def _classify_batch_to_dataframe(request: BatchClassificationRequest) -> pd.DataFrame:
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

    return pd.DataFrame(records)