"""
Add 37 missing UR keys to the UR dict
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

UR_ADDITIONS = {
    'future.aiProc': 'AI پروسیسنگ',
    'future.alerts': 'اٹریکٹس اور واقعات',
    'future.cctv': 'سی سی ٹی وی کیمرے',
    'future.cloud': 'کلاؤڈ ڈیش بورڈ',
    'future.disclaimer': 'اٹیج باکس مستقبل کا منصوبہ ہے۔ موجودہ سینٹینل-ایکس صرف سافٹ ویئر پلیٹ فارم ہے۔',
    'future.edgeDesc': 'سینٹینل-ایکس ای آئی پروسیسنگ کو کیمرے انفراسٹرکچر کے قریب لانے کے لئے ایک وختہ انڈج کمپیوٹنگ آئین ہے۔',
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

# Find the UR dict ending - it's the last dict before the ENGINE section
# The UR dict ends with 'tech.restapi.role' followed by '};'
# Use a broader pattern that handles any characters
pattern = r"(    'tech\.restapi\.role':\s*'(?:[^'\\]|\\.)*',\n)(\s*});"
match = re.search(pattern, content[content.find('dicts.ur'):])
if match:
    ur_start_pos = content.find('dicts.ur = {')
    insert_pos = ur_start_pos + match.start(2)
    new_entries = "\n"
    for key, val in UR_ADDITIONS.items():
        new_entries += f"    '{key}': '{val}',\n"
    content = content[:insert_pos] + new_entries + content[insert_pos:]
    print("Added 37 missing UR keys")
else:
    print("ERROR: Could not find UR closing pattern")
    # Try to find it differently
    ur_section = content[content.find('dicts.ur'):]
    # Find all lines with tech.restapi
    for i, line in enumerate(ur_section.split('\n')):
        if 'restapi.role' in line:
            print(f"Line {i}: found restapi.role")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated")
