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


<img width="1651" height="700" alt="Screenshot 2026-07-06 at 12 30 21 PM" src="https://github.com/user-attachments/assets/a8da1a85-3dd8-4dd8-8234-6f5d00a1517c" />
<img width="1643" height="832" alt="Screenshot 2026-07-06 at 12 30 03 PM" src="https://github.com/user-attachments/assets/c93dbbdf-1c91-44d8-b8e3-014f15290ae5" />
<img width="1619" height="562" alt="Screenshot 2026-07-06 at 12 29 47 PM" src="https://github.com/user-attachments/assets/af47ac31-4445-43e2-b0df-c98c8116585b" />
<img width="862" height="458" alt="Screenshot 2026-07-06 at 12 29 38 PM" src="https://github.com/user-attachments/assets/585b5273-e044-4564-8ddc-7e8aa698b013" />
