function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadCameras(){

    const grid = document.getElementById("camera-grid");

    if(!grid) return;

    grid.innerHTML = "";

    showSkeletonCards("camera-grid", 4);

    try {

        const response = await fetch("/api/cameras");

        if (!response.ok) {

            throw new Error(`HTTP ${response.status}`);

        }

        const data = await response.json();

        let cameras = [];

        if (Array.isArray(data)) {

            cameras = data;

        } else if (data && typeof data === 'object') {

            cameras = Object.entries(data).map(([name, cam]) => ({

                id: name,

                name: cam.name || name,

                location: cam.zone || cam.location || 'Unknown',

                status: cam.status || 'OFFLINE',

                stream: `/video_feed?camera_name=${encodeURIComponent(cam.name || name)}`,

                resolution: cam.resolution || '640x480',

                fps: cam.fps || 0,

                latency: cam.latency || 0,

                health: cam.health || 'UNKNOWN',

                is_recording: cam.is_recording || false

            }));

        }

        hideSkeletons();

        if (cameras.length === 0) {

            showEmptyState("emptyState", "No Cameras Found", "There are no cameras configured.", [{label:"Refresh", onclick:"loadCameras()", class:"btn-primary"}]);

            return;

        }

        cameras.forEach((camera, index) => {

            const card = document.createElement("div");

            card.className = "camera-card";

            card.style.animationDelay = `${Math.min(index * 0.05, 0.4)}s`;

            const isOnline = camera.status === "ONLINE";

            card.innerHTML = `

                <div class="camera-top">

                    <div>

                        <h3>${escapeHtml(camera.name)}</h3>

                        <p>${escapeHtml(camera.location)}</p>

                    </div>

                    <span class="${

                        isOnline

                        ? "camera-online"

                        : "camera-offline"

                    }">

                        ● ${camera.status}

                    </span>

                </div>

                ${

                    isOnline

                    ?

                    `<img src="${camera.stream}" alt="${camera.name} live stream" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'camera-placeholder\\'>LIVE FEED</div>'">`

                    :

                    `<div class="camera-placeholder">

                        NO SIGNAL

                    </div>`

                }

                <div class="camera-info">

                    <div>

                        <span>Resolution</span>

                        <strong>${camera.resolution}</strong>

                    </div>

                    <div>

                        <span>FPS</span>

                        <strong>${camera.fps}</strong>

                    </div>

                    <div>

                        <span>Latency</span>

                        <strong>${camera.latency} ms</strong>

                    </div>

                    <div>

                        <span>Health</span>

                        <strong>${camera.health}</strong>

                    </div>

                    <div>

                        <span>Status</span>

                        <strong>

                            ${camera.status}

                        </strong>

                    </div>

                    <div>

                        <span>Recording</span>

                        <strong>

                            ${camera.is_recording ? 'ON' : 'OFF'}

                        </strong>

                    </div>

                </div>

                <div class="camera-buttons">

                    <a href="/camera_view?camera=${encodeURIComponent(camera.name)}">

                        <button class="live-btn">

                            ▶ Live

                        </button>

                    </a>

                    <button class="snapshot-btn" onclick="takeSnapshot('${camera.name}')">

                        📷 Snapshot

                    </button>

                    <button class="refresh-btn" onclick="refreshCamera('${camera.name}')">

                        ⟳ Refresh

                    </button>

                    <button class="settings-btn" onclick="viewCameraDetails('${camera.name}')">

                        ⚙

                    </button>

                </div>

            `;

            grid.appendChild(card);

        });

    }

    catch (err) {

        console.error("Failed to load cameras:", err);

        hideSkeletons();

        showEmptyState("emptyState", "Unable to Load Cameras", "The camera service could not be reached.", [{label:"Retry", onclick:"loadCameras()", class:"btn-primary"}]);

    }

}

loadCameras();

async function takeSnapshot(cameraName){

    try {

        const response = await fetch("/api/camera/snapshot", {

            method: "POST",

            headers: { "Content-Type": "application/json" },

            body: JSON.stringify({ camera_name: cameraName })

        });

        const data = await response.json();

        if (data.success) {

            showToast("Snapshot", "Snapshot captured successfully", "success");

        } else {

            showToast("Snapshot", data.error || "Failed to capture snapshot", "error");

        }

    } catch (err) {

        showToast("Snapshot", "Failed to capture snapshot", "error");

    }

}

async function refreshCamera(cameraName){

    showToast("Refresh", `Refreshing ${cameraName}...`, "info");

    await loadCameras();

}

function viewCameraDetails(cameraName){

    showToast("Camera", `Opening details for ${cameraName}`, "info");

}

function showSkeletonCards(containerId, count){

    const container = document.getElementById(containerId);

    if (!container) return;

    for (let i = 0; i < count; i++) {

        const skeleton = document.createElement("div");

        skeleton.className = "camera-card skeleton-card";

        skeleton.innerHTML = `

            <div class="skeleton-line" style="width:60%;height:16px;margin-bottom:12px;"></div>

            <div class="skeleton-line" style="width:100%;height:180px;margin-bottom:12px;"></div>

            <div class="skeleton-line" style="width:100%;height:10px;margin-bottom:6px;"></div>

            <div class="skeleton-line" style="width:80%;height:10px;"></div>

        `;

        container.appendChild(skeleton);

    }

}

function hideSkeletons(){

    document.querySelectorAll(".skeleton-card").forEach(c => c.remove());

}

function showEmptyState(containerId, title, message, actions){

    const container = document.getElementById(containerId);

    if (!container) return;

    const actionsHtml = actions.map(a =>

        `<button class="${a.class || 'btn-secondary'}" onclick="${a.onclick}">${a.label}</button>`

    ).join("");

    container.style.display = "flex";

    container.innerHTML = `

        <div style="grid-column:1/-1;text-align:center;padding:60px 20px;">

            <div style="font-size:48px;margin-bottom:16px;opacity:0.6;">📹</div>

            <h3 style="color:#e2e8f0;margin:0 0 8px 0;">${title}</h3>

            <p style="color:#94a3b8;margin:0 0 20px 0;">${message}</p>

            <div style="display:flex;gap:10px;justify-content:center;">

                ${actionsHtml}

            </div>

        </div>

    `;

}

function showToast(title, message, type){

    const toast = document.createElement("div");

    toast.className = `toast toast-${type}`;

    toast.innerHTML = `

        <div class="toast-title">${title}</div>

        <div class="toast-message">${message}</div>

    `;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.classList.add("show");

    }, 10);

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => toast.remove(), 300);

    }, 3000);

}

/* ==========================================
   CAMERA CLEANUP ON PAGE LEAVE
========================================== */

function cleanupCameras() {
    document.querySelectorAll('.camera-feed img, .camera-feed video').forEach(el => {
        el.pause();
        el.src = "";
        el.load();
    });
}

window.addEventListener("beforeunload", cleanupCameras);
