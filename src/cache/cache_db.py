import sqlite3
from pathlib import Path

DB_PATH = Path("data/cache.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spotify_artist (
        artist_name TEXT PRIMARY KEY,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()
