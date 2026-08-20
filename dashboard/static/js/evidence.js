let currentStorageGb = null;

let evidenceData = [];

let selectedEvidence = null;

let selectedIds = new Set();

let currentFilter = 'all';

let currentView = 'grid';

/* ==========================================
    LOADING & INIT
========================================== */
async function loadEvidence() {

    const grid = document.getElementById("galleryGrid");

    const empty = document.getElementById("noEvidence");

    grid.innerHTML = "";

    empty.style.display = "none";

    showSkeletons();

    try {

        const [evidenceRes, storageRes] = await Promise.all([

            fetch("/api/evidence"),

            fetch("/api/storage").catch(() => null)

        ]);

        if (!evidenceRes || !evidenceRes.ok) {

            throw new Error(`HTTP ${evidenceRes ? evidenceRes.status : 'Network'}`);

        }

        const data = await evidenceRes.json();

        evidenceData = Array.isArray(data) ? data : [];

        let storageGb = null;

        if (storageRes && storageRes.ok) {

            const storageData = await storageRes.json();

            storageGb = storageData.storage_gb;

        }

        currentStorageGb = storageGb;

        updateStats(storageGb);

        renderGallery(evidenceData);

        hideSkeletons();

        updateTimeline();

        updateHistogram();

    }

    catch (err) {

        console.error("Failed to load evidence:", err);

        hideSkeletons();

        showEmptyState("emptyState", "Unable to Load Evidence", "The evidence service could not be reached.", [{label:"Retry", onclick:"loadEvidence()", class:"btn-primary"}]);

    }

}
function showSkeletons(){

    const grid = document.getElementById("galleryGrid");

    for(let i = 0; i < 6; i++){

        const card = document.createElement("div");

        card.className = "ev-card skeleton-card";

        card.innerHTML = `

            <div class="ev-card-image">

                <div class="ev-card-placeholder"></div>

            </div>

            <div class="ev-card-info">

                <div class="skeleton-line" style="width:65%;height:10px;margin-bottom:8px;"></div>

                <div class="skeleton-line" style="width:100%;height:10px;margin-bottom:6px;"></div>

                <div class="skeleton-line" style="width:45%;height:10px;"></div>

            </div>

        `;

        grid.appendChild(card);

    }

}

function hideSkeletons(){

    const grid = document.getElementById("galleryGrid");

    grid.querySelectorAll(".skeleton-card").forEach(c => c.remove());

}

function showError(){

    const grid = document.getElementById("galleryGrid");

    const empty = document.getElementById("noEvidence");

    grid.innerHTML = "";

    grid.style.display = "none";

    empty.style.display = "flex";

    empty.innerHTML = `

        <div class="ev-empty-icon">

            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">

                <rect x="3" y="3" width="18" height="18" rx="2"></rect>

                <circle cx="8.5" cy="8.5" r="1.5"></circle>

                <path d="M21 15l-5-5L11 19"></path>

            </svg>

        </div>

        <h3>Unable to Load Evidence</h3>

        <p>The evidence service could not be reached. Please try again.</p>

        <div class="ev-empty-actions">

            <button class="btn btn-primary" onclick="loadEvidence()">

                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">

                    <polyline points="23 4 23 10 17 10"></polyline>

                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>

                </svg>

                Retry

            </button>

        </div>

    `;

}

/* ==========================================
   STATS
========================================== */

function updateStats(storageGb){

    const total = evidenceData.length;

    const favs = evidenceData.filter(e => e.favorite).length;

    const today = evidenceData.filter(e => {

        const d = new Date(e.time || "");

        const now = new Date();

        return d.toDateString() === now.toDateString();

    }).length;

    const critical = evidenceData.filter(e => {

        const sev = getSeverity(e.severity || e.event);

        return sev === 'critical' || sev === 'high';

    }).length;

    const avgConf = evidenceData.length > 0 ?

        (evidenceData.reduce((sum, e) => sum + (parseFloat(e.confidence) || 0), 0) / evidenceData.length).toFixed(1) + '%'

        : '0%';

    document.getElementById("statTotal").textContent = total;

    document.getElementById("statToday").textContent = today;

    document.getElementById("statCritical").textContent = critical;

    document.getElementById("statStorage").textContent = storageGb !== null ? storageGb + ' GB' : '0 GB';

    document.getElementById("statConfidence").textContent = avgConf;

}

