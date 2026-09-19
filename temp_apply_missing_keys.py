"""
Comprehensive script to add all missing UR and ZH keys.
Only adds keys that are needed for the landing page (not dashboard/login/signup).
"""
import re

URDU_TRANSLATIONS = {
    # Section labels
    'hero.liveCameras': 'لاائیو کیمرے',
    'hero.viewDashboard': 'ڈیش بورڈ کو دیکھیں',
    'problem.label': 'بنیادی چیلنجز',
    'solution.label': 'سینٹینل-ایکس کا حل',
    'how.label': 'یہ کیسے کام کرتا ہے',
    'cap.label': 'اہم کوئلیفکیشنز',
    'cap.loitering.title': 'لاٹھ پلائنگ کی نقل و نبات',
    'cap.loitering.desc': 'متوقع مدت تک رکنے والے افراد کی پہچان اور انٹیلیجنٹ اٹریکٹ کرنا۔',
    'lim.label': 'ذمہ دارانہ اخبارات',
    'use.label': 'ممکنہ ایپلیکیشنز',
    'preview.label': 'ڈیش بورڈ پیش کش',
    'sec.label': 'اعتماد اور رازگوشتگی',
    'tech.label': 'کیٹھ کے اندر',
    'tech.restapi': 'ری ایس ٹی ای پی اے',
    'future.label': 'مستقبل کا ڈسپلے',
    'future.planned': ' منتخب شدہ',
    'future.roadmap.0': 'امیج انگیجمنٹ',
    'future.roadmap.1': 'فی الحال',
    'future.roadmap.2': 'کم از کم',
    'future.roadmap.3': 'مستقبل',
    'future.roadmap.4': 'ٹیکنالوجی',
    'future.roadmap.5': 'انٹیگریشن',
    'footer.brand': 'سینٹینل-ایکس',
    'footer.copyright': 'تمامی حقوق محفوظ ہیں۔',
    'footer.builtWith': 'کے ساتھ بنایا گیا',
    'footer.col.product': 'پروڈکٹ',
    'footer.col.technology': 'ٹیکنالوجی',
    'footer.col.project': 'پروجیکٹ',
    'footer.link.github': 'گٹ ہب',
    'footer.link.underTheHood': 'انڈر دہ ہود',
    'footer.link.responsibleAI': 'ذمہ دارانہ ای اے آئی',
    'footer.link.limitations': 'حدود',
    'footer.dashboardPreview': 'ڈیش بورڈ کی پیشکش',
    'evidence.title': 'ثبوت کی دیوانی',
    'evidence.desc': 'سینٹینل-ایکس نے تمام مشینوں کی حفاظت اور جمع کرنا کے لئے تیار کیا ہے۔',
    'faq.title': 'اکثر پوچھے جانے والے سوالات',
    'faq.1.q': 'سینٹینل-ایکس کیا ہے؟',
    'faq.1.a': 'سینٹینل-ایکس ای آئی پاورڈ ویڈیو سرویلنس پلیٹ فارم ہے۔',
    'faq.2.q': 'کیا اسے موجودہ چیمرے استعمال کیے جا سکتے ہیں؟',
    'faq.2.a': 'جی ہاں، سینٹینل-ایکس موجودہ چیمرے انفراسٹرکچر کے ساتھ کام کرتا ہے۔',
    'faq.3.q': 'ای آئی کتنا زندہ ہے؟',
    'faq.3.a': 'سینٹینل-ایکس ای آئی کی شناخت کے ساتھ زندہ ویڈیو پروسیسنگ فراہم کرتا ہے۔',
    'faq.4.q': 'کیا یہ جامع ہے؟',
    'faq.4.a': 'سینٹینل-ایکس ایک مکمل ذمہ دارانہ ای ای آئی سسٹم ہے۔',
    'faq.5.q': 'ڈیش بورڈ کیسے استعمال کیا جاتا ہے؟',
    'faq.5.a': 'ویب بیسچ ڈیش بورڈ سے آسانی سے استعمال کریں۔',
    'faq.6.q': 'کیا یہ مفت ہے؟',
    'faq.6.a': 'سینٹینل-ایکس مفت ڈیمو کے ساتھ دستیاب ہے۔',
}

ZH_MISSING = {
    # Missing ZH keys
    'cta.signIn': '登入',
    'dash.nav.evidence': '证据',
    'login.errorConnection': '连接错误。请检查服务器并重试。',
    'solution.pipe.alert': '警报',
    'solution.pipe.dashboard': '仪表板',
    'solution.pipe.tracking': '目标跟踪',
    'solution.pipe.vision': 'AI视觉',
    'tech.sqlite': '数据存储',
    'tech.yolo': '目标检测',
    'use.hospitals': '医院',
}

# Read the file
with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the UR dict end and insert missing keys before the closing };
# The UR dict ends at line 557-558: 'footer.text': '...',
#   };
# We need to add keys before the closing };

# Split on the UR dict closing
# Find the pattern: 'footer.text': ...,
#   };
#   /* ══════════════════════ ENGINE ══════════════════════ */

# Find UR dict closing brace
ur_end_pattern = r"('footer\.text':[^,]+,\n)(\s*\};\n)"
ur_match = re.search(ur_end_pattern, content)

if ur_match:
    insert_pos = ur_match.start(2)  # Position before };
    
    # Build the new lines to insert
    new_lines = "\n"
    for key, value in URDU_TRANSLATIONS.items():
        new_lines += f"    '{key}': '{value}',\n"
    
    # Insert before the };
    content = content[:insert_pos] + new_lines + content[insert_pos:]
    print("Inserted UR keys successfully")
else:
    print("ERROR: Could not find UR dict closing pattern")

# Now handle ZH missing keys - find the ZH dict closing
zh_end_pattern = r"('login\.errorConnection':[^,]+,\n)(\s*\};)"
zh_match = re.search(zh_end_pattern, content)

if zh_match:
    insert_pos = zh_match.start(2)
    new_lines = "\n"
    for key, value in ZH_MISSING.items():
        new_lines += f"    '{key}': '{value}',\n"
    content = content[:insert_pos] + new_lines + content[insert_pos:]
    print("Inserted ZH keys successfully")
else:
    print("ERROR: Could not find ZH dict closing pattern")

# Write back
with open(r'dashboard\static\js\i18n.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nFile updated successfully")
