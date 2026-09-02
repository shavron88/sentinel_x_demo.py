function animateValue(id, start, end, duration = 500){
    if(start === end) return;

    const element = document.getElementById(id);

    if(!element) return;

    let startTimestamp = null;

    function step(timestamp){

        if(!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min(
            (timestamp - startTimestamp) / duration,
            1
        );
        const value = Math.floor(
            progress * (end - start) + start
        );

        element.innerText = value;

        if(progress < 1){

            window.requestAnimationFrame(step);

        }

    }

    window.requestAnimationFrame(step);

}


// Added missing updateSystemStatus function to prevent ReferenceError
function updateSystemStatus(stats) {
    const statusEl = document.getElementById('system-status');
    if (statusEl && stats && stats.threat) {
        statusEl.innerText = stats.threat;
    }
}
function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function updateDashboard() {
    // Skip if this page has no dashboard elements
    if (!document.getElementById("stats-grid") && !document.getElementById("person-count") && !document.getElementById("kpi-threat")) {
        return;
    }

    showSkeletonCards("stats-grid", 4);

    try {
        const response = await fetch("/stats");
        const stats = await response.json();

        hideSkeletons();

        // Clear any previous error message on successful fetch
        const errorEl = document.getElementById("dashboardError");
        if (errorEl) {
            errorEl.innerHTML = "";
            errorEl.style.display = "none";
        }

        if (!stats || Object.keys(stats).length === 0) {
            showEmptyState("emptyState", "No Data Available", "Dashboard data is not available.", [{label:"Refresh", onclick:"updateDashboard()", class:"btn-primary"}]);
            return;
        }

        const cameraFPS = document.getElementById("camera-fps");

        if(cameraFPS){
            cameraFPS.innerText = stats.fps;
        }

        const personElement = document.getElementById("person-count");
        const vehicleElement = document.getElementById("vehicle-count");
        const alertElement = document.getElementById("alert-count");
        const fpsElement = document.getElementById("fps");
        updateSystemStatus(stats);

        if(document.getElementById("person-count-footer"))
            document.getElementById("person-count-footer").innerText = stats.persons;

        if(document.getElementById("vehicle-count-footer"))
            document.getElementById("vehicle-count-footer").innerText = stats.vehicles;

        if(document.getElementById("fps-footer"))
            document.getElementById("fps-footer").innerText = stats.fps;

        if(personElement){
            animateValue("person-count", Number(personElement.innerText) || 0, stats.persons);
        }

        if(vehicleElement){
            animateValue("vehicle-count", Number(vehicleElement.innerText) || 0, stats.vehicles);
        }

        if(alertElement){
            animateValue("alert-count", Number(alertElement.innerText) || 0, stats.alerts);
        }

        if(fpsElement){
            animateValue("fps", Number(fpsElement.innerText) || 0, stats.fps);
        }

        const threat = document.getElementById("threat-level");
        const fill = document.getElementById("threat-fill");

        if(threat){
            threat.innerText = stats.threat;

            if(stats.threat === "LOW"){
                fill.style.width = "30%";
                fill.style.background = "#22c55e";
            }
            else if(stats.threat === "MEDIUM"){
                fill.style.width = "65%";
                fill.style.background = "#facc15";
            }
            else{
                fill.style.width = "100%";
                fill.style.background = "#ef4444";
            }
        }

        if(document.getElementById("fps"))
            document.getElementById("fps").innerText = stats.fps;
        if(document.getElementById("camera-fps"))
            document.getElementById("camera-fps").innerText = stats.fps;

        if(document.getElementById("fps-overlay"))
            document.getElementById("fps-overlay").innerText = "FPS : " + stats.fps;

        if(document.getElementById("health-threat"))
            document.getElementById("health-threat").innerText = stats.threat;

        // Update new KPI bar
        await updateKPIBar(stats);

    } catch (err) {
        console.log("Dashboard Error:", err);
        const errorEl = document.getElementById("dashboardError");
        if (errorEl) {
            errorEl.innerHTML = '<div style="color:#ef4444;padding:10px;text-align:center;">Unable to load dashboard data. <button onclick="updateDashboard()" style="background:none;border:none;color:#3b82f6;cursor:pointer;text-decoration:underline;">Retry</button></div>';
            errorEl.style.display = "block";
        }
    }
}


async function loadAIFeed() {
    // Skip if this page has no timeline element
    if (!document.getElementById("timeline")) return;

    try {
        const response = await fetch("/timeline");

        const data = await response.json();
        const feed = document.getElementById("timeline");

        if(!feed) return;

        feed.innerHTML = "";
        const timelineItems = data.timeline || [];

        if(timelineItems.length === 0){

            feed.innerHTML = '<div style="color:#64748b;font-size:12px;padding:10px;">No recent events</div>';

            return;

        }

        timelineItems.forEach((item, index) => {

            const event = item.event_type || item.event || "Unknown Event";

            const severity = item.severity || "LOW";

            const zone = item.zone || "Unknown";

            const timestamp = item.timestamp || item.time || "";

            const thumbnail = item.thumbnail || item.image_url || "";

            const extraDetails = item.details || item.description || "";

            const timeStr = (function() {
                if (!timestamp) return "--:--";
                var d = new Date(timestamp);
                return isNaN(d.getTime()) ? "--:--" : d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
            })();

            const truncateTitle = event.length > 80;
            const shortEvent = truncateTitle ? event.slice(0, 80) + "..." : event;
            const hasExtra = extraDetails || thumbnail;

            const div = document.createElement("div");

            div.className = `ai-feed-item feed-${severity.toLowerCase()}`;

            let html = '';

            // Optional thumbnail image with containment
            if (thumbnail) {
                html += '<div class="ai-feed-img"><img src="' + escapeHtml(thumbnail) + '" alt="Evidence thumbnail" onerror="this.style.display=\'none\';this.closest(\'.ai-feed-img\').style.display=\'none\';"></div>';
            }

            html += '<span class="ai-feed-time">' + escapeHtml(timeStr) + '</span>';

            html += '<div class="ai-feed-content">';

            // Truncated title (always shown, CSS line-clamp limits to 2 lines)
            html += '<div class="ai-feed-title">' + escapeHtml(shortEvent) + '</div>';

            // Show More button for long descriptions
            if (truncateTitle) {
                html += '<span class="ai-feed-more" onclick="document.getElementById(\'extra-' + index + '\').classList.add(\'visible\'); this.style.display=\'none\';">Show More</span>';
                html += '<div class="ai-feed-extra" id="extra-' + index + '">' + escapeHtml(event.slice(80)) + '</div>';
            }

            // Extra details if present
            if (extraDetails) {
                html += '<div class="ai-feed-extra">' + escapeHtml(extraDetails) + '</div>';
            }

            html += '<div class="ai-feed-meta">';
            html += '<span><svg class="chip-icon" style="width:12px;height:12px;vertical-align:-1px;margin-right:3px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>' + escapeHtml(zone) + '</span>';

            if (hasExtra) {
                html += '<span><svg class="chip-icon" style="width:12px;height:12px;vertical-align:-1px;margin-right:3px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4v4a4 4 0 1 0 0-8V8a4 4 0 0 0 0 8z"/></svg>Details</span>';
            }

            html += '</div>';  // end ai-feed-meta
            html += '</div>';  // end ai-feed-content
            html += '<span class="ai-feed-badge ' + severity.toLowerCase() + '">' + escapeHtml(severity) + '</span>';

            div.innerHTML = html;

            feed.appendChild(div);

        });

        feed.scrollTop = feed.scrollHeight;

    } catch(err) {

        console.log(err);

        if(feed){

            feed.innerHTML = '<div style="color:#ef4444;font-size:12px;padding:10px;">Unable to load timeline. <button onclick="loadAIFeed()" style="background:none;border:none;color:#3b82f6;cursor:pointer;text-decoration:underline;">Retry</button></div>';

        }

    }

}
// Refresh at reasonable intervals to avoid excessive server load
window._dashboardIntervals = window._dashboardIntervals || [];
window._dashboardIntervals.push(setInterval(updateDashboard, 2000));
window._dashboardIntervals.push(setInterval(loadAIFeed, 5000));

let lastAlertedEventId = null;

async function updateAlerts() {
    try {
        const response = await fetch("/events");
        const events = await response.json();
        if (!Array.isArray(events) || events.length === 0) return;
        const latest = events[0];
        if (latest.id !== lastAlertedEventId && (latest.severity === "HIGH" || latest.severity === "CRITICAL")) {
            lastAlertedEventId = latest.id;
            const type = latest.severity === "CRITICAL" ? "danger" : "warning";
            showToast(
                latest.severity === "CRITICAL" ? "Critical Alert" : "High Alert",
                `${latest.event_type || "Event"} detected at ${latest.zone || "Unknown zone"}`,
                type
            );
        }
    } catch (e) {
        // silent
    }
}

window._dashboardIntervals.push(setInterval(updateAlerts, 5000));
updateAlerts();

// Run immediately
updateDashboard();
loadAIFeed();
// ==========================
// Evidence Gallery
// ==========================
async function loadGallery(){
 try{

    const response = await fetch("/gallery");

    const data = await response.json();
    const gallery = document.getElementById("gallery");

    if(!gallery) return;

    let html="";
    const items = Array.isArray(data) ? data : [];

    const fifteenMinutesAgo = new Date(Date.now() - 15 * 60 * 1000);

    const filtered = items.filter(item => {
        const t = new Date(item.timestamp || item.time || "");
        return t >= fifteenMinutesAgo;
    });

    const latest = filtered.slice(0, 10);

    if (latest.length < 10) {
        const older = items.filter(item => !filtered.includes(item)).slice(0, 10 - latest.length);
        latest.push(...older);
    }

    latest.forEach(item => {

        const raw = item.image_path || "";

        const filename = raw.split(/[\\/]/).pop();

        if(!filename) return;

        html += `
        <a href="/evidence" title="View all evidence">
            <img
                src="/evidence/screenshots/${filename}"
                class="gallery-image"
                loading="lazy"
                onerror="this.closest('a').style.display='none'"
            >
        </a>
        `;
    });

    gallery.innerHTML=html;
 } catch(e){
    console.error("loadGallery failed", e);
    if (typeof hideSkeletons === "function") hideSkeletons();
 }
}

window._dashboardIntervals.push(setInterval(loadGallery, 3000));
loadGallery();

/* ==========================================
   DETECTION HISTORY CHART
========================================== */

async function updateKPIBar(stats){
    const threatEl = document.getElementById("kpi-threat");
    const camerasEl = document.getElementById("kpi-cameras");
    const camerasTotalEl = document.getElementById("kpi-cameras-total");
    const camerasDotEl = document.getElementById("kpi-cameras-dot");
    const camerasTextEl = document.getElementById("kpi-cameras-text");
    const accuracyEl = document.getElementById("kpi-accuracy");
    const accuracyDotEl = document.getElementById("kpi-accuracy-dot");
    const accuracyTextEl = document.getElementById("kpi-accuracy-text");
    const alertsEl = document.getElementById("kpi-alerts");
    const alertsDotEl = document.getElementById("kpi-alerts-dot");
    const alertsTextEl = document.getElementById("kpi-alerts-text");

    // Threat level
    if(threatEl){
        const threat = stats.threat || "LOW";
        threatEl.innerText = threat;
        const threatIndicator = threatEl.closest('.kpi-card')?.querySelector('.kpi-dot');
        const threatText = threatEl.closest('.kpi-card')?.querySelector('.kpi-text');
        if(threatIndicator){
            threatIndicator.className = 'kpi-dot ' + (threat === 'LOW' ? 'online' : threat === 'MEDIUM' ? 'warning' : 'error');
        }
        if(threatText) threatText.innerText = threat === 'LOW' ? 'Secure' : threat === 'MEDIUM' ? 'Caution' : 'Alert';
    }

    // Alerts
    if(alertsEl){
        const alertCount = stats.alerts || 0;
        alertsEl.innerText = String(alertCount).padStart(2, "0");
        if(alertsDotEl) alertsDotEl.className = 'kpi-dot ' + (alertCount > 5 ? 'error' : alertCount > 0 ? 'warning' : 'online');
        if(alertsTextEl) alertsTextEl.innerText = 'Today';
    }

    // Cameras - fetch from health endpoint
    if(camerasEl){
        try {
            const res = await fetch("/api/health");
            const data = await res.json();
            const camData = data.services?.cameras || {};
            const online = camData.online || 0;
            const total = camData.total || 0;
            camerasEl.innerText = online;
            if(camerasTotalEl) camerasTotalEl.innerText = '/' + total;
            if(camerasDotEl) camerasDotEl.className = 'kpi-dot ' + (online === total && total > 0 ? 'online' : online > 0 ? 'warning' : 'offline');
            if(camerasTextEl) camerasTextEl.innerText = online === total && total > 0 ? 'All Online' : online > 0 ? 'Partial' : 'Offline';
        } catch(e) {
            camerasEl.innerText = "--";
            if(camerasTotalEl) camerasTotalEl.innerText = '/--';
            if(camerasTextEl) camerasTextEl.innerText = 'Unknown';
        }
    }

    // Accuracy - from AI summary
    if(accuracyEl){
        try {
            const aiRes = await fetch("/ai_summary");
            const aiData = await aiRes.json();
            const conf = aiData.confidence || "--";
            accuracyEl.innerText = conf.replace('%', '');
            const confNum = parseFloat(conf) || 0;
            if(accuracyDotEl) accuracyDotEl.className = 'kpi-dot ' + (confNum >= 90 ? 'high' : confNum >= 70 ? 'warning' : 'offline');
            if(accuracyTextEl) accuracyTextEl.innerText = confNum >= 90 ? 'Excellent' : confNum >= 70 ? 'Good' : confNum > 0 ? 'Fair' : 'No Data';
        } catch(e) {
            accuracyEl.innerText = "--";
            if(accuracyDotEl) accuracyDotEl.className = 'kpi-dot';
            if(accuracyTextEl) accuracyTextEl.innerText = 'Unavailable';
        }
    }
}

/* ==========================================
   AI DETECTION OVERLAY
   Real data is loaded from /ai_summary
========================================== */

// AI overlay data is now fetched from backend via loadAISummary()

async function loadAISummary(){

    try{

        const response=await fetch("/ai_summary");
        const data=await response.json();

        const riskEl = document.getElementById("ai-risk-level");
        const riskFill = document.getElementById("ai-risk-fill");
        const detectionsEl = document.getElementById("ai-active-detections");
        const confidenceEl = document.getElementById("ai-confidence");
        const recommendationEl = document.getElementById("ai-recommendation");

        if(riskEl) riskEl.innerText = data.risk || "LOW";
        if(riskFill) {
            const width = data.risk === "HIGH" ? "90%" : data.risk === "MEDIUM" ? "60%" : "25%";
            riskFill.style.width = width;
        }
        const detCount = data.detections;
        if(detectionsEl) detectionsEl.innerText = detCount != null ? (detCount + " Detections") : "-- Persons";
        if(confidenceEl) confidenceEl.innerText = data.confidence || "--%";
        if(recommendationEl) recommendationEl.innerText = data.recommendation || "--";

    }
    catch(e){

        console.log(e);

    }

}

/* ==========================================
   SYSTEM HEALTH STATUS CARDS
========================================== */

function setSystemDot(dotId, isOnline) {
    const dot = document.getElementById(dotId);
    if (!dot) return;
    dot.className = 'status-card-dot ' + (isOnline ? 'online' : 'offline');
}

async function updateSystemHealthCards() {
    // Dashboard is always active when page loads
    setSystemDot('sys-dot-dashboard', true);
    const dashVal = document.getElementById('sys-val-dashboard');
    if (dashVal) dashVal.textContent = 'Active';

    try {
        // Fetch both health endpoints for comprehensive data
        const [v1Res, healthRes] = await Promise.all([
            fetch('/api/v1/health').then(r => r.json()).catch(() => ({})),
            fetch('/api/health').then(r => r.json()).catch(() => ({}))
        ]);

        const aiEngine = v1Res.ai_engine || {};
        const services = healthRes.services || {};

        // AI Engine
        const aiStatus = (aiEngine.status || '').toLowerCase();
        const aiOk = aiStatus === 'healthy' || aiStatus === 'degraded';
        setSystemDot('sys-dot-ai', aiOk);
        const aiVal = document.getElementById('sys-val-ai');
        if (aiVal) aiVal.textContent = aiOk ? (aiStatus === 'healthy' ? 'Running' : 'Degraded') : 'Stopped';

        // YOLO Model
        const yoloStatus = (aiEngine.yolo_status || '').toLowerCase();
        const yoloOk = yoloStatus === 'loaded' || yoloStatus === 'running';
        setSystemDot('sys-dot-yolo', yoloOk);
        const yoloVal = document.getElementById('sys-val-yolo');
        if (yoloVal) yoloVal.textContent = yoloOk ? 'Loaded' : (yoloStatus || 'Unknown');

        // Detection Engine (tracker/worker)
        const trackerStatus = (aiEngine.tracker_status || '').toLowerCase();
        const trackerOk = trackerStatus === 'active' || trackerStatus === 'running';
        setSystemDot('sys-dot-detection', trackerOk);
        const detVal = document.getElementById('sys-val-detection');
        if (detVal) detVal.textContent = trackerOk ? 'Active' : (trackerStatus || 'Inactive');

        // Database
        const dbStatus = services.database?.status;
        const dbOk = dbStatus === 'HEALTHY';
        setSystemDot('sys-dot-db', dbOk);
        const dbVal = document.getElementById('sys-val-db');
        if (dbVal) dbVal.textContent = dbOk ? 'Connected' : (dbStatus ? 'Error' : 'Unknown');

        // Camera
        const camData = services.cameras || {};
        const camOnline = (camData.online || 0) > 0;
        setSystemDot('sys-dot-camera', camOnline);
        const camVal = document.getElementById('sys-val-camera');
        if (camVal) camVal.textContent = camOnline ? (camData.online + '/' + camData.total + ' Online') : 'No Cameras';

    } catch (e) {
        console.log('System health fetch error:', e);
        ['sys-dot-ai', 'sys-dot-yolo', 'sys-dot-detection', 'sys-dot-db', 'sys-dot-camera'].forEach(id => setSystemDot(id, false));
        ['sys-val-ai', 'sys-val-yolo', 'sys-val-detection', 'sys-val-db', 'sys-val-camera'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = 'Unknown';
        });
    }
}

