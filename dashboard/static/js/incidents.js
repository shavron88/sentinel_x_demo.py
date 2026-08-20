let allIncidents = [];
let currentFilter = 'ALL';
let searchQuery = '';

async function loadIncidents() {
    const list = document.getElementById("incident-list");
    const empty = document.getElementById("emptyState");
    
    if (!list) return;
    
    list.innerHTML = "";
    if (empty) empty.style.display = "none";
    
    showSkeletonRows("incident-list", 5);
    
    try {
        const response = await fetch("/api/incidents");
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        allIncidents = Array.isArray(data) ? data : [];
        
        hideSkeletons();
        
        if (allIncidents.length === 0) {
            showEmptyState("emptyState", "No Incidents Found", "There are no incidents matching your criteria.", [{label:"Refresh", onclick:"loadIncidents()", class:"btn-primary"}]);
            return;
        }
        
        renderIncidents(allIncidents);
        
    } catch (err) {
        console.error("Failed to load incidents:", err);
        hideSkeletons();
        showEmptyState("emptyState", "Unable to Load Incidents", "The incident service could not be reached.", [{label:"Retry", onclick:"loadIncidents()", class:"btn-primary"}]);
    }
}

function renderIncidents(data) {
    const list = document.getElementById("incident-list");
    if (!list) return;
    
    list.innerHTML = "";
    
    let filtered = data;
    
    if (currentFilter !== 'ALL') {
        filtered = filtered.filter(i => i.severity === currentFilter);
    }
    
    if (searchQuery) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(i => 
            (i.type || '').toLowerCase().includes(q) ||
            (i.zone || '').toLowerCase().includes(q) ||
            (i.description || '').toLowerCase().includes(q) ||
            (i.camera || '').toLowerCase().includes(q)
        );
    }
    
    if (filtered.length === 0) {
        list.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px 20px;color:#64748b;">No incidents match your criteria</div>';
        return;
    }
    
    filtered.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = `incident-card ${(item.severity || 'LOW').toLowerCase()}`;
        card.style.animationDelay = `${Math.min(index * 0.04, 0.5)}s`;
        
        const severityClass = (item.severity || 'LOW').toLowerCase();
        const severityIcon = severityClass === 'critical' ? '🔴' : severityClass === 'high' ? '🟠' : severityClass === 'medium' ? '🟡' : '🟢';
        
        card.innerHTML = `
            <div class="incident-header">
                <h3>${escapeHtml(item.type || 'Unknown Incident')}</h3>
                <strong class="severity-badge ${severityClass}">${severityIcon} ${escapeHtml(item.severity || 'LOW')}</strong>
            </div>
            
            <div class="incident-meta">
                <span>📍 ${escapeHtml(item.zone || 'Unknown')}</span>
                <span>🕒 ${escapeHtml(item.time || '--:--')}</span>
                <span>📹 ${escapeHtml(item.camera || 'Unknown')}</span>
            </div>
            
            <div class="incident-description">
                ${escapeHtml(item.description || 'No description available')}
            </div>
            
            <div class="incident-footer">
                <span class="incident-id">ID: #INC-${escapeHtml(String(item.id || '--'))}</span>
                <button class="view-btn" onclick="viewIncidentEvidence(${item.id}, '${escapeHtml(item.type || '')}')">
                    View Evidence
                </button>
            </div>
        `;
        
        list.appendChild(card);
    });
}

function viewIncidentEvidence(incidentId, incidentType) {
    window.location.href = `/evidence?incident=${incidentId}`;
}

document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
        currentFilter = btn.dataset.filter || "ALL";
        renderIncidents(allIncidents);
    });
});

document.getElementById("incident-search").addEventListener("input", e => {
    searchQuery = e.target.value;
    renderIncidents(allIncidents);
});

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadIncidents();