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

        const response = await fetch("/api/evidence");

        const data = await response.json();

        evidenceData = data.evidence || [];

        updateStats();

        renderGallery(evidenceData);

        hideSkeletons();

        updateTimeline();

        updateHistogram();

    }

    catch (err) {

        console.error("Failed to load evidence:", err);

        hideSkeletons();

        showError();

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

        <div class="ev-empty-icon">⚠️</div>

        <h3>Failed to Load Evidence</h3>

        <p>Please check your connection and try again</p>

        <button class="btn btn-primary" onclick="loadEvidence()" style="margin-top:16px;">

            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">

                <polyline points="23 4 23 10 17 10"></polyline>

                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>

            </svg>

            Retry

        </button>

    `;

}

/* ==========================================
   STATS
========================================== */

function updateStats(){

    const total = evidenceData.length;

    const favs = evidenceData.filter(e => e.favorite).length;

    const today = evidenceData.filter(e => {

        const d = new Date(e.time || e.date || "");

        const now = new Date();

        return d.toDateString() === now.toDateString();

    }).length;

    const critical = evidenceData.filter(e => {

        const sev = getSeverity(e.event);

        return sev === 'critical' || sev === 'high';

    }).length;

    const avgConf = evidenceData.length > 0 ?

        (evidenceData.reduce((sum, e) => sum + (parseFloat(e.confidence) || 98), 0) / evidenceData.length).toFixed(1) + '%'

        : '0%';

    document.getElementById("statTotal").textContent = total;

    document.getElementById("statToday").textContent = today;

    document.getElementById("statCritical").textContent = critical;

    document.getElementById("statStorage").textContent = (total * 0.05).toFixed(1) + ' GB';

    document.getElementById("statConfidence").textContent = avgConf;

}

/* ==========================================
   HISTOGRAM
========================================== */

function updateHistogram(){

    const container = document.getElementById("evHistogram");

    if(!container) return;

    const hours = 12;

    const bars = [];

    for(let i = 0; i < hours; i++){

        const height = Math.floor(Math.random() * 80) + 20;

        const hour = new Date(Date.now() - (hours - 1 - i) * 3600000).getHours();

        const label = `${hour}:00`;

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

function getSeverity(event){

    const e = event.toLowerCase();

    if(e.includes("weapon") || e.includes("critical")) return "critical";

    if(e.includes("fall") || e.includes("perimeter")) return "high";

    if(e.includes("loiter") || e.includes("crowd") || e.includes("vehicle")) return "medium";

    return "low";

}

function getEventLabel(event){

    return event

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

function createEvidenceCard(item, index){

    const card = document.createElement("div");

    card.className = "ev-card";

    card.style.animationDelay = `${Math.min(index * 0.04, 0.5)}s`;

    if(selectedIds.has(item.image)){

        card.classList.add("selected");

    }

    const severity = getSeverity(item.event);

    const confidence = (90 + Math.random() * 9.9).toFixed(1);

    const time = item.time || new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

    card.innerHTML = `

        <div class="ev-card-image">

            <div class="ev-card-placeholder"></div>

            <img src="${item.image}" 

                 alt="${item.event}" 

                 class="ev-card-img"

                 loading="lazy"

                 onload="this.classList.add('loaded')"

                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22%3E%3Crect fill=%22%231a2332%22 width=%22300%22 height=%22200%22/%3E%3Ctext fill=%22%2364748b%22 x=%22150%22 y=%22100%22 text-anchor=%22middle%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'">

            <div class="ev-card-badges">

                <span class="ev-threat-badge ${severity}">

                    ${severity === 'critical' ? '🔴' : severity === 'high' ? '🟠' : severity === 'medium' ? '🟡' : '🟢'}

                    ${severity.toUpperCase()}

                </span>

                <span class="ev-fav-badge ${item.favorite ? 'active' : ''}" 

                     onclick="event.stopPropagation(); toggleFavorite('${item.image}')">

                    ${item.favorite ? '⭐' : '☆'}

                </span>

            </div>

            <div class="ev-card-overlay">

                <button class="ev-overlay-btn" onclick="event.stopPropagation(); openFullscreenFor('${item.image}')" title="Preview">

                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>

                        <circle cx="12" cy="12" r="3"></circle>

                    </svg>

                </button>

                <button class="ev-overlay-btn" onclick="event.stopPropagation(); downloadEvidence('${item.image}')" title="Download">

                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>

                        <polyline points="7 10 12 15 17 10"></polyline>

                        <line x1="12" y1="15" x2="12" y2="3"></line>

                    </svg>

                </button>

                <button class="ev-overlay-btn" onclick="event.stopPropagation(); toggleFavorite('${item.image}')" title="Favorite">

                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">

                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>

                    </svg>

                </button>

            </div>

        </div>

        <div class="ev-card-info">

            <h4 class="ev-card-title">${getEventLabel(item.event)}</h4>

            <div class="ev-card-meta">

                <span><span class="meta-icon">📹</span> ${item.camera || 'Camera 01'}</span>

                <span><span class="meta-icon">📍</span> ${item.location || 'Main Entrance'}</span>

                <span><span class="meta-icon">🕒</span> ${time}</span>

            </div>

            <div class="ev-card-confidence">${confidence}%</div>

        </div>

    `;

    card.onclick = () => selectEvidence(item, card);

    return card;

}

/* ==========================================
   SELECTION & DETAILS
========================================== */

function selectEvidence(item, cardElement){

    selectedEvidence = item;

    document.querySelectorAll(".ev-card").forEach(c => c.classList.remove("selected"));

    if(cardElement){

        cardElement.classList.add("selected");

        cardElement.scrollIntoView({ behavior:"smooth", block:"nearest" });

    }

    const preview = document.getElementById("previewImage");

    preview.src = item.image;

    document.getElementById("summaryEvent").textContent = getEventLabel(item.event);

    const confidence = (90 + Math.random() * 9.9).toFixed(1);

    document.getElementById("summaryConfidence").textContent = confidence + '%';

    document.getElementById("summaryCamera").textContent = item.camera || 'Camera 01';

    document.getElementById("summaryTracking").textContent = '#TX-' + (1000 + Math.floor(Math.random() * 100));

    document.getElementById("summaryThreat").textContent = getSeverity(item.event).toUpperCase();

    document.getElementById("summaryZone").textContent = item.location || 'Main Entrance';

    document.getElementById("summaryTime").textContent = item.time || new Date().toLocaleString();

    // Update confidence ring

    const ring = document.getElementById("confidenceRing");

    const ringValue = document.getElementById("confidenceValue");

    if(ring && ringValue){

        const pct = parseFloat(confidence);

        const color = pct >= 95 ? '#22c55e' : pct >= 85 ? '#f59e0b' : '#ef4444';

        ring.style.background = `conic-gradient(${color} ${pct}%, #1e293b 0)`;

        ringValue.textContent = pct + '%';

    }

    updateDetailsPanel(item);

    updateCameraMap(item);

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
   FAVORITES
========================================== */

function toggleFavorite(imageSrc){

    const item = evidenceData.find(e => e.image === imageSrc);

    if(!item) return;

    item.favorite = !item.favorite;

    const filtered = getCurrentFilteredData();

    renderGallery(filtered);

    updateStats();

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

            item.event.toLowerCase().includes(searchVal) ||

            (item.camera || "").toLowerCase().includes(searchVal) ||

            (item.location || "").toLowerCase().includes(searchVal) ||

            (item.trackingId || "").toLowerCase().includes(searchVal);

        const matchesFilter = currentFilter === 'all' ||

            (currentFilter === 'today' && isToday(item)) ||

            (currentFilter === 'yesterday' && isYesterday(item)) ||

            (currentFilter === 'week' && isThisWeek(item)) ||

            (currentFilter === 'high' && ['high', 'critical'].includes(getSeverity(item.event))) ||

            (currentFilter === 'critical' && getSeverity(item.event) === 'critical') ||

            (currentFilter === 'person' && item.event.toLowerCase().includes('person')) ||

            (currentFilter === 'vehicle' && item.event.toLowerCase().includes('vehicle')) ||

            (currentFilter === 'weapon' && item.event.toLowerCase().includes('weapon')) ||

            (currentFilter === 'crowd' && item.event.toLowerCase().includes('crowd')) ||

            (currentFilter === 'running' && item.event.toLowerCase().includes('running')) ||

            (currentFilter === 'loitering' && item.event.toLowerCase().includes('loiter')) ||

            (currentFilter === 'fall' && item.event.toLowerCase().includes('fall'));

        return matchesSearch && matchesFilter;

    });

}

