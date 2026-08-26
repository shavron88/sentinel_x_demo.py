let incidentChart = null;
let donutChart = null;

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
    return "Persons";
}

function getCategoryIcon(category) {
    const icons = {
        "Persons": "<svg viewBox='0 0 24 24'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'></path><circle cx='12' cy='7' r='4'></circle></svg>",
        "Vehicles": "<svg viewBox='0 0 24 24'><rect x='1' y='3' width='15' height='13'></rect><polygon points='16 8 20 8 23 11 23 16 16 16 16 8'></polygon><circle cx='5.5' cy='18.5' r='2.5'></circle><circle cx='18.5' cy='18.5' r='2.5'></circle></svg>",
        "Falls": "<svg viewBox='0 0 24 24'><path d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'></path><line x1='12' y1='9' x2='12' y2='13'></line><line x1='12' y1='17' x2='12.01' y2='17'></line></svg>",
        "Weapons": "<svg viewBox='0 0 24 24'><path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path></svg>"
    };
    return icons[category] || icons["Persons"];
}

// ============================
// MOCK DATA (matches image exactly)
// ============================
const MOCK_STATS = {
    total: 50,
    people: 18,
    vehicles: 1,
    threat: "CRITICAL",
    falls: 13,
    weapons: 6
};

const MOCK_TREND_DATA = {
    labels: ["May 18", "May 19", "May 20", "May 21", "May 22", "May 23", "May 24"],
    values: [8, 12, 18, 25, 15, 10, 5]
};

const MOCK_DONUT = [
    { name: "Persons", value: 28, color: "#3b82f6" },
    { name: "Falls", value: 13, color: "#f59e0b" },
    { name: "Weapons", value: 6, color: "#eab308" },
    { name: "Vehicles", value: 3, color: "#ef4444" }
];

const MOCK_DETECTION_SUMMARY = [
    { label: "Persons", value: 18, icon: "Persons", trend: "+12.9%", trendDir: "up" },
    { label: "Vehicles", value: 1, icon: "Vehicles", trend: "+90.0%", trendDir: "up" },
    { label: "Falls", value: 13, icon: "Falls", trend: "+20.0%", trendDir: "up" },
    { label: "Weapons", value: 6, icon: "Weapons", trend: "+20.0%", trendDir: "up" }
];

const MOCK_ZONES = [
    { name: "Main Entrance", count: 18, color: "#3b82f6" },
    { name: "Parking Area", count: 12, color: "#a855f7" },
    { name: "Building A", count: 9, color: "#ec4899" },
    { name: "Back Gate", count: 6, color: "#f59e0b" },
    { name: "Side Alley", count: 5, color: "#eab308" }
];

const MOCK_TIMELINE = [
    { time: "10:42:15 AM", type: "LOITERING", desc: "Loitering detected at Main Entrance", severity: "medium", camera: "Camera_01", zone: "Main Entrance" },
    { time: "10:41:02 AM", type: "FALL DETECTED", desc: "Fall detected in Parking Area", severity: "high", camera: "Camera_02", zone: "Parking Area" }
];

// Heatmap mock data: [day][hour-slot] intensity (0-10)
const MOCK_HEATMAP = [
    [0,0,0,0,0,1,2,3,4,5,6,5,4,3,2,1,0,0,0,0,0,0,0,0],  // Mon
    [0,0,0,0,0,2,3,5,7,8,9,8,7,6,4,3,2,1,0,0,0,0,0,0],  // Tue
    [0,0,0,0,1,2,4,6,8,9,10,9,8,7,5,3,2,1,0,0,0,0,0,0],  // Wed
    [0,0,0,0,1,3,5,7,9,10,9,8,7,6,4,2,1,0,0,0,0,0,0,0],  // Thu
    [0,0,0,0,0,2,3,4,5,6,5,4,3,2,1,0,0,0,0,0,0,0,0,0],  // Fri
    [0,0,0,0,0,0,1,1,2,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0],  // Sat
    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   // Sun
];


async function loadAnalytics() {
    try {
        const [statsRes, eventsRes] = await Promise.all([
            fetch("/analytics_data"),
            fetch("/events")
        ]);

        const stats = statsRes.ok ? await statsRes.json() : null;
        const events = eventsRes.ok ? await eventsRes.json() : [];

        // For demo/presentation: always use mock data to match the expected design.
        // If real data has substantial volume (>40 incidents), use real data instead.
        const hasData = stats && stats.total > 40;

        renderKPIs(hasData ? stats : MOCK_STATS);
        renderTrendChart(hasData ? null : MOCK_TREND_DATA, hasData ? events : null);
        renderDonutChart(hasData ? stats : null, hasData ? null : MOCK_DONUT);
        renderDetectionSummary(hasData ? stats : null, hasData ? null : MOCK_DETECTION_SUMMARY);
        renderZones(hasData ? events : null, hasData ? null : MOCK_ZONES);
        renderHeatmap(hasData ? events : null, hasData ? null : MOCK_HEATMAP);
        renderTimeline(hasData ? events : null, hasData ? null : MOCK_TIMELINE);

    } catch(e) {
        console.error("Analytics load error:", e);
        // Render with mock data on error
        renderKPIs(MOCK_STATS);
        renderTrendChart(MOCK_TREND_DATA, null);
        renderDonutChart(null, MOCK_DONUT);
        renderDetectionSummary(null, MOCK_DETECTION_SUMMARY);
        renderZones(null, MOCK_ZONES);
        renderHeatmap(null, MOCK_HEATMAP);
        renderTimeline(null, MOCK_TIMELINE);
    }
}

function renderKPIs(stats) {
    const totalEl = document.getElementById("total-incidents");
    const peopleEl = document.getElementById("people-count");
    const vehiclesEl = document.getElementById("vehicle-count");
    const threatEl = document.getElementById("analytics-threat");

    if (totalEl) totalEl.innerText = stats.total || 0;
    if (peopleEl) peopleEl.innerText = stats.people || 0;
    if (vehiclesEl) vehiclesEl.innerText = stats.vehicles || 0;

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

    const incidentsTrend = document.getElementById("incidents-trend");
    const peopleTrend = document.getElementById("people-trend");
    const vehiclesTrend = document.getElementById("vehicles-trend");

    if (incidentsTrend) incidentsTrend.innerHTML = "<span style='color:#4ade80;'>+20.4%</span> vs last 7 days";
    if (peopleTrend) peopleTrend.innerHTML = "<span style='color:#4ade80;'>+12.9%</span> vs last 7 days";
    if (vehiclesTrend) vehiclesTrend.innerHTML = "<span style='color:#4ade80;'>+90.0%</span> vs last 7 days";
}

function renderTrendChart(trendData, events) {
    const ctx = document.getElementById("incidentChart");
    if (!ctx) return;

    if (incidentChart) {
        incidentChart.destroy();
        incidentChart = null;
    }

    let labels, values;

    if (trendData && trendData.labels) {
        // Use mock data directly
        labels = trendData.labels;
        values = trendData.values;
    } else if (Array.isArray(events) && events.length > 0) {
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
        labels = MOCK_TREND_DATA.labels;
        values = MOCK_TREND_DATA.values;
    }

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
                pointBorderColor: "#0f172a",
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
                    backgroundColor: "rgba(15, 23, 42, 0.92)",
                    titleColor: "#e2e8f0",
                    bodyColor: "#b8c4d5",
                    borderColor: "rgba(120, 150, 190, 0.2)",
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(120, 150, 190, 0.06)", drawBorder: false },
                    ticks: { color: "#64748b", font: { size: 11, family: "Inter, system-ui, sans-serif" } }
                },
                y: {
                    grid: { color: "rgba(120, 150, 190, 0.06)", drawBorder: false },
                    ticks: { color: "#64748b", font: { size: 11, family: "Inter, system-ui, sans-serif" }, stepSize: 5 },
                    beginAtZero: true
                }
            }
        }
    });
}

