# PulseRisk AI

PulseRisk AI is a Voice-of-Customer Risk Intelligence platform that converts unstructured customer feedback into actionable product, operations, and risk insights.

Companies receive customer feedback from many places: app reviews, support tickets, surveys, call transcripts, and social comments. Most of this feedback is unstructured and difficult to analyze manually. PulseRisk AI helps teams classify comments, detect severity, identify risk types, route issues to owner teams, group recurring issues, suggest root causes, generate action tickets, and visualize customer pain points in an executive-style dashboard.

## Version 2

Version 2 expands the MVP from simple classification into root-cause and action intelligence.

### V2 Features

- Upload customer feedback CSV files
- Use sample customer feedback data
- Rule-based classification with AI-ready optional classifier
- Classify comments by issue category
- Detect sentiment
- Assign severity level
- Identify risk type
- Route issues to owner teams
- Recommend next actions
- Filter by company, product, category, severity, sentiment, and risk type
- Executive dashboard
- Issue clustering
- Root-cause suggestions
- Product version impact detection
- Simple spike detection
- Jira-style action ticket generation
- Download classified comments as CSV
- Download action tickets as CSV
- FastAPI backend with classification and insight endpoints

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
- OpenAI-ready classifier
- Rule-based fallback classifier

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

## Run the Streamlit Dashboard

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
streamlit run frontend/streamlit_app.py
```

## Run the FastAPI Backend

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

The app works without any API key using the transparent rule-based classifier.

To enable the OpenAI classifier:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"
streamlit run frontend/streamlit_app.py
```

Then enable **Use AI classifier** in the Streamlit sidebar.

## Sample API Request

```bash
curl -X POST "http://127.0.0.1:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"comment_text": "The app keeps crashing after the latest update.", "rating": 1, "use_ai": false}'
```

## CSV Format

Uploaded CSV files should include:

```text
source
company
product_name
rating
comment_text
comment_date
product_version
```

## Product Vision

The long-term vision for PulseRisk AI is to become an enterprise feedback intelligence system that can analyze reviews, support tickets, surveys, and call transcripts to detect customer pain patterns, operational risks, root causes, churn signals, and product issues.

Future versions will include:

- App Store and Google Play review ingestion
- Embedding-based issue clustering
- PostgreSQL storage
- Jira and Slack integration
- Role-based dashboards
- PDF executive reports
- Authentication and multi-user support