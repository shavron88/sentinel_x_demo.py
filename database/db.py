"""
SentinelX Authentication Module with Email OTP Verification & Database
"""
import os
import sqlite3
import hashlib
import secrets
import time
import random
import json
import logging
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from flask import session, request, jsonify

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Single source of truth for the database location. config.DB_PATH resolves
# DB_PATH against the project root (and loads .env), so the file is found no
# matter which working directory the process was launched from. The literal
# "sentinelx.db" fallback here used to create a second, empty database.
try:
    from config import DB_PATH  # noqa: F401
except Exception:  # pragma: no cover - config import failure fallback
    DB_PATH = os.getenv("DB_PATH", "sentinelx.db")
    if not os.path.isabs(DB_PATH):
        DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)

logger = logging.getLogger("SentinelX.Database")

DEMO_USERNAME = os.getenv("SENTINELX_USER", "sentinelx_admin")
DEMO_PASSWORD_HASH = hashlib.sha256(
    os.getenv("SENTINELX_PASSWORD", "SentinelX_SecurePassword2026!").encode()
).hexdigest()

SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT", "60"))
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60
_rate_limit_store = {}
_rate_limit_lock = threading.Lock()
_write_lock = threading.Lock()


def get_connection():
    """Returns a new thread-safe connection to SQLite with Row factory.

    Callers must either close the returned connection or use ``db_connection()``,
    which guarantees the handle is released.
    """
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_connection():
    """Context manager that ALWAYS closes the SQLite handle.

    ``with sqlite3.connect(...)`` only commits/rolls back -- it never closes the
    handle, which leaked a file descriptor on every read. This wrapper commits
    on success and always closes.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


@contextmanager
def db_write_connection():
    """Serialized write context manager.

    SQLite serialises writers anyway; taking an in-process lock first turns
    "database is locked" timeouts into short, deterministic waits.
    """
    with _write_lock:
        with db_connection() as conn:
            yield conn


_RATE_LIMIT_MAX_KEYS = 2048


def _prune_rate_limit_store(window_start):
    """Bounds the rate-limit store.

    The key space is ``client_ip + request.path``, so an attacker or a wide
    user base can create unlimited distinct keys. Two-stage eviction:
    expired/empty buckets first, then the least-recently-active ones until the
    store is back under the cap.
    """
    if len(_rate_limit_store) <= _RATE_LIMIT_MAX_KEYS:
        return
    for k in [k for k, v in _rate_limit_store.items() if not v or max(v) <= window_start]:
        _rate_limit_store.pop(k, None)
    if len(_rate_limit_store) <= _RATE_LIMIT_MAX_KEYS:
        return
    ordered = sorted(_rate_limit_store.items(), key=lambda kv: max(kv[1]) if kv[1] else 0)
    for k, _ in ordered[:len(_rate_limit_store) - _RATE_LIMIT_MAX_KEYS]:
        _rate_limit_store.pop(k, None)


def _check_rate_limit(key):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    with _rate_limit_lock:
        _prune_rate_limit_store(window_start)
        bucket = _rate_limit_store.setdefault(key, [])
        bucket = [t for t in bucket if t > window_start]
        if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
            _rate_limit_store[key] = bucket
            return False
        bucket.append(now)
        _rate_limit_store[key] = bucket
        return True


def is_authenticated():
    if "authenticated" not in session or session.get("authenticated") != True:
        return False
    last_active = session.get("last_active")
    if not last_active:
        return False
    try:
        last_active_time = datetime.fromisoformat(last_active)
        if datetime.now() - last_active_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            session.clear()
            return False
    except (ValueError, TypeError):
        session.clear()
        return False
    session["last_active"] = datetime.now().isoformat()
    return True


def get_current_user_id():
    return session.get("user_id", 1)


def login(username, password):
    if not username or not password:
        return False, "Username and password required"
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash, is_verified FROM admin_users WHERE username = ?", (username,))
            row = cursor.fetchone()
        
        if row:
            if "is_verified" in row.keys() and row["is_verified"] == 0:
                return False, "Account not verified. Please complete signup verification."
            if row["password_hash"] == password_hash:
                session.clear()
                session["authenticated"] = True
                session["username"] = username
                session["user_id"] = row["id"]
                session["email"] = f"{username}@sentinelx.ai"
                session["role"] = "System Administrator"
                session["last_active"] = datetime.now().isoformat()
                session["csrf_token"] = secrets.token_hex(32)
                return True, "Login successful"
    except Exception as e:
        print(f"Database authentication error: {e}")
        
    if username == DEMO_USERNAME and password_hash == DEMO_PASSWORD_HASH:
        session.clear()
        session["authenticated"] = True
        session["username"] = username
        session["user_id"] = 1
        session["email"] = f"{username}@sentinelx.ai"
        session["role"] = "System Administrator"
        session["last_active"] = datetime.now().isoformat()
        session["csrf_token"] = secrets.token_hex(32)
        return True, "Login successful (demo fallback)"
    return False, "Invalid credentials"


def logout():
    session.clear()


def _backfill_event_stats(cursor):
    """Populates event_stats_daily from historical events on first run.

    Runs once (when the rollup is empty but `events` is not) and is a single
    GROUP BY, so it is cheap even for large tables. Safe to call repeatedly.
    """
    try:
        rollup_rows = cursor.execute("SELECT COUNT(*) FROM event_stats_daily").fetchone()[0]
        if rollup_rows:
            return
        event_rows = cursor.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        if not event_rows:
            return
        cursor.execute("""
            INSERT INTO event_stats_daily (user_id, day, event_type, severity, total, confidence_sum)
            SELECT
                user_id,
                SUBSTR(timestamp, 1, 10) AS day,
                event_type,
                COALESCE(NULLIF(UPPER(severity), ''), 'LOW') AS severity,
                COUNT(*) AS total,
                SUM(COALESCE(confidence, 0)) AS confidence_sum
            FROM events
            WHERE timestamp IS NOT NULL AND SUBSTR(timestamp, 1, 4) GLOB '[0-9][0-9][0-9][0-9]'
            GROUP BY user_id, day, event_type, severity
            ON CONFLICT(user_id, day, event_type, severity) DO UPDATE SET
                total = total + excluded.total,
                confidence_sum = confidence_sum + excluded.confidence_sum
        """)
        logger.info("Backfilled event_stats_daily from %d historical events.", event_rows)
    except sqlite3.OperationalError as exc:
        logger.warning("event_stats_daily backfill skipped: %s", exc)


def _migrate_settings_primary_key(cursor):
    """Rebuild a legacy ``settings(key PRIMARY KEY, value, user_id)`` table.

    The single-column primary key meant one user's settings silently replaced
    another user's for the same key. Rebuild with PRIMARY KEY (key, user_id).
    """
    try:
        cursor.execute("PRAGMA table_info(settings)")
        columns = cursor.fetchall()
        if not columns:
            return
        pk_columns = [c["name"] for c in columns if c["pk"]]
        if len(pk_columns) != 1 or pk_columns[0] != "key":
            return  # already composite, or no PK at all

        cursor.execute("ALTER TABLE settings RENAME TO settings_legacy_migration")
        cursor.execute("""
            CREATE TABLE settings (
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                user_id INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (key, user_id)
            )
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, user_id)
            SELECT key, value, COALESCE(user_id, 1) FROM settings_legacy_migration
        """)
        cursor.execute("DROP TABLE settings_legacy_migration")
        logger.info("Migrated settings table to a per-user composite primary key.")
    except sqlite3.OperationalError as exc:
        logger.warning("Settings primary-key migration skipped: %s", exc)


def init_db():
    """Creates database schema tables and adds required columns if missing."""
    with db_write_connection() as conn:
        cursor = conn.cursor()

        # Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'LOW',
                camera TEXT NOT NULL,
                zone TEXT DEFAULT 'General Area',
                track_id INTEGER DEFAULT -1,
                confidence REAL DEFAULT 0.0,
                duration REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)

        # Evidence Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                event_id INTEGER,
                timestamp TEXT NOT NULL,
                camera TEXT NOT NULL,
                image_path TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)

        # Cameras Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                location TEXT DEFAULT 'Unspecified',
                stream_url TEXT NOT NULL,
                status TEXT DEFAULT 'OFFLINE',
                fps REAL DEFAULT 0.0,
                latency REAL DEFAULT 0.0,
                resolution TEXT DEFAULT '640x480',
                network_errors INTEGER DEFAULT 0,
                decode_errors INTEGER DEFAULT 0,
                last_error TEXT,
                is_rtsp INTEGER DEFAULT 0,
                UNIQUE(user_id, name)
            )
        """)

        # Admin Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'System Administrator',
                is_verified INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Settings Table -- created here (previously only created lazily by
        # SettingsStore, so the migration below always failed on a fresh DB).
        # Scoped per user via a composite primary key.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                user_id INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (key, user_id)
            )
        """)

        # Daily KPI rollup. The dashboard polls aggregate counters every few
        # seconds; computing them from `events` meant a full scan of every row
        # for that user (100k+ rows -> ~200ms per poll). save_event() now
        # increments this table, and get_event_stats() reads it instead.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_stats_daily (
                user_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                total INTEGER NOT NULL DEFAULT 0,
                confidence_sum REAL NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, day, event_type, severity)
            )
        """)

        # Known Faces Table (face registration page)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Email verification codes table (used by api.auth OTP flow)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ---- Indexes for the hot read paths -------------------------------
        # Every dashboard poll hits events/evidence ordered by recency and
        # filtered by user; without these the ORDER BY forces a full scan.
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id, id DESC)",
            "CREATE INDEX IF NOT EXISTS idx_events_user_ts ON events(user_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_events_camera ON events(camera, id DESC)",
            "CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity, id DESC)",
            "CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_events_user_type_sev ON events(user_id, event_type, severity)",
            # Covering index for the KPI aggregation: serves COUNT, the severity
            # and event_type SUMs, and AVG(confidence) without touching the table.
            "CREATE INDEX IF NOT EXISTS idx_events_kpi ON events(user_id, event_type, severity, confidence)",
            "CREATE INDEX IF NOT EXISTS idx_evidence_user ON evidence(user_id, id DESC)",
            "CREATE INDEX IF NOT EXISTS idx_evidence_event ON evidence(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_evidence_camera_ts ON evidence(camera, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_evidence_ts ON evidence(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_cameras_user ON cameras(user_id, id ASC)",
            "CREATE INDEX IF NOT EXISTS idx_settings_user ON settings(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_event_stats_day ON event_stats_daily(user_id, day)",
            "CREATE INDEX IF NOT EXISTS idx_verify_email ON email_verifications(email, id DESC)",
        ]
        for statement in index_statements:
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError:
                pass

        # Migration checks for existing columns
        migrations = [
            "ALTER TABLE cameras ADD COLUMN network_errors INTEGER DEFAULT 0",
            "ALTER TABLE cameras ADD COLUMN decode_errors INTEGER DEFAULT 0",
            "ALTER TABLE cameras ADD COLUMN last_error TEXT",
            "ALTER TABLE cameras ADD COLUMN is_rtsp INTEGER DEFAULT 0",
            "ALTER TABLE cameras ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE cameras ADD COLUMN resolution TEXT DEFAULT '640x480'",
            "ALTER TABLE events ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE evidence ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE admin_users ADD COLUMN is_verified INTEGER DEFAULT 1",
            "ALTER TABLE admin_users ADD COLUMN email TEXT",
        ]
        for query in migrations:
            try:
                cursor.execute(query)
            except sqlite3.OperationalError:
                pass

        # Legacy settings tables used `key TEXT PRIMARY KEY`, which made every
        # user's settings overwrite each other. Rebuild with composite key.
        _migrate_settings_primary_key(cursor)

        # One-time rollup of historical events for the fast KPI queries.
        _backfill_event_stats(cursor)

        # Seed default admin user if not exists
        default_username = os.getenv("SENTINELX_USER", "sentinelx_admin")
        default_password = os.getenv("SENTINELX_PASSWORD", "SentinelX_SecurePassword2026!")
        default_password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute(
            "INSERT OR IGNORE INTO admin_users (username, password_hash, email, role, is_verified) VALUES (?, ?, ?, ?, 1)",
            (default_username, default_password_hash, f"{default_username}@sentinelx.ai", "System Administrator")
        )

        conn.commit()
        logger.info("Database initialized successfully.")


