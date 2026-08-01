let notifications = [];

// =========================
// TOAST
// =========================

function showToast(title, message, type = "info") {

    const icons = {

        success: "✅",
        warning: "⚠️",
        danger: "🚨",
        info: "ℹ️"

    };

    const toast = document.createElement("div");

    toast.className = `toast ${type}`;

    toast.innerHTML = `

        <div class="toast-icon">

            ${icons[type]}

        </div>

        <div>

            <div class="toast-title">

                ${title}

            </div>

            <div class="toast-message">

                ${message}

            </div>

        </div>

    `;

    const toastContainer = document.getElementById("toast-container");

    if (toastContainer) {

        toastContainer.prepend(toast);

    }

    // -------------------------
    // Save notification history
    // -------------------------

    notifications.unshift({

        title: title,

        message: message,

        time: new Date().toLocaleTimeString()

    });

    if (notifications.length > 20) {

        notifications.pop();

    }

    updateNotifications();

    setTimeout(() => {

        toast.style.animation = "fadeOut .4s forwards";

    }, 4500);

    setTimeout(() => {

        toast.remove();

    }, 5000);

}

// =========================
// Notification Panel
// =========================

function updateNotifications() {

    const list = document.getElementById("notification-list");
    const count = document.getElementById("notification-count");

    if (!list || !count) return;

    count.innerText = notifications.length;

    if (notifications.length === 0) {

        list.innerHTML = "<p>No Notifications</p>";

        return;

    }

    let html = "";

    notifications.forEach(item => {

        html += `

        <div class="notification-item">

            <strong>${item.title}</strong>

            <p>${item.message}</p>

            <small>${item.time}</small>

        </div>

        `;

    });

    list.innerHTML = html;

}

// =========================
// Toggle Notification Panel
// =========================

document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("notification-btn");
    const panel = document.getElementById("notification-panel");

    if (!btn || !panel) return;

    btn.addEventListener("click", () => {

        panel.style.display =
            panel.style.display === "block"
            ? "none"
            : "block";

    });

});

document.querySelector(".snapshot-action")?.addEventListener("click",()=>{

    showToast(

        "Snapshot",

        "Manual snapshot captured.",

        "success"

    );

});

document.querySelector(".record-action")?.addEventListener("click",()=>{

    showToast(

        "Recording",

        "Recording started.",

        "info"

    );

});

document.querySelector(".alarm-action")?.addEventListener("click",()=>{

    showToast(

        "Emergency",

        "Alarm triggered.",

        "danger"

    );

});

document.querySelector(".report-action")?.addEventListener("click",()=>{

    window.location.href="/reports";

});

document.querySelector(".refresh-action")?.addEventListener("click",()=>{

    location.reload();

});

document.querySelector(".settings-action")?.addEventListener("click",()=>{

    window.location.href="/settings";

}); 