#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []
def track(label):
    changes.append(label)
    print(f"  OK: {label}")

# ═══════════════════════════════════════════════════════
# HELPER: Extract a dict's content as Python dict
# ═══════════════════════════════════════════════════════
def extract_js_dict(content, dict_name):
    r"""Extract a JS object literal as a Python dict"""
    pattern = re.compile(re.escape(dict_name) + r" = \{")
    match = pattern.search(content)
    if not match:
        return None, -1, -1
    start = match.end()
    # Find matching closing brace
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    dict_str = content[start:i-1]
    # Parse key-value pairs
    result = {}
    # Match 'key': 'value' patterns (handling escaped quotes and \uXXXX)
    # Simple approach: find all 'key': 'value' pairs
    pair_pattern = r"'([^']*)':\s*'((?:[^'\\]|\\.)*)',"
    for m in re.finditer(pair_pattern, dict_str):
        key = m.group(1)
        val = m.group(2)
        result[key] = val
    return result, start, i

def rebuild_dict_section(content, dict_name, new_entries, indent="    "):
    r"""Replace a dict's content with new entries"""
    pattern = re.compile(re.escape(dict_name) + r" = \{")
    match = pattern.search(content)
    if not match:
        return content, False
    
    start = match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    
    lines = []
    for key, val in new_entries.items():
        lines.append(f"{indent}'{key}': '{val}',")
    new_content = "\n" + "\n".join(lines) + "\n  "
    
    return content[:start] + new_content + content[i:], True

# ═══════════════════════════════════════════════════════
# PARSE EXISTING DICTS
# ═══════════════════════════════════════════════════════

en_dict, en_start, en_end = extract_js_dict(content, "dicts.en")
zh_dict, zh_start, zh_end = extract_js_dict(content, "dicts.zh")
ur_dict, ur_start, ur_end = extract_js_dict(content, "dicts.ur")

print(f"EN dict: {len(en_dict)} keys")
print(f"ZH dict: {len(zh_dict)} keys")
print(f"UR dict: {len(ur_dict)} keys")

# ═══════════════════════════════════════════════════════
# UR DICTIONARY UPDATES
# ═══════════════════════════════════════════════════════

# 1. Update changed values (EN text changed, UR needs to follow)
ur_updates = {
    # Hero - completely changed
    'hero.title1': "صرف ریکارڈ نہیں کرو، جو ہو گیا۔",
    'hero.title2': "سمجھ لو کہ ابھی کیا ہو رہا ہے۔",
    'hero.subtitle': "Sentinel-X اٹھار سے متحرک ذہین ویڈیو نگرانی کی پلیٹ فارم بناتا ہے — پتا لگاتا ہے، ٹریک کرتا ہے، اور دھمکیوں کی نشاندہی کرتا ہے۔",
    
    # Problem - changed wording
    'problem.title': "روایتی CCTV صرف ریکارڈ کرتا ہے۔ یہ سمجھتا نہیں۔",
    'problem.1.desc': "انسان ایک ہی وقت پر ہر کیمرے کی فڈ ہر کچھ نہیں دیکھ سکتا۔ توجہ کی تھکاؤ واقعات کو مفقود کر دیتی ہے۔",
    'problem.3.desc': "کئی گھنٹوں کی ریکارڈنگ کو دوبارہ جانچنے میں وقت لگتا ہے، یہ سست اور وسیع وسائل کی مانگ ہے۔",
    'problem.4.desc': "CCTV صرف یہ ریکارڈ کرتا ہے — یہ کسی وقت آگاہ نہیں کرتا۔",
    
    # Solution - minor change
    'solution.desc': "Sentinel-X کیمرا اٹھار سے متحرک ذہین ویڈیو نگرانی کی پلیٹ فارم بناتا ہے — خام فوڈیج کو منظم قابل عمل سیکیورٹی واقعات میں تبدیل کرتا ہے۔",
    
    # Use cases - added 'real'
    'use.desc': "Sentinel-X ان محول کے لئے بنائے گیا ہے جہاں مسلسل ڈیلی کیمرا نگرانی اضافی حقیقی سیکیورٹی کی قدر رکھتی ہے۔",
    
    # Preview - added 'Demo data shown below.'
    'preview.desc': "ایک متحدہ ویب ڈیش بورڈ جو کیمرے رصد کرتا ہے، واقعات کا جائزہ لےتا ہے، ثبوت کی جانچ کرتا ہے، اور سیکیورٹی کے رجحانات کا جائزہ لےتا ہے۔ ڈیمو ڈیٹا مندرج ذیل ہے۔",
    
    # Footer - changed
    'footer.text': "Sentinel-X AI ایج سرویلینس پلیٹ فارم · ورژن 1.0 · Python، Flask، OpenCV، YOLO11 کے ساتھ تیار",
    
    # cap.alerts.desc - removed 'system'
    'cap.alerts.desc': "حد سے زیادہ پروگرام نیاگری کے ساتھ واقعات کو کم، درمیانی، اعلیٰ یا طبیعی طور پر تقسیم کرتا ہے۔",
}

