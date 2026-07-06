import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from app.services.risk_rules import classify_comment_rule_based


st.set_page_config(page_title="PulseRisk AI", layout="wide")

st.title("PulseRisk AI")
st.caption("Voice-of-Customer Risk Intelligence Platform")

uploaded_file = st.file_uploader("Upload customer feedback CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    sample_path = ROOT / "backend" / "app" / "data" / "sample_comments.csv"
    df = pd.read_csv(sample_path)

records = []

for _, row in df.iterrows():
    rating = int(row["rating"]) if not pd.isna(row["rating"]) else None
    result = classify_comment_rule_based(str(row["comment_text"]), rating)

    records.append({
        **row.to_dict(),
        **result,
    })

classified_df = pd.DataFrame(records)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Comments", len(classified_df))
col2.metric("Negative Comments", len(classified_df[classified_df["sentiment"] == "Negative"]))
col3.metric("High / Critical Issues", len(classified_df[classified_df["severity"].isin(["High", "Critical"])]))
col4.metric("Companies", classified_df["company"].nunique())

st.subheader("Top Issue Categories")
category_counts = classified_df["category"].value_counts().reset_index()
category_counts.columns = ["category", "count"]
st.plotly_chart(
    px.bar(category_counts, x="category", y="count", title="Issue Categories"),
    use_container_width=True,
)

st.subheader("Risk Type Breakdown")
risk_counts = classified_df["risk_type"].value_counts().reset_index()
risk_counts.columns = ["risk_type", "count"]
st.plotly_chart(
    px.pie(risk_counts, names="risk_type", values="count", title="Risk Types"),
    use_container_width=True,
)

st.subheader("Owner Team Routing")
team_counts = classified_df["owner_team"].value_counts().reset_index()
team_counts.columns = ["owner_team", "count"]
st.plotly_chart(
    px.bar(team_counts, x="owner_team", y="count", title="Owner Teams"),
    use_container_width=True,
)

st.subheader("High-Risk Comments")
high_risk_df = classified_df[classified_df["severity"].isin(["High", "Critical"])]
st.dataframe(
    high_risk_df[
        [
            "company",
            "product_name",
            "rating",
            "comment_text",
            "category",
            "severity",
            "risk_type",
            "owner_team",
            "recommended_action",
        ]
    ],
    use_container_width=True,
)

st.subheader("All Classified Comments")
st.dataframe(classified_df, use_container_width=True)