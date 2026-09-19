#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

ur_start = content.find('dicts.ur =')
zh_start = content.find('dicts.zh =')

for key in ['sec.auth.title', 'solution.pipe.alert', 'solution.pipe.threat', 'tech.restapi', 'footer.text', 'future.planned', 'evidence.label', 'faq.label', 'problem.label', 'how.label', 'cap.loitering.title']:
    search_key = "'" + key + "'"
    idx = content.find(search_key)
    if idx >= 0:
        if idx < zh_start:
            loc = 'EN'
        elif idx < ur_start:
            loc = 'ZH'
        else:
            loc = 'UR'
        val_start = idx + len(search_key) + 3  # skip: ': '
        val_end = val_start + 60
        print(f"{key} ({loc}): {content[val_start:val_end]}")
    else:
        print(f"{key}: NOT FOUND")

# Check for double commas
dc_count = content.count(',,')
print(f"\nDouble commas: {dc_count}")
if dc_count > 0:
    # Find them
    idx = 0
    while True:
        idx = content.find(',,', idx)
        if idx == -1:
            break
        print(f"  Double comma at pos {idx}: ...{repr(content[idx-30:idx+5])}...")
        idx += 2

# Check solution pipe values in EN
for pipe_key in ['solution.pipe.camera', 'solution.pipe.vision', 'solution.pipe.detection', 'solution.pipe.tracking', 'solution.pipe.analysis', 'solution.pipe.threat', 'solution.pipe.evidence', 'solution.pipe.dashboard']:
    full_key = "'" + pipe_key + "'"
    idx = content.find(full_key)
    if idx >= 0:
        val_start = idx + len(full_key) + 3
        val_end = content.find("',", val_start)
        val = content[val_start:val_end]
        if idx < zh_start:
            loc = 'EN'
        elif idx < ur_start:
            loc = 'ZH'
        else:
            loc = 'UR'
        print(f"{pipe_key} ({loc}): '{val}'")