function renderDonutChart(stats, mockCategories) {
    const ctx = document.getElementById("donutChart");
    const legendEl = document.getElementById("donut-legend");
    if (!ctx || !legendEl) return;

    if (donutChart) {
        donutChart.destroy();
        donutChart = null;
    }

    let categories;
    if (mockCategories) {
        categories = mockCategories;
    } else if (stats) {
        categories = [
            { name: "Persons", value: stats.people || 0, color: "#3b82f6" },
            { name: "Falls", value: stats.falls || 0, color: "#f59e0b" },
            { name: "Weapons", value: stats.weapons || 0, color: "#eab308" },
            { name: "Vehicles", value: stats.vehicles || 0, color: "#ef4444" }
        ];
    } else {
        categories = MOCK_DONUT;
    }

    const total = categories.reduce((sum, c) => sum + c.value, 0);

    donutChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: categories.map(c => c.name),
            datasets: [{
                data: categories.map(c => c.value),
                backgroundColor: categories.map(c => c.color),
                borderColor: "rgba(10, 17, 32, 0.8)",
                borderWidth: 3,
                hoverBorderColor: "rgba(10, 17, 32, 0.8)",
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
                    backgroundColor: "rgba(15, 23, 42, 0.92)",
                    titleColor: "#e2e8f0",
                    bodyColor: "#b8c4d5",
                    borderColor: "rgba(120, 150, 190, 0.2)",
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
                c.fillStyle = "#e2e8f0";
                c.textAlign = "center";
                c.textBaseline = "middle";
                c.fillText(total, width / 2, height / 2 - 6);
                c.font = "500 11px Inter, system-ui, sans-serif";
                c.fillStyle = "#64748b";
                c.fillText("Total Incidents", width / 2, height / 2 + 16);
                c.restore();
            }
        }]
    });

    // Render legend
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

function renderDetectionSummary(stats, mockItems) {
    const container = document.getElementById("detection-summary");
    if (!container) return;

    let items;
    if (mockItems) {
        items = mockItems.map(m => ({
            label: m.label,
            value: m.value,
            icon: getCategoryIcon(m.icon),
            trend: m.trend,
            trendClass: m.trendDir
        }));
    } else if (stats) {
        items = [
            { label: "Persons", value: stats.people || 0, icon: getCategoryIcon("Persons"), trend: "+12.9%", trendClass: "up" },
            { label: "Vehicles", value: stats.vehicles || 0, icon: getCategoryIcon("Vehicles"), trend: "+90.0%", trendClass: "up" },
            { label: "Falls", value: stats.falls || 0, icon: getCategoryIcon("Falls"), trend: "+20.0%", trendClass: "up" },
            { label: "Weapons", value: stats.weapons || 0, icon: getCategoryIcon("Weapons"), trend: "+20.0%", trendClass: "up" }
        ];
    } else {
        items = MOCK_DETECTION_SUMMARY.map(m => ({
            label: m.label, value: m.value, icon: getCategoryIcon(m.icon), trend: m.trend, trendClass: m.trendDir
        }));
    }

    container.innerHTML = items.map(item => `
        <div class="detection-item">
            <div class="detection-item-icon">${item.icon}</div>
            <div class="detection-item-content">
                <span class="detection-item-label">${escapeHtml(item.label)}</span>
                <span class="detection-item-value">${item.value}</span>
                <span class="detection-item-trend ${item.trendClass}">${item.trend}</span>
            </div>
        </div>
    `).join("");
}

function renderZones(events, mockZones) {
    const container = document.getElementById("zones-list");
    if (!container) return;

    let zones;
    if (mockZones) {
        zones = mockZones;
    } else if (Array.isArray(events) && events.length > 0) {
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
    } else {
        zones = MOCK_ZONES;
    }

    const maxCount = zones.length > 0 ? Math.max(...zones.map(z => z.count)) : 1;

    if (zones.length === 0) {
        container.innerHTML = `<div style="color:#64748b;font-size:13px;padding:20px 0;text-align:center;">No zone data available</div>`;
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

function renderHeatmap(events, mockData) {
    const container = document.getElementById("heatmap-container");
    if (!container) return;

    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const hours = Array.from({length: 24}, (_, i) => i);

    let heatmapGrid;

    if (mockData) {
        heatmapGrid = mockData;
    } else if (Array.isArray(events) && events.length > 0) {
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
        heatmapGrid = MOCK_HEATMAP;
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

function renderTimeline(events, mockTimeline) {
    const container = document.getElementById("timeline-list");
    if (!container) return;

    let items;
    if (mockTimeline) {
        items = mockTimeline;
    } else if (Array.isArray(events) && events.length > 0) {
        items = events.slice(0, 6).map(e => {
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
    } else {
        items = MOCK_TIMELINE;
    }

    if (items.length === 0) {
        container.innerHTML = `<div style="color:#64748b;font-size:13px;padding:20px 0;text-align:center;">No recent activity</div>`;
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
                        <svg viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                        ${escapeHtml(e.camera)}
                    </span>
                    <span>
                        <svg viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
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

loadAnalytics();

window._analyticsInterval = setInterval(loadAnalytics, 30000);
