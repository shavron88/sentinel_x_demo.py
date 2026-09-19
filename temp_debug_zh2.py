#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all dict boundaries
for name in ['dicts.en', 'dicts.zh', 'dicts.ur']:
    idx = content.find(name + ' = {')
    if idx >= 0:
        # Find the closing };
        brace_idx = content.find('{', idx)
        depth = 0
        i = brace_idx
        while i < len(content):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    print(f"{name}: start={idx}, end={i}, chars={i-idx}")
                    print(f"  Context before end: ...{repr(content[i-30:i])}")
                    print(f"  Context after end: {repr(content[i:i+30])}")
                    break
            i += 1

# Also check if there are stray }; in the file
print("\nAll '};' occurrences after dicts.zh:")
idx = content.find('dicts.zh = {')
pos = idx
while True:
    pos = content.find('};', pos + 1)
    if pos == -1 or pos > len(content) - 10:
        break
    if pos < idx + 10:
        continue
    print(f"  pos {pos}: {repr(content[pos-20:pos+10])}")
    if pos > idx + 50000:
        break
