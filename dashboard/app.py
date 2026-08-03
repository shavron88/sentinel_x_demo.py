from flask import Flask, render_template, jsonify, Response

from dashboard.store import get_events, get_stats
from dashboard.stream import generate
from dashboard.timeline import get_timeline
from evidence.evidence_manager import get_gallery
from flask import send_from_directory
import os

app = Flask(__name__)


# ==========================
# HOME
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# LIVE VIDEO
# ==========================
@app.route("/video_feed")
def video_feed():
    print("Browser connected to video stream")

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ==========================
# EVENTS API
# ==========================
@app.route("/events")
def events():
    return jsonify(get_events())





# ==========================
# LIVE STATS API
# ==========================
@app.route("/stats")
def stats():
    return jsonify(get_stats())



@app.route("/timeline")
def timeline():

    return {

        "timeline": get_timeline()

    }
    



@app.route("/evidence/screenshots/<filename>", endpoint="evidence_screenshots")
def evidence_screenshots(filename):

    return send_from_directory(
        "../evidence/screenshots",
        filename
    )



@app.route("/cameras")
def cameras():
    return render_template("cameras.html")


@app.route("/incidents")
def incidents():
    return render_template("incidents.html")


@app.route("/evidence")
def evidence_page():
    return render_template("evidence.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/gallery")
def gallery():

    folder="evidence/screenshots"

    images=[]

    if os.path.exists(folder):

        images=sorted(

            os.listdir(folder),

            reverse=True

        )[:15]

    return jsonify({

        "images":images

    })


@app.route("/evidence/<filename>", endpoint="evidence_file")
def evidence_file(filename):

    return send_from_directory(

        "evidence/screenshots",

        filename

    )

@app.route("/api/cameras")
def api_cameras():

    cameras = [

        {
            "id":1,
            "name":"Camera 01",
            "location":"Main Entrance",
            "status":"ONLINE",
            "fps":30,
            "resolution":"640x480",
            "stream":"/video_feed"
        },

        {
            "id":2,
            "name":"Camera 02",
            "location":"Parking Area",
            "status":"ONLINE",
            "fps":28,
            "resolution":"640x480",
            "stream":"/video_feed"
        },

        {
            "id":3,
            "name":"Camera 03",
            "location":"Warehouse",
            "status":"OFFLINE",
            "fps":0,
            "resolution":"640x480",
            "stream":""
        }

    ]

    return jsonify(cameras)

@app.route("/camera/<int:camera_id>")
def camera_page(camera_id):

    return render_template(

        "camera_view.html",

        camera_id=camera_id

    )

@app.route("/api/incidents")
def api_incidents():

    incidents = [

        {
            "id":1,
            "type":"FALL DETECTED",
            "zone":"Restricted Zone",
            "time":"10:42 PM",
            "severity":"HIGH",
            "description":"Person ID 5 collapsed. Evidence available."
        },

        {
            "id":2,
            "type":"LOITERING",
            "zone":"Entrance Area",
            "time":"10:38 PM",
            "severity":"MEDIUM",
            "description":"Person ID 8 stayed 15 seconds."
        },

        {
            "id":3,
            "type":"CROWD DETECTED",
            "zone":"Lobby",
            "time":"10:35 PM",
            "severity":"LOW",
            "description":"Crowd threshold exceeded."
        }

    ]

    return jsonify(incidents)

@app.route("/api/evidence")
def api_evidence():

    from evidence.evidence_manager import get_gallery

    return jsonify({

        "evidence":get_gallery()

    })

@app.route("/analytics_data")
def analytics_data():

    return jsonify({

        "total":18,

        "people":10,

        "vehicles":5,

        "falls":2,

        "weapons":1,

        "threat":"LOW",

        "labels":[

            "Mon",

            "Tue",

            "Wed",

            "Thu",

            "Fri",

            "Sat",

            "Sun"

        ],

        "values":[

            2,

            5,

            3,

            8,

            6,

            9,

            4

        ],

        "events":[

            {

                "event":"PERSON_DETECTED",

                "time":"10:21",

                "severity":"LOW"

            },

            {

                "event":"FALL_DETECTED",

                "time":"10:35",

                "severity":"HIGH"

            },

            {

                "event":"VEHICLE",

                "time":"10:45",

                "severity":"LOW"

            }

        ]

    })

@app.route("/reports_data")
def reports_data():

    return jsonify({

        "camera_online":4,

        "total_events":58,

        "total_evidence":34,

        "threat_level":"MEDIUM",

        "event_summary":[

            {

                "name":"Person",

                "count":24

            },

            {

                "name":"Vehicle",

                "count":16

            },

            {

                "name":"Fall",

                "count":3

            },

            {

                "name":"Loitering",

                "count":8

            },

            {

                "name":"Weapon",

                "count":1

            }

        ],

        "camera_summary":[

            {

                "name":"Camera 01",

                "status":"ONLINE",

                "events":18

            },

            {

                "name":"Camera 02",

                "status":"ONLINE",

                "events":14

            },

            {

                "name":"Camera 03",

                "status":"OFFLINE",

                "events":"--"

            },

            {

                "name":"Camera 04",

                "status":"ONLINE",

                "events":26

            }

        ],

        "evidence":{

            "images":34,

            "today":11,

            "storage":"428 MB"

        },

        "high_priority":[

            {

                "event":"Fall Detection",

                "camera":"Camera 01",

                "location":"Main Entrance",

                "time":"10:45 PM"

            },

            {

                "event":"Weapon Detection",

                "camera":"Camera 03",

                "location":"Parking",

                "time":"09:52 PM"

            }

        ]

    })

@app.route("/live-wall")
def live_wall():

    return render_template("live_wall.html")

@app.route("/security-map")
def security_map():

    return render_template("security_map.html")