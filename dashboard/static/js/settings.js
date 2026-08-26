/* ==========================================
   SETTINGS PAGE
========================================== */

let currentTheme = 'midnight';
let settingsLoaded = false;

/* ==========================================
   LOAD SETTINGS FROM BACKEND
========================================== */

async function loadSettings() {
    try {
        const response = await fetch("/api/settings");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        if (data.theme) {
            const saved = (() => {
                try { return localStorage.getItem('sentinelx-theme'); } catch(e) { return null; }
            })();
            if (!saved || !['dark', 'light', 'midnight'].includes(saved)) {
                setTheme(data.theme);
            }
        }

        if (data.profile) {
            const nameEl = document.getElementById("profileName");
            const emailEl = document.getElementById("profileEmail");
            if (nameEl && data.profile.name) nameEl.value = data.profile.name;
            if (emailEl && data.profile.email) emailEl.value = data.profile.email;
        }

        if (data.cameras && Array.isArray(data.cameras)) {
            applyCameraSettings(data.cameras);
        }

        if (data.notifications) {
            applyNotificationSettings(data.notifications);
        }

        settingsLoaded = true;
    } catch (err) {
        console.error("Failed to load settings:", err);
    }
}

function applyCameraSettings(cameras) {
    const cards = document.querySelectorAll('.camera-card');
    cards.forEach((card, index) => {
        const cam = cameras[index];
        if (!cam) return;

        const toggle = card.querySelector('.camera-card-header .toggle-switch input');
        if (toggle && typeof cam.enabled === 'boolean') {
            toggle.checked = cam.enabled;
        }

        const select = card.querySelector('select');
        if (select && cam.resolution) {
            select.value = cam.resolution;
        }

        const fpsInput = card.querySelector('input[type="number"]');
        if (fpsInput && cam.fps) {
            fpsInput.value = cam.fps;
        }
    });
}

function applyNotificationSettings(notifications) {
    const cards = document.querySelectorAll('.notification-card');
    const mapping = [
        { key: 'desktop', index: 0 },
        { key: 'email', index: 1 },
        { key: 'sms', index: 2 },
        { key: 'sound', index: 3 },
        { key: 'daily', index: 4 },
        { key: 'security', index: 5 }
    ];

    mapping.forEach(item => {
        const card = cards[item.index];
        if (!card) return;
        const toggle = card.querySelector('.toggle-switch input');
        if (toggle && typeof notifications[item.key] === 'boolean') {
            toggle.checked = notifications[item.key];
        }
    });

    // Restore email recipients
    const emailRecipientsEl = document.getElementById('emailRecipients');
    if (emailRecipientsEl && notifications.email_recipients) {
        emailRecipientsEl.value = notifications.email_recipients;
    }
    const dailyRecipientsEl = document.getElementById('dailyReportRecipients');
    if (dailyRecipientsEl && notifications.daily_recipients) {
        dailyRecipientsEl.value = notifications.daily_recipients;
    }

    // Toggle email config visibility based on toggle state
    updateEmailConfigVisibility();
}

/* ==========================================
   THEME SWITCHING
========================================== */

document.querySelectorAll('.theme-card').forEach(card => {
    card.addEventListener('click', function() {
        const theme = this.dataset.theme;
        setTheme(theme);
    });
});

function setTheme(theme){
    if (!['dark', 'light', 'midnight'].includes(theme)) {
        theme = 'midnight';
    }
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
    const activeCard = document.querySelector(`.theme-card[data-theme="${theme}"]`);
    if(activeCard){
        activeCard.classList.add('active');
    }
    try {
        localStorage.setItem('sentinelx-theme', theme);
    } catch(e) {}
    showToast('Theme', `Switched to ${theme.charAt(0).toUpperCase() + theme.slice(1)} theme`, 'info');
}

/* ==========================================
   SAVE SETTINGS
========================================== */

