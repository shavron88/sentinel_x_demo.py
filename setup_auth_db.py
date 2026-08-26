"""
SentinelX Auth Database Setup
Initializes the SQLite database with a secure hashed admin credential.
"""
import sqlite3
import hashlib
import os

DB_PATH = "sentinelx.db"

def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create admin_users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    
    # Default credentials to secure
    username = "sentinelx_admin"
    raw_password = "SentinelX_SecurePassword2026!"
    
    # Generate SHA-256 hash
    password_hash = hashlib.sha256(raw_password.encode()).hexdigest()
    
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO admin_users (id, username, password_hash) VALUES (1, ?, ?)",
            (username, password_hash)
        )
        conn.commit()
        print("[SUCCESS] Admin credentials securely hashed and stored in database!")
    except Exception as e:
        print(f"[ERROR] Failed to save credentials: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_auth_db()