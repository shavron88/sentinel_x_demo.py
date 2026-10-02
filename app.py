import sys
import os
from pathlib import Path
from threading import Thread

# Ensure Project Root is in Python Path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Imports
from dashboard.app import app, start_background_services, start_camera_services

# Optional DB and Core Engine setup
try:
    from database.db import init_db
    init_db()
except ImportError:
    pass


def _port():
    return int(os.getenv("PORT", "5000"))


def _host():
    return os.getenv("HOST", "127.0.0.1")


def shutdown():
    """Stops the detection engine and releases camera handles."""
    stop_event = app.config.get("SENTINELX_STOP_EVENT")
    if stop_event is not None:
        stop_event.set()
    thread = app.config.get("SENTINELX_ENGINE_THREAD")
    if thread is not None:
        thread.join(timeout=60)
    print("SentinelX stopped cleanly.")


def serve():
    """Starts the services and serves the dashboard.

    ``dashboard.app`` already starts the detection engine and camera services on
    import; calling the starters here too is harmless because they are
    idempotent, and it keeps this entrypoint correct if autostart is disabled.
    """
    start_background_services()
    start_camera_services()

    from werkzeug.serving import make_server

    print("====================================")
    print("   SentinelX AI Dashboard Starting   ")
    print(f"   Open Browser: http://{_host()}:{_port()}")
    print("====================================")

    server = make_server(_host(), _port(), app, threaded=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down SentinelX...")
    finally:
        shutdown()


if __name__ == "__main__":
    serve()
