#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

def do_replace(old, new, label):
    global content
    if old not in content:
        print(f"FAIL: {label}")
        # Show what's nearby
        idx = content.find(old[:30])
        if idx >= 0:
            print(f"  Found start at {idx}, nearby: {repr(content[idx:idx+100])}")
        return False
    content = content.replace(old, new, 1)
    changes.append(label)
    print(f"OK: {label}")
    return True

# ═══ Fix garbled Urdu lim.5 ═══
# The file has literal \uXXXX escape sequences, so use raw string
old_lim5 = r"'lim.5': 'AI \u0646\u06af\u0631\u0627\u0646\u06cc \u06a9\u0648 \u0630\u0645\u06c1 \u062f\u0627\u0631\u06cc \u0633\u06d2 \u0646\u0627\u0641\u0630 \u06a9\u06cc\u0627 \u062c\u0627\u0646\u0627 \u0686\u0627\u06c1\u06cc\u06d2\u06d4',"
new_lim5 = "'lim.5': 'AI نگرانی کو شفاف طور پر ڈپلائی کرنا چاہیے، اور یہ عمل کے اصول یا مقام کی پالیسی کے مطابق ہو۔',"
do_replace(old_lim5, new_lim5, "Fix garbled Urdu lim.5")

# ═══ Update en-dict problem values ═══
# Check exact content first
idx = content.find("'problem.4.desc'")
if idx >= 0:
    snippet = content[idx:idx+200]
    print(f"\n  problem.4.desc found: {repr(snippet[:80])}")
    # Check for em-dash
    if '—' in snippet:
        print("  Em-dash found in problem.4.desc")
    elif '-' in snippet:
        # Find what dash character is there
        dash_pos = snippet.find('records rather')
        if dash_pos >= 0:
            print(f"  Char after 'understands': {repr(snippet[dash_pos+15])}")

old_problem_full = content[content.find("    'problem.badge': 'The Challenge'"):content.find("    'problem.4.desc': 'Traditional") + 300]
print(f"\n  problem section length: {len(old_problem_full)}")
print(f"  problem.4.desc starts at internal pos: {old_problem_full.find('problem.4.desc')}")

# Let me just build the old string from the file itself
prob_start = content.find("    'problem.badge': 'The Challenge'")
prob_end_marker = "    'problem.5.title'"
prob_end = content.find(prob_end_marker, prob_start)
if prob_end > prob_start:
    actual_problem = content[prob_start:prob_end].rstrip()
    # Remove trailing newline for matching
    if actual_problem.endswith(','):
        actual_problem = actual_problem[:-1].rstrip()
    print(f"\n  Actual problem section ({len(actual_problem)} chars):")
    print(f"  First 80: {repr(actual_problem[:80])}")
    print(f"  Last 80: {repr(actual_problem[-80:])}")

# Build replacement
new_problem = """    'problem.label': '// 01 — the problem',
    'problem.badge': 'The Challenge',
    'problem.title': 'Traditional CCTV records. It doesn\\'t understand.',
    'problem.desc': 'Most surveillance systems record footage but don\\'t understand what they see. Security teams face challenges that technology should help solve.',
    'problem.1.title': 'Continuous monitoring is impossible',
    'problem.1.desc': 'Humans cannot effectively watch every camera feed at once. Attention fatigue leads to missed events.',
    'problem.2.title': 'Critical events get missed',
    'problem.2.desc': 'Important security events can go unnoticed in real time, only discovered after damage has occurred.',
    'problem.3.title': 'Footage review is inefficient',
    'problem.3.desc': 'Reviewing hours of recorded video to find one incident is slow and resource-intensive.',
    'problem.4.title': 'Reactive, not proactive',
    'problem.4.desc': 'CCTV captures what happened — it doesn\\'t alert anyone while it\\'s happening.',"""

# Find and replace the problem section
if prob_start >= 0 and prob_end > prob_start:
    # Extract the exact old text
    old_text = content[prob_start:prob_end].rstrip()
    # The old text ends with a comma before the next line
    # Let's just replace from prob_start to prob_end
    content = content[:prob_start] + new_problem + ",\n" + content[prob_end:]
    changes.append("Update en-dict problem values")
    print("OK: Update en-dict problem values")
else:
    print(f"FAIL: Could not find problem section boundaries ({prob_start}, {prob_end})")

# ═══ Update en-dict solution values ═══
sol_start = content.find("    'solution.badge': 'The Sentinel-X Solution'")
sol_end = content.find("    'solution.pipe.camera'", sol_start)
if sol_start >= 0 and sol_end > sol_start:
    old_sol_text = content[sol_start:sol_end].rstrip()
    print(f"\n  Solution section ({len(old_sol_text)} chars):")
    print(f"  Content: {repr(old_sol_text[:100])}")

    new_sol = """    'solution.label': '// 02 — the solution',
    'solution.badge': 'The Sentinel-X Solution',
    'solution.title': 'From raw video to security intelligence',
    'solution.desc': 'Sentinel-X processes camera streams through a multi-stage AI pipeline that transforms raw footage into structured, actionable events.',"""

    content = content[:sol_start] + new_sol + ",\n" + content[sol_end:]
    changes.append("Update en-dict solution values")
    print("OK: Update en-dict solution values")
else:
    print(f"FAIL: Could not find solution section ({sol_start}, {sol_end})")

# ═══ Fix solution.pipe.alert -> solution.pipe.threat ═══
old_pipe = "    'solution.pipe.analysis': 'Analysis', 'solution.pipe.alert': 'Alert',\n    'solution.pipe.evidence': 'Evidence', 'solution.pipe.dashboard': 'Dashboard',"
new_pipe = "    'solution.pipe.analysis': 'ANALYSIS', 'solution.pipe.threat': 'THREAT',\n    'solution.pipe.evidence': 'EVIDENCE', 'solution.pipe.dashboard': 'DASHBOARD',"
if old_pipe in content:
    content = content.replace(old_pipe, new_pipe, 1)
    changes.append("Fix solution.pipe labels + change alert to threat")
    print("OK: Fix solution.pipe labels + change alert to threat")
else:
    # Check what the actual content looks like
    idx = content.find("'solution.pipe.analysis'")
    if idx >= 0:
        print(f"\n  pipe section: {repr(content[idx:idx+300])}")
    else:
        print("FAIL: solution.pipe.analysis not found at all")
    # Maybe the format is different (each on own line?)
    old_pipe2 = "    'solution.pipe.analysis': 'Analysis',\n    'solution.pipe.alert': 'Alert',\n    'solution.pipe.evidence': 'Evidence',\n    'solution.pipe.dashboard': 'Dashboard',"
    if old_pipe2 in content:
        content = content.replace(old_pipe2, new_pipe, 1)
        changes.append("Fix solution.pipe labels + change alert to threat")
        print("OK (alt format): Fix solution.pipe labels + change alert to threat")
    else:
        print("FAIL: Could not match solution.pipe format")

# Save
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*60}")
print(f"Total changes applied: {len(changes)}")
for c in changes:
    print(f"  ✓ {c}")
