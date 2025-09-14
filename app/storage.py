from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "alerts.db"
import sqlite3

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
