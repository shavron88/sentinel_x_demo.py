#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find UR dict
ur_start = content.find('dicts.ur = {')
zh_start = content.find('dicts.zh = {')
# Find end of UR dict
ur_end = content.find('};', ur_start)

# Check all tech.* keys in UR
for key in ['tech.python', 'tech.flask', 'tech.opencv', 'tech.yolo', 'tech.bytetrack', 'tech.sqlite', 'tech.jscss', 'tech.restapi']:
    idx = content.find("'" + key + "'", ur_start, ur_end)
    if idx >= 0:
        val_start = idx + len(key) + 5  # skip 'key': '
        val_end = content.find("',", val_start)
        print(f"UR {key}: {repr(content[val_start:val_end])}")
    else:
        print(f"UR {key}: NOT FOUND")

# Check all sec.* keys in UR
for key in ['sec.auth.title', 'sec.auth.desc', 'sec.protected.title', 'sec.protected.desc', 'sec.access.title', 'sec.access.desc', 'sec.evidence.title', 'sec.evidence.desc', 'sec.history.title', 'sec.history.desc', 'sec.ai.title', 'sec.ai.desc']:
    idx = content.find("'" + key + "'", ur_start, ur_end)
    if idx >= 0:
        val_start = idx + len(key) + 5
        val_end = content.find("',", val_start)
        print(f"UR {key}: {repr(content[val_start:val_end][:100])}")
    else:
        print(f"UR {key}: NOT FOUND")

# Check all evidence.* keys in UR
for key in ['evidence.label', 'evidence.title', 'evidence.desc', 'evidence.step.detection', 'evidence.step.event', 'evidence.step.evidence', 'evidence.step.hash', 'evidence.step.storage', 'evidence.step.audit', 'evidence.note']:
    idx = content.find("'" + key + "'", ur_start, ur_end)
    if idx >= 0:
        val_start = idx + len(key) + 5
        val_end = content.find("',", val_start)
        print(f"UR {key}: {repr(content[val_start:val_end][:80])}")
    else:
        print(f"UR {key}: NOT FOUND")

# Check all faq.* keys in UR
for i in range(1, 7):
    for suffix in ['.q', '.a']:
        key = f'faq.{i}{suffix}'
        idx = content.find("'" + key + "'", ur_start, ur_end)
        if idx >= 0:
            val_start = idx + len(key) + 5
            val_end = content.find("',", val_start)
            print(f"UR {key}: {repr(content[val_start:val_end][:80])}")
        else:
            print(f"UR {key}: NOT FOUND")
