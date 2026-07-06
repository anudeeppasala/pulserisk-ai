# PulseRisk AI - Architecture

## Overview

PulseRisk AI ingests customer reviews, classifies sentiment, applies rule-based risk scoring, and surfaces analytics through a Streamlit dashboard.

## Components

- **Backend (FastAPI)**: REST API for review ingestion, classification, and analytics.
  - `routers/reviews.py` - CRUD and ingestion endpoints
  - `routers/analytics.py` - aggregate metrics endpoints
  - `services/classifier.py` - sentiment classification
  - `services/risk_rules.py` - rule-based risk scoring
  - `services/ingestion.py` - CSV / external data ingestion
- **Database**: SQLite via SQLAlchemy (swappable via `DATABASE_URL`).
- **Frontend (Streamlit)**: dashboard consuming the backend API.

## Data Flow

1. Reviews are ingested via API or CSV.
2. Each review is classified for sentiment and scored for risk.
3. Results are persisted and exposed through analytics endpoints.
4. The Streamlit dashboard visualizes trends and high-risk reviews.
