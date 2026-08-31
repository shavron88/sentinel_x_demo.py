let incidentChart = null;
let donutChart = null;

// Date range and filter state
let dateRange = {
    start: null,
    end: null
};

let activeFilters = {
    eventTypes: [],
    severity: [],
    cameras: []
};

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function formatPercent(value, total) {
    if (!total || total === 0) return "0%";
    return Math.round((value / total) * 100) + "%";
}

function getSeverityClass(severity) {
    const s = (severity || "").toUpperCase();
    if (s === "HIGH" || s === "CRITICAL") return "high";
    if (s === "MEDIUM") return "medium";
    return "low";
}

function getEventCategory(eventType) {
    const e = (eventType || "").toUpperCase();
    if (e.includes("PERSON") || e.includes("LOITERING")) return "Persons";
    if (e.includes("VEHICLE")) return "Vehicles";
    if (e.includes("FALL")) return "Falls";
    if (e.includes("WEAPON")) return "Weapons";
    if (e.includes("CROWD")) return "Crowd";
    if (e.includes("LINE_CROSSING")) return "Line Crossing";
    if (e.includes("ABANDONED")) return "Abandoned Objects";
    return "Other";
}

function getCategoryIcon(category) {
    const icons = {
        "Persons": "<svg viewBox='0 0 24 24'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'></path><circle cx='12' cy='7' r='4'></circle></svg>",
        "Vehicles": "<svg viewBox='0 0 24 24'><rect x='1' y='3' width='15' height='13'></rect><polygon points='16 8 20 8 23 11 23 16 16 16 16 8'></polygon><circle cx='5.5' cy='18.5' r='2.5'></circle><circle cx='18.5' cy='18.5' r='2.5'></circle></svg>",
        "Falls": "<svg viewBox='0 0 24 24'><path d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'></path><line x1='12' y1='9' x2='12' y2='13'></line><line x1='12' y1='17' x2='12.01' y2='17'></line></svg>",
        "Weapons": "<svg viewBox='0 0 24 24'><path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path></svg>",
        "Other": "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='10'></circle><line x1='12' y1='16' x2='12' y2='12'></line><line x1='12' y1='8' x2='12.01' y2='8'></line></svg>"
    };
    return icons[category] || icons["Other"];
}

// ============================
// DATE RANGE PICKER
// ============================
// DROPDOWN BACKDROP (Mobile)
// ============================
function createBackdrop() {
    let backdrop = document.querySelector('.dropdown-backdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.className = 'dropdown-backdrop';
        document.body.appendChild(backdrop);
        
        // Close all dropdowns when backdrop is clicked
        backdrop.addEventListener('click', closeAllDropdowns);
    }
    return backdrop;
}

function closeAllDropdowns() {
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
    });
    const backdrop = document.querySelector('.dropdown-backdrop');
    if (backdrop) backdrop.classList.remove('show');
}

function toggleDropdown(dropdown) {
    const isShown = dropdown.classList.contains('show');
    const backdrop = createBackdrop();
    
    // Close all other dropdowns first
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        if (menu !== dropdown) menu.classList.remove('show');
    });
    
    if (isShown) {
        dropdown.classList.remove('show');
        backdrop.classList.remove('show');
    } else {
        dropdown.classList.add('show');
        backdrop.classList.add('show');
        
        // Position the dropdown correctly for fixed positioning
        positionDropdown(dropdown);
    }
}

function positionDropdown(dropdown) {
    // On mobile, the CSS handles centering - skip JS positioning
    if (window.innerWidth <= 768) {
        dropdown.style.position = 'fixed';
        dropdown.style.top = '50%';
        dropdown.style.left = '50%';
        dropdown.style.right = 'auto';
        dropdown.style.transform = 'translate(-50%, -50%)';
        return;
    }
    
    // Find the corresponding button for this dropdown
    let btn;
    if (dropdown.id === 'date-range-dropdown') {
        btn = document.getElementById('date-range-btn');
    } else if (dropdown.id === 'filter-dropdown') {
        btn = document.getElementById('filter-btn');
    }
    
    if (!btn) return;
    
    const btnRect = btn.getBoundingClientRect();
    const dropdownWidth = 360; // Fixed width for desktop dropdowns
    
    // Calculate position - right-aligned with button
    let left = btnRect.right - dropdownWidth;
    if (left < 16) left = 16; // Don't go off-screen left
    
    let top = btnRect.bottom + 8;
    
    // If dropdown would go off bottom of viewport, show above button
    const dropdownHeight = dropdown.scrollHeight || 400;
    if (top + dropdownHeight > window.innerHeight - 20) {
        top = btnRect.top - dropdownHeight - 8;
        if (top < 16) top = 16; // Don't go off-screen top
    }
    
    dropdown.style.position = 'fixed';
    dropdown.style.top = top + 'px';
    dropdown.style.left = left + 'px';
    dropdown.style.right = 'auto';
    dropdown.style.width = dropdownWidth + 'px';
}