# 2. Add new keys to UR dict
ur_new = {
    'hero.liveCameras': "4 دوربینوں پر لائیو",
    'hero.viewDashboard': "ڈیش بورڈ دیکھیں",
    'problem.label': "// 01 — مسئلہ",
    'solution.label': "// 02 — حل",
    'solution.pipe.threat': "دھمکی",
    'how.label': "// 03 — کام کرنے کا طریقہ",
    'cap.label': "// 04 — صلاحیتیں",
    'cap.loitering.title': "بے جانبی کی تشخیص",
    'cap.loitering.desc': "متعین شدہ وقت کے حد سے زیادہ مانیٹرڈ علاقے میں باقی رہنے والے افراد کی نشاندہی کرتا ہے۔",
    'adv.label': "// 05 — فوائد",
    'lim.label': "// 06 — ذمہ داری",
    'use.label': "// 07 — امکانات",
    'preview.label': "// 08 — ڈیش بورڈ پیش نظر",
    'sec.label': "// 09 — سیکیورٹی اور رازداری",
    'sec.auth.title': "تصدیقی ثبوت",
    'sec.auth.desc': "جلسوں پر مبنی تصدیق، قابل ترتیب ٹائم آؤٹ کے ساتھ۔ تمام صارفین کو ڈیش بورڈ تک رسائی کے لئے سائن ان کرنا ضروری ہے۔",
    'sec.protected.title': "محفوظ ڈیش بورڈ",
    'sec.protected.desc': "ہر ڈیش بورڈ راستہ تصدیق کے سامنے محفوظ ہے۔ غیر مصدقح د visitors کو دوبارہ رجوع کر دیا جاتا ہے۔",
    'sec.access.title': "محدود رسائی",
    'sec.access.desc': "تبدیلیوں پر CSRF ٹوکن کی حفاظت۔ تصدیقی نقاط پر رفعِ رفتار۔",
    'sec.evidence.title': "ثبوت کی انتظام",
    'sec.evidence.desc': "واقعات کے ثبوت منظم ڈیٹابیس میں محفوظ ہیں، جس میں وقت، کیمرا حوالہ اور کمانٹی ہیشنگ شامل ہے۔",
    'sec.history.title': "واقعات کی تاریخ",
    'sec.history.desc': " تمام واقعات کے ساتھ مکمل.audit ٹریل، درج ذیل ہے — سختی درجہ بندی، کیمرا سورس، اور علاقائی معلومات۔",
    'sec.ai.title': "ذمہ دار AI",
    'sec.ai.desc': "AI ڈیٹیکشن کے نتائج کے ساتھ پیغام نمائیں گئے ہیں۔ نظام معاونت کے لئے ڈیزائن ہوا ہے، انسانی فیصلہ سے بہتر نہیں۔",
    'tech.label': "// 10 — ٹیکنالوجی",
    'tech.restapi': "انٹیگریشن",
    'future.label': "// 12 — مستقبل کا خیال",
    'future.planned': "منصوبہ بند",
    'future.roadmap.0': "اعلیٰ AI ڈیٹیکشن ماڈلز",
    'future.roadmap.1': "وسیع کردیا ہوا دھمکی ڈیٹیکشن کی اقسام",
    'future.roadmap.2': "ہارڈ ویئر ایج ڈپلائمنٹ",
    'future.roadmap.3': "اضافی سسٹم انٹیگریشنز",
    'future.roadmap.4': "وسیع تجزیہ و رپورٹنگ",
    'future.roadmap.5': "منظور شدہ شناختی انٹیگریشنز",
    'footer.brand': "AI سے متحرک ذہین ویڈیو سیکیورٹی انٹی لگنگ ایمریجنسی پلیٹ فارم۔ ایک سافٹ ویئر پہلاں پلیٹ فارم۔",
    'footer.copyright': "Sentinel-X AI ایج سرویلینس پلیٹ فارم · ورژن 1.0",
    'footer.builtWith': "Python، Flask، OpenCV، YOLO11 کے ساتھ تیار",
    'footer.col.product': "پروڈکٹ",
    'footer.col.technology': "ٹیکنالوجی",
    'footer.col.project': "پروجیکٹ",
    'footer.link.github': "GitHub ریپوزٹری",
    'footer.link.underTheHood': "اندر کی چیزیں",
    'footer.link.responsibleAI': "ذمہ دار AI",
    'footer.link.limitations': "احتمالات اور استعمال",
    'footer.dashboardPreview': "ڈیش بورڈ پیش نظر",
    'evidence.label': "// 11 — ثبوت کی نقل و اہتمام",
    'evidence.title': "Sentinel-X کیسے ثبوت کو ہینڈل کرتا ہے",
    'evidence.desc': "جب سے کوئی چیز پتا چلتا ہے اس سے لے کر مکمل طور پر جانچے گئے ریکارڈ تک — ہر قدم لاگ اور ٹریس کیلئے ہے۔",
    'evidence.step.detection': "شناخت",
    'evidence.step.event': "واقعہ",
    'evidence.step.evidence': "ثبوت",
    'evidence.step.hash': "ہیش",
    'evidence.step.storage': "محفوظ کرنا",
    'evidence.step.audit': "جانچ",
    'evidence.note': "ثبوت کے ریکارڈ میں وقت، کیمرا سورس اور انٹیگرٹی ہیشنگ شامل ہیں۔ یہ موجودہ عمل کو بیان کرتا ہے — یہ قانونی قابل قبول ہونے کی کوئی دعویٰ نہیں کرتا یا حکومتی تصدیق نہیں کرتا۔",
    'faq.label': "// 13 — اکثر پوچھے جانے والے",
    'faq.title': "عام سوالات",
    'faq.desc': "براہ راست جوابات، بشمول ان علاقوں میں جہاں Sentinel-X فی الحال کمزور ہے۔",
    'faq.1.q': "کیا مجھے نئے کیمرے خریدنے چاہئیں؟",
    'faq.1.a': "نہیں۔ Sentinel-X آپ کے پاس موجود سب کچھ کام کرتا ہے — ویب کیمرا، IP کیمرا، RTSP اسٹریمز، یا ویڈیو فائلیں۔ یہ موجودہ بنیاد کے اوپر ایک ذہین لائر ہے، ہارڈ ویئر کی تبدیلی نہیں۔",
    'faq.2.q': "ڈیٹیکشن کتنا درست ہے؟",
    'faq.2.a': "ڈیٹیکشن YOLO11 کا استعمال کرتا ہے، لیکن کوئی AI سسٹم بلاک ہے — فالس پوزٹیوز اور فالس نیگیٹیوز ہوتے ہیں۔ درستگی کیمرا کیفیت، ریزولوشن، کون، اور لائٹنگ کی شرائط پر منحصی ہے، جو سسٹم پر تھوڑے اسکور کے طور پر بیان کرتا ہے۔",
    'faq.3.q': "جب وہ کچھ پتا لگاتا ہے تو کیا ہوتا ہے؟",
    'faq.3.a': "مشانگل واقعات سختی کے سطح پر طبقہ بند کر لیے ہیں (جی سے طبیقی تک)، ڈیش بورڈ پر اعلیٰ وقت کے انتباہ کو متحرک کرتے ہیں، اور خودکار طور پر ثبوت کی تصاویر کے ساتھ میٹیڈیٹا کی گرفتاری کرتے ہیں۔ آپ تمام کو ویب ڈیش بورڈ سے جائزہ اور تحقیق کرتے ہیں۔",
    'faq.4.q': "کیا یہ متعدد کیمرے کے لئے سائز ہو سکتا ہے؟",
    'faq.4.a': "جی ہاں۔ متعدد کیمرا مانیتڈ نظریہ ایک ساتھ ایک ڈیش بورڈ سے مرکزی نظریہ اور پروسیسنگ فراہم کرتا ہے، اور آبجیکٹ ٹریکنگ متعدد کیمرے میں مسلسل IDs برقرار رکھتا ہے۔",
}

