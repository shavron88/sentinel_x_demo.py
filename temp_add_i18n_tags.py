"""
Add data-i18n tags to all untagged text elements in landing.html
"""
import re

file_path = r'dashboard\templates\landing.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── HERO SECTION ───
# Line 388: "Live on 4 cameras right now" → needs data-i18n="hero.liveCameras"
content = content.replace(
    '<span class="pulse"></span> Live on 4 cameras right now',
    '<span class="pulse"></span> <span data-i18n="hero.liveCameras">Live on 4 cameras right now</span>'
)

# Line 389: Headline text (has <br> and span)
# "Don't just record what happened." and "Understand what's happening."
content = content.replace(
    '<h1 class="headline">Don\'t just record what happened.<br><span class="grad">Understand what\'s happening.</span></h1>',
    '<h1 class="headline" data-i18n="hero.title1">Don\'t just record what happened.<br><span class="grad" data-i18n="hero.title2">Understand what\'s happening.</span></h1>'
)

# Line 390: hero-copy
content = content.replace(
    '<p class="hero-copy">Sentinel-X turns your existing cameras into an intelligence layer — detecting, tracking, and scoring threats in real time, before they become incidents.</p>',
    '<p class="hero-copy" data-i18n="hero.subtitle">Sentinel-X turns your existing cameras into an intelligence layer — detecting, tracking, and scoring threats in real time, before they become incidents.</p>'
)

# Line 392: Get Started button
content = content.replace(
    '<a href="#capabilities" class="btn btn-primary btn-lg">Get Started</a>',
    '<a href="#capabilities" class="btn btn-primary btn-lg" data-i18n="hero.getStarted">Get Started</a>'
)

# Line 393: View Dashboard button
content = content.replace(
    '<a href="#dashboard" class="btn btn-ghost btn-lg">View Dashboard</a>',
    '<a href="#dashboard" class="btn btn-ghost btn-lg" data-i18n="hero.viewDashboard">View Dashboard</a>'
)

# ─── PROBLEM SECTION ───
# mlabel
content = content.replace(
    '<div class="mlabel">// 01 — the problem</div>',
    '<div class="mlabel" data-i18n="problem.label">// 01 — the problem</div>'
)
# Section title
content = content.replace(
    '<h2 class="section-title" style="margin-bottom:28px;">Traditional CCTV records. It doesn\'t understand.</h2>',
    '<h2 class="section-title" style="margin-bottom:28px;" data-i18n="problem.title">Traditional CCTV records. It doesn\'t understand.</h2>'
)

# ─── SOLUTION PIPELINE ───
# mlabel
content = content.replace(
    '<div class="mlabel">// 02 — the solution</div>',
    '<div class="mlabel" data-i18n="solution.label">// 02 — the solution</div>'
)
# Section title
content = content.replace(
    '<h2 class="section-title">From raw video to security intelligence</h2>',
    '<h2 class="section-title" data-i18n="solution.title">From raw video to security intelligence</h2>'
)
# Section subtitle
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable events.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="solution.desc">Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable events.</p>',
    1  # Only first occurrence
)

# Pipeline labels (uppercase → need to check if they match dict values)
# The EN dict has solution.pipe.camera as 'Camera Feed', but HTML has 'CAMERA'
# The plan says to pipe values to uppercase, so we need to update the EN dict
# For now, just add data-i18n tags with the current text
content = content.replace('><span class="pipe-label">CAMERA</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.camera">CAMERA</span></div>')
content = content.replace('><span class="pipe-label">AI VISION</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.vision">AI VISION</span></div>')
content = content.replace('><span class="pipe-label">DETECTION</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.detection">DETECTION</span></div>')
content = content.replace('><span class="pipe-label">TRACKING</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.tracking">TRACKING</span></div>')
content = content.replace('><span class="pipe-label">ANALYSIS</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.analysis">ANALYSIS</span></div>')
content = content.replace('><span class="pipe-label">THREAT</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.threat">THREAT</span></div>')
content = content.replace('><span class="pipe-label">EVIDENCE</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.evidence">EVIDENCE</span></div>')
content = content.replace('><span class="pipe-label">DASHBOARD</span></div>', '><span class="pipe-label" data-i18n="solution.pipe.dashboard">DASHBOARD</span></div>')

# ─── HOW IT WORKS ───
content = content.replace(
    '<div class="mlabel">// 03 — how it works</div>',
    '<div class="mlabel" data-i18n="how.label">// 03 — how it works</div>'
)
content = content.replace(
    '<h2 class="section-title">From camera to dashboard in seconds</h2>',
    '<h2 class="section-title" data-i18n="how.title">From camera to dashboard in seconds</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">A step-by-step look at how Sentinel-X processes camera feeds and delivers security intelligence.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="how.desc">A step-by-step look at how Sentinel-X processes camera feeds and delivers security intelligence.</p>',
    1  # Only first occurrence
)

# ─── CAPABILITIES ───
content = content.replace(
    '<div class="mlabel">// 04 — capabilities</div>',
    '<div class="mlabel" data-i18n="cap.label">// 04 — capabilities</div>'
)
content = content.replace(
    '<h2 class="section-title">What Sentinel-X detects</h2>',
    '<h2 class="section-title" data-i18n="cap.title">What Sentinel-X detects</h2>'
)
# Cap desc - need to be careful to only replace the first occurrence
cap_desc_old = '<p class="section-sub" style="margin-bottom:44px;">Powered by YOLO11 object detection and ByteTrack multi-object tracking, Sentinel-X supports a range of security-relevant detection scenarios.</p>'
cap_desc_new = '<p class="section-sub" style="margin-bottom:44px;" data-i18n="cap.desc">Powered by YOLO11 object detection and ByteTrack multi-object tracking, Sentinel-X supports a range of security-relevant detection scenarios.</p>'
content = content.replace(cap_desc_old, cap_desc_new, 1)

# Loitering card (line 511) - missing data-i18n tags
content = content.replace(
    '<div class="cap-title">Loitering Detection</div><div class="cap-desc">Flags individuals remaining in a monitored area beyond a defined time threshold.</div>',
    '<div class="cap-title" data-i18n="cap.loitering.title">Loitering Detection</div><div class="cap-desc" data-i18n="cap.loitering.desc">Flags individuals remaining in a monitored area beyond a defined time threshold.</div>'
)

# Cap alerts desc (line 516) - missing data-i18n tag
content = content.replace(
    '<div class="cap-desc">Severity-based alerting classifies events as Low, Medium, High, or Critical.</div></div><div class="cap-status"><span class="dot"></span>LIVE</div></div></div>',
    '<div class="cap-desc" data-i18n="cap.alerts.desc">Severity-based alerting classifies events as Low, Medium, High, or Critical.</div></div><div class="cap-status"><span class="dot"></span>LIVE</div></div></div>'
)

# ─── ADVANTAGES ───
content = content.replace(
    '<div class="mlabel">// 05 — advantages</div>',
    '<div class="mlabel" data-i18n="adv.badge">// 05 — advantages</div>'
)
content = content.replace(
    '<h2 class="section-title">Why Sentinel-X?</h2>',
    '<h2 class="section-title" data-i18n="adv.title">Why Sentinel-X?</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Practical benefits for security monitoring operations.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="adv.desc">Practical benefits for security monitoring operations.</p>',
    1
)

# ─── LIMITATIONS ───
content = content.replace(
    '<div class="mlabel">// 06 — responsible disclosure</div>',
    '<div class="mlabel" data-i18n="lim.badge">// 06 — responsible disclosure</div>'
)
content = content.replace(
    '<h2 class="section-title">Limitations &amp; responsible use</h2>',
    '<h2 class="section-title" data-i18n="lim.title">Limitations &amp; responsible use</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Transparency about what Sentinel-X can and cannot do. Understanding these limitations is important for effective deployment.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="lim.desc">Transparency about what Sentinel-X can and cannot do. Understanding these limitations is important for effective deployment.</p>',
    1
)

