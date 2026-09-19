"""
Fix remaining issues:
1. Remove emojis from sec.* titles in EN and ZH dicts
2. Add 37 missing UR keys (existing EN keys that UR doesn't have)
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── Fix 1: Remove emojis from sec.* titles ───
# The emoji escape sequences in JS are like: '\ud83d\udd10'
# In the file they appear as literal backslash-u sequences
# Pattern: \\ud83[d-f]\\uXXXX followed by optional more emojis and a space

# EN dict fixes - remove emoji escapes from sec.* titles
en_sec_emoji_map = {
    r"'sec\.auth\.title':\s*'\\ud83d\\udd10\s*": "'sec.auth.title': '",
    r"'sec\.protected\.title':\s*'\\ud83d\\udee1\\ufe0f\s*": "'sec.protected.title': '",
    r"'sec\.access\.title':\s*'\\ud83d\\udd11\s*": "'sec.access.title': '",
    r"'sec\.evidence\.title':\s*'\\ud83d\\udcc1\s*": "'sec.evidence.title': '",
    r"'sec\.history\.title':\s*'\\ud83d\\udccc\s*": "'sec.history.title': '",
    r"'sec\.ai\.title':\s*'\\ud83e\\udd16\s*": "'sec.ai.title': '",
}

for pattern, replacement in en_sec_emoji_map.items():
    content = re.sub(pattern, replacement, content)
print("Fixed EN sec.* titles")

# ZH dict fixes
zh_sec_emoji_map = {
    r"'sec\.auth\.title':\s*'\\ud83d\\udd10\s*": "'sec.auth.title': '",
    r"'sec\.protected\.title':\s*'\\ud83d\\udee1\\ufe0f\s*": "'sec.protected.title': '",
    r"'sec\.access\.title':\s*'\\ud83d\\udd11\s*": "'sec.access.title': '",
    r"'sec\.evidence\.title':\s*'\\ud83d\\udcc1\s*": "'sec.evidence.title': '",
    r"'sec\.history\.title':\s*'\\ud83d\\udccc\s*": "'sec.history.title': '",
    r"'sec\.ai\.title':\s*'\\ud83e\\udd16\s*": "'sec.ai.title': '",
}

for pattern, replacement in zh_sec_emoji_map.items():
    content = re.sub(pattern, replacement, content)
print("Fixed ZH sec.* titles")

# ═══ Fix 2: Add 37 missing UR keys ═──
# These are existing EN keys that the UR dict should also have
UR_ADDITIONS = {
    # Future keys
    'future.aiProc': 'AI پروسیسنگ',
    'future.alerts': 'اٹریکٹس اور واقعات',
    'future.cctv': 'سی سی ٹی وی کیمرے',
    'future.cloud': 'کلاؤڈ ڈیش بورڈ',
    'future.disclaimer': 'اٹیج باکس مستقبل کا منصوبہ ہے۔ موجودہ سینٹینل-ایکس صرف سافٹ ویئر پلیٹ فارم ہے۔',
    'future.edgeDesc': 'سینٹینل-ایکس ای آئی پروسیسنگ کو کیمرے انفراسٹرکچر کے قریب لانے کے لئے ایک وختہ انڈج کمپیوٹنگ آئین ہے۔',
    'future.edgeNode': 'سینٹینل-ایکس ایج باکس',
    
    # Preview keys
    'preview.camera01': 'کیمرا_01 — مین انٹرانس',
    'preview.createAccount': 'اپنا سینٹینی-ایکس اکاؤنٹ بنائیں',
    'preview.detChart': 'AI ڈیٹیکشن چارٹ',
    'preview.detItems': 'افراد · ای موٹی · اٹریکٹس',
    'preview.kpi.accuracy': 'Accuracy',
    'preview.kpi.alerts': 'Alerts Today',
    'preview.kpi.cameras': 'Cameras',
    'preview.kpi.threat': 'Threat Level',
    'preview.liveFeed': 'Live Camera Feed',
    'preview.mockLabel': 'Sentinel-X Dashboard',
    'preview.ready': 'Ready to turn your cameras into intelligent security systems?',
    
    # Security keys
    'sec.auth.title': 'یقینی تھیٹ ایڈجسٹمنٹ',
    'sec.auth.desc': 'سیشن پر مبنی تھیٹ ایڈجسٹمنٹ کے ساتھ۔ تمام یوزرز ڈیش بورڈ تک رسائی کے لئے سائن ان کرنا ضروری ہے۔',
    'sec.protected.title': 'محفوظ ڈیش بورڈ',
    'sec.protected.desc': 'ہر ایک ڈیش بورڈ راٹ محفوظ ہے۔',
    'sec.access.title': 'کنٹرولڈ اینکسس',
    'sec.access.desc': 'سی ایس ایس ایف ٹوکن پروٹیکشن اسٹیٹ کے تبدیلی والے آپریشن پر۔ رینج لک ڈاؤن ان تھیٹ ایڈجسٹمنٹ پر۔',
    'sec.evidence.title': 'ثبوت کی مینیجمنٹ',
    'sec.evidence.desc': 'واقعات کے ثبوت کی ایک ڈیٹا بیس میں محفوظ ہیں۔',
    'sec.history.title': 'واقعات کی تاریخ',
    'sec.history.desc': 'بنیادی رازگوشتگی کی تاریخ کے ساتھ مشمولہ۔',
    'sec.ai.title': 'ذمہ دارانہ ای آئی',
    'sec.ai.desc': 'AI ڈیٹیکشن کے نتائج کو یقینی اعتماد سکور کے ساتھ پیش کیا جاتا ہے۔ سسٹم مدد کے لئے ڈیزائین کیا گیا ہے، اننھیں تبدیل نہیں۔',
    
    # Tech keys
    'tech.python': 'کور رین ٹائم',
    'tech.flask': 'ویب فریم ورک',
    'tech.opencv': 'ویڈیو پروسیسنگ',
    'tech.yolo': 'آئی بی ایس',
    'tech.bytetrack': 'آئی بی بی ایس',
    'tech.sqlite': 'ڈیٹا اسٹوریج',
    'tech.jscss': 'ڈیش بورڈ یو آئی',
}

# Find the UR dict and add missing keys before closing };
# The UR dict ends with: 'footer.dashboardPreview': 'Value',\n  };
# We need to insert before "  };"

# Find the engine section start (after UR dict)
engine_start = content.find('/* ══════════════════════ ENGINE')

# Find the }; just before the engine section
# Search backwards from engine_start for "  };"
ur_close_match = re.search(r"\n  \};\n", content[engine_start-200:engine_start])
if ur_close_match:
    insert_pos = engine_start - 200 + ur_close_match.start() + 1  # After the newline
    new_entries = "\n"
    for key, val in UR_ADDITIONS.items():
        new_entries += f"    '{key}': '{val}',\n"
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added 37 missing UR keys")
else:
    print("ERROR: Could not find UR closing position")
    # Try alternate approach - find last entry in UR dict
    # Search for the pattern right before the engine comment
    ur_tail = content[engine_start-500:engine_start]
    print(f"UR tail: {repr(ur_tail[-200:])}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated")