window._dashboardIntervals.push(setInterval(updateSystemHealthCards, 5000));
updateSystemHealthCards();

window._dashboardIntervals.push(setInterval(loadAISummary, 5000));
loadAISummary();

/* ==========================================
   CAMERA CONTROLS
========================================== */

document.querySelectorAll(".camera-control-btn").forEach(btn => {
    btn.addEventListener("click", function() {

        const action = this.dataset.action;

        switch(action) {

            case "snapshot":

                showToast("Camera", "Snapshot captured", "success");

                break;

            case "record":

                this.classList.toggle("recording");

                const isRecording = this.classList.contains("recording");

                this.querySelector("span").innerText = isRecording ? "Stop" : "Record";

                showToast("Camera", isRecording ? "Recording started" : "Recording stopped", "info");

                break;

            case "ptz":

                showToast("Camera", "PTZ controls activated", "info");

                break;

            case "zoom":

                showToast("Camera", "Zoom toggled", "info");

                break;

            case "ai-tracking":

                this.classList.toggle("active");

                const tracking = this.classList.contains("active");

                showToast("AI", tracking ? "AI Tracking enabled" : "AI Tracking disabled", "success");

                break;

            case "export":

                showToast("Export", "Preparing export...", "info");

                break;

        }

    });
});

/* ==========================================
   PER-CAMERA DASHBOARD CARDS
========================================== */