# ─── APPLICATIONS ───
content = content.replace(
    '<div class="mlabel">// 07 — potential applications</div>',
    '<div class="mlabel" data-i18n="use.badge">// 07 — potential applications</div>'
)
content = content.replace(
    '<h2 class="section-title">Who can use Sentinel-X?</h2>',
    '<h2 class="section-title" data-i18n="use.title">Who can use Sentinel-X?</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Sentinel-X is designed for environments where continuous camera monitoring adds real security value.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="use.desc">Sentinel-X is designed for environments where continuous camera monitoring adds real security value.</p>',
    1
)

# ─── DASHBOARD PREVIEW ───
content = content.replace(
    '<div class="mlabel">// 08 — dashboard preview</div>',
    '<div class="mlabel" data-i18n="preview.label">// 08 — dashboard preview</div>'
)
content = content.replace(
    '<h2 class="section-title">Your security command center</h2>',
    '<h2 class="section-title" data-i18n="preview.title">Your security command center</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends. Demo data shown below.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="preview.desc">A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends. Demo data shown below.</p>',
    1
)

# ─── SECURITY SECTION ───
content = content.replace(
    '<div class="mlabel">// 09 — security &amp; privacy</div>',
    '<div class="mlabel" data-i18n="sec.label">// 09 — security &amp; privacy</div>'
)
content = content.replace(
    '<h2 class="section-title">Built-in protections</h2>',
    '<h2 class="section-title" data-i18n="sec.title">Built-in protections</h2>',
    1
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Sentinel-X implements fundamental security controls for access management and data handling.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="sec.desc">Sentinel-X implements fundamental security controls for access management and data handling.</p>',
    1
)

# Security card titles and descs (these are in the sec.* section, not cap.*)
# Authentication
content = content.replace(
    '<div class="cap-title">Authentication</div><div class="cap-desc">Session-based authentication with configurable timeout. All users must sign in to access the dashboard.</div>',
    '<div class="cap-title" data-i18n="sec.auth.title">Authentication</div><div class="cap-desc" data-i18n="sec.auth.desc">Session-based authentication with configurable timeout. All users must sign in to access the dashboard.</div>'
)
# Protected Dashboard
content = content.replace(
    '<div class="cap-title">Protected Dashboard</div><div class="cap-desc">Every dashboard route is protected behind authentication. Unauthenticated visitors are redirected to sign in.</div>',
    '<div class="cap-title" data-i18n="sec.protected.title">Protected Dashboard</div><div class="cap-desc" data-i18n="sec.protected.desc">Every dashboard route is protected behind authentication. Unauthenticated visitors are redirected to sign in.</div>'
)
# Controlled Access
content = content.replace(
    '<div class="cap-title">Controlled Access</div><div class="cap-desc">CSRF token protection on state-changing operations, with rate limiting on authentication endpoints.</div>',
    '<div class="cap-title" data-i18n="sec.access.title">Controlled Access</div><div class="cap-desc" data-i18n="sec.access.desc">CSRF token protection on state-changing operations, with rate limiting on authentication endpoints.</div>'
)
# Evidence Management
content = content.replace(
    '<div class="cap-title">Evidence Management</div><div class="cap-desc">Event evidence is stored in a structured database with timestamps, camera references, and integrity hashing.</div>',
    '<div class="cap-title" data-i18n="sec.evidence.title">Evidence Management</div><div class="cap-desc" data-i18n="sec.evidence.desc">Event evidence is stored in a structured database with timestamps, camera references, and integrity hashing.</div>'
)
# Event History
content = content.replace(
    '<div class="cap-title">Event History</div><div class="cap-desc">A complete audit trail of detected events, with severity classification, camera source, and zone information.</div>',
    '<div class="cap-title" data-i18n="sec.history.title">Event History</div><div class="cap-desc" data-i18n="sec.history.desc">A complete audit trail of detected events, with severity classification, camera source, and zone information.</div>'
)
# Responsible AI
content = content.replace(
    '<div class="cap-title">Responsible AI</div><div class="cap-desc">AI detection results are shown with confidence scores. The system is designed to assist, not replace, human judgment.</div>',
    '<div class="cap-title" data-i18n="sec.ai.title">Responsible AI</div><div class="cap-desc" data-i18n="sec.ai.desc">AI detection results are shown with confidence scores. The system is designed to assist, not replace, human judgment.</div>'
)

