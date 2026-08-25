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



function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function updateDashboard() {

    showSkeletonCards("stats-grid", 4);

    try {

        const response = await fetch("/stats");
        const stats = await response.json();

        hideSkeletons();

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
        updateKPIBar(stats);

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

            const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }) : "--:--";

            const div = document.createElement("div");

            div.className = `ai-feed-item feed-${severity.toLowerCase()}`;

            div.innerHTML = `

                <span class="ai-feed-time">${timeStr}</span>

                <div class="ai-feed-content">

                    <div class="ai-feed-title">${event}</div>

                    <div class="ai-feed-meta">

                        <span>📍 ${zone}</span>

                    </div>

                </div>

                <span class="ai-feed-badge ${severity.toLowerCase()}">${severity}</span>

            `;

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


// Refresh every second
window._dashboardIntervals = window._dashboardIntervals || [];
window._dashboardIntervals.push(setInterval(updateDashboard, 1000));
window._dashboardIntervals.push(setInterval(loadAIFeed, 3000));

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

window._dashboardIntervals.push(setInterval(updateAlerts, 3000));
updateAlerts();

// Run immediately
updateDashboard();
loadAIFeed();
// ==========================
// Evidence Gallery
// ==========================

async function loadGallery(){

    const response = await fetch("/gallery");

    const data = await response.json();

    const gallery = document.getElementById("gallery");

    if(!gallery) return;

    let html="";

    const items = Array.isArray(data) ? data : [];

    items.forEach(item => {

        const raw = item.image_path || "";

        const filename = raw.split("/").pop();

        if(!filename) return;

        html += `
        <a href="/evidence" title="View all evidence">
            <img
                src="/evidence/screenshots/${filename}"
                class="gallery-image"
                loading="lazy"
            >
        </a>
        `;

    });

    gallery.innerHTML=html;

}

window._dashboardIntervals.push(setInterval(loadGallery, 1000));
loadGallery();

/* ==========================================
   DETECTION HISTORY CHART
========================================== */

async function updateKPIBar(stats){

    const threatEl = document.getElementById("kpi-threat");
    const camerasEl = document.getElementById("kpi-cameras");
    const accuracyEl = document.getElementById("kpi-accuracy");
    const alertsEl = document.getElementById("kpi-alerts");

    if(threatEl){
        threatEl.innerText = stats.threat || "LOW";
    }

    if(alertsEl){
        alertsEl.innerText = String(stats.alerts || 0).padStart(2, "0");
    }
    if(camerasEl){
        try {
            const res = await fetch("/api/cameras");
            const data = await res.json();
            const cameras = (data && data.cameras) ? data.cameras : (Array.isArray(data) ? data : []);
            const active = cameras.filter(c => c.status === "ONLINE").length;
            camerasEl.innerText = active;
        } catch(e) {
            camerasEl.innerText = "4";
        }
    }

    if(accuracyEl){
        accuracyEl.innerText = "--";
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
        if(detectionsEl) detectionsEl.innerText = data.detections || "3 Persons";
        if(confidenceEl) confidenceEl.innerText = data.confidence || "98.4%";
        if(recommendationEl) recommendationEl.innerText = data.recommendation || "Continue Monitoring";

    }

    catch(e){

        console.log(e);

    }

}

window._dashboardIntervals.push(setInterval(loadAISummary, 2000));

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
                    backgroundColor: "rgba(15,23,42,.9)",
                    borderColor: "rgba(255,255,255,.1)",
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    titleColor: "#e2e8f0",
                    bodyColor: "#94a3b8",
                    bodyFont: {
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: "rgba(255,255,255,.05)",
                        drawBorder: false
                    },
                    ticks: {
                        color: "#64748b",
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
                        color: "rgba(255,255,255,.05)",
                        drawBorder: false
                    },
                    ticks: {
                        color: "#64748b",
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

}

function updateDetectionChart(){

    if(!detectionChart) return;

    const chart = detectionChart;
    const labels = chart.data.labels;
    const now = new Date();
    const newLabel = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

    labels.shift();
    labels.push(newLabel);

    chart.data.datasets.forEach(dataset => {
        const prev = dataset.data[dataset.data.length - 1] || 0;
        dataset.data.shift();
        dataset.data.push(prev);
    });

    chart.update("none");

}

