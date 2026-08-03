async function loadReport() {

    try {

        const response = await fetch("/reports_data");

        const data = await response.json();

        // ================= SUMMARY =================

        document.getElementById("camera-online").innerText =
            data.camera_online;

        document.getElementById("total-events").innerText =
            data.total_events;

        document.getElementById("total-evidence").innerText =
            data.total_evidence;

        document.getElementById("report-threat").innerText =
            data.threat_level;

        // ================= EVENT TABLE =================

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

        // ================= CAMERA TABLE =================

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

        // ================= EVIDENCE =================

        document.getElementById("images-total").innerText =
            data.evidence.images;

        document.getElementById("images-today").innerText =
            data.evidence.today;

        document.getElementById("storage-used").innerText =
            data.evidence.storage;

        // ================= INCIDENTS =================

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

        document.getElementById("incident-report-list").innerHTML =
            incidents;

    }

    catch (err) {

        console.log(err);

    }

}

function downloadPDF() {

    window.location.href = "/download_pdf";

}

function downloadCSV() {

    window.location.href = "/download_csv";

}

loadReport();

setInterval(loadReport,5000);