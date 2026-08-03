/* ==========================================
   GLOBAL LOADING SYSTEM
   Skeleton loaders, spinners, fade animations, empty states
========================================== */

// =========================
// PAGE LOADING
// =========================

function showPageLoading() {

    const overlay = document.getElementById("pageLoadingOverlay");

    if (overlay) {

        overlay.classList.remove("hidden");

    }

}

function hidePageLoading() {

    const overlay = document.getElementById("pageLoadingOverlay");

    if (overlay) {

        overlay.classList.add("hidden");

        setTimeout(() => {

            overlay.style.display = "none";

        }, 500);

    }

}

// =========================
// SKELETON LOADERS
// =========================

function showSkeletonCards(containerId, count = 6) {

    const container = document.getElementById(containerId);

    if (!container) return;

    container.innerHTML = "";

    for (let i = 0; i < count; i++) {

        const card = createSkeletonCard(i);

        container.appendChild(card);

    }

}

function createSkeletonCard(delay = 0) {

    const card = document.createElement("div");

    card.className = "skeleton-card";

    card.style.animationDelay = `${delay * 0.1}s`;

    card.innerHTML = `

        <div class="skeleton skeleton-image"></div>

        <div class="skeleton skeleton-title"></div>

        <div class="skeleton skeleton-text h100"></div>

        <div class="skeleton skeleton-text short"></div>

    `;

    return card;

}

function showSkeletonRows(containerId, count = 5) {

    const container = document.getElementById(containerId);

    if (!container) return;

    container.innerHTML = "";

    for (let i = 0; i < count; i++) {

        const row = document.createElement("div");

        row.className = "skeleton-row";

        row.style.animationDelay = `${i * 0.1}s`;

        row.innerHTML = `

            <div class="skeleton skeleton-avatar"></div>

            <div class="skeleton-content">

                <div class="skeleton skeleton-line h70"></div>

                <div class="skeleton skeleton-line h100"></div>

                <div class="skeleton skeleton-line h50"></div>

            </div>

        `;

        container.appendChild(row);

    }

}

function showSkeletonTable(containerId, rows = 5) {

    const container = document.getElementById(containerId);

    if (!container) return;

    container.innerHTML = "";

    for (let i = 0; i < rows; i++) {

        const row = document.createElement("div");

        row.className = "skeleton-table-row";

        row.style.animationDelay = `${i * 0.05}s`;

        row.innerHTML = `

            <div class="skeleton skeleton-cell w30"></div>

            <div class="skeleton skeleton-cell w20"></div>

            <div class="skeleton skeleton-cell w40"></div>

        `;

        container.appendChild(row);

    }

}

// =========================
// EMPTY STATES
// =========================

function showEmptyState(containerId, title, description, actions = []) {

    const container = document.getElementById(containerId);

    if (!container) return;

    const actionsHtml = actions.map(action => {

        return `

            <button class="btn ${action.class || "btn-primary"}" onclick="${action.onclick}">

                ${action.icon ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">${action.icon}</svg>` : ""}

                ${action.label}

            </button>

        `;

    }).join("");

    container.innerHTML = `

        <div class="empty-state fade-in">

            <div class="empty-state-icon">

                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">

                    <rect x="3" y="3" width="18" height="18" rx="2"></rect>

                    <circle cx="8.5" cy="8.5" r="1.5"></circle>

                    <path d="M21 15l-5-5L11 19"></path>

                </svg>

            </div>

            <h3 class="empty-state-title">${title}</h3>

            <p class="empty-state-description">${description}</p>

            <div class="empty-state-actions">

                ${actionsHtml}

            </div>

        </div>

    `;

}

// =========================
// FADE UTILITIES
// =========================

function fadeIn(element, duration = 500) {

    element.style.opacity = "0";

    element.style.transform = "translateY(10px)";

    element.style.transition = `opacity ${duration}ms ease, transform ${duration}ms ease`;

    requestAnimationFrame(() => {

        element.style.opacity = "1";

        element.style.transform = "translateY(0)";

    });

}

function fadeOut(element, duration = 300) {

    element.style.transition = `opacity ${duration}ms ease`;

    element.style.opacity = "0";

    setTimeout(() => {

        element.style.display = "none";

    }, duration);

}

function staggerFadeIn(elements, baseDelay = 0) {

    elements.forEach((el, index) => {

        el.style.opacity = "0";

        el.style.transform = "translateY(10px)";

        el.style.transition = "opacity .4s ease, transform .4s ease";

        setTimeout(() => {

            el.style.opacity = "1";

            el.style.transform = "translateY(0)";

        }, baseDelay + index * 50);

    });

}

// =========================
// LOADING STATE MANAGEMENT
// =========================

const LoadingState = {

    active: false,

    set(active) {

        this.active = active;

        document.body.style.cursor = active ? "wait" : "";

    },

    start() {

        this.set(true);

    },

    stop() {

        this.set(false);

    }

};

// =========================
// INTERSECTION OBSERVER FOR ANIMATIONS
// =========================

function initScrollAnimations(selector = ".fade-in") {

    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                entry.target.classList.add("visible");

                observer.unobserve(entry.target);

            }

        });

    }, {

        threshold: 0.1,

        rootMargin: "0px 0px -50px 0px"

    });

    document.querySelectorAll(selector).forEach(el => {

        observer.observe(el);

    });

}

// =========================
// INIT
// =========================

document.addEventListener("DOMContentLoaded", () => {

    hidePageLoading();

    initScrollAnimations();

});

// Hide loading on window load as fallback

window.addEventListener("load", () => {

    hidePageLoading();

});
