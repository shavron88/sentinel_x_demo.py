import re

with open('dashboard/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the entire LIVE CAMERAS section (lines 99-413)
start_marker = '<!-- ================= LIVE CAMERAS (FULL WIDTH BAND) ================= -->'
end_marker = '<!-- ================= MONITORING TWO-COLUMN ================= -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    replacement = '''<!-- ================= LIVE CAMERAS LINK SECTION ================= -->
<section class="live-cameras-link-section">
    <div class="live-cameras-link-card">
        <div class="live-cameras-link-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                <circle cx="12" cy="13" r="4"></circle>
            </svg>
        </div>
        <div class="live-cameras-link-content">
            <h2>Live Camera Wall</h2>
            <p>View all camera streams together in a unified multi-camera grid. Click any camera to open its full view with AI detection, FPS, and controls.</p>
            <div class="live-cameras-link-meta">
                <span id="kpi-cameras-link">--</span>
                <span class="live-cameras-link-total" id="kpi-cameras-total-link">/--</span>
                <span class="live-cameras-link-status" id="kpi-cameras-status-link">Checking</span>
            </div>
        </div>
        <a href="/cameras_wall" class="live-cameras-link-btn">
            <span>Open Camera Wall</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 3h6v6"></path>
                <path d="M10 14 21 3"></path>
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            </svg>
        </a>
    </div>
</section>

'''
    content = content[:start_idx] + replacement + content[end_idx:]
    
    with open('dashboard/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Successfully removed camera cards section')
else:
    print('Markers not found')