# Apply UR updates
for key, val in ur_updates.items():
    if key in ur_dict:
        ur_dict[key] = val
        track(f"UR update {key}")
    else:
        print(f"  NOTE: UR key '{key}' not found in dict (will add)")

for key, val in ur_new.items():
    if key not in ur_dict:
        ur_dict[key] = val
        track(f"UR add {key}")
    else:
        # Update if value differs
        if ur_dict[key] != val:
            ur_dict[key] = val
            track(f"UR update existing {key}")

# ═══════════════════════════════════════════════════════
# ZH DICTIONARY UPDATES
# ═══════════════════════════════════════════════════════

zh_updates = {
    'hero.title1': "别只是记录所发生的事",
    'hero.title2': "了解正在发生的事情。",
    'hero.subtitle': "Sentinel-X 将您现有的摄像头转化为智能监控层 — 实时检测、跟踤和评估威胁。",
    'problem.title': "传统CCTV只能录像，它不理解。",
    'problem.1.desc': "人类无法同时有效地观看每一个摄像头画面。注意力疲劳会导致事件被遗漏。",
    'problem.3.desc': "要找到特定事件，浏览数小时的录像既缓慢又消耗资源。",
    'problem.4.desc': "CCTV 只会记录所发生的事 — 它不会在发生时提醒任何人。",
    'solution.desc': "Sentinel-X 通过多阶段AI管道处理摄像头视频流，将原始画面转化为结构化的、可操作的安全事件。",
    'use.desc': "Sentinel-X 适用于连续摄像头监控能够增加真正安全价值的环境。",
    'preview.desc': "一个统一的Web仪表板，用于监控摄像头、审查事件、检查证据和分析安全趋势。演示数据如下所示。",
    'footer.text': "Sentinel-X AI边缘监控平台 · 版本 1.0 · 使用 Python、Flask、OpenCV、YOLO11 构建",
    'cap.alerts.desc': "基于严重程度的警报系统将事件分类为低、中、高或紧急。",
}