// ============================
// DATE RANGE PICKER
// ============================
function initDateRangePicker() {
    const dateBtn = document.getElementById("date-range-btn");
    const dateDropdown = document.getElementById("date-range-dropdown");
    
    if (!dateBtn || !dateDropdown) return;
    
    // Set default date range (last 7 days)
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);
    dateRange.start = start;
    dateRange.end = end;
    
    updateDateRangeDisplay();
    
    dateBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleDropdown(dateDropdown);
    });
    
    // Close dropdown when clicking outside (desktop only)
    document.addEventListener("click", (e) => {
        if (window.innerWidth > 768) {
            if (!dateBtn.contains(e.target) && !dateDropdown.contains(e.target)) {
                dateDropdown.classList.remove("show");
            }
        }
    });
    
    // Quick select buttons
    dateDropdown.querySelectorAll(".date-quick-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const range = btn.dataset.range;
            const end = new Date();
            const start = new Date();
            
            switch(range) {
                case "today":
                    start.setHours(0, 0, 0, 0);
                    break;
                case "7days":
                    start.setDate(start.getDate() - 7);
                    break;
                case "30days":
                    start.setDate(start.getDate() - 30);
                    break;
                case "90days":
                    start.setDate(start.getDate() - 90);
                    break;
            }
            
            dateRange.start = start;
            dateRange.end = end;
            updateDateRangeDisplay();
            closeAllDropdowns();
            loadAnalytics();
        });
    });
    
    // Custom date range
    const applyBtn = document.getElementById("apply-date-range");
    if (applyBtn) {
        applyBtn.addEventListener("click", () => {
            const startInput = document.getElementById("date-start");
            const endInput = document.getElementById("date-end");
            
            if (startInput && startInput.value) {
                dateRange.start = new Date(startInput.value);
            }
            if (endInput && endInput.value) {
                dateRange.end = new Date(endInput.value);
            }
            
            updateDateRangeDisplay();
            closeAllDropdowns();
            loadAnalytics();
        });
    }
}

function updateDateRangeDisplay() {
    const display = document.getElementById("date-range-display");
    if (!display || !dateRange.start || !dateRange.end) return;
    
    const formatDate = (d) => d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    display.textContent = `${formatDate(dateRange.start)} – ${formatDate(dateRange.end)}`;
}

// ============================
// FILTER SYSTEM
// ============================
function initFilters() {
    const filterBtn = document.getElementById("filter-btn");
    const filterDropdown = document.getElementById("filter-dropdown");
    
    if (!filterBtn || !filterDropdown) return;
    
    filterBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleDropdown(filterDropdown);
        updateFilterOptions();
    });
    
    // Close dropdown when clicking outside (desktop only)
    document.addEventListener("click", (e) => {
        if (window.innerWidth > 768) {
            if (!filterBtn.contains(e.target) && !filterDropdown.contains(e.target)) {
                filterDropdown.classList.remove("show");
            }
        }
    });
    
    // Apply filters button
    const applyBtn = document.getElementById("apply-filters");
    if (applyBtn) {
        applyBtn.addEventListener("click", () => {
            // Collect checked event types
            activeFilters.eventTypes = [];
            filterDropdown.querySelectorAll(".filter-event-type:checked").forEach(cb => {
                activeFilters.eventTypes.push(cb.value);
            });
            
            // Collect checked severity
            activeFilters.severity = [];
            filterDropdown.querySelectorAll(".filter-severity:checked").forEach(cb => {
                activeFilters.severity.push(cb.value);
            });
            
            // Collect checked cameras
            activeFilters.cameras = [];
            filterDropdown.querySelectorAll(".filter-camera:checked").forEach(cb => {
                activeFilters.cameras.push(cb.value);
            });
            
            updateFilterBadge();
            closeAllDropdowns();
            loadAnalytics();
        });
    }
    
    // Clear filters button
    const clearBtn = document.getElementById("clear-filters");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            filterDropdown.querySelectorAll("input[type='checkbox']").forEach(cb => {
                cb.checked = false;
            });
            activeFilters = { eventTypes: [], severity: [], cameras: [] };
            updateFilterBadge();
            closeAllDropdowns();
            loadAnalytics();
        });
    }
}

