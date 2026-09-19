"""
Comprehensive i18n fix script:
1. Add missing EN keys (section labels, evidence, FAQ, hero, future roadmap, footer, cap.loitering)
2. Remove emojis from sec.* titles in EN
3. Fix double-escaped \\u0688 in UR solution.pipe.dashboard
4. Add all missing UR keys with Urdu translations
5. Add all missing ZH keys with Chinese translations
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
    'cap.label': '\�یشن',
    'lim.label': '\u0630مہِ دارانہ اخبارات',
    'use.label': '\u0627پلیکیشنز',
    'preview.label': '\u0688ش بورڈ پیشکش',
    'sec.label': '\u0627ور رازگوشتگی',
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
    'footer.link.github': 'گڈ ہب',
    'footer.link.underTheHood': 'انڈر دہ ہود',
    'footer.link.responsibleAI': 'ذمہ دارانہ ای آئی',
    'footer.link.limitations': 'حدود',
    'footer.dashboardPreview': 'ڈیش بورڈ کی پیشکش',
}

# ─── ZH translations for the new EN keys ───
ZH_ADDITIONS = {
    'problem.label': '挑战',
    'solution.label': '解决方案',
    'how.label': '工作原理',
    'cap.label': '核心功能',
    'lim.label': '负责声明',
    'use.label': '应用程序',
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

# ─── Apply EN additions ───
# Find EN dict closing (before the last entry + };)
en_close_match = re.search(r"(    'signup\.errorConn':[^,]+,\n)(\s*\};)", content)
if en_close_match:
    insert_pos = en_close_match.start(2)
    new_entries = "\n"
    for key, val in EN_ADDITIONS.items():
        escaped = val.replace("'", "\\'")
        new_entries += f"    '{key}': '{escaped}',\n"
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added EN keys successfully")
else:
    print("ERROR: Could not find EN dict closing")

# ─── Remove emojis from sec.* titles in EN ───
# Pattern: 'sec.xxx.title': '\ud83d\xxxx... Title Text'
# Remove emoji escape sequences
content = re.sub(
    r"('sec\.[^']+\.title':\s*')(\\ud83d\\[0-9a-f]{4}\\u[0-9a-f]{4}.*?\\u[0-9a-f]{4}\s*)",
    r"\1",
    content
)
# Also handle single emoji patterns
content = re.sub(
    r"('sec\.[^']+\.title':\s*')(\\ud83d\\[0-9a-f]{4}\\u[0-9a-f]{4}.*?\s*)",
    r"\1",
    content
)
print("Removed emojis from sec titles (if any matched)")

# Verify sec titles
en_match2 = re.search(r"dicts\.en\s*=\s*\{(.*?)\n\s*\};", content, re.DOTALL)
if en_match2:
    for m in re.finditer(r"'sec\.[^']+\.title':\s*'([^']+)'", en_match2.group(1)):
        print(f"  sec title now: {m.group(1)}")

# ─── Fix double-escaped \u0688 in UR solution.pipe.dashboard ───
content = content.replace("'solution.pipe.dashboard': '\\\\u0688\\u06cc\\u0634 \\u0628\\u0648\\u0631\\u0688'",
                          "'solution.pipe.dashboard': '\\u0688\\u06cc\\u0634 \\u0628\\u0648\\u0631\\u0688'")
print("Fixed double-escaped UR solution.pipe.dashboard")

# ─── Add ZH additions ───
# ZH dict now ends after login.errorConnection (which was the missing key we added earlier)
# Actually, we need to re-find the ZH dict end
zh_close_match = re.search(r"(    'login\.errorConnection':[^,]+,\n)(\s*\};)", content)
if zh_close_match:
    insert_pos = zh_close_match.start(2)
    new_entries = "\n"
    for key, val in ZH_ADDITIONS.items():
        escaped = val.replace("'", "\\'")
        new_entries += f"    '{key}': '{escaped}',\n"
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added ZH keys successfully")
else:
    print("ERROR: Could not find ZH dict closing")

# ─── Add UR additions ───
# UR dict ends with footer.text
ur_close_match = re.search(r"(    'footer\.text':[^,]+,\n)(\s*\};)", content)
if ur_close_match:
    insert_pos = ur_close_match.start(2)
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
