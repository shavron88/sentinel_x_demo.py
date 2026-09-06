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
                        <strong><svg class="marker-icon" style="width:16px;height:16px;vertical-align:-3px;margin-right:6px;color:#3b82f6;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m23 7-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>${escapeHtml(cam.name)}</strong>
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
                const SVG = {
                    alert: '<svg class="marker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
                    person: '<svg class="marker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
                    vehicle: '<svg class="marker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17h14M5 17a2 2 0 0 1-2-2V9l2-5h14l2 5v6a2 2 0 0 1-2 2M7 17v2M17 17v2"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/></svg>',
                    crowd: '<svg class="marker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
                    run: '<svg class="marker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>',
                    pin: '<svg class="marker-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
                };
                const iconMap = {
                    'fall detection': SVG.alert,
                    'weapon detected': SVG.alert,
                    'running detected': SVG.run,
                    'person detected': SVG.person,
                    'vehicle detected': SVG.vehicle,
                    'crowd detected': SVG.crowd,
                    'loitering detected': SVG.pin
                };
                const etype = (evt.event_type || 'Unknown').toLowerCase();
                const icon = iconMap[etype] || SVG.pin;
                marker.innerHTML = icon;
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
            <div style="font-size:48px;margin-bottom:16px;opacity:0.6;"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3-6-3z"/><path d="M9 3v15M15 6v15"/></svg></div>
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