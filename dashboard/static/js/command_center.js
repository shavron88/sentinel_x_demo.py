async function loadCommandCenter() {
    showSkeletonCards("command-grid", 4);
    const panels = {
        'live-wall': loadLiveWallPanel,
        'threat-feed': loadThreatFeedPanel,
        'analytics': loadAnalyticsPanel,
        'heatmap': loadHeatmapPanel,
        'security-map': loadSecurityMapPanel,
        'system-health': loadSystemHealthPanel,
        'copilot': loadCopilotPanel,
        'latest-evidence': loadLatestEvidencePanel
    };
    
    const grid = document.querySelector('.command-grid');
    if (!grid) {
        showEmptyState('emptyState', 'No Data Available', 'Command center is not available.', [{label:'Refresh', onclick:'loadCommandCenter()', class:'btn-primary'}]);
        return;
    }

    for (const [panelId, loader] of Object.entries(panels)) {
        const el = document.querySelector(`.${panelId}`);
        if (!el) continue;

        el.innerHTML = `<div class="panel-loading">Loading...</div>`;
        
        try {
            await loader(el);
        } catch (err) {
            console.error(`Failed to load ${panelId}:`, err);
            el.innerHTML = `
                <div class="panel-error">
                    <div class="panel-error-icon">⚠️</div>
                    <h3>Unable to Load</h3>
                    <p>The ${panelId.replace(/-/g, ' ')} service could not be reached.</p>
                    <button class="btn btn-secondary" onclick="loadCommandCenter()">Retry</button>
                </div>
            `;
        }
    }
    
    hideSkeletons();
}