# ─── TECHNOLOGY ───
content = content.replace(
    '<div class="mlabel">// 10 — technology</div>',
    '<div class="mlabel" data-i18n="tech.label">// 10 — technology</div>'
)
content = content.replace(
    '<h2 class="section-title">Under the hood</h2>',
    '<h2 class="section-title" data-i18n="tech.title">Under the hood</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:36px;">Sentinel-X is built with proven open-source technologies for AI-powered video analysis.</p>',
    '<p class="section-sub" style="margin-bottom:36px;" data-i18n="tech.desc">Sentinel-X is built with proven open-source technologies for AI-powered video analysis.</p>',
    1
)

# Tech chip names and roles
content = content.replace(
    '<div class="name">Python</div><div class="role">core runtime</div>',
    '<div class="name" data-i18n="tech.python">Python</div><div class="role" data-i18n="tech.python.role">core runtime</div>'
)
content = content.replace(
    '<div class="name">Flask</div><div class="role">web framework</div>',
    '<div class="name" data-i18n="tech.flask">Flask</div><div class="role" data-i18n="tech.flask.role">web framework</div>'
)
content = content.replace(
    '<div class="name">OpenCV</div><div class="role">video processing</div>',
    '<div class="name" data-i18n="tech.opencv">OpenCV</div><div class="role" data-i18n="tech.opencv.role">video processing</div>'
)
content = content.replace(
    '<div class="name">YOLO11</div><div class="role">object detection</div>',
    '<div class="name" data-i18n="tech.yolo">YOLO11</div><div class="role" data-i18n="tech.yolo.role">object detection</div>'
)
content = content.replace(
    '<div class="name">ByteTrack</div><div class="role">object tracking</div>',
    '<div class="name" data-i18n="tech.bytetrack">ByteTrack</div><div class="role" data-i18n="tech.bytetrack.role">object tracking</div>'
)
content = content.replace(
    '<div class="name">SQLite</div><div class="role">data storage</div>',
    '<div class="name" data-i18n="tech.sqlite">SQLite</div><div class="role" data-i18n="tech.sqlite.role">data storage</div>'
)
content = content.replace(
    '<div class="name">REST API</div><div class="role">integration</div>',
    '<div class="name" data-i18n="tech.restapi">REST API</div><div class="role">integration</div>'
)
content = content.replace(
    '<div class="name">JS / CSS</div><div class="role">dashboard UI</div>',
    '<div class="name">JS / CSS</div><div class="role" data-i18n="tech.jscss">dashboard UI</div>'
)

# ─── EVIDENCE FLOW ───
content = content.replace(
    '<div class="mlabel" style="justify-content:center;">// 11 — evidence handling</div>',
    '<div class="mlabel" style="justify-content:center;" data-i18n="evidence.label">// 11 — evidence handling</div>'
)
content = content.replace(
    '<h2 class="section-title" style="margin-left:auto;margin-right:auto;">How Sentinel-X handles evidence</h2>',
    '<h2 class="section-title" style="margin-left:auto;margin-right:auto;" data-i18n="evidence.title">How Sentinel-X handles evidence</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-left:auto;margin-right:auto;">From the moment something is detected to a fully audited record — every step is logged and traceable.</p>',
    '<p class="section-sub" style="margin-left:auto;margin-right:auto;" data-i18n="evidence.desc">From the moment something is detected to a fully audited record — every step is logged and traceable.</p>',
    1
)

# Evidence flow labels
content = content.replace('><span class="ev-label">DETECTION</span></div>', '><span class="ev-label" data-i18n="evidence.detection">DETECTION</span></div>')
content = content.replace('><span class="ev-label">EVENT</span></div>', '><span class="ev-label" data-i18n="evidence.event">EVENT</span></div>')
content = content.replace('><span class="ev-label">EVIDENCE</span></div>', '><span class="ev-label" data-i18n="evidence.evidence">EVIDENCE</span></div>')
content = content.replace('><span class="ev-label">HASH</span></div>', '><span class="ev-label" data-i18n="evidence.hash">HASH</span></div>')
content = content.replace('><span class="ev-label">STORAGE</span></div>', '><span class="ev-label" data-i18n="evidence.storage">STORAGE</span></div>')
content = content.replace('><span class="ev-label">AUDIT</span></div>', '><span class="ev-label" data-i18n="evidence.audit">AUDIT</span></div>')