const CAMERA_UPDATE_INTERVAL_MS = 2000;

function setText(id, value){
    const el = document.getElementById(id);
    if(el) el.innerText = value;
}

function setClassList(el, classes){
    if(!el) return;
    el.className = classes;
}

function updateStatusDot(dotId, status){
    const dot = document.getElementById(dotId);
    if(!dot) return;
    const s = String(status || "OFFLINE").toLowerCase();
    let state = "offline";
    if(["online", "playing"].includes(s)) state = "online";
    else if(["connecting", "reconnecting"].includes(s)) state = "connecting";
    else if(["error", "critical", "disconnected"].includes(s)) state = "error";
    dot.className = "status-dot " + state;
}

async function updateCameraCard(cameraName){
    try{
        const response = await fetch(`/api/camera/status?camera_name=${encodeURIComponent(cameraName)}`);
        if(!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        const status = data.status || "OFFLINE";
        const isVideo = data.is_video_file;
        const displayStatus = (isVideo && status === "ONLINE") ? "PLAYING" : status;

        setText(`cam-status-${cameraName}`, displayStatus);
        updateStatusDot(`cam-dot-${cameraName}`, displayStatus);

        setText(`cam-fps-${cameraName}`, data.fps != null ? data.fps : "0");
        setText(`cam-resolution-${cameraName}`, data.resolution || "--");
        setText(`cam-latency-${cameraName}`, data.latency != null ? `${data.latency} ms` : "--");
        setText(`cam-health-${cameraName}`, data.health || "--");
        setText(`cam-persons-${cameraName}`, data.persons != null ? data.persons : "0");
        setText(`cam-vehicles-${cameraName}`, data.vehicles != null ? data.vehicles : "0");

        const detections = data.detections;
        let detectionCount = 0;
        if(Array.isArray(detections)){
            detectionCount = detections.length;
        } else if(typeof detections === "number"){
            detectionCount = detections;
        }
        setText(`cam-detections-${cameraName}`, detectionCount);

        const recEl = document.getElementById(`cam-recording-${cameraName}`);
        if(recEl){
            recEl.innerText = data.is_recording ? "ON" : "OFF";
            recEl.style.color = data.is_recording ? "#ef4444" : "";
        }

        const aiEl = document.getElementById(`cam-ai-${cameraName}`);
        if(aiEl){
            const workerRunning = data.worker_status === "Running";
            aiEl.innerHTML = workerRunning
                ? '<span class="ai-dot online"></span> AI ACTIVE'
                : '<span class="ai-dot offline"></span> AI INACTIVE';
            aiEl.className = workerRunning ? "ai-active" : "";
            aiEl.style.color = workerRunning ? "#22c55e" : "#ef4444";
        }

        const zoneEl = document.getElementById(`cam-zone-${cameraName}`);
        if(zoneEl && data.zone){
            zoneEl.innerHTML = '<svg class="chip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>' + escapeHtml(data.zone);
        }
    } catch(err){
        console.log(`Camera status error (${cameraName}):`, err);
        setText(`cam-status-${cameraName}`, "OFFLINE");
        updateStatusDot(`cam-dot-${cameraName}`, "OFFLINE");
    }
}

function updateAllCameraCards(){
    document.querySelectorAll(".camera-hero[data-camera-name]").forEach(card => {
        const cameraName = card.dataset.cameraName;
        if(cameraName) updateCameraCard(cameraName);
    });
}

window._dashboardIntervals.push(setInterval(updateAllCameraCards, CAMERA_UPDATE_INTERVAL_MS));
updateAllCameraCards();

/* ==========================================
   PER-CAMERA CONTROLS (snapshot / record / replay)
========================================== */

document.querySelectorAll(".cam-btn").forEach(btn => {
    btn.addEventListener("click", async function(){
        const cameraName = this.dataset.camera;
        const action = this.dataset.action;
        if(!cameraName || !action) return;

        if(action === "snapshot"){
            try{
                const res = await fetch("/api/camera/snapshot", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({camera_name: cameraName})
                });
                const data = await res.json();
                showToast("Snapshot", data.success ? "Saved: " + data.image : (data.error || "Failed"), data.success ? "success" : "error");
            } catch(e){
                showToast("Snapshot", "Request failed", "error");
            }
            return;
        }

        if(action === "record"){
            const isRecording = this.classList.contains("recording");
            const endpoint = isRecording ? "/api/camera/stop-record" : "/api/camera/start-record";
            try{
                const res = await fetch(endpoint, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({camera_name: cameraName})
                });
                const data = await res.json();
                if(data.success){
                    this.classList.toggle("recording");
                    this.innerText = isRecording ? "Record" : "Stop";
                    showToast("Recording", data.message, "info");
                } else {
                    showToast("Recording", data.error || "Failed", "error");
                }
            } catch(e){
                showToast("Recording", "Request failed", "error");
            }
            return;
        }

        if(action === "replay"){
            window.open(`/replay?camera=${encodeURIComponent(cameraName)}`, "_blank");
            return;
        }
    });
});