zh_new = {
    'hero.liveCameras': "当前在4个摄像头上直播",
    'hero.viewDashboard': "查看仪表板",
    'problem.label': "// 01 — 问题",
    'solution.label': "// 02 — 解决方案",
    'solution.pipe.threat': "威胁",
    'how.label': "// 03 — 工作原理",
    'cap.label': "// 04 — 能力",
    'cap.loitering.title': "徘徊检测",
    'cap.loitering.desc': "标记在监控区域逗留超过定义时间阈值的个体。",
    'adv.label': "// 05 — 优势",
    'lim.label': "// 06 — 负责披露",
    'use.label': "// 07 — 潜在应用",
    'preview.label': "// 08 — 仪表板预览",
    'sec.label': "// 09 — 安全与隐私",
    'sec.auth.title': "身份验证",
    'sec.auth.desc': "基于会话的身份验证，支持配置的超时。所有用户必须登录才能访问仪表板。",
    'sec.protected.title': "受保护的仪表板",
    'sec.protected.desc': "每个仪表板路由都受身份验证保护。未经身份验证的访客将被重定向到登录。",
    'sec.access.title': "受控访问",
    'sec.access.desc': "对状态更改操作的CSRF令牌保护。对身份验证端点的速率限制。",
    'sec.evidence.title': "证据管理",
    'sec.evidence.desc': "事件证据存储在结构化数据库中，包含时间戳、摄像头引用和完整性哈希。",
    'sec.history.title': "事件历史",
    'sec.history.desc': "完整的事件审计跟踪，包括严重性分类、摄像头来源和区域信息。",
    'sec.ai.title': "负责任的AI",
    'sec.ai.desc': "AI检测结果显示置信度分数。该系统旨在辅助而非替代人工判断。",
    'tech.label': "// 10 — 技术",
    'tech.restapi': "集成",
    'future.label': "// 12 — 未来愿景",
    'future.planned': "计划中",
    'future.roadmap.0': "先进的AI检测模型",
    'future.roadmap.1': "扩展的威胁检测类型",
    'future.roadmap.2': "硬件边缘部署",
    'future.roadmap.3': "其他系统集成",
    'future.roadmap.4': "扩展分析与报告",
    'future.roadmap.5': "授权身份集成",
    'footer.brand': "基于 AI 的视频安全情报，适用于现有摄像头基础设施。 纯软件 MVP。",
    'footer.copyright': "Sentinel-X AI边缘监控平台 · 版本 1.0",
    'footer.builtWith': "使用 Python、Flask、OpenCV、YOLO11 构建",
    'footer.col.product': "产品",
    'footer.col.technology': "技术",
    'footer.col.project': "项目",
    'footer.link.github': "GitHub 仓库",
    'footer.link.underTheHood': "深入了解",
    'footer.link.responsibleAI': "负责任的AI",
    'footer.link.limitations': "局限性与使用",
    'footer.dashboardPreview': "仪表板预览",
    'evidence.label': "// 11 — 证据处理",
    'evidence.title': "Sentinel-X 如何处理证据",
    'evidence.desc': "从检测到某个事物到完整的审计记录 — 每个步骤都被记录和可追踪。",
    'evidence.step.detection': "检测",
    'evidence.step.event': "事件",
    'evidence.step.evidence': "证据",
    'evidence.step.hash': "哈希",
    'evidence.step.storage': "存储",
    'evidence.step.audit': "审计",
    'evidence.note': "证据记录包括时间戳、摄像头来源和完整性哈希。这描述了当前已实施的工作流程 — 它不构成法律可采性或政府认证的声明。",
    'faq.label': "// 13 — 常见问题",
    'faq.title': "常见问题",
    'faq.desc': "直接的答案，包括 Sentinel-X 当前在哪些方面存在不足。",
    'faq.1.q': "我需要买新的摄像头吗？",
    'faq.1.a': "不需要。Sentinel-X 适用于您已经拥有的任何设备 — 摄像头、IP 摄像头、RTSP 流或视频文件。它是现有基础设施之上的智能监控层，而不是硬件更换。",
    'faq.2.q': "检测准确度如何？",
    'faq.2.a': "检测使用 YOLO11，但没有任何AI系统是完美的 — 误报和漏报都会发生。准确率取决于摄像头质量、分辨率、角度和光照条件，系统会将其作为每个检测的置信度分数报告。",
    'faq.3.q': "检测到什么会怎么样？",
    'faq.3.a': "检测结果将被分类为事件（低到紧急级别），在仪表板上触发实时警报，并自动捕获带有元数据的证据截图。您可以在Web仪表板上查看和调查所有内容。",
    'faq.4.q': "它能扩展到多个摄像头吗？",
    'faq.4.a': "可以。多摄像头监控从单个仪表板提供集中视图和处理能力，对象跟踤在摄像头之间保持一致的ID。",
}

