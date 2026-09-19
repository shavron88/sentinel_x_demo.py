#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find UR dict boundaries
ur_start = content.find('dicts.ur = {')
ur_start_brace = content.find('{', ur_start)
depth = 0
i = ur_start_brace
while i < len(content):
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            ur_end = i + 1
            break
    i += 1

print(f"UR dict: chars {ur_start}-{ur_end} (len={ur_end-ur_start})")

ur_section = content[ur_start:ur_end]

# Find all keys
key_pattern = re.compile(r"'(\w[\w.]*)'\s*:")
ur_keys = [m.group(1) for m in key_pattern.finditer(ur_section)]
print(f"Total keys in UR dict: {len(ur_keys)}")

# Check what's missing
all_expected_ur_keys = [
    'nav.capabilities', 'nav.howItWorks', 'nav.technology', 'nav.dashboard',
    'nav.applications', 'nav.about', 'nav.signIn', 'nav.createAccount',
    'hero.badge', 'hero.liveCameras', 'hero.title1', 'hero.title2',
    'hero.subtitle', 'hero.getStarted', 'hero.viewDashboard', 'hero.signIn',
    'hero.explore', 'status.operational', 'status.aiEngine', 'status.cameraNetwork',
    'status.threatMonitoring', 'status.yoloModel', 'status.detectionEngine',
    'status.evidenceStore', 'status.online', 'status.active', 'status.loaded',
    'status.running', 'status.connected',
    'problem.label', 'problem.badge', 'problem.title', 'problem.desc',
    'problem.1.title', 'problem.1.desc', 'problem.2.title', 'problem.2.desc',
    'problem.3.title', 'problem.3.desc', 'problem.4.title', 'problem.4.desc',
    'problem.5.title', 'problem.5.desc',
    'solution.label', 'solution.badge', 'solution.title', 'solution.desc',
    'solution.pipe.camera', 'solution.pipe.vision', 'solution.pipe.detection',
    'solution.pipe.tracking', 'solution.pipe.analysis', 'solution.pipe.threat',
    'solution.pipe.evidence', 'solution.pipe.dashboard',
    'cap.badge', 'cap.title', 'cap.desc', 'cap.person.title', 'cap.person.desc',
    'cap.crowd.title', 'cap.crowd.desc', 'cap.restricted.title', 'cap.restricted.desc',
    'cap.abandoned.title', 'cap.abandoned.desc', 'cap.fall.title', 'cap.fall.desc',
    'cap.weapon.title', 'cap.weapon.desc', 'cap.line.title', 'cap.line.desc',
    'cap.multi.title', 'cap.multi.desc', 'cap.track.title', 'cap.track.desc',
    'cap.evidence.title', 'cap.evidence.desc', 'cap.alerts.title', 'cap.alerts.desc',
    'cap.analytics.title', 'cap.analytics.desc', 'cap.loitering.title', 'cap.loitering.desc',
    'how.badge', 'how.title', 'how.desc', 'how.1.title', 'how.1.desc', 'how.2.title',
    'how.2.desc', 'how.3.title', 'how.3.desc', 'how.4.title', 'how.4.desc',
    'how.5.title', 'how.5.desc', 'how.6.title', 'how.6.desc', 'how.7.title',
    'how.7.desc', 'how.8.title', 'how.8.desc', 'how.9.title', 'how.9.desc',
    'adv.badge', 'adv.title', 'adv.desc', 'adv.1', 'adv.2', 'adv.3', 'adv.4',
    'adv.5', 'adv.6', 'adv.7', 'adv.8', 'adv.9', 'adv.10',
    'lim.label', 'lim.badge', 'lim.title', 'lim.desc', 'lim.1', 'lim.2', 'lim.3',
    'lim.4', 'lim.5', 'lim.6', 'lim.7',
    'use.badge', 'use.title', 'use.desc', 'use.label',
    'app.badge', 'app.title', 'app.desc',
    'preview.badge', 'preview.title', 'preview.desc', 'preview.label',
    'sec.badge', 'sec.title', 'sec.desc', 'sec.label',
    'sec.auth.title', 'sec.auth.desc', 'sec.protected.title', 'sec.protected.desc',
    'sec.access.title', 'sec.access.desc', 'sec.evidence.title', 'sec.evidence.desc',
    'sec.history.title', 'sec.history.desc', 'sec.ai.title', 'sec.ai.desc',
    'tech.badge', 'tech.title', 'tech.desc', 'tech.label',
    'tech.python', 'tech.flask', 'tech.opencv', 'tech.yolo', 'tech.bytetrack',
    'tech.sqlite', 'tech.jscss', 'tech.restapi',
    'future.badge', 'future.title', 'future.comingSoon', 'future.planned',
    'future.edgeBox', 'future.edgeDesc', 'future.cctv', 'future.edgeNode',
    'future.aiProc', 'future.alerts', 'future.cloud', 'future.disclaimer',
    'future.label', 'future.roadmap.0', 'future.roadmap.1', 'future.roadmap.2',
    'future.roadmap.3', 'future.roadmap.4', 'future.roadmap.5',
    'cta.title1', 'cta.title2', 'cta.subtitle', 'cta.createAccount', 'cta.signIn',
    'cta.exploreDemo',
    'footer.text', 'footer.brand', 'footer.copyright', 'footer.builtWith',
    'footer.col.product', 'footer.col.technology', 'footer.col.project',
    'footer.link.github', 'footer.link.underTheHood', 'footer.link.responsibleAI',
    'footer.link.limitations', 'footer.dashboardPreview',
    'evidence.label', 'evidence.title', 'evidence.desc',
    'evidence.step.detection', 'evidence.step.event', 'evidence.step.evidence',
    'evidence.step.hash', 'evidence.step.storage', 'evidence.step.audit',
    'evidence.note',
    'faq.label', 'faq.title', 'faq.desc',
    'faq.1.q', 'faq.1.a', 'faq.2.q', 'faq.2.a', 'faq.3.q', 'faq.3.a',
    'faq.4.q', 'faq.4.a', 'faq.5.q', 'faq.5.a', 'faq.6.q', 'faq.6.a',
    'dash.error.notAvailable', 'dash.error.backBtn',
    'login.title', 'login.subtitle', 'login.tagline',
    'signup.title', 'signup.subtitle', 'signup.tagline',
    'login.secureAccess', 'login.signInDesc', 'login.connectionStatus',
    'login.secureConn', 'login.encrypted',
    'signup.footerText'
]

missing = [k for k in all_expected_ur_keys if k not in ur_keys]
print(f"\nMissing from UR dict ({len(missing)}):")
for k in missing:
    print(f"  - {k}")