function updateFilterOptions() {
    // This will be populated with available options from the data
    const eventTypeContainer = document.getElementById("filter-event-types");
    const severityContainer = document.getElementById("filter-severity");
    const cameraContainer = document.getElementById("filter-cameras");
    
    if (eventTypeContainer && window._availableEventTypes) {
        eventTypeContainer.innerHTML = window._availableEventTypes.map(type => `
            <label class="filter-option">
                <input type="checkbox" class="filter-event-type" value="${escapeHtml(type)}" ${activeFilters.eventTypes.includes(type) ? "checked" : ""}>
                <span>${escapeHtml(type)}</span>
            </label>
        `).join("");
    }
    
    if (severityContainer) {
        const severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
        severityContainer.innerHTML = severities.map(sev => `
            <label class="filter-option">
                <input type="checkbox" class="filter-severity" value="${sev}" ${activeFilters.severity.includes(sev) ? "checked" : ""}>
                <span class="severity-badge ${sev.toLowerCase()}">${sev}</span>
            </label>
        `).join("");
    }
    
    if (cameraContainer && window._availableCameras) {
        cameraContainer.innerHTML = window._availableCameras.map(cam => `
            <label class="filter-option">
                <input type="checkbox" class="filter-camera" value="${escapeHtml(cam)}" ${activeFilters.cameras.includes(cam) ? "checked" : ""}>
                <span>${escapeHtml(cam)}</span>
            </label>
        `).join("");
    }
}

function updateFilterBadge() {
    const badge = document.getElementById("filter-badge");
    const totalFilters = activeFilters.eventTypes.length + activeFilters.severity.length + activeFilters.cameras.length;
    
    if (badge) {
        if (totalFilters > 0) {
            badge.textContent = totalFilters;
            badge.style.display = "inline";
        } else {
            badge.style.display = "none";
        }
    }
}

// ============================
// DATA FETCHING WITH FILTERS
// ============================
async function fetchAnalyticsData() {
    const params = new URLSearchParams();
    
    if (dateRange.start) {
        params.set("start_date", dateRange.start.toISOString().split("T")[0]);
    }
    if (dateRange.end) {
        params.set("end_date", dateRange.end.toISOString().split("T")[0]);
    }
    
    if (activeFilters.eventTypes.length > 0) {
        params.set("event_types", activeFilters.eventTypes.join(","));
    }
    if (activeFilters.severity.length > 0) {
        params.set("severity", activeFilters.severity.join(","));
    }
    if (activeFilters.cameras.length > 0) {
        params.set("cameras", activeFilters.cameras.join(","));
    }
    
    const response = await fetch(`/analytics_data?${params.toString()}`);
    if (!response.ok) throw new Error("Failed to fetch analytics data");
    return response.json();
}

async function fetchEvents() {
    const params = new URLSearchParams();
    params.set("limit", "500");
    
    if (dateRange.start) {
        params.set("start_date", dateRange.start.toISOString().split("T")[0]);
    }
    if (dateRange.end) {
        params.set("end_date", dateRange.end.toISOString().split("T")[0]);
    }
    
    const response = await fetch(`/events?${params.toString()}`);
    if (!response.ok) throw new Error("Failed to fetch events");
    return response.json();
}

// ============================
// MAIN LOAD FUNCTION
// ============================
async function loadAnalytics() {
    try {
        const [stats, events] = await Promise.all([
            fetchAnalyticsData(),
            fetchEvents()
        ]);
        
        // Store available filter options
        window._availableEventTypes = [...new Set(events.map(e => e.event_type).filter(Boolean))];
        window._availableCameras = [...new Set(events.map(e => e.camera).filter(Boolean))];
        
        // Apply client-side filters
        let filteredEvents = events;
        if (activeFilters.eventTypes.length > 0) {
            filteredEvents = filteredEvents.filter(e => activeFilters.eventTypes.includes(e.event_type));
        }
        if (activeFilters.severity.length > 0) {
            filteredEvents = filteredEvents.filter(e => activeFilters.severity.includes((e.severity || "LOW").toUpperCase()));
        }
        if (activeFilters.cameras.length > 0) {
            filteredEvents = filteredEvents.filter(e => activeFilters.cameras.includes(e.camera));
        }
        
        renderKPIs(stats, filteredEvents);
        renderTrendChart(filteredEvents);
        renderDonutChart(stats, filteredEvents);
        renderDetectionSummary(stats, filteredEvents);
        renderZones(filteredEvents);
        renderHeatmap(filteredEvents);
        renderTimeline(filteredEvents);
        
    } catch(e) {
        console.error("Analytics load error:", e);
        showEmptyState();
    }
}