_DB_READY = False


def ensure_db_ready():
    """Idempotently initialise the schema once per process.

    Guarded so a schema failure (e.g. a read-only volume) cannot crash imports;
    requests then surface the real error instead of an import-time traceback.
    """
    global _DB_READY
    if _DB_READY:
        return True
    try:
        init_db()
        _DB_READY = True
        return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Database initialisation failed: %s", exc)
        return False


ensure_db_ready()


def initiate_signup(username, password, email):
    """Directly registers and saves user to database upon signup."""
    import re
    if not username or not password or not email:
        return False, "Username, password and email are required"
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters"
    if len(password) < 4 or len(password) > 100:
        return False, "Password must be at least 4 characters"
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Username may only contain letters, numbers, dots, hyphens and underscores"
    if "@" not in email or "." not in email:
        return False, "Invalid email address format"

    try:
        with db_write_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM admin_users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists"

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO admin_users (username, password_hash, email, is_verified) VALUES (?, ?, ?, 1)",
                (username, password_hash, email)
            )
            conn.commit()
        return True, "Account successfully created! You can now log in."
    except Exception as e:
        print(f"Signup database error: {e}")
        return False, "Failed to create account. Please try again."


def signup(username, password, email):
    """Alias wrapper to satisfy dashboard/app.py import expectations."""
    return initiate_signup(username, password, email)


