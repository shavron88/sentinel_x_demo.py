let notifications = [];
let soundEnabled = true;
let alertPopupActive = false;

// app.js is the first script on every authenticated page, so it cannot rely on
// a later file to have defined escapeHtml(). Identical implementations exist
// in several page scripts; this one guarantees the core bundle stands alone.
if (typeof window.escapeHtml !== "function") {
    window.escapeHtml = function (text) {
        if (text == null) return "";
        const div = document.createElement("div");
        div.textContent = String(text);
        return div.innerHTML;
    };
}

const ICONS = { success: "✅", warning: "⚠️", danger: "🚨", info: "ℹ️" };

/* ==========================================
   CONNECTION STATE
   Every poll used to swallow its error, so a dead backend left the dashboard
   showing stale numbers with no indication anything was wrong. For a
   surveillance product that is the dangerous state: "no threats" and
   "detection is down" looked identical.
========================================= */
const ConnectionState = (() => {
    let el = null;
    let failures = 0;
    let lastOk = Date.now();
    let stamp = null;

    function ensure() {
        if (!el) {
            el = document.createElement("div");
            el.className = "conn-banner";
            el.setAttribute("role", "alert");
            el.setAttribute("aria-live", "assertive");
            el.hidden = true;
            document.body.appendChild(el);
        }
        return el;
    }

    function setStamp() {
        if (!stamp) stamp = document.getElementById("dataFreshness");
        if (stamp) stamp.textContent = new Date(lastOk).toLocaleTimeString();
    }

    function markStale(stale) {
        if (!stamp) stamp = document.getElementById("dataFreshness");
        if (stamp) stamp.parentElement.classList.toggle("is-stale", stale);
    }

    return {
        ok() {
            lastOk = Date.now();
            failures = 0;
            setStamp();
            markStale(false);
            const node = ensure();
            if (!node.hidden) {
                node.hidden = true;
            }
        },
        fail() {
            failures += 1;
            markStale(true);
            if (failures < 2) return;          // ignore a single blip
            const node = ensure();
            node.textContent =
                `Live data unavailable - showing last known values from `
                + `${new Date(lastOk).toLocaleTimeString()}. Retrying...`;
            node.hidden = false;
        },
        get lastSuccess() { return lastOk; }
    };
})();
window.ConnectionState = ConnectionState;

/* ==========================================
   SINGLE-FLIGHT POLLER
   setInterval does not wait for the previous request. Whenever a response was
   slower than the interval (routine on this box, where /stats measured up to
   1.2s against a 2s tick) several calls overlapped and whichever resolved last
   won, so stale values overwrote fresh ones. This keeps at most one request in
   flight per key, pauses while the tab is hidden, and reports failures.
========================================= */
window.pollSafely = function (key, url, intervalMs, onData, onError) {
    const inflight = (window._inflight = window._inflight || {});
    let stopped = false;
    let timer = null;

    async function tick() {
        if (stopped || document.hidden) return;
        if (inflight[key]) return;                       // single-flight
        inflight[key] = true;
        try {
            const res = await fetch(url, { cache: "no-store", headers: { "Accept": "application/json" } });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            ConnectionState.ok();
            if (typeof onData === "function") onData(data);
        } catch (err) {
            ConnectionState.fail();
            if (typeof onError === "function") onError(err);
        } finally {
            inflight[key] = false;
        }
    }

    tick();
    timer = setInterval(tick, intervalMs);
    (window._dashboardIntervals = window._dashboardIntervals || []).push(timer);

    // Catch up immediately when the operator comes back to the tab.
    document.addEventListener("visibilitychange", () => {
        if (!document.hidden && !stopped) tick();
    });

    return function stop() {
        stopped = true;
        if (timer) clearInterval(timer);
    };
};

/* ==========================================
   GLOBAL THEME RESTORE
   Runs on every page to apply saved theme.
   Light theme is disabled - defaults to dark.
========================================= */

