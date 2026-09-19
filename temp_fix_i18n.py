#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
changes = []

def replace(old, new, label):
    global content
    if old not in content:
        print(f"WARNING: Could not find: {label}")
        return False
    content = content.replace(old, new, 1)
    changes.append(label)
    return True

# ═══════════════════════════════════════════════════════════
# 1. FIX GARBLED URDU lim.4 and lim.5
# ═══════════════════════════════════════════════════════════

# lim.4 ur: garbled -> proper Urdu
old_lim4_ur = r"'lim.4': '\u0646\u06cc\u0679 \u0648\u0631\u06a9 \u06a9\u06cc\u0645\u0631\u0648\u06ba \u06a9\u0648 \u0645\u0639\u062a\u0628\u0631 \u06a9\u0646\u06cc\u06a9\u0679\u06cc\u0648\u06cc\u0679\u06cc \u06a9\u06cc \u0636\u0631\u0648\u0631\u062a \u06c1\u0648\u062a\u06cc \u06c1\u06d2\u06d4',"
new_lim4_ur = "'lim.4': '\u0646\u06cc\u0679 \u0648\u0631\u06a9 \u06a9\u06cc\u0645\u0631\u0648\u06ba \u06a9\u06cc \u0644\u0626\u06d2 \u0645\u0633\u062a\u062d\u06a9\u0645 \u0627\u0648\u0631 \u0642\u0627\u0628\u0644 \u0627\u0639\u062a\u0628\u0627\u0631 \u06a9\u0646 \u06a9\u0646\u06a9\u0634\u0646 \u06a9\u06cc \u0636\u0631\u0648\u0631\u062a \u06c1\u0648\u062a\u06cc \u06c1\u06d2\u06d4',"
replace(old_lim4_ur, new_lim4_ur, "Fix garbled Urdu lim.4")

old_lim5_ur = "'lim.5': 'AI \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0648 \u0630\u0645\u06c1 \u062f\u0627\u0631\u06cc \u0633\u06d2 \u0646\u0627\u0641\u0630 \u06a9\u06cc\u0627 \u062c\u0627\u0646\u0627 \u0686\u0627\u06c1\u06cc\u06d2\u06d4',"
new_lim5_ur = "'lim.5': 'AI \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0648 \u0634\u0627\u06a9\u0633\u06cc \u0637\u0648\u0631 \u067e\u0631 \u0686\u0627\u0647\u06cc \u06d9 \u062f\u06cc\u0691 \u0644\u06cc\u06d4 \u0627\u0648\u0631 \u06a9\u0648 \u0639\u0645\u0644 \u06a9\u06cc \u0627\u0635\u0644 \u06cc\u0627 \u0645\u0642\u0627\u0645\u06cc \u067e\u0627\u0644\u06cc\u0633\u06cc \u06a9\u06c1 \u0645\u0637\u0627\u0628\u0642 \u06c1\u0648 \u06af\u06cc\u0611 \u06d4',"
replace(old_lim5_ur, new_lim5_ur, "Fix garbled Urdu lim.5")

# ═══════════════════════════════════════════════════════════
# 2. UPDATE EN-DICT HERO VALUES
# ═══════════════════════════════════════════════════════════

old_hero = """    'hero.badge': 'AI-Powered Surveillance Platform',
    'hero.title1': 'See Threats Before',
    'hero.title2': 'They Become <span class="accent-word">Incidents.</span>',
    'hero.subtitle': 'AI-powered intelligent video surveillance that transforms ordinary camera streams into actionable security intelligence — in real time.',
    'hero.getStarted': 'Get Started',
    'hero.signIn': 'Sign In',
    'hero.explore': 'Explore Sentinel-X',"""

new_hero = """    'hero.badge': 'AI-Powered Surveillance Platform',
    'hero.liveCameras': 'Live on 4 cameras right now',
    'hero.title1': 'Don\\'t just record what happened.',
    'hero.title2': 'Understand what\\'s happening.',
    'hero.subtitle': 'Sentinel-X turns your existing cameras into an intelligence layer — detecting, tracking, and scoring threats in real time, before they become incidents.',
    'hero.getStarted': 'Get Started',
    'hero.viewDashboard': 'View Dashboard',
    'hero.signIn': 'Sign In',
    'hero.explore': 'Explore Sentinel-X',"""