window._dashboardIntervals.push(setInterval(updateDetectionChart, 5000));

/* ==========================================
   AI PERFORMANCE CHART
========================================== */

let performanceChart;
const fpsHistory = [];
const MAX_FPS_HISTORY = 20;

async function updateAIPerformance() {

    const spinner = document.getElementById('perfSpinner');
    const chartContainer = document.getElementById('perfChartContainer');
    const metricsEl = document.getElementById('aiPerfMetrics');
    const errorEl = document.getElementById('perfError');

    if (!chartContainer) return;

    if (spinner) spinner.style.display = 'flex';
    if (chartContainer) chartContainer.classList.add('chart-loading');
    if (metricsEl) metricsEl.style.display = 'none';
    if (errorEl) errorEl.style.display = 'none';

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
        const response = await fetch('/api/v1/health', { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            throw new Error('Invalid API response');
        }

        const data = await response.json();
        const aiEngine = data.ai_engine;

        if (!aiEngine) {
            throw new Error('No AI engine data');
        }

        const metrics = aiEngine.metrics || {};
        const fps = metrics.detection_fps || 0;

        if (metricsEl) {
            const statusEl = document.getElementById('perf-status');
            const fpsEl = document.getElementById('perf-fps');
            const inferenceEl = document.getElementById('perf-inference');
            const queueEl = document.getElementById('perf-queue');

            if (statusEl) {
                statusEl.innerText = aiEngine.status || '--';
                statusEl.style.color = aiEngine.status === 'Healthy' ? 'var(--ev-success)' :
                                       aiEngine.status === 'Degraded' ? '#facc15' : 'var(--ev-text-muted)';
            }
            if (fpsEl) fpsEl.innerText = fps.toFixed(1);
            if (inferenceEl) inferenceEl.innerText = (metrics.avg_inference_ms || 0).toFixed(1) + ' ms';
            if (queueEl) queueEl.innerText = metrics.queue_size || 0;

            metricsEl.style.display = 'grid';
        }

        fpsHistory.push(fps);
        if (fpsHistory.length > MAX_FPS_HISTORY) fpsHistory.shift();

        const ctx = document.getElementById('performanceChart');
        if (ctx) {
            const labels = fpsHistory.map((_, i) => '');

            if (!performanceChart) {
                performanceChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Detection FPS',
                            data: [...fpsHistory],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59,130,246,.1)',
                            borderWidth: 2,
                            tension: .4,
                            fill: true,
                            pointRadius: 2,
                            pointBackgroundColor: '#3b82f6'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: 'rgba(15,23,42,.9)',
                                borderColor: 'rgba(255,255,255,.1)',
                                borderWidth: 1,
                                padding: 10,
                                cornerRadius: 6,
                                titleColor: '#e2e8f0',
                                bodyColor: '#94a3b8',
                                bodyFont: { size: 11 }
                            }
                        },
                        scales: {
                            x: {
                                display: false,
                                grid: { display: false }
                            },
                            y: {
                                grid: { color: 'rgba(255,255,255,.05)', drawBorder: false },
                                ticks: { color: '#64748b', font: { size: 10 }, stepSize: 5 },
                                beginAtZero: true
                            }
                        },
                        animation: { duration: 300 }
                    }
                });
            } else {
                performanceChart.data.labels = labels;
                performanceChart.data.datasets[0].data = [...fpsHistory];
                performanceChart.update('none');
            }
        }

        if (spinner) spinner.style.display = 'none';
        if (chartContainer) chartContainer.classList.remove('chart-loading');

    } catch (err) {
        clearTimeout(timeoutId);
        console.log('AI Performance Error:', err);

        if (spinner) spinner.style.display = 'none';
        if (chartContainer) chartContainer.classList.remove('chart-loading');

        if (errorEl) {
            errorEl.innerHTML = '<div style="color:#ef4444;font-size:12px;padding:10px;text-align:center;">Unable to load AI performance data. <button onclick="updateAIPerformance()" style="background:none;border:none;color:#3b82f6;cursor:pointer;text-decoration:underline;">Retry</button></div>';
            errorEl.style.display = 'block';
        }
    }
}

/* ==========================================
   INIT
========================================== */

loadEvidence();
initDetectionChart();
updateDetectionChart();
window._dashboardIntervals.push(setInterval(updateAIPerformance, 2000));
updateAIPerformance();
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
