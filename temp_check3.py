#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Reconstruct old_problem exactly
old_problem = """    'problem.badge': 'The Challenge',
    'problem.title': 'Traditional CCTV Has Limits',
    'problem.desc': 'Most surveillance systems record footage but don\\'t understand what they see. Security teams face challenges that technology should help solve.',
    'problem.1.title': 'Continuous Monitoring Is Impossible',
    'problem.1.desc': 'Humans cannot effectively watch every camera feed simultaneously. Attention fatigue leads to missed events.',
    'problem.2.title': 'Critical Events Get Missed',
    'problem.2.desc': 'Important security events can go unnoticed in real time, only discovered after damage has occurred.',
    'problem.3.title': 'Footage Review Is Inefficient',
    'problem.3.desc': 'Reviewing hours of recorded video to find a specific incident is time-consuming and resource-intensive.',
    'problem.4.title': 'Reactive, Not Proactive',
    'problem.4.desc': 'Traditional CCTV primarily records rather than understands — it captures what happened, but doesn\\'t alert you while it\\'s happening.',"""

# Find the exact problem section in the file
start = content.find("'problem.badge': 'The Challenge'")
if start >= 0:
    # Find the end (look for 13 lines)
    line_end = content.find("'problem.4.desc'", start) + 200
    actual = content[start:line_end]
    print("=== ACTUAL file content (repr) ===")
    print(repr(actual[:600]))
    print("\n=== EXPECTED old_problem (repr) ===")
    print(repr(old_problem[:600]))

# Try char-by-char comparison
for i in range(min(len(actual), len(old_problem))):
    if actual[i] != old_problem[i]:
        print(f"\nFirst mismatch at char {i}:")
        print(f"  Actual: {repr(actual[i:i+30])}")
        print(f"  Expected: {repr(old_problem[i:i+30])}")
        break
else:
    if len(actual) >= len(old_problem):
        print("\nFirst 600 chars match perfectly!")
    else:
        print(f"\nActual is shorter: {len(actual)} vs {len(old_problem)}")

# Now check the em-dash
print("\n=== Em-dash check ===")
dash_idx = actual.find('—')
if dash_idx >= 0:
    print(f"Found em-dash at position {dash_idx}: {repr(actual[dash_idx:dash_idx+5])}")
else:
    print("No em-dash found in actual content")
    dash_idx = old_problem.find('—')
    if dash_idx >= 0:
        print(f"Em-dash in expected at position {dash_idx}: {repr(old_problem[dash_idx:dash_idx+5])}")