/* ==========================================
   HISTOGRAM
========================================== */

function updateHistogram(){

    const container = document.getElementById("evHistogram");

    if(!container) return;

    if (evidenceData.length === 0) {

        container.innerHTML = '<div style="color:var(--ev-text-muted);font-size:12px;padding:10px;">No data available</div>';

        return;

    }

    const hours = 12;

    const bars = [];

    const now = new Date();

    for(let i = hours - 1; i >= 0; i--){

        const hourStart = new Date(now);

        hourStart.setHours(now.getHours() - i, 0, 0, 0);

        const hourEnd = new Date(hourStart);

        hourEnd.setHours(hourStart.getHours() + 1);

        const count = evidenceData.filter(e => {

            const t = new Date(e.time || "");

            return t >= hourStart && t < hourEnd;

        }).length;

        const maxCount = Math.max(1, ...evidenceData.map(e => {

            const t = new Date(e.time || "");

            const h = new Date(t);

            h.setMinutes(0, 0, 0);

            return evidenceData.filter(ev => {

                const te = new Date(ev.time || "");

                const he = new Date(te);

                he.setMinutes(0, 0, 0);

                return he.getTime() === h.getTime();

            }).length;

        }));

        const height = maxCount > 0 ? Math.max(8, (count / maxCount) * 100) : 8;

        const label = `${hourStart.getHours()}:00`;

        bars.push(`<div class="ev-histogram-bar" style="height:${height}%;"><span class="ev-histogram-label">${label}</span></div>`);

    }

    container.innerHTML = bars.join("");

}

/* ==========================================
   CAMERA MAP
========================================== */

function updateCameraMap(item){

    const cameras = document.querySelectorAll(".ev-camera-item");

    cameras.forEach(cam => {

        const name = cam.querySelector(".ev-camera-name")?.textContent || "";

        if(item && item.camera && name.toLowerCase().includes(item.camera.toLowerCase())){

            cam.style.background = "rgba(59,130,246,.12)";

            cam.style.borderColor = "rgba(59,130,246,.25)";

        } else {

            cam.style.background = "";

            cam.style.borderColor = "";

        }

    });

}

/* ==========================================
   RENDER GALLERY
========================================== */

function getSeverity(sev){

    if (!sev) return 'low';

    const s = String(sev).toLowerCase();

    if(s.includes("critical") || s.includes("weapon")) return "critical";

    if(s.includes("high") || s.includes("fall") || s.includes("perimeter")) return "high";

    if(s.includes("medium") || s.includes("loiter") || s.includes("crowd") || s.includes("vehicle")) return "medium";

    return "low";

}

function getEventLabel(event){

    if (!event) return 'Unknown';

    return String(event)

        .replace(/_/g, " ")

        .replace("DETECTED", "")

        .replace("VEHICLE", "Vehicle")

        .trim();

}

function renderGallery(data){

    const grid = document.getElementById("galleryGrid");

    const empty = document.getElementById("noEvidence");

    grid.innerHTML = "";

    if(data.length === 0){

        grid.style.display = "none";

        empty.style.display = "flex";

        empty.innerHTML = `

            <div class="ev-empty-icon">

                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">

                    <rect x="3" y="3" width="18" height="18" rx="2"></rect>

                    <circle cx="8.5" cy="8.5" r="1.5"></circle>

                    <path d="M21 15l-5-5L11 19"></path>

                </svg>

            </div>

            <h3>No Evidence Found</h3>

            <p>AI has not recorded any evidence matching your criteria.</p>

            <div class="ev-empty-actions">

                <button class="btn btn-primary" onclick="loadEvidence()">

                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">

                        <polyline points="23 4 23 10 17 10"></polyline>

                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>

                    </svg>

                    Refresh

                </button>

                <button class="btn btn-secondary" onclick="window.location.href='/cameras'">

                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">

                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>

                        <circle cx="12" cy="13" r="4"></circle>

                    </svg>

                    Open Cameras

                </button>

            </div>

        `;

        return;

    }

    grid.style.display = "";

    empty.style.display = "none";

    data.forEach((item, index) => {

        const card = createEvidenceCard(item, index);

        grid.appendChild(card);

    });

}

