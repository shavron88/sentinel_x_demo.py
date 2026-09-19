"""
Add missing EN keys and corresponding ZH/UR translations
"""
import re

js_path = r'dashboard\static\js\i18n.js'

with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── Missing EN additions ───
EN_MISSING = {
    'evidence.label': 'Evidence Handling',
    'evidence.detection': 'DETECTION',
    'evidence.event': 'EVENT',
    'evidence.evidence': 'EVIDENCE',
    'evidence.hash': 'HASH',
    'evidence.storage': 'STORAGE',
    'evidence.audit': 'AUDIT',
    'faq.label': 'Frequently Asked',
    'faq.desc': 'Straight answers, including where Sentinel-X currently falls short.',
    'footer.desc': 'AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.',
    'footer.dashboardPreview': 'Dashboard Preview',
    'future.planned': 'PLANNED',
    'nav.about': 'The Challenge',
    'nav.applications': 'Applications',
    'nav.dashboard': 'Dashboard Preview',
    'solution.pipe.threat': 'Threat',
    'tech.python.role': 'core runtime',
    'tech.flask.role': 'web framework',
    'tech.opencv.role': 'video processing',
    'tech.yolo.role': 'object detection',
    'tech.bytetrack.role': 'object tracking',
    'tech.sqlite.role': 'data storage',
}

# ─── ZH translations for missing keys ───
ZH_MISSING = {
    'evidence.label': '证据处理',
    'evidence.detection': '检测',
    'evidence.event': '事件',
    'evidence.evidence': '证据',
    'evidence.hash': '哈希',
    'evidence.storage': '存储',
    'evidence.audit': '审计',
    'faq.label': '常见问题',
    'faq.desc': '直接的答案，包括 Sentinel-X 目前存在的不足之处。',
    'footer.desc': '基于现有摄像头基础设施的 AI 驱动视频安全智能。软件优先的 MVP。',
    'footer.dashboardPreview': '仪表板预览',
    'future.planned': '计划中',
    'nav.about': '挑战',
    'nav.applications': '应用程序',
    'nav.dashboard': '仪表板预览',
    'solution.pipe.threat': '威胁',
    'tech.python.role': '核心运行时',
    'tech.flask.role': 'Web框架',
    'tech.opencv.role': '视频处理',
    'tech.yolo.role': '目标检测',
    'tech.bytetrack.role': '目标跟踪',
    'tech.sqlite.role': '数据存储',
}

# ─── UR translations for missing keys ───
UR_MISSING = {
    'evidence.label': 'ثبوت کی نوصان',
    'evidence.detection': 'تشخیص',
    'evidence.event': 'واقعہ',
    'evidence.evidence': 'ثبوت',
    'evidence.hash': 'ہیش',
    'evidence.storage': 'محفوظ کرنا',
    'evidence.audit': 'جائزہ',
    'faq.label': 'اکثر پوچھے جانے والے سوالات',
    'faq.desc': 'براہ راست جوابات، بشمول اس بات کی حالت میں کہ Sentinel-X ابھی کمزور ہے۔',
    'footer.desc': 'موجودہ چیمرے انفراسٹرکچر کے لئے AI پاورڈ ویڈیو سیکورٹی انٹیلیجنس۔ سافٹ ویئر فرسٹ MVP۔',
    'footer.dashboardPreview': 'ڈیش بورڈ کی پیشکش',
    'future.planned': 'منصوبے',
    'nav.about': 'چیلنج',
    'nav.applications': 'ایپلیکیشنز',
    'nav.dashboard': 'ڈیش بورڈ کی پیشکش',
    'solution.pipe.threat': 'خطرہ',
    'tech.python.role': 'کور رین ٹائم',
    'tech.flask.role': 'ویب فریم ورک',
    'tech.opencv.role': 'ویڈیو پروسیسنگ',
    'tech.yolo.role': 'آئی بی ایس',
    'tech.bytetrack.role': 'آئی بی بی ایس',
    'tech.sqlite.role': 'ڈیٹا اسٹوریج',
}

# ─── Add EN keys ───
# Find EN dict closing (signup.errorConn now has a comma)
en_close = re.search(r"(    'signup\.errorConn':\s*'[^']+',\n)(\s*// ── Dashboard)", content)
if en_close:
    insert_pos = en_close.start(2) - 1  # Before the comment
    new_entries = ""
    for key, val in EN_MISSING.items():
        escaped = val.replace("'", "\\'")
        new_entries += f"    '{key}': '{escaped}',\n"
    content = content[:insert_pos] + new_entries + "\n" + content[insert_pos:]
    print("Added EN keys")
else:
    # Try another approach - find the last entry before the ZH dict
    en_end = re.search(r"(    'footer\.dashboardPreview':\s*'[^']+',\n)(\s*/\*.*CHINESE)", content)
    if en_end:
        insert_pos = en_end.start(2) - 1
        new_entries = ""
        for key, val in EN_MISSING.items():
            escaped = val.replace("'", "\\'")
            new_entries += f"    '{key}': '{escaped}',\n"
        content = content[:insert_pos] + new_entries + "\n" + content[insert_pos:]
        print("Added EN keys (alternate)")
    else:
        print("Could not find EN insertion point")

# ─── Add ZH keys ───
# Find ZH dict closing (login.errorConnection now has comma)
zh_close = re.search(r"(    'login\.errorConnection':\s*'[^']+',\n)(\s*// ──)", content)
if zh_close:
    insert_pos = zh_close.start(2) - 1
    new_entries = ""
    for key, val in ZH_MISSING.items():
        escaped = val.replace("'", "\\'")
        new_entries += f"    '{key}': '{escaped}',\n"
    content = content[:insert_pos] + new_entries + "\n" + content[insert_pos:]
    print("Added ZH keys")
else:
    print("Could not find ZH insertion point")

# ─── Add UR keys ───
# Find UR dict closing
ur_close = re.search(r"(    'footer\.dashboardPreview':\s*'[^']+',\n)(\s*\};)", content)
if ur_close:
    insert_pos = ur_close.start(2) - 1
    new_entries = ""
    for key, val in UR_MISSING.items():
        new_entries += f"    '{key}': '{val}',\n"
    content = content[:insert_pos] + new_entries + "\n" + content[insert_pos:]
    print("Added UR keys")
else:
    # Find the UR footer.text line
    ur_end = re.search(r"(    'footer\.text':\s*'[^']+'[^,}]+)(\n\s*\};)", content[content.find('dicts.ur'):])
    if ur_end:
        full_content_pos = content.find('dicts.ur') + ur_end.start()
        insert_pos = full_content_pos + ur_end.start(2)
        new_entries = ""
        for key, val in UR_MISSING.items():
            new_entries += f"    '{key}': '{val}',\n"
        content = content[:insert_pos] + new_entries + content[insert_pos:]
        print("Added UR keys (alternate)")
    else:
        print("Could not find UR insertion point")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated")
