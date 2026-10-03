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

            // Every interpolated value is escaped: camera names, zones and
            // stream URLs are user supplied, and feeding them into an HTML
            // attribute (or into inline JS) was a stored-XSS hole. Actions are
            // carried in data-* attributes and dispatched by one delegated
            // listener instead of per-card inline handlers.
            const name = escapeHtml(camera.name);
            const liveHref = `/camera_view?camera=${encodeURIComponent(camera.name)}`;

            card.innerHTML = `

                <div class="camera-top">

                    <div>

                        <h3>${name}</h3>

                        <p>${escapeHtml(camera.location)}</p>

                    </div>

                    <span class="${isOnline ? "camera-online" : "camera-offline"}">

                        ● ${escapeHtml(camera.status)}

                    </span>

                </div>

                <div class="camera-feed-mount"></div>

                <div class="camera-info">

                    <div><span>Resolution</span><strong>${escapeHtml(camera.resolution)}</strong></div>

                    <div><span>FPS</span><strong>${escapeHtml(camera.fps)}</strong></div>

                    <div><span>Latency</span><strong>${escapeHtml(camera.latency)} ms</strong></div>

                    <div><span>Health</span><strong>${escapeHtml(camera.health)}</strong></div>

                    <div><span>Status</span><strong>${escapeHtml(camera.status)}</strong></div>

                    <div><span>Recording</span><strong>${camera.is_recording ? "ON" : "OFF"}</strong></div>

                </div>

                <div class="camera-buttons">

                    <a href="${liveHref}"><button class="live-btn" type="button">▶ Live</button></a>

                    <button class="snapshot-btn" type="button"
                            data-action="snapshot" data-camera="${name}">📷 Snapshot</button>

                    <button class="refresh-btn" type="button"
                            data-action="refresh" data-camera="${name}">⟳ Refresh</button>

                    <button class="settings-btn" type="button"
                            data-action="details" data-camera="${name}"
                            aria-label="Camera settings for ${name}">⚙</button>

                </div>

            `;

            // The live feed is built with DOM APIs: the src is assigned as a
            // property, so it can never be parsed as markup.
            const mount = card.querySelector(".camera-feed-mount");
            if (mount) {
                if (isOnline) {
                    const img = document.createElement("img");
                    img.src = String(camera.stream || "");
                    img.alt = `${camera.name} live stream`;
                    img.loading = "lazy";
                    img.decoding = "async";
                    img.addEventListener("error", () => {
                        const placeholder = document.createElement("div");
                        placeholder.className = "camera-placeholder";
                        placeholder.textContent = "LIVE FEED";
                        mount.replaceChildren(placeholder);
                    }, { once: true });
                    mount.appendChild(img);
                } else {
                    const placeholder = document.createElement("div");
                    placeholder.className = "camera-placeholder";
                    placeholder.textContent = "NO SIGNAL";
                    mount.appendChild(placeholder);
                }
            }

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

            <h3 style="color:#e2e8f0;margin:0 0 8px 0;">${escapeHtml(title)}</h3>

            <p style="color:#94a3b8;margin:0 0 20px 0;">${escapeHtml(message)}</p>

            <div style="display:flex;gap:10px;justify-content:center;">

                ${actionsHtml}

            </div>

        </div>

    `;

}

/* ==========================================
   CAMERA CLEANUP ON PAGE LEAVE
========================================== */

function cleanupCameras() {
    // The feed <img> is mounted inside .camera-feed-mount, so the old
    // '.camera-feed img' selector matched nothing and no stream was ever torn
    // down. Assigning src = "" also makes the browser re-request the current
    // page as an image, and .pause() throws on an <img> (HTMLImageElement has
    // no pause()), which aborted the loop.
    document.querySelectorAll('.camera-card img[src*="/video_feed"], .camera-feed-mount img')
        .forEach(img => img.removeAttribute("src"));

    document.querySelectorAll('video, audio').forEach(el => {
        try { el.pause(); } catch (e) { /* not a media element */ }
        el.removeAttribute("src");
        if (typeof el.load === "function") { try { el.load(); } catch (e) {} }
    });
}

/* ==========================================
   DELEGATED CARD ACTIONS
   Replaces inline onclick="fn('${camera.name}')" handlers, which put a
   user-controlled camera name inside a JavaScript string in an attribute.
========================================== */

document.addEventListener("click", function (event) {
    const btn = event.target.closest("[data-action]");
    if (!btn) return;
    const name = btn.getAttribute("data-camera") || "";
    switch (btn.getAttribute("data-action")) {
        case "snapshot": takeSnapshot(name); break;
        case "refresh":  refreshCamera(name); break;
        case "details":  viewCameraDetails(name); break;
    }
});

window.addEventListener("pagehide", cleanupCameras);
window.addEventListener("beforeunload", cleanupCameras);