async function saveAllSettings(){
    const profileName = document.getElementById("profileName")?.value || "";
    const profileEmail = document.getElementById("profileEmail")?.value || "";

    if (!profileName.trim()) {
        showToast('Settings', 'Name cannot be empty', 'danger');
        return;
    }

    if (!isValidEmail(profileEmail)) {
        showToast('Settings', 'Please enter a valid email address', 'danger');
        return;
    }

    const cameras = Array.from(document.querySelectorAll('.camera-card')).map(card => {
        const fpsInput = card.querySelector('input[type="number"]');
        const fps = parseInt(fpsInput?.value || '30', 10);
        if (isNaN(fps) || fps < 1 || fps > 60) {
            showToast('Settings', `Invalid FPS on ${card.querySelector('h4')?.textContent || 'camera'}`, 'danger');
            return null;
        }
        return {
            name: card.querySelector('h4')?.textContent || "",
            enabled: card.querySelector('.camera-card-header .toggle-switch input')?.checked || false,
            resolution: card.querySelector('select')?.value || "",
            fps: fps
        };
    }).filter(Boolean);

    if (cameras.length === 0) {
        showToast('Settings', 'No valid camera settings to save', 'danger');
        return;
    }

    const notifications = {
        desktop: document.querySelector('.notification-card:nth-child(1) .toggle-switch input')?.checked || false,
        email: document.getElementById('toggleEmailAlerts')?.checked || false,
        sms: document.querySelector('.notification-card:nth-child(3) .toggle-switch input')?.checked || false,
        sound: document.querySelector('.notification-card:nth-child(4) .toggle-switch input')?.checked || false,
        daily: document.getElementById('toggleDailyReports')?.checked || false,
        security: document.querySelector('.notification-card:nth-child(6) .toggle-switch input')?.checked || false
    };

    // Collect and validate email recipients
    const emailRecipientsText = document.getElementById('emailRecipients')?.value || '';
    const dailyRecipientsText = document.getElementById('dailyReportRecipients')?.value || '';

    if (notifications.email && emailRecipientsText.trim() && !isValidEmails(emailRecipientsText)) {
        showToast('Settings', 'Invalid email address in Email Alerts recipients', 'danger');
        return;
    }
    if (notifications.daily && dailyRecipientsText.trim() && !isValidEmails(dailyRecipientsText)) {
        showToast('Settings', 'Invalid email address in Daily Reports recipients', 'danger');
        return;
    }

    if (notifications.email && !emailRecipientsText.trim()) {
        showToast('Settings', 'Email Alerts is enabled but no recipients specified', 'danger');
        return;
    }
    if (notifications.daily && !dailyRecipientsText.trim()) {
        showToast('Settings', 'Daily Reports is enabled but no recipients specified', 'danger');
        return;
    }

    notifications.email_recipients = emailRecipientsText.trim();
    notifications.daily_recipients = dailyRecipientsText.trim();

    const settingsPayload = {
        profile: { name: profileName, email: profileEmail },
        theme: currentTheme,
        cameras: cameras,
        notifications: notifications
    };

    try {
        const [settingsRes, cameraRes, notifRes] = await Promise.all([
            fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ key: "general", value: { profile: settingsPayload.profile, theme: settingsPayload.theme } })
            }),
            fetch("/api/settings/camera", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ cameras: settingsPayload.cameras })
            }),
            fetch("/api/settings/notifications", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ notifications: settingsPayload.notifications })
            })
        ]);

        const settingsOk = settingsRes.ok;
        const cameraOk = cameraRes.ok;
        const notifOk = notifRes.ok;

        if (settingsOk && cameraOk && notifOk) {
            showToast('Settings', 'Settings saved successfully', 'success');
        } else {
            const errors = [];
            if (!settingsOk) errors.push("profile/theme");
            if (!cameraOk) errors.push("camera");
            if (!notifOk) errors.push("notifications");
            showToast('Settings', `Failed to save: ${errors.join(', ')}`, 'danger');
        }

    } catch (err) {
        console.error("Save settings error:", err);
        showToast('Settings', 'Network error while saving settings', 'danger');
    }
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidEmails(text) {
    if (!text || !text.trim()) return true; // Empty is valid (no recipients required)
    const emails = parseEmailList(text);
    return emails.length > 0 && emails.every(email => isValidEmail(email));
}

