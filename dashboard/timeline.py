timeline = []


def add_incident(event):

    global timeline

    timeline.insert(0, event)

    # Keep last 50 incidents
    timeline = timeline[:50]


def get_timeline():

    return timeline