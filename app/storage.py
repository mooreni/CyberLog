from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "alerts.db"
import sqlite3
import uuid
from datetime import datetime, timezone
from app import models
from typing import List, Optional

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

def add_alert(alert: models.AlertIn) -> str:
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

def get_alert(alert_id: str) -> Optional[models.AlertReciept]:
    """Fetch one alert by id. Return AlertReciept or None if not found."""
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        if row:
            return models.AlertReciept(**dict(row))
        return None
    finally:
        conn.close()

def list_alerts(limit: int = 10, offset: int = 0) -> List[models.AlertReciept]:
    """Return a list of alerts, newest first."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [models.AlertReciept(**dict(r)) for r in rows]
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

def update_alert(alert_id: str, changes: models.AlertUpdate) -> Optional[models.AlertReciept]:
    """Apply partial updates; return updated alert or None if not found."""
    # Build SET clauses dynamically for provided fields
    fields = []
    values = []

    if changes.title is not None:
        fields.append("title = ?")
        values.append(changes.title)
    if changes.severity is not None:
        fields.append("severity = ?")
        values.append(changes.severity)
    if changes.source is not None:
        fields.append("source = ?")
        values.append(changes.source)
    if changes.details is not None:
        fields.append("details = ?")
        values.append(changes.details)

    conn = _connect()
    try:
        sql = f"UPDATE alerts SET {', '.join(fields)} WHERE id = ?"
        values.append(alert_id)
        cur = conn.execute(sql, tuple(values))
        conn.commit()
        if cur.rowcount == 0:
            return None
    finally:
        conn.close()

    return get_alert(alert_id)

def replace_alert(alert_id: str, data: models.AlertIn) -> Optional[models.AlertReciept]:
    """Replace an alert completely with new data. Returns updated alert or None if missing."""
    conn = _connect()
    try:
        cur = conn.execute(
            """
            UPDATE alerts
            SET title = ?, severity = ?, source = ?, details = ?
            WHERE id = ?
            """,
            (data.title, data.severity, data.source, data.details, alert_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return None
    finally:
        conn.close()

    return get_alert(alert_id)