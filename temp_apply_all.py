#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
changes = []

def rep(old, new, label):
    """Replace first occurrence of old with new. Fails loudly if not found."""
    global content
    count = content.count(old)
    if count == 0:
        print(f"  FAIL: {label} (not found)")
        return False
    if count > 1:
        print(f"  WARN: {label} (found {count} times, replacing first)")
    content = content.replace(old, new, 1)
    changes.append(label)
    print(f"  OK: {label}")
    return True

# ═══════════════════════════════════════════════════════
# EN DICT CHANGES
# ═══════════════════════════════════════════════════════
print("=== EN DICT ===")

# Hero: update values + add keys
rep(
    "    'hero.badge': 'AI-Powered Surveillance Platform',\n    'hero.title1': 'See Threats Before',\n    'hero.title2': 'They Become <span class=\"accent-word\">Incidents.</span>',\n    'hero.subtitle': 'AI-powered intelligent video surveillance that transforms ordinary camera streams into actionable security intelligence — in real time.',\n    'hero.getStarted': 'Get Started',\n    'hero.signIn': 'Sign In',",
    "    'hero.badge': 'AI-Powered Surveillance Platform',\n    'hero.liveCameras': 'Live on 4 cameras right now',\n    'hero.title1': \"Don't just record what happened.\",\n    'hero.title2': \"Understand what's happening.\",\n    'hero.subtitle': 'Sentinel-X turns your existing cameras into an intelligence layer — detecting, tracking, and scoring threats in real time, before they become incidents.',\n    'hero.getStarted': 'Get Started',\n    'hero.viewDashboard': 'View Dashboard',\n    'hero.signIn': 'Sign In',",
    "EN hero values + new keys"
)

# Problem: update values + add label
rep(
    "    'problem.badge': 'The Challenge',\n    'problem.title': 'Traditional CCTV Has Limits',\n    'problem.1.title': 'Continuous Monitoring Is Impossible',\n    'problem.1.desc': 'Humans cannot effectively watch every camera feed simultaneously. Attention fatigue leads to missed events.',\n    'problem.2.title': 'Critical Events Get Missed',\n    'problem.3.title': 'Footage Review Is Inefficient',\n    'problem.3.desc': 'Reviewing hours of recorded video to find a specific incident is time-consuming and resource-intensive.',\n    'problem.4.title': 'Reactive, Not Proactive',\n    'problem.4.desc': \"Traditional CCTV primarily records rather than understands — it captures what happened, but doesn\\'t alert you while it\\'s happening.\",",
    "    'problem.label': '// 01 — the problem',\n    'problem.badge': 'The Challenge',\n    'problem.title': \"Traditional CCTV records. It doesn't understand.\",\n    'problem.1.title': 'Continuous monitoring is impossible',\n    'problem.1.desc': 'Humans cannot effectively watch every camera feed at once. Attention fatigue leads to missed events.',\n    'problem.2.title': 'Critical events get missed',\n    'problem.3.title': 'Footage review is inefficient',\n    'problem.3.desc': 'Reviewing hours of recorded video to find one incident is slow and resource-intensive.',\n    'problem.4.title': 'Reactive, not proactive',\n    'problem.4.desc': \"CCTV captures what happened — it doesn't alert anyone while it's happening.\",",
    "EN problem values + label"
)

# Solution: update values + add label + change alert to threat
rep(
    "    'solution.badge': 'The Sentinel-X Solution',\n    'solution.title': 'From Raw Video to Security Intelligence',\n    'solution.desc': 'Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable security events.',\n    'solution.pipe.camera': 'Camera Feed', 'solution.pipe.vision': 'AI Vision',\n    'solution.pipe.detection': 'Detection', 'solution.pipe.tracking': 'Tracking',\n    'solution.pipe.analysis': 'Analysis', 'solution.pipe.alert': 'Alert',\n    'solution.pipe.evidence': 'Evidence', 'solution.pipe.dashboard': 'Dashboard',",
    "    'solution.label': '// 02 — the solution',\n    'solution.badge': 'The Sentinel-X Solution',\n    'solution.title': 'From raw video to security intelligence',\n    'solution.desc': 'Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable events.',\n    'solution.pipe.camera': 'CAMERA', 'solution.pipe.vision': 'AI VISION',\n    'solution.pipe.detection': 'DETECTION', 'solution.pipe.tracking': 'TRACKING',\n    'solution.pipe.analysis': 'ANALYSIS', 'solution.pipe.threat': 'THREAT',\n    'solution.pipe.evidence': 'EVIDENCE', 'solution.pipe.dashboard': 'DASHBOARD',",
    "EN solution values + label + threat"
)