function showEmptyState() {
    const containers = ["total-incidents", "people-count", "vehicle-count"];
    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = "0";
    });
    
    const chartContainers = ["incidentChart", "donutChart"];
    chartContainers.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas) {
            const parent = canvas.parentElement;
            parent.innerHTML = `<div class="empty-state-message">
                <svg viewBox="0 0 24 24" width="48" height="48"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
                <p>No data available for the selected period</p>
            </div>`;
        }
    });
    
    const listContainers = ["detection-summary", "zones-list", "heatmap-container", "timeline-list"];
    listContainers.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `<div class="empty-state-message">
                <svg viewBox="0 0 24 24" width="48" height="48"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>
                <p>No events found for the selected filters</p>
            </div>`;
        }
    });
}

// ============================
// RENDER FUNCTIONS (with real data)
// ============================
function renderKPIs(stats, events) {
    const totalEl = document.getElementById("total-incidents");
    const peopleEl = document.getElementById("people-count");
    const vehiclesEl = document.getElementById("vehicle-count");
    const threatEl = document.getElementById("analytics-threat");
    
    const total = events.length || stats.total || 0;
    const people = events.filter(e => (e.event_type || "").toLowerCase().includes("person")).length || stats.people || 0;
    const vehicles = events.filter(e => (e.event_type || "").toLowerCase().includes("vehicle")).length || stats.vehicles || 0;
    
    if (totalEl) totalEl.innerText = total;
    if (peopleEl) peopleEl.innerText = people;
    if (vehiclesEl) vehiclesEl.innerText = vehicles;
    
    if (threatEl) {
        const threat = (stats.threat || "LOW").toUpperCase();
        threatEl.innerText = threat;
        const threatStatus = document.getElementById("threat-status");
        if (threatStatus) {
            if (threat === "CRITICAL") {
                threatStatus.innerHTML = "<span style='color:#f87171;'>High Risk Environment</span>";
            } else if (threat === "MEDIUM") {
                threatStatus.innerHTML = "<span style='color:#fbbf24;'>Elevated Risk</span>";
            } else {
                threatStatus.innerHTML = "<span style='color:#4ade80;'>Normal Operations</span>";
            }
        }
    }
    
    // Calculate trends (compare with previous period)
    const incidentsTrend = document.getElementById("incidents-trend");
    const peopleTrend = document.getElementById("people-trend");
    const vehiclesTrend = document.getElementById("vehicles-trend");
    
    if (incidentsTrend) incidentsTrend.innerText = "vs previous period";
    if (peopleTrend) peopleTrend.innerText = "vs previous period";
    if (vehiclesTrend) vehiclesTrend.innerText = "vs previous period";
}

