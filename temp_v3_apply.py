"""
Comprehensive i18n update script - v3
Uses line-by-line parsing to safely modify all three dicts.
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ─── Define all new keys to add ───
# Format: (key, en_value, zh_value, ur_value)
NEW_KEYS = [
    # Section labels
    ('problem.label', 'The Challenge', '挑战', 'چیلنج'),
    ('solution.label', 'The Solution', '解决方案', 'حل'),
    ('how.label', 'How It Works', '工作原理', 'کسے کام کرتا ہے'),
    ('cap.label', 'Core Capabilities', '核心功能', 'بنیادی صلاحیتيں'),
    ('lim.label', 'Responsible Disclosure', '负责声明', 'ذمہِ دارانہ اخبارات'),
    ('use.label', 'Applications', '应用', 'اپلیکیشنز'),
    ('preview.label', 'Dashboard Preview', '仪表板预览', 'ڈیش بورڈ کی پیشکش'),
    ('sec.label', 'Security & Privacy', '安全与隐私', 'اعتماد اور رازگوشتگی'),
    ('tech.label', 'Technology', '技术', 'ٹیکنالوجی'),
    ('future.label', 'Future Vision', '未来愿景', 'مستقبل کا ڈسپلے'),
    ('evidence.label', 'Evidence Handling', '证据处理', 'ثبوت کی نوصان'),
    ('faq.label', 'Frequently Asked', '常见问题', 'اکثر پوچھے جانے والے سوالات'),

    # Hero additional keys
    ('hero.liveCameras', 'Live Cameras', '实时摄像头', 'لاىو کیمرے'),
    ('hero.viewDashboard', 'View Dashboard', '查看仪表板', 'ڈیش بورڈ کو دیکھیں'),

    # Evidence section sub-keys
    ('evidence.desc', 'From detection to a fully audited record — every step logged and traceable.', '从检测到完全审计的记录 — 每个步骤都有日志且可追溯。', 'تشخيص سے مکمل ثبوت تک — ہر قدم ریکارڈ اور قابل تعقیب ہے۔'),
    ('evidence.detection', 'DETECTION', '检测', 'تشخيص'),
    ('evidence.event', 'EVENT', '事件', 'واقعہ'),
    ('evidence.evidence', 'EVIDENCE', '证据', 'ثبوت'),
    ('evidence.hash', 'HASH', '哈希', 'ہیش'),
    ('evidence.storage', 'STORAGE', '存储', 'محفوظ کرنا'),
    ('evidence.audit', 'AUDIT', '审计', 'جائزہ'),
    ('evidence.title', 'How Sentinel-X Handles Evidence', 'Sentinel-X 如何处理证据', 'سینٹینل-ایکس نے ثبوت کیسے ہینڈل کیا'),

    # FAQ section
    ('faq.desc', 'Straight answers, including where Sentinel-X currently falls short.', '直接的答案，包括 Sentinel-X 目前存在的不足之处。', 'براہ راست جوابات، اس بات کی حالت میں کہ Sentinel-X ابھی کمزور ہے۔'),
    ('faq.1.q', 'Do I need to buy new cameras?', '我需要买新的摄像头吗？', 'کیا مجھے نئے کیمرے خریدنے ہیں؟'),
    ('faq.1.a', 'No. Sentinel-X works with what you already have — webcam, IP camera, RTSP streams, or video files. It\'s an intelligence layer on top of existing infrastructure, not a hardware replacement.', '不。Sentinel-X 可以与您已有的设备一起使用 — 网络摄像头、IP 摄像头、RTSP 流或视频文件。这是一个智能层，而不是硬件更换。', 'نہیں۔ سینٹینل-ایکس آپ کے پاس موجودہ ہے — ویب کیمرا، IP کیمرا، RTSP اسٹreams یا ویڈیو فائلیں۔ یہ موجودہ انفراسٹرکچر پر انٹیلیجنس لائیئر ہے، ہارڈ ویئر کی بدلے نہیں۔'),
    ('faq.2.q', 'How accurate is the detection?', '检测准确度如何？', 'شناخت کتنا precise ہے؟'),
    ('faq.2.a', 'Detection uses YOLO11, but no AI system is infallible — false positives and false negatives happen. Accuracy depends on camera quality, resolution, angle, and lighting conditions, which the system reports as confidence scores per detection.', '检测使用 YOLO11，但没有 AI 系统是完美的 — 误报和漏报是正常的。准确度取决于摄像头质量、分辨率、角度和光照条件，系统会显示每个检测的置信度分数。', 'شناخت YOLO11 استعمال کرتا ہے، لیکن کوئی AI سسٹم مکمل طور پر سے ہی نہیں — غلط مثبت اور غلط منفی ہو سکتے ہیں۔ درستگی کیمرے کی کوالٹی، ریزولوشن، کون اور روشنی کی حالت پر منحصر ہے، جو سسٹم ہر شناخت کے لئے اعتماد اسکوئر کے طور پر بتاتا ہے۔'),
    ('faq.3.q', 'What happens when it detects something?', '当它检测到 something 时会发生什么？', 'جب یہ کچھ پاتتا ہے تو کیا ہوتا ہے؟'),
    ('faq.3.a', 'Detections become events that are severity-classified (Low through Critical), trigger real-time alerts on the dashboard, and automatically capture evidence screenshots with metadata. You review and investigate everything from the web dashboard.', '检测结果会成为严重性分类的事件 (从低到紧急)，在仪表板上触发实时警报，并自动捕获带有元数据的证据截图。你可以通过网页仪表板查看和调查所有内容。', 'شناخت ایسے واقعات بنتے ہیں جو سختی کے حساب سے طبقہ بند کیے گئے ہیں (کم از کم سے زیادہ تک)، ڈیش بورڈ پر ریئل ٹائم اٹریکٹس کو متحرک کرتے ہیں، اور خود بخود ثبوت کی اسکرین شاٹ کو میٹا ڈیٹا کے ساتھ پکڑ لیتا ہے۔ آپ تمام چیزوں کا جائزہ اور تحقیق ویب ڈیش بورڈ سے کر سکتے ہیں۔'),
    ('faq.4.q', 'Does it scale to multiple cameras?', '它可以扩展到多摄像头吗？', 'کیا یہ متعدد کیمرے تک پہنچ سکتا ہے؟'),
    ('faq.4.a', 'Yes. Multi-Camera Monitoring gives you a centralized view and processing of multiple feeds from a single dashboard, with Object Tracking maintaining consistent IDs across cameras.', '是的。多摄像头监控使您可以从单个仪表板集中查看和处理多个摄像头馈线，并通过目标跟踪在摄像头之间保持一致的 ID。', 'جی ہاں۔ ملٹی کیمرا مانیٹرنگ آپ کو ایک ڈیش بورڈ سے متعدد فیڈز کا مرکزی جائزہ اور پروسیسنگ دیتا ہے، جہاں آبجیکٹ ٹریکنگ کیمرے کے درمیان مکمل IDs برقرار رکھتا ہے۔'),
    ('faq.5.q', 'Is Sentinel-X production-ready?', 'Sentinel-X 生产就绪了吗？', 'کیا سینٹینل-ایکس پروڈکشن تیار ہے؟'),
    ('faq.5.a', 'It\'s a functional MVP (Version 1.0) — the pipeline runs end to end, but the limitations are real: AI detection can miss events, network reliability matters, and real-time throughput needs GPU acceleration. It\'s ready to evaluate, not yet ready for blind trust.', '它是一个功能性 MVP (版本 1.0) — 管道从头到尾都可以运行，但局限性是真实的：AI 检测可能会错过事件，网络可靠性很重要，实时吞吐量需要 GPU 加速。它已经可以评估，但还不适合盲目信任。', 'یہ ایک فعالیت MBA (ورژن 1.0) ہے — پائپ لائن مکمل طور پر چلتا ہے، لیکن حدود حقیقی ہیں: AI شناخت پا سکتا ہے واقعات کو چھوڑ دے، نیٹ ورک کی امانوس کام آتا ہے، اور ریئل ٹائم ٹھرواؤ GPU تیز رفتار کی ضرورت ہے۔ یہ ایویلویٹ کے لئے تیار ہے، ابھی بلاک خود میں اعتماد کے لئے تیار نہیں۔'),
    ('faq.6.q', 'What\'s Sentinel-X built on?', 'Sentinel-X 是建立在什麼上？', 'سینٹینل-ایکس کیسے بنایا گیا؟'),
    ('faq.6.a', 'Python, Flask, OpenCV, and YOLO11 for detection with ByteTrack for object tracking. The dashboard is a web interface you access from any modern browser.', 'Python、Flask、OpenCV 和 YOLO11 用于检测，ByteTrack 用于目标跟踪。仪表板是一个网页界面，你可以从任何现代浏览器访问。', 'Python، Flask، OpenCV، اور YOLO11 شناخت کے لئے، ByteTrack آئی بی بی ایس ٹریکنگ کے لئے۔ ڈیش بورڈ ایک ویب انٹرفیس ہے جسے آپ کسی بھی جدید براؤزر سے ایکسیس کر سکتے ہیں۔'),

    # Future roadmap keys
    ('future.roadmap.0', 'Advanced AI detection models', '先进的 AI 检测模型', 'اعجاز AI ڈیٹیکشن ماڈلز'),
    ('future.roadmap.1', 'Expanded threat detection types', '扩展的威胁检测类型', 'وسیع ہوئے دھمکیاں ڈیٹیکشن کی اقسام'),
    ('future.roadmap.2', 'Hardware edge deployment', '硬件边缘部署', 'ہارڈ ویئر انڈج کی تعمیر'),
    ('future.roadmap.3', 'Additional system integrations', '附加系统集成', 'اضافی سسٹم انٹیگریشن'),
    ('future.roadmap.4', 'Expanded analytics & reporting', '扩展的分析和报告', 'وسیع ہوئے تجزیہ و اظہار'),
    ('future.roadmap.5', 'Authorized identity integrations', '授权的身份集成', 'ممنوع شناخت انٹیگریشن'),

    # Cap loitering
    ('cap.loitering.title', 'Loitering Detection', '徘徊检测', 'لاٹھ پلائنگ کی نقل و نبات'),
    ('cap.loitering.desc', 'Flags individuals remaining in a monitored area beyond a defined time threshold.', '检测监控区域内的长时间逗留人员并生成警报。', 'متوقع مدت تک رکنے والے افراد کی نشاندہی اور اٹریکٹس کی تشکیل۔'),

    # Footer additional keys
    ('footer.brand', 'Sentinel-X', 'Sentinel-X', 'سینٹینل-ایکس'),
    ('footer.copyright', 'All rights reserved.', '版权所有。', 'تمامی حقوق محفوظ ہیں۔'),
    ('footer.builtWith', 'Built with', '构建于', 'کے ساتھ بنایا گیا'),
    ('footer.col.product', 'Product', '产品', 'پروڈکٹ'),
    ('footer.col.technology', 'Technology', '技术', 'ٹیکنالوجی'),
    ('footer.col.project', 'Project', '项目', 'پروجیکٹ'),
    ('footer.link.github', 'GitHub', 'GitHub', 'گٹ ہب'),
    ('footer.link.underTheHood', 'Under the Hood', '引擎盖下', 'انڈر دہ ہود'),
    ('footer.link.responsibleAI', 'Responsible AI', '负责的人工智能', 'ذمہ دارانہ ای آئی'),
    ('footer.link.limitations', 'Limitations', 'Limitations', 'حدود'),
    ('footer.dashboardPreview', 'Dashboard Preview', '仪表板预览', 'ڈیش بورڈ کی پیشکش'),
    ('footer.desc', 'AI-powered video security intelligence for existing camera infrastructure. A software-first MVP.', '基于现有摄像头基础设施的 AI 驱动视频安全智能。软件优先的 MVP。', 'موجودہ چیمرے انفراسٹرکچر کے لئے AI پاورڈ ویڈیو سیکورٹی انٹیلیجنس۔ سافٹ ویئر فرسٹ MVP۔'),

    # Future planned
    ('future.planned', 'PLANNED', '计划中', 'منصوبے'),

    # Nav keys
    ('nav.about', 'The Challenge', '挑战', 'چیلنج'),
    ('nav.applications', 'Applications', '应用程序', 'ایپلیکیشنز'),
    ('nav.dashboard', 'Dashboard Preview', '仪表板预览', 'ڈیش بورڈ کی پیشکش'),

    # Solution pipe threat
    ('solution.pipe.threat', 'THREAT', '威胁', 'خطرہ'),

    # Tech roles
    ('tech.python.role', 'core runtime', '核心运行时', 'کور رین ٹائم'),
    ('tech.flask.role', 'web framework', 'Web框架', 'ویب فریم ورک'),
    ('tech.opencv.role', 'video processing', '视频处理', 'ویڈیو پروسیسنگ'),
    ('tech.yolo.role', 'object detection', '目标检测', 'آئی بی ایس'),
    ('tech.bytetrack.role', 'object tracking', '目标跟踪', 'آئی بی بی ایس'),
    ('tech.sqlite.role', 'data storage', '数据存储', 'ڈیٹا اسٹوریج'),
    ('tech.restapi', 'REST API', 'REST API', 'REST API'),
    ('tech.restapi.role', 'integration', '集成', 'انٹیگریشن'),
]

# ─── Remove emojis from sec.* titles ───
def remove_emoji_from_value(line):
    """Remove emoji unicode escapes from a JS string value"""
    # Pattern: 'key': '\ud83d\udc4d Text' -> 'key': 'Text'
    return re.sub(r"'\\ud83[d-f]\\u[0-9a-f]{4}\s*", '', line)

# ─── Find dict boundaries ───
# EN dict: from "dicts.en = {" to the closing "};"
# ZH dict: from "dicts.zh = {" to the closing "};"
# UR dict: from "dicts.ur = {" to the closing "};"

content = ''.join(lines)
en_start = content.find('dicts.en = {')
zh_start = content.find('dicts.zh = {')
ur_start = content.find('dicts.ur = {')

# Find closing positions
en_close = content.find('};', content.rfind('}', content.rfind('}', en_start)))  # This won't work for nested
# Better approach: find "};" after each dict start, that's at the start of a line

def find_dict_end(content, start):
    """Find the closing }; of a dict starting at position start"""
    i = content.find('{', start)
    if i == -1: return -1
    depth = 1
    i += 1
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return i  # Position after the closing }

content = ''.join(lines)

en_end = find_dict_end(content, en_start)
zh_end = find_dict_end(content, zh_start)
ur_end = find_dict_end(content, ur_start)

print(f"EN dict: {en_start} to {en_end}")
print(f"ZH dict: {zh_start} to {zh_end}")
print(f"UR dict: {ur_start} to {ur_end}")

# ─── Remove emojis from sec.* titles in EN ───
en_section = content[en_start:en_end]
# Remove emoji escapes from sec.* titles in EN
en_section = re.sub(
    r"('sec\.([^']+)\.title':\s*)'\\ud83[d-f]\\u[0-9a-f]{4}\\u[0-9a-f]{4}\s*([^']*)'",
    r"\1'\3'",
    en_section
)
# Also handle double emoji
en_section = re.sub(
    r"('sec\.([^']+)\.title':\s*)'(\\ud83[d-f]\\u[0-9a-f]{4}\\u[0-9a-f]{4}\\u[0-9a-f]{4}\\u[0-9a-f]{4})\s*([^']*)'",
    r"\1'\3\4'",
    en_section
)

# Simpler approach: just replace the known emoji patterns
en_section = en_section.replace("'\ud83d\udd10 Authentication'", "'Authentication'")
en_section = en_section.replace("'\ud83d\udee1\ufe0f Protected Dashboard'", "'Protected Dashboard'")
en_section = en_section.replace("'\ud83d\udd11 Controlled Access'", "'Controlled Access'")
en_section = en_section.replace("'\ud83d\udcc1 Evidence Management'", "'Evidence Management'")
en_section = en_section.replace("'\ud83d\udcdc Event History'", "'Event History'")
en_section = en_section.replace("'\ud83e\udd16 Responsible AI'", "'Responsible AI'")

# ZH sec.* titles - remove emoji from sec.ai.title
zh_section = content[zh_start:zh_end]
zh_section = zh_section.replace("'\ud83d\udd10 \u4efd\u9a8c\u8bc1'", "'\u4efd\u9a8c\u8bc1'")
zh_section = zh_section.replace("'\ud83e\udd16 \u8d1f\u8d23\u4efb\u7684AI'", "'\u8d1f\u8d23\u4efb\u7684AI'")

# UR sec.* titles - they already have no emojis

# ─── Add new keys before the closing }; of each dict ───
# For EN: insert before the last line that contains just "  };"
# Find the line before the closing };

def add_keys_to_dict(content, dict_start, dict_end, keys_with_langs, lang_index):
    """Add new keys to a dict section"""
    section = content[dict_start:dict_end]
    
    # Find the position of the last entry (before };)
    # Look for the pattern: 'lastkey': 'value'\n  or 'lastkey': 'value',\n  }
    # We want to insert after the last entry
    
    # Find the closing };
    closing_match = re.search(r"\n\s*\};", section)
    if not closing_match:
        print("Could not find closing }")
        return content, section
    
    insert_pos = closing_match.start()
    
    # Build new entries
    new_entries = "\n"
    for key, en_val, zh_val, ur_val in keys_with_langs:
        val = [en_val, zh_val, ur_val][lang_index]
        escaped = val.replace("'", "\\'").replace("\n", "\\n")
        new_entries += f"    '{key}': '{escaped}',\n"
    
    # Insert
    new_section = section[:insert_pos] + new_entries + section[insert_pos:]
    return content[:dict_start] + new_section + content[dict_end:], new_section

# Update content with emoji fixes
content = content[:en_start] + en_section + content[en_end:]
content = content[:zh_start] + zh_section + content[zh_end:]

# Re-calculate boundaries after modifications
en_end = find_dict_end(content, en_start)
zh_end = find_dict_end(content, zh_start)
ur_end = find_dict_end(content, ur_start)

# Add keys to EN
content, _ = add_keys_to_dict(content, en_start, en_end, NEW_KEYS, 0)

# Re-calculate boundaries
zh_start = content.find('dicts.zh = {')
zh_end = find_dict_end(content, zh_start)
ur_start = content.find('dicts.ur = {')
ur_end = find_dict_end(content, ur_start)

# Add keys to ZH
content, _ = add_keys_to_dict(content, zh_start, zh_end, NEW_KEYS, 1)

# Re-calculate boundaries
ur_start = content.find('dicts.ur = {')
ur_end = find_dict_end(content, ur_start)

# Add keys to UR
content, _ = add_keys_to_dict(content, ur_start, ur_end, NEW_KEYS, 2)

# Also fix the double-escaped \u0688 in UR solution.pipe.dashboard
content = content.replace("'\\\\u0688\\u06cc\\u0634 \\u0628\\u0648\\u0631\\u0688'", "'\\u0688\\u06cc\\u0634 \\u0628\\u0648\\u0631\\u0688'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("All keys added and emojis removed")
