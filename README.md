# PulseRisk AI

PulseRisk AI is a Voice-of-Customer Risk Intelligence platform that converts customer feedback into actionable risk signals, severity insights, and owner-team routing.

## What it does

PulseRisk AI analyzes app reviews, support tickets, survey feedback, and customer comments to identify recurring product issues, operational risks, customer pain points, and high-severity complaint patterns.

## Version 1 Features

- Upload customer feedback CSV files
- Classify comments by issue category
- Detect sentiment and severity
- Identify risk type
- Route issues to owner teams
- Show executive-style dashboard
- Highlight high-risk comments

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Rule-based classification engine

## Sample Use Case

A company receives hundreds of customer comments across app stores and support channels. PulseRisk AI groups those comments into categories like authentication issues, app reliability, customer support problems, document access issues, and security concerns, then routes them to the right owner team.

## Run Locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
streamlit run frontend/streamlit_app.py