function escapeHtml(text){

    if(text == null) return "";

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}

function createEvidenceCard(item, index){

    const card = document.createElement("div");

    card.className = "ev-card";

    card.style.animationDelay = `${Math.min(index * 0.04, 0.5)}s`;

    if(selectedIds.has(item.image)){

        card.classList.add("selected");

    }

    const severity = getSeverity(item.severity || item.event);

    const confidence = item.confidence ? parseFloat(item.confidence).toFixed(1) : '--';

    const timeStr = item.time ? formatTime(item.time) : '--';

    const trackingId = item.trackingId ? `#TX-${item.trackingId}` : '--';

    card.innerHTML = `

        <div class="ev-card-image">

            <div class="ev-card-placeholder"></div>

            <img src="${escapeHtml(item.image || '')}"

                 alt="${escapeHtml(getEventLabel(item.event))}"

                 class="ev-card-img"

                 loading="lazy"

                 style="max-width:100%;object-fit:cover;"

                 onload="this.classList.add('loaded')"

                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22%3E%3Crect fill=%22%231a2332%22 width=%22300%22 height=%22200%22/%3E%3Ctext fill=%22%2364748b%22 x=%22150%22 y=%22100%22 text-anchor=%22middle%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'">

            <div class="ev-card-badges">

                <span class="ev-threat-badge ${severity}">

                    ${severity === 'critical' ? '🔴' : severity === 'high' ? '🟠' : severity === 'medium' ? '🟡' : '🟢'}

                    ${escapeHtml(severity.toUpperCase())}

                </span>

                <span class="ev-fav-badge ${item.favorite ? 'active' : ''}"

                     onclick="event.stopPropagation(); toggleFavorite('${escapeHtml(item.image)}')">

                    ${item.favorite ? '⭐' : '☆'}

                </span>

            </div>

            <div class="ev-card-overlay">

                <button class="ev-overlay-btn" onclick="event.stopPropagation(); openFullscreenFor('${escapeHtml(item.image)}')" title="Preview">

                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>

                        <circle cx="12" cy="12" r="3"></circle>

                    </svg>

                </button>

                <button class="ev-overlay-btn" onclick="event.stopPropagation(); downloadEvidence('${escapeHtml(item.image)}')" title="Download">

                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>

                        <polyline points="7 10 12 15 17 10"></polyline>

                        <line x1="12" y1="15" x2="12" y2="3"></line>

                    </svg>

                </button>

                <button class="ev-overlay-btn" onclick="event.stopPropagation(); toggleFavorite('${escapeHtml(item.image)}')" title="Favorite">

                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>

                    </svg>

                </button>

            </div>

        </div>

        <div class="ev-card-info">

            <h4 class="ev-card-title">${escapeHtml(getEventLabel(item.event))}</h4>

            <div class="ev-card-meta">

                <span><span class="meta-icon">📹</span> ${escapeHtml(item.camera || 'Camera 01')}</span>

                <span><span class="meta-icon">📍</span> ${escapeHtml(item.location || 'Unknown')}</span>

                <span><span class="meta-icon">🕒</span> ${timeStr}</span>

            </div>

            <div class="ev-card-footer">

                <span class="ev-card-id">ID: #EV-${escapeHtml(String(item.id || '--'))}</span>

                <span class="ev-card-confidence">${confidence}%</span>

            </div>

        </div>

    `;

    card.onclick = () => selectEvidence(item, card);

    return card;

}

