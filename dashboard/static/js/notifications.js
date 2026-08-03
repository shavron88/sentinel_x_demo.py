function renderNotificationHistory() {
    const list = document.getElementById("notificationHistoryList");
    const empty = document.getElementById("historyEmptyState");
    const stats = document.getElementById("notificationStats");
    const search = document.getElementById("notificationSearch");
    const activeFilter = document.querySelector(".filter-chip.active")?.dataset.filter || "all";

    if (!list) return;

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
                    <div class="notification-history-title">${item.title}</div>
                    <div class="notification-history-message">${item.message}</div>
                    <div class="notification-history-meta">
                        <span>🕒 ${item.time}</span>
                        <span>📅 ${item.date}</span>
                    </div>
                </div>
                <span class="notification-history-badge badge-${item.type}">${item.type}</span>
            </div>
        `;
    });

    list.innerHTML = html;
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
