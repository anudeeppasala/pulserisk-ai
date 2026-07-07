from typing import Any

import pandas as pd


def generate_action_tickets(clusters_df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts issue clusters into Jira-style action tickets.
    """

    if clusters_df.empty:
        return pd.DataFrame()

    tickets: list[dict[str, Any]] = []

    for _, row in clusters_df.iterrows():
        ticket_type = _ticket_type_from_severity(row["highest_severity"])

        ticket_title = f"[{row['highest_severity']}] {row['issue_title']} - {row['product_name']}"

        description = (
            f"Issue cluster detected for {row['product_name']}.\n\n"
            f"Category: {row['category']}\n"
            f"Sub-category: {row['sub_category']}\n"
            f"Comment volume: {row['comment_count']}\n"
            f"Risk type: {row['risk_type']}\n"
            f"Owner team: {row['owner_team']}\n"
            f"Product version(s): {row['product_versions']}\n"
            f"First seen: {row['first_seen']}\n"
            f"Last seen: {row['last_seen']}\n\n"
            f"Suspected root cause:\n{row['suspected_root_cause']}\n\n"
            f"Recommended action:\n{row['recommended_action']}\n\n"
            f"Sample comments:\n"
            + "\n".join([f"- {comment}" for comment in row["sample_comments"]])
        )

        tickets.append(
            {
                "ticket_id": f"PRISK-{int(row['cluster_id']):04d}",
                "ticket_type": ticket_type,
                "title": ticket_title,
                "priority": row["highest_severity"],
                "owner_team": row["owner_team"],
                "risk_type": row["risk_type"],
                "status": "Open",
                "description": description,
            }
        )

    return pd.DataFrame(tickets)


def _ticket_type_from_severity(severity: str) -> str:
    if severity == "Critical":
        return "Incident"
    if severity == "High":
        return "Bug"
    if severity == "Medium":
        return "Task"
    return "Improvement"