function formatTime(timeStr){

    if (!timeStr) return '--';

    try {

        const d = new Date(timeStr);

        if (isNaN(d.getTime())) return timeStr;

        return d.toLocaleString("en-US", {

            month: "short",

            day: "numeric",

            hour: "2-digit",

            minute: "2-digit",

            hour12: false

        });

    } catch {

        return timeStr;

    }

}

/* ==========================================
   SELECTION & DETAILS
========================================== */

function selectEvidence(item, cardElement){

    if(compareMode && compareInitialItem && item.image !== compareInitialItem.image){

        const imgB = document.getElementById("compareImageB");

        const titleB = document.getElementById("compareTitleB");

        const labelB = document.getElementById("compareLabelB");

        imgB.src = item.image;

        titleB.textContent = getEventLabel(item.event);

        labelB.textContent = (item.camera || "Unknown") + " • " + (item.time || "");

        showToast("Compare", "Evidence B selected. Click Confirm.", "success");

        return;

    }

    selectedEvidence = item;

    document.querySelectorAll(".ev-card").forEach(c => c.classList.remove("selected"));

    if(cardElement){

        cardElement.classList.add("selected");

        cardElement.scrollIntoView({ behavior:"smooth", block:"nearest" });

    }

    const preview = document.getElementById("previewImage");

    preview.src = item.image || '';

    document.getElementById("summaryEvent").textContent = getEventLabel(item.event);

    const confidence = item.confidence ? parseFloat(item.confidence).toFixed(1) + '%' : '--%';

    document.getElementById("summaryConfidence").textContent = confidence;

    document.getElementById("summaryCamera").textContent = item.camera || 'Camera 01';

    document.getElementById("summaryTracking").textContent = item.trackingId ? `#TX-${item.trackingId}` : '--';

    document.getElementById("summaryThreat").textContent = getSeverity(item.severity || item.event).toUpperCase();

    document.getElementById("summaryZone").textContent = item.location || 'Unknown';

    document.getElementById("summaryTime").textContent = formatTime(item.time);

    const ring = document.getElementById("confidenceRing");

    const ringValue = document.getElementById("confidenceValue");

    if(ring && ringValue){

        const pct = item.confidence ? parseFloat(item.confidence) : 0;

        const color = pct >= 95 ? '#22c55e' : pct >= 85 ? '#f59e0b' : '#ef4444';

        ring.style.transition = 'background .8s ease';

        ring.style.background = `conic-gradient(${color} ${pct}%, #1e293b 0)`;

        ringValue.textContent = pct > 0 ? pct.toFixed(1) + '%' : '--%';

    }

    updateThreatBadge(item);

    updateDetailsPanel(item);

    updateCameraMap(item);

    updateAIDescription(item);

    updateSimilarEvidence(item);

    updateOcrAndTags(item);

}

function updateDetailsPanel(item){

    const favBtn = document.getElementById("sidebarFavorite");

    if(!item){

        document.getElementById("previewImage").src = "";

        document.getElementById("summaryEvent").textContent = "-";

        favBtn.classList.remove("active");

        return;

    }

    if(item.favorite){

        favBtn.classList.add("active");

    } else {

        favBtn.classList.remove("active");

    }

}

/* ==========================================
   THREAT BADGE
========================================== */

function updateThreatBadge(item){

    const badge = document.getElementById("threatBadge");

    const dot = badge?.querySelector(".threat-dot");

    const text = document.getElementById("threatText");

    if(!badge || !dot || !text) return;

    const sev = getSeverity(item.severity || item.event);

    const labels = { critical: "CRITICAL", high: "HIGH", medium: "MEDIUM", low: "LOW" };

    dot.className = "threat-dot " + sev;

    text.textContent = labels[sev] || "LOW";

    badge.className = "ev-badge";

    badge.classList.add("threat-" + sev);

}

/* ==========================================
   AI DESCRIPTION
========================================== */

