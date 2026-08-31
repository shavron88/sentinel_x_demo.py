timeline = []


def add_incident(event, user_id=None):
    global timeline
    timeline.insert(0, event)
    timeline = timeline[:50]


def get_timeline(user_id=None):
    return timeline