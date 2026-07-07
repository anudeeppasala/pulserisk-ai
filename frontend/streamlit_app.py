import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from app.services.risk_rules import classify_comment_rule_based


st.set_page_config(
    page_title="PulseRisk AI",
    page_icon="📊",
    layout="wide",
)

st.title("📊 PulseRisk AI")

st.markdown(
    """
    **Voice-of-Customer Risk Intelligence Platform**

    Convert customer comments, app reviews, support tickets, and survey feedback into
    issue categories, sentiment, severity, risk signals, recommended actions, and owner-team routing.
    """
)

st.divider()


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    sample_path = ROOT / "backend" / "app" / "data" / "sample_comments.csv"
    return pd.read_csv(sample_path)


def validate_input_dataframe(df: pd.DataFrame) -> list[str]:
    required_columns = {
        "source",
        "company",
        "product_name",
        "rating",
        "comment_text",
        "comment_date",
        "product_version",
    }

    missing_columns = sorted(required_columns - set(df.columns))
    return missing_columns


def classify_comments(df: pd.DataFrame) -> pd.DataFrame:
    records = []

    for _, row in df.iterrows():
        rating = None

        if "rating" in row and not pd.isna(row["rating"]):
            try:
                rating = int(row["rating"])
            except ValueError:
                rating = None

        result = classify_comment_rule_based(
            text=str(row["comment_text"]),
            rating=rating,
        )

        records.append(
            {
                **row.to_dict(),
                **result,
            }
        )

    classified_df = pd.DataFrame(records)

    severity_order = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    classified_df["severity_rank"] = classified_df["severity"].map(severity_order).fillna(0)

    return classified_df


uploaded_file = st.file_uploader(
    "Upload customer feedback CSV",
    type=["csv"],
    help=(
        "CSV should include: source, company, product_name, rating, "
        "comment_text, comment_date, product_version."
    ),
)

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file)
    st.success("Uploaded customer feedback CSV successfully.")
else:
    raw_df = load_sample_data()
    st.caption("Using sample customer feedback data. Upload a CSV to analyze your own data.")

missing_columns = validate_input_dataframe(raw_df)

if missing_columns:
    st.error(
        "Your CSV is missing required columns: "
        + ", ".join(missing_columns)
        + ". Please update the file and upload again."
    )
    st.stop()

classified_df = classify_comments(raw_df)

st.sidebar.header("🔎 Filters")

companies = ["All"] + sorted(classified_df["company"].dropna().unique().tolist())
selected_company = st.sidebar.selectbox("Company", companies)

products = ["All"] + sorted(classified_df["product_name"].dropna().unique().tolist())
selected_product = st.sidebar.selectbox("Product", products)

severities = ["All", "Critical", "High", "Medium", "Low"]
selected_severity = st.sidebar.selectbox("Severity", severities)

categories = ["All"] + sorted(classified_df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

risk_types = ["All"] + sorted(classified_df["risk_type"].dropna().unique().tolist())
selected_risk_type = st.sidebar.selectbox("Risk Type", risk_types)

sentiments = ["All"] + sorted(classified_df["sentiment"].dropna().unique().tolist())
selected_sentiment = st.sidebar.selectbox("Sentiment", sentiments)

filtered_df = classified_df.copy()

if selected_company != "All":
    filtered_df = filtered_df[filtered_df["company"] == selected_company]

if selected_product != "All":
    filtered_df = filtered_df[filtered_df["product_name"] == selected_product]

if selected_severity != "All":
    filtered_df = filtered_df[filtered_df["severity"] == selected_severity]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if selected_risk_type != "All":
    filtered_df = filtered_df[filtered_df["risk_type"] == selected_risk_type]

if selected_sentiment != "All":
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]

filtered_df = filtered_df.sort_values(by="severity_rank", ascending=False)

col1, col2, col3, col4 = st.columns(4)

total_comments = len(filtered_df)
negative_comments = len(filtered_df[filtered_df["sentiment"] == "Negative"])
high_critical_issues = len(filtered_df[filtered_df["severity"].isin(["High", "Critical"])])
company_count = filtered_df["company"].nunique()

col1.metric("Total Comments", total_comments)
col2.metric("Negative Comments", negative_comments)
col3.metric("High / Critical Issues", high_critical_issues)
col4.metric("Companies", company_count)

critical_count = len(filtered_df[filtered_df["severity"] == "Critical"])
high_count = len(filtered_df[filtered_df["severity"] == "High"])

top_category = (
    filtered_df["category"].value_counts().idxmax()
    if not filtered_df.empty
    else "No data"
)

top_risk_type = (
    filtered_df["risk_type"].value_counts().idxmax()
    if not filtered_df.empty
    else "No data"
)

st.info(
    f"""
    **Executive Summary:**  
    The dashboard analyzed **{total_comments} customer comments**.  
    The top issue category is **{top_category}** and the leading risk type is **{top_risk_type}**.  
    There are **{critical_count} critical** and **{high_count} high-severity** issues requiring attention.
    """
)

st.divider()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Top Issue Categories")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        category_counts = filtered_df["category"].value_counts().reset_index()
        category_counts.columns = ["category", "count"]

        fig_category = px.bar(
            category_counts,
            x="category",
            y="count",
            title="Issue Categories",
            text="count",
        )

        fig_category.update_layout(
            xaxis_title="Category",
            yaxis_title="Number of Comments",
        )

        st.plotly_chart(fig_category, use_container_width=True)

with chart_col2:
    st.subheader("Severity Breakdown")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        severity_counts = filtered_df["severity"].value_counts().reset_index()
        severity_counts.columns = ["severity", "count"]

        fig_severity = px.pie(
            severity_counts,
            names="severity",
            values="count",
            title="Severity Distribution",
        )

        st.plotly_chart(fig_severity, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Risk Type Breakdown")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        risk_counts = filtered_df["risk_type"].value_counts().reset_index()
        risk_counts.columns = ["risk_type", "count"]

        fig_risk = px.pie(
            risk_counts,
            names="risk_type",
            values="count",
            title="Risk Types",
        )

        st.plotly_chart(fig_risk, use_container_width=True)

with chart_col4:
    st.subheader("Owner Team Routing")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        team_counts = filtered_df["owner_team"].value_counts().reset_index()
        team_counts.columns = ["owner_team", "count"]

        fig_team = px.bar(
            team_counts,
            x="owner_team",
            y="count",
            title="Owner Teams",
            text="count",
        )

        fig_team.update_layout(
            xaxis_title="Owner Team",
            yaxis_title="Number of Comments",
        )

        st.plotly_chart(fig_team, use_container_width=True)

st.divider()

st.subheader("🚨 High-Risk Comments")

high_risk_df = filtered_df[filtered_df["severity"].isin(["High", "Critical"])]

if high_risk_df.empty:
    st.success("No high-risk comments found for the selected filters.")
else:
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
        hide_index=True,
    )

st.subheader("📋 All Classified Comments")

display_columns = [
    "source",
    "company",
    "product_name",
    "rating",
    "comment_text",
    "category",
    "sub_category",
    "sentiment",
    "severity",
    "risk_type",
    "owner_team",
    "recommended_action",
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    label="Download Classified Results as CSV",
    data=filtered_df[display_columns].to_csv(index=False),
    file_name="pulserisk_classified_comments.csv",
    mime="text/csv",
)