function generateAIDescription(item){

    if(!item) return "No evidence selected.";

    const eventLabel = getEventLabel(item.event);

    const severity = getSeverity(item.event);

    const camera = item.camera || "an unknown camera";

    const location = item.location || "an unspecified zone";

    const time = item.time || new Date().toLocaleTimeString();

    const conf = parseFloat(item.confidence) || 95;

    const threatText = {

        critical: "a critical security threat requiring immediate attention",

        high: "a high-severity security incident",

        medium: "a moderate security event",

        low: "a routine security detection"

    }[severity] || "a security detection";

    return `AI analysis detected ${eventLabel} at ${camera} (${location}) at ${time}. `

        + `Confidence: ${conf}%. Classification: ${threatText}. `

        + "Review footage and take appropriate action if needed.";

}

function updateAIDescription(item){

    const descEl = document.getElementById("aiDescriptionText");

    if(!descEl) return;

    if(!item){

        descEl.textContent = "Select an evidence item for AI analysis.";

        return;

    }

    const desc = item.description || generateAIDescription(item);

    descEl.textContent = desc;

}

/* ==========================================
   SIMILAR EVIDENCE
========================================== */

function updateSimilarEvidence(item){

    const listEl = document.getElementById("similarEvidenceList");

    const countEl = document.getElementById("similarCount");

    if(!listEl || !countEl) return;

    if(!item){

        listEl.innerHTML = '<div class="ev-similar-empty">No evidence selected.</div>';

        countEl.textContent = "0";

        return;

    }

    const similar = evidenceData.filter(e => {

        if(e.image === item.image) return false;

        const sameEvent = e.event === item.event;

        const sameCamera = e.camera === item.camera;

        const sameTracking = e.trackingId && e.trackingId === item.trackingId;

        const nearbyTime = e.time && item.time && Math.abs(new Date(e.time) - new Date(item.time)) < 3600000;

        return sameEvent || sameCamera || sameTracking || nearbyTime;

    }).slice(0, 5);

    countEl.textContent = similar.length;

    if(similar.length === 0){

        listEl.innerHTML = '<div class="ev-similar-empty">No similar evidence found.</div>';

        return;

    }

    listEl.innerHTML = similar.map(e => {

        const time = e.time || "";

        const label = getEventLabel(e.event);

        const camera = e.camera || "";

        return `

            <div class="ev-similar-item" onclick="selectSimilarEvidence('${escapeHtml(e.image)}')">

                <img src="${escapeHtml(e.image)}" class="ev-similar-thumb" alt="${escapeHtml(label)}">

                <div class="ev-similar-info">

                    <div class="ev-similar-title">${escapeHtml(label)}</div>

                    <div class="ev-similar-meta">${escapeHtml(camera)} • ${escapeHtml(time)}</div>

                </div>

            </div>

        `;

    }).join("");

}

function selectSimilarEvidence(imageSrc){

    const item = evidenceData.find(e => e.image === imageSrc);

    if(item){

        let targetCard = null;

        document.querySelectorAll(".ev-card").forEach(c => {

            const img = c.querySelector(".ev-card-img");

            if(img && img.src.endsWith(imageSrc)){

                targetCard = c;

            }

        });

        selectEvidence(item, targetCard);

    }

}

/* ==========================================
   OCR & TAGS
========================================== */

function updateOcrAndTags(item){

    if(!item) return;

    const ocrEl = document.getElementById("ocrText");

    const tagsEl = document.getElementById("evidenceTags");

    if(!ocrEl || !tagsEl) return;

    const ocrText = item.ocr_text || item.metadata?.ocr_text || "";

    if(ocrText){

        ocrEl.textContent = ocrText;

    } else {

        ocrEl.textContent = "No OCR data available for this evidence.";

    }

    const tags = item.tags || item.metadata?.tags || [];

    if(tags.length > 0){

        tagsEl.innerHTML = tags.map(tag => `<span class="ev-tag">${escapeHtml(tag)}</span>`).join("");

    } else {

        const inferred = inferTags(item);

        tagsEl.innerHTML = inferred.map(t => `<span class="ev-tag ${escapeHtml(t.type)}">${escapeHtml(t.label)}</span>`).join("");

    }

}