function renderTrendChart(events) {
    const ctx = document.getElementById("incidentChart");
    if (!ctx) return;
    
    if (incidentChart) {
        incidentChart.destroy();
        incidentChart = null;
    }
    
    let labels, values;
    
    if (Array.isArray(events) && events.length > 0) {
        // Derive daily trend from real events
        const dailyMap = {};
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const d = new Date(today);
            d.setDate(d.getDate() - i);
            const key = d.toISOString().split("T")[0];
            dailyMap[key] = 0;
        }
        events.forEach(e => {
            if (e.timestamp) {
                const day = e.timestamp.split(" ")[0];
                if (dailyMap.hasOwnProperty(day)) dailyMap[day]++;
            }
        });
        labels = Object.keys(dailyMap).map(d => {
            const date = new Date(d + "T00:00:00");
            return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
        });
        values = Object.values(dailyMap);
    } else {
        labels = [];
        values = [];
    }
    
    const t = (typeof getChartTheme === 'function') ? getChartTheme() : {
        tooltipBg:'rgba(15,23,42,0.92)', tooltipBorder:'rgba(120,150,190,0.2)',
        tooltipTitle:'#e2e8f0', tooltipBody:'#b8c4d5', gridColor:'rgba(120,150,190,0.06)',
        tickColor:'#64748b', pointBorder:'#0f172a'
    };
    
    incidentChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Incidents",
                data: values,
                borderColor: "#3b82f6",
                backgroundColor: "rgba(59, 130, 246, 0.08)",
                borderWidth: 2.5,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: "#3b82f6",
                pointBorderColor: t.pointBorder,
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: "index" },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: t.tooltipBg,
                    titleColor: t.tooltipTitle,
                    bodyColor: t.tooltipBody,
                    borderColor: t.tooltipBorder,
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: { color: t.gridColor, drawBorder: false },
                    ticks: { color: t.tickColor, font: { size: 11, family: "Inter, system-ui, sans-serif" } }
                },
                y: {
                    grid: { color: t.gridColor, drawBorder: false },
                    ticks: { color: t.tickColor, font: { size: 11, family: "Inter, system-ui, sans-serif" }, stepSize: 1 },
                    beginAtZero: true
                }
            }
        }
    });
    
    window.incidentChart = incidentChart;
}

function renderDonutChart(stats, events) {
    const ctx = document.getElementById("donutChart");
    const legendEl = document.getElementById("donut-legend");
    if (!ctx || !legendEl) return;
    
    if (donutChart) {
        donutChart.destroy();
        donutChart = null;
    }
    
    let categories;
    
    if (Array.isArray(events) && events.length > 0) {
        // Derive categories from real events
        const categoryCounts = {};
        events.forEach(e => {
            const cat = getEventCategory(e.event_type);
            categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });
        const colors = ["#3b82f6", "#f59e0b", "#eab308", "#ef4444", "#a855f7", "#ec4899"];
        categories = Object.entries(categoryCounts).map(([name, value], i) => ({
            name, value, color: colors[i % colors.length]
        }));
    } else if (stats && stats.labels) {
        const colors = ["#3b82f6", "#f59e0b", "#eab308", "#ef4444", "#a855f7", "#ec4899"];
        categories = stats.labels.map((label, i) => ({
            name: label,
            value: stats.values[i] || 0,
            color: colors[i % colors.length]
        }));
    } else {
        categories = [];
    }
    
    const total = categories.reduce((sum, c) => sum + c.value, 0);
    
    const dt = (typeof getChartTheme === 'function') ? getChartTheme() : {
        tooltipBg:'rgba(15,23,42,0.92)', tooltipBorder:'rgba(120,150,190,0.2)',
        tooltipTitle:'#e2e8f0', tooltipBody:'#b8c4d5', centerText:'#e2e8f0',
        centerLabel:'#64748b', donutBorder:'rgba(10,17,32,0.8)'
    };
    
    donutChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: categories.map(c => c.name),
            datasets: [{
                data: categories.map(c => c.value),
                backgroundColor: categories.map(c => c.color),
                borderColor: dt.donutBorder,
                borderWidth: 3,
                hoverBorderColor: dt.donutBorder,
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: "68%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: dt.tooltipBg,
                    titleColor: dt.tooltipTitle,
                    bodyColor: dt.tooltipBody,
                    borderColor: dt.tooltipBorder,
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 10
                }
            }
        },
        plugins: [{
            id: "centerText",
            beforeDraw(chart) {
                const { width, height, ctx: c } = chart;
                c.save();
                c.font = "700 28px Inter, system-ui, sans-serif";
                c.fillStyle = dt.centerText;
                c.textAlign = "center";
                c.textBaseline = "middle";
                c.fillText(total, width / 2, height / 2 - 6);
                c.font = "500 11px Inter, system-ui, sans-serif";
                c.fillStyle = dt.centerLabel;
                c.fillText("Total Incidents", width / 2, height / 2 + 16);
                c.restore();
            }
        }]
    });
    
    window.donutChart = donutChart;
    
    // Render legend
    if (categories.length === 0) {
        legendEl.innerHTML = `<div class="empty-state-message small"><p>No data</p></div>`;
    } else {
        legendEl.innerHTML = categories.map(c => `
            <div class="analytics-legend-item">
                <div class="analytics-legend-left">
                    <span class="analytics-legend-dot" style="background:${c.color};"></span>
                    <span class="analytics-legend-label">${escapeHtml(c.name)}</span>
                </div>
                <span class="analytics-legend-value">${c.value}</span>
                <span class="analytics-legend-percent">${formatPercent(c.value, total)}</span>
            </div>
        `).join("");
    }
}

