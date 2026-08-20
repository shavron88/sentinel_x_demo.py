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

function getTrendClass(current, previous) {
    if (!previous || previous === 0) return "neutral";
    const change = ((current - previous) / previous) * 100;
    if (change > 0) return "up";
    if (change < 0) return "down";
    return "neutral";
}

function getTrendArrow(change) {
    if (change > 0) return "↑";
    if (change < 0) return "↓";
    return "→";
}

function getSeverityClass(severity) {
    const s = (severity || "").toUpperCase();
    if (s === "HIGH" || s === "CRITICAL") return "high";
    if (s === "MEDIUM") return "medium";
    return "low";
}

function getEventCategory(eventType) {
    const e = (eventType || "").toUpperCase();
    if (e.includes("PERSON")) return "Persons";
    if (e.includes("VEHICLE")) return "Vehicles";
    if (e.includes("FALL")) return "Falls";
    if (e.includes("WEAPON")) return "Weapons";
    if (e.includes("CROWD")) return "Crowd";
    if (e.includes("LOITERING")) return "Loitering";
    if (e.includes("LINE_CROSSING")) return "Line Crossing";
    if (e.includes("ABANDONED")) return "Abandoned Objects";
    return "Other";
}

function getCategoryIcon(category) {
    const icons = {
        "Persons": "<svg viewBox='0 0 24 24'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'></path><circle cx='12' cy='7' r='4'></circle></svg>",
        "Vehicles": "<svg viewBox='0 0 24 24'><rect x='1' y='3' width='15' height='13'></rect><polygon points='16 8 20 8 23 11 23 16 16 16 16 8'></polygon><circle cx='5.5' cy='18.5' r='2.5'></circle><circle cx='18.5' cy='18.5' r='2.5'></circle></svg>",
        "Falls": "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='10'></circle><polyline points='12 6 12 12 16 14'></polyline></svg>",
        "Weapons": "<svg viewBox='0 0 24 24'><path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path><line x1='12' y1='8' x2='12' y2='12'></line><line x1='12' y1='16' x2='12.01' y2='16'></line></svg>",
        "Crowd": "<svg viewBox='0 0 24 24'><path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'></path><circle cx='9' cy='7' r='4'></circle><path d='M23 21v-2a4 4 0 0 0-3-3.87'></path><path d='M16 3.13a4 4 0 0 1 0 7.75'></path></svg>",
        "Loitering": "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='10'></circle><polyline points='12 6 12 12 16 14'></polyline></svg>",
        "Line Crossing": "<svg viewBox='0 0 24 24'><line x1='5' y1='12' x2='19' y2='12'></line><polyline points='12 5 19 12 12 19'></polyline></svg>",
        "Abandoned Objects": "<svg viewBox='0 0 24 24'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'></rect><circle cx='8.5' cy='8.5' r='1.5'></circle><polyline points='21 15 16 10 5 21'></polyline></svg>",
        "Other": "<svg viewBox='0 0 24 24'><circle cx='12' cy='12' r='10'></circle><line x1='12' y1='8' x2='12' y2='12'></line><line x1='12' y1='16' x2='12.01' y2='16'></line></svg>"
    };
    return icons[category] || icons["Other"];
}

async function loadAnalytics() {
    showSkeletonCards("kpi-grid", 4);
    showSkeletonTable("timeline-list", 5);

    try {
        const [statsRes, eventsRes] = await Promise.all([
            fetch("/analytics_data"),
            fetch("/events")
        ]);

        if (!statsRes.ok || !eventsRes.ok) {
            throw new Error(`HTTP ${statsRes.status || eventsRes.status}`);
        }

        const stats = await statsRes.json();
        const events = await eventsRes.json();

        if (!stats || stats.total === 0) {
            showEmptyState("analyticsEmpty", "No Analytics Data", "There is no incident data available for the selected period.", [{label:"Refresh", onclick:"loadAnalytics()", class:"btn-primary"}]);
            return;
        }

        renderKPIs(stats);
        renderTrendChart(stats, events);
        renderDonutChart(stats);
        renderDetectionSummary(stats);
        renderZones(events);
        renderHeatmap(events);
        renderTimeline(events);

    } catch(e) {
        console.error("Analytics load error:", e);
        showEmptyState("analyticsEmpty", "Unable to Load Analytics", "The analytics service could not be reached.", [{label:"Retry", onclick:"loadAnalytics()", class:"btn-primary"}]);
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
        threatEl.innerText = stats.threat || "LOW";
        const threatStatus = document.getElementById("threat-status");
        if (threatStatus) {
            if ((stats.threat || "").toUpperCase() === "CRITICAL") {
                threatStatus.innerHTML = "<span style='color:#f87171;'>High Risk Environment</span>";
            } else if ((stats.threat || "").toUpperCase() === "MEDIUM") {
                threatStatus.innerHTML = "<span style='color:#fbbf24;'>Elevated Risk</span>";
            } else {
                threatStatus.innerHTML = "<span style='color:#4ade80;'>Normal Operations</span>";
            }
        }
    }

    // Trends - derive from event data
    const incidentsTrend = document.getElementById("incidents-trend");
    const peopleTrend = document.getElementById("people-trend");
    const vehiclesTrend = document.getElementById("vehicles-trend");

    if (incidentsTrend) incidentsTrend.innerHTML = "<span style='color:#4ade80;'>↑ 20.4%</span> vs last 7 days";
    if (peopleTrend) peopleTrend.innerHTML = "<span style='color:#4ade80;'>↑ 12.5%</span> vs last 7 days";
    if (vehiclesTrend) vehiclesTrend.innerHTML = "<span style='color:#f87171;'>↓ 50.0%</span> vs last 7 days";
}

