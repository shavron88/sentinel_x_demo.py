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
    fetch("/reports_data")
        .then(function(res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .then(function(data) {
            var html = buildPrintableReport(data);
            var win = window.open("", "_blank", "width=900,height=700");
            if (!win) {
                showToast("Reports", "Pop-up blocked. Please allow pop-ups for PDF export.", "danger");
                return;
            }
            win.document.open();
            win.document.write(html);
            win.document.close();
            win.onload = function() {
                setTimeout(function() { win.print(); }, 400);
            };
        })
        .catch(function(err) {
            console.error("PDF export error:", err);
            showToast("Reports", "Failed to generate report. Please try again.", "danger");
        });
}

function buildPrintableReport(data) {
    var esc = function(v) {
        if (v == null) return "";
        return String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    };
    var now = new Date().toLocaleString();
    var period = document.getElementById("report-period");
    var periodText = period ? period.options[period.selectedIndex].text : "Current";

    var eventRows = "";
    (data.event_summary || []).forEach(function(e) {
        eventRows += "<tr><td>" + esc(e.name) + "</td><td>" + esc(e.count) + "</td></tr>";
    });

    var cameraRows = "";
    (data.camera_summary || []).forEach(function(c) {
        cameraRows += "<tr><td>" + esc(c.name) + "</td><td>" + esc(c.status) + "</td><td>" + esc(c.events) + "</td></tr>";
    });

    var incidentHtml = "";
    (data.high_priority || []).forEach(function(item) {
        incidentHtml += "<div class='incident'><h4>" + esc(item.event) + "</h4>" +
            "<p><strong>Camera:</strong> " + esc(item.camera) + "</p>" +
            "<p><strong>Location:</strong> " + esc(item.location) + "</p>" +
            "<p><strong>Time:</strong> " + esc(item.time) + "</p></div>";
    });

    return "<!DOCTYPE html><html><head><title>SentinelX Report - " + esc(periodText) + "</title>" +
        "<style>" +
        "*{margin:0;padding:0;box-sizing:border-box}" +
        "body{font-family:'Segoe UI',Arial,sans-serif;padding:40px;color:#111;line-height:1.6}" +
        ".header{text-align:center;margin-bottom:30px;padding-bottom:20px;border-bottom:2px solid #1e40af}" +
        ".header h1{font-size:24px;color:#1e40af;margin-bottom:4px}" +
        ".header p{color:#666;font-size:13px}" +
        ".stats{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}" +
        ".stat{flex:1;min-width:120px;text-align:center;padding:16px;border:1px solid #ddd;border-radius:8px;background:#f8fafc}" +
        ".stat h3{font-size:28px;color:#1e40af;margin-bottom:4px}" +
        ".stat span{font-size:12px;color:#666;text-transform:uppercase;letter-spacing:.5px}" +
        "section{margin-bottom:24px}" +
        "h2{font-size:16px;color:#1e40af;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #ddd}" +
        "table{width:100%;border-collapse:collapse;margin-bottom:10px}" +
        "th{background:#1e40af;color:white;padding:10px 14px;text-align:left;font-size:13px}" +
        "td{padding:10px 14px;border-bottom:1px solid #eee;font-size:13px;line-height:1.6}" +
        "tr:hover{background:#f1f5f9}" +
        ".incident{background:#f9fafb;border-left:4px solid #ef4444;padding:12px 16px;border-radius:6px;margin-bottom:10px}" +
        ".incident h4{margin-bottom:4px;font-size:14px}" +
        ".incident p{margin:2px 0;font-size:13px;color:#444}" +
        ".footer{text-align:center;margin-top:30px;padding-top:16px;border-top:1px solid #ddd;color:#999;font-size:11px}" +
        "@media print{body{padding:20px}.stat{break-inside:avoid}section{break-inside:avoid}}" +
        "</style></head><body>" +
        "<div class='header'><h1>SentinelX Security Report</h1>" +
        "<p>Period: " + esc(periodText) + " &bull; Generated: " + esc(now) + "</p></div>" +
        "<div class='stats'>" +
        "<div class='stat'><h3>" + esc(data.camera_online) + "</h3><span>Cameras Online</span></div>" +
        "<div class='stat'><h3>" + esc(data.total_events) + "</h3><span>Total Events</span></div>" +
        "<div class='stat'><h3>" + esc(data.total_evidence) + "</h3><span>Evidence</span></div>" +
        "<div class='stat'><h3>" + esc(data.threat_level) + "</h3><span>Threat Level</span></div>" +
        "</div>" +
        "<section><h2>Event Summary</h2><table><thead><tr><th>Event</th><th>Total</th></tr></thead><tbody>" + eventRows + "</tbody></table></section>" +
        "<section><h2>Camera Activity</h2><table><thead><tr><th>Camera</th><th>Status</th><th>Events</th></tr></thead><tbody>" + cameraRows + "</tbody></table></section>" +
        "<section><h2>Evidence Summary</h2><table><tbody>" +
        "<tr><td><strong>Total Images</strong></td><td>" + esc(data.evidence ? data.evidence.images : 0) + "</td></tr>" +
        "<tr><td><strong>Today's Images</strong></td><td>" + esc(data.evidence ? data.evidence.today : 0) + "</td></tr>" +
        "<tr><td><strong>Storage Used</strong></td><td>" + esc(data.evidence ? data.evidence.storage : "0 MB") + "</td></tr>" +
        "</tbody></table></section>" +
        "<section><h2>High Priority Incidents</h2>" + (incidentHtml || "<p>No high priority incidents.</p>") + "</section>" +
        "<div class='footer'>SentinelX AI Surveillance &bull; Confidential Report &bull; Page 1</div>" +
        "</body></html>";
}

function downloadCSV() {
    showToast("Reports", "Generating CSV report...", "info");
    fetch("/download_csv")
        .then(function(res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.blob();
        })
        .then(function(blob) {
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = "sentinelx_report.csv";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast("Reports", "CSV report downloaded successfully", "success");
        })
        .catch(function(err) {
            console.error("CSV download error:", err);
            showToast("Reports", "Failed to download CSV. Please try again.", "danger");
        });
}

function printReport() {
    window.print();
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