replace(old_hero, new_hero, "Update en-dict hero values")

# ═══════════════════════════════════════════════════════════
# 3. UPDATE EN-DICT PROBLEM VALUES
# ═══════════════════════════════════════════════════════════

old_problem = """    'problem.badge': 'The Challenge',
    'problem.title': 'Traditional CCTV Has Limits',
    'problem.desc': 'Most surveillance systems record footage but don\\'t understand what they see. Security teams face challenges that technology should help solve.',
    'problem.1.title': 'Continuous Monitoring Is Impossible',
    'problem.1.desc': 'Humans cannot effectively watch every camera feed simultaneously. Attention fatigue leads to missed events.',
    'problem.2.title': 'Critical Events Get Missed',
    'problem.2.desc': 'Important security events can go unnoticed in real time, only discovered after damage has occurred.',
    'problem.3.title': 'Footage Review Is Inefficient',
    'problem.3.desc': 'Reviewing hours of recorded video to find a specific incident is time-consuming and resource-intensive.',
    'problem.4.title': 'Reactive, Not Proactive',
    'problem.4.desc': 'Traditional CCTV primarily records rather than understands — it captures what happened, but doesn\\'t alert you while it\\'s happening.',"""

new_problem = """    'problem.label': '// 01 — the problem',
    'problem.badge': 'The Challenge',
    'problem.title': 'Traditional CCTV records. It doesn\\'t understand.',
    'problem.desc': 'Most surveillance systems record footage but don\\'t understand what they see. Security teams face challenges that technology should help solve.',
    'problem.1.title': 'Continuous monitoring is impossible',
    'problem.1.desc': 'Humans cannot effectively watch every camera feed at once. Attention fatigue leads to missed events.',
    'problem.2.title': 'Critical events get missed',
    'problem.2.desc': 'Important security events can go unnoticed in real time, only discovered after damage has occurred.',
    'problem.3.title': 'Footage review is inefficient',
    'problem.3.desc': 'Reviewing hours of recorded video to find one incident is slow and resource-intensive.',
    'problem.4.title': 'Reactive, not proactive',
    'problem.4.desc': 'CCTV captures what happened — it doesn\\'t alert anyone while it\\'s happening.',"""

replace(old_problem, new_problem, "Update en-dict problem values")

# ═══════════════════════════════════════════════════════════
# 4. UPDATE EN-DICT SOLUTION VALUES
# ═══════════════════════════════════════════════════════════

old_solution = """    'solution.badge': 'The Sentinel-X Solution',
    'solution.title': 'From Raw Video to Security Intelligence',
    'solution.desc': 'Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable security events.',
    'solution.pipe.camera': 'Camera Feed', 'solution.pipe.vision': 'AI Vision',
    'solution.pipe.detection': 'Detection', 'solution.pipe.tracking': 'Tracking',
    'solution.pipe.analysis': 'Analysis', 'solution.pipe.alert': 'Alert',
    'solution.pipe.evidence': 'Evidence', 'solution.pipe.dashboard': 'Dashboard',"""

new_solution = """    'solution.label': '// 02 — the solution',
    'solution.badge': 'The Sentinel-X Solution',
    'solution.title': 'From raw video to security intelligence',
    'solution.desc': 'Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable events.',
    'solution.pipe.camera': 'CAMERA', 'solution.pipe.vision': 'AI VISION',
    'solution.pipe.detection': 'DETECTION', 'solution.pipe.tracking': 'TRACKING',
    'solution.pipe.analysis': 'ANALYSIS', 'solution.pipe.threat': 'THREAT',
    'solution.pipe.evidence': 'EVIDENCE', 'solution.pipe.dashboard': 'DASHBOARD',"""

replace(old_solution, new_solution, "Update en-dict solution values + add solution.pipe.threat")