/* ==========================================
   DETECTION HISTORY CHART
========================================== */

let detectionChart;

function initDetectionChart(){
    const ctx = document.getElementById("detectionChart");
    if(!ctx) return;
    const labels = [];
    const now = new Date();
    for(let i = 11; i >= 0; i--){
        const d = new Date(now.getTime() - i * 60000);
        labels.push(d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }));
    }

    const t = (typeof getChartTheme === 'function') ? getChartTheme() : {
        tooltipBg:'rgba(15,23,42,.9)', tooltipBorder:'rgba(255,255,255,.1)',
        tooltipTitle:'#e2e8f0', tooltipBody:'#94a3b8', gridColor:'rgba(255,255,255,.05)', tickColor:'#64748b'
    };

    detectionChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Persons",
                    data: Array(12).fill(0),
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,.1)",
                    borderWidth: 2,
                    tension: .4,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: "#3b82f6"
                },
                {
                    label: "Vehicles",
                    data: Array(12).fill(0),
                    borderColor: "#22c55e",
                    backgroundColor: "rgba(34,197,94,.05)",
                    borderWidth: 2,
                    tension: .4,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: "#22c55e"
                },
                {
                    label: "Alerts",
                    data: Array(12).fill(0),
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239,68,68,.05)",
                    borderWidth: 2,
                    tension: .4,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: "#ef4444"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: t.tooltipBg,
                    borderColor: t.tooltipBorder,
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    titleColor: t.tooltipTitle,
                    bodyColor: t.tooltipBody,
                    bodyFont: {
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: t.gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        color: t.tickColor,
                        font: {
                            size: 11
                        },
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6
                    }
                },
                y: {
                    grid: {
                        color: t.gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        color: t.tickColor,
                        font: {
                            size: 11
                        },
                        stepSize: 1
                    },
                    beginAtZero: true
                }
            },
            animation: {
                duration: 750,
                easing: "easeInOutQuart"
            }
        }
    });

    // Expose globally for theme refresh
    window.detectionChart = detectionChart;

    // Hide detection spinner once chart is ready
    const detSpinner = document.getElementById('detectionSpinner');
    if (detSpinner) detSpinner.style.display = 'none';
    const detContainer = document.getElementById('detectionChartContainer');
    if (detContainer) detContainer.classList.remove('chart-loading');
}

