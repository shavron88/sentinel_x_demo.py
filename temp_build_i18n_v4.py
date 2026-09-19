"""
Comprehensive i18n builder - builds the entire i18n.js from scratch
by extracting current dicts, applying all transformations, and writing back.
"""
import re
import json

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── Parse existing dicts ───
def extract_dict(text, dict_name):
    """Extract a dict from the JS content and parse it into a Python dict"""
    pattern = rf"dicts\.{dict_name}\s*=\s*\{{(.*?)\n\s*\}};".replace("\\\\", "\\\\")
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        print(f"Could not find dict.{dict_name}")
        return {}
    
    dict_text = match.group(1)
    result = {}
    
    # Parse key-value pairs - handle single quotes and escaped values
    i = 0
    while i < len(dict_text):
        # Find a key pattern: 'key':
        key_match = re.match(r"\s*'([^']+)':\s*", dict_text[i:])
        if key_match:
            key = key_match.group(1)
            i += key_match.end()
            
            # Find the value - it's either '...' or could be complex
            # Find the opening quote
            val_start = dict_text.find("'", i)
            if val_start == -1:
                break
            
            # Find the closing quote (not escaped)
            j = val_start + 1
            while j < len(dict_text):
                if dict_text[j] == '\\' and j + 1 < len(dict_text):
                    j += 2
                    continue
                if dict_text[j] == "'":
                    break
                j += 1
            
            value = dict_text[val_start+1:j]
            result[key] = value
            i = j + 1
        else:
            # Skip to next character
            i += 1
    
    return result

# Extract dicts
en_dict = extract_dict(content, 'en')
zh_dict = extract_dict(content, 'zh')
ur_dict = extract_dict(content, 'ur')

print(f"EN: {len(en_dict)} keys")
print(f"ZH: {len(zh_dict)} keys")
print(f"UR: {len(ur_dict)} keys")

# ─── Define new keys ───
# (key, en, zh, ur)
NEW_KEYS = [
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
    ('evidence.desc', 'From detection to a fully audited record — every step logged and traceable.', '从检测到完全审计的记录 — 每个步骤都有日志且可追溯。', 'تشخيص سے مکمل ثبوت تک — ہر قدم ریکارڈ اور قابل تعقیب ہے۔'),
    ('evidence.title', 'How Sentinel-X Handles Evidence', 'Sentinel-X 如何处理证据', 'سینٹینل-ایکس نے ثبوت کیسے ہینڈل کیا'),
    ('evidence.detection', 'DETECTION', '检测', 'تشخيص'),
    ('evidence.event', 'EVENT', '事件', 'واقعہ'),
    ('evidence.evidence', 'EVIDENCE', '证据', 'ثبوت'),
    ('evidence.hash', 'HASH', '哈希', 'ہیش'),
    ('evidence.storage', 'STORAGE', '存储', 'محفوظ کرنا'),
    ('evidence.audit', 'AUDIT', '审计', 'جائزہ'),
    ('faq.label', 'Frequently Asked', '常见问题', 'اکثر پوچھے جانے والے سوالات'),
    ('faq.desc', 'Straight answers, including where Sentinel-X currently falls short.', '直接的答案，包括 Sentinel-X 目前存在的不足之处。', 'براہ راست جوابات، اس بات کی حالت میں کہ Sentinel-X ابھی کمزور ہے۔'),
    ('faq.1.q', 'Do I need to buy new cameras?', '我需要买新的摄像头吗？', 'کیا مجھے نئے کیمرے خریدنا ہیں؟'),
    ('faq.1.a', 'No. Sentinel-X works with what you already have — webcam, IP camera, RTSP streams, or video files. It\'s an intelligence layer on top of existing infrastructure, not a hardware replacement.', '不。Sentinel-X 可以与您已有的设备一起使用 — 网络摄像头、IP 摄像头、RTSP 流或视频文件。这是一个智能层，而不是硬件更换。', 'نہیں۔ سینٹینل-ایکس آپ کے پاس موجودہ ہے — ویب کیمرا، IP کیمرا، RTSP اسٹریمز یا ویڈیو فائلیں۔ یہ موجودہ انفراسٹرکچر پر انٹیلیجنس لائیئر ہے، ہارڈ ویئر کی بدلے نہیں۔'),
    ('faq.2.q', 'How accurate is the detection?', '检测准确度如何？', 'شناخت کتنا ایکیئر ہے؟'),
    ('faq.2.a', 'Detection uses YOLO11, but no AI system is infallible — false positives and false negatives happen. Accuracy depends on camera quality, resolution, angle, and lighting conditions, which the system reports as confidence scores per detection.', '检测使用 YOLO11，但没有 AI 系统是完美的 — 误报和漏报是正常的。准确度取决于摄像头质量、分辨率、角度和光照条件，系统会显示每个检测的置信度分数。', 'شناخت YOLO11 استعمال کرتا ہے، لیکن کوئی AI سسٹم مکمل طور پر سے ہی نہیں — غلط مثبت اور غلط منفی ہو سکتے ہیں۔ درستگی کیمرے کی کوالٹی، ریزولوشن، کون اور روشنی کی حالت پر منحصر ہے، جو سسٹم ہر شناخت کے لئے اعتماد اسکوئر کے طور پر بتاتا ہے۔'),
    ('faq.3.q', 'What happens when it detects something?', '当它检测到 something 时会发生什么？', 'جب یہ کچھ پاتتا ہے تو کیا ہوتا ہے؟'),
    ('faq.3.a', 'Detections become events that are severity-classified (Low through Critical), trigger real-time alerts on the dashboard, and automatically capture evidence screenshots with metadata. You review and investigate everything from the web dashboard.', '检测结果会成为严重性分类的事件 (从低到紧急)，在仪表板上触发实时警报，并自动捕获带有元数据的证据截图。你可以通过网页仪表板查看和调查所有内容。', 'شناخت ایسے واقعات بنتے ہیں جو سختی کے حساب سے طبقہ بند کیے گئے ہیں (کم از کم سے زیادہ تک)، ڈیش بورڈ پر ریئل ٹائم اٹریکٹس کو متحرک کرتے ہیں، اور خود بخود ثبوت کی اسکرین شاٹ کو میٹا ڈیٹا کے ساتھ پکڑ لیتا ہے۔ آپ تمام چیزوں کا جائزہ اور تحقیق ویب ڈیش بورڈ سے کر سکتے ہیں۔'),
    ('faq.4.q', 'Does it scale to multiple cameras?', '它可以扩展到多摄像头吗？', 'کیا یہ متعدد کیمرے تک پہنچ سکتا ہے؟'),
    ('faq.4.a', 'Yes. Multi-Camera Monitoring gives you a centralized view and processing of multiple feeds from a single dashboard, with Object Tracking maintaining consistent IDs across cameras.', '是的。多摄像头监控使您可以从单个仪表板集中查看和处理多个摄像头馈线，并通过目标跟踪在摄像头之间保持一致的 ID。', 'جی ہاں۔ ملٹی کیمرا مانیٹرنگ آپ کو ایک ڈیش بورڈ سے متعدد فیڈز کا مرکزی جائزہ اور پروسیسنگ دیتا ہے، جہاں آبجیکٹ ٹریکنگ کیمرے کے درمیان مکمل IDs برقرار رکھتا ہے۔'),
    ('faq.5.q', 'Is Sentinel-X production-ready?', 'Sentinel-X 生产就绪了吗？', 'کیا سینٹینل-ایکس پروڈکشن تیار ہے؟'),
    ('faq.5.a', 'It\'s a functional MVP (Version 1.0) — the pipeline runs end to end, but the limitations are real: AI detection can miss events, network reliability matters, and real-time throughput needs GPU acceleration. It\'s ready to evaluate, not yet ready for blind trust.', '它是一个功能性 MVP (版本 1.0) — 管道从头到尾都可以运行，但局限性是真实的：AI 检测可能会错过事件，网络可靠性很重要，实时吞吐量需要 GPU 加速。它已经可以评估，但还不适合盲目信任。', 'یہ ایک فعالیت MBA (ورژن 1.0) ہے — پائپ لائن مکمل طور پر چلتا ہے، لیکن حدود حقیقی ہیں: AI شناخت پا سکتا ہے واقعات کو چھوڑ دے، نیٹ ورک کی امانوس کام آتا ہے، اور ریئل ٹائم ٹھرواؤ GPU تیز رفتار کی ضرورت ہے۔ یہ ایویلویٹ کے لئے تیار ہے، ابھی بلاک خود میں اعتماد کے لئے تیار نہیں۔'),
    ('faq.6.q', 'What\'s Sentinel-X built on?', 'Sentinel-X 是建立在什麼上？', 'سینٹینل-ایکس کیسے بنایا گیا؟'),
    ('faq.6.a', 'Python, Flask, OpenCV, and YOLO11 for detection with ByteTrack for object tracking. The dashboard is a web interface you access from any modern browser.', 'Python、Flask、OpenCV 和 YOLO11 用于检测，ByteTrack 用于目标跟踪。仪表板是一个网页界面，你可以从任何现代浏览器访问。', 'Python، Flask، OpenCV، اور YOLO11 شناخت کے لئے، ByteTrack آئی بی بی ایس ٹریکنگ کے لئے۔ ڈیش بورڈ ایک ویب انٹرفیس ہے جسے آپ کسی بھی جدید براؤزر سے ایکسیس کر سکتے ہیں۔'),
    ('future.roadmap.0', 'Advanced AI detection models', '先进的 AI 检测模型', 'اعجاز AI ڈیٹیکشن ماڈلز'),
    ('future.roadmap.1', 'Expanded threat detection types', '扩展的威胁检测类型', 'وسیع ہوئے دھمکیاں ڈیٹیکشن کی اقسام'),
    ('future.roadmap.2', 'Hardware edge deployment', '硬件边缘部署', 'ہارڈ ویئر انڈج کی تعمیر'),
    ('future.roadmap.3', 'Additional system integrations', '附加系统集成', 'اضافی سسٹم انٹیگریشن'),
    ('future.roadmap.4', 'Expanded analytics & reporting', '扩展的分析和报告', 'وسیع ہوئے تجزیے و اظہار'),
    ('future.roadmap.5', 'Authorized identity integrations', '授权的身份集成', 'ممنوع شناخت انٹیگریشن'),
    ('cap.loitering.title', 'Loitering Detection', '徘徊检测', 'لاٹھ پلائنگ کی نقل و نبات'),
    ('cap.loitering.desc', 'Flags individuals remaining in a monitored area beyond a defined time threshold.', '检测监控区域内的长时间逗留人员并生成警报。', 'متوقع مدت تک رکنے والے افراد کی نشاندہی اور اٹریکٹس کی تشکیل۔'),
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
    ('future.planned', 'PLANNED', '计划中', 'منصوبے'),
    ('nav.about', 'The Challenge', '挑战', 'چیلنج'),
    ('nav.applications', 'Applications', '应用程序', 'ایپلیکیشنز'),
    ('nav.dashboard', 'Dashboard Preview', '仪表板预览', 'ڈیش بورڈ کی پیشکش'),
    ('solution.pipe.threat', 'THREAT', '威胁', 'خطرہ'),
    ('hero.liveCameras', 'Live Cameras', '实时摄像头', 'لاىو کیمرے'),
    ('hero.viewDashboard', 'View Dashboard', '查看仪表板', 'ڈیش بورڈ کو دیکھیں'),
    ('tech.python.role', 'core runtime', '核心运行时', 'کور رین ٹائم'),
    ('tech.flask.role', 'web framework', 'Web框架', 'ویب فریم ورک'),
    ('tech.opencv.role', 'video processing', '视频处理', 'ویڈیو پروسیسنگ'),
    ('tech.yolo.role', 'object detection', '目标检测', 'آئی بی ایس'),
    ('tech.bytetrack.role', 'object tracking', '目标跟踪', 'آئی بی بی ایس'),
    ('tech.sqlite.role', 'data storage', '数据存储', 'ڈیٹا اسٹوریج'),
    ('tech.restapi', 'REST API', 'REST API', 'REST API'),
    ('tech.restapi.role', 'integration', '集成', 'انٹیگریشن'),
]

# Add new keys to each dict
for key, en_val, zh_val, ur_val in NEW_KEYS:
    en_dict[key] = en_val
    zh_dict[key] = zh_val
    ur_dict[key] = ur_val

# Remove emojis from sec.* titles in EN
for k in list(en_dict.keys()):
    if k.startswith('sec.') and k.endswith('.title'):
        # Remove emoji unicode escapes
        en_dict[k] = re.sub(r'\\[ud83][udfce0][uf\d]{4}\\u[0-9a-f]{4}\\s*', '', en_dict[k])
        en_dict[k] = re.sub(r'\\ud83[def]\\u[0-9a-f]{4}\\u[0-9a-f]{4}\s*', '', en_dict[k])
        # Hardcoded fixes
        en_dict[k] = en_dict[k].replace('\ud83d\udd10', '').replace('\ud83d\udee1\ufe0f', '').replace('\ud83d\udd11', '').replace('\ud83d\udcc1', '').replace('\ud83d\udcdc', '').replace('\ud83e\udd16', '')
        en_dict[k] = en_dict[k].strip()

# Remove emoji from ZH sec.ai.title
zh_dict['sec.ai.title'] = '负责任的AI'.replace('的', 'AI') if 'sec.ai.title' in zh_dict else zh_dict.get('sec.ai.title', '负责任的AI')
# Actually just remove the emoji
if 'sec.ai.title' in zh_dict:
    zh_dict['sec.ai.title'] = re.sub(r'\\ud83[def]\\u[0-9a-f]{4}\s*', '', zh_dict['sec.ai.title'])

