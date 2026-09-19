#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# ═══════════════════════════════════════════════════════
# FIX 1: Add missing UR dict keys + fix English values
# ═══════════════════════════════════════════════════════

# Find the end of the UR dict (the closing `};` of dicts.ur)
ur_start = content.find('dicts.ur = {')
depth = 0
i = content.find('{', ur_start)
while i < len(content):
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            ur_close = i
            break
    i += 1

print(f"UR dict closes at char {ur_close}")

# The content before the closing brace ends with whitespace/newline
# We need to insert new keys before the closing brace
# Find the last non-whitespace before the closing
insert_point = ur_close
while insert_point > 0 and content[insert_point-1] in ' \t\n\r':
    insert_point -= 1

# Fix sec.access.desc (English -> Urdu)
old_access = "'sec.access.desc': 'CSRF token protection on state-changing operations, with rate limiting on authentication endpoints.',"
new_access = "'sec.access.desc': 'تبدیلیوں پر CSRF ٹوکن کی حفاظت۔ تصدیقی نقاط پر رفعِ رفتار۔',"
if old_access in content:
    content = content.replace(old_access, new_access, 1)
    print("  Fixed sec.access.desc (UR)")
else:
    print(f"  sec.access.desc old text not found")

# Fix sec.ai.desc (English -> Urdu)
old_ai_desc = "'sec.ai.desc': 'AI detection results are shown with confidence scores. The system is designed to assist, not replace, human judgment.',"
new_ai_desc = "'sec.ai.desc': 'AI ڈیٹیکشن کے نتائج کے ساتھ پیغام نمائیں گئے ہیں۔ نظام معاونت کے لئے ڈیزائن ہوا ہے، انسانی فیصلہ سے بہتر نہیں۔',"
if old_ai_desc in content:
    content = content.replace(old_ai_desc, new_ai_desc, 1)
    print("  Fixed sec.ai.desc (UR)")
else:
    # Maybe it has different escaping
    idx = content.find("'sec.ai.desc'")
    if idx >= 0:
        end = content.find("',\n", idx)
        print(f"  sec.ai.desc actual: {repr(content[idx:end+2][:80])}")

# Fix sec.history.desc - remove remaining ".audit" artifact
old_hist = ".audit ٹریل، تمام واقعات کے ساتھ"
new_hist = "audit ٹریل، تمام واقعات کے ساتھ"
if old_hist in content:
    content = content.replace(old_hist, new_hist, 1)
    print("  Fixed sec.history.desc artifact (UR)")
else:
    idx = content.find("'sec.history.desc'")
    if idx >= 0:
        end = content.find("',\n", idx)
        print(f"  sec.history.desc: {repr(content[idx:end+2][:100])}")

# Missing UR keys to add
ur_missing = {
    'tech.python': "نظریہ استصال",
    'tech.flask': "ویب فریم ورک",
    'tech.opencv': "ویڈیو پروسیسنگ",
    'tech.yolo': "اجسام کی تشخیص",
    'tech.bytetrack': "اجسام کا ٹریک کرنا",
    'tech.sqlite': "ڈیٹا ذخیرہ",
    'tech.jscss': "ڈیش بورڈ UI",
    'future.edgeDesc': "ایک مخصوص ایج کمپیوٹنگ آئٹ ایپلائنٹسی ہے جو Sentinel-X AI کی پروسیسنگ کو کیمرا بنیاد کے قریب ڈپلائی کرتا ہے — مرکزی کمپیوٹنگ پر منحصی کم کرے، اور ممکنہ طور پر ترسیل کی لچک، تاخیر اور بنڈ وائڈتھ کو بہتر بنائے۔",
    'future.cctv': "CCTV کیمرے",
    'future.edgeNode': "Sentinel-X ایج باکس",
    'future.aiProc': "AI پروسیسنگ",
    'future.alerts': "انتباہات اور واقعات",
    'future.cloud': "کلاؤڈ ڈیش بورڈ",
    'future.disclaimer': "Edge Box موجودہ مستقبل کے منصوبے ہیں۔ موجودہ Sentinel-X ایک خالص سافٹ ویئر پلیٹ فارم ہے۔",
    'footer.text': "Sentinel-X AI ایج سرویلینس پلیٹ فارم · ورژن 1.0 · Python، Flask، OpenCV، YOLO11 کے ساتھ تیار",
    'faq.5.q': "کیا Sentinel-X پروڈکشن کے لائق ہے؟",
    'faq.5.a': "یہ ایک فعال MVP (ورژن 1.0) ہے — پائپ لائن مکمل طور پر چلتا ہے، لیکن حدود حقیقی ہیں: AI ڈیٹیکشن واقعات کو مسل کر سکتا ہے، نیٹ ورک کی قابلیت اہم ہے، اور رئیل کے ذریعے GPU تیزی کی ضرورت ہے۔ یہ قیمت کے لئے تیار ہے، ابھی اعتبار کے لئے نہیں۔",
    'faq.6.q': "Sentinel-X کس پر چلتا ہے؟",
    'faq.6.a': "Python، Flask، OpenCV، اور YOLO11 ڈیٹیکشن کے لئے بائیٹریک کے ساتھ آبجیکٹ ٹریکنگ۔ ڈیش بورڈ کوئی موڈرن براوزر سے رسائی کے ساتھ ایک ویب انٹر فیس ل ہے۔",
}

# Insert missing keys at the end of UR dict
new_lines = []
for key, val in ur_missing.items():
    new_lines.append(f"    '{key}': '{val}',")
insert_text = "\n" + "\n".join(new_lines) + "\n  "
content = content[:insert_point] + insert_text + content[ur_close:]
print(f"  Added {len(ur_missing)} missing UR keys")

# ═══════════════════════════════════════════════════════
# FIX 2: Check ZH dict for missing keys too
# ═══════════════════════════════════════════════════════

zh_start = content.find('dicts.zh = {')
depth = 0
i = content.find('{', zh_start)
while i < len(content):
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            zh_close = i
            break
    i += 1

# Check ZH for the same missing keys
zh_content = content[zh_start:zh_close] if 'zh_close' in dir() else ''
zh_missing = [k for k in ur_missing.keys() if "'" + k + "'" not in zh_content]
print(f"\nZH missing the same keys: {zh_missing}")

# Check if ZH has sec.access.desc in English
idx = zh_content.find("'sec.access.desc'")
if idx >= 0:
    end = content.find("',\n", idx)
    # Find relative to content
    actual_idx = content.find("'sec.access.desc'", zh_start, zh_close if 'zh_close' in dir() else len(content))
    end_act = content.find("',\n", actual_idx)
    print(f"ZH sec.access.desc: {repr(content[actual_idx:end_act+2][:100])}")

# Check ZH for faq.5 and faq.6
for k in ['faq.5.q', 'faq.5.a', 'faq.6.q', 'faq.6.a']:
    if "'" + k + "'" not in zh_content:
        print(f"  ZH missing: {k}")

# ═══════════════════════════════════════════════════════
# FIX 3: Check UR for solution.pipe.dashboard double-backslash issue
# ═══════════════════════════════════════════════════════
idx = content.find("'solution.pipe.dashboard'", ur_start)
if idx >= 0:
    end = content.find("',\n", idx)
    print(f"\nUR solution.pipe.dashboard: {repr(content[idx:end+2][:80])}")

# ═══════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone. File saved.")