# How: add label + update title
rep(
    "    'how.badge': 'How It Works',\n    'how.title': 'From Camera to Dashboard in Seconds',",
    "    'how.label': '// 03 — how it works',\n    'how.badge': 'How It Works',\n    'how.title': 'From camera to dashboard in seconds',",
    "EN how label + title"
)

# Cap: add label + update title + add loitering + fix alerts.desc
rep(
    "    'cap.badge': 'Core Capabilities',\n    'cap.title': 'What Sentinel-X Detects',",
    "    'cap.label': '// 04 — capabilities',\n    'cap.badge': 'Core Capabilities',\n    'cap.title': 'What Sentinel-X detects',",
    "EN cap label + title"
)

rep(
    "    'cap.analytics.title': 'Security Analytics', 'cap.analytics.desc': 'Historical trend analysis, zone heatmaps, and detection summaries for operational insight.',",
    "    'cap.loitering.title': 'Loitering Detection', 'cap.loitering.desc': 'Flags individuals remaining in a monitored area beyond a defined time threshold.',\n    'cap.analytics.title': 'Security Analytics', 'cap.analytics.desc': 'Historical trend analysis, zone heatmaps, and detection summaries for operational insight.',",
    "EN add cap.loitering"
)

rep(
    "    'cap.alerts.title': 'Intelligent Alerts', 'cap.alerts.desc': 'Severity-based alerting system classifies events as Low, Medium, High, or Critical.',",
    "    'cap.alerts.title': 'Intelligent Alerts', 'cap.alerts.desc': 'Severity-based alerting classifies events as Low, Medium, High, or Critical.',",
    "EN fix cap.alerts.desc"
)

# Adv: add label
rep(
    "    'adv.badge': 'Advantages',",
    "    'adv.label': '// 05 — advantages',\n    'adv.badge': 'Advantages',",
    "EN adv label"
)

# Lim: add label
rep(
    "    'lim.badge': 'Responsible Disclosure',",
    "    'lim.label': '// 06 — responsible disclosure',\n    'lim.badge': 'Responsible Disclosure',",
    "EN lim label"
)

# Use: add label + update title/desc
rep(
    "    'use.badge': 'Potential Applications',\n    'use.title': 'Who Can Use Sentinel-X?',\n    'use.desc': 'Sentinel-X is designed for environments where continuous camera monitoring adds security value.',",
    "    'use.label': '// 07 — potential applications',\n    'use.badge': 'Potential Applications',\n    'use.title': 'Who can use Sentinel-X?',\n    'use.desc': 'Sentinel-X is designed for environments where continuous camera monitoring adds real security value.',",
    "EN use label + title + desc"
)

# Preview: add label + update title/desc
rep(
    "    'preview.badge': 'Dashboard Preview',\n    'preview.title': 'Your Security Command Center',\n    'preview.desc': 'A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends.',",
    "    'preview.label': '// 08 — dashboard preview',\n    'preview.badge': 'Dashboard Preview',\n    'preview.title': 'Your security command center',\n    'preview.desc': 'A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends. Demo data shown below.',",
    "EN preview label + title + desc"
)

# Sec: add label + remove emojis + fix wording
rep(
    "    'sec.badge': 'Security & Privacy',\n    'sec.title': 'Built-In Protections',\n    'sec.desc': 'Sentinel-X implements fundamental security controls for access management and data handling.',\n    'sec.auth.title': '\\ud83d\\udd10 Authentication', 'sec.auth.desc': 'Session-based authentication with configurable timeout. All users must sign in to access the dashboard.',\n    'sec.protected.title': '\\ud83d\\udee1\\ufe0f Protected Dashboard', 'sec.protected.desc': 'Every dashboard route is protected behind authentication. Unauthenticated visitors are redirected.',\n    'sec.access.title': '\\ud83d\\udd11 Controlled Access', 'sec.access.desc': 'CSRF token protection on state-changing operations. Rate limiting on authentication endpoints.',\n    'sec.evidence.title': '\\ud83d\\udcc1 Evidence Management', 'sec.evidence.desc': 'Event evidence is stored in a structured database with timestamps, camera references, and metadata.',\n    'sec.history.title': '\\ud83d\\udccc Event History', 'sec.history.desc': 'Complete audit trail of detected events with severity classification, camera source, and zone information.',\n    'sec.ai.title': '\\ud83e\\udd16 Responsible AI', 'sec.ai.desc': 'AI detection results are presented with confidence scores. The system is designed to assist, not replace, human judgment.',",
    "    'sec.label': '// 09 — security & privacy',\n    'sec.badge': 'Security & Privacy',\n    'sec.title': 'Built-in protections',\n    'sec.desc': 'Sentinel-X implements fundamental security controls for access management and data handling.',\n    'sec.auth.title': 'Authentication', 'sec.auth.desc': 'Session-based authentication with configurable timeout. All users must sign in to access the dashboard.',\n    'sec.protected.title': 'Protected Dashboard', 'sec.protected.desc': 'Every dashboard route is protected behind authentication. Unauthenticated visitors are redirected to sign in.',\n    'sec.access.title': 'Controlled Access', 'sec.access.desc': 'CSRF token protection on state-changing operations, with rate limiting on authentication endpoints.',\n    'sec.evidence.title': 'Evidence Management', 'sec.evidence.desc': 'Event evidence is stored in a structured database with timestamps, camera references, and integrity hashing.',\n    'sec.history.title': 'Event History', 'sec.history.desc': 'A complete audit trail of detected events, with severity classification, camera source, and zone information.',\n    'sec.ai.title': 'Responsible AI', 'sec.ai.desc': 'AI detection results are shown with confidence scores. The system is designed to assist, not replace, human judgment.',",
    "EN sec values (remove emojis, match HTML)"
)