# Fix double-escaped UR solution.pipe.dashboard
ur_dict['solution.pipe.dashboard'] = '\u0688\u06cc\u0634 \u0628\u0648\u0631\u0688'  # ٹیش بورڈ (proper)

# ─── Generate JS output ───
def escape_js(s):
    """Escape a string for use in JS single-quoted string"""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")

def dict_to_js(d, indent="    "):
    """Convert a Python dict to JS object literal"""
    lines = []
    for k, v in d.items():
        lines.append(f"{indent}'{k}': '{escape_js(v)}',")
    return "\n".join(lines)

# Find the positions to replace
en_match = re.search(r"dicts\.en\s*=\s*\{.*?\n\s*\};", content, re.DOTALL)
zh_match = re.search(r"dicts\.zh\s*=\s*\{.*?\n\s*\};", content, re.DOTALL)
ur_match = re.search(r"dicts\.ur\s*=\s*\{.*?\n\s*\};", content, re.DOTALL)

print(f"\nEN match: {en_match.start() if en_match else 'NOT FOUND'} to {en_match.end() if en_match else 'NOT FOUND'}")
print(f"ZH match: {zh_match.start() if zh_match else 'NOT FOUND'} to {zh_match.end() if zh_match else 'NOT FOUND'}")
print(f"UR match: {ur_match.start() if ur_match else 'NOT FOUND'} to {ur_match.end() if ur_match else 'NOT FOUND'}")

# Build new dicts
new_en = f"dicts.en = {{\n{dict_to_js(en_dict)}\n  }}"
new_zh = f"dicts.zh = {{\n{dict_to_js(zh_dict)}\n  }}"
new_ur = f"dicts.ur = {{\n{dict_to_js(ur_dict)}\n  }}"

# But we need to keep the comments and section structure
# Let's just replace the dict content

if en_match:
    content = content[:en_match.start()] + new_en + content[en_match.end():]
    print("Replaced EN dict")

if zh_match:
    # Re-find after EN replacement
    zh_match = re.search(r"dicts\.zh\s*=\s*\{.*?\n\s*\};", content, re.DOTALL)
    if zh_match:
        content = content[:zh_match.start()] + new_zh + content[zh_match.end():]
        print("Replaced ZH dict")

if ur_match:
    # Re-find after ZH replacement
    ur_match = re.search(r"dicts\.ur\s*=\s*\{.*?\n\s*\};", content, re.DOTALL)
    if ur_match:
        content = content[:ur_match.start()] + new_ur + content[ur_match.end():]
        print("Replaced UR dict")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nFile rebuilt successfully")
print(f"EN: {len(en_dict)} keys, ZH: {len(zh_dict)} keys, UR: {len(ur_dict)} keys")
