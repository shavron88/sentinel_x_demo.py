async function loadCameraWall() {
    const wall = document.getElementById("cameraWall");
    const empty = document.getElementById("emptyState");
    
    if (!wall) return;
    
    wall.innerHTML = "";
    if (empty) empty.style.display = "none";
    
    showSkeletonCards("cameraWall", 4);
    
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
                stream: `/video_feed?camera_name=${encodeURIComponent(cam.name || name)}`,
                fps: cam.fps || 0,
                health: cam.health || 'UNKNOWN'
            }));
        }
        
        hideSkeletons();
        
        if (cameras.length === 0) {
            showEmptyState("emptyState", "No Camera Feeds", "No active camera feeds available.", [{label:"Retry", onclick:"loadCameraWall()", class:"btn-primary"}]);
            updateWallStats(0, 0, 0);
            return;
        }
        
        let onlineCount = 0;
        let alertCount = 0;
        
        cameras.forEach((camera, index) => {
            const card = document.createElement("div");
            card.className = "camera-card";
            card.style.animationDelay = `${Math.min(index * 0.05, 0.4)}s`;
            
            const isOnline = camera.status === "ONLINE";
            const cameraAlert = alertsData[camera.name] || alertsData[camera.id] || {};
            const hasAlert = cameraAlert.has_alert || false;
            const alertCountCam = cameraAlert.alert_count || 0;
            
            if (isOnline) onlineCount++;
            if (hasAlert) alertCount++;
            
            const statusClass = isOnline ? "online" : "offline";
            const alertClass = hasAlert ? "alert" : "";
            
            card.className = "camera-card " + alertClass;
            card.dataset.cameraName = camera.name || camera.id;
            card.onclick = function() {
                window.location.href = `/camera_view?camera=${encodeURIComponent(camera.name || camera.id)}`;
            };
            
            const alertBadge = hasAlert ? `
                <span class="alert-badge" title="${alertCountCam} high alert(s)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    ${alertCountCam}
                </span>
            ` : '';
            
            card.innerHTML = `
                <div class="camera-header">
                    <span class="camera-name">📹 ${escapeHtml(camera.name)}</span>
                    <span class="camera-status ${statusClass}">
                        ${camera.status}
                    </span>
                    ${alertBadge}
                </div>
                ${isOnline ? `
                    <img src="${camera.stream}" 
                         alt="${escapeHtml(camera.name)} live stream" 
                         loading="lazy"
                         onerror="this.parentElement.innerHTML='<div class=\\'camera-placeholder\\'>NO SIGNAL</div>'">
                ` : `
                    <div class="camera-placeholder">
                        NO SIGNAL
                    </div>
                `}
                <div class="camera-footer">
                    <span>FPS : ${camera.fps}</span>
                    <span>AI : ${camera.health === 'EXCELLENT' || camera.health === 'GOOD' ? 'ACTIVE' : 'INACTIVE'}</span>
                </div>
            `;
            
            wall.appendChild(card);
        });
        
        updateWallStats(onlineCount, alertCount, cameras.length);
        
    } catch (err) {
        console.error("Failed to load camera wall:", err);
        hideSkeletons();
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

// Auto-refresh camera wall
setInterval(loadCameraWall, 3000);
loadCameraWall();

/* ==========================================
   LIVE WALL CLEANUP ON PAGE LEAVE
========================================= */
function cleanupLiveWall() {
    document.querySelectorAll('#cameraWall img').forEach(el => {
        el.src = "";
    });
}

window.addEventListener("beforeunload", cleanupLiveWall);