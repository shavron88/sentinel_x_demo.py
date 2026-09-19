#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

def do_replace(old, new, label):
    global content
    if old not in content:
        print(f"  FAIL: {label}")
        return False
    content = content.replace(old, new, 1)
    changes.append(label)
    return True

# ═══════════════════════════════════════
# UR DICTIONARY CHANGES
# ═══════════════════════════════════════

# 1. hero.title1 - completely changed
do_replace(
    "'hero.title1': '\u062e\u0637\u0631\u0627\u062a \u06a9\u0648 \u067e\u06c1\u0644\u06d2 \u062f\u06cc\u06a9\u06be\u06cc\u06ba',",
    "'hero.title1': 'صرف ریکارڈ نہیں کرو، جو ہو گیا۔',",
    "UR hero.title1"
)

# 2. hero.title2 - completely changed
do_replace(
    "'hero.title2': '\u0648\u06cbe \u0648\u0627\u0642\u0639\u0627\u062a \u0628\u0646\u0646\u06d2 <span class=\"accent-word\">\u0633\u06d2 \u067e\u06c1\u0644\u06d2\u06d4</span>',",
    "'hero.title2': 'سمجھ لو کہ ابھی کیا ہو رہا ہے۔',",
    "UR hero.title2"
)

# 3. hero.subtitle - completely changed
do_replace(
    "'hero.subtitle': 'AI \u0633\u06d2 \u0645\u062a\u062d\u0631\u06a9 \u0630\u06c1\u064a\u0646 \u0648\u06cc\u0688\u06cc\u0648 \u0646\u06af\u0631\u0627\u0646\u06cc \u062c\u0648 \u0639\u0627\u0645 \u06a9\u06cc\u0645\u0631\u0627 \u0627\u0633\u0679\u0631\u06cc\u0645\u0632 \u06a9\u0648 \u0642\u0627\u0628\u0644\u0650 \u0639\u0645\u0644 \u0633\u06cc\u06a9\u06cc\u0648\u0631\u0679\u06cc \u062e\u0641\u06cc\u0627 \u0645\u06cc\u06ba \u062a\u0628\u062f\u06cc\u0644 \u06a9\u0631\u062a\u06cc \u06c1\u06d2 \u2014 \u062d\u0642\u06cc\u0642\u06cc \u0648\u0642\u062a \u0645\u06cc\u06ba\u06d4',",
    "'hero.subtitle': 'Sentinel-X اٹھار سے متحرک ذہین ویڈیو نگرانی کی پلیٹ فارم بناتا ہے — پتا لگاتا ہے، ٹریک کرتا ہے، اور دھمکیوں کی نشاندہی کرتا ہے۔',",
    "UR hero.subtitle"
)

# 4. Add new hero keys after hero.badge
do_replace(
    "'hero.badge': 'AI \u0633\u06d2 \u0645\u062a\u062d\u0631\u06a9 \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0627 \u067e\u0644\u06cc\u0679 \u0641\u0627\u0631\u0645',\n    'hero.liveCameras': '', 'hero.title1'",
    "'hero.badge': 'AI \u0633\u06d2 \u0645\u062a\u062d\u0631\u06a9 \u0646\u06af\u0631\u0627\u0648\u06cc \u06a9\u0627 \u067e\u0644\u06cc\u0679 \u0641\u0627\u0631\u0645',\n    'hero.liveCameras': '4 دوربینوں پر لائیو', 'hero.title1'",
    "UR add hero.liveCameras"
)

# Add hero.viewDashboard after hero.getStarted
do_replace(
    "'hero.getStarted': '\u0634\u0631\u0648\u0639 \u06a9\u0631\u064a\u06ba',\n    'hero.signIn':",
    "'hero.getStarted': '\u0634\u0631\u0648\u0639 \u06a9\u0631\u064a\u06ba', 'hero.viewDashboard': '\u0688\u06cc\u0634 \u0628\u0648\u0631\u0688 \u062f\u06cc\u06a9\u06be\u06cc\u06ba',\n    'hero.signIn':",
    "UR add hero.viewDashboard"
)

