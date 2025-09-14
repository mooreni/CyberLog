from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "alerts.db"
import sqlite3
import uuid
from datetime import datetime, timezone
from app.models import AlertIn
from typing import Optional, List
from app.models import AlertReciept

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                severity TEXT NOT NULL CHECK (severity IN ('low','medium','high')),
                source TEXT,
                details TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

_init_db()

def add_alert(alert: AlertIn) -> str:
    """Insert a new alert row and return its generated id."""
    alert_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO alerts (id, title, severity, source, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (alert_id, alert.title, alert.severity, alert.source, alert.details, created_at),
        )
        conn.commit()
    finally:
        conn.close()

    return alert_id

def get_alert(alert_id: str) -> Optional[AlertReciept]:
    """Fetch one alert by id. Return AlertReciept or None if not found."""
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        if row:
            return AlertReciept(**dict(row))
        return None
    finally:
        conn.close()

def list_alerts(limit: int = 10, offset: int = 0) -> List[AlertReciept]:
    """Return a list of alerts, newest first."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [AlertReciept(**dict(r)) for r in rows]
    finally:
        conn.close()

def delete_alert(alert_id: str) -> bool:
    """Delete one alert by id. Return True if deleted, False if missing."""
    conn = _connect()
    try:
        deleted = conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        conn.commit()
        return deleted.rowcount > 0
    finally:
        conn.close()