# ═══════════════════════════════════════════════════════════
# 5. UPDATE EN-DICT HOW IT WORKS (title + add label)
# ═══════════════════════════════════════════════════════════

old_how = """    'how.badge': 'How It Works',
    'how.title': 'From Camera to Dashboard in Seconds',"""
new_how = """    'how.label': '// 03 — how it works',
    'how.badge': 'How It Works',
    'how.title': 'From camera to dashboard in seconds',"""
replace(old_how, new_how, "Update en-dict how.title + add how.label")

# ═══════════════════════════════════════════════════════════
# 6. UPDATE EN-DICT CAPABILITIES (title + add loitering + fix alerts.desc)
# ═══════════════════════════════════════════════════════════

old_cap_badge = """    'cap.badge': 'Core Capabilities',
    'cap.title': 'What Sentinel-X Detects',"""
new_cap_badge = """    'cap.label': '// 04 — capabilities',
    'cap.badge': 'Core Capabilities',
    'cap.title': 'What Sentinel-X detects',"""
replace(old_cap_badge, new_cap_badge, "Update en-dict cap values + add cap.label")

# Add loitering card keys + fix alerts.desc
old_cap_end = """    'cap.alerts.title': 'Intelligent Alerts', 'cap.alerts.desc': 'Severity-based alerting system classifies events as Low, Medium, High, or Critical.',"""
new_cap_end = """    'cap.loitering.title': 'Loitering Detection', 'cap.loitering.desc': 'Flags individuals remaining in a monitored area beyond a defined time threshold.',
    'cap.alerts.title': 'Intelligent Alerts', 'cap.alerts.desc': 'Severity-based alerting classifies events as Low, Medium, High, or Critical.',"""
replace(old_cap_end, new_cap_end, "Add cap.loitering keys + fix cap.alerts.desc")

# ═══════════════════════════════════════════════════════════
# 7. ADD adv.label
# ═══════════════════════════════════════════════════════════

old_adv = """    'adv.badge': 'Advantages',
    'adv.title': 'Why Sentinel-X?',"""
new_adv = """    'adv.label': '// 05 — advantages',
    'adv.badge': 'Advantages',
    'adv.title': 'Why Sentinel-X?',"""
replace(old_adv, new_adv, "Add adv.label")

# ═══════════════════════════════════════════════════════════
# 8. ADD lim.label
# ═══════════════════════════════════════════════════════════

old_lim = """    'lim.badge': 'Responsible Disclosure',"""
new_lim = """    'lim.label': '// 06 — responsible disclosure',
    'lim.badge': 'Responsible Disclosure',"""
replace(old_lim, new_lim, "Add lim.label")

# ═══════════════════════════════════════════════════════════
# 9. UPDATE EN-DICT USE CASES (add label, fix title/desc)
# ═══════════════════════════════════════════════════════════

old_use = """    'use.badge': 'Potential Applications',
    'use.title': 'Who Can Use Sentinel-X?',
    'use.desc': 'Sentinel-X is designed for environments where continuous camera monitoring adds security value.',"""
new_use = """    'use.label': '// 07 — potential applications',
    'use.badge': 'Potential Applications',
    'use.title': 'Who can use Sentinel-X?',
    'use.desc': 'Sentinel-X is designed for environments where continuous camera monitoring adds real security value.',"""
replace(old_use, new_use, "Update en-dict use values + add use.label")

# ═══════════════════════════════════════════════════════════
# 10. UPDATE EN-DICT PREVIEW (add label, fix title/desc)
# ═══════════════════════════════════════════════════════════

old_preview = """    'preview.badge': 'Dashboard Preview',
    'preview.title': 'Your Security Command Center',
    'preview.desc': 'A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends.',"""
new_preview = """    'preview.label': '// 08 — dashboard preview',
    'preview.badge': 'Dashboard Preview',
    'preview.title': 'Your security command center',
    'preview.desc': 'A unified web dashboard for monitoring cameras, reviewing events, examining evidence, and analyzing security trends. Demo data shown below.',"""