function renderDetectionSummary(stats, events) {
    const container = document.getElementById("detection-summary");
    if (!container) return;
    
    let items = [];
    
    if (Array.isArray(events) && events.length > 0) {
        // Derive from real events
        const categoryCounts = {};
        events.forEach(e => {
            const cat = getEventCategory(e.event_type);
            categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });
        items = Object.entries(categoryCounts).map(([label, value]) => ({
            label, value, icon: getCategoryIcon(label), trend: "", trendClass: ""
        }));
    } else if (stats) {
        items = [
            { label: "Persons", value: stats.people || 0, icon: getCategoryIcon("Persons"), trend: "", trendClass: "" },
            { label: "Vehicles", value: stats.vehicles || 0, icon: getCategoryIcon("Vehicles"), trend: "", trendClass: "" },
            { label: "Falls", value: stats.falls || 0, icon: getCategoryIcon("Falls"), trend: "", trendClass: "" },
            { label: "Weapons", value: stats.weapons || 0, icon: getCategoryIcon("Weapons"), trend: "", trendClass: "" }
        ];
    }
    
    if (items.length === 0) {
        container.innerHTML = `<div class="empty-state-message small"><p>No detections</p></div>`;
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="detection-item">
            <div class="detection-item-icon">${item.icon}</div>
            <div class="detection-item-content">
                <span class="detection-item-label">${escapeHtml(item.label)}</span>
                <span class="detection-item-value">${item.value}</span>
                ${item.trend ? `<span class="detection-item-trend ${item.trendClass}">${item.trend}</span>` : ""}
            </div>
        </div>
    `).join("");
}

function renderZones(events) {
    const container = document.getElementById("zones-list");
    if (!container) return;
    
    let zones = [];
    
    if (Array.isArray(events) && events.length > 0) {
        const zoneCounts = {};
        events.forEach(e => {
            const zone = e.zone || e.camera || "Unknown";
            zoneCounts[zone] = (zoneCounts[zone] || 0) + 1;
        });
        const sorted = Object.entries(zoneCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
        const colors = ["#3b82f6", "#a855f7", "#ec4899", "#f59e0b", "#eab308"];
        zones = sorted.map(([name, count], i) => ({
            name, count, color: colors[i % colors.length]
        }));
    }
    
    const maxCount = zones.length > 0 ? Math.max(...zones.map(z => z.count)) : 1;
    
    if (zones.length === 0) {
        container.innerHTML = `<div class="empty-state-message small"><p>No zone data available</p></div>`;
        return;
    }
    
    container.innerHTML = zones.map(zone => {
        const pct = (zone.count / maxCount) * 100;
        return `
        <div class="zone-item">
            <div class="zone-item-header">
                <span class="zone-item-name">${escapeHtml(zone.name)}</span>
                <span class="zone-item-count">${zone.count}</span>
            </div>
            <div class="zone-bar-bg">
                <div class="zone-bar-fill" style="width:${pct}%;background:${zone.color};box-shadow:0 0 8px ${zone.color}33;"></div>
            </div>
        </div>
        `;
    }).join("");
}

function renderHeatmap(events) {
    const container = document.getElementById("heatmap-container");
    if (!container) return;
    
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const hours = Array.from({length: 24}, (_, i) => i);
    
    let heatmapGrid;
    
    if (Array.isArray(events) && events.length > 0) {
        heatmapGrid = Array.from({length: 7}, () => Array(24).fill(0));
        events.forEach(e => {
            if (e.timestamp) {
                const dt = new Date(e.timestamp);
                const dayIndex = (dt.getDay() + 6) % 7;
                const hourIndex = dt.getHours();
                if (dayIndex < 7 && hourIndex < 24) {
                    heatmapGrid[dayIndex][hourIndex]++;
                }
            }
        });
    } else {
        heatmapGrid = Array.from({length: 7}, () => Array(24).fill(0));
    }
    
    const maxVal = Math.max(1, ...heatmapGrid.flat());
    
    function heatColor(value) {
        const ratio = value / maxVal;
        if (ratio === 0) return "rgba(59, 130, 246, 0.03)";
        if (ratio < 0.15) return "rgba(59, 130, 246, 0.12)";
        if (ratio < 0.3) return "rgba(59, 130, 246, 0.25)";
        if (ratio < 0.5) return "rgba(99, 102, 241, 0.4)";
        if (ratio < 0.7) return "rgba(168, 85, 247, 0.5)";
        if (ratio < 0.85) return "rgba(236, 72, 153, 0.6)";
        return "rgba(239, 68, 68, 0.75)";
    }
    
    let html = '<div class="heatmap-grid-full">';
    
    // Header row — hours
    html += '<div class="heatmap-corner"></div>';
    hours.forEach(h => {
        html += `<div class="heatmap-header-cell">${h.toString().padStart(2, "0")}</div>`;
    });
    
    // Data rows
    days.forEach((day, di) => {
        html += `<div class="heatmap-day-label">${day}</div>`;
        hours.forEach(h => {
            const val = (heatmapGrid[di] && heatmapGrid[di][h]) || 0;
            html += `<div class="heatmap-cell" style="background:${heatColor(val)};" title="${day} ${h.toString().padStart(2,'0')}:00 — ${val} events"></div>`;
        });
    });
    
    html += "</div>";
    
    html += `
    <div class="heatmap-legend">
        <span>Low Activity</span>
        <div class="heatmap-legend-bar"></div>
        <span>High Activity</span>
    </div>
    `;
    
    container.innerHTML = html;
}

function renderTimeline(events) {
    const container = document.getElementById("timeline-list");
    if (!container) return;
    
    let items = [];
    
    if (Array.isArray(events) && events.length > 0) {
        items = events.slice(0, 10).map(e => {
            const time = e.timestamp ? new Date(e.timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "--:--:--";
            const category = getEventCategory(e.event_type);
            return {
                time,
                type: (e.event_type || "EVENT").toUpperCase(),
                desc: `${category} detected at ${e.zone || "Unknown"}`,
                severity: e.severity || "LOW",
                camera: e.camera || "Camera_01",
                zone: e.zone || "Unknown"
            };
        });
    }
    
    if (items.length === 0) {
        container.innerHTML = `<div class="empty-state-message small">
            <svg viewBox="0 0 24 24" width="48" height="48"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <p>No recent activity</p>
        </div>`;
        return;
    }
    
    container.innerHTML = items.map(e => {
        const sevClass = getSeverityClass(e.severity);
        const dotColor = sevClass === "high" ? "#ef4444" : sevClass === "medium" ? "#a855f7" : "#3b82f6";
        const badgeClass = sevClass;
        return `
        <div class="analytics-timeline-item">
            <div class="analytics-timeline-dot" style="background:${dotColor};box-shadow:0 0 8px ${dotColor}66;"></div>
            <div class="analytics-timeline-content">
                <div class="analytics-timeline-top">
                    <span class="analytics-timeline-time">${escapeHtml(e.time)}</span>
                    <span class="analytics-timeline-badge ${badgeClass}">${escapeHtml(e.type)}</span>
                </div>
                <div class="analytics-timeline-desc">${escapeHtml(e.desc)}</div>
                <div class="analytics-timeline-meta">
                    <span>
                        <svg viewBox="0 0 24 24"><path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'></path><circle cx="12" cy="13" r="4"></circle></svg>
                        ${escapeHtml(e.camera)}
                    </span>
                    <span>
                        <svg viewBox="0 0 24 24"><path d='M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z'></path><circle cx="12" cy="10" r="3"></circle></svg>
                        ${escapeHtml(e.zone)}
                    </span>
                </div>
            </div>
        </div>
        `;
    }).join("");
}

// Cleanup
function cleanupAnalytics() {
    if (window._analyticsInterval) {
        clearInterval(window._analyticsInterval);
        window._analyticsInterval = null;
    }
    if (incidentChart) {
        incidentChart.destroy();
        incidentChart = null;
    }
    if (donutChart) {
        donutChart.destroy();
        donutChart = null;
    }
}

window.addEventListener("beforeunload", cleanupAnalytics);

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    initDateRangePicker();
    initFilters();
    loadAnalytics();
    
    // Close dropdowns on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeAllDropdowns();
        }
    });
});

// Watch for theme changes and re-apply chart colors for analytics charts
if (typeof refreshChartsOnThemeChange === 'function') refreshChartsOnThemeChange();

window._analyticsInterval = setInterval(loadAnalytics, 30000);
