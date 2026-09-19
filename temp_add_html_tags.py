"""
Add data-i18n tags to landing.html
Uses precise string replacements for each element
"""
import re

file_path = r'dashboard\templates\landing.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # ─── NAVBAR ───
    # Logo text - Sentinel-X already has span, just the "Sentinel" part
    # Nav links already tagged
    
    # ─── HERO ───
    # Eyebrow text
    ('<span class="pulse"></span> Live on 4 cameras right now</span>',
     '<span class="pulse"></span> <span data-i18n="hero.liveCameras">Live on 4 cameras right now</span></span>'),
    
    # Headline
    ('<h1 class="headline">Don\'t just record what happened.<br><span class="grad">Understand what\'s happening.</span></h1>',
     '<h1 class="headline" data-i18n="hero.title1">Don\'t just record what happened.<br><span class="grad" data-i18n="hero.title2">Understand what\'s happening.</span></h1>'),
    
    # Hero copy
    ('<p class="hero-copy">Sentinel-X turns your existing cameras into an intelligence layer — detecting, tracking, and scoring threats in real time, before they become incidents.</p>',
     '<p class="hero-copy" data-i18n="hero.subtitle">Sentinel-X turns your existing cameras into an intelligence layer — detecting, tracking, and scoring threats in real time, before they become incidents.</p>'),
    
    # Hero CTAs
    ('<a href="#capabilities" class="btn btn-primary btn-lg">Get Started</a>',
     '<a href="#capabilities" class="btn btn-primary btn-lg" data-i18n="hero.getStarted">Get Started</a>'),
    ('<a href="#dashboard" class="btn btn-ghost btn-lg">View Dashboard</a>',
     '<a href="#dashboard" class="btn btn-ghost btn-lg" data-i18n="hero.viewDashboard">View Dashboard</a>'),
    
    # Stage title
    ('<span class="stage-title">Cam_02 — Parking Entrance</span>',
     '<span class="stage-title" data-i18n="preview.camera01">Cam_02 — Parking Entrance</span>'),
    
    # Stage live indicator
    ('<span class="stage-live"><span class="dot"></span>LIVE DETECTION</span>',
     '<span class="stage-live"><span class="dot"></span><span data-i18n="status.liveDetection">LIVE DETECTION</span></span>'),
    
    # HUD top
    ('<span>REC ● 00:14:32</span><span>YOLO11 · 92.5% CONF</span>',
     '<span>REC ● 00:14:32</span><span data-i18n="status.hudInfo">YOLO11 · 92.5% CONF</span>'),
    
    # Stage footer
    ('<span>Demo visualization — illustrative detection data</span>',
     '<span data-i18n="status.demoViz">Demo visualization — illustrative detection data</span>'),
    ('<span><span class="dot" style="background:var(--mint)"></span>Tracking active</span>',
     '<span><span class="dot" style="background:var(--mint)"></span><span data-i18n="status.trackingActive">Tracking active</span></span>'),
    ('<span><span class="dot" style="background:var(--accent)"></span>4/4 cameras online</span>',
     '<span><span class="dot" style="background:var(--accent)"></span><span data-i18n="status.camerasOnline">4/4 cameras online</span></span>'),
]

# Apply replacements
for old, new in replacements:
    if old in content:
        content = content.replace(old, new, 1)
        print(f"  Replaced: {old[:50]}...")
    else:
        print(f"  NOT FOUND: {old[:50]}...")

# ─── PROBLEM SECTION ───
# mlabel
content = content.replace(
    '<div class="mlabel">// 01 — the problem</div>',
    '<div class="mlabel" data-i18n="problem.label">// 01 — the problem</div>', 1)

# Section title
content = content.replace(
    '<h2 class="section-title" style="margin-bottom:28px;">Traditional CCTV records. It doesn\'t understand.</h2>',
    '<h2 class="section-title" style="margin-bottom:28px;" data-i18n="problem.title">Traditional CCTV records. It doesn\'t understand.</h2>', 1)

# Problem rows - add data-i18n tags
content = content.replace(
    '<h4>Continuous monitoring is impossible</h4>',
    '<h4 data-i18n="problem.1.title">Continuous monitoring is impossible</h4>', 1)
content = content.replace(
    '<p>Humans cannot effectively watch every camera feed at once. Attention fatigue leads to missed events.</p>',
    '<p data-i18n="problem.1.desc">Humans cannot effectively watch every camera feed at once. Attention fatigue leads to missed events.</p>', 1)
content = content.replace(
    '<h4>Critical events get missed</h4>',
    '<h4 data-i18n="problem.2.title">Critical events get missed</h4>', 1)
content = content.replace(
    '<p>Important security events can go unnoticed in real time, only discovered after damage has occurred.</p>',
    '<p data-i18n="problem.2.desc">Important security events can go unnoticed in real time, only discovered after damage has occurred.</p>', 1)
content = content.replace(
    '<h4>Footage review is inefficient</h4>',
    '<h4 data-i18n="problem.3.title">Footage review is inefficient</h4>', 1)