function restoreTheme() {
    try {
        const saved = localStorage.getItem('sentinelx-theme');
        // Honour the stored theme rather than deleting 'light'. The previous
        // behaviour threw the operator's choice away on every page load even
        // though the theme system implements light fully.
        if (saved && ['dark', 'light', 'midnight'].includes(saved)) {
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

    const icon = ICONS[type] || ICONS.info;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-body">
            <div class="toast-title">${escapeHtml(title)}</div>
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <div class="toast-progress"></div>
        <button class="toast-close" type="button" aria-label="Dismiss notification">✕</button>
    `;
    toast.querySelector(".toast-close")
        .addEventListener("click", () => toast.remove());

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
    const modal = document.getElementById("alertPopup");
    if (!modal) return;
    alertPopupActive = true;
    _lastFocused = document.activeElement;

    document.getElementById("alertPopupTitle").textContent = notification.title;
    document.getElementById("alertPopupMessage").textContent = notification.message;
    document.getElementById("alertPopupTime").textContent = notification.time;

    modal.hidden = false;
    modal.classList.add("active");
    document.body.style.overflow = "hidden";

    // Move focus into the dialog so keyboard users are not stranded behind it.
    const ack = modal.querySelector(".alert-popup-btn-ack");
    if (ack) ack.focus();

    AudioEngine.play("danger");
}

let _lastFocused = null;

function closeAlertPopup() {
    const modal = document.getElementById("alertPopup");
    if (modal) {
        modal.classList.remove("active");
        modal.hidden = true;
        document.body.style.overflow = "";
        alertPopupActive = false;
        // Return focus to whatever opened the dialog.
        if (_lastFocused && typeof _lastFocused.focus === "function") {
            _lastFocused.focus();
        }
        _lastFocused = null;
    }
}

// Escape closes the dialog and Tab is trapped inside it. Without this the
// popup could not be dismissed from the keyboard at all.
document.addEventListener("keydown", (e) => {
    const modal = document.getElementById("alertPopup");
    if (!modal || !alertPopupActive) return;

    if (e.key === "Escape") {
        e.preventDefault();
        closeAlertPopup();
        return;
    }
    if (e.key !== "Tab") return;

    const focusables = modal.querySelectorAll(
        'button:not([disabled]), [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
    }
});

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
    const btn = document.getElementById("notification-btn");

    if (!list) return;

    // The badge showed the unread count, but the *total* whenever nothing was
    // unread -- so the number silently changed meaning. It now always means
    // "unread" and is hidden at zero, with an accessible label.
    const unread = notifications.filter(n => !n.read).length;

    if (count) {
        count.textContent = unread > 99 ? "99+" : String(unread);
        count.hidden = unread === 0;
        count.classList.toggle("is-read", unread === 0);
    }
    if (btn) {
        btn.setAttribute("aria-label",
            unread ? `${unread} unread notification${unread === 1 ? "" : "s"}`
                   : "Notifications");
        btn.setAttribute("aria-expanded",
            String(document.getElementById("notification-panel")?.classList.contains("active") || false));
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
        // These values originate from detection data (camera/zone names) and
        // are persisted to localStorage, so they are escaped here exactly as
        // showToast() escapes them on the way in. The id also went into an
        // inline onclick, so actions are delegated instead.
        const icon = ICONS[item.type] || ICONS.info;
        html += `
            <div class="notification-item ${item.read ? "read" : "unread"}"
                 data-id="${escapeHtml(item.id)}" role="button" tabindex="0">
                <div class="notification-item-icon notification-${escapeHtml(item.type)}">
                    ${icon}
                </div>
                <div class="notification-item-content">
                    <div class="notification-item-title">${escapeHtml(item.title)}</div>
                    <div class="notification-item-message">${escapeHtml(item.message)}</div>
                    <div class="notification-item-time">${escapeHtml(item.time)}</div>
                </div>
            </div>
        `;
    });

    if (notifications.length > 10) {
        html += `<div class="notification-view-all" data-view-all="1">View all ${notifications.length} notifications →</div>`;
    }

    list.innerHTML = html;

    list.querySelectorAll(".notification-item").forEach(el => {
        const activate = () => markAsRead(el.getAttribute("data-id"));
        el.addEventListener("click", activate);
        el.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                activate();
            }
        });
    });
    const viewAll = list.querySelector("[data-view-all]");
    if (viewAll) {
        viewAll.setAttribute("role", "button");
        viewAll.setAttribute("tabindex", "0");
        viewAll.addEventListener("click", () => { window.location.href = "/notifications"; });
        viewAll.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                window.location.href = "/notifications";
            }
        });
    }
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
            const open = panel.classList.toggle("active");
            btn.setAttribute("aria-expanded", String(open));
            if (open) {
                updateNotificationPanel();
            }
        });

        // Escape closes the panel and returns focus to the trigger.
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && panel.classList.contains("active")) {
                panel.classList.remove("active");
                btn.setAttribute("aria-expanded", "false");
                btn.focus();
            }
        });

        document.addEventListener("click", (e) => {
            if (!panel.contains(e.target) && !btn.contains(e.target)) {
                panel.classList.remove("active");
                btn.setAttribute("aria-expanded", "false");
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
// SIDEBAR EXPANDABLE PARENTS
// =========================

document.addEventListener("DOMContentLoaded", () => {
    const parents = document.querySelectorAll(".sidebar-nav-parent");
    
    parents.forEach(parent => {
        parent.addEventListener("click", function(e) {
            const item = this.parentElement;
            const wasOpen = item.classList.contains("open");
            
            if (!wasOpen) {
                e.preventDefault();
                document.querySelectorAll(".sidebar-nav-item.open").forEach(openItem => {
                    if (openItem !== item) {
                        openItem.classList.remove("open");
                    }
                });
                item.classList.add("open");
            }
        });
    });
    
    // Auto-expand based on current path
    const path = window.location.pathname;
    document.querySelectorAll(".sidebar-nav-item").forEach(item => {
        const parentHref = item.querySelector(".sidebar-nav-parent")?.getAttribute("href");
        const childHrefs = Array.from(item.querySelectorAll(".sidebar-nav-child")).map(el => el.getAttribute("href"));
        
        if (parentHref === path || childHrefs.includes(path)) {
            item.classList.add("open");
        }
    });
});

// =========================
// SIDEBAR TOGGLE (MOBILE)
// =========================

function toggleSidebar(force) {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggle = document.getElementById("sidebarToggle");
    if (!sidebar || !overlay) return;

    const isOpen = force !== undefined
        ? !!force
        : !sidebar.classList.contains("open");

    sidebar.classList.toggle("open", isOpen);
    overlay.classList.toggle("active", isOpen);
    if (toggle) toggle.setAttribute("aria-expanded", String(isOpen));
    document.body.style.overflow = isOpen ? "hidden" : "";

    if (isOpen) {
        // Move focus into the drawer so keyboard users are not left behind it.
        const first = sidebar.querySelector("a, button");
        if (first) first.focus();
        document.addEventListener("keydown", onSidebarEscape);
    } else {
        document.removeEventListener("keydown", onSidebarEscape);
        if (toggle && force === false) toggle.focus();
    }
}

function onSidebarEscape(e) {
    if (e.key === "Escape") {
        e.preventDefault();
        toggleSidebar(false);
    }
}

// Close sidebar on window resize to desktop
window.addEventListener("resize", () => {
    if (window.innerWidth > 1024) {
        const sidebar = document.getElementById("sidebar");
        const overlay = document.getElementById("sidebarOverlay");
        const toggle = document.getElementById("sidebarToggle");
        if (sidebar) sidebar.classList.remove("open");
        if (overlay) overlay.classList.remove("active");
        if (toggle) toggle.setAttribute("aria-expanded", "false");
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
    // The token is rendered server-side into a <meta> tag by base.html, so it
    // is available synchronously and no request can race ahead of the fetch.
    var meta = document.querySelector('meta[name="sentinelx-csrf"]');
    if (meta && meta.content) {
        window.__SENTINELX_CSRF__ = meta.content;
        try { sessionStorage.setItem("sentinelx_csrf", meta.content); } catch(e) {}
    }

    function currentToken() {
        if (window.__SENTINELX_CSRF__) return window.__SENTINELX_CSRF__;
        try { return sessionStorage.getItem("sentinelx_csrf"); } catch(e) { return null; }
    }

    // Automatically attach the CSRF header to every state-changing request.
    // Previously each page had to remember to do this, so settings saves,
    // snapshots, deletions and chat all returned 403.
    var SAFE_METHODS = { GET: 1, HEAD: 1, OPTIONS: 1, TRACE: 1 };
    var nativeFetch = window.fetch && window.fetch.bind(window);
    if (nativeFetch) {
        window.fetch = function(input, init) {
            try {
                var method = ((init && init.method) ||
                              (input && input.method) || "GET").toUpperCase();
                if (!SAFE_METHODS[method]) {
                    var token = currentToken();
                    if (token) {
                        if (!init) { init = {}; }
                        var headers = new Headers(init.headers || {});
                        if (!headers.has("X-CSRF-Token")) {
                            headers.set("X-CSRF-Token", token);
                        }
                        init.headers = headers;
                    }
                }
            } catch (e) { /* Never let the wrapper break a request */ }
            return nativeFetch(input, init);
        };
    }

    // Keep the cached token fresh across long-lived tabs.
    fetch("/api/auth/csrf-token", { headers: { "Accept": "application/json" } })
        .then(function(r) { return r.ok ? r.json() : null; })
        .then(function(data) {
            if (data && data.csrf_token) {
                window.__SENTINELX_CSRF__ = data.csrf_token;
                try { sessionStorage.setItem("sentinelx_csrf", data.csrf_token); } catch(e) {}
            }
        })
        .catch(function() { /* Silent fail — token will be fetched on demand */ });
})();
