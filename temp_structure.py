#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We'll work with line-based replacements
# First, let's understand the structure by finding section markers
section_starts = {}
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('dicts.en') or stripped.startswith('dicts.zh') or stripped.startswith('dicts.ur'):
        name = stripped.split('=')[0].strip()
        section_starts[name] = i
    if stripped.startswith('// ──') or stripped.startswith('// ── Login') or stripped.startswith('// ── Signup') or stripped.startswith('// ── Dashboard') or stripped.startswith('// ── Application') or stripped.startswith('// ── Evidence') or stripped.startswith('// ── FAQ'):
        print(f"  Line {i+1}: {stripped}")

print(f"\nTotal lines: {len(lines)}")
print(f"EN dict starts at line {section_starts.get('dicts.en', '?')+1}")
print(f"ZH dict starts at line {section_starts.get('dicts.zh', '?')+1}")
print(f"UR dict starts at line {section_starts.get('dicts.ur', '?')+1}")

# Find the end of each dict (the line with just `};`)
for dict_name, start in section_starts.items():
    for i in range(start, len(lines)):
        if lines[i].strip() == '};':
            print(f"  {dict_name} ends at line {i+1}")
            break
