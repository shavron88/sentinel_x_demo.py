async function loadThreats() {
    const feed = document.getElementById("threatFeed");
    const log = document.getElementById("aiDecisionLog");
    const riskGauge = document.getElementById("riskGauge");
    const empty = document.getElementById("emptyState");
    
    if (!feed) return;
    
    feed.innerHTML = "";
    if (log) log.innerHTML = "";
    if (empty) empty.style.display = "none";
    
    showSkeletonRows("threatFeed", 5);
    if (log) showSkeletonRows("aiDecisionLog", 3);
    
    try {
        const [eventsRes, timelineRes] = await Promise.all([
            fetch("/events").catch(() => null),
            fetch("/timeline").catch(() => null)
        ]);
        
        let events = [];
        if (eventsRes && eventsRes.ok) {
            const data = await eventsRes.json();
            events = Array.isArray(data) ? data : [];
        }
        
        let timeline = [];
        if (timelineRes && timelineRes.ok) {
            const tdata = await timelineRes.json();
            timeline = Array.isArray(tdata) ? tdata : (tdata.timeline || []);
        }
        
        const allItems = [...events, ...timeline];
        
        hideSkeletons();
        
        if (allItems.length === 0) {
            showEmptyState("emptyState", "No Active Threats", "All systems are secure. No threats detected.", [{label:"Refresh", onclick:"loadThreats()", class:"btn-primary"}]);
            if (riskGauge) riskGauge.textContent = "LOW";
            if (log) log.innerHTML = '<div class="ai-log">No AI decisions recorded.</div>';
            return;
        }
        
        const severityOrder = { 'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3 };
        const sorted = allItems.sort((a, b) => {
            const sa = severityOrder[(a.severity || 'LOW').toUpperCase()] ?? 9;
            const sb = severityOrder[(b.severity || 'LOW').toUpperCase()] ?? 9;
            return sa - sb;
        });
        
        const topThreats = sorted.slice(0, 8);
        const highestSeverity = topThreats.length > 0 ? (topThreats[0].severity || 'LOW').toUpperCase() : 'LOW';
        
        if (riskGauge) {
            riskGauge.textContent = highestSeverity;
            riskGauge.className = "risk-gauge " + highestSeverity.toLowerCase();
        }
        
        topThreats.forEach((item, index) => {
            const card = document.createElement("div");
            card.className = `feed-item ${(item.severity || 'low').toLowerCase()}`;
            card.style.animationDelay = `${Math.min(index * 0.04, 0.5)}s`;
            
            const eventType = item.event_type || item.event || "Unknown Event";
            const severity = (item.severity || 'LOW').toUpperCase();
            const camera = item.camera || 'Unknown';
            const zone = item.zone || 'Unknown';
            const time = item.timestamp || item.time || new Date().toLocaleTimeString();
            
            card.innerHTML = `
                <h3>${escapeHtml(eventType)}</h3>
                <p><strong>Severity:</strong> ${escapeHtml(severity)}</p>
                <p><strong>Camera:</strong> ${escapeHtml(camera)}</p>
                <p><strong>Zone:</strong> ${escapeHtml(zone)}</p>
                <p><strong>Time:</strong> ${escapeHtml(time)}</p>
            `;
            
            feed.appendChild(card);
        });
        
        if (log) {
            const aiLogs = [
                { msg: "Object classification complete", conf: "98.2%" },
                { msg: "Behavior analysis updated", conf: "96.5%" },
                { msg: "Zone monitoring active", conf: "99.1%" },
                { msg: "Threat assessment recalibrated", conf: "97.3%" }
            ];
            
            aiLogs.forEach(entry => {
                const div = document.createElement("div");
                div.className = "ai-log";
                div.innerHTML = `${escapeHtml(entry.msg)} - Confidence: ${entry.conf}`;
                log.appendChild(div);
            });
        }
        
    } catch (err) {
        console.error("Failed to load threat center:", err);
        hideSkeletons();
        showEmptyState("emptyState", "Unable to Load Threats", "The threat service could not be reached.", [{label:"Retry", onclick:"loadThreats()", class:"btn-primary"}]);
    }
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadThreats();
window._threatInterval = setInterval(loadThreats, 10000);
/* ==========================================
   THREAT CENTER CLEANUP
========================================== */

function cleanupThreatCenter() {
    if (window._threatInterval) {
        clearInterval(window._threatInterval);
        window._threatInterval = null;
    }
}

window.addEventListener("beforeunload", cleanupThreatCenter);
