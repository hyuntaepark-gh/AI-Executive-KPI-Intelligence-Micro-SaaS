from typing import Any, Dict, List
from api.app.db import get_conn


def ensure_analysis_log_table() -> None:
    """
    Creates analysis_log table + indexes if they do not exist.
    Safe to run multiple times.
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS analysis_log (
        id BIGSERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        metric TEXT NOT NULL,
        range TEXT NOT NULL,
        style TEXT NOT NULL,
        sql TEXT NOT NULL,
        narrative TEXT,
        risk TEXT,
        recommendation TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_analysis_log_created_at
        ON analysis_log (created_at DESC);

    CREATE INDEX IF NOT EXISTS idx_analysis_log_metric
        ON analysis_log (metric);
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
    finally:
        conn.close()


def insert_analysis_log(row: Dict[str, Any]) -> None:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO analysis_log (metric, range, style, sql, narrative, risk, recommendation)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row.get("metric"),
                    row.get("range"),
                    row.get("style"),
                    row.get("sql"),
                    row.get("narrative"),
                    row.get("risk"),
                    row.get("recommendation"),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def fetch_analysis_history(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, created_at, metric, range, style, sql, narrative, risk, recommendation
                FROM analysis_log
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            cols = [d.name for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    finally:
        conn.close()