# 5. problem.title
do_replace(
    "'problem.title': '\u0631\u0648\u0627\u06cc\u062a\u06cc CCTV \u06a9\u06cc \u062d\u062f\u0648\u062f',",
    "'problem.title': 'روایتی CCTV صرف ریکارڈ کرتا ہے۔ یہ سمجھتا نہیں۔',",
    "UR problem.title"
)

# 6. problem.1.desc
do_replace(
    "'problem.1.desc': '\u0627\u0646\u0633\u0627\u0646 \u0628\u0635\u0631\u062a \u0627\u06cc\u06a9 \u0648\u0642\u062a \u0645\u06cc\u06ba \u06c1\u0631 \u06a9\u06cc\u0645\u0631\u0627 \u0641\u06cc\u0688 \u0646\u06c1\u06cc\u06ba \u062f\u06cc\u06a9\u06be \u0633\u06a9\u062a\u06d2\u06d4 \u062a\u0648\u062c\u06c1 \u06a9\u064a \u062a\u06be\u06a7\u0648\u0679 \u0633\u06d2 \u0648\u0627\u0642\u0639\u0627\u062a \u0686\u06be\u0648\u0679 \u062c\u0627\u062a\u06d2 \u06c1\u06cc\u06ba\u06d4',",
    "'problem.1.desc': 'انسان ایک ہی وقت پر ہر کیمرے کی فڈ ہر کچھ نہیں دیکھ سکتا۔ توجہ کی تھکاؤ واقعات کو مفقود کر دیتی ہے۔',",
    "UR problem.1.desc"
)

# 7. problem.3.desc
do_replace(
    "'problem.3.desc': '\u06af\u06be\u0646\u0679\u0648\u0631 \u0631\u06cc\u06a9\u0627\u0631\u0688\u0688\u064a\u0648 \u06a9\u0627 \u062c\u0627\u0626\u0632\u06c1 \u0644\u06cc\u0646\u0627 \u0648\u0642\u062a \u0627\u0648\u0631 \u0648\u0633\u0627\u0626\u0644 \u06a9\u0627 \u0636\u06cc\u0627\u0639 \u06c1\u06d2\u06d4',",
    "'problem.3.desc': 'کئی گھنٹوں کی ریکارڈنگ کو دوبارہ جانچنے میں وقت لگتا ہے، یہ سست اور وسیع وسائل کی مانگ ہے۔',",
    "UR problem.3.desc"
)

# 8. problem.4.desc
do_replace(
    "'problem.4.desc': '\u0631\u0648\u0627\u06cc\u062a\u06cc CCTV \u0635\u0631\u0641 \u0631\u06cc\u06a9\u0627\u0631\u0688 \u06a9\u0631\u062a\u0627 \u06c1\u06d2 \u2014 \u06cc\u06c1 \u06a9\u0648 \u0686\u06be\u062a\u0627 \u06c1\u06d2 \u062c\u0648 \u06c1\u0648\u0627\u060c \u0644\u06cc\u06a9\u0646 \u06c1\u0648\u062a\u06d2 \u0648\u0642\u062a \u0622\u06af\u0627\u06c1 \u0646\u06c1\u06cc\u06ba \u06a9\u0631\u062a\u0627 \u06c1\u06d2\u06d4',",
    "'problem.4.desc': 'CCTV صرف یہ ریکارڈ کرتا ہے — یہ کسی وقت آگاہ نہیں کرتا۔',",
    "UR problem.4.desc"
)