# Tech: add label + lowercase + add REST API
rep(
    "    'tech.badge': 'Technology',\n    'tech.title': 'Under the Hood',\n    'tech.desc': 'Sentinel-X is built with proven open-source technologies for AI-powered video analysis.',\n    'tech.python': 'Core runtime', 'tech.flask': 'Web framework', 'tech.opencv': 'Video processing',\n    'tech.yolo': 'Object detection', 'tech.bytetrack': 'Object tracking',\n    'tech.sqlite': 'Data storage', 'tech.jscss': 'Dashboard UI',",
    "    'tech.label': '// 10 — technology',\n    'tech.badge': 'Technology',\n    'tech.title': 'Under the hood',\n    'tech.desc': 'Sentinel-X is built with proven open-source technologies for AI-powered video analysis.',\n    'tech.python': 'core runtime', 'tech.flask': 'web framework', 'tech.opencv': 'video processing',\n    'tech.yolo': 'object detection', 'tech.bytetrack': 'object tracking',\n    'tech.sqlite': 'data storage', 'tech.restapi': 'integration', 'tech.jscss': 'dashboard UI',",
    "EN tech values + label + restapi"
)

# Future: add label + planned + roadmap + update title/desc
rep(
    "    'future.badge': 'Future Vision',\n    'future.title': \"What\\'s Next for Sentinel-X\",\n    'future.comingSoon': 'Coming Soon',\n    'future.edgeBox': 'Sentinel-X Edge Box',\n    'future.edgeDesc': 'A dedicated edge-computing appliance designed to run Sentinel-X AI processing closer to the camera infrastructure — reducing dependency on centralized computing and potentially improving deployment flexibility, latency, and bandwidth usage.',\n    'future.cctv': 'CCTV Cameras', 'future.edgeNode': 'Sentinel-X Edge Box',\n    'future.aiProc': 'AI Processing', 'future.alerts': 'Alerts & Events', 'future.cloud': 'Cloud Dashboard',\n    'future.disclaimer': 'The Edge Box is planned future work. The current Sentinel-X release is a software-only platform.',",
    "    'future.label': '// 12 — future vision',\n    'future.badge': 'Future Vision',\n    'future.title': \"What's next for Sentinel-X\",\n    'future.comingSoon': 'Coming Soon',\n    'future.planned': 'PLANNED',\n    'future.edgeBox': 'Sentinel-X Edge Box',\n    'future.edgeDesc': 'A dedicated edge-computing appliance designed to run Sentinel-X AI processing closer to camera infrastructure — reducing dependency on centralized computing and potentially improving deployment flexibility, latency, and bandwidth usage.',\n    'future.cctv': 'CCTV Cameras', 'future.edgeNode': 'Sentinel-X Edge Box',\n    'future.aiProc': 'AI Processing', 'future.alerts': 'Alerts & Events', 'future.cloud': 'Cloud Dashboard',\n    'future.disclaimer': 'The Edge Box is planned future work. The current Sentinel-X release is a software-only platform.',\n    'future.roadmap.0': 'Advanced AI detection models',\n    'future.roadmap.1': 'Expanded threat detection types',\n    'future.roadmap.2': 'Hardware edge deployment',\n    'future.roadmap.3': 'Additional system integrations',\n    'future.roadmap.4': 'Expanded analytics & reporting',\n    'future.roadmap.5': 'Authorized identity integrations',",
    "EN future values + new keys"
)