def verify_otp_and_register(email, otp_code):
    """Legacy wrapper support."""
    return True, "Account already verified."


# ==========================================
# EVENTS & EVIDENCE FUNCTIONS
# ==========================================

# Closed vocabularies used for aggregation. Matching exact values instead of
# LIKE patterns keeps the KPI aggregation on an index.
PERSON_EVENT_TYPES = ("PERSON_DETECTED", "FACE_RECOGNIZED", "PERSON")
VEHICLE_EVENT_TYPES = ("VEHICLE_DETECTED", "CAR_DETECTED", "TRUCK_DETECTED",
                       "BUS_DETECTED", "MOTORCYCLE_DETECTED")


def get_all_events(limit=50, user_id=None, start_date=None, end_date=None,
                   event_types=None, severities=None, cameras=None):
    """Fetches recorded events, newest first.

    All filters are optional and are applied as SQL predicates (not in Python)
    so the LIMIT still bounds the number of rows materialised.
    """
    try:
        limit = max(1, min(int(limit or 50), 2000))
        where = []
        params = []
        if user_id is not None:
            where.append("user_id = ?")
            params.append(user_id)
        if start_date:
            where.append("timestamp >= ?")
            params.append(start_date)
        if end_date:
            where.append("timestamp < ?")
            params.append(end_date)
        if event_types:
            types = [t for t in event_types if t]
            if types:
                where.append("LOWER(event_type) IN (%s)" % ",".join("?" * len(types)))
                params.extend(t.lower() for t in types)
        if severities:
            sevs = [s.upper() for s in severities if s]
            if sevs:
                where.append("UPPER(severity) IN (%s)" % ",".join("?" * len(sevs)))
                params.extend(sevs)
        if cameras:
            cams = [c for c in cameras if c]
            if cams:
                where.append("camera IN (%s)" % ",".join("?" * len(cams)))
                params.extend(cams)

        sql = "SELECT * FROM events"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with db_connection() as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return []