content = content.replace(
    '<p>Reviewing hours of recorded video to find one incident is slow and resource-intensive.</p>',
    '<p data-i18n="problem.3.desc">Reviewing hours of recorded video to find one incident is slow and resource-intensive.</p>', 1)
content = content.replace(
    '<h4>Reactive, not proactive</h4>',
    '<h4 data-i18n="problem.4.title">Reactive, not proactive</h4>', 1)
content = content.replace(
    '<p>CCTV captures what happened — it doesn\'t alert anyone while it\'s happening.</p>',
    '<p data-i18n="problem.4.desc">CCTV captures what happened — it doesn\'t alert anyone while it\'s happening.</p>', 1)

# Timeline viz labels
content = content.replace(
    '<span>CAM_02 — 8HR RECORDING</span>',
    '<span data-i18n="status.camLabel">CAM_02 — 8HR RECORDING</span>', 1)

# ─── SOLUTION PIPELINE ───
content = content.replace(
    '<div class="mlabel">// 02 — the solution</div>',
    '<div class="mlabel" data-i18n="solution.label">// 02 — the solution</div>', 1)
content = content.replace(
    '<h2 class="section-title">From raw video to security intelligence</h2>',
    '<h2 class="section-title" data-i18n="solution.title">From raw video to security intelligence</h2>', 1)

# ─── HOW IT WORKS ───
content = content.replace(
    '<div class="mlabel">// 03 — how it works</div>',
    '<div class="mlabel" data-i18n="how.label">// 03 — how it works</div>', 1)
content = content.replace(
    '<h2 class="section-title">From camera to dashboard in seconds</h2>',
    '<h2 class="section-title" data-i18n="how.title">From camera to dashboard in seconds</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">A step-by-step look at how Sentinel-X processes camera feeds and delivers security intelligence.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="how.desc">A step-by-step look at how Sentinel-X processes camera feeds and delivers security intelligence.</p>', 1)

# ─── CAPABILITIES ───
content = content.replace(
    '<div class="mlabel">// 04 — capabilities</div>',
    '<div class="mlabel" data-i18n="cap.label">// 04 — capabilities</div>', 1)
content = content.replace(
    '<h2 class="section-title">What Sentinel-X detects</h2>',
    '<h2 class="section-title" data-i18n="cap.title">What Sentinel-X detects</h2>', 1)

# ─── ADVANTAGES ───
content = content.replace(
    '<div class="mlabel">// 05 — advantages</div>',
    '<div class="mlabel" data-i18n="adv.badge">// 05 — advantages</div>', 1)
content = content.replace(
    '<h2 class="section-title">Why Sentinel-X?</h2>',
    '<h2 class="section-title" data-i18n="adv.title">Why Sentinel-X?</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Practical benefits for security monitoring operations.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="adv.desc">Practical benefits for security monitoring operations.</p>', 1)

# ─── LIMITATIONS ───
content = content.replace(
    '<div class="mlabel">// 06 — responsible disclosure</div>',
    '<div class="mlabel" data-i18n="lim.badge">// 06 — responsible disclosure</div>', 1)
content = content.replace(
    '<h2 class="section-title">Limitations &amp; responsible use</h2>',
    '<h2 class="section-title" data-i18n="lim.title">Limitations &amp; responsible use</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Transparency about what Sentinel-X can and cannot do. Understanding these limitations is important for effective deployment.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="lim.desc">Transparency about what Sentinel-X can and cannot do. Understanding these limitations is important for effective deployment.</p>', 1)

# ─── APPLICATIONS ───
content = content.replace(
    '<div class="mlabel">// 07 — potential applications</div>',
    '<div class="mlabel" data-i18n="use.badge">// 07 — potential applications</div>', 1)
content = content.replace(
    '<h2 class="section-title">Who can use Sentinel-X?</h2>',
    '<h2 class="section-title" data-i18n="use.title">Who can use Sentinel-X?</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Sentinel-X is designed for environments where continuous camera monitoring adds real security value.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="use.desc">Sentinel-X is designed for environments where continuous camera monitoring adds real security value.</p>', 1)

# ─── DASHBOARD PREVIEW ───
content = content.replace(
    '<div class="mlabel">// 08 — dashboard preview</div>',
    '<div class="mlabel" data-i18n="preview.label">// 08 — dashboard preview</div>', 1)
content = content.replace(
    '<h2 class="section-title">Your security command center</h2>',
    '<h2 class="section-title" data-i18n="preview.title">Your security command center</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends. Demo data shown below.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="preview.desc">A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends. Demo data shown below.</p>', 1)

# ─── SECURITY ───
content = content.replace(
    '<div class="mlabel">// 09 — security &amp; privacy</div>',
    '<div class="mlabel" data-i18n="sec.label">// 09 — security &amp; privacy</div>', 1)
content = content.replace(
    '<h2 class="section-title">Built-in protections</h2>',
    '<h2 class="section-title" data-i18n="sec.title">Built-in protections</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:44px;">Sentinel-X implements fundamental security controls for access management and data handling.</p>',
    '<p class="section-sub" style="margin-bottom:44px;" data-i18n="sec.desc">Sentinel-X implements fundamental security controls for access management and data handling.</p>', 1)

