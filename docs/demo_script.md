# PulseRisk AI - Demo Script

## Setup

1. Start the stack: `docker-compose up` (or run backend and frontend locally).
2. Backend API docs: http://localhost:8000/docs
3. Dashboard: http://localhost:8501

## Demo Flow

1. **Ingest sample data** - load `sample_comments.csv` via the ingestion endpoint.
2. **Show classification** - submit a new review and show sentiment + risk score.
3. **Analytics** - open the dashboard and walk through aggregate risk metrics.
4. **High-risk alerting** - highlight reviews flagged as high risk.
