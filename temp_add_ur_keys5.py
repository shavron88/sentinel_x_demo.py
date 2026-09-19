"""
Add 37 missing UR keys - fix closing pattern detection
"""
import re, sys

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

UR_ADDITIONS = [
    ('future.aiProc', 'AI پروسیسنی'),
    ('future.alerts', 'اٹریکٹس اور واقعات'),
    ('future.cctv', 'سی سی ٹی وی کیمرے'),
    ('future.cloud', 'کلاؤڈ ڈیش بورڈ'),
    ('future.disclaimer', 'اٹیج باکس مستقبل کا منصوبہ ہے۔ موجودہ سینٹینل-ایکس صرف سافٹ ویئر پلیٹ فارم ہے۔'),
    ('future.edgeDesc', 'سینٹینل-ایکس ای آئی پروسیسنگ کو کیمرے انفراسٹریکچر کے قریب لانے کے لئے ایک وختہ انڈج کمپیوٹنگ آئین ہے۔'),
    ('future.edgeNode', 'سینٹینل-ایکس ایج باکس'),
    ('preview.camera01', 'کیمرا_01 — مین انٹرانس'),
    ('preview.createAccount', 'اپنا سینٹینی-ایکس اکاؤنٹ بنائیں'),
    ('preview.detChart', 'AI ڈیٹیکشن چارٹ'),
    ('preview.detItems', 'افراد · ای موٹی · اٹریکٹس'),
    ('preview.kpi.accuracy', 'Accuracy'),
    ('preview.kpi.alerts', 'Alerts Today'),
    ('preview.kpi.cameras', 'Cameras'),
    ('preview.kpi.threat', 'Threat Level'),
    ('preview.liveFeed', 'Live Camera Feed'),
    ('preview.mockLabel', 'Sentinel-X Dashboard'),
    ('preview.ready', 'Ready to turn your cameras into intelligent security systems?'),
    ('sec.auth.title', 'یقینی تھیٹ ایڈجسٹمنٹ'),
    ('sec.auth.desc', 'سیشن پر مبنی تھیٹ ایڈجسٹمنٹ کے ساتھ۔ تمام یوزرز ڈیش بورڈ تک رسائی کے لئے سائن ان کرنا ضروری ہے۔'),
    ('sec.protected.title', 'محفوظ ڈیش بورڈ'),
    ('sec.protected.desc', 'ہر ایک ڈیش بورڈ راٹ محفوظ ہے۔'),
    ('sec.access.title', 'کنٹرولڈ اینکسس'),
    ('sec.access.desc', 'سی ایس ایس ایف ٹوکن پروٹیکشن اسٹیٹ کے تبدیلی والے آپریشن پر۔ رینج لک ڈاؤن ان تھیٹ ایڈجسٹمنٹ پر۔'),
    ('sec.evidence.title', 'ثبوت کی مینیجمنٹ'),
    ('sec.evidence.desc', 'واقعات کے ثبوت کی ایک ڈیٹا بیس میں محفوظ ہیں۔'),
    ('sec.history.title', 'واقعات کی تاریخ'),
    ('sec.history.desc', 'بنیادی رازگوشتگی کی تاریخ کے ساتھ مشمولہ۔'),
    ('sec.ai.title', 'ذمہ دارانہ ای آئی'),
    ('sec.ai.desc', 'AI ڈیٹیکشن کے نتائج کو یقینی اعتماد سکور کے ساتھ پیش کیا جاتا ہے۔ سسٹم مدد کے لئے ڈیزائین کیا گیا ہے، اننھیں تبدیل نہیں۔'),
    ('tech.python', 'کور رین ٹائم'),
    ('tech.flask', 'ویب فریم ورک'),
    ('tech.opencv', 'ویڈیو پروسیسنگ'),
    ('tech.yolo', 'آئی بی ایس'),
    ('tech.bytetrack', 'آئی بی بی ایس'),
    ('tech.sqlite', 'ڈیٹا اسٹوریج'),
    ('tech.jscss', 'ڈیش بورڈ یو آئی'),
]

# Find the UR dict section
ur_start = content.find('dicts.ur = {')
engine_idx = content.find('/*', ur_start + 100)

# Find the closing of UR dict - it ends with "  }" or "  };"
# Look for the pattern: last entry line, then "  }" or "  };"
ur_section = content[ur_start:engine_idx]

# Find 'tech.restapi.role' in UR section
restapi_pos = ur_section.rfind("'tech.restapi.role'")
if restapi_pos == -1:
    output = "ERROR: tech.restapi.role not found in UR section"
else:
    # Find the next newline after the value
    line_end = ur_section.find('\n', restapi_pos)
    if line_end == -1:
        output = "ERROR: Could not find end of line"
    else:
        # Find the closing };
        close_pos = ur_section.find('}', line_end)
        if close_pos == -1:
            output = "ERROR: Could not find closing }"
        else:
            # Insert before the }
            full_insert_pos = ur_start + close_pos
            
            new_entries = "\n"
            for key, val in UR_ADDITIONS:
                new_entries += f"    '{key}': '{val}',\n"
            
            content = content[:full_insert_pos] + new_entries + content[full_insert_pos:]
            output = "Added 37 missing UR keys"

# Write output to file
with open('debug_output.txt', 'w', encoding='utf-8') as f:
    f.write(output)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(output)