function inferTags(item){

    const event = (item.event || "").toLowerCase();

    const tags = [];

    if(event.includes("person")) tags.push({label: "Person", type: "person"});

    if(event.includes("vehicle")) tags.push({label: "Vehicle", type: "vehicle"});

    if(event.includes("weapon")) tags.push({label: "Weapon", type: "weapon"});

    if(event.includes("loiter") || event.includes("crowd") || event.includes("running"))

        tags.push({label: "Behavior", type: "behavior"});

    if(item.location) tags.push({label: item.location, type: "location"});

    if(tags.length === 0) tags.push({label: "Uncategorized", type: ""});

    return tags;

}

/* ==========================================
   FAVORITES
========================================== */

function toggleFavorite(imageSrc){

    if (!imageSrc) return;

    const item = evidenceData.find(e => e.image === imageSrc);

    if(!item) return;

    item.favorite = !item.favorite;

    const filtered = getCurrentFilteredData();

    renderGallery(filtered);

    updateStats(currentStorageGb);

    if(selectedEvidence && selectedEvidence.image === imageSrc){

        selectedEvidence = item;

        updateDetailsPanel(item);

    }

}

/* ==========================================
   FILTERING
========================================== */

function getCurrentFilteredData(){

    const searchVal = document.getElementById("searchEvidence").value.toLowerCase();

    return evidenceData.filter(item => {

        const matchesSearch = !searchVal ||

            (item.event || '').toLowerCase().includes(searchVal) ||

            (item.camera || '').toLowerCase().includes(searchVal) ||

            (item.location || '').toLowerCase().includes(searchVal) ||

            (item.trackingId || '').toLowerCase().includes(searchVal) ||

            String(item.id || '').includes(searchVal);

        const matchesFilter = currentFilter === 'all' ||

            (currentFilter === 'today' && isToday(item)) ||

            (currentFilter === 'yesterday' && isYesterday(item)) ||

            (currentFilter === 'week' && isThisWeek(item)) ||

            (currentFilter === 'high' && ['high', 'critical'].includes(getSeverity(item.severity || item.event))) ||

            (currentFilter === 'critical' && getSeverity(item.severity || item.event) === 'critical') ||

            (currentFilter === 'person' && (item.event || '').toLowerCase().includes('person')) ||

            (currentFilter === 'vehicle' && (item.event || '').toLowerCase().includes('vehicle')) ||

            (currentFilter === 'weapon' && (item.event || '').toLowerCase().includes('weapon')) ||

            (currentFilter === 'crowd' && (item.event || '').toLowerCase().includes('crowd')) ||

            (currentFilter === 'running' && (item.event || '').toLowerCase().includes('running')) ||

            (currentFilter === 'loitering' && (item.event || '').toLowerCase().includes('loiter')) ||

            (currentFilter === 'fall' && (item.event || '').toLowerCase().includes('fall'));

        return matchesSearch && matchesFilter;

    });

}

function isToday(item){

    const d = new Date(item.time || "");

    return d.toDateString() === new Date().toDateString();

}

function isYesterday(item){

    const d = new Date(item.time || "");

    const yesterday = new Date();

    yesterday.setDate(yesterday.getDate() - 1);

    return d.toDateString() === yesterday.toDateString();

}

function isThisWeek(item){

    const d = new Date(item.time || "");

    const now = new Date();

    const day = now.getDay();

    const diff = now.getDate() - day;

    const weekStart = new Date(now.setDate(diff));

    weekStart.setHours(0, 0, 0, 0);

    return d >= weekStart;

}

/* ==========================================
   FILTER CHIPS
========================================== */

document.querySelectorAll(".chip").forEach(chip => {

    chip.addEventListener("click", function() {

        document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));

        this.classList.add("active");

        currentFilter = this.dataset.filter;

        const filtered = getCurrentFilteredData();

        renderGallery(filtered);

    });

});

