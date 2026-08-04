import sqlite3
import json
import logging
from datetime import datetime

DB_PATH = "sentinelx.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes standard production relational schema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Cameras Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                ip_url TEXT,
                zone TEXT DEFAULT 'DEFAULT',
                status TEXT DEFAULT 'ONLINE',
                fps INTEGER DEFAULT 0,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Events Table (Primary Analytics Source)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH')) NOT NULL,
                camera TEXT NOT NULL,
                zone TEXT DEFAULT 'UNKNOWN',
                track_id INTEGER DEFAULT -1,
                confidence REAL DEFAULT 0.0,
                duration REAL DEFAULT 0.0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Evidence Table (Linked via Foreign Key)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                image_path TEXT NOT NULL,
                favorite INTEGER DEFAULT 0,
                metadata TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        """)
        conn.commit()