for key, val in zh_updates.items():
    if key in zh_dict:
        zh_dict[key] = val
        track(f"ZH update {key}")
    else:
        print(f"  NOTE: ZH key '{key}' not found (will add)")

for key, val in zh_new.items():
    if key not in zh_dict:
        zh_dict[key] = val
        track(f"ZH add {key}")
    else:
        if zh_dict[key] != val:
            zh_dict[key] = val
            track(f"ZH update existing {key}")

# ═══════════════════════════════════════════════════════
# Remove solution.pipe.alert from UR and ZH (replaced by threat)
# ═══════════════════════════════════════════════════════
if 'solution.pipe.alert' in ur_dict:
    del ur_dict['solution.pipe.alert']
    track("UR remove solution.pipe.alert")
if 'solution.pipe.alert' in zh_dict:
    del zh_dict['solution.pipe.alert']
    track("ZH remove solution.pipe.alert")

# ═══════════════════════════════════════════════════════
# REBUILD DICTS
# ═══════════════════════════════════════════════════════

# Rebuild UR dict
result = rebuild_dict_section(content, "dicts.ur", ur_dict)
if result[1]:
    content = result[0]
    track("Rebuild UR dict")
else:
    print("FAIL: Could not rebuild UR dict")

# Rebuild ZH dict
result = rebuild_dict_section(content, "dicts.zh", zh_dict)
if result[1]:
    content = result[0]
    track("Rebuild ZH dict")
else:
    print("FAIL: Could not rebuild ZH dict")

# ═══════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*60}")
print(f"Total changes: {len(changes)}")
