#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Check lim.5 ur (the garbled one)
# Find the ur-dict lim.5
positions = []
start = 0
while True:
    idx = content.find("'lim.5':", start)
    if idx == -1:
        break
    positions.append(idx)
    start = idx + 1

print(f"Found {len(positions)} occurrences of lim.5:")
for i, pos in enumerate(positions):
    snippet = content[pos:pos+120]
    print(f"  loc #{i+1} at char {pos}: {repr(snippet)}")

# Check problem values
idx = content.find("'problem.badge'")
print(f"\nproblem.badge at char {idx}:")
print(repr(content[idx:idx+800]))

# Check solution values
idx = content.find("'solution.badge'")
print(f"\nsolution.badge at char {idx}:")
print(repr(content[idx:idx+600]))