# ─── TECHNOLOGY ───
content = content.replace(
    '<div class="mlabel">// 10 — technology</div>',
    '<div class="mlabel" data-i18n="tech.label">// 10 — technology</div>', 1)
content = content.replace(
    '<h2 class="section-title">Under the hood</h2>',
    '<h2 class="section-title" data-i18n="tech.title">Under the hood</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:36px;">Sentinel-X is built with proven open-source technologies for AI-powered video analysis.</p>',
    '<p class="section-sub" style="margin-bottom:36px;" data-i18n="tech.desc">Sentinel-X is built with proven open-source technologies for AI-powered video analysis.</p>', 1)

# ─── EVIDENCE FLOW ───
content = content.replace(
    '<div class="mlabel" style="justify-content:center;">// 11 — evidence handling</div>',
    '<div class="mlabel" style="justify-content:center;" data-i18n="evidence.label">// 11 — evidence handling</div>', 1)
content = content.replace(
    '<h2 class="section-title" style="margin-left:auto;margin-right:auto;">How Sentinel-X handles evidence</h2>',
    '<h2 class="section-title" style="margin-left:auto;margin-right:auto;" data-i18n="evidence.title">How Sentinel-X handles evidence</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-left:auto;margin-right:auto;">From the moment something is detected to a fully audited record — every step is logged and traceable.</p>',
    '<p class="section-sub" style="margin-left:auto;margin-right:auto;" data-i18n="evidence.desc">From the moment something is detected to a fully audited record — every step is logged and traceable.</p>', 1)

# ─── FUTURE ───
content = content.replace(
    '<div class="mlabel">// 12 — future vision</div>',
    '<div class="mlabel" data-i18n="future.label">// 12 — future vision</div>', 1)
content = content.replace(
    '<h2 class="section-title">What\'s next for Sentinel-X</h2>',
    '<h2 class="section-title" data-i18n="future.title">What\'s next for Sentinel-X</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:36px;">Items below are planned or conceptual — not part of the current MVP release.</p>',
    '<p class="section-sub" style="margin-bottom:36px;" data-i18n="future.comingSoon">Items below are planned or conceptual — not part of the current MVP release.</p>', 1)

# ─── FAQ ───
content = content.replace(
    '<div class="mlabel">// 13 — frequently asked</div>',
    '<div class="mlabel" data-i18n="faq.label">// 13 — frequently asked</div>', 1)
content = content.replace(
    '<h2 class="section-title">Common questions</h2>',
    '<h2 class="section-title" data-i18n="faq.title">Common questions</h2>', 1)
content = content.replace(
    '<p class="section-sub" style="margin-bottom:36px;">Straight answers, including where Sentinel-X currently falls short.</p>',
    '<p class="section-sub" style="margin-bottom:36px;" data-i18n="faq.desc">Straight answers, including where Sentinel-X currently falls short.</p>', 1)

# ─── FOOTER ───
content = content.replace(
    '<p>AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.</p>',
    '<p data-i18n="footer.desc">AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.</p>', 1)

content = content.replace(
    '<h4>Product</h4>',
    '<h4 data-i18n="footer.col.product">Product</h4>', 1)
content = content.replace(
    '<h4>Technology</h4>',
    '<h4 data-i18n="footer.col.technology">Technology</h4>', 1)
content = content.replace(
    '<h4>Project</h4>',
    '<h4 data-i18n="footer.col.project">Project</h4>', 1)

# Footer links
content = content.replace(
    '<a href="#security">Responsible AI</a>',
    '<a href="#security" data-i18n="footer.link.responsibleAI">Responsible AI</a>', 1)
content = content.replace(
    '<a href="#limitations">Limitations &amp; Use</a>',
    '<a href="#limitations" data-i18n="footer.link.limitations">Limitations &amp; Use</a>', 1)
content = content.replace(
    '<a href="https://github.com/shavron88/sentinel_x_demo.py" target="_blank" rel="noopener">GitHub Repository</a>',
    '<a href="https://github.com/shavron88/sentinel_x_demo.py" target="_blank" rel="noopener" data-i18n="footer.link.github">GitHub Repository</a>', 1)

# Footer bottom
content = content.replace(
    '<span>Sentinel-X AI Edge Surveillance Platform · Version 1.0</span>',
    '<span data-i18n="footer.text">Sentinel-X AI Edge Surveillance Platform · Version 1.0</span>', 1)
content = content.replace(
    '<span>Built with Python, Flask, OpenCV, YOLO11</span>',
    '<span data-i18n="footer.builtWith">Built with Python, Flask, OpenCV, YOLO11</span>', 1)

# ─── FINAL CTA ───
content = content.replace(
    '<h2>Your cameras already see everything.',
    '<h2 data-i18n="cta.title1">Your cameras already see everything.', 1)
content = content.replace(
    '<span class="soft">Sentinel-X helps you understand what matters.</span></h2>',
    '<span class="soft" data-i18n="cta.title2">Sentinel-X helps you understand what matters.</span></h2>', 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("data-i18n tags added to landing.html")
