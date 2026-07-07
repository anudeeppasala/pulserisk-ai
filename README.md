# PulseRisk AI

PulseRisk AI is a Voice-of-Customer Risk Intelligence platform that converts unstructured customer feedback into actionable product, operations, and risk insights.

Companies receive customer feedback from many places: app reviews, support tickets, surveys, call transcripts, and social comments. Most of this feedback is unstructured and difficult to analyze manually. PulseRisk AI helps teams classify comments, detect severity, identify risk types, route issues to owner teams, and visualize customer pain points in an executive-style dashboard.

## Version 1

Version 1 is a local dashboard MVP with a reusable classification engine.

### Features

- Upload customer feedback CSV files
- Use sample customer feedback data
- Classify comments by issue category
- Detect sentiment
- Assign severity level
- Identify risk type
- Route issues to owner teams
- Recommend next actions
- Filter by company, product, category, severity, sentiment, and risk type
- Display executive summary
- Visualize issue categories, severity, risk types, and owner teams
- Highlight high-risk comments
- Download classified results as CSV
- Lightweight FastAPI backend with health and classification endpoints

## Example Categories

PulseRisk AI can classify comments into categories such as:

- Authentication / Login
- App Reliability
- Customer Support
- Documents
- Billing / Payments
- Fraud / Security Concern
- Feature Request
- General Feedback

## Tech Stack

- Python
- Streamlit
- FastAPI
- Pandas
- Plotly
- Pydantic
- Rule-based classification engine

## Project Structure

```text
pulserisk-ai/
│
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       ├── data/
│       │   └── sample_comments.csv
│       └── services/
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