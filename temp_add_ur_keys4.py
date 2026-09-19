"""
Add 37 missing UR keys by finding the UR dict and inserting before closing
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

UR_ADDITIONS = [
    ('future.aiProc', 'AI پروسیسنگ'),
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

# Find the UR dict - look for the LAST occurrence of 'tech.restapi.role' 
# that's followed by a closing };
# The UR dict is the last dict before the ENGINE section

# Find the engine section
engine_idx = content.find('/* ══════════════════════ ENGINE')

# Find the UR dict section (from dicts.ur to the closing })
ur_section_start = content.rfind('dicts.ur = {', 0, engine_idx)

# In the UR section, find 'tech.restapi.role' 
ur_section = content[ur_section_start:engine_idx]
restapi_idx = ur_section.rfind("'tech.restapi.role'")

if restapi_idx == -1:
    print("ERROR: Could not find tech.restapi.role in UR section")
else:
    # Find the end of the value for this key
    # Find the closing quote after restapi.role
    val_start = ur_section.find("'", restapi_idx + len("'tech.restapi.role': ") + 1)
    if val_start != -1:
        # Find the closing quote
        val_end = ur_section.find("'", val_start + 1)
        if val_end != -1:
            # Check if there's a comma or newline after
            after_val = ur_section[val_end+1:val_end+10]
            print(f"After value: {repr(after_val)}")
            
            # Find the closing }; of the dict
            closing_idx = ur_section.find('};', val_end)
            if closing_idx != -1:
                # Insert before the };
                insert_pos = ur_section_start + closing_idx
                
                new_entries = "\n"
                for key, val in UR_ADDITIONS:
                    new_entries += f"    '{key}': '{val}',\n"
                
                content = content[:insert_pos] + new_entries + content[insert_pos:]
                print("Added 37 missing UR keys")
            else:
                print("Could not find closing }; in UR section")
        else:
            print("Could not find closing quote for value")
    else:
        print("Could not find value start")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated")