function updateDetectionChart(){
    if(!detectionChart) return;

    const chart = detectionChart;
    const labels = chart.data.labels;
    const now = new Date();
    const newLabel = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

    labels.shift();
    labels.push(newLabel);

    // Fetch real event data and update chart
    fetch("/events")
        .then(r => r.json())
        .then(events => {
            const arr = Array.isArray(events) ? events : [];
            const oneMinAgo = now.getTime() - 60000;
            let personCount = 0, vehicleCount = 0, alertCount = 0;
            arr.forEach(e => {
                const ts = e.timestamp ? new Date(e.timestamp).getTime() : 0;
                if (ts >= oneMinAgo) {
                    const etype = (e.event_type || "").toUpperCase();
                    if (etype.includes("PERSON") || etype.includes("LOITERING")) personCount++;
                    if (etype.includes("VEHICLE")) vehicleCount++;
                    if (e.severity === "HIGH" || e.severity === "CRITICAL") alertCount++;
                }
            });
            chart.data.datasets[0].data.shift();
            chart.data.datasets[0].data.push(personCount);
            chart.data.datasets[1].data.shift();
            chart.data.datasets[1].data.push(vehicleCount);
            chart.data.datasets[2].data.shift();
            chart.data.datasets[2].data.push(alertCount);
            chart.update("none");
        })
        .catch(() => {
            // On error, just shift with previous values
            chart.data.datasets.forEach(dataset => {
                const prev = dataset.data[dataset.data.length - 1] || 0;
                dataset.data.shift();
                dataset.data.push(prev);
            });
            chart.update("none");
        });
}

