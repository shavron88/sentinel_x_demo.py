from threading import Thread
from dashboard.app import app
from core.engine import run_engine


def start_ai():
    run_engine()


if __name__ == "__main__":

    # Start AI in background thread
    ai_thread = Thread(target=start_ai, daemon=True)
    ai_thread.start()

    # Start dashboard
    app.run(
        debug=False,
        port=5000,
        threaded=True
    )  