replace(old_preview, new_preview, "Update en-dict preview values + add preview.label")

# ═══════════════════════════════════════════════════════════
# 11. UPDATE EN-DICT SECURITY (remove emojis, fix desc match HTML)
# ═══════════════════════════════════════════════════════════

old_sec = """    'sec.badge': 'Security & Privacy',
    'sec.title': 'Built-In Protections',
    'sec.desc': 'Sentinel-X implements fundamental security controls for access management and data handling.',
    'sec.auth.title': '\\ud83d\\udd10 Authentication', 'sec.auth.desc': 'Session-based authentication with configurable timeout. All users must sign in to access the dashboard.',
    'sec.protected.title': '\\ud83d\\udee1\\ufe0f Protected Dashboard', 'sec.protected.desc': 'Every dashboard route is protected behind authentication. Unauthenticated visitors are redirected.',
    'sec.access.title': '\\ud83d\\udd11 Controlled Access', 'sec.access.desc': 'CSRF token protection on state-changing operations. Rate limiting on authentication endpoints.',
    'sec.evidence.title': '\\ud83d\\udcc1 Evidence Management', 'sec.evidence.desc': 'Event evidence is stored in a structured database with timestamps, camera references, and metadata.',
    'sec.history.title': '\\ud83d\\udcdc Event History', 'sec.history.desc': 'Complete audit trail of detected events with severity classification, camera source, and zone information.',
    'sec.ai.title': '\\ud83e\\udd16 Responsible AI', 'sec.ai.desc': 'AI detection results are presented with confidence scores. The system is designed to assist, not replace, human judgment.',"""

new_sec = """    'sec.label': '// 09 — security & privacy',
    'sec.badge': 'Security & Privacy',
    'sec.title': 'Built-in protections',
    'sec.desc': 'Sentinel-X implements fundamental security controls for access management and data handling.',
    'sec.auth.title': 'Authentication', 'sec.auth.desc': 'Session-based authentication with configurable timeout. All users must sign in to access the dashboard.',
    'sec.protected.title': 'Protected Dashboard', 'sec.protected.desc': 'Every dashboard route is protected behind authentication. Unauthenticated visitors are redirected to sign in.',
    'sec.access.title': 'Controlled Access', 'sec.access.desc': 'CSRF token protection on state-changing operations, with rate limiting on authentication endpoints.',
    'sec.evidence.title': 'Evidence Management', 'sec.evidence.desc': 'Event evidence is stored in a structured database with timestamps, camera references, and integrity hashing.',
    'sec.history.title': 'Event History', 'sec.history.desc': 'A complete audit trail of detected events, with severity classification, camera source, and zone information.',
    'sec.ai.title': 'Responsible AI', 'sec.ai.desc': 'AI detection results are shown with confidence scores. The system is designed to assist, not replace, human judgment.',"""

replace(old_sec, new_sec, "Update en-dict security values (remove emojis, match HTML)")

# ═══════════════════════════════════════════════════════════
# 12. UPDATE EN-DICT TECHNOLOGY (add label, lowercase roles, add REST API)
# ═══════════════════════════════════════════════════════════

old_tech = """    'tech.badge': 'Technology',
    'tech.title': 'Under the Hood',
    'tech.desc': 'Sentinel-X is built with proven open-source technologies for AI-powered video analysis.',
    'tech.python': 'Core runtime', 'tech.flask': 'Web framework', 'tech.opencv': 'Video processing',
    'tech.yolo': 'Object detection', 'tech.bytetrack': 'Object tracking',
    'tech.sqlite': 'Data storage', 'tech.jscss': 'Dashboard UI',"""

new_tech = """    'tech.label': '// 10 — technology',
    'tech.badge': 'Technology',
    'tech.title': 'Under the hood',
    'tech.desc': 'Sentinel-X is built with proven open-source technologies for AI-powered video analysis.',
    'tech.python': 'core runtime', 'tech.flask': 'web framework', 'tech.opencv': 'video processing',
    'tech.yolo': 'object detection', 'tech.bytetrack': 'object tracking',
    'tech.sqlite': 'data storage', 'tech.restapi': 'integration', 'tech.jscss': 'dashboard UI',"""

