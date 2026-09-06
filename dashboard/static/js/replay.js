let replayData = null;
let isPlaying = false;

const $ = (id) => document.getElementById(id);

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = String(text);
    return div.innerHTML;
}

function setText(id, value, fallback) {
    const el = $(id);
    if (!el) return;
    el.textContent = (value == null || value === "") ? (fallback || "--") : value;
}

function setPriority(severity) {
    const wrap = $("replayPriority");
    const text = $("replayPriorityText");
    if (!wrap || !text) return;
    const sev = (severity || "").toUpperCase();
    let label = "INFO";
    let cls = "replay-priority";
    if (sev === "CRITICAL") { label = "CRITICAL"; cls += " replay-priority--critical"; }
    else if (sev === "HIGH") { label = "HIGH PRIORITY"; cls += " replay-priority--high"; }
    else if (sev === "MEDIUM" || sev === "MODERATE") { label = "MEDIUM"; cls += " replay-priority--medium"; }
    else if (sev === "LOW") { label = "LOW"; cls += " replay-priority--low"; }
    else { label = sev || "INFO"; }
    wrap.className = cls;
    text.textContent = label;
}

function showViewportLoader(show) {
    const el = $("replayViewportLoader");
    if (el) el.style.display = show ? "flex" : "none";
}

function showViewportEmpty(message) {
    const empty = $("replayViewportEmpty");
    const msg = $("replayViewportEmptyMsg");
    if (!empty) return;
    empty.style.display = "flex";
    if (msg) msg.textContent = message || "No replay available.";
    showViewportLoader(false);
    const ctrls = $("replayControls");
    if (ctrls) ctrls.style.display = "none";
    const v = $("incidentVideo");
    if (v) v.style.display = "none";
    const p = $("replayPoster");
    if (p) p.style.display = "none";
}

function showViewportMedia(videoSrc, posterSrc) {
    const empty = $("replayViewportEmpty");
    if (empty) empty.style.display = "none";
    const v = $("incidentVideo");
    const p = $("replayPoster");
    const ctrls = $("replayControls");
    const dl = $("replayDownloadBtn");

    if (videoSrc) {
        if (p) p.style.display = "none";
        if (v) {
            const source = v.querySelector("source");
            if (source) source.src = videoSrc;
            v.load();
            v.style.display = "block";
        }
        if (dl) {
            dl.style.display = "inline-flex";
            dl.onclick = function () {
                const a = document.createElement("a");
                a.href = videoSrc;
                a.download = "incident_replay.mp4";
                document.body.appendChild(a);
                a.click();
                a.remove();
            };
        }
        if (ctrls) ctrls.style.display = "flex";
        showViewportLoader(false);
    } else if (posterSrc) {
        if (v) v.style.display = "none";
        if (p) {
            p.src = posterSrc;
            p.style.display = "block";
        }
        if (dl) {
            dl.style.display = "inline-flex";
            dl.onclick = function () { window.open(posterSrc, "_blank"); };
        }
        if (ctrls) ctrls.style.display = "none";
        showViewportLoader(false);
    } else {
        showViewportEmpty("No video or image evidence was found for this incident.");
    }
}

function updateOverlayTimestamp() {
    const el = $("replayOverlayTime");
    if (!el) return;
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");
    el.textContent = now.toLocaleDateString() + " \u00b7 " + hh + ":" + mm + ":" + ss;
}

async function loadReplay() {
    const eventId = new URLSearchParams(window.location.search).get("event") || "1";
    showViewportLoader(true);

    try {
        const response = await fetch("/api/replay/event/" + encodeURIComponent(eventId), {
            credentials: "same-origin"
        });
        if (!response.ok) throw new Error("HTTP " + response.status);
        const data = await response.json();

        if (!data || !data.success || !data.replay) {
            showViewportEmpty((data && (data.message || data.error)) || "No replay data found for this incident.");
            return;
        }

        replayData = data.replay;
        const r = replayData;

        // Overlay + summary
        setText("replayOverlayCamera", r.camera || "Camera");
        setText("replayEvent", r.event_type || r.event || "Unknown Event");
        setText("replayCamera", r.camera || "Unknown");
        setText("replayTime", r.timestamp ? new Date(r.timestamp).toLocaleString() : "--");
        setText("replayStatus", (r.severity || "INFO").toString().toUpperCase());
        setText("replayConfidence", r.confidence != null ? Number(r.confidence).toFixed(1) + "%" : "--");
        setText("replayDuration", r.duration != null ? r.duration + " seconds" : "--");
        setText("replayResolve", r.status || (r.severity === "HIGH" || r.severity === "CRITICAL" ? "Active" : "Resolved"));

        setPriority(r.severity || r.priority);

        updateOverlayTimestamp();
        setInterval(updateOverlayTimestamp, 1000);

        // Media
        const imagePath = r.image_path || (r.metadata && r.metadata.image_path) || "";
        if (imagePath && /\.mp4($|\?)/i.test(imagePath)) {
            showViewportMedia(imagePath, null);
        } else if (imagePath) {
            showViewportMedia(null, imagePath);
        } else {
            showViewportEmpty("No video or image evidence available for this incident.");
        }
    } catch (err) {
        console.error("Failed to load replay:", err);
        showViewportEmpty("Unable to load replay data. The backend could not be reached.");
    }
}

function togglePlay() {
    const video = $("incidentVideo");
    const playBtn = $("replayPlayBtn");
    const playIcon = $("replayPlayIcon");
    const playText = $("replayPlayText");
    if (!video) return;
    if (video.paused) {
        video.play().catch(function () {});
        isPlaying = true;
        if (playIcon) playIcon.innerHTML = '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>';
        if (playText) playText.textContent = "Pause";
    } else {
        video.pause();
        isPlaying = false;
        if (playIcon) playIcon.innerHTML = '<polygon points="6 4 20 12 6 20 6 4"></polygon>';
        if (playText) playText.textContent = "Play";
    }
}

function skipBack() {
    const video = $("incidentVideo");
    if (video) {
        try { video.currentTime = Math.max(0, video.currentTime - 10); } catch (e) {}
    }
}

function skipForward() {
    const video = $("incidentVideo");
    if (video) {
        try { video.currentTime = Math.min((video.duration || 0), video.currentTime + 10); } catch (e) {}
    }
}

// Keep play button label in sync with native controls
document.addEventListener("DOMContentLoaded", function () {
    const video = $("incidentVideo");
    if (!video) return;
    video.addEventListener("play", function () {
        const playIcon = $("replayPlayIcon");
        const playText = $("replayPlayText");
        if (playIcon) playIcon.innerHTML = '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>';
        if (playText) playText.textContent = "Pause";
        isPlaying = true;
    });
    video.addEventListener("pause", function () {
        const playIcon = $("replayPlayIcon");
        const playText = $("replayPlayText");
        if (playIcon) playIcon.innerHTML = '<polygon points="6 4 20 12 6 20 6 4"></polygon>';
        if (playText) playText.textContent = "Play";
        isPlaying = false;
    });
});

loadReplay();