window._dashboardIntervals.push(setInterval(updateDetectionChart, 10000));

/* ==========================================
   AI PERFORMANCE
========================================== */

let performanceChart = null;

const fpsHistory = [];
const MAX_FPS_HISTORY = 20;

async function updateAIPerformance() {

    const spinner = document.getElementById("perfSpinner");
    const chartContainer = document.getElementById("perfChartContainer");
    const metricsEl = document.getElementById("aiPerfMetrics");
    const errorEl = document.getElementById("perfError");

    if (!chartContainer) {
        return;
    }

    if (errorEl) {
        errorEl.style.display = "none";
    }

    if (!performanceChart && spinner) {
        spinner.style.display = "flex";
        chartContainer.classList.add("chart-loading");
    }

    try {

        const controller = new AbortController();

        const timeoutId = setTimeout(() => {
            controller.abort();
        }, 10000);

        const response = await fetch(
            "/api/v1/health",
            {
                signal: controller.signal,
                cache: "no-store"
            }
        );

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            throw new Error("Invalid API response");
        }

        const data = await response.json();

        const aiEngine = data.ai_engine || {};
        const metrics = aiEngine.metrics || {};

        /* -----------------------------------------
           READ EXISTING BACKEND VALUES
        ----------------------------------------- */

        const status =
            aiEngine.status || "--";

        const fps =
            Number(metrics.detection_fps) || 0;

        const inference =
            Number(metrics.avg_inference_ms) || 0;

        const queue =
            Number(metrics.queue_size) || 0;

        /* -----------------------------------------
           UPDATE METRICS
        ----------------------------------------- */

        const statusEl =
            document.getElementById("perf-status");

        const fpsEl =
            document.getElementById("perf-fps");

        const inferenceEl =
            document.getElementById("perf-inference");

        const queueEl =
            document.getElementById("perf-queue");

        if (statusEl) {

            statusEl.textContent = status;

            statusEl.classList.remove(
                "perf-status-degraded",
                "perf-status-unhealthy"
            );

            if (status === "Healthy") {

                statusEl.style.color = "#22c55e";

            } else if (status === "Degraded") {

                statusEl.style.color = "#facc15";
                statusEl.classList.add(
                    "perf-status-degraded"
                );

            } else if (
                status === "Unhealthy"
            ) {

                statusEl.style.color = "#ef4444";
                statusEl.classList.add(
                    "perf-status-unhealthy"
                );

            } else {

                statusEl.style.color = "#94a3b8";
            }
        }

        if (fpsEl) {
            fpsEl.textContent = fps.toFixed(1);
        }

        if (inferenceEl) {
            inferenceEl.textContent =
                `${inference.toFixed(1)} ms`;
        }

        if (queueEl) {
            queueEl.textContent =
                String(Math.round(queue));
        }

        if (metricsEl) {
            metricsEl.style.display = "grid";
        }

        /* -----------------------------------------
           FPS HISTORY
        ----------------------------------------- */

        fpsHistory.push(fps);

        if (fpsHistory.length > MAX_FPS_HISTORY) {
            fpsHistory.shift();
        }

        /* -----------------------------------------
           CHART
        ----------------------------------------- */

        const canvas =
            document.getElementById("performanceChart");

        if (canvas && typeof Chart !== "undefined") {

            const labels =
                fpsHistory.map(() => "");

            if (!performanceChart) {

                const pt = (typeof getChartTheme === 'function') ? getChartTheme() : {
                    tooltipBg:'rgba(15,23,42,0.96)', tooltipBorder:'rgba(59,130,246,0.25)',
                    tooltipTitle:'#e5e7eb', tooltipBody:'#94a3b8'
                };

                performanceChart = new Chart(
                    canvas,
                    {
                        type: "line",

                        data: {
                            labels: labels,

                            datasets: [
                                {
                                    label: "FPS",

                                    data: [...fpsHistory],

                                    borderColor: "#3b82f6",

                                    backgroundColor:
                                        "rgba(59,130,246,0.12)",

                                    borderWidth: 2,

                                    fill: true,

                                    tension: 0.4,

                                    pointRadius: 0,

                                    pointHoverRadius: 3,

                                    pointHoverBackgroundColor:
                                        "#3b82f6",

                                    pointHoverBorderWidth: 0
                                }
                            ]
                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio: false,

                            interaction: {
                                intersect: false,
                                mode: "index"
                            },

                            plugins: {

                                legend: {
                                    display: false
                                },

                                tooltip: {

                                    enabled: true,

                                    backgroundColor:
                                        pt.tooltipBg,

                                    borderColor:
                                        pt.tooltipBorder,

                                    borderWidth: 1,

                                    titleColor: pt.tooltipTitle,

                                    bodyColor: pt.tooltipBody,

                                    padding: 9,

                                    displayColors: false,

                                    callbacks: {

                                        title: () => "",

                                        label: context =>
                                            `${Number(
                                                context.raw || 0
                                            ).toFixed(1)} FPS`
                                    }
                                }
                            },

                            scales: {

                                x: {
                                    display: false,

                                    grid: {
                                        display: false
                                    }
                                },

                                y: {

                                    display: false,

                                    beginAtZero: true,

                                    grid: {
                                        display: false
                                    }
                                }
                            },

                            animation: {
                                duration: 300
                            }
                        }
                    }
                );

                // Expose globally for theme refresh
                window.performanceChart = performanceChart;

            } else {

                performanceChart.data.labels =
                    labels;

                performanceChart.data.datasets[0].data =
                    [...fpsHistory];

                performanceChart.update("none");
            }
        }

        /* -----------------------------------------
           FINISH LOADING
        ----------------------------------------- */

        if (spinner) {
            spinner.style.display = "none";
        }

        chartContainer.classList.remove(
            "chart-loading"
        );

    } catch (error) {

        console.warn(
            "AI Performance update failed:",
            error
        );

        if (spinner) {
            spinner.style.display = "none";
        }

        chartContainer.classList.remove(
            "chart-loading"
        );

        /*
         * Do NOT destroy existing metrics/chart.
         * The dashboard should remain usable if
         * one health request temporarily fails.
         */

        if (!performanceChart && errorEl) {
            errorEl.style.display = "block";
        }
    }
}

/* ==========================================
   INIT
========================================== */

if (typeof loadEvidence === 'function') loadEvidence();
initDetectionChart();
updateDetectionChart();
window._dashboardIntervals.push(setInterval(updateAIPerformance, 5000));
updateAIPerformance();

// Watch for theme changes and re-apply chart colors
if (typeof refreshChartsOnThemeChange === 'function') refreshChartsOnThemeChange();
/* ==========================================
   CLEANUP ON PAGE LEAVE
========================================== */

function cleanupDashboard() {
    if (window._dashboardIntervals) {
        window._dashboardIntervals.forEach(id => clearInterval(id));
        window._dashboardIntervals = [];
    }
    const overlay = document.getElementById("aiOverlay");
    if (overlay) overlay.style.display = "none";
    const video = document.getElementById("dashboardVideo");
    if (video) {
        video.pause();
        video.src = "";
    }
}

window.addEventListener("beforeunload", cleanupDashboard);