document.getElementById("searchEvidence").addEventListener("input", () => {

    const filtered = getCurrentFilteredData();

    renderGallery(filtered);

});

/* ==========================================
   VIEW TOGGLE
========================================== */

document.querySelectorAll(".view-btn").forEach(btn => {

    btn.addEventListener("click", function() {

        const view = this.dataset.view;

        const grid = document.getElementById("galleryGrid");

        grid.classList.remove("list-view", "timeline-view", "map-view");

        if(view === "list"){

            grid.classList.add("list-view");

        } else if(view === "timeline"){

            grid.classList.add("timeline-view");

        } else if(view === "map"){

            grid.classList.add("map-view");

        }

        document.querySelectorAll(".view-btn").forEach(b => b.classList.remove("active"));

        this.classList.add("active");

    });

});

/* ==========================================
   BULK SELECTION
========================================== */

function toggleSelectAll(){

    const selectAll = document.getElementById("selectAll");

    const cards = document.querySelectorAll(".ev-card");

    cards.forEach(card => {

        const img = card.querySelector(".ev-card-img");

        if(!img) return;

        if(selectAll.checked){

            selectedIds.add(img.src);

            card.classList.add("selected");

        } else {

            selectedIds.delete(img.src);

            card.classList.remove("selected");

        }

    });

    updateBulkBar();

}

function updateBulkBar(){

    const bulkBar = document.getElementById("bulkBar");

    const count = document.getElementById("selectedCount");

    count.textContent = selectedIds.size;

    bulkBar.style.display = selectedIds.size > 0 ? "flex" : "none";

}

/* ==========================================
   BULK ACTIONS
========================================== */

function bulkAction(action){

    if(selectedIds.size === 0) return;

    showToast("Bulk Action", `${action.charAt(0).toUpperCase() + action.slice(1)}ing ${selectedIds.size} items...`, "info");

    selectedIds.clear();

    document.getElementById("selectAll").checked = false;

    updateBulkBar();

    renderGallery(getCurrentFilteredData());

}

/* ==========================================
   TIMELINE
========================================== */

function updateTimeline(){

    const timeline = document.getElementById("evidenceTimeline");

    if(!timeline) return;

    const items = evidenceData.slice(0, 8);

    timeline.innerHTML = items.map((item, i) => {

        const time = formatTime(item.time) || new Date(Date.now() - i * 60000).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

        return `

            <div class="ev-timeline-item">

                <span class="ev-timeline-time">${time}</span>

                <div class="ev-timeline-content">

                    <div class="ev-timeline-title">${getEventLabel(item.event)}</div>

                    <div class="ev-timeline-meta">${item.camera || 'Camera 01'} • ${item.location || 'Unknown'}</div>

                </div>

            </div>

        `;

    }).join("");

}

/* ==========================================
   ACTIONS
========================================== */

document.getElementById("sidebarFavorite").addEventListener("click", () => {

    if(!selectedEvidence) return;

    toggleFavorite(selectedEvidence.image);

});

document.getElementById("sidebarDownload").addEventListener("click", () => {

    if(!selectedEvidence) return;

    downloadEvidence(selectedEvidence.image);

});

function downloadEvidence(imageSrc){

    if (!imageSrc) return;

    const a = document.createElement("a");

    a.href = imageSrc;

    a.download = `evidence_${Date.now()}.jpg`;

    a.click();

    showToast("Download", "Evidence downloaded successfully", "success");

}

function exportAll(){

    showToast("Export", "Preparing evidence export...", "info");

}

function openFullscreenFor(imageSrc){

    const item = evidenceData.find(e => e.image === imageSrc);

    if(!item) return;

    selectedEvidence = item;

    openFullscreen();

}

function downloadCurrent(){

    if(!selectedEvidence) return;

    downloadEvidence(selectedEvidence.image);

}

