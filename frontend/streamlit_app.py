import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from app.ingestion.app_store_connector import fetch_app_store_reviews_mock
from app.ingestion.csv_ingestion import validate_review_dataframe
from app.ingestion.google_play_connector import fetch_google_play_reviews_mock
from app.services.action_tickets import generate_action_tickets
from app.services.ai_classifier import classify_comment_ai_ready
from app.services.clustering import (
    build_issue_clusters,
    detect_spikes,
    detect_version_impact,
)
from app.storage import (
    clear_database,
    create_alerts_from_tickets,
    fetch_action_tickets,
    fetch_alerts,
    fetch_audit_events,
    fetch_classified_comments,
    get_database_summary,
    init_db,
    save_action_tickets,
    save_classified_comments,
    update_alert_status,
    update_ticket_status,
)


st.set_page_config(
    page_title="PulseRisk AI V3",
    page_icon="📊",
    layout="wide",
)

init_db()

st.title("📊 PulseRisk AI V3")

st.markdown(
    """
    **Enterprise Voice-of-Customer Risk Intelligence Platform**

    Ingest customer feedback, classify issues, detect risk, group recurring complaints,
    suggest root causes, generate internal tickets, create alerts, track status changes,
    and produce executive reports.
    """
)

st.divider()


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    sample_path = ROOT / "backend" / "app" / "data" / "sample_comments.csv"
    return pd.read_csv(sample_path)


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


def build_filtered_df(classified_df: pd.DataFrame) -> pd.DataFrame:
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

    return filtered_df.sort_values(by="severity_rank", ascending=False)


with st.sidebar:
    st.header("⚙️ Settings")

    use_ai_classifier = st.toggle(
        "Use AI classifier",
        value=False,
        help="Requires OPENAI_API_KEY. If unavailable, the app uses rule-based fallback.",
    )

    st.header("📥 Ingestion Source")

    ingestion_source = st.radio(
        "Choose source",
        [
            "Sample CSV",
            "Upload CSV",
            "Mock Google Play Reviews",
            "Mock App Store Reviews",
            "Combined Mock Store Reviews",
            "Load From SQLite Database",
        ],
    )

    uploaded_file = None

    if ingestion_source == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload customer feedback CSV",
            type=["csv"],
        )


if ingestion_source == "Sample CSV":
    raw_df = load_sample_data()
    st.caption("Using sample CSV data.")

elif ingestion_source == "Upload CSV":
    if uploaded_file is None:
        st.warning("Upload a CSV file to continue.")
        st.stop()

    raw_df = pd.read_csv(uploaded_file)
    st.success("Uploaded CSV successfully.")

elif ingestion_source == "Mock Google Play Reviews":
    raw_df = fetch_google_play_reviews_mock()
    st.caption("Using mock Google Play reviews.")

elif ingestion_source == "Mock App Store Reviews":
    raw_df = fetch_app_store_reviews_mock()
    st.caption("Using mock App Store reviews.")

elif ingestion_source == "Combined Mock Store Reviews":
    google_df = fetch_google_play_reviews_mock()
    apple_df = fetch_app_store_reviews_mock()
    raw_df = pd.concat([google_df, apple_df], ignore_index=True)
    st.caption("Using combined mock Google Play + App Store reviews.")

else:
    db_df = fetch_classified_comments()

    if db_df.empty:
        st.warning("No saved records found in SQLite yet. Use another source and click Save to SQLite first.")
        st.stop()

    raw_df = db_df[
        [
            "source",
            "company",
            "product_name",
            "rating",
            "comment_text",
            "comment_date",
            "product_version",
        ]
    ]
    st.caption("Loaded records from SQLite database.")


missing_columns = validate_review_dataframe(raw_df)

if missing_columns:
    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
        + ". Required columns are source, company, product_name, rating, comment_text, comment_date, product_version."
    )
    st.stop()


classified_df = classify_comments(raw_df, use_ai=use_ai_classifier)
filtered_df = build_filtered_df(classified_df)

filtered_clusters_df = build_issue_clusters(filtered_df)
filtered_tickets_df = generate_action_tickets(filtered_clusters_df)
filtered_spikes_df = detect_spikes(filtered_df)
filtered_version_impact_df = detect_version_impact(filtered_df)

