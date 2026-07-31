from threading import Thread
from dashboard.app import app
from core.engine import run_engine
<<<<<<< HEAD
from database.db import create_tables
=======
>>>>>>> 2ad808518949971ad8ab73951416556e7319fb7e


def start_ai():
    run_engine()


if __name__ == "__main__":

<<<<<<< HEAD
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
        debug=False,
        threaded=True,
        use_reloader=False
    )
=======
    # Start AI in background thread
    ai_thread = Thread(target=start_ai, daemon=True)
    ai_thread.start()

    # Start dashboard
    app.run(
        debug=False,
        port=5000,
        threaded=True
    )  
>>>>>>> 2ad808518949971ad8ab73951416556e7319fb7e
