const _wallCards = new Map();

async function loadCameraWall() {
    const wall = document.getElementById("cameraWall");
    const empty = document.getElementById("emptyState");

    if (!wall) return;

    if (empty) empty.style.display = "none";

    const isFirstPaint = _wallCards.size === 0;
    if (isFirstPaint) {
        wall.innerHTML = "";
        showSkeletonCards("cameraWall", 4);
    }

    try {
        const [camerasResponse, alertsResponse] = await Promise.all([
            fetch("/api/cameras"),
            fetch("/api/camera/alerts")
        ]);

        if (!camerasResponse.ok) {
            throw new Error(`HTTP ${camerasResponse.status}`);
        }

        const data = await camerasResponse.json();
        const alertsData = alertsResponse.ok ? await alertsResponse.json() : {};

        let cameras = [];

        if (Array.isArray(data)) {
            cameras = data;
        } else if (data && typeof data === 'object') {
            cameras = Object.entries(data).map(([name, cam]) => ({
                id: name,
                name: cam.name || name,
                location: cam.zone || cam.location || 'Unknown',
                status: cam.status || 'OFFLINE',
                // Prefer the server-provided MJPEG url; fall back to the feed route.
                stream: cam.stream || `/video_feed?camera_name=${encodeURIComponent(cam.name || name)}`,
                fps: cam.fps || 0,
                health: cam.health || 'UNKNOWN'
            }));
        }

        if (isFirstPaint) hideSkeletons();

        if (cameras.length === 0) {
            _wallCards.forEach(card => card.remove());
            _wallCards.clear();
            showEmptyState("emptyState", "No Camera Feeds", "No active camera feeds available.", [{label:"Retry", onclick:"loadCameraWall()", class:"btn-primary"}]);
            updateWallStats(0, 0, 0);
            return;
        }

        let onlineCount = 0;
        let alertCount = 0;
        const seen = new Set();

        cameras.forEach((camera, index) => {
            const key = camera.name || camera.id;
            seen.add(key);

            const isOnline = camera.status === "ONLINE";
            const cameraAlert = alertsData[camera.name] || alertsData[camera.id] || {};
            const hasAlert = cameraAlert.has_alert || false;
            const alertCountCam = cameraAlert.alert_count || 0;

            if (isOnline) onlineCount++;
            if (hasAlert) alertCount++;

            const statusClass = isOnline ? "online" : "offline";
            const alertClass = hasAlert ? "alert" : "";

            let card = _wallCards.get(key);

            if (!card) {
                // Build the card once per camera and reuse it on every refresh.
                // Previously the whole wall was rebuilt every 3s, which tore down
                // and restarted every MJPEG connection (flicker + constant load).
                card = document.createElement("div");
                card.className = "camera-card";
                card.style.animationDelay = `${Math.min(index * 0.05, 0.4)}s`;
                card.dataset.cameraName = key;
                card.onclick = function() {
                    window.location.href = `/camera_view?camera=${encodeURIComponent(key)}`;
                };
                card.innerHTML = `
                    <div class="camera-header">
                        <span class="camera-name">📹 ${escapeHtml(key)}</span>
                        <span class="camera-status ${statusClass}">${camera.status}</span>
                        <span class="alert-slot"></span>
                    </div>
                    <div class="camera-feed">
                        <img alt="${escapeHtml(key)} live stream" loading="lazy">
                    </div>
                    <div class="camera-footer">
                        <span class="wall-fps">FPS : ${camera.fps}</span>
                        <span class="wall-ai">AI : INACTIVE</span>
                    </div>
                `;
                wall.appendChild(card);
                _wallCards.set(key, card);
            } else {
                // Keep DOM order in sync with the server ordering.
                if (wall.children[index] !== card) {
                    wall.insertBefore(card, wall.children[index] || null);
                }
            }

            card.className = "camera-card " + alertClass;

            const statusEl = card.querySelector(".camera-status");
            if (statusEl) {
                statusEl.textContent = camera.status;
                statusEl.className = "camera-status " + statusClass;
            }

            const alertSlot = card.querySelector(".alert-slot");
            if (alertSlot) {
                alertSlot.innerHTML = hasAlert ? `
                    <span class="alert-badge" title="${alertCountCam} high alert(s)">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        ${alertCountCam}
                    </span>
                ` : '';
            }

            const feedBox = card.querySelector(".camera-feed") || card;
            let img = card.querySelector("img");

            if (isOnline && !img) {
                // The card was showing a NO SIGNAL placeholder; bring the
                // stream back without rebuilding the whole card.
                img = document.createElement("img");
                img.alt = `${key} live stream`;
                img.loading = "lazy";
                feedBox.innerHTML = "";
                feedBox.appendChild(img);
            }

            if (img) {
                if (isOnline) {
                    const wantedSrc = camera.stream || `/video_feed?camera_name=${encodeURIComponent(key)}`;
                    // Assigning src restarts the MJPEG stream, so only on change.
                    if (img.getAttribute("src") !== wantedSrc) {
                        img.src = wantedSrc;
                    }
                } else if (img.getAttribute("src") !== null) {
                    // Stop the stream rather than leaving it pulling frames.
                    img.removeAttribute("src");
                    img.replaceWith(Object.assign(document.createElement("div"), {
                        className: "camera-placeholder",
                        textContent: "NO SIGNAL"
                    }));
                }
            }

            const fpsEl = card.querySelector(".wall-fps");
            if (fpsEl) fpsEl.textContent = `FPS : ${camera.fps}`;

            const aiEl = card.querySelector(".wall-ai");
            if (aiEl) {
                const active = camera.health === 'EXCELLENT' || camera.health === 'GOOD';
                aiEl.textContent = `AI : ${active ? 'ACTIVE' : 'INACTIVE'}`;
            }
        });

        // Drop cards for cameras that no longer exist.
        _wallCards.forEach((card, key) => {
            if (!seen.has(key)) {
                const img = card.querySelector("img");
                if (img) img.src = "";
                card.remove();
                _wallCards.delete(key);
            }
        });

        updateWallStats(onlineCount, alertCount, cameras.length);

    } catch (err) {
        console.error("Failed to load camera wall:", err);
        if (isFirstPaint) hideSkeletons();
        showEmptyState("emptyState", "Unable to Load Camera Feeds", "The camera service could not be reached.", [{label:"Retry", onclick:"loadCameraWall()", class:"btn-primary"}]);
        updateWallStats(0, 0, 0);
    }
}