# ─── FUTURE SECTION ───
content = content.replace(
    '<div class="mlabel">// 12 — future vision</div>',
    '<div class="mlabel" data-i18n="future.label">// 12 — future vision</div>'
)
content = content.replace(
    '<h2 class="section-title">What\'s next for Sentinel-X</h2>',
    '<h2 class="section-title" data-i18n="future.title">What\'s next for Sentinel-X</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:36px;">Items below are planned or conceptual — not part of the current MVP release.</p>',
    '<p class="section-sub" style="margin-bottom:36px;" data-i18n="future.comingSoon">Items below are planned or conceptual — not part of the current MVP release.</p>',
    1
)
content = content.replace(
    '<span class="coming-soon">PLANNED</span>',
    '<span class="coming-soon" data-i18n="future.planned">PLANNED</span>'
)
content = content.replace(
    '<h3>Sentinel-X Edge Box</h3>',
    '<h3 data-i18n="future.edgeBox">Sentinel-X Edge Box</h3>',
    1
)
content = content.replace(
    '<p>A dedicated edge-computing appliance designed to run Sentinel-X AI processing closer to camera infrastructure — reducing dependency on centralized computing and potentially improving deployment flexibility, latency, and bandwidth usage.</p>',
    '<p data-i18n="future.edgeDesc">A dedicated edge-computing appliance designed to run Sentinel-X AI processing closer to camera infrastructure — reducing dependency on centralized computing and potentially improving deployment flexibility, latency, and bandwidth usage.</p>',
    1
)

# Edge flow nodes
content = content.replace(
    '<span class="edge-node">CCTV Cameras</span>',
    '<span class="edge-node" data-i18n="future.cctv">CCTV Cameras</span>'
)
content = content.replace(
    '<span class="edge-node mid">Sentinel-X Edge Box</span>',
    '<span class="edge-node mid" data-i18n="future.edgeNode">Sentinel-X Edge Box</span>'
)
content = content.replace(
    '<span class="edge-node">AI Processing</span>',
    '<span class="edge-node" data-i18n="future.aiProc">AI Processing</span>'
)
content = content.replace(
    '<span class="edge-node">Alerts &amp; Events</span>',
    '<span class="edge-node" data-i18n="future.alerts">Alerts &amp; Events</span>'
)
content = content.replace(
    '<span class="edge-node">Cloud Dashboard</span>',
    '<span class="edge-node" data-i18n="future.cloud">Cloud Dashboard</span>'
)
content = content.replace(
    '<p class="edge-note">// The Edge Box is planned future work. The current Sentinel-X release is a software-only platform.</p>',
    '<p class="edge-note" data-i18n="future.disclaimer">// The Edge Box is planned future work. The current Sentinel-X release is a software-only platform.</p>',
    1
)

# Roadmap tags
roadmap_items = [
    ('Advanced AI detection models', 'future.roadmap.0'),
    ('Expanded threat detection types', 'future.roadmap.1'),
    ('Hardware edge deployment', 'future.roadmap.2'),
    ('Additional system integrations', 'future.roadmap.3'),
    ('Expanded analytics & reporting', 'future.roadmap.4'),
    ('Authorized identity integrations', 'future.roadmap.5'),
]
for text, key in roadmap_items:
    content = content.replace(
        f'<div class="roadmap-tag"><span class="badge">PLANNED</span>{text}</div>',
        f'<div class="roadmap-tag"><span class="badge" data-i18n="future.planned">PLANNED</span><span data-i18n="{key}">{text}</span></div>'
    )

