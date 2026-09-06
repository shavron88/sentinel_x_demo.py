async function loadCameraWall() {
    const wall = document.getElementById("cameraWall");
    const empty = document.getElementById("emptyState");
    
    if (!wall) return;
    
    wall.innerHTML = "";
    if (empty) empty.style.display = "none";
    
    showSkeletonCards("cameraWall", 4);
    
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
                fps: cam.fps || 0,
                health: cam.health || 'UNKNOWN'
            }));
        }
        
        hideSkeletons();
        
        if (cameras.length === 0) {
            showEmptyState("emptyState", "No Camera Feeds", "No active camera feeds available.", [{label:"Retry", onclick:"loadCameraWall()", class:"btn-primary"}]);
            return;
        }
        
        cameras.forEach((camera, index) => {
            const card = document.createElement("div");
            card.className = "camera-card";
            card.style.animationDelay = `${Math.min(index * 0.05, 0.4)}s`;
            
            const isOnline = camera.status === "ONLINE";
            const statusClass = isOnline ? "online" : "offline";
            
            card.innerHTML = `
                <div class="camera-header">
                    <span>📹 ${escapeHtml(camera.name)}</span>
                    <span class="camera-status ${statusClass}">
                        ${camera.status}
                    </span>
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
        
    } catch (err) {
        console.error("Failed to load camera wall:", err);
        hideSkeletons();
        showEmptyState("emptyState", "Unable to Load Camera Feeds", "The camera service could not be reached.", [{label:"Retry", onclick:"loadCameraWall()", class:"btn-primary"}]);
    }
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadCameraWall();
/* ==========================================
   LIVE WALL CLEANUP ON PAGE LEAVE
========================================== */

function cleanupLiveWall() {
    document.querySelectorAll('#cameraWall img').forEach(el => {
        el.src = "";
    });
}

window.addEventListener("beforeunload", cleanupLiveWall);
