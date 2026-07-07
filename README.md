# PulseRisk AI

PulseRisk AI is an Enterprise Voice-of-Customer Risk Intelligence platform that converts unstructured customer feedback into actionable product, operations, and risk insights.

It ingests customer comments, classifies issue categories, detects severity, identifies risk types, groups recurring issues, suggests root causes, generates internal action tickets, creates internal alerts, stores results in SQLite, tracks status changes, and produces executive reports.

## Current Version

### PulseRisk AI V3 — Enterprise Workflow + Safe Review Ingestion Layer

V3 turns PulseRisk AI from a dashboard into a self-contained enterprise workflow system.

## Features

- CSV ingestion
- Mock Google Play review connector
- Mock App Store review connector
- Normalized review ingestion layer
- Rule-based classification
- Optional OpenAI classifier with safe fallback
- Sentiment detection
- Severity scoring
- Risk type detection
- Owner-team routing
- Issue clustering
- Root-cause suggestions
- Product version impact analysis
- Spike detection
- Internal action tickets
- Internal alert center
- SQLite persistence
- Ticket status workflow
- Alert status workflow
- Audit trail
- Executive report generation
- FastAPI backend
- Streamlit executive dashboard

## Why Mock Store Connectors?

Google Play and App Store review APIs usually require developer or app-owner credentials. This project avoids risky public scraping. Instead, it uses connector interfaces and mock normalized data to demonstrate production-ready ingestion architecture.

In production:

```text
Google Play Developer API / App Store Connect API
        ↓
PulseRisk ingestion connector
        ↓
Normalized review model
        ↓
Database
        ↓
Classification + clustering
        ↓
Tickets + alerts + reports
```

## Tech Stack

- Python
- Streamlit
- FastAPI
- SQLite
- Pandas
- Plotly
- Pydantic
- OpenAI-ready classifier

## Project Structure

```text
pulserisk-ai/
│
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       ├── storage.py
│       ├── data/
│       │   └── sample_comments.csv
│       ├── ingestion/
│       │   ├── normalized_review.py
│       │   ├── csv_ingestion.py
│       │   ├── google_play_connector.py
│       │   └── app_store_connector.py
│       └── services/
│           ├── action_tickets.py
│           ├── ai_classifier.py
│           ├── clustering.py
│           └── risk_rules.py
│
├── frontend/
│   └── streamlit_app.py
│
├── docs/
│   └── demo_script.md
│
├── README.md
├── .gitignore
└── docker-compose.yml
```

## Run Streamlit Dashboard

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
streamlit run frontend/streamlit_app.py
```

## Run FastAPI Backend

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Optional AI Classifier

The app works without any API key.

To enable OpenAI classification:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"
streamlit run frontend/streamlit_app.py
```

Then enable **Use AI classifier** in the Streamlit sidebar.

## Product Vision

PulseRisk AI is designed as an enterprise operating layer for customer feedback intelligence.

Future improvements:

- Real Google Play Developer API integration
- Real App Store Connect API integration
- PostgreSQL instead of SQLite
- Embedding-based semantic clustering
- Real Jira integration
- Slack or Teams alerting
- Role-based authentication
- PDF reports
- Scheduled ingestion jobs