# ─── FAQ SECTION ───
content = content.replace(
    '<div class="mlabel">// 13 — frequently asked</div>',
    '<div class="mlabel" data-i18n="faq.label">// 13 — frequently asked</div>'
)
content = content.replace(
    '<h2 class="section-title">Common questions</h2>',
    '<h2 class="section-title" data-i18n="faq.title">Common questions</h2>'
)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:36px;">Straight answers, including where Sentinel-X currently falls short.</p>',
    '<p class="section-sub" style="margin-bottom:36px;" data-i18n="faq.desc">Straight answers, including where Sentinel-X currently falls short.</p>',
    1
)

# FAQ items
faq_items = [
    ('Do I need to buy new cameras?', 'No. Sentinel-X works with what you already have — webcam, IP camera, RTSP streams, or video files. It\'s an intelligence layer on top of existing infrastructure, not a hardware replacement.'),
    ('How accurate is the detection?', 'Detection uses YOLO11, but no AI system is infallible — false positives and false negatives happen. Accuracy depends on camera quality, resolution, angle, and lighting conditions, which the system reports as confidence scores per detection.'),
    ('What happens when it detects something?', 'Detections become events that are severity-classified (Low through Critical), trigger real-time alerts on the dashboard, and automatically capture evidence screenshots with metadata. You review and investigate everything from the web dashboard.'),
    ('Does it scale to multiple cameras?', 'Yes. Multi-Camera Monitoring gives you a centralized view and processing of multiple feeds from a single dashboard, with Object Tracking maintaining consistent IDs across cameras.'),
    ('Is Sentinel-X production-ready?', 'It\'s a functional MVP (Version 1.0) — the pipeline runs end to end, but the limitations are real: AI detection can miss events, network reliability matters, and real-time throughput needs GPU acceleration. It\'s ready to evaluate, not yet ready for blind trust.'),
    ('What\'s Sentinel-X built on?', 'Python, Flask, OpenCV, and YOLO11 for detection with ByteTrack for object tracking. The dashboard is a web interface you access from any modern browser.')
]
for i, (q, a) in enumerate(faq_items, 1):
    content = content.replace(
        f'>Do I need to buy new cameras?<' if i == 1 else f'>{q}<',
        f' data-i18n="faq.{i}.q">{q}<',
        1
    )
    content = content.replace(a, f'<span data-i18n="faq.{i}.a">{a}</span>', 1)

# ─── FINAL CTA ───
content = content.replace(
    '<h2>Your cameras already see everything.<br><span class="soft">Sentinel-X helps you understand what matters.</span></h2>',
    '<h2 data-i18n="cta.title1">Your cameras already see everything.<br><span class="soft" data-i18n="cta.title2">Sentinel-X helps you understand what matters.</span></h2>'
)

# ─── FOOTER ───
content = content.replace(
    '<div class="footer-brand">',
    '<div class="footer-brand" data-i18n="footer.brand">'
)
content = content.replace(
    '<p>AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.</p>',
    '<p data-i18n="footer.desc">AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.</p>'
)
# Footer column headers
content = content.replace('<h4>Product</h4>', '<h4 data-i18n="footer.col.product">Product</h4>')
content = content.replace('<h4>Technology</h4>', '<h4 data-i18n="footer.col.technology">Technology</h4>')
content = content.replace('<h4>Project</h4>', '<h4 data-i18n="footer.col.project">Project</h4>')

# Footer links
content = content.replace(
    '<a href="#security">Responsible AI</a>',
    '<a href="#security" data-i18n="footer.link.responsibleAI">Responsible AI</a>'
)
content = content.replace(
    '<a href="#limitations">Limitations &amp; Use</a>',
    '<a href="#limitations" data-i18n="footer.link.limitations">Limitations &amp; Use</a>'
)

# Footer bottom text
content = content.replace(
    '<span>Sentinel-X AI Edge Surveillance Platform · Version 1.0</span>',
    '<span data-i18n="footer.text">Sentinel-X AI Edge Surveillance Platform · Version 1.0</span>'
)
content = content.replace(
    '<span>Built with Python, Flask, OpenCV, YOLO11</span>',
    '<span data-i18n="footer.builtWith">Built with Python, Flask, OpenCV, YOLO11</span>'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("All data-i18n tags added to landing.html")
