import sqlite3

DB_NAME = "sentinelx.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        severity TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_event(event_type, severity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO events (event_type, severity) VALUES (?, ?)",
        (event_type, severity)
    )

    conn.commit()
    conn.close()