# 9. solution.desc
do_replace(
    "'solution.desc': 'Sentinel-X \u06a9\u06cc\u0645\u0631\u0627 \u0627\u0633\u0679\u0631\u06cc\u0645\u0632 \u06a9\u0648 \u06a9\u062b\u06cc\u0631 \u0645\u0631\u0627\u062d\u0644 AI \u067e\u0627\u0626\u067e \u0644\u0627\u0626\u0646\u0633\u06d3\u0644 \u06a9\u0631\u062a\u0627 \u06c1\u06d2 \u062c\u0648 \u062e\u0627\u0645 \u0641\u0648\u0679\u06cc\u062c \u06a9\u0648 \u0645\u0646\u0638\u0645 \u0642\u0627\u0628\u0644\u0650 \u0639\u0645\u0644 \u0633\u06cc\u06a9\u06cc\u0648\u0631\u0679\u06cc \u0648\u0627\u0642\u0639\u0627\u062a \u0645\u06cc\u06ba \u062a\u0628\u062f\u06cc\u0644 \u06a9\u0631\u062a\u0627 \u06c1\u06d2\u06d4',",
    "'solution.desc': 'Sentinel-X کیمرا اٹھار سے متحرک ذہین ویڈیو نگرانی کی پلیٹ فارم بناتا ہے — خام فوڈیج کو منظم قابل عمل سیکیورٹی واقعات میں تبدیل کرتا ہے۔',",
    "UR solution.desc"
)

# 10. use.desc - added 'real'
do_replace(
    "'use.desc': 'Sentinel-X \u0627\u0646 \u0645\u062d\u0648\u0644 \u06a9\u06d2 \u0644\u0626\u06d2 \u062a\u0635\u0645\u06cc\u0645 \u06a9\u06cc\u0627 \u06af\u06cc\u0627 \u06c1\u06d2 \u062c\u06c1\u0627\u06ba \u0645\u0633\u0644\u0633\u0644 \u06a1\u06cc\u0645\u0631\u0627 \u0646\u06af\u0631\u0627\u0646\u06cc \u0633\u06cc\u06a6\u0648\u0631\u0679\u06cc \u0642\u062f\u0631 \u0645\u06cc\u06ba \u0627\u0636\u0627\u0641\u06c1 \u06a9\u0631\u062a\u06cc \u06c1\u06d2\u06d4',",
    "'use.desc': 'Sentinel-X ان محول کے لئے بنائے گیا ہے جہاں مسلسل ڈیلی کیمرا نگرانی اضافی حقیقی سیکیورٹی کی قدر رکھتی ہے۔',",
    "UR use.desc"
)

# 11. preview.desc - added "Demo data shown below."
do_replace(
    "'preview.desc': '\u06a9\u06cc\u0645\u0631\u0648\u06ba \u06a9\u06cc \u0646\u06af\u0631\u0627\u0646\u06cc\u060c \u0648\u0627\u0642\u0639\u0627\u062a \u06a9\u06d2 \u062c\u0627\u0626\u0632\u06d2\u060c \u0634\u0648\u0627\u06c1\u062f \u06a9\u06cc \u062c\u0627\u0646\u0686 \u0627\u0648\u0631 \u0633\u06cc\u06a6\u0648\u0631\u0679\u06cc \u0631\u062c\u062d\u0627\u0646\u0627\u062a \u06a9\u06d9 \u0644\u0626\u06d2 \u0645\u062a\u062d\u062f Web \u0688\u06cc\u0634 \u0628\u0648\u0631\u0688\u06d4',",
    "'preview.desc': 'کیمرا نظام اور اپنا خود موجود ہے۔',",  # This is wrong - let me redo
    "UR preview.desc temp"
)
# Actually this is getting too complex with the escape sequences. Let me take a different approach.

print("\n--- Switching to direct string approach for remaining changes ---")

# Reset content
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# For remaining changes, I'll work with the decoded Urdu characters directly
# The file has \uXXXX escape sequences, but Python's str.replace works on the literal text

# Let me find the exact positions and work with line-by-line replacements instead
print(f"File size: {len(content)} chars")
print(f"UR dict starts at: {content.find('dicts.ur =')}")

# Find the end of the UR dict
ur_end = content.find('};\n\n', content.find('dicts.ur ='))
if ur_end < 0:
    ur_end = content.find('};', content.find('dicts.ur ='))
print(f"UR dict ends at: {ur_end}")
print(f"UR dict end context: {repr(content[ur_end-50:ur_end+10])}")