replace(old_tech, new_tech, "Update en-dict technology values + add tech.label + tech.restapi")

# ═══════════════════════════════════════════════════════════
# 13. UPDATE EN-DICT FUTURE (add label, fix title, add roadmap keys)
# ═══════════════════════════════════════════════════════════

old_future = """    'future.badge': 'Future Vision',
    'future.title': 'What\\'s Next for Sentinel-X',
    'future.comingSoon': 'Coming Soon',
    'future.edgeBox': 'Sentinel-X Edge Box',
    'future.edgeDesc': 'A dedicated edge-computing appliance designed to run Sentinel-X AI processing closer to the camera infrastructure — reducing dependency on centralized computing and potentially improving deployment flexibility, latency, and bandwidth usage.',
    'future.cctv': 'CCTV Cameras', 'future.edgeNode': 'Sentinel-X Edge Box',
    'future.aiProc': 'AI Processing', 'future.alerts': 'Alerts & Events', 'future.cloud': 'Cloud Dashboard',
    'future.disclaimer': 'The Edge Box is planned future work. The current Sentinel-X release is a software-only platform.',"""

new_future = """    'future.label': '// 12 — future vision',
    'future.badge': 'Future Vision',
    'future.title': 'What\\'s next for Sentinel-X',
    'future.comingSoon': 'Coming Soon',
    'future.planned': 'PLANNED',
    'future.edgeBox': 'Sentinel-X Edge Box',
    'future.edgeDesc': 'A dedicated edge-computing appliance designed to run Sentinel-X AI processing closer to camera infrastructure — reducing dependency on centralized computing and potentially improving deployment flexibility, latency, and bandwidth usage.',
    'future.cctv': 'CCTV Cameras', 'future.edgeNode': 'Sentinel-X Edge Box',
    'future.aiProc': 'AI Processing', 'future.alerts': 'Alerts & Events', 'future.cloud': 'Cloud Dashboard',
    'future.disclaimer': 'The Edge Box is planned future work. The current Sentinel-X release is a software-only platform.',
    'future.roadmap.0': 'Advanced AI detection models',
    'future.roadmap.1': 'Expanded threat detection types',
    'future.roadmap.2': 'Hardware edge deployment',
    'future.roadmap.3': 'Additional system integrations',
    'future.roadmap.4': 'Expanded analytics & reporting',
    'future.roadmap.5': 'Authorized identity integrations',"""

replace(old_future, new_future, "Update en-dict future values + add future.label/planned/roadmap keys")

# ═══════════════════════════════════════════════════════════
# 14. UPDATE EN-DICT CTA & FOOTER
# ═══════════════════════════════════════════════════════════

old_cta_footer = """    'cta.createAccount': 'Create Account',
    'cta.signIn': 'Sign In',
    'cta.exploreDemo': 'Explore Demo',
    'footer.text': 'Sentinel-X AI Edge Surveillance Platform \\u00b7 Version 1.0 \\u00b7 Built with Python, Flask, OpenCV, YOLO11',"""

new_cta_footer = """    'cta.createAccount': 'Create Account',
    'cta.signIn': 'Sign In',
    'cta.exploreDemo': 'Explore Demo',
    'footer.text': 'AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.',
    'footer.brand': 'AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.',
    'footer.copyright': 'Sentinel-X AI Edge Surveillance Platform · Version 1.0',
    'footer.builtWith': 'Built with Python, Flask, OpenCV, YOLO11',
    'footer.col.product': 'Product', 'footer.col.technology': 'Technology', 'footer.col.project': 'Project',
    'footer.link.github': 'GitHub Repository',
    'footer.link.underTheHood': 'Under the Hood',
    'footer.link.responsibleAI': 'Responsible AI',
    'footer.link.limitations': 'Limitations & Use',
    'footer.dashboardPreview': 'Dashboard Preview',"""

replace(old_cta_footer, new_cta_footer, "Update en-dict cta/footer + add footer keys")