# CTA/Footer: update footer.text + add new keys
rep(
    "    'cta.createAccount': 'Create Account',\n    'cta.signIn': 'Sign In',\n    'cta.exploreDemo': 'Explore Demo',\n    'footer.text': 'Sentinel-X AI Edge Surveillance Platform \\u00b7 Version 1.0 \\u00b7 Built with Python, Flask, OpenCV, YOLO11',",
    "    'cta.createAccount': 'Create Account',\n    'cta.signIn': 'Sign In',\n    'cta.exploreDemo': 'Explore Demo',\n    'footer.text': 'AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.',\n    'footer.brand': 'AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.',\n    'footer.copyright': 'Sentinel-X AI Edge Surveillance Platform · Version 1.0',\n    'footer.builtWith': 'Built with Python, Flask, OpenCV, YOLO11',\n    'footer.col.product': 'Product', 'footer.col.technology': 'Technology', 'footer.col.project': 'Project',\n    'footer.link.github': 'GitHub Repository',\n    'footer.link.underTheHood': 'Under the Hood',\n    'footer.link.responsibleAI': 'Responsible AI',\n    'footer.link.limitations': 'Limitations & Use',\n    'footer.dashboardPreview': 'Dashboard Preview',",
    "EN footer values + new keys"
)

# Evidence + FAQ: insert before the dashboard section
rep(
    "    // ── Dashboard ──",
    "    // ── Evidence Flow ──\n    'evidence.label': '// 11 — evidence handling',\n    'evidence.title': 'How Sentinel-X handles evidence',\n    'evidence.desc': 'From the moment something is detected to a fully audited record — every step is logged and traceable.',\n    'evidence.step.detection': 'DETECTION', 'evidence.step.event': 'EVENT',\n    'evidence.step.evidence': 'EVIDENCE', 'evidence.step.hash': 'HASH',\n    'evidence.step.storage': 'STORAGE', 'evidence.step.audit': 'AUDIT',\n    'evidence.note': 'Evidence records include timestamps, camera source, and integrity hashing. This describes the current implemented workflow — it does not constitute a claim of legal admissibility or government certification.',\n    // ── FAQ ──\n    'faq.label': '// 13 — frequently asked',\n    'faq.title': 'Common questions',\n    'faq.desc': 'Straight answers, including where Sentinel-X currently falls short.',\n    'faq.1.q': 'Do I need to buy new cameras?',\n    'faq.1.a': \"No. Sentinel-X works with what you already have — webcam, IP camera, RTSP streams, or video files. It's an intelligence layer on top of existing infrastructure, not a hardware replacement.\",\n    'faq.2.q': 'How accurate is the detection?',\n    'faq.2.a': 'Detection uses YOLO11, but no AI system is infallible — false positives and false negatives happen. Accuracy depends on camera quality, resolution, angle, and lighting conditions, which the system reports as confidence scores per detection.',\n    'faq.3.q': 'What happens when it detects something?',\n    'faq.3.a': 'Detections become events that are severity-classified (Low through Critical), trigger real-time alerts on the dashboard, and automatically capture evidence screenshots with metadata. You review and investigate everything from the web dashboard.',\n    'faq.4.q': 'Does it scale to multiple cameras?',\n    'faq.4.a': 'Yes. Multi-Camera Monitoring gives you a centralized view and processing of multiple feeds from a single dashboard, with Object Tracking maintaining consistent IDs across cameras.',\n    'faq.5.q': 'Is Sentinel-X production-ready?',\n    'faq.5.a': \"It's a functional MVP (Version 1.0) — the pipeline runs end to end, but the limitations are real: AI detection can miss events, network reliability matters, and real-time throughput needs GPU acceleration. It's ready to evaluate, not yet ready for blind trust.\",\n    'faq.6.q': \"What's Sentinel-X built on?\",\n    'faq.6.a': 'Python, Flask, OpenCV, and YOLO11 for detection with ByteTrack for object tracking. The dashboard is a web interface you access from any modern browser.',\n    // ── Dashboard ──",
    "EN evidence + FAQ keys"
)

# ═══════════════════════════════════════════════════════
# UR DICT CHANGES
# ═══════════════════════════════════════════════════════
print("\n=== UR DICT ===")