function updateWallStats(online, alerts, total) {
    const onlineEl = document.getElementById("wall-online-count");
    const alertEl = document.getElementById("wall-alert-count");
    const totalEl = document.getElementById("wall-total-count");
    
    if (onlineEl) onlineEl.textContent = online;
    if (alertEl) alertEl.textContent = alerts;
    if (totalEl) totalEl.textContent = total;
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Layout switching
function changeLayout(number){
    const wall=document.getElementById("cameraWall");
    if (wall) {
        wall.className="camera-wall layout-"+number;
    }
    document.querySelectorAll('.layout-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.layout === String(number)) {
            btn.classList.add('active');
        }
    });
}

// Bind layout buttons
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.layout-btn');
    if (btn) {
        const layout = btn.dataset.layout;
        changeLayout(layout);
    }
});

// Auto-refresh camera wall. Only the status chrome is re-rendered; the MJPEG
// connections stay up between refreshes.
if (document.getElementById("cameraWall")) {
    window._wallInterval = setInterval(loadCameraWall, 3000);
    loadCameraWall();
}

/* ==========================================
   LIVE WALL CLEANUP ON PAGE LEAVE
========================================== */
function cleanupLiveWall() {
    if (window._wallInterval) {
        clearInterval(window._wallInterval);
        window._wallInterval = null;
    }
    _wallCards.forEach(card => {
        const img = card.querySelector("img");
        if (img) img.src = "";
    });
    _wallCards.clear();
}

window.addEventListener("beforeunload", cleanupLiveWall);