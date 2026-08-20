function renderNotificationHistory() {
    const list = document.getElementById("notificationHistoryList");
    const empty = document.getElementById("historyEmptyState");
    const stats = document.getElementById("notificationStats");
    const search = document.getElementById("notificationSearch");
    const activeFilter = document.querySelector(".filter-chip.active")?.dataset.filter || "all";

    if (!list) return;

    showSkeletonRows("notificationHistoryList", 8);

    if (list.innerHTML.trim() === '' || list.querySelector('.panel-loading')) {
        list.innerHTML = '<div style="text-align:center;padding:40px;color:#64748b;">Loading notifications...</div>';
    }
    
    if (!notifications.length) {
        list.innerHTML = "";
        if (empty) {
            empty.style.display = "flex";
            empty.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:40px;height:40px;opacity:0.4;margin-bottom:12px;">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                <h3 style="color:#e2e8f0;margin:0 0 8px 0;">No Notifications Yet</h3>
                <p style="color:#94a3b8;margin:0;">When alerts are generated, they will appear here.</p>
            `;
        }
        if (stats) stats.innerHTML = 'Showing <strong>0</strong> of <strong>0</strong> notifications';
        return;
    }

    let filtered = [...notifications];

    if (activeFilter !== "all") {
        filtered = filtered.filter(n => n.type === activeFilter);
    }

    if (search && search.value.trim()) {
        const q = search.value.toLowerCase();
        filtered = filtered.filter(n =>
            n.title.toLowerCase().includes(q) ||
            n.message.toLowerCase().includes(q)
        );
    }

    if (stats) {
        stats.innerHTML = `Showing <strong>${filtered.length}</strong> of <strong>${notifications.length}</strong> notifications`;
    }

    if (filtered.length === 0) {
        list.innerHTML = "";
        if (empty) empty.style.display = "flex";
        return;
    }

    if (empty) empty.style.display = "none";

    const typeIcons = {
        danger: "🚨",
        warning: "⚠️",
        success: "✅",
        info: "ℹ️"
    };

    let html = "";
    filtered.forEach(item => {
        html += `
            <div class="notification-history-item type-${item.type} ${item.read ? "" : "unread"}" onclick="markAsRead('${item.id}')">
                <div class="notification-history-icon notification-${item.type}">
                    ${typeIcons[item.type] || "ℹ️"}
                </div>
                <div class="notification-history-content">
                    <div class="notification-history-title">${escapeHtml(item.title)}</div>
                    <div class="notification-history-message">${escapeHtml(item.message)}</div>
                    <div class="notification-history-meta">
                        <span>🕒 ${escapeHtml(item.time)}</span>
                        <span>📅 ${escapeHtml(item.date)}</span>
                    </div>
                </div>
                <span class="notification-history-badge badge-${item.type}">${item.type}</span>
            </div>
        `;
    });

    list.innerHTML = html;
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function setFilter(filter) {
    document.querySelectorAll(".filter-chip").forEach(chip => {
        chip.classList.toggle("active", chip.dataset.filter === filter);
    });
    renderNotificationHistory();
}

function filterNotifications() {
    renderNotificationHistory();
}

function clearNotificationHistory() {
    if (confirm("Clear all notification history?")) {
        notifications = [];
        saveNotificationHistory();
        updateNotificationPanel();
        renderNotificationHistory();
    }
}

function markAllAsRead() {
    notifications.forEach(n => n.read = true);
    saveNotificationHistory();
    updateNotificationPanel();
    renderNotificationHistory();
}

function markAsRead(id) {
    const item = notifications.find(n => String(n.id) === String(id));
    if (item) {
        item.read = true;
        saveNotificationHistory();
        updateNotificationPanel();
        renderNotificationHistory();
    }
}

function loadNotificationHistory() {
    try {
        const stored = localStorage.getItem("sentinelx_notifications");
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Array.isArray(parsed)) {
                notifications = parsed;
            }
        }
    } catch (e) {
        console.error("Failed to load notifications:", e);
        const empty = document.getElementById("historyEmptyState");
        if (empty) {
            empty.style.display = "flex";
            empty.innerHTML = `
                <h3 style="color:#e2e8f0;margin:0 0 8px 0;">Unable to Load Notifications</h3>
                <p style="color:#94a3b8;margin:0 0 20px 0;">The notification service could not be reached.</p>
                <button class="btn btn-primary" onclick="loadNotificationHistory()">Retry</button>
            `;
        }
    }
    renderNotificationHistory();
}

loadNotificationHistory();
