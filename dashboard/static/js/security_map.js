async function loadSecurityMap() {
    const container = document.querySelector(".map-container");
    const tooltip = document.getElementById("mapTooltip");
    
    if (!container) return;
    
    showSkeletonCards("map-container", 1);
    
    try {
        const [camerasRes, eventsRes] = await Promise.all([
            fetch("/api/cameras"),
            fetch("/events").catch(() => null)
        ]);
        
        let cameras = [];
        if (camerasRes && camerasRes.ok) {
            const camData = await camerasRes.json();
            if (Array.isArray(camData)) {
                cameras = camData;
            } else if (camData && typeof camData === 'object') {
                cameras = Object.entries(camData).map(([name, cam]) => ({
                    name: cam.name || name,
                    status: cam.status || 'OFFLINE',
                    location: cam.zone || cam.location || 'Unknown',
                    fps: cam.fps || 0,
                    health: cam.health || 'UNKNOWN'
                }));
            }
        }
        
        let events = [];
        if (eventsRes && eventsRes.ok) {
            events = await eventsRes.json();
            if (!Array.isArray(events)) events = [];
        }
        
        const cameraMarkers = document.querySelectorAll('.camera-marker');
        const eventMarkers = document.querySelectorAll('.event-marker');
        
        cameraMarkers.forEach((marker, index) => {
            const cam = cameras[index];
            if (cam) {
                marker.title = cam.name;
                marker.setAttribute('data-name', cam.name);
                marker.setAttribute('data-status', cam.status);
                marker.setAttribute('data-location', cam.location);
                
                marker.onclick = (e) => {
                    e.stopPropagation();
                    showTooltip(marker, `
                        <strong>📹 ${escapeHtml(cam.name)}</strong>
                        <div>Status: ${escapeHtml(cam.status)}</div>
                        <div>Location: ${escapeHtml(cam.location)}</div>
                        <div>FPS: ${cam.fps}</div>
                        <div>Health: ${escapeHtml(cam.health)}</div>
                    `);
                };
            } else {
                marker.style.display = 'none';
            }
        });
        
        eventMarkers.forEach((marker, index) => {
            const evt = events[index];
            if (evt) {
                const icons = {
                    'fall detection': '🚨',
                    'weapon detected': '🚨',
                    'running detected': '🏃',
                    'person detected': '🚶',
                    'vehicle detected': '🚗',
                    'crowd detected': '👥',
                    'loitering detected': '⏳'
                };
                const etype = (evt.event_type || 'Unknown').toLowerCase();
                const icon = icons[etype] || '📍';
                marker.textContent = icon;
                marker.title = evt.event_type || 'Event';
                marker.setAttribute('data-event', evt.event_type);
                marker.setAttribute('data-severity', evt.severity);
                marker.setAttribute('data-zone', evt.zone);
                marker.setAttribute('data-time', evt.timestamp);
                
                marker.onclick = (e) => {
                    e.stopPropagation();
                    showTooltip(marker, `
                        <strong>${escapeHtml(evt.event_type || 'Event')}</strong>
                        <div>Severity: ${escapeHtml(evt.severity || 'LOW')}</div>
                        <div>Zone: ${escapeHtml(evt.zone || 'Unknown')}</div>
                        <div>Time: ${escapeHtml(evt.timestamp || '')}</div>
                        <div>Camera: ${escapeHtml(evt.camera || 'Unknown')}</div>
                    `);
                };
            } else {
                marker.style.display = 'none';
            }
        });
        
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.camera-marker') && !e.target.closest('.event-marker')) {
                hideTooltip();
            }
        });
        
        hideSkeletons();
        
    } catch (err) {
        console.error("Failed to load security map:", err);
        hideSkeletons();
        showEmptyState("emptyState", "Unable to Load Security Map", "The map service could not be reached.", [{label:"Retry", onclick:"loadSecurityMap()", class:"btn-primary"}]);
    }
}

function showMapEmpty(message) {
    const container = document.querySelector(".map-container");
    if (!container) return;
    container.innerHTML = `
        <div style="text-align:center;padding:60px 20px;color:#64748b;">
            <div style="font-size:48px;margin-bottom:16px;opacity:0.6;">🗺️</div>
            <h3 style="color:#e2e8f0;margin:0 0 8px 0;">No Map Data</h3>
            <p style="margin:0 0 20px 0;">${escapeHtml(message)}</p>
            <button class="btn btn-secondary" onclick="loadSecurityMap()">Retry</button>
        </div>
    `;
}

function showTooltip(marker, html) {
    const tooltip = document.getElementById("mapTooltip");
    if (!tooltip) return;
    
    tooltip.innerHTML = html;
    tooltip.style.display = "block";
    
    const rect = marker.getBoundingClientRect();
    const container = document.querySelector(".map-container");
    const containerRect = container.getBoundingClientRect();
    
    tooltip.style.left = (rect.left - containerRect.left + 20) + "px";
    tooltip.style.top = (rect.top - containerRect.top - 10) + "px";
}

function hideTooltip() {
    const tooltip = document.getElementById("mapTooltip");
    if (tooltip) tooltip.style.display = "none";
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadSecurityMap();