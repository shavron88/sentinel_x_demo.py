#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find dicts.zh = {
zh_match = re.search(r"dicts\.zh = \{", content)
if not zh_match:
    print("Could not find dicts.zh")
    sys.exit(1)

print(f"dicts.zh = {{ at char {zh_match.start()}")

# Find the closing brace by counting
start = zh_match.end()  # position right after the opening {
depth = 1
i = start
brace_positions = []
while i < len(content) and depth > 0:
    if content[i] == '{':
        depth += 1
        brace_positions.append((i, '{'))
    elif content[i] == '}':
        depth -= 1
        brace_positions.append((i, '}'))
    i += 1

print(f"Closing brace at char {i-1}, depth={depth}")
print(f"Total braces found: {len(brace_positions)}")
if brace_positions:
    print(f"Last 5 brace positions: {brace_positions[-5:]}")
    for pos, ch in brace_positions[-5:]:
        print(f"  pos {pos}: {ch} context: {repr(content[pos-20:pos+20])}")
