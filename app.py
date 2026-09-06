import sys
import os
from pathlib import Path
from threading import Thread

# Ensure Project Root is in Python Path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Imports
from dashboard.app import app

# Optional DB and Core Engine setup
try:
    from database.db import init_db
    init_db()
except ImportError:
    pass

try:
    from core.engine import run_engine
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False


def start_ai():
    from core.engine import run_engine
    run_engine()


if __name__ == "__main__":
    if HAS_ENGINE:
        ai_thread = Thread(target=start_ai, daemon=True)
        ai_thread.start()
        print("✔ AI Engine Started in background thread.")

    print("====================================")
    print("   SentinelX AI Dashboard Starting   ")
    print("   Open Browser: http://127.0.0.1:5000")
    print("====================================")

    from werkzeug.serving import make_server
    server = make_server("127.0.0.1", 5000, app, threaded=True)
    server.serve_forever()