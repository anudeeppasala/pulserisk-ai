import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from app.services.action_tickets import generate_action_tickets
from app.services.ai_classifier import classify_comment_ai_ready
from app.services.clustering import (
    build_issue_clusters,
    detect_spikes,
    detect_version_impact,
)


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
    issue categories, sentiment, severity, risk signals, root-cause insights, action tickets,
    and owner-team routing.
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


def classify_comments(df: pd.DataFrame, use_ai: bool = False) -> pd.DataFrame:
    records = []

    for _, row in df.iterrows():
        rating = None

        if "rating" in row and not pd.isna(row["rating"]):
            try:
                rating = int(row["rating"])
            except ValueError:
                rating = None

        result = classify_comment_ai_ready(
            text=str(row["comment_text"]),
            rating=rating,
            use_ai=use_ai,
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


with st.sidebar:
    st.header("⚙️ Settings")

    use_ai_classifier = st.toggle(
        "Use AI classifier",
        value=False,
        help="Requires OPENAI_API_KEY in your environment. If unavailable, the app safely falls back to rule-based classification.",
    )

    st.header("📥 Data")

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

classified_df = classify_comments(raw_df, use_ai=use_ai_classifier)
clusters_df = build_issue_clusters(classified_df)
tickets_df = generate_action_tickets(clusters_df)
spikes_df = detect_spikes(classified_df)
version_impact_df = detect_version_impact(classified_df)

with st.sidebar:
    st.header("🔎 Filters")

    companies = ["All"] + sorted(classified_df["company"].dropna().unique().tolist())
    selected_company = st.selectbox("Company", companies)

    products = ["All"] + sorted(classified_df["product_name"].dropna().unique().tolist())
    selected_product = st.selectbox("Product", products)

    severities = ["All", "Critical", "High", "Medium", "Low"]
    selected_severity = st.selectbox("Severity", severities)

    categories = ["All"] + sorted(classified_df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("Category", categories)

    risk_types = ["All"] + sorted(classified_df["risk_type"].dropna().unique().tolist())
    selected_risk_type = st.selectbox("Risk Type", risk_types)

    sentiments = ["All"] + sorted(classified_df["sentiment"].dropna().unique().tolist())
    selected_sentiment = st.selectbox("Sentiment", sentiments)

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

filtered_clusters_df = build_issue_clusters(filtered_df)
filtered_tickets_df = generate_action_tickets(filtered_clusters_df)
filtered_spikes_df = detect_spikes(filtered_df)
filtered_version_impact_df = detect_version_impact(filtered_df)

tab_dashboard, tab_clusters, tab_tickets, tab_trends, tab_data = st.tabs(
    [
        "Executive Dashboard",
        "Issue Clusters",
        "Action Tickets",
        "Trends & Version Impact",
        "Classified Data",
    ]
)

with tab_dashboard:
    col1, col2, col3, col4, col5 = st.columns(5)

    total_comments = len(filtered_df)
    negative_comments = len(filtered_df[filtered_df["sentiment"] == "Negative"])
    high_critical_issues = len(filtered_df[filtered_df["severity"].isin(["High", "Critical"])])
    cluster_count = len(filtered_clusters_df)
    ticket_count = len(filtered_tickets_df)

    col1.metric("Total Comments", total_comments)
    col2.metric("Negative Comments", negative_comments)
    col3.metric("High / Critical Issues", high_critical_issues)
    col4.metric("Issue Clusters", cluster_count)
    col5.metric("Action Tickets", ticket_count)

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

    top_owner_team = (
        filtered_df["owner_team"].value_counts().idxmax()
        if not filtered_df.empty
        else "No data"
    )

    st.info(
        f"""
        **Executive Summary:**  
        The dashboard analyzed **{total_comments} customer comments** and detected **{cluster_count} issue clusters**.  
        The top issue category is **{top_category}**, the leading risk type is **{top_risk_type}**, and the most impacted owner team is **{top_owner_team}**.  
        There are **{critical_count} critical** and **{high_count} high-severity** comments requiring attention.
        """
    )

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

with tab_clusters:
    st.subheader("🧩 Issue Clusters")

    st.markdown(
        """
        Issue clusters group similar comments by company, product, category, and sub-category.
        V2 uses transparent clustering logic. Later versions can upgrade this to embedding-based clustering.
        """
    )

    if filtered_clusters_df.empty:
        st.warning("No issue clusters available for the selected filters.")
    else:
        st.dataframe(
            filtered_clusters_df[
                [
                    "cluster_id",
                    "company",
                    "product_name",
                    "issue_title",
                    "comment_count",
                    "highest_severity",
                    "risk_type",
                    "owner_team",
                    "product_versions",
                    "suspected_root_cause",
                    "recommended_action",
                    "priority_score",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Top Cluster Cards")

        for _, cluster in filtered_clusters_df.head(5).iterrows():
            with st.expander(
                f"{cluster['issue_title']} | {cluster['product_name']} | Priority {cluster['priority_score']}"
            ):
                st.write(f"**Company:** {cluster['company']}")
                st.write(f"**Product:** {cluster['product_name']}")
                st.write(f"**Comment Count:** {cluster['comment_count']}")
                st.write(f"**Highest Severity:** {cluster['highest_severity']}")
                st.write(f"**Risk Type:** {cluster['risk_type']}")
                st.write(f"**Owner Team:** {cluster['owner_team']}")
                st.write(f"**Product Versions:** {cluster['product_versions']}")
                st.write(f"**Suspected Root Cause:** {cluster['suspected_root_cause']}")
                st.write(f"**Recommended Action:** {cluster['recommended_action']}")
                st.write("**Sample Comments:**")
                for comment in cluster["sample_comments"]:
                    st.write(f"- {comment}")

with tab_tickets:
    st.subheader("🎫 Action Tickets")

    st.markdown(
        """
        Action tickets convert issue clusters into Jira-style work items with severity,
        owner team, evidence, suspected root cause, and recommended action.
        """
    )

    if filtered_tickets_df.empty:
        st.warning("No action tickets available for the selected filters.")
    else:
        st.dataframe(
            filtered_tickets_df[
                [
                    "ticket_id",
                    "ticket_type",
                    "title",
                    "priority",
                    "owner_team",
                    "risk_type",
                    "status",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Ticket Details")

        for _, ticket in filtered_tickets_df.head(5).iterrows():
            with st.expander(f"{ticket['ticket_id']} - {ticket['title']}"):
                st.write(f"**Type:** {ticket['ticket_type']}")
                st.write(f"**Priority:** {ticket['priority']}")
                st.write(f"**Owner Team:** {ticket['owner_team']}")
                st.write(f"**Risk Type:** {ticket['risk_type']}")
                st.write(f"**Status:** {ticket['status']}")
                st.code(ticket["description"])

        st.download_button(
            label="Download Action Tickets as CSV",
            data=filtered_tickets_df.to_csv(index=False),
            file_name="pulserisk_action_tickets.csv",
            mime="text/csv",
        )

with tab_trends:
    st.subheader("📈 Trends & Version Impact")

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        st.markdown("### Daily Comment Volume")

        if filtered_df.empty:
            st.warning("No data available for selected filters.")
        else:
            daily_counts = filtered_df.groupby("comment_date").size().reset_index(name="comment_count")
            fig_daily = px.line(
                daily_counts,
                x="comment_date",
                y="comment_count",
                markers=True,
                title="Daily Feedback Volume",
            )
            st.plotly_chart(fig_daily, use_container_width=True)

    with trend_col2:
        st.markdown("### Spike Signals")

        if filtered_spikes_df.empty:
            st.success("No major spikes detected in the selected data.")
        else:
            st.dataframe(filtered_spikes_df, use_container_width=True, hide_index=True)

    st.markdown("### Product Version Impact")

    if filtered_version_impact_df.empty:
        st.warning("No product version impact data available.")
    else:
        st.dataframe(
            filtered_version_impact_df,
            use_container_width=True,
            hide_index=True,
        )

        top_version_impact = filtered_version_impact_df.head(10)
        fig_version = px.bar(
            top_version_impact,
            x="product_version",
            y="comment_count",
            color="category",
            title="Top Product Version Complaint Concentration",
            text="comment_count",
        )
        st.plotly_chart(fig_version, use_container_width=True)

with tab_data:
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
        "classification_method",
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