function parseEmailList(text) {
    if (!text || !text.trim()) return [];
    return text.split(/[,\n]+/)
        .map(e => e.trim())
        .filter(e => e.length > 0);
}

function updateEmailConfigVisibility() {
    // Email Alerts card
    const emailToggle = document.getElementById('toggleEmailAlerts');
    const emailConfig = document.getElementById('emailAlertsConfig');
    if (emailToggle && emailConfig) {
        emailConfig.style.display = emailToggle.checked ? 'flex' : 'none';
    }

    // Daily Reports card
    const dailyToggle = document.getElementById('toggleDailyReports');
    const dailyConfig = document.getElementById('dailyReportsConfig');
    if (dailyToggle && dailyConfig) {
        dailyConfig.style.display = dailyToggle.checked ? 'flex' : 'none';
    }
}

/* ==========================================
   SYSTEM ACTIONS
========================================== */

async function restartEngine(){
    try {
        const response = await fetch("/api/system/restart", { method: "POST" });
        const data = await response.json();
        if (data.success) {
            showToast('System', 'AI Engine restarted successfully', 'success');
        } else {
            showToast('System', data.error || 'Failed to restart engine', 'danger');
        }
    } catch (err) {
        showToast('System', 'Backend integration pending', 'danger');
    }
}

async function backupDatabase(){
    try {
        showToast('Database', 'Creating backup...', 'info');
        const response = await fetch("/api/system/backup", { method: "POST" });
        const data = await response.json();
        if (data.success) {
            showToast('Database', `Backup completed: ${data.path}`, 'success');
        } else {
            showToast('Database', data.error || 'Backup failed', 'danger');
        }
    } catch (err) {
        showToast('Database', 'Backend integration pending', 'danger');
    }
}

async function clearOldEvidence(){
    if(!confirm('Are you sure you want to clear old evidence? This action cannot be undone.')) return;

    try {
        showToast('Storage', 'Clearing old evidence...', 'info');
        const response = await fetch("/api/system/cleanup", { method: "POST" });
        const data = await response.json();
        if (data.success) {
            showToast('Storage', `Cleared ${data.deleted} old evidence items`, 'success');
        } else {
            showToast('Storage', data.error || 'Cleanup failed', 'danger');
        }
    } catch (err) {
        showToast('Storage', 'Backend integration pending', 'danger');
    }
}

/* ==========================================
   TOGGLE SWITCHES
========================================== */

document.querySelectorAll('.toggle-switch input').forEach(toggle => {
    toggle.addEventListener('change', function() {
        const label = this.closest('.toggle-switch')?.previousElementSibling?.textContent || "Setting";
        const state = this.checked ? 'enabled' : 'disabled';
        console.log(`${label}: ${state}`);
    });
});

// Email config visibility toggles
const emailAlertToggle = document.getElementById('toggleEmailAlerts');
if (emailAlertToggle) {
    emailAlertToggle.addEventListener('change', updateEmailConfigVisibility);
}
const dailyReportToggle = document.getElementById('toggleDailyReports');
if (dailyReportToggle) {
    dailyReportToggle.addEventListener('change', updateEmailConfigVisibility);
}

// Initialize email config visibility on page load
updateEmailConfigVisibility();

/* ==========================================
   CAMERA SETTINGS
========================================== */

document.querySelectorAll('.camera-card select, .camera-card input[type="number"]').forEach(input => {
    input.addEventListener('change', function() {
        const card = this.closest('.camera-card');
        const cameraName = card?.querySelector('h4')?.textContent || "Camera";
        const setting = this.tagName === 'SELECT' ? 'resolution' : 'fps';
        const value = this.value;
        console.log(`${cameraName} ${setting}: ${value}`);
    });
});

function restoreTheme(){
    try {
        const saved = localStorage.getItem('sentinelx-theme');
        if (saved && ['dark', 'light', 'midnight'].includes(saved)) {
            setTheme(saved);
        } else {
            setTheme('midnight');
        }
    } catch(e) {
        setTheme('midnight');
    }
}

/* ==========================================
    INIT
========================================== */

document.addEventListener('DOMContentLoaded', () => {
    restoreTheme();
    loadSettings();
});