def _stats_from_events(user_id, start_date, end_date):
    """Exact aggregation straight from `events` (slow fallback)."""
    where = []
    params = []
    if user_id is not None:
        where.append("user_id = ?")
        params.append(user_id)
    if start_date:
        where.append("timestamp >= ?")
        params.append(start_date)
    if end_date:
        where.append("timestamp < ?")
        params.append(end_date)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    person_clause = "event_type IN (%s)" % ",".join("'%s'" % t for t in PERSON_EVENT_TYPES)
    vehicle_clause = "event_type IN (%s)" % ",".join("'%s'" % t for t in VEHICLE_EVENT_TYPES)
    sql = f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN UPPER(severity) IN ('HIGH','CRITICAL') THEN 1 ELSE 0 END) AS high_sev,
            SUM(CASE WHEN UPPER(severity) = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_sev,
            SUM(CASE WHEN UPPER(severity) = 'LOW' THEN 1 ELSE 0 END) AS low_sev,
            SUM(CASE WHEN {person_clause} THEN 1 ELSE 0 END) AS person_events,
            SUM(CASE WHEN {vehicle_clause} THEN 1 ELSE 0 END) AS vehicle_events,
            AVG(COALESCE(confidence, 0)) AS avg_confidence
        FROM events{clause}
    """
    with db_connection() as conn:
        row = conn.execute(sql, params).fetchone()
    return {k: row[k] for k in row.keys()} if row else {}


def get_event_stats(user_id=None, since=None, until=None, exact=False):
    """Aggregated event counters used by /stats, /ai_summary and reports.

    Reads the incrementally maintained ``event_stats_daily`` rollup, so the KPI
    poll costs a handful of rows instead of a scan of every event. Resolution is
    one day, so ``since``/``until`` are snapped to whole days. Pass
    ``exact=True`` for arbitrary sub-day windows (slower, scans ``events``).

    Falls back to the exact scan when the rollup is unavailable.
    """
    def normalise(stats):
        stats = dict(stats or {})
        for key in ("total", "high_sev", "medium_sev", "low_sev",
                    "person_events", "vehicle_events"):
            stats[key] = int(stats.get(key) or 0)
        stats["avg_confidence"] = round(float(stats.get("avg_confidence") or 0.0), 4)
        return stats

    try:
        if exact:
            return normalise(_stats_from_events(user_id, since, until))

        where = []
        params = []
        if user_id is not None:
            where.append("user_id = ?")
            params.append(user_id)
        if since:
            where.append("day >= ?")
            params.append(str(since)[:10])
        if until:
            where.append("day <= ?")
            params.append(str(until)[:10])
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        person_clause = "event_type IN (%s)" % ",".join("'%s'" % t for t in PERSON_EVENT_TYPES)
        vehicle_clause = "event_type IN (%s)" % ",".join("'%s'" % t for t in VEHICLE_EVENT_TYPES)
        sql = f"""
            SELECT
                COALESCE(SUM(total), 0) AS total,
                COALESCE(SUM(CASE WHEN severity IN ('HIGH','CRITICAL') THEN total ELSE 0 END), 0) AS high_sev,
                COALESCE(SUM(CASE WHEN severity = 'MEDIUM' THEN total ELSE 0 END), 0) AS medium_sev,
                COALESCE(SUM(CASE WHEN severity = 'LOW' THEN total ELSE 0 END), 0) AS low_sev,
                COALESCE(SUM(CASE WHEN {person_clause} THEN total ELSE 0 END), 0) AS person_events,
                COALESCE(SUM(CASE WHEN {vehicle_clause} THEN total ELSE 0 END), 0) AS vehicle_events,
                COALESCE(SUM(confidence_sum), 0) AS confidence_sum
            FROM event_stats_daily{clause}
        """
        with db_connection() as conn:
            try:
                row = conn.execute(sql, params).fetchone()
            except sqlite3.OperationalError:
                # Rollup table missing (pre-migration database).
                return normalise(_stats_from_events(user_id, since, until))
        stats = normalise({k: row[k] for k in row.keys()})
        confidence_sum = float(stats.pop("confidence_sum", 0.0) or 0.0)
        total = stats["total"]
        stats["avg_confidence"] = round(confidence_sum / total, 4) if total else 0.0
        return stats
    except Exception as e:
        logger.error(f"Error computing event stats: {e}")
        return normalise({})


def get_evidence_by_id(evidence_id, user_id=None):
    """Fetches single evidence record with joined event details."""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    WHERE e.id = ? AND e.user_id = ?
                """, (evidence_id, user_id))
            else:
                cursor.execute("""
                    SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                    FROM evidence e
                    LEFT JOIN events ev ON e.event_id = ev.id
                    WHERE e.id = ?
                """, (evidence_id,))
            row = cursor.fetchone()
            return _row_to_evidence_dict(row)
    except Exception as ex:
        logger.error(f"Error fetching evidence: {ex}")
        return None