function favoriteCurrent(){

    if(!selectedEvidence) return;

    toggleFavorite(selectedEvidence.image);

}

/* ==========================================
   COMPARE TWO EVIDENCES
========================================== */

let compareMode = false;

let compareInitialItem = null;

function openCompareMode(){

    if(!selectedEvidence) return;

    compareMode = true;

    compareInitialItem = selectedEvidence;

    const modal = document.getElementById("compareModal");

    const imgA = document.getElementById("compareImageA");

    const titleA = document.getElementById("compareTitleA");

    const labelA = document.getElementById("compareLabelA");

    imgA.src = selectedEvidence.image;

    titleA.textContent = getEventLabel(selectedEvidence.event);

    labelA.textContent = (selectedEvidence.camera || "Unknown") + " • " + (selectedEvidence.time || "");

    document.getElementById("compareImageB").src = "";

    document.getElementById("compareTitleB").textContent = "Select Evidence B";

    document.getElementById("compareLabelB").textContent = "";

    modal.style.display = "flex";

    requestAnimationFrame(() => modal.classList.add("show"));

    document.body.style.overflow = "hidden";

    showToast("Compare Mode", "Click any evidence card to compare.", "info");

}

function closeCompare(){

    const modal = document.getElementById("compareModal");

    modal.classList.remove("show");

    setTimeout(() => { modal.style.display = "none"; }, 350);

    document.body.style.overflow = "";

    compareMode = false;

    compareInitialItem = null;

}

function confirmCompare(){

    showToast("Compare", "Comparison saved.", "success");

    closeCompare();

}

document.getElementById("compareModal").addEventListener("click", function(e){

    if(e.target === this){

        closeCompare();

    }

});

document.getElementById("fullscreenModal").addEventListener("click", function(e){

    if(e.target === this){

        closeFullscreen();

    }

});

window.addEventListener("keydown", (e) => {

    if(e.key === "Escape"){

        if(compareMode){

            closeCompare();

        } else {

            closeFullscreen();

        }

    }

});

/* ==========================================
   TOAST
========================================== */

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
   SMOOTH ANIMATIONS
========================================== */

function setupSmoothAnimations() {

    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                entry.target.style.opacity = '1';

                entry.target.style.transform = 'translateY(0) scale(1)';

                observer.unobserve(entry.target);

            }

        });

    }, {

        threshold: 0.1,

        rootMargin: '0px 0px -40px 0px'

    });

    document.querySelectorAll('.ev-card, .ev-stat-card, .ev-preview-card, .ev-summary-card, .ev-timeline-card').forEach(el => {

        el.style.opacity = '0';

        el.style.transform = 'translateY(20px) scale(0.97)';

        el.style.transition = 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';

        observer.observe(el);

    });

}

/* ==========================================
   SMOOTH MODAL
========================================== */

function openFullscreen(){

    if(!selectedEvidence) return;

    const modal = document.getElementById("fullscreenModal");

    const dialog = modal.querySelector('.ev-modal-dialog') || modal;

    document.getElementById("fullscreenImage").src = selectedEvidence.image || '';

    document.getElementById("modalEvent").textContent = getEventLabel(selectedEvidence.event);

    document.getElementById("modalCamera").textContent = selectedEvidence.camera || 'Camera 01';

    document.getElementById("modalTime").textContent = formatTime(selectedEvidence.time);

    modal.style.display = "flex";

    requestAnimationFrame(() => {

        requestAnimationFrame(() => {

            modal.classList.add("show");

            setupSmoothAnimations();

        });

    });

    document.body.style.overflow = "hidden";

}

function closeFullscreen(){

    const modal = document.getElementById("fullscreenModal");

    modal.classList.remove("show");

    setTimeout(() => {

        modal.style.display = "none";

    }, 400);

    document.body.style.overflow = "";

}

/* ==========================================
   INIT
========================================== */

loadEvidence();

document.addEventListener('DOMContentLoaded', () => {

    setTimeout(setupSmoothAnimations, 100);

});
