from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "bucketly.db"

def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bucket_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT '✨ Personal',
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Dream',
                location TEXT DEFAULT '',
                target_date TEXT,
                created_at TEXT NOT NULL,
                reflection TEXT NOT NULL DEFAULT '',
                completed_at TEXT
            )
        """)
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(bucket_items)").fetchall()
        }
        if "reflection" not in columns:
            conn.execute(
                "ALTER TABLE bucket_items ADD COLUMN reflection TEXT NOT NULL DEFAULT ''"
            )
        if "completed_at" not in columns:
            conn.execute("ALTER TABLE bucket_items ADD COLUMN completed_at TEXT")
        conn.commit()


def create_item(title, description, category, priority, location, target_date, status="Dream", reflection=""):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO bucket_items
            (title, description, category, priority, status, location, target_date,
             created_at, reflection, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'),
                    ?, CASE WHEN ? = 'Completed' THEN date('now', 'localtime') END)""",
            (title, description, category, priority, status, location, target_date, reflection, status),
        )
        conn.commit()


def list_items():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM bucket_items ORDER BY created_at DESC"
        ).fetchall()


def update_item(item_id, title, description, category, priority, location, target_date, reflection):
    with get_connection() as conn:
        conn.execute(
            """UPDATE bucket_items
            SET title = ?, description = ?, category = ?, priority = ?,
                location = ?, target_date = ?, reflection = ?
            WHERE id = ?""",
            (title, description, category, priority, location, target_date, reflection, item_id),
        )
        conn.commit()


def update_status(item_id, status):
    with get_connection() as conn:
        if status == "Completed":
            conn.execute(
                """UPDATE bucket_items
                SET status = ?, completed_at = COALESCE(completed_at, date('now', 'localtime'))
                WHERE id = ?""",
                (status, item_id),
            )
        else:
            conn.execute(
                "UPDATE bucket_items SET status = ?, completed_at = NULL WHERE id = ?",
                (status, item_id),
            )
        conn.commit()


def delete_item(item_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM bucket_items WHERE id = ?", (item_id,))
        conn.commit()
