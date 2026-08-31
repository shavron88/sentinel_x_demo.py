"""
SentinelX Authentication Module with Email OTP Verification
"""
import os
import sqlite3
import hashlib
import secrets
import time
import random
from datetime import datetime, timedelta
from flask import session, request, jsonify

DB_PATH = "sentinelx.db"
DEMO_USERNAME = os.getenv("SENTINELX_USER", "sentinelx_admin")
DEMO_PASSWORD_HASH = hashlib.sha256(
    os.getenv("SENTINELX_PASSWORD", "SentinelX_SecurePassword2026!").encode()
).hexdigest()

SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT", "60"))
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60
_rate_limit_store = {}

# Temporary store for pending OTP verifications { email: {"otp": "123456", "expires": timestamp, "username": ..., "password_hash": ...} }
_pending_otp_store = {}


def _check_rate_limit(key):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if t > window_start]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    _rate_limit_store[key].append(now)
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash, is_verified FROM admin_users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            if row[2] == 0:
                return False, "Account not verified. Please complete signup verification."
            if row[1] == password_hash:
                session.clear()
                session["authenticated"] = True
                session["username"] = username
                session["user_id"] = row[0]
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


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_verified INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def initiate_signup(username, password, email):
    """Step 1: Validate details, generate OTP, store temporarily, and send email."""
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

    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin_users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return False, "Username or email already exists"
        conn.close()
    except Exception as e:
        return False, "Database error during registration check"

    # Generate 6-digit OTP
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    expiry = time.time() + 300  # Valid for 5 minutes

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Store in memory temporarily
    _pending_otp_store[email] = {
        "otp": otp,
        "expires": expiry,
        "username": username,
        "password_hash": password_hash
    }

    # Print to console (In production, replace this with an SMTP email sender)
    print(f"\n========================================")
    print(f" [SENTINEL-X OTP] Email: {email}")
    print(f" [SENTINEL-X OTP] Your Verification Code is: {otp}")
    print(f"========================================\n")

    return True, "OTP sent successfully to your email. Please verify to complete registration."


def signup(username, password, email):
    """Alias wrapper to satisfy dashboard/app.py import expectations."""
    return initiate_signup(username, password, email)


def verify_otp_and_register(email, otp_code):
    """Step 2: Verify OTP code and save user permanently to database."""
    if email not in _pending_otp_store:
        return False, "No active signup request found for this email. Please sign up again."

    record = _pending_otp_store[email]

    if time.time() > record["expires"]:
        del _pending_otp_store[email]
        return False, "OTP has expired. Please sign up again."

    if record["otp"] != otp_code.strip():
        return False, "Invalid OTP code. Please try again."

    # OTP is correct, save user to database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash, email, is_verified) VALUES (?, ?, ?, 1)",
            (record["username"], record["password_hash"], email)
        )
        conn.commit()
        conn.close()

        # Clean up temporary store
        del _pending_otp_store[email]
        return True, "Account successfully verified and created!"
    except Exception as e:
        print(f"Final signup database error: {e}")
        return False, "Failed to create account. Please try again."


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