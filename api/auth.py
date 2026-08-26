"""
SentinelX Authentication Module

<<<<<<< HEAD
Database-backed secure authentication for the SentinelX security event monitoring system.
"""
import os
import sqlite3
=======
Simple session-based authentication for the hackathon demo.
In production, replace with proper user management and JWT tokens.
"""
import os
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from flask import session, request, jsonify

<<<<<<< HEAD
DB_PATH = "sentinelx.db"
=======
# Demo credentials (in production, use a proper database)
DEMO_USERNAME = os.getenv("SENTINELX_USER", "sentinelx")
DEMO_PASSWORD_HASH = hashlib.sha256(
    os.getenv("SENTINELX_PASSWORD", "auth").encode()
).hexdigest()
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227

# Session settings
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT", "60"))

# Rate limiting settings
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60
_rate_limit_store = {}


def _check_rate_limit(key):
    """Check if the rate limit has been exceeded for the given key."""
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
    """Check if the current session is authenticated and not expired."""
    if "authenticated" not in session:
        return False
    
    if session.get("authenticated") != True:
        return False
    
<<<<<<< HEAD
=======
    # Check session expiration
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
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
    
<<<<<<< HEAD
=======
    # Update last active time
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    session["last_active"] = datetime.now().isoformat()
    return True


def login(username, password):
<<<<<<< HEAD
    """Attempt to log in by validating against the SQLite database hash."""
=======
    """Attempt to log in with the given credentials."""
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    if not username or not password:
        return False, "Username and password required"
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
<<<<<<< HEAD
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM admin_users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == password_hash:
            session.clear()
            session["authenticated"] = True
            session["username"] = username
            session["email"] = f"{username}@sentinelx.ai"
            session["role"] = "System Administrator"
            session["last_active"] = datetime.now().isoformat()
            session["csrf_token"] = secrets.token_hex(32)
            return True, "Login successful"
            
    except Exception as e:
        print(f"Database authentication error: {e}")
        
=======
    if username == DEMO_USERNAME and password_hash == DEMO_PASSWORD_HASH:
        session.clear()
        session["authenticated"] = True
        session["username"] = username
        session["email"] = f"{username}@sentinelx.ai"
        session["role"] = "System Administrator"
        session["last_active"] = datetime.now().isoformat()
        session["csrf_token"] = secrets.token_hex(32)
        return True, "Login successful"
    
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
    return False, "Invalid credentials"


def logout():
    """Log out the current user."""
    session.clear()


def get_csrf_token():
    """Get the current CSRF token, or generate one if missing."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(token):
    """Validate a CSRF token against the session."""
    return session.get("csrf_token") == token


def require_auth(f):
    """Decorator to require authentication for a route."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return jsonify({"error": "Authentication required", "status": "unauthorized"}), 401
        return f(*args, **kwargs)
    
    return decorated_function


def require_csrf(f):
    """Decorator to require valid CSRF token for state-changing methods."""
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
    """Decorator to apply rate limiting to a route."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
<<<<<<< HEAD
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
=======
        client_ip = request.remote_addr or "unknown"
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
        rate_key = f"{client_ip}:{request.path}"
        
        if not _check_rate_limit(rate_key):
            return jsonify({"error": "Rate limit exceeded", "status": "too_many_requests"}), 429
        
        return f(*args, **kwargs)
    
<<<<<<< HEAD
    return decorated_function
=======
    return decorated_function
>>>>>>> e9db60090b9098332b468e1f462e3026c107e227
