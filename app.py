from threading import Thread
from dashboard.app import app
from core.engine import run_engine
from database.db import create_tables


def start_ai():
    run_engine()


if __name__ == "__main__":
    # Create Database & Tables
    create_tables()

    # Start AI Thread
    ai_thread = Thread(target=start_ai, daemon=True)
    ai_thread.start()

    print("====================================")
    print("Dashboard Starting...")
    print("Open Browser: http://127.0.0.1:5000")
    print("====================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=False
    )
