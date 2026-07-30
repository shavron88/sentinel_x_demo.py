from flask import Flask, render_template, jsonify, Response

from dashboard.store import get_events, get_stats
from dashboard.stream import generate
from dashboard.store import get_stats
from dashboard.timeline import get_timeline
from evidence.evidence_manager import get_gallery
from flask import send_from_directory

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
    

@app.route("/gallery")
def gallery():

    return {

        "images": get_gallery()

    }

@app.route("/evidence/screenshots/<filename>")
def evidence(filename):

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