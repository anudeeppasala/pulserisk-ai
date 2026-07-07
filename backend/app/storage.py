import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "pulserisk.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS classified_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                company TEXT,
                product_name TEXT,
                rating INTEGER,
                comment_text TEXT,
                comment_date TEXT,
                product_version TEXT,
                category TEXT,
                sub_category TEXT,
                sentiment TEXT,
                severity TEXT,
                risk_type TEXT,
                owner_team TEXT,
                recommended_action TEXT,
                summary TEXT,
                classification_method TEXT,
                created_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE,
                ticket_type TEXT,
                title TEXT,
                priority TEXT,
                owner_team TEXT,
                risk_type TEXT,
                status TEXT,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_title TEXT,
                severity TEXT,
                owner_team TEXT,
                risk_type TEXT,
                message TEXT,
                status TEXT,
                created_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT,
                entity_id TEXT,
                action TEXT,
                old_value TEXT,
                new_value TEXT,
                note TEXT,
                created_at TEXT
            )
            """
        )

        conn.commit()


def clear_database() -> None:
    init_db()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM classified_comments")
        cursor.execute("DELETE FROM action_tickets")
        cursor.execute("DELETE FROM alerts")
        cursor.execute("DELETE FROM audit_events")
        conn.commit()


def save_classified_comments(classified_df: pd.DataFrame) -> int:
    init_db()

    now = datetime.utcnow().isoformat()

    rows = []

    for _, row in classified_df.iterrows():
        rows.append(
            (
                row.get("source"),
                row.get("company"),
                row.get("product_name"),
                int(row.get("rating")) if pd.notna(row.get("rating")) else None,
                row.get("comment_text"),
                row.get("comment_date"),
                row.get("product_version"),
                row.get("category"),
                row.get("sub_category"),
                row.get("sentiment"),
                row.get("severity"),
                row.get("risk_type"),
                row.get("owner_team"),
                row.get("recommended_action"),
                row.get("summary"),
                row.get("classification_method"),
                now,
            )
        )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO classified_comments (
                source,
                company,
                product_name,
                rating,
                comment_text,
                comment_date,
                product_version,
                category,
                sub_category,
                sentiment,
                severity,
                risk_type,
                owner_team,
                recommended_action,
                summary,
                classification_method,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()

    return len(rows)


def fetch_classified_comments() -> pd.DataFrame:
    init_db()

    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM classified_comments ORDER BY id DESC", conn)


def save_action_tickets(tickets_df: pd.DataFrame) -> int:
    init_db()

    now = datetime.utcnow().isoformat()
    count = 0

    with get_connection() as conn:
        cursor = conn.cursor()

        for _, row in tickets_df.iterrows():
            ticket_id = row.get("ticket_id")

            cursor.execute(
                "SELECT status FROM action_tickets WHERE ticket_id = ?",
                (ticket_id,),
            )
            existing = cursor.fetchone()

            if existing:
                continue

            cursor.execute(
                """
                INSERT INTO action_tickets (
                    ticket_id,
                    ticket_type,
                    title,
                    priority,
                    owner_team,
                    risk_type,
                    status,
                    description,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("ticket_id"),
                    row.get("ticket_type"),
                    row.get("title"),
                    row.get("priority"),
                    row.get("owner_team"),
                    row.get("risk_type"),
                    row.get("status", "New"),
                    row.get("description"),
                    now,
                    now,
                ),
            )
            count += 1

        conn.commit()

    return count


def fetch_action_tickets() -> pd.DataFrame:
    init_db()

    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM action_tickets ORDER BY id DESC", conn)


def update_ticket_status(ticket_id: str, new_status: str, note: str = "") -> None:
    init_db()

    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT status FROM action_tickets WHERE ticket_id = ?",
            (ticket_id,),
        )
        result = cursor.fetchone()

        old_status: Optional[str] = result[0] if result else None

        cursor.execute(
            """
            UPDATE action_tickets
            SET status = ?, updated_at = ?
            WHERE ticket_id = ?
            """,
            (new_status, now, ticket_id),
        )

        cursor.execute(
            """
            INSERT INTO audit_events (
                entity_type,
                entity_id,
                action,
                old_value,
                new_value,
                note,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "ticket",
                ticket_id,
                "status_change",
                old_status,
                new_status,
                note,
                now,
            ),
        )

        conn.commit()


def create_alerts_from_tickets(tickets_df: pd.DataFrame) -> int:
    init_db()

    if tickets_df.empty:
        return 0

    now = datetime.utcnow().isoformat()
    count = 0

    with get_connection() as conn:
        cursor = conn.cursor()

        for _, row in tickets_df.iterrows():
            if row.get("priority") not in ["Critical", "High"]:
                continue

            alert_title = f"{row.get('priority')} issue: {row.get('title')}"

            cursor.execute(
                """
                SELECT id FROM alerts
                WHERE alert_title = ?
                """,
                (alert_title,),
            )
            existing = cursor.fetchone()

            if existing:
                continue

            cursor.execute(
                """
                INSERT INTO alerts (
                    alert_title,
                    severity,
                    owner_team,
                    risk_type,
                    message,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert_title,
                    row.get("priority"),
                    row.get("owner_team"),
                    row.get("risk_type"),
                    row.get("description"),
                    "Open",
                    now,
                ),
            )
            count += 1

        conn.commit()

    return count


def fetch_alerts() -> pd.DataFrame:
    init_db()

    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC", conn)


def update_alert_status(alert_id: int, new_status: str, note: str = "") -> None:
    init_db()

    now = datetime.utcnow().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT status FROM alerts WHERE id = ?",
            (alert_id,),
        )
        result = cursor.fetchone()

        old_status = result[0] if result else None

        cursor.execute(
            """
            UPDATE alerts
            SET status = ?
            WHERE id = ?
            """,
            (new_status, alert_id),
        )

        cursor.execute(
            """
            INSERT INTO audit_events (
                entity_type,
                entity_id,
                action,
                old_value,
                new_value,
                note,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "alert",
                str(alert_id),
                "status_change",
                old_status,
                new_status,
                note,
                now,
            ),
        )

        conn.commit()


def fetch_audit_events() -> pd.DataFrame:
    init_db()

    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM audit_events ORDER BY id DESC", conn)


def get_database_summary() -> dict:
    init_db()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM classified_comments")
        comments_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM action_tickets")
        tickets_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alerts")
        alerts_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM audit_events")
        audit_count = cursor.fetchone()[0]

    return {
        "comments_count": comments_count,
        "tickets_count": tickets_count,
        "alerts_count": alerts_count,
        "audit_count": audit_count,
        "db_path": str(DB_PATH),
    }