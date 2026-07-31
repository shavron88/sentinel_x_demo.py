async function updateDashboard() {

    try {

        const response = await fetch("/stats");
        const stats = await response.json();

        document.getElementById("person-count").innerText = stats.persons;
        document.getElementById("vehicle-count").innerText = stats.vehicles;
        document.getElementById("alert-count").innerText = stats.alerts;
        const threat = document.getElementById("threat-level");
const fill = document.getElementById("threat-fill");

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
        document.getElementById("fps").innerText = stats.fps;
        document.getElementById("camera-fps").innerText = stats.fps;

document.getElementById("fps-overlay").innerText =
"FPS : " + stats.fps;

document.getElementById("health-threat").innerText =
stats.threat;

    } catch (err) {

        console.log("Dashboard Error:", err);

    }

}


async function loadTimeline() {

    try {

        const response = await fetch("/timeline");
        const data = await response.json();

        const timeline = document.getElementById("timeline");

        timeline.innerHTML = "";

        data.timeline.forEach(item => {

            let color = "#28a745";
            let icon = "🟢";

            if (item.severity === "MEDIUM") {
                color = "#ffc107";
                icon = "🟡";
            }

            if (item.severity === "HIGH") {
                color = "#dc3545";
                icon = "🔴";
            }

            const div = document.createElement("div");

            div.className = "timeline-item";

            div.innerHTML = `
                <div class="timeline-left">
                    <span class="timeline-icon">${icon}</span>
                </div>

                <div class="timeline-content">

                    <div class="timeline-header">

                        <span class="event-name">${item.event.replaceAll("_"," ")}</span>

                        <span class="severity-badge"
                              style="background:${color}">
                              ${item.severity}
                        </span>

                    </div>

                    <div class="timeline-info">

                        <span>📍 ${item.zone}</span>

                        <span>🕒 ${item.time}</span>

                    </div>

                </div>
            `;

            timeline.appendChild(div);

        });

    } catch(err){

        console.log(err);

    }

}


// Refresh every second
setInterval(updateDashboard, 1000);
setInterval(loadTimeline, 1000);

// Run immediately
updateDashboard();
loadTimeline();


async function loadGallery(){

    const response = await fetch("/gallery");

    const data = await response.json();

    let html="";

    data.images.forEach(img=>{

        html += `
        <img
            src="/evidence/screenshots/${img}"
            class="gallery-image"
        >
        `;

    });

    document.getElementById("gallery").innerHTML=html;

}

setInterval(loadGallery,1000);
loadGallery();