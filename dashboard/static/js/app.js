let notifications = [];
let soundEnabled = true;
let alertPopupActive = false;

/* ==========================================
   GLOBAL THEME RESTORE
   Runs on every page to apply saved theme.
   Light theme is disabled - defaults to dark.
========================================= */

function restoreTheme() {
    try {
        const saved = localStorage.getItem('sentinelx-theme');
        // Force dark theme - clear any saved light theme
        if (saved === 'light') {
            localStorage.removeItem('sentinelx-theme');
        }
        if (saved && ['dark', 'midnight'].includes(saved)) {
            document.documentElement.setAttribute('data-theme', saved);
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    } catch (e) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

/* ==========================================
    CHART THEME HELPER
   Returns colors adapted to current theme.
   Shared by dashboard.js and analytics.js.
========================================== */

window.getChartTheme = function() {
    var isLight = document.documentElement.getAttribute('data-theme') === 'light';
    return {
        tooltipBg:     isLight ? 'rgba(255,255,255,0.97)'   : 'rgba(15,23,42,0.92)',
        tooltipBorder: isLight ? 'rgba(0,0,0,0.08)'         : 'rgba(120,150,190,0.2)',
        tooltipTitle:  isLight ? '#0f172a'                   : '#e2e8f0',
        tooltipBody:   isLight ? '#475569'                   : '#94a3b8',
        gridColor:     isLight ? 'rgba(0,0,0,0.06)'         : 'rgba(255,255,255,0.05)',
        tickColor:     isLight ? '#475569'                   : '#64748b',
        centerText:    isLight ? '#0f172a'                   : '#e2e8f0',
        centerLabel:   isLight ? '#64748b'                   : '#64748b',
        donutBorder:   isLight ? 'rgba(255,255,255,0.9)'    : 'rgba(10,17,32,0.8)',
        pointBorder:   isLight ? '#ffffff'                   : '#0f172a'
    };
};

/* ==========================================
   AUTO-REFRESH CHARTS ON THEME CHANGE
   Watches for data-theme attribute changes
   and re-applies chart colors.
========================================== */

window.refreshChartsOnThemeChange = function() {
    new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
            if (m.attributeName !== 'data-theme') return;
            var t = window.getChartTheme();

            // Standard line charts (dashboard + analytics)
            [window.detectionChart, window.performanceChart, window.incidentChart].forEach(function(chart) {
                if (!chart || !chart.options) return;
                var tip = chart.options.plugins.tooltip;
                if (tip) {
                    tip.backgroundColor = t.tooltipBg;
                    tip.borderColor     = t.tooltipBorder;
                    tip.titleColor      = t.tooltipTitle;
                    tip.bodyColor       = t.tooltipBody;
                }
                if (chart.options.scales) {
                    ['x','y'].forEach(function(axis) {
                        var s = chart.options.scales[axis];
                        if (s && s.grid) s.grid.color = t.gridColor;
                        if (s && s.ticks) s.ticks.color = t.tickColor;
                    });
                }
                chart.update('none');
            });

            // Donut chart needs special centerText plugin handling
            if (window.donutChart && window.donutChart.options) {
                var dTip = window.donutChart.options.plugins.tooltip;
                if (dTip) {
                    dTip.backgroundColor = t.tooltipBg;
                    dTip.borderColor     = t.tooltipBorder;
                    dTip.titleColor      = t.tooltipTitle;
                    dTip.bodyColor       = t.tooltipBody;
                }
                // Update donut border color
                var ds = window.donutChart.data.datasets[0];
                if (ds) {
                    ds.borderColor = t.donutBorder;
                    ds.hoverBorderColor = t.donutBorder;
                }
                window.donutChart.update('none');
            }
        });
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
};

/* ==========================================
    AUDIO ENGINE
========================================== */

const AudioEngine = {
    ctx: null,

    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
    },

    play(type = "info") {
        if (!soundEnabled) return;
        this.init();
        const ctx = this.ctx;
        const now = ctx.currentTime;

        const sounds = {
            success: [
                { f: 880, t: 0, d: 0.1 },
                { f: 1100, t: 0.1, d: 0.15 }
            ],
            warning: [
                { f: 660, t: 0, d: 0.15 },
                { f: 660, t: 0.2, d: 0.15 }
            ],
            danger: [
                { f: 440, t: 0, d: 0.2 },
                { f: 350, t: 0.25, d: 0.3 },
                { f: 440, t: 0.6, d: 0.4 }
            ],
            info: [
                { f: 520, t: 0, d: 0.1 }
            ]
        };

        const tones = sounds[type] || sounds.info;
        tones.forEach(tone => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = tone.f;
            osc.type = "sine";
            gain.gain.setValueAtTime(0.15, now + tone.t);
            gain.gain.exponentialRampToValueAtTime(0.001, now + tone.t + tone.d);
            osc.start(now + tone.t);
            osc.stop(now + tone.t + tone.d + 0.05);
        });
    }
};

