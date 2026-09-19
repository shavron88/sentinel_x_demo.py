#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# Fix UR sec.history.desc - garbled with ".audit"
old = "'sec.history.desc': ' تمام واقعات کے ساتھ مکمل.audit ٹریل، درج ذیل ہے — سختی درجہ بندی، کیمرا سورس، اور علاقائی معلومات۔',"
new = "'sec.history.desc': 'مکمل.audit ٹریل، تمام واقعات کے ساتھ، درج ذیل ہے — سختی درجہ بندی، کیمرا سورس، اور علاقائی معلومات۔',"
# Actually, let me fix this better - remove the ".audit" artifact
new = "'sec.history.desc': 'مکمل.audit ٹریل، تمام واقعات کے ساتھ — سختی درجہ بندی، کیمراسورس اور علاقائی معلومات شامل ہیں۔',"

if old in content:
    content = content.replace(old, new, 1)
    changes.append("Fix UR sec.history.desc")
else:
    # Try finding it
    idx = content.find("'sec.history.desc'")
    if idx >= 0:
        end = content.find("',\n", idx)
        actual = content[idx:end+2]
        print(f"Actual: {repr(actual[:120])}")
        # Just do a targeted replacement of the garbled part
        old_part = ".audit ٹریل، درج ذیل ہے —"
        new_part = "audit ٹریل، تمام واقعات کے ساتھ —"
        if old_part in content:
            content = content.replace(old_part, new_part, 1)
            changes.append("Fix UR sec.history.desc garbled text")
        else:
            print("Could not find garbled substring")

# Fix UR sec.evidence.title grammar (انتظام → انتظام)
old2 = "'sec.evidence.title': 'ثبوت کی انتظام',"
new2 = "'sec.evidence.title': 'ثبوت کا انتظام',"
if old2 in content:
    content = content.replace(old2, new2, 1)
    changes.append("Fix UR sec.evidence.title grammar")
else:
    print("sec.evidence.title not found in UR")

# Fix UR sec.protected.desc - has "visitors" in English
old3 = "'sec.protected.desc': 'ہر ڈیش بورڈ راستہ تصدیق کے سامنے محفوظ ہے۔ غیر مصدقح د visitors کو دوبارہ رجوع کر دیا جاتا ہے۔',"
new3 = "'sec.protected.desc': 'ہر ڈیش بورڈ راستہ تصدیق کے سامنے محفوظ ہے۔ غیر مصدقح د دیدکرتم کو دوبارہ راستہ دیا جاتا ہے۔',"
# Better translation
new3 = "'sec.protected.desc': 'ہر ڈیش بورڈ راستہ تصدیق کے سامنے محفوظ ہے۔ غیر مصدقح د دید کرتے ہیں کو سائن ان کے لئے رجوع کرائے جاتے ہیں۔',"
if old3 in content:
    content = content.replace(old3, new3, 1)
    changes.append("Fix UR sec.protected.desc English word")
else:
    print("sec.protected.desc not found or different in UR")
    idx = content.find("'sec.protected.desc'")
    if idx >= 0:
        end = content.find("',\n", idx)
        print(f"Actual: {repr(content[idx:end+2][:120])}")

# Fix UR sec.access.desc - has incomplete translation
idx = content.find("'sec.access.desc'")
if idx >= 0:
    end = content.find("',\n", idx)
    print(f"UR sec.access.desc: {repr(content[idx:end+2][:120])}")

# Fix UR sec.ai.desc - check quality
idx = content.find("'sec.ai.desc'")
if idx >= 0:
    end = content.find("',\n", idx)
    print(f"UR sec.ai.desc: {repr(content[idx:end+2][:120])}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nChanges: {len(changes)}")
for c in changes:
    print(f"  OK: {c}")
