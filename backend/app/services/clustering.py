from collections import Counter
from typing import Any

import pandas as pd

from app.services.risk_rules import get_severity_rank


def build_issue_clusters(classified_df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups classified comments into issue clusters.

    V2 clustering is intentionally transparent:
    cluster = company + product_name + category + sub_category

    Later versions can replace this with embedding/vector clustering.
    """

    if classified_df.empty:
        return pd.DataFrame()

    required_columns = [
        "company",
        "product_name",
        "category",
        "sub_category",
        "severity",
        "risk_type",
        "owner_team",
        "comment_text",
        "comment_date",
        "product_version",
        "recommended_action",
    ]

    for column in required_columns:
        if column not in classified_df.columns:
            classified_df[column] = ""

    grouped = classified_df.groupby(
        ["company", "product_name", "category", "sub_category"],
        dropna=False,
    )

    cluster_records: list[dict[str, Any]] = []

    for cluster_id, ((company, product_name, category, sub_category), group) in enumerate(grouped, start=1):
        severity_counts = group["severity"].value_counts().to_dict()
        highest_severity = max(
            group["severity"].dropna().tolist(),
            key=get_severity_rank,
            default="Low",
        )

        risk_type = _most_common_value(group["risk_type"].tolist())
        owner_team = _most_common_value(group["owner_team"].tolist())
        recommended_action = _most_common_value(group["recommended_action"].tolist())
        versions = sorted([str(v) for v in group["product_version"].dropna().unique().tolist()])
        first_seen = str(group["comment_date"].min())
        last_seen = str(group["comment_date"].max())

        sample_comments = group["comment_text"].head(3).tolist()

        root_cause = suggest_root_cause(
            category=category,
            sub_category=sub_category,
            group=group,
        )

        cluster_records.append(
            {
                "cluster_id": cluster_id,
                "company": company,
                "product_name": product_name,
                "category": category,
                "sub_category": sub_category,
                "issue_title": f"{category}: {sub_category}",
                "comment_count": len(group),
                "highest_severity": highest_severity,
                "critical_count": severity_counts.get("Critical", 0),
                "high_count": severity_counts.get("High", 0),
                "risk_type": risk_type,
                "owner_team": owner_team,
                "product_versions": ", ".join(versions),
                "first_seen": first_seen,
                "last_seen": last_seen,
                "suspected_root_cause": root_cause,
                "recommended_action": recommended_action,
                "sample_comments": sample_comments,
                "priority_score": calculate_priority_score(group),
            }
        )

    clusters_df = pd.DataFrame(cluster_records)

    if not clusters_df.empty:
        clusters_df = clusters_df.sort_values(
            by=["priority_score", "comment_count"],
            ascending=False,
        )

    return clusters_df


def suggest_root_cause(category: str, sub_category: str, group: pd.DataFrame) -> str:
    text_blob = " ".join(group["comment_text"].astype(str).tolist()).lower()
    versions = group["product_version"].dropna().astype(str).unique().tolist()

    mentions_update = any(
        phrase in text_blob
        for phrase in [
            "latest update",
            "new version",
            "after update",
            "after the update",
            "version",
            "recent update",
        ]
    )

    if mentions_update and versions:
        return f"Possible release-related issue affecting version(s): {', '.join(sorted(versions))}."

    if category == "Authentication / Login":
        return "Possible authentication, verification, password reset, or session management issue."

    if category == "App Reliability":
        return "Possible application stability, performance, or recent deployment regression."

    if category == "Documents":
        return "Possible file-processing, document storage, upload, download, or permissions issue."

    if category == "Customer Support":
        return "Possible support handoff, escalation, training, or response-time issue."

    if category == "Fraud / Security Concern":
        return "Potential fraud, dispute, or security workflow requiring urgent review."

    if category == "Billing / Payments":
        return "Possible transaction, billing, refund, or payment reconciliation issue."

    if category == "Feature Request":
        return "Customer experience improvement opportunity for product roadmap review."

    return "Root cause unclear; review sample comments and supporting system data."


def calculate_priority_score(group: pd.DataFrame) -> int:
    severity_points = {
        "Critical": 10,
        "High": 7,
        "Medium": 4,
        "Low": 1,
    }

    total = 0

    for severity in group["severity"].dropna().tolist():
        total += severity_points.get(severity, 1)

    negative_count = len(group[group["sentiment"] == "Negative"]) if "sentiment" in group else 0
    total += negative_count * 2

    volume_bonus = min(len(group), 10)
    total += volume_bonus

    return total


def detect_spikes(classified_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects simple spikes by category and date.

    V2 logic:
    If a category has 3+ comments on the same date, flag it as a spike.
    """

    if classified_df.empty or "comment_date" not in classified_df.columns:
        return pd.DataFrame()

    date_category_counts = (
        classified_df.groupby(["comment_date", "category"])
        .size()
        .reset_index(name="comment_count")
    )

    spike_df = date_category_counts[date_category_counts["comment_count"] >= 3].copy()

    if spike_df.empty:
        return spike_df

    spike_df["spike_signal"] = spike_df.apply(
        lambda row: f"{row['category']} received {row['comment_count']} comments on {row['comment_date']}.",
        axis=1,
    )

    return spike_df.sort_values(by="comment_count", ascending=False)


def detect_version_impact(classified_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects product versions with high complaint concentration.
    """

    if classified_df.empty or "product_version" not in classified_df.columns:
        return pd.DataFrame()

    impact_df = (
        classified_df.groupby(["product_name", "product_version", "category", "severity"])
        .size()
        .reset_index(name="comment_count")
    )

    impact_df = impact_df.sort_values(by="comment_count", ascending=False)

    return impact_df


def _most_common_value(values: list[Any]) -> str:
    cleaned = [str(value) for value in values if str(value).strip()]
    if not cleaned:
        return ""

    return Counter(cleaned).most_common(1)[0][0]