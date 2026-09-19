"""
Add 37 missing UR keys by directly manipulating lines
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the UR dict end - look for the line with 'tech.restapi.role' followed by '  };'
# Search for the pattern where 'tech.restapi.role' is followed by '};' on next line
insert_after = None
for i, line in enumerate(lines):
    if 'tech.restapi.role' in line and 'integration' not in line and 'integration' not in line.lower() and 'انٹیگری' not in line:
        # This might be the wrong one
        pass
    if 'tech.restapi.role' in line:
        # Check if next line is '  };'
        if i + 1 < len(lines) and lines[i+1].strip() == '};':
            insert_after = i
            break

if insert_after is None:
    # Try finding ANY line in the UR dict area with 'tech.restapi.role'
    # The UR dict starts after the ZH dict
    ur_start = None
    for i, line in enumerate(lines):
        if 'dicts.ur = {' in line:
            ur_start = i
            break
    
    if ur_start:
        for i in range(ur_start, len(lines)):
            if 'tech.restapi.role' in lines[i]:
                if i + 1 < len(lines) and lines[i+1].strip() == '};':
                    insert_after = i
                    break

if insert_after is not None:
    print(f"Found UR closing at line {insert_after + 1}")
    
    ur_additions = {
        'future.aiProc': 'AI پروسیسنگ',
        'future.alerts': 'اٹریکٹس اور واقعات',
        'future.cctv': 'سی سی ٹی وی کیمرے',
        'future.cloud': 'کلاؤڈ ڈیش بورڈ',
        'future.disclaimer': 'اٹیج باکس مستقبل کا منصوبہ ہے۔ موجودہ سینٹینل-ایکس صرف سافٹ ویئر پلیٹ فارم ہے۔',
        'future.edgeDesc': 'سینٹینل-ایکس ای آئی پروسیسنگ کو کیمرے انفراسٹریکچر کے قریب لانے کے لئے ایک وختہ انڈج کمپیوٹنگ آئین ہے۔',
        'future.edgeNode': 'سینٹینل-ایکس ایج باکس',
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
        'tech.python': 'کور رین ٹائم',
        'tech.flask': 'ویب فریم ورک',
        'tech.opencv': 'ویڈیو پروسیسنگ',
        'tech.yolo': 'آئی بی ایس',
        'tech.bytetrack': 'آئی بی بی ایس',
        'tech.sqlite': 'ڈیٹا اسٹوریج',
        'tech.jscss': 'ڈیش بورڈ یو آئی',
    }
    
    # Build new lines to insert
    new_lines = []
    for key, val in ur_additions.items():
        new_lines.append(f"    '{key}': '{val}',\n")
    
    # Insert after the 'tech.restapi.role' line
    lines = lines[:insert_after + 1] + new_lines + lines[insert_after + 1:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Added 37 missing UR keys successfully")
else:
    print("ERROR: Could not find UR closing position")
    # Debug: show lines around tech.restapi
    for i, line in enumerate(lines):
        if 'restapi' in line:
            print(f"Line {i+1}: {line.rstrip()[:80]}")
