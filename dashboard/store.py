from threading import Lock

# ==========================
# Thread Safety
# ==========================
lock = Lock()

# ==========================
# Recent Events
# ==========================
events = []

# ==========================
# Live Statistics
# ==========================
stats = {
    "persons": 0,
    "vehicles": 0,
    "alerts": 0,
    "threat": "LOW",
    "fps": 0
}


# ==========================
# EVENTS
# ==========================
def add_event(event):
    global events

    with lock:
        events.insert(0, event)

        # Keep only latest 50 events
        events = events[:50]

        stats["alerts"] = len(events)


def get_events():
    with lock:
        return list(events)


# ==========================
# STATS
# ==========================
def update_stats(persons=None,
                 vehicles=None,
                 threat=None,
                 fps=None):

    print("update_stats called")
    print("persons =", persons)

    with lock:

        if persons is not None:
            stats["persons"] = persons

        if vehicles is not None:
            stats["vehicles"] = vehicles

        if threat is not None:
            stats["threat"] = threat

        if fps is not None:
            stats["fps"] = fps

    print("Current stats:", stats)


def get_stats():
    with lock:
        return dict(stats)