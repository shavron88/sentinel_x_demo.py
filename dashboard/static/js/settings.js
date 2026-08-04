/* ==========================================
   SETTINGS PAGE
========================================== */

let currentTheme = 'dark';

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

    currentTheme = theme;

    document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));

    const activeCard = document.querySelector(`.theme-card[data-theme="${theme}"]`);

    if(activeCard){

        activeCard.classList.add('active');

    }

    showToast('Theme', `Switched to ${theme.charAt(0).toUpperCase() + theme.slice(1)} theme`, 'info');

}

/* ==========================================
   SAVE SETTINGS
========================================== */

function saveAllSettings(){

    const profileName = document.getElementById("profileName")?.value || "";

    const profileEmail = document.getElementById("profileEmail")?.value || "";

    const settings = {

        profile: {

            name: profileName,

            email: profileEmail

        },

        theme: currentTheme,

        cameras: Array.from(document.querySelectorAll('.camera-card')).map(card => ({

            name: card.querySelector('h4')?.textContent || "",

            enabled: card.querySelector('.camera-card-header .toggle-switch input')?.checked || false,

            resolution: card.querySelector('select')?.value || "",

            fps: card.querySelector('input[type="number"]')?.value || 30

        })),

        notifications: {

            desktop: document.querySelector('.notification-card:nth-child(1) .toggle-switch input')?.checked || false,

            email: document.querySelector('.notification-card:nth-child(2) .toggle-switch input')?.checked || false,

            sms: document.querySelector('.notification-card:nth-child(3) .toggle-switch input')?.checked || false,

            sound: document.querySelector('.notification-card:nth-child(4) .toggle-switch input')?.checked || false,

            daily: document.querySelector('.notification-card:nth-child(5) .toggle-switch input')?.checked || false,

            security: document.querySelector('.notification-card:nth-child(6) .toggle-switch input')?.checked || false

        }

    };

    console.log("Saving settings:", settings);

    showToast('Settings', 'Settings saved successfully', 'success');

}

/* ==========================================
   SYSTEM ACTIONS
========================================== */

function restartEngine(){

    showToast('System', 'Restarting AI Engine...', 'info');

    setTimeout(() => {

        showToast('System', 'AI Engine restarted successfully', 'success');

    }, 2000);

}

function backupDatabase(){

    showToast('Database', 'Creating backup...', 'info');

    setTimeout(() => {

        showToast('Database', 'Backup completed successfully', 'success');

    }, 1500);

}

function clearOldEvidence(){

    if(confirm('Are you sure you want to clear old evidence? This action cannot be undone.')){

        showToast('Storage', 'Clearing old evidence...', 'info');

        setTimeout(() => {

            showToast('Storage', 'Old evidence cleared successfully', 'success');

        }, 1500);

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

/* ==========================================
   INIT
========================================== */

document.addEventListener('DOMContentLoaded', () => {

    const savedTheme = localStorage.getItem('sentinelx_theme') || 'dark';

    setTheme(savedTheme);

});