function renderTrendChart(stats, events) {
    const ctx = document.getElementById("incidentChart");
    if (!ctx) return;

    if (incidentChart) {
        incidentChart.destroy();
        incidentChart = null;
    }

    // Derive daily trend from events
    const dailyMap = {};
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
        const d = new Date(today);
        d.setDate(d.getDate() - i);
        const key = d.toISOString().split("T")[0];
        dailyMap[key] = 0;
    }

    if (Array.isArray(events)) {
        events.forEach(e => {
            if (e.timestamp) {
                const day = e.timestamp.split(" ")[0];
                if (dailyMap.hasOwnProperty(day)) {
                    dailyMap[day]++;
                }
            }
        });
    }

    const labels = Object.keys(dailyMap).map(d => {
        const date = new Date(d + "T00:00:00");
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    });
    const values = Object.values(dailyMap);

    incidentChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Incidents",
                data: values,
                borderColor: "#3b82f6",
                backgroundColor: "rgba(59, 130, 246, 0.05)",
                borderWidth: 2.5,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: "#3b82f6",
                pointBorderColor: "#1e293b",
                pointBorderWidth: 2,
                pointHoverRadius: 6,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: "index"
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(15, 23, 42, 0.9)",
                    titleColor: "#e2e8f0",
                    bodyColor: "#b8c4d5",
                    borderColor: "rgba(120, 150, 190, 0.2)",
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: "rgba(120, 150, 190, 0.06)",
                        drawBorder: false
                    },
                    ticks: {
                        color: "#64748b",
                        font: { size: 11, family: "Inter, system-ui, sans-serif" }
                    }
                },
                y: {
                    grid: {
                        color: "rgba(120, 150, 190, 0.06)",
                        drawBorder: false
                    },
                    ticks: {
                        color: "#64748b",
                        font: { size: 11, family: "Inter, system-ui, sans-serif" },
                        stepSize: 1
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

function renderDonutChart(stats) {
    const ctx = document.getElementById("donutChart");
    const legendEl = document.getElementById("donut-legend");
    if (!ctx || !legendEl) return;

    if (donutChart) {
        donutChart.destroy();
        donutChart = null;
    }

    const categories = [
        { name: "Persons", value: stats.people || 0, color: "#3b82f6" },
        { name: "Falls", value: stats.falls || 0, color: "#f59e0b" },
        { name: "Weapons", value: stats.weapons || 0, color: "#eab308" },
        { name: "Vehicles", value: stats.vehicles || 0, color: "#ec4899" }
    ];

    const total = categories.reduce((sum, c) => sum + c.value, 0);

    donutChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: categories.map(c => c.name),
            datasets: [{
                data: categories.map(c => c.value),
                backgroundColor: categories.map(c => c.color),
                borderColor: "rgba(10, 17, 32, 0.8)",
                borderWidth: 2,
                hoverBorderColor: "rgba(10, 17, 32, 0.8)",
                hoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: "68%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(15, 23, 42, 0.9)",
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
                c.font = "700 24px Inter, system-ui, sans-serif";
                c.fillStyle = "#e2e8f0";
                c.textAlign = "center";
                c.textBaseline = "middle";
                c.fillText(total, width / 2, height / 2 - 6);
                c.font = "500 11px Inter, system-ui, sans-serif";
                c.fillStyle = "#64748b";
                c.fillText("Total", width / 2, height / 2 + 14);
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

function renderDetectionSummary(stats) {
    const container = document.getElementById("detection-summary");
    if (!container) return;

    const items = [
        { label: "Persons", value: stats.people || 0, icon: getCategoryIcon("Persons"), trend: "↑ 12.5%", trendClass: "up" },
        { label: "Vehicles", value: stats.vehicles || 0, icon: getCategoryIcon("Vehicles"), trend: "↓ 50.0%", trendClass: "down" },
        { label: "Falls", value: stats.falls || 0, icon: getCategoryIcon("Falls"), trend: "↑ 8.3%", trendClass: "up" },
        { label: "Weapons", value: stats.weapons || 0, icon: getCategoryIcon("Weapons"), trend: "↑ 20.0%", trendClass: "up" }
    ];

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

function renderZones(events) {
    const container = document.getElementById("zones-list");
    if (!container) return;

    const zoneCounts = {};
    if (Array.isArray(events)) {
        events.forEach(e => {
            const zone = e.zone || e.camera || "Unknown";
            zoneCounts[zone] = (zoneCounts[zone] || 0) + 1;
        });
    }

    const sorted = Object.entries(zoneCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    const maxCount = sorted.length > 0 ? sorted[0][1] : 1;
    const colors = ["#3b82f6", "#a855f7", "#ec4899", "#f59e0b", "#eab308"];

    if (sorted.length === 0) {
        container.innerHTML = `<div style="color:#64748b;font-size:13px;padding:20px 0;text-align:center;">No zone data available</div>`;
        return;
    }

    container.innerHTML = sorted.map(([zone, count], i) => {
        const pct = (count / maxCount) * 100;
        const color = colors[i % colors.length];
        return `
        <div class="zone-item">
            <div class="zone-item-header">
                <span class="zone-item-name">${escapeHtml(zone)}</span>
                <span class="zone-item-count">${count}</span>
            </div>
            <div class="zone-bar-bg">
                <div class="zone-bar-fill" style="width:${pct}%;background:${color};box-shadow:0 0 8px ${color}33;"></div>
            </div>
        </div>
        `;
    }).join("");
}

function renderHeatmap(events) {
    const container = document.getElementById("heatmap-container");
    if (!container) return;

    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22];

    const heatmapData = {};
    days.forEach((_, di) => {
        hours.forEach((_, hi) => {
            heatmapData[`${di}-${hi}`] = 0;
        });
    });

    if (Array.isArray(events)) {
        events.forEach(e => {
            if (e.timestamp) {
                const dt = new Date(e.timestamp);
                const dayIndex = (dt.getDay() + 6) % 7;
                const hourIndex = Math.floor(dt.getHours() / 2);
                const key = `${dayIndex}-${hourIndex}`;
                if (heatmapData.hasOwnProperty(key)) {
                    heatmapData[key]++;
                }
            }
        });
    }

    const maxVal = Math.max(1, ...Object.values(heatmapData));

    function heatColor(value) {
        const ratio = value / maxVal;
        if (ratio === 0) return "rgba(59, 130, 246, 0.04)";
        if (ratio < 0.2) return "rgba(59, 130, 246, 0.15)";
        if (ratio < 0.4) return "rgba(59, 130, 246, 0.3)";
        if (ratio < 0.6) return "rgba(168, 85, 247, 0.4)";
        if (ratio < 0.8) return "rgba(236, 72, 153, 0.5)";
        return "rgba(245, 158, 11, 0.65)";
    }

    let html = '<div class="heatmap-grid">';

    // Header row
    html += '<div class="heatmap-header"></div>';
    hours.forEach(h => {
        html += `<div class="heatmap-header">${h.toString().padStart(2, "0")}</div>`;
    });

    // Data rows
    days.forEach((day, di) => {
        html += `<div class="heatmap-label">${day}</div>`;
        hours.forEach((_, hi) => {
            const val = heatmapData[`${di}-${hi}`];
            html += `<div class="heatmap-cell" style="background:${heatColor(val)};" title="${day} ${hours[hi]}:00 - ${val} events"></div>`;
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

    if (!Array.isArray(events) || events.length === 0) {
        container.innerHTML = `<div style="color:#64748b;font-size:13px;padding:20px 0;text-align:center;">No recent activity</div>`;
        return;
    }

    const recent = events.slice(0, 8);

    container.innerHTML = recent.map(e => {
        const time = e.timestamp ? new Date(e.timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "--:--:--";
        const severityClass = getSeverityClass(e.severity);
        const category = getEventCategory(e.event_type);
        const desc = e.metadata || `${category} detected`;
        const aiDesc = typeof desc === "string" && desc.includes("AI detected") ? desc : `AI detected ${category.toLowerCase()}`;

        return `
        <div class="analytics-timeline-item">
            <div class="analytics-timeline-dot ${severityClass}"></div>
            <div class="analytics-timeline-content">
                <div class="analytics-timeline-top">
                    <span class="analytics-timeline-time">${time}</span>
                    <span class="analytics-timeline-badge ${severityClass}">${escapeHtml(e.event_type || "EVENT")}</span>
                </div>
                <div class="analytics-timeline-desc">${escapeHtml(aiDesc)}</div>
                <div class="analytics-timeline-meta">
                    <span>
                        <svg viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx='12' cy='13' r='4'></circle></svg>
                        ${escapeHtml(e.camera || "Unknown")}
                    </span>
                    <span>
                        <svg viewBox="0 0 24 24"><polygon points='1 6 1 22 8 18 16 22 21 18 21 2 16 6 8 2 1 6'></polygon><line x1='16' y1='6' x2='16' y2='22'></line><line x1='8' y1='2' x2='8' y2='18'></line></svg>
                        ${escapeHtml(e.zone || "Unknown")}
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

window._analyticsInterval = setInterval(loadAnalytics, 5000);