# ═══════════════════════════════════════════════════════════
# 15. ADD EVIDENCE AND FAQ KEYS (before dashboard section comment)
# ═══════════════════════════════════════════════════════════

old_evidence_add = """    // ── Dashboard ──"""
new_evidence_add = """    // ── Evidence Flow ──
    'evidence.label': '// 11 — evidence handling',
    'evidence.title': 'How Sentinel-X handles evidence',
    'evidence.desc': 'From the moment something is detected to a fully audited record — every step is logged and traceable.',
    'evidence.step.detection': 'DETECTION', 'evidence.step.event': 'EVENT',
    'evidence.step.evidence': 'EVIDENCE', 'evidence.step.hash': 'HASH',
    'evidence.step.storage': 'STORAGE', 'evidence.step.audit': 'AUDIT',
    'evidence.note': 'Evidence records include timestamps, camera source, and integrity hashing. This describes the current implemented workflow — it does not constitute a claim of legal admissibility or government certification.',
    // ── FAQ ──
    'faq.label': '// 13 — frequently asked',
    'faq.title': 'Common questions',
    'faq.desc': 'Straight answers, including where Sentinel-X currently falls short.',
    'faq.1.q': 'Do I need to buy new cameras?',
    'faq.1.a': 'No. Sentinel-X works with what you already have — webcam, IP camera, RTSP streams, or video files. It\\'s an intelligence layer on top of existing infrastructure, not a hardware replacement.',
    'faq.2.q': 'How accurate is the detection?',
    'faq.2.a': 'Detection uses YOLO11, but no AI system is infallible — false positives and false negatives happen. Accuracy depends on camera quality, resolution, angle, and lighting conditions, which the system reports as confidence scores per detection.',
    'faq.3.q': 'What happens when it detects something?',
    'faq.3.a': 'Detections become events that are severity-classified (Low through Critical), trigger real-time alerts on the dashboard, and automatically capture evidence screenshots with metadata. You review and investigate everything from the web dashboard.',
    'faq.4.q': 'Does it scale to multiple cameras?',
    'faq.4.a': 'Yes. Multi-Camera Monitoring gives you a centralized view and processing of multiple feeds from a single dashboard, with Object Tracking maintaining consistent IDs across cameras.',
    'faq.5.q': 'Is Sentinel-X production-ready?',
    'faq.5.a': 'It\\'s a functional MVP (Version 1.0) — the pipeline runs end to end, but the limitations are real: AI detection can miss events, network reliability matters, and real-time throughput needs GPU acceleration. It\\'s ready to evaluate, not yet ready for blind trust.',
    'faq.6.q': 'What\\'s Sentinel-X built on?',
    'faq.6.a': 'Python, Flask, OpenCV, and YOLO11 for detection with ByteTrack for object tracking. The dashboard is a web interface you access from any modern browser.',
    // ── Dashboard ──"""

replace(old_evidence_add, new_evidence_add, "Add evidence and FAQ keys")

# ═══════════════════════════════════════════════════════════
# 16. UPDATE EN-DICT STATUS PANEL VALUES (to match HTML)
# ═══════════════════════════════════════════════════════════

old_status = """    'status.operational': 'Operational',
    'status.aiEngine': 'AI Engine',"""
new_status = """    'status.operational': 'Operational',
    'status.aiEngine': 'AI Engine',"""
# These already match. No change needed for status.* keys.

# ═══════════════════════════════════════════════════════════
# 17. Update en-dict cap.alerts.title/desc and add cap.loitering
# (already done in step 6)

# ═══════════════════════════════════════════════════════════
# 18. FIX solution.pipe.alert -> solution.pipe.threat in en-dict
# (already done in step 4 - we replaced alert with threat)

# ═══════════════════════════════════════════════════════════
# SAVE AND VERIFY
# ═══════════════════════════════════════════════════════════

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*60}")
print(f"Successfully applied {len(changes)} changes to i18n.js")
print(f"{'='*60}")
for c in changes:
    print(f"  ✓ {c}")
print(f"\nChanges saved to {filepath}")
