"""
Business logic for creating, reading and closing client queries.

All operations use cursor-based SQL through the `database` module. Timestamps
are generated with datetime.now() as required by the spec.
"""

from datetime import datetime

import pandas as pd

import config
import database

DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def _now() -> str:
    return datetime.now().strftime(DT_FORMAT)


def create_query(
    mail_id: str,
    mobile_number: str,
    query_heading: str,
    query_description: str,
    category: str,
) -> int:
    """
    Insert a new query. status defaults to 'Open', query_created_time is set to
    now(), and query_closed_time stays NULL. Returns the new query_id.
    """
    created = _now()
    return database.run_write(
        """
        INSERT INTO queries
            (mail_id, mobile_number, query_heading, query_description,
             category, status, query_created_time, query_closed_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            mail_id.strip(),
            mobile_number.strip(),
            query_heading.strip(),
            query_description.strip(),
            category,
            config.STATUS_OPEN,
            created,
            None,
        ),
    )


def close_query(query_id: int) -> None:
    """Mark a query as Closed and stamp query_closed_time with now()."""
    database.run_write(
        """
        UPDATE queries
        SET status = %s, query_closed_time = %s
        WHERE query_id = %s AND status = %s
        """,
        (config.STATUS_CLOSED, _now(), query_id, config.STATUS_OPEN),
    )


def get_queries(status: str | None = None, category: str | None = None) -> pd.DataFrame:
    """
    Return queries as a DataFrame, optionally filtered by status and/or category.
    """
    sql = "SELECT * FROM queries"
    conditions = []
    params: list = []

    if status and status != "All":
        conditions.append("status = %s")
        params.append(status)
    if category and category != "All":
        conditions.append("category = %s")
        params.append(category)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY query_created_time DESC"

    columns, rows = database.run_query(sql, tuple(params))
    return pd.DataFrame(rows, columns=columns)


def get_metrics() -> dict:
    """Return summary metrics for the support dashboard."""
    df = get_queries()
    metrics = {
        "total": len(df),
        "open": 0,
        "closed": 0,
        "avg_resolution_hours": None,
        "by_category": {},
    }
    if df.empty:
        return metrics

    metrics["open"] = int((df["status"] == config.STATUS_OPEN).sum())
    metrics["closed"] = int((df["status"] == config.STATUS_CLOSED).sum())

    # Average resolution time over closed queries (in hours).
    closed = df[df["status"] == config.STATUS_CLOSED].copy()
    closed = closed.dropna(subset=["query_closed_time"])
    if not closed.empty:
        created = pd.to_datetime(closed["query_created_time"], errors="coerce")
        closed_t = pd.to_datetime(closed["query_closed_time"], errors="coerce")
        diff = (closed_t - created).dropna()
        if not diff.empty:
            metrics["avg_resolution_hours"] = round(
                diff.dt.total_seconds().mean() / 3600.0, 2
            )

    metrics["by_category"] = df["category"].fillna("Uncategorized").value_counts().to_dict()
    return metrics
