/**
 * Incident center.
 *
 * This is the single implementation for /incidents. The page template used to
 * embed a second, near-identical <script> that fetched /events, bound its own
 * filter handlers and re-rendered #incident-list -- so every filter click ran
 * two renderers and two competing fetch loops.
 */
let allIncidents = [];
let currentFilter = 'ALL';
let searchQuery = '';

async function loadIncidents() {
    const list = document.getElementById("incident-list");
    const empty = document.getElementById("emptyState");

    if (!list) return;

    if (empty) empty.style.display = "none";
    showSkeletonRows("incident-list", 5);

    try {
        const response = await fetch("/api/incidents?limit=200");

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

        updateIncidentSummary(allIncidents);
        renderIncidents(allIncidents);

    } catch (err) {
        console.error("Failed to load incidents:", err);
        hideSkeletons();
        showEmptyState("emptyState", "Unable to Load Incidents", "The incident service could not be reached.", [{label:"Retry", onclick:"loadIncidents()", class:"btn-primary"}]);
    }
}

/** Updates the summary strip counts shown above the incident list. */
function updateIncidentSummary(items) {
    const severity = (i) => (i.severity || "LOW").toUpperCase();
    const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };
    set("incident-count", items.length);
    set("critical-count", items.filter(i => severity(i) === "HIGH" || severity(i) === "CRITICAL").length);
    set("medium-count", items.filter(i => severity(i) === "MEDIUM").length);
    set("low-count", items.filter(i => severity(i) === "LOW").length);
}

function renderIncidents(data) {
    const list = document.getElementById("incident-list");
    if (!list) return;

    let filtered = data;

    if (currentFilter !== 'ALL') {
        filtered = filtered.filter(i => (i.severity || "LOW").toUpperCase() === currentFilter);
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

    list.innerHTML = "";

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
                <button class="view-btn" onclick="viewIncidentEvidence(${Number(item.id) || 0})">
                    View Evidence
                </button>
            </div>
        `;

        list.appendChild(card);
    });
}

function viewIncidentEvidence(incidentId) {
    window.location.href = `/evidence?incident=${encodeURIComponent(incidentId)}`;
}

function initIncidentFilters() {
    document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentFilter = btn.dataset.filter || "ALL";
            renderIncidents(allIncidents);
        });
    });

    const search = document.getElementById("incident-search");
    if (!search) return;

    let searchTimer;
    search.addEventListener("input", e => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            searchQuery = e.target.value;
            renderIncidents(allIncidents);
        }, 180);
    });

    document.addEventListener("keydown", e => {
        if (e.key === "/" && document.activeElement !== search) {
            e.preventDefault();
            search.focus();
        }
    });
}

initIncidentFilters();
loadIncidents();
window._incidentsInterval = setInterval(loadIncidents, 10000);

window.addEventListener("beforeunload", () => {
    if (window._incidentsInterval) clearInterval(window._incidentsInterval);
});
