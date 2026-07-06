# PulseRisk AI

Customer review risk intelligence: ingest reviews, classify sentiment, score risk, and visualize insights.

## Structure

- `backend/` - FastAPI service (ingestion, classification, analytics)
- `frontend/` - Streamlit dashboard
- `docs/` - architecture notes and demo script

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

### Frontend

```bash
pip install streamlit
streamlit run frontend/streamlit_app.py
```

Dashboard at http://localhost:8501

### Docker

```bash
docker-compose up
```