function showCommandCenterEmpty() {
    const grid = document.querySelector(".command-grid");
    if (!grid) return;
    grid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:#64748b;">
            <div style="font-size:48px;margin-bottom:16px;opacity:0.6;">📊</div>
            <h3 style="color:#e2e8f0;margin:0 0 8px 0;">No Data Available</h3>
            <p style="margin:0 0 20px 0;">Command center panels are loading.</p>
            <button class="btn btn-primary" onclick="loadCommandCenter()">Refresh</button>
        </div>
    `;
}

async function loadLiveWallPanel(container) {
    const response = await fetch("/api/cameras");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    
    let cameras = [];
    if (Array.isArray(data)) {
        cameras = data;
    } else if (data && typeof data === 'object') {
        cameras = Object.entries(data).map(([name, cam]) => ({
            name: cam.name || name,
            status: cam.status || 'OFFLINE',
            fps: cam.fps || 0,
            health: cam.health || 'UNKNOWN'
        }));
    }
    
    const onlineCount = cameras.filter(c => c.status === 'ONLINE').length;
    
    container.innerHTML = `
        <div class="panel-header">
            <h3>📹 Live Camera Feeds</h3>
            <span class="badge badge-success">${onlineCount} Online</span>
        </div>
        <div class="panel-content">
            ${cameras.length === 0 ? '<p class="panel-empty">No cameras configured.</p>' : `
                <div class="mini-camera-list">
                    ${cameras.slice(0, 4).map(cam => `
                        <div class="mini-camera-item ${cam.status === 'ONLINE' ? 'online' : 'offline'}">
                            <span class="mini-camera-name">${escapeHtml(cam.name)}</span>
                            <span class="mini-camera-status">${cam.status}</span>
                            <span class="mini-camera-fps">${cam.fps} FPS</span>
                        </div>
                    `).join('')}
                </div>
            `}
        </div>
    `;
}

async function loadThreatFeedPanel(container) {
    const response = await fetch("/events");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const events = await response.json();
    
    const highSeverity = events.filter(e => (e.severity || 'LOW').toUpperCase() === 'HIGH' || (e.severity || 'LOW').toUpperCase() === 'CRITICAL');
    
    container.innerHTML = `
        <div class="panel-header">
            <h3>🚨 Active Threats</h3>
            <span class="badge badge-danger">${highSeverity.length} Active</span>
        </div>
        <div class="panel-content">
            ${highSeverity.length === 0 ? '<p class="panel-empty">No active threats.</p>' : `
                <div class="mini-threat-list">
                    ${highSeverity.slice(0, 5).map(e => `
                        <div class="mini-threat-item ${(e.severity || 'low').toLowerCase()}">
                            <span class="mini-threat-event">${escapeHtml(e.event_type || 'Unknown')}</span>
                            <span class="mini-threat-zone">${escapeHtml(e.zone || 'Unknown')}</span>
                            <span class="mini-threat-time">${escapeHtml(e.timestamp || '')}</span>
                        </div>
                    `).join('')}
                </div>
            `}
        </div>
    `;
}

async function loadAnalyticsPanel(container) {
    const response = await fetch("/analytics_data");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    
    container.innerHTML = `
        <div class="panel-header">
            <h3>📈 Analytics Overview</h3>
        </div>
        <div class="panel-content">
            <div class="mini-stats">
                <div class="mini-stat">
                    <span class="mini-stat-value">${data.total || 0}</span>
                    <span class="mini-stat-label">Incidents</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-value">${data.people || 0}</span>
                    <span class="mini-stat-label">People</span>
                </div>
                <div class="mini-stat">
                    <span class="mini-stat-value">${data.vehicles || 0}</span>
                    <span class="mini-stat-label">Vehicles</span>
                </div>
            </div>
        </div>
    `;
}

async function loadHeatmapPanel(container) {
    container.innerHTML = `
        <div class="panel-header">
            <h3>🔥 Activity Heatmap</h3>
        </div>
        <div class="panel-content">
            <div class="panel-pending">
                <div class="panel-pending-icon">🗺️</div>
                <h3>Backend Integration Pending</h3>
                <p>Heatmap data is not yet available.</p>
            </div>
        </div>
    `;
}

async function loadSecurityMapPanel(container) {
    container.innerHTML = `
        <div class="panel-header">
            <h3>🗺 Security Map</h3>
            <a href="/security_map" class="view-all-link">View Full →</a>
        </div>
        <div class="panel-content">
            <div class="panel-pending">
                <div class="panel-pending-icon">📍</div>
                <h3>Backend Integration Pending</h3>
                <p>Security map widget is not yet integrated.</p>
                <a href="/security_map" class="btn btn-secondary">Open Security Map</a>
            </div>
        </div>
    `;
}

async function loadSystemHealthPanel(container) {
    const response = await fetch("/api/v1/health");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    
    const system = data.system || {};
    const ai = data.ai_engine || {};
    
    container.innerHTML = `
        <div class="panel-header">
            <h3>🖥 System Health</h3>
        </div>
        <div class="panel-content">
            <div class="mini-health-list">
                <div class="mini-health-item">
                    <span>CPU</span>
                    <span class="mini-health-value">${system.cpu || '--'}%</span>
                </div>
                <div class="mini-health-item">
                    <span>RAM</span>
                    <span class="mini-health-value">${system.ram || '--'}%</span>
                </div>
                <div class="mini-health-item">
                    <span>GPU</span>
                    <span class="mini-health-value">${system.gpu || '--'}%</span>
                </div>
                <div class="mini-health-item">
                    <span>AI Engine</span>
                    <span class="mini-health-value ${ai.status === 'HEALTHY' ? 'healthy' : 'unhealthy'}">${ai.status || 'UNKNOWN'}</span>
                </div>
            </div>
        </div>
    `;
}

async function loadCopilotPanel(container) {
    container.innerHTML = `
        <div class="panel-header">
            <h3>🤖 AI Copilot</h3>
            <a href="/copilot" class="view-all-link">Open →</a>
        </div>
        <div class="panel-content">
            <div class="panel-pending">
                <div class="panel-pending-icon">💬</div>
                <h3>Backend Integration Pending</h3>
                <p>AI chat functionality is not yet connected.</p>
                <a href="/copilot" class="btn btn-secondary">Open Copilot</a>
            </div>
        </div>
    `;
}

async function loadLatestEvidencePanel(container) {
    const response = await fetch("/api/evidence");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const evidence = await response.json();
    
    container.innerHTML = `
        <div class="panel-header">
            <h3>📸 Latest Evidence</h3>
            <a href="/evidence" class="view-all-link">View All →</a>
        </div>
        <div class="panel-content">
            ${evidence.length === 0 ? '<p class="panel-empty">No evidence available.</p>' : `
                <div class="mini-evidence-list">
                    ${evidence.slice(0, 4).map(e => `
                        <div class="mini-evidence-item">
                            <img src="${escapeHtml(e.image || '')}" alt="${escapeHtml(e.event || 'Evidence')}" loading="lazy">
                            <span class="mini-evidence-event">${escapeHtml(e.event || 'Unknown')}</span>
                        </div>
                    `).join('')}
                </div>
            `}
        </div>
    `;
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadCommandCenter();
    window._commandCenterInterval = setInterval(loadCommandCenter, 30000);
/* ==========================================
   COMMAND CENTER CLEANUP
========================================== */

function cleanupCommandCenter() {
    if (window._commandCenterInterval) {
        clearInterval(window._commandCenterInterval);
        window._commandCenterInterval = null;
    }
    document.querySelectorAll('.command-grid img, .command-grid video').forEach(el => {
        if (el.tagName === 'VIDEO') {
            el.pause();
        }
        el.src = "";
    });
}

window.addEventListener("beforeunload", cleanupCommandCenter);
