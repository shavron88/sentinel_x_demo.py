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


    const cameraFPS = document.getElementById("camera-fps");

if(cameraFPS){

    cameraFPS.innerText = stats.fps;

}

 try {

        const response = await fetch("/stats");
        const stats = await response.json();

        const personElement = document.getElementById("person-count");
const vehicleElement = document.getElementById("vehicle-count");
const alertElement = document.getElementById("alert-count");
const fpsElement = document.getElementById("fps");
updateSystemStatus(stats);

document.getElementById("person-count-footer").innerText = stats.persons;

document.getElementById("vehicle-count-footer").innerText = stats.vehicles;

document.getElementById("fps-footer").innerText = stats.fps;

animateValue(
    "person-count",
    Number(personElement.innerText) || 0,
    stats.persons
);

animateValue(
    "vehicle-count",
    Number(vehicleElement.innerText) || 0,
    stats.vehicles
);

animateValue(
    "alert-count",
    Number(alertElement.innerText) || 0,
    stats.alerts
);

animateValue(
    "fps",
    Number(fpsElement.innerText) || 0,
    stats.fps
);
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


setTimeout(()=>{

    showToast(

        "Camera",

        "Camera Connected",

        "success"

    );

},1000);

setTimeout(()=>{

    showToast(

        "AI Engine",

        "YOLOv8 Model Loaded",

        "info"

    );

},3000);

setTimeout(()=>{

    showToast(

        "Security",

        "Restricted Zone Monitoring Enabled",

        "warning"

    );

},5000);


// ======================
// LIVE CLOCK
// ======================

function updateClock(){

    const now = new Date();

    const date = now.toLocaleDateString(

        "en-US",

        {

            weekday:"long",

            day:"numeric",

            month:"long",

            year:"numeric"

        }

    );

    const time = now.toLocaleTimeString();

    document.getElementById("current-date").innerHTML = date;

    document.getElementById("current-time").innerHTML = time;

}

updateClock();

setInterval(updateClock,1000);

// ==========================
// Evidence Gallery
// ==========================

async function loadGallery(){

    try{

        const response=await fetch("/gallery");

        const data=await response.json();

        const gallery=document.getElementById("gallery");

        gallery.innerHTML="";

        data.images.forEach(img=>{

            gallery.innerHTML+=`

            <img

                src="/evidence/${img}"

                onclick="openImage('/evidence/${img}')"

            >

            `;

        });

    }

    catch(e){

        console.log(e);

    }

}

setInterval(loadGallery,2000);

loadGallery();

function openImage(src){

    document.getElementById("image-modal").style.display="flex";

    document.getElementById("modal-image").src=src;

}

document.getElementById("close-modal").onclick=()=>{

    document.getElementById("image-modal").style.display="none";

}

function updateSystemStatus(stats){

    const camera=document.getElementById("camera-status");

    if(!camera) return;

    if(stats.fps>0){

        camera.innerText="CONNECTED";

        camera.className="health-online";

    }

    else{

        camera.innerText="OFFLINE";

        camera.className="health-offline";

    }

}

async function loadAISummary(){

    try{

        const response=await fetch("/ai_summary");

        const data=await response.json();

        document.getElementById("ai-summary").innerHTML=`

            <h4>${data.event}</h4>

            <p>${data.summary}</p>

            <br>

            <strong>

                Recommendation

            </strong>

            <p>${data.recommendation}</p>

        `;

    }

    catch(e){

        console.log(e);

    }

}

setInterval(loadAISummary,2000);

loadAISummary();