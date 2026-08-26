let replayData = null;
let currentIndex = 0;
let isPlaying = false;
let playInterval = null;

async function loadReplay() {
    const video = document.getElementById("incidentVideo");
    const timelineControls = document.getElementById("timelineControls");
    const empty = document.getElementById("emptyState");
    
    if (!video) return;
    
    showSkeletonCards("timelineControls", 3);
    
    try {
        const eventId = new URLSearchParams(window.location.search).get('event') || '1';
        const response = await fetch(`/api/replay/event/${eventId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success || !data.replay) {
            showReplayUnavailable("No replay data found for this incident.");
            return;
        }
        
        replayData = data.replay;
        const imagePath = replayData.image_path || replayData.metadata?.image_path || "";
        
        // Populate incident summary with real backend data
        const cameraEl = document.getElementById("replayCamera");
        const eventEl = document.getElementById("replayEvent");
        const confidenceEl = document.getElementById("replayConfidence");
        const durationEl = document.getElementById("replayDuration");
        const timeEl = document.getElementById("replayTime");
        const statusEl = document.getElementById("replayStatus");
        
        if (cameraEl) cameraEl.textContent = replayData.camera || "Unknown";
        if (eventEl) eventEl.textContent = replayData.event_type || "Unknown Event";
        if (confidenceEl) confidenceEl.textContent = replayData.confidence ? `${replayData.confidence}%` : "--";
        if (durationEl) durationEl.textContent = replayData.duration ? `${replayData.duration} seconds` : "--";
        if (timeEl) timeEl.textContent = replayData.timestamp ? new Date(replayData.timestamp).toLocaleTimeString() : "--";
        if (statusEl) statusEl.textContent = replayData.severity || "Unknown";
        
        if (imagePath && imagePath.includes('.mp4')) {
            video.querySelector('source').src = imagePath;
            video.load();
            video.poster = "";
        } else if (imagePath) {
            video.querySelector('source').src = "";
            video.poster = imagePath;
            video.removeAttribute('poster');
            video.poster = imagePath;
        } else {
            showReplayUnavailable("No video or image evidence available for this incident.");
            return;
        }
        
        video.style.display = "block";
        if (timelineControls) timelineControls.style.display = "flex";
        if (empty) empty.style.display = "none";
        
    } catch (err) {
        console.error("Failed to load replay:", err);
        showReplayUnavailable("Unable to load replay data. The backend could not be reached.");
    }
}

function showReplayError(message) {
    const video = document.getElementById("incidentVideo");
    const timelineControls = document.getElementById("timelineControls");
    const empty = document.getElementById("emptyState");
    
    if (video) {
        video.style.display = "none";
        video.querySelector('source').src = "";
    }
    if (timelineControls) timelineControls.style.display = "none";
    if (empty) {
        empty.style.display = "flex";
        empty.innerHTML = `
            <div style="text-align:center;padding:60px 20px;">
                <div style="font-size:48px;margin-bottom:16px;opacity:0.6;">⚠️</div>
                <h3 style="color:#e2e8f0;margin:0 0 8px 0;">Unable to Load Replay</h3>
                <p style="color:#94a3b8;margin:0 0 20px 0;">${escapeHtml(message)}</p>
                <button class="btn btn-secondary" onclick="loadReplay()">Retry</button>
            </div>
        `;
    }
}

function showReplayUnavailable(message) {
    const video = document.getElementById("incidentVideo");
    const timelineControls = document.getElementById("timelineControls");
    const empty = document.getElementById("emptyState");
    
    if (video) {
        video.style.display = "none";
        video.querySelector('source').src = "";
    }
    if (timelineControls) timelineControls.style.display = "none";
    if (empty) {
        empty.style.display = "flex";
        empty.innerHTML = `
            <div style="text-align:center;padding:60px 20px;">
                <div style="font-size:48px;margin-bottom:16px;opacity:0.6;">🎬</div>
                <h3 style="color:#e2e8f0;margin:0 0 8px 0;">No Replay Available</h3>
                <p style="color:#94a3b8;margin:0 0 20px 0;">${escapeHtml(message)}</p>
                <button class="btn btn-secondary" onclick="history.back()">Back</button>
            </div>
        `;
    }
}

function togglePlay() {
    const video = document.getElementById("incidentVideo");
    if (!video) return;
    
    if (video.paused) {
        video.play();
        isPlaying = true;
    } else {
        video.pause();
        isPlaying = false;
    }
}

function skipBack() {
    const video = document.getElementById("incidentVideo");
    if (video) video.currentTime = Math.max(0, video.currentTime - 10);
}

function skipForward() {
    const video = document.getElementById("incidentVideo");
    if (video) video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

loadReplay();