tab_dashboard, tab_clusters, tab_tickets, tab_alerts, tab_database, tab_report, tab_data = st.tabs(
    [
        "Executive Dashboard",
        "Issue Clusters",
        "Internal Tickets",
        "Alert Center",
        "Database & Audit",
        "Executive Report",
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
    col3.metric("High / Critical", high_critical_issues)
    col4.metric("Issue Clusters", cluster_count)
    col5.metric("Internal Tickets", ticket_count)

    critical_count = len(filtered_df[filtered_df["severity"] == "Critical"])
    high_count = len(filtered_df[filtered_df["severity"] == "High"])

    top_category = filtered_df["category"].value_counts().idxmax() if not filtered_df.empty else "No data"
    top_risk_type = filtered_df["risk_type"].value_counts().idxmax() if not filtered_df.empty else "No data"
    top_owner_team = filtered_df["owner_team"].value_counts().idxmax() if not filtered_df.empty else "No data"

    st.info(
        f"""
        **Executive Summary:**  
        PulseRisk analyzed **{total_comments} customer comments** and detected **{cluster_count} issue clusters**.  
        The top issue category is **{top_category}**, the leading risk type is **{top_risk_type}**, and the most impacted team is **{top_owner_team}**.  
        There are **{critical_count} critical** and **{high_count} high-severity** comments requiring attention.
        """
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Top Issue Categories")

        if filtered_df.empty:
            st.warning("No data available.")
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
            st.plotly_chart(fig_category, use_container_width=True)

    with chart_col2:
        st.subheader("Severity Breakdown")

        if filtered_df.empty:
            st.warning("No data available.")
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
            st.warning("No data available.")
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
            st.warning("No data available.")
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
            st.plotly_chart(fig_team, use_container_width=True)


with tab_clusters:
    st.subheader("🧩 Issue Clusters + Root Cause")

    if filtered_clusters_df.empty:
        st.warning("No issue clusters available.")
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
    st.subheader("🎫 Internal Action Tickets")

    st.markdown(
        """
        This replaces Jira for now. PulseRisk creates internal work items with owner team,
        priority, root-cause evidence, and status workflow.
        """
    )

    if filtered_tickets_df.empty:
        st.warning("No tickets generated.")
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

        save_col1, save_col2 = st.columns(2)

        with save_col1:
            if st.button("Save Current Comments + Tickets to SQLite"):
                comments_saved = save_classified_comments(filtered_df)
                tickets_saved = save_action_tickets(filtered_tickets_df)
                alerts_created = create_alerts_from_tickets(filtered_tickets_df)

                st.success(
                    f"Saved {comments_saved} comments, {tickets_saved} new tickets, and {alerts_created} new alerts."
                )

        with save_col2:
            st.download_button(
                label="Download Tickets CSV",
                data=filtered_tickets_df.to_csv(index=False),
                file_name="pulserisk_internal_tickets.csv",
                mime="text/csv",
            )

        st.subheader("Update Saved Ticket Status")

        saved_tickets_df = fetch_action_tickets()

        if saved_tickets_df.empty:
            st.info("No saved tickets yet. Save current tickets first.")
        else:
            selected_ticket_id = st.selectbox(
                "Select saved ticket",
                saved_tickets_df["ticket_id"].tolist(),
            )

            new_status = st.selectbox(
                "New status",
                ["New", "Assigned", "In Progress", "Resolved", "Escalated"],
            )

            ticket_note = st.text_area("Status change note", placeholder="Example: Assigned to platform team for review.")

            if st.button("Update Ticket Status"):
                update_ticket_status(
                    ticket_id=selected_ticket_id,
                    new_status=new_status,
                    note=ticket_note,
                )
                st.success(f"Updated {selected_ticket_id} to {new_status}.")


with tab_alerts:
    st.subheader("🚨 Internal Alert Center")

    st.markdown(
        """
        This replaces Slack for now. High and critical tickets become internal alerts.
        Later, these alerts can be sent to Slack, Teams, email, or PagerDuty.
        """
    )

    alerts_df = fetch_alerts()

    if alerts_df.empty:
        st.info("No alerts saved yet. Save high or critical tickets first.")
    else:
        st.dataframe(
            alerts_df[
                [
                    "id",
                    "alert_title",
                    "severity",
                    "owner_team",
                    "risk_type",
                    "status",
                    "created_at",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        selected_alert_id = st.selectbox(
            "Select alert",
            alerts_df["id"].tolist(),
        )

        new_alert_status = st.selectbox(
            "New alert status",
            ["Open", "Acknowledged", "Investigating", "Resolved"],
        )

        alert_note = st.text_area("Alert note", placeholder="Example: Alert acknowledged by support operations.")

        if st.button("Update Alert Status"):
            update_alert_status(
                alert_id=int(selected_alert_id),
                new_status=new_alert_status,
                note=alert_note,
            )
            st.success(f"Updated alert {selected_alert_id} to {new_alert_status}.")


with tab_database:
    st.subheader("🗄️ SQLite Database + Audit Trail")

    summary = get_database_summary()

    db_col1, db_col2, db_col3, db_col4 = st.columns(4)

    db_col1.metric("Saved Comments", summary["comments_count"])
    db_col2.metric("Saved Tickets", summary["tickets_count"])
    db_col3.metric("Saved Alerts", summary["alerts_count"])
    db_col4.metric("Audit Events", summary["audit_count"])

    st.caption(f"Database path: {summary['db_path']}")

    st.subheader("Saved Tickets")
    saved_tickets_df = fetch_action_tickets()

    if saved_tickets_df.empty:
        st.info("No saved tickets yet.")
    else:
        st.dataframe(saved_tickets_df, use_container_width=True, hide_index=True)

    st.subheader("Audit Trail")
    audit_df = fetch_audit_events()

    if audit_df.empty:
        st.info("No audit events yet.")
    else:
        st.dataframe(audit_df, use_container_width=True, hide_index=True)

    st.warning("Danger zone")

    if st.button("Clear SQLite Database"):
        clear_database()
        st.success("Database cleared. Refresh the app to see updated counts.")


with tab_report:
    st.subheader("📄 Executive Report")

    st.markdown("### PulseRisk Executive Summary")

    report_text = f"""
PulseRisk AI analyzed {len(filtered_df)} customer feedback records.

Key Findings:
- Total comments analyzed: {len(filtered_df)}
- Negative comments: {len(filtered_df[filtered_df["sentiment"] == "Negative"])}
- High/Critical comments: {len(filtered_df[filtered_df["severity"].isin(["High", "Critical"])])}
- Issue clusters detected: {len(filtered_clusters_df)}
- Internal tickets generated: {len(filtered_tickets_df)}
- Spike signals detected: {len(filtered_spikes_df)}

Top Category:
{top_category if not filtered_df.empty else "No data"}

Top Risk Type:
{top_risk_type if not filtered_df.empty else "No data"}

Most Impacted Owner Team:
{top_owner_team if not filtered_df.empty else "No data"}

Recommended Leadership Action:
Review top high-priority clusters, assign internal tickets to owner teams, and monitor recurring complaints by product version.
"""

    st.text_area("Generated Executive Report", value=report_text, height=350)

    st.download_button(
        label="Download Executive Report TXT",
        data=report_text,
        file_name="pulserisk_executive_report.txt",
        mime="text/plain",
    )

    st.subheader("Trends & Version Impact")

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        if filtered_df.empty:
            st.warning("No data available.")
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
        if filtered_spikes_df.empty:
            st.success("No major spikes detected.")
        else:
            st.dataframe(filtered_spikes_df, use_container_width=True, hide_index=True)

    st.markdown("### Product Version Impact")

    if filtered_version_impact_df.empty:
        st.warning("No version impact data available.")
    else:
        st.dataframe(filtered_version_impact_df, use_container_width=True, hide_index=True)


with tab_data:
    st.subheader("📋 Classified Data")

    display_columns = [
        "source",
        "company",
        "product_name",
        "rating",
        "comment_text",
        "comment_date",
        "product_version",
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
        label="Download Classified Results CSV",
        data=filtered_df[display_columns].to_csv(index=False),
        file_name="pulserisk_v3_classified_comments.csv",
        mime="text/csv",
    )