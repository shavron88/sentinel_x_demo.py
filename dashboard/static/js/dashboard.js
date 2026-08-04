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



async function updateDashboard() {

    try {

        const response = await fetch("/stats");
        const stats = await response.json();

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
    }

}



async function loadAIFeed() {

    try {

        const response = await fetch("/timeline");
        const data = await response.json();

        const feed = document.getElementById("timeline");

        if(!feed) return;

        feed.innerHTML = "";

        const sampleEvents = [
            "Person Entered Restricted Zone",
            "Fall Detected",
            "Crowd Density High",
            "Loitering Warning",
            "Vehicle Detected in No-Parking",
            "Perimeter Breach Alert",
            "Unattended Object Detected",
            "Crowd Density High",
            "Person Entered Restricted Zone",
            "Fall Detected"
        ];

        const severities = ["HIGH", "MEDIUM", "LOW"];
        const zones = ["Main Entrance", "Parking A", "Warehouse", "Lobby", "Restricted Zone", "Corridor B"];

        const now = new Date();

        sampleEvents.forEach((event, index) => {

            const severity = severities[index % 3];
            const time = new Date(now.getTime() - (sampleEvents.length - index) * 60000);
            const timeStr = time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

            const div = document.createElement("div");
            div.className = `ai-feed-item feed-${severity.toLowerCase()}`;

            div.innerHTML = `
                <span class="ai-feed-time">${timeStr}</span>
                <div class="ai-feed-content">
                    <div class="ai-feed-title">${event}</div>
                    <div class="ai-feed-meta">
                        <span>📍 ${zones[index % zones.length]}</span>
                    </div>
                </div>
                <span class="ai-feed-badge ${severity.toLowerCase()}">${severity}</span>
            `;

            feed.appendChild(div);

        });

        feed.scrollTop = feed.scrollHeight;

    } catch(err) {

        console.log(err);

    }

}


// Refresh every second
setInterval(updateDashboard, 1000);
setInterval(loadAIFeed, 3000);

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

    data.images.forEach(img=>{
        html += `
        <a href="/evidence" title="View all evidence">
            <img
                src="/evidence/screenshots/${img}"
                class="gallery-image"
                loading="lazy"
            >
        </a>
        `;
    });

    gallery.innerHTML=html;

}

setInterval(loadGallery,1000);
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
            const cameras = await res.json();
            const active = cameras.filter(c => c.status === "ONLINE").length;
            camerasEl.innerText = active;

        } catch(e) {

            camerasEl.innerText = "4";

        }
    }

    if(accuracyEl){
        const accuracy = (97 + Math.random() * 2.5).toFixed(1);
        accuracyEl.innerText = accuracy;
    }

}

/* ==========================================
   AI DETECTION OVERLAY
========================================== */

const aiDirections = ["→ North", "→ South", "→ East", "→ West", "↗ NE", "↘ SE", "↙ SW", "↖ NW"];
const aiZones = ["Main Entrance", "Parking A", "Warehouse", "Lobby", "Restricted Zone", "Corridor B"];
let aiPersonCounter = 1;
let currentTrackingId = 1001;

function updateAIOverlay(){

    const overlay = document.getElementById("aiOverlay");
    if(!overlay) return;

    const confidence = (95 + Math.random() * 4.9).toFixed(1);
    const velocity = (0.5 + Math.random() * 2.5).toFixed(1);
    const direction = aiDirections[Math.floor(Math.random() * aiDirections.length)];
    const zone = aiZones[Math.floor(Math.random() * aiZones.length)];

    const titleEl = document.getElementById("aiTitle");
    const confidenceEl = document.getElementById("aiConfidence");
    const zoneEl = document.getElementById("aiZone");
    const trackingEl = document.getElementById("aiTracking");
    const velocityEl = document.getElementById("aiVelocity");
    const directionEl = document.getElementById("aiDirection");

    if(titleEl) titleEl.innerText = `Person #${aiPersonCounter}`;
    if(confidenceEl) confidenceEl.innerText = `${confidence}%`;
    if(zoneEl) zoneEl.innerText = zone;
    if(trackingEl) trackingEl.innerText = `#TX-${currentTrackingId}`;
    if(velocityEl) velocityEl.innerText = `${velocity} m/s`;
    if(directionEl) directionEl.innerText = direction;

    aiPersonCounter++;
    if(aiPersonCounter > 20) aiPersonCounter = 1;
    currentTrackingId++;
    if(currentTrackingId > 1099) currentTrackingId = 1001;

    overlay.style.animation = "none";
    overlay.offsetHeight;
    overlay.style.animation = "aiFadeIn .5s ease";

}

setInterval(updateAIOverlay, 2000);
updateAIOverlay();

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

setInterval(loadAISummary,2000);

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
                    data: Array.from({length: 12}, () => Math.floor(Math.random() * 8) + 2),
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
                    data: Array.from({length: 12}, () => Math.floor(Math.random() * 5) + 1),
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
                    data: Array.from({length: 12}, () => Math.floor(Math.random() * 4)),
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
        const change = Math.floor(Math.random() * 5) - 2;
        let next = prev + change;
        if(next < 0) next = 0;
        if(next > 15) next = 15;
        dataset.data.shift();
        dataset.data.push(next);
    });

    chart.update("none");

}

setInterval(updateDetectionChart, 5000);

/* ==========================================
   INIT
========================================== */

loadEvidence();
initDetectionChart();
updateDetectionChart();