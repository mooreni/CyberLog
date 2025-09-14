from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "alerts.db"
print("Database will be stored at:", DB_PATH)