// =========================
// TOAST SYSTEM
// =========================

function showToast(title, message, type = "info", persistent = false) {
    AudioEngine.play(type);

    const icons = {
        success: "✅",
        warning: "⚠️",
        danger: "🚨",
        info: "ℹ️"
    };

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-body">
            <div class="toast-title">${escapeHtml(title)}</div>
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <div class="toast-progress"></div>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    const container = document.getElementById("toast-container");
    if (container) {
        container.prepend(toast);
    }

    // Force reflow for animation
    void toast.offsetWidth;
    toast.classList.add("toast-enter");

    // Save to history
    const entry = {
        id: Date.now() + Math.random(),
        title,
        message,
        type,
        time: new Date().toLocaleTimeString(),
        date: new Date().toLocaleDateString(),
        read: false
    };

    notifications.unshift(entry);
    if (notifications.length > 50) notifications.pop();

    saveNotificationHistory();
    updateNotificationPanel();

    // Alert popup for danger
    if (type === "danger" && !persistent) {
        showAlertPopup(entry);
    }

    if (!persistent) {
        const duration = type === "danger" ? 8000 : 5000;
        setTimeout(() => {
            toast.classList.remove("toast-enter");
            toast.classList.add("toast-exit");
            setTimeout(() => toast.remove(), 400);
        }, duration);
    }

    return entry;
}

// =========================
// ALERT POPUP
// =========================

function showAlertPopup(notification) {
    if (alertPopupActive) return;
    alertPopupActive = true;

    const modal = document.getElementById("alertPopup");
    if (!modal) return;

    document.getElementById("alertPopupTitle").textContent = notification.title;
    document.getElementById("alertPopupMessage").textContent = notification.message;
    document.getElementById("alertPopupTime").textContent = notification.time;

    modal.classList.add("active");
    document.body.style.overflow = "hidden";

    AudioEngine.play("danger");
}

function closeAlertPopup() {
    const modal = document.getElementById("alertPopup");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
        alertPopupActive = false;
    }
}

// =========================
// NOTIFICATION PERSISTENCE
// =========================

function saveNotificationHistory() {
    try {
        localStorage.setItem("sentinelx_notifications", JSON.stringify(notifications));
    } catch (e) {}
}

function loadNotificationHistory() {
    try {
        const stored = localStorage.getItem("sentinelx_notifications");
        if (stored) {
            notifications = JSON.parse(stored);
        }
    } catch (e) {}
}

function clearNotificationHistory() {
    notifications = [];
    saveNotificationHistory();
    updateNotificationPanel();
    renderNotificationHistory();
}

function markAllAsRead() {
    notifications.forEach(n => n.read = true);
    saveNotificationHistory();
    updateNotificationPanel();
    renderNotificationHistory();
}

// =========================
// NOTIFICATION PANEL (Dropdown)
// =========================

function updateNotificationPanel() {
    const list = document.getElementById("notification-list");
    const count = document.getElementById("notification-count");

    if (!list) return;

    if (count) {
        const unread = notifications.filter(n => !n.read).length;
        count.innerText = unread > 0 ? unread : notifications.length;
        count.style.display = notifications.length > 0 ? "flex" : "none";
    }

    if (notifications.length === 0) {
        list.innerHTML = `
            <div class="notification-empty">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.4">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                <p>No notifications yet</p>
            </div>
        `;
        return;
    }

    let html = "";
    notifications.slice(0, 10).forEach(item => {
        html += `
            <div class="notification-item ${item.read ? "read" : "unread"}" data-id="${item.id}" onclick="markAsRead('${item.id}')">
                <div class="notification-item-icon notification-${item.type}">
                    ${item.type === "danger" ? "🚨" : item.type === "warning" ? "⚠️" : item.type === "success" ? "✅" : "ℹ️"}
                </div>
                <div class="notification-item-content">
                    <div class="notification-item-title">${item.title}</div>
                    <div class="notification-item-message">${item.message}</div>
                    <div class="notification-item-time">${item.time}</div>
                </div>
            </div>
        `;
    });

    if (notifications.length > 10) {
        html += `<div class="notification-view-all" onclick="window.location.href='/notifications'">View all ${notifications.length} notifications →</div>`;
    }

    list.innerHTML = html;
}

function markAsRead(id) {
    const item = notifications.find(n => String(n.id) === String(id));
    if (item) {
        item.read = true;
        saveNotificationHistory();
        updateNotificationPanel();
    }
}

// =========================
// SOUND TOGGLE
// =========================

function toggleSound() {
    soundEnabled = !soundEnabled;
    const btn = document.getElementById("soundToggle");
    if (btn) {
        btn.classList.toggle("active", soundEnabled);
        btn.innerHTML = soundEnabled
            ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`
            : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>`;
    }
    showToast("Sound", soundEnabled ? "Notifications enabled" : "Notifications muted", "info");
}

// =========================
// NOTIFICATION TOGGLE PANEL
// =========================

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("notification-btn");
    const panel = document.getElementById("notification-panel");

    if (btn && panel) {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            panel.classList.toggle("active");
            if (panel.classList.contains("active")) {
                updateNotificationPanel();
            }
        });

        document.addEventListener("click", (e) => {
            if (!panel.contains(e.target) && !btn.contains(e.target)) {
                panel.classList.remove("active");
            }
        });
    }
});

// =========================
// INIT
// =========================

document.addEventListener("DOMContentLoaded", () => {
    restoreTheme();
    loadNotificationHistory();
    updateNotificationPanel();

    const soundBtn = document.getElementById("soundToggle");
    if (soundBtn) {
        soundBtn.classList.add("active");
        soundBtn.addEventListener("click", toggleSound);
    }
});

// =========================
// SIDEBAR TOGGLE (MOBILE)
// =========================

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    if (!sidebar || !overlay) return;

    const isOpen = sidebar.classList.contains("open");

    if (isOpen) {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
        document.body.style.overflow = "";
    } else {
        sidebar.classList.add("open");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

// Close sidebar on window resize to desktop

window.addEventListener("resize", () => {
    if (window.innerWidth > 1024) {
        const sidebar = document.getElementById("sidebar");
        const overlay = document.getElementById("sidebarOverlay");
        if (sidebar) sidebar.classList.remove("open");
        if (overlay) overlay.classList.remove("active");
        document.body.style.overflow = "";
    }
});

// =========================
// PROFILE DROPDOWN & LOGOUT
// =========================

(function() {
    const avatarBtn = document.getElementById("avatarBtn");
    const dropdown  = document.getElementById("profileDropdown");
    const logoutBtn = document.getElementById("logoutBtn");

    function setText(id, value, fallback) {
        const el = document.getElementById(id);
        if (el && value) el.textContent = value;
        else if (el && fallback) el.textContent = fallback;
    }

    function setInitials(text) {
        const initials = (text || "SX").slice(0, 2).toUpperCase();
        setText("avatarInitials", initials);
        setText("dropdownAvatarInitials", initials);
    }

    function loadUserProfile() {
        fetch("/api/auth/status")
            .then(function(r) { return r.ok ? r.json() : null; })
            .then(function(data) {
                if (!data || !data.authenticated) return;
                const name = data.username || "";
                const email = data.email || "";
                const role = data.role || "";
                setText("profileDisplayName", name.charAt(0).toUpperCase() + name.slice(1), name);
                setText("profileDisplayEmail", email, "admin@sentinelx.ai");
                setText("profileDisplayRole", role, "System Administrator");
                setInitials(name);
            })
            .catch(function() { /* Keep server-rendered defaults */ });
    }

    if (avatarBtn && dropdown) {
        // Populate dynamic user info on every dashboard page load
        loadUserProfile();

        avatarBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            const isOpen = dropdown.classList.toggle("open");
            avatarBtn.setAttribute("aria-expanded", isOpen);
        });

        // Keyboard support
        avatarBtn.addEventListener("keydown", function(e) {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                avatarBtn.click();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", function(e) {
            if (!dropdown.contains(e.target) && e.target !== avatarBtn) {
                dropdown.classList.remove("open");
                avatarBtn.setAttribute("aria-expanded", "false");
            }
        });

        // Close on Escape
        document.addEventListener("keydown", function(e) {
            if (e.key === "Escape" && dropdown.classList.contains("open")) {
                dropdown.classList.remove("open");
                avatarBtn.setAttribute("aria-expanded", "false");
                avatarBtn.focus();
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", function() {
            logoutBtn.disabled = true;
            const csrf = window.__SENTINELX_CSRF__ ||
                         (function() {
                             try { return sessionStorage.getItem("sentinelx_csrf"); } catch(e) { return null; }
                         })();

            const headers = { "Accept": "application/json" };
            if (csrf) headers["X-CSRF-Token"] = csrf;

            fetch("/api/auth/logout", { method: "POST", headers: headers })
                .then(function() {
                    try {
                        sessionStorage.removeItem("sentinelx_csrf");
                        localStorage.removeItem("sentinelx_notifications");
                    } catch(e) {}
                    window.location.href = "/login";
                })
                .catch(function() {
                    // Force redirect even if logout request fails
                    window.location.href = "/login";
                });
        });
    }
})();

// =========================
// CSRF TOKEN BOOTSTRAP
// =========================

(function() {
    // Fetch CSRF token on page load and store for AJAX requests
    fetch("/api/auth/csrf-token")
        .then(function(r) { return r.ok ? r.json() : null; })
        .then(function(data) {
            if (data && data.csrf_token) {
                window.__SENTINELX_CSRF__ = data.csrf_token;
                try { sessionStorage.setItem("sentinelx_csrf", data.csrf_token); } catch(e) {}
            }
        })
        .catch(function() { /* Silent fail — token will be fetched on demand */ });
})();
