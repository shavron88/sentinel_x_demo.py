#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find dicts.zh = {
idx = content.find('dicts.zh = {')
print(f"dicts.zh = {{ at char {idx}")

# Check if there's an opening brace
open_brace = content.find('{', idx)
print(f"Opening brace at char {open_brace}")

# Count braces starting from the opening brace
depth = 0
i = open_brace
issues = []
while i < len(content) and depth >= 0:
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            print(f"Found closing brace at char {i}")
            print(f"Content after: {repr(content[i:i+20])}")
            break
    i += 1

if depth > 0:
    print(f"Depth never reached 0! Final depth at end of file: {depth}")
    # Find all single } (not };) after the opening
    pos = open_brace + 1
    count = 0
    while True:
        pos = content.find('}', pos + 1)
        if pos == -1 or pos > 94800:
            break
        context = content[pos-30:pos+10]
        print(f"  }} at pos {pos}: {repr(context)}")
        count += 1
        if count > 20:
            print("  ... (stopping at 20)")
            break

# Also check: what does the content look like right after the EN dict's closing }?
en_end = content.find('};\n\n', 27000)
if en_end >= 0:
    print(f"\nEN dict closes at {en_end}")
    print(f"Content after EN close: {repr(content[en_end:en_end+100])}")
# Find what's between EN and UR dicts
ur_start = content.find('dicts.ur = {')
between = content[en_end:ur_start] if en_end >= 0 else ""
print(f"\nContent between EN close and UR start ({len(between)} chars):")
# Find dicts.zh within this
zh_in_between = between.find('dicts.zh')
if zh_in_between >= 0:
    print(f"  dicts.zh found at offset {zh_in_between} in 'between'")
    print(f"  Context: {repr(between[zh_in_between-20:zh_in_between+50])}")
else:
    print("  dicts.zh NOT found between EN and UR")
    # Check if it's somewhere else
    zh_idx = content.find('dicts.zh')
    print(f"  dicts.zh found at char {zh_idx}")