# Fix garbled lim.4 and lim.5 (using raw strings for \u escapes)
rep(
    r"'lim.4': '\u0646\u06cc\u0679 \u0648\u0631\u06a9 \u06a9\u06cc\u0645\u0631\u0648\u06ba \u06a9\u0648 \u0645\u0639\u062a\u0628\u0631 \u06a9\u0646\u06cc\u06a9\u0679\u06cc\u0648\u06cc\u0679\u06cc \u06a9\u06cc \u0636\u0631\u0648\u0631\u062a \u06c1\u0648\u062a\u06cc \u06c1\u06d2\u06d4',",
    "'lim.4': 'نیٹ ورک کیمرے کے لئے مستحکم اور قابل اعتبار کن کنکشن کی ضرورت ہوتی ہے۔',",
    "UR fix lim.4"
)

rep(
    r"'lim.5': 'AI \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0648 \u0630\u0645\u06c1 \u062f\u0627\u0631\u06cc \u0633\u06d2 \u0646\u0627\u0641\u0630 \u06a9\u06cc\u0627 \u062c\u0627\u0646\u0627 \u0686\u0627\u06c1\u06cc\u06d2\u06d4',",
    "'lim.5': 'AI نگرانی کو شفاف طور پر ڈپلائی کرنا چاہیے، اور یہ عمل کے اصول یا مقام کی پالیسی کے مطابق ہو۔',",
    "UR fix lim.5"
)

# UR hero updates
rep(
    r"'hero.title1': '\u062e\u0637\u0631\u0627\u062a \u06a9\u0648 \u067e\u06c1\u0644\u06d2 \u062f\u06cc\u06a9\u06be\u06cc\u06ba',",
    "'hero.title1': 'صرف ریکارڈ نہیں کرو، جو ہو گیا۔',",
    "UR hero.title1"
)

rep(
    r"'hero.title2': '\u0648\u06c7 \u0648\u0627\u0642\u0639\u0627\u062a \u0628\u0646\u0646\u06d2 <span class=""accent-word\">\u0633\u06d2 \u067e\u06c1\u0644\u06d2\u06d4</span>',",
    "'hero.title2': 'سمجھ لو کہ ابھی کیا ہو رہا ہے۔',",
    "UR hero.title2"
)

rep(
    r"'hero.subtitle': 'AI \u0633\u06d2 \u0645\u062a\u062d\u0631\u06a9 \u0630\u06c1\u064a\u0646 \u0648\u06cc\u0688\u06cc\u0648 \u0646\u06af\u0631\u0627\u0646\u06cc \u062c\u0648 \u0639\u0627\u0645 \u06a9\u06cc\u0645\u0631\u0627 \u0627\u0633\u0679\u0631\u06cc\u0645\u0632 \u06a9\u0648 \u0642\u0627\u0628\u0644\u0650 \u0639\u0645\u0644 \u0633\u06cc\u06a1\u0648\u0631\u0679\u06cc \u062e\u0641\u06cc\u0627 \u0645\u06cc\u06ba \u062a\u0628\u062f\u06cc\u0644 \u06a9\u0631\u062a\u06cc \u06c1\u06d2 \u2014 \u062d\u0642\u064a\u0642\u064a \u0648\u0642\u062a \u0645\u06cc\u06ba\u06d4',",
    "'hero.subtitle': 'Sentinel-X اٹھار سے متحرک ذہین ویڈیو نگرانی کی پلیٹ فارم بناتا ہے — پتا لگاتا ہے، ٹریک کرتا ہے، اور دھمکیوں کی نشاندہی کرتا ہے۔',",
    "UR hero.subtitle"
)

# Add UR hero.liveCameras + hero.viewDashboard
rep(
    r"'hero.badge': 'AI \u0633\u06d2 \u0645\u062a\u062d\u0631\u06a9 \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0627 \u067e\u0644\u06cc\u0679 \u0641\u0627\u0631\u0645',\n    'hero.liveCameras': '', 'hero.title1'",
    r"'hero.badge': 'AI \u0633\u06d2 \u0645\u062a\u062d\u0631\u06a9 \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0627 \u067e\u0644\u06cc\u0679 \u0641\u0627\u0631\u0645',\n    'hero.liveCameras': '4 دوربینوں پر لائیو', 'hero.title1'",
    "UR add hero.liveCameras"
)

# ─── Now let's check: does the UR dict already have hero.liveCameras?
# If the file was restored from git, it won't have it.
# Let me check the original UR dict structure

print("\n  (checking if new keys need to be added via insertion)")

# ═══════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*60}")
print(f"EN dict changes applied: {len([c for c in changes if c.startswith('EN')])}")
print(f"UR dict changes applied: {len([c for c in changes if c.startswith('UR')])}")
