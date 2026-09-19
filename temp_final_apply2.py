"""
Comprehensive i18n fix script v2:
1. Add missing EN keys (section labels, evidence, FAQ, hero, future roadmap, footer, cap.loitering)
2. Remove emojis from sec.* titles in EN
3. Add all missing UR keys with Urdu translations
4. Add all missing ZH keys with Chinese translations
5. Fix double-escaped UR solution.pipe.dashboard (already done in previous run)
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── EN additions ───
EN_ADDITIONS = {
    # Section labels
    'problem.label': 'The Challenge',
    'solution.label': 'The Solution',
    'how.label': 'How It Works',
    'cap.label': 'Core Capabilities',
    'lim.label': 'Responsible Disclosure',
    'use.label': 'Applications',
    'preview.label': 'Dashboard Preview',
    'sec.label': 'Security & Privacy',
    'tech.label': 'Technology',
    'future.label': 'Future Vision',
    
    # Hero additional keys
    'hero.liveCameras': 'Live Cameras',
    'hero.viewDashboard': 'View Dashboard',
    
    # Evidence section
    'evidence.title': 'Evidence Gallery',
    'evidence.desc': 'Captured evidence from detected security events.',
    
    # FAQ section
    'faq.title': 'Frequently Asked Questions',
    'faq.1.q': 'What is Sentinel-X?',
    'faq.1.a': 'Sentinel-X is an AI-powered video surveillance platform.',
    'faq.2.q': 'Can it work with existing cameras?',
    'faq.2.a': 'Yes, Sentinel-X works with your existing camera infrastructure.',
    'faq.3.q': 'What AI models does it use?',
    'faq.3.a': 'Sentinel-X uses YOLO11 for object detection and ByteTrack for tracking.',
    'faq.4.q': 'Is my data secure?',
    'faq.4.a': 'Yes, all data is stored securely with proper encryption.',
    'faq.5.q': 'How do I get started?',
    'faq.5.a': 'Sign up for an account and connect your cameras.',
    'faq.6.q': 'Is there a free demo?',
    'faq.6.a': 'Yes, you can explore the demo without an account.',
    
    # Future roadmap
    'future.roadmap.0': 'Integration',
    'future.roadmap.1': 'Deployment',
    'future.roadmap.2': 'Minimum',
    'future.roadmap.3': 'Future',
    'future.roadmap.4': 'Technology',
    'future.roadmap.5': 'Vision',
    
    # Cap loitering
    'cap.loitering.title': 'Loitering Detection',
    'cap.loitering.desc': 'Detects prolonged presence in monitored areas and generates alerts.',
    
    # Footer additional keys
    'footer.brand': 'Sentinel-X',
    'footer.copyright': 'All rights reserved.',
    'footer.builtWith': 'Built with',
    'footer.col.product': 'Product',
    'footer.col.technology': 'Technology',
    'footer.col.project': 'Project',
    'footer.link.github': 'GitHub',
    'footer.link.underTheHood': 'Under the Hood',
    'footer.link.responsibleAI': 'Responsible AI',
    'footer.link.limitations': 'Limitations',
    'footer.dashboardPreview': 'Dashboard Preview',
}

# ─── Urdu translations ───
UR_ADDITIONS = {
    'problem.label': '\u0686یلنج',
    'solution.label': '\u062dل',
    'how.label': '\u06a9سے کام کرتا ہے',
    'cap.label': '\u0628نیادی صلاحیتيں',
    'lim.label': '\u0630مہِ دارانہ اخبارات',
    'use.label': '\u0627پلیکیشنز',
    'preview.label': '\u0688ش بورڈ پیشکش',
    'sec.label': '\u0627ور اور رازگوشتگی',
    'tech.label': '\u0679کنالوجی',
    'future.label': 'مستقبل کا ڈسپلے',
    'hero.liveCameras': '\u0644ائیو کیمرے',
    'hero.viewDashboard': '\u0688ش بورڈ کو دیکھیں',
    'evidence.title': '\u0633بت کی دیوانی',
    'evidence.desc': 'مشینوں کی حفاظت اور جمع کرنا کے لئے تیار کیا ہے۔',
    'faq.title': '\u0627کثر پوچھے جانے والے سوالات',
    'faq.1.q': 'سینٹینل-ایکس کیا ہے؟',
    'faq.1.a': 'سینٹینل-ایکس ای آئی پاورڈ ویڈیو سرویلنس پلیٹ فارم ہے۔',
    'faq.2.q': 'کیا اسے موجودہ چیمرے استعمال کیے جا سکتے ہیں؟',
    'faq.2.a': 'جی ہاں، سینٹینل-ایکس موجودہ چیمرے انفراسٹرکچر کے ساتھ کام کرتا ہے۔',
    'faq.3.q': 'AI کتنا زندہ ہے؟',
    'faq.3.a': 'سینٹینل-ایکس ای آئی کی شناخت کے ساتھ زندہ ویڈیو پروسیسنگ فراہم کرتا ہے۔',
    'faq.4.q': 'کیا یہ جامع ہے؟',
    'faq.4.a': 'سینٹینل-ایکس ایک مکمل ذمہ دارانہ ای آئی سسٹم ہے۔',
    'faq.5.q': 'ڈیش بورڈ کیسے استعمال کیا جاتا ہے؟',
    'faq.5.a': 'ویب بیسچ ڈیش بورڈ سے آسانی سے استعمال کریں۔',
    'faq.6.q': 'کیا یہ مفت ہے؟',
    'faq.6.a': 'سینٹینل-ایکس مفت ڈیمو کے ساتھ دستیاب ہے۔',
    'future.roadmap.0': 'انٹیگریشن',
    'future.roadmap.1': 'ڈیپلائمنٹ',
    'future.roadmap.2': 'کم از کم',
    'future.roadmap.3': 'مستقبل',
    'future.roadmap.4': 'ٹیکنالوجی',
    'future.roadmap.5': 'انٹیلیجنس',
    'cap.loitering.title': '\u0644ٹرنگ کی نقل و نبات',
    'cap.loitering.desc': 'متوقع مدت تک رکنے والے افراد کی پہچان اور انٹیلیجنٹ اٹریکٹ کرنا۔',
    'footer.brand': 'سینٹینل-ایکس',
    'footer.copyright': '\u062a محفوظ ہیں۔',
    'footer.builtWith': 'کے ساتھ بنایا گیا',
    'footer.col.product': 'پروڈکٹ',
    'footer.col.technology': 'ٹیکنالوجی',
    'footer.col.project': 'پروجیکٹ',
    'footer.link.github': 'گٹ ہب',
    'footer.link.underTheHood': 'انڈر دہ ہود',
    'footer.link.responsibleAI': 'ذمہ دارانہ ای آئی',
    'footer.link.limitations': 'حدود',
    'footer.dashboardPreview': 'ڈیش بورڈ کی پیشکش',
    
    # Existing missing UR keys (from the 37 missing)
    'future.aiProc': 'AI پروسیسنگ',
    'future.alerts': 'اٹریکٹس اور واقعات',
    'future.cctv': 'سی سی ٹی وی کیمرے',
    'future.cloud': 'کلاؤڈ ڈیش بورڈ',
    'future.disclaimer': 'اٹیج باکس مستقبل کا منصوبہ ہے۔ موجودہ سینٹینل-ایکس صرف سافٹ ویئر پلیٹ فارم ہے۔',
    'future.edgeDesc': 'سینٹینل-ایکس ای آئی پ्रوسیسنگ کو کیمرے انفراسٹرکچر کے قریب لانے کے لئے ایک وختہ اینج کمپیوٹنگ آئین ہے۔',
    'preview.camera01': 'کیمرا_01 — مین انٹرانس',
    'preview.createAccount': 'اپنا سینٹینی-ایکس اکاؤنٹ بنائیں',
    'preview.detChart': 'AI ڈیٹیکشن چارٹ',
    'preview.detItems': 'افراد · ای موٹی · اٹریکٹس',
    'preview.kpi.accuracy': ' Accuracy',
    'preview.kpi.alerts': ' آج کے اٹریکٹس',
    'preview.kpi.cameras': ' کیمرے',
    'preview.kpi.threat': ' خطرے کی سطح',
    'preview.liveFeed': ' لائیو کیمرا فیڈ',
    'preview.mockLabel': ' سینٹینی-ایکس ڈیش بورڈ',
    'preview.ready': ' اپنے کیمروں کو ذہیہ سیکیورٹی سسٹم بنانے کے لئے تیار ہیں؟',
    'sec.access.desc': ' سی ایس ایس ایف ٹوکن پروٹیکشن اسٹیٹ کے تبدیلی والے آپریشن پر۔ رینج لک ڈاؤن ان تھیٹ ایڈجسٹمنٹ پر۔',
    'sec.access.title': ' کنٹرولڈ اینکسس',
    'sec.ai.desc': ' AI ڈیٹیکشن کے نتائج کو یقینی اعتماد سکور کے ساتھ پیش کیا جاتا ہے۔ سسٹم مدد کے لئے ڈیزائین کیا گیا ہے، اننھیں تبدیل نہیں۔',
    'sec.ai.title': ' ریسپانسبل AI',
    'sec.auth.desc': ' سیشن پر مبنی تھیٹ ایڈجسٹمنٹ کے ساتھ۔ تمام یوزرز ڈیش بورڈ تک رسائی کے لئے سائن ان کرنا ضروری ہے۔',
    'sec.auth.title': ' یقینی تھیٹ ایڈجسٹمنٹ',
    'sec.evidence.desc': ' واقعات کے ثبوت کی ایک ڈیٹا بیس میں محفوظ ہیں۔',
    'sec.evidence.title': ' ثبوت کی مینیجمنٹ',
    'sec.history.desc': ' بنیادی رازگوشتگی کی تاریخ کے ساتھ مشمولہ۔',
    'sec.history.title': ' واقعات کی تاریخ',
    'sec.protected.desc': ' ہر ایک ڈیش بورڈ راٹ محفوظ ہے۔',
    'sec.protected.title': ' محفوظ ڈیش بورڈ',
    'tech.bytetrack': ' آئی بی بی ایس',
    'tech.flask': ' ویب فریم ورک',
    'tech.jscss': ' ڈیش بورڈ یو آئی',
    'tech.opencv': ' ویڈیو پروسیسنگ',
    'tech.python': ' کور رین ٹائم',
    'tech.sqlite': ' ڈیٹا اسٹوریج',
    'tech.yolo': ' آئی بی ایس',
}

# ─── ZH translations for the new EN keys ───
ZH_ADDITIONS = {
    'problem.label': '挑战',
    'solution.label': '解决方案',
    'how.label': '工作原理',
    'cap.label': '核心功能',
    'lim.label': '负责声明',
    'use.label': '应用',
    'preview.label': '仪表板预览',
    'sec.label': '安全与隐私',
    'tech.label': '技术',
    'future.label': '未来愿景',
    'hero.liveCameras': '实时摄像头',
    'hero.viewDashboard': '查看仪表板',
    'evidence.title': '证据库',
    'evidence.desc': '从检测到的安全事件中捕获的证据。',
    'faq.title': '常见问题',
    'faq.1.q': '什么是 Sentinel-X？',
    'faq.1.a': 'Sentinel-X 是一个 AI 驱动的视频监控平台。',
    'faq.2.q': '它可以与现有摄像头一起使用吗？',
    'faq.2.a': '是的，Sentinel-X 可以与您现有的摄像头基础设施一起使用。',
    'faq.3.q': '它使用哪些 AI 模型？',
    'faq.3.a': 'Sentinel-X 使用 YOLO11 进行目标检测和 ByteTrack 进行跟踪。',
    'faq.4.q': '我的数据安全吗？',
    'faq.4.a': '是的，所有数据都经过适当的加密安全存储。',
    'faq.5.q': '如何开始使用？',
    'faq.5.a': '注册账户并连接您的摄像头即可开始。',
    'faq.6.q': '有免费演示吗？',
    'faq.6.a': '是的，您可以在不注册账户的情况下浏览演示。',
    'future.roadmap.0': '集成',
    'future.roadmap.1': '部署',
    'future.roadmap.2': '最低要求',
    'future.roadmap.3': '未来',
    'future.roadmap.4': '技术',
    'future.roadmap.5': '愿景',
    'cap.loitering.title': '徘徊检测',
    'cap.loitering.desc': '检测监控区域内的长时间逗留人员并生成警报。',
    'footer.brand': 'Sentinel-X',
    'footer.copyright': '版权所有。',
    'footer.builtWith': '构建于',
    'footer.col.product': '产品',
    'footer.col.technology': '技术',
    'footer.col.project': '项目',
    'footer.link.github': 'GitHub',
    'footer.link.underTheHood': '引擎盖下',
    'footer.link.responsibleAI': '负责的人工智能',
    'footer.link.limitations': '限制',
    'footer.dashboardPreview': '仪表板预览',
}

# ─── Remove emojis from sec.* titles in EN ───
# These are lines like: 'sec.auth.title': '\ud83d\udd10 Authentication',
# We need to remove the emoji escape sequences
def remove_emojis_from_line(line):
    """Remove emoji unicode escapes from a JS string value"""
    # Pattern: 'key': '\ud83d\xxxx\yyyy Text'
    # Match everything after the opening quote until we hit actual text
    return re.sub(r"('\\ud83d\\[0-9a-f]{4}\\u[0-9a-f]{4}.*?\\u[0-9a-f]{4}\s*)", '', line)

# More robust approach: find sec.* titles and clean them
sec_title_pattern = re.compile(
    r"('sec\.(\w+)\.title':\s*)'((?:\\ud83d\\u[0-9a-f]{4}.*?\\u[0-9a-f]{4}\s*)?)([^']+)'",
    re.DOTALL
)

def clean_sec_title(match):
    prefix = match.group(1)
    title_text = match.group(4).strip()
    return f"{prefix}'{title_text}'"

content = sec_title_pattern.sub(clean_sec_title, content)
print("Cleaned sec.* titles in EN")

# ─── EN additions ───
# The EN dict ends with 'signup.errorConn' which has no trailing comma
en_end_pattern = re.compile(r"(    'signup\.errorConn':[^,]+,?)(\n\s*\};)")
en_end_match = en_end_pattern.search(content)
if en_end_match:
    # Find position to insert (before };)
    before_brace = en_end_match.end(1)
    after_comma = en_end_match.end(1)  # This is after the ,
    
    # Check if there's a comma after the value
    if content[en_end_match.start(2)-1] == ',':
        insert_pos = en_end_match.start(2)  # After the comma
    else:
        # Need to add comma
        insert_pos = en_end_match.end(1)
        # Actually let me just insert before };
        insert_pos = en_end_match.start(2)
        # Check what's right before }
        # content[insert_pos-1] should be the last char of the value
    
    new_entries = "\n"
    for key, val in EN_ADDITIONS.items():
        escaped = val.replace("'", "\\'")
        new_entries += f"    '{key}': '{escaped}',\n"
    
    # Insert before the };
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added EN keys successfully")
else:
    print("ERROR: Could not find EN dict closing")
    # Try alternate pattern
    en_end_alt = re.search(r"'signup\.errorConn':\s*'[^']+'\s*\n\s*\};", content)
    if en_end_alt:
        print("Found alternate pattern")
    else:
        print("Could not find alternate pattern either")

# ─── ZH additions ───
# Find ZH dict end - it ends with login.errorConnection
zh_end_pattern = re.search(r"(    'login\.errorConnection':\s*'[^']+'\s*)\n(\s*\};)", content)
if zh_end_pattern:
    insert_pos = zh_end_pattern.end(1)  # After the value, before \n};
    new_entries = "\n"
    for key, val in ZH_ADDITIONS.items():
        escaped = val.replace("'", "\\'")
        new_entries += f"    '{key}': '{escaped}',\n"
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added ZH keys successfully")
else:
    print("ERROR: Could not find ZH dict closing")

# ─── UR additions ───
# Find UR dict end - it ends with footer.text
ur_end_pattern = re.search(r"(    'footer\.text':\s*'[^']+'\s*)\n(\s*\};)", content)
if ur_end_pattern:
    insert_pos = ur_end_pattern.end(1)
    new_entries = "\n"
    for key, val in UR_ADDITIONS.items():
        new_entries += f"    '{key}': '{val}',\n"
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added UR keys successfully")
else:
    print("ERROR: Could not find UR dict closing")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nFile updated: {file_path}")