function isToday(item){

    const d = new Date(item.time || item.date || "");

    return d.toDateString() === new Date().toDateString();

}

function isYesterday(item){

    const d = new Date(item.time || item.date || "");

    const yesterday = new Date();

    yesterday.setDate(yesterday.getDate() - 1);

    return d.toDateString() === yesterday.toDateString();

}

function isThisWeek(item){

    const d = new Date(item.time || item.date || "");

    const now = new Date();

    const weekStart = new Date(now.setDate(now.getDate() - now.getDay()));

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

        const time = item.time || new Date(Date.now() - i * 60000).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

        return `

            <div class="ev-timeline-item">

                <span class="ev-timeline-time">${time}</span>

                <div class="ev-timeline-content">

                    <div class="ev-timeline-title">${getEventLabel(item.event)}</div>

                    <div class="ev-timeline-meta">${item.camera || 'Camera 01'} • ${item.location || 'Main Entrance'}</div>

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

    const a = document.createElement("a");

    a.href = imageSrc;

    a.download = `evidence_${Date.now()}.jpg`;

    a.click();

    showToast("Download", "Evidence downloaded successfully", "success");

}

function exportAll(){

    showToast("Export", "Preparing evidence export...", "info");

}

/* ==========================================
   FULLSCREEN MODAL
========================================== */

function openFullscreen(){

    if(!selectedEvidence) return;

    document.getElementById("fullscreenImage").src = selectedEvidence.image;

    document.getElementById("modalEvent").textContent = getEventLabel(selectedEvidence.event);

    document.getElementById("modalCamera").textContent = selectedEvidence.camera || 'Camera 01';

    document.getElementById("modalTime").textContent = selectedEvidence.time || new Date().toLocaleString();

    const modal = document.getElementById("fullscreenModal");

    modal.style.display = "flex";

    requestAnimationFrame(() => {

        modal.classList.add("show");

    });

    document.body.style.overflow = "hidden";

}

function openFullscreenFor(imageSrc){

    const item = evidenceData.find(e => e.image === imageSrc);

    if(!item) return;

    selectedEvidence = item;

    openFullscreen();

}

function closeFullscreen(){

    const modal = document.getElementById("fullscreenModal");

    modal.classList.remove("show");

    setTimeout(() => {

        modal.style.display = "none";

    }, 350);

    document.body.style.overflow = "";

}

function downloadCurrent(){

    if(!selectedEvidence) return;

    downloadEvidence(selectedEvidence.image);

}

function favoriteCurrent(){

    if(!selectedEvidence) return;

    toggleFavorite(selectedEvidence.image);

}

document.getElementById("fullscreenModal").addEventListener("click", function(e){

    if(e.target === this){

        closeFullscreen();

    }

});

window.addEventListener("keydown", (e) => {

    if(e.key === "Escape"){

        closeFullscreen();

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
   INIT
========================================== */

loadEvidence();