def get_all_evidence(limit=100, user_id=None):
    """Fetches evidence records with joined event details for the evidence vault."""
    try:
        limit = max(1, min(int(limit or 100), 2000))
        if user_id is not None:
            sql = """
                SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                FROM evidence e
                LEFT JOIN events ev ON e.event_id = ev.id
                WHERE e.user_id = ?
                ORDER BY e.id DESC
                LIMIT ?
            """
            params = (user_id, limit)
        else:
            sql = """
                SELECT e.*, ev.event_type, ev.severity, ev.zone, ev.confidence as event_confidence
                FROM evidence e
                LEFT JOIN events ev ON e.event_id = ev.id
                ORDER BY e.id DESC
                LIMIT ?
            """
            params = (limit,)
        with db_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [_row_to_evidence_dict(row) for row in rows]
    except Exception as ex:
        logger.error(f"Error fetching evidence list: {ex}")
        return []


def _row_to_evidence_dict(row):
    """Converts a database row into the evidence dict format expected by the frontend."""
    if row is None:
        return None
    item = dict(row)
    metadata = item.get("metadata")
    meta = {}
    if metadata:
        try:
            meta = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            pass
    image_path = item.get("image_path", "")
    if image_path and not image_path.startswith("/"):
        image_path = "/" + image_path.lstrip("/")
    image_path = image_path.replace("\\", "/")
    return {
        "id": item.get("id"),
        "event_id": item.get("event_id"),
        "image": image_path,
        "event": meta.get("event_type", item.get("event_type", "")),
        "camera": item.get("camera", meta.get("camera", "")),
        "location": item.get("zone", meta.get("location", "")),
        "time": item.get("timestamp", ""),
        "trackingId": meta.get("tracking_id", ""),
        "confidence": float(item.get("event_confidence", meta.get("confidence", 0))),
        "severity": item.get("severity", "LOW"),
        "favorite": meta.get("favorite", False),
        "description": meta.get("ai_description", ""),
        "ocr_text": meta.get("ocr_text", ""),
        "tags": meta.get("tags", []),
        "similar_ids": meta.get("similar_ids", []),
        "metadata": meta,
    }


