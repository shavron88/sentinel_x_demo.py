function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadReport() {
    showSkeletonCards("stats-grid", 4);
    showSkeletonTable("event-summary", 4);
    showSkeletonTable("camera-summary", 3);
    showSkeletonRows("incident-report-list", 3);
    try {
        const response = await fetch("/reports_data");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        if (data.total_events === 0) {
            showEmptyState("reportsEmpty", "No Reports Available", "There are no events recorded for the selected period.", [{label:"Refresh", onclick:"loadReport()", class:"btn-primary"}]);
            return;
        }

        document.getElementById("camera-online").innerText = data.camera_online;
        document.getElementById("total-events").innerText = data.total_events;
        document.getElementById("total-evidence").innerText = data.total_evidence;
        document.getElementById("report-threat").innerText = data.threat_level;

        let events = "";
        data.event_summary.forEach(event => {
            events += `
            <tr>
                <td>${event.name}</td>
                <td>${event.count}</td>
            </tr>
            `;
        });
        document.getElementById("event-summary").innerHTML = events;

        let cameras = "";
        data.camera_summary.forEach(camera => {
            cameras += `
            <tr>
                <td>${camera.name}</td>
                <td>${camera.status}</td>
                <td>${camera.events}</td>
            </tr>
            `;
        });
        document.getElementById("camera-summary").innerHTML = cameras;

        document.getElementById("images-total").innerText = data.evidence.images;
        document.getElementById("images-today").innerText = data.evidence.today;
        document.getElementById("storage-used").innerText = data.evidence.storage;

        let incidents = "";
        data.high_priority.forEach(item => {
            incidents += `
            <div class="incident-item">
                <h4>${item.event}</h4>
                <p><strong>Camera:</strong> ${item.camera}</p>
                <p><strong>Location:</strong> ${item.location}</p>
                <p><strong>Time:</strong> ${item.time}</p>
            </div>
            `;
        });
        document.getElementById("incident-report-list").innerHTML = incidents;

    } catch (err) {
        console.error("Reports load error:", err);
        showEmptyState("reportsEmpty", "Unable to Load Reports", "The report service could not be reached.", [{label:"Retry", onclick:"loadReport()", class:"btn-primary"}]);
    }
}

function downloadPDF() {

    window.location.href = "/download_pdf";

}

function downloadCSV() {

    window.location.href = "/download_csv";

}

loadReport();

window._reportInterval = setInterval(loadReport,5000);
/* ==========================================
   REPORTS CLEANUP
========================================== */

function cleanupReports() {
    if (window._reportInterval) {
        clearInterval(window._reportInterval);
        window._reportInterval = null;
    }
}

window.addEventListener("beforeunload", cleanupReports);