# ==========================================
# CAMERA CRUD FUNCTIONS
# ==========================================

def save_camera(name, stream_url, location="Unspecified", status="OFFLINE", fps=0.0, latency=0.0, resolution="640x480", user_id=1, **kwargs):
    """Saves or updates camera config in DB."""
    try:
        with db_write_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cameras (user_id, name, stream_url, location, status, fps, latency, resolution, network_errors, decode_errors, last_error, is_rtsp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, name) DO UPDATE SET
                    stream_url=excluded.stream_url,
                    location=excluded.location,
                    status=excluded.status,
                    fps=excluded.fps,
                    latency=excluded.latency,
                    resolution=excluded.resolution,
                    network_errors=excluded.network_errors,
                    decode_errors=excluded.decode_errors,
                    last_error=excluded.last_error,
                    is_rtsp=excluded.is_rtsp
            """, (
                user_id, name, stream_url, location, status, fps, latency, resolution,
                kwargs.get("network_errors", 0),
                kwargs.get("decode_errors", 0),
                kwargs.get("last_error"),
                kwargs.get("is_rtsp", 0)
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error saving camera '{name}': {e}")
        return False


def update_camera_status(name, status, fps=0.0, latency=0.0, user_id=None, **kwargs):
    """Updates camera online status, fps, and latency."""
    try:
        with db_write_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("""
                    UPDATE cameras 
                    SET status = ?, fps = ?, latency = ?
                    WHERE name = ? AND user_id = ?
                """, (status, fps, latency, name, user_id))
            else:
                cursor.execute("""
                    UPDATE cameras 
                    SET status = ?, fps = ?, latency = ?
                    WHERE name = ?
                """, (status, fps, latency, name))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error updating status for camera '{name}': {e}")
        return False


def get_camera(name, user_id=None):
    """Fetches camera details by camera name."""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM cameras WHERE name = ? AND user_id = ?", (name, user_id))
            else:
                cursor.execute("SELECT * FROM cameras WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching camera '{name}': {e}")
        return None


def get_all_cameras(user_id=None):
    """Fetches all registered cameras from database."""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM cameras WHERE user_id = ? ORDER BY id ASC", (user_id,))
            else:
                cursor.execute("SELECT * FROM cameras ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching cameras: {e}")
        return []


def save_event(event_type, severity="LOW", camera="Unknown", zone="General Area", confidence=0.0, duration=0.0, metadata=None, screenshot="", track_id=-1, user_id=1):
    """Saves a new event/detection to the database."""
    try:
        with db_write_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO events (user_id, timestamp, event_type, severity, camera, zone, track_id, confidence, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, timestamp, event_type, severity, camera, zone, track_id, confidence, duration, json.dumps(metadata) if metadata else None))
            new_id = cursor.lastrowid
            # Maintain the KPI rollup in the same transaction so the counters
            # can never drift from the events they summarise.
            try:
                cursor.execute("""
                    INSERT INTO event_stats_daily (user_id, day, event_type, severity, total, confidence_sum)
                    VALUES (?, ?, ?, ?, 1, ?)
                    ON CONFLICT(user_id, day, event_type, severity) DO UPDATE SET
                        total = total + 1,
                        confidence_sum = confidence_sum + excluded.confidence_sum
                """, (user_id, timestamp[:10], event_type,
                      (severity or "LOW").upper(), float(confidence or 0)))
            except sqlite3.OperationalError:
                # Rollup unavailable (pre-migration DB); events still record fine.
                pass
            conn.commit()
            return new_id
    except Exception as e:
        logger.error(f"Error saving event: {e}")
        return None


def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(token):
    return session.get("csrf_token") == token


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return jsonify({"error": "Authentication required", "status": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_csrf(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
            if not token or not validate_csrf_token(token):
                return jsonify({"error": "CSRF token missing or invalid", "status": "forbidden"}), 403
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
        rate_key = f"{client_ip}:{request.path}"
        if not _check_rate_limit(rate_key):
            return jsonify({"error": "Rate limit exceeded", "status": "too_many_requests"}), 429
        return f(*args, **kwargs)
    return decorated_function