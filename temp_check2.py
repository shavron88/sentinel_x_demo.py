#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix lim.5 ur - the file uses literal \uXXXX, so I need raw strings
# Find the exact ur-dict lim.5
idx = content.find("'lim.5': 'AI \\u0646")  # Looking for the ur-dict version
if idx == -1:
    # Try without the AI space
    idx = content.find("'lim.5': 'AI", 70000)
    if idx >= 0:
        print("Found lim.5 ur near char", idx)
        print(repr(content[idx:idx+80]))

# Let me also check problem section
idx_p = content.find("'problem.badge': 'The Challenge'")
if idx_p >= 0:
    print("\n=== problem section exists at char", idx_p, "===")
    # Check if our changes already changed something
    print(repr(content[idx_p:idx_p+30]))

# Check if any of our changes already applied
print("\n=== Checking if hero changes applied ===")
if "'hero.liveCameras'" in content:
    print("hero.liveCameras: YES (already changed)")
else:
    print("hero.liveCameras: NO")

print("\n=== Checking if solution changes applied ===")
if "'solution.pipe.threat'" in content:
    print("solution.pipe.threat: YES (already changed)")
else:
    print("solution.pipe.threat: NO")

# Check exact repr around problem.badge
idx_pb = content.find("'problem.badge'")
print("\n=== problem.badge exact repr ===")
print(repr(content[idx_pb:idx_pb+10]))

# Check exact repr around solution.badge
idx_sb = content.find("'solution.badge'")
print("\n=== solution.badge exact repr ===")
print(repr(content[idx_sb:idx_sb+10]))

# Now let's try the exact replacements
# For lim.5 ur:
old_lim5 = "'lim.5': 'AI \\u0646\\u06af\\u0631\\u0627\\u0646\\u06cc \\u06a9\\u0648 \\u0630\\u0645\\u06c1 \\u062f\\u0627\\u0631\\u06cc \\u0633\\u06d2 \\u0646\\u0627\\u0641\\u0630 \\u06a9\\u06cc\\u0627 \\u062c\\u0627\\u0646\\u0627 \\u0686\\u0627\\u06c1\\u06cc\\u06d2\\u06d4',"
new_lim5 = "'lim.5': '\u0646\u06cc\u0679 \u0648\u0631\u06a9 \u06a9\u06cc\u0645\u0631\u0648\u06ba \u06a9\u0648 \u0634\u0627\u06a9\u0633\u06cc \u0637\u0648\u0631 \u067e\u0631 \u0686\u0627\u06c1\u06cc \u06d9 \u062f\u06cc\u0691 \u0644\u06cc\u06d4 \u0627\u0648\u0631 \u06a9\u0648 \u0639\u0645\u0644 \u06a9\u06cc \u0627\u0635\u0644 \u06cc\u0627 \u0645\u0642\u0627\u0645\u06cc \u067e\u0627\u0644\u06cc\u0633\u06cc \u06a9\u06c1 \u0645\u0637\u0627\u0628\u0642 \u06c1\u0648 \u06af\u06cc\u0611 \u06d4',"

print("\n=== Testing lim.5 replacement ===")
if old_lim5 in content:
    print("MATCH FOUND!")
else:
    print("NOT FOUND. Let's check what's there...")
    # Find lim.5 in ur dict
    idx = content.find("'lim.5': 'AI", 70000)
    if idx >= 0:
        actual = content[idx:idx+200]
        print("Actual content:", repr(actual))
        print("\nExpected:", repr(old_lim5[:100]))

# For problem: the issue might be with don\'t escaping
# Let's check
old_prob_test = "don\\'t understand"
print("\n=== Testing problem.desc substring ===")
if old_prob_test in content:
    print("FOUND: don\\'t understand")
else:
    print("NOT FOUND: don\\'t understand")
    # Try without the backslash
    old_prob_test2 = "don't understand"
    if old_prob_test2 in content:
        print("FOUND: don't understand (no backslash)")
    else:
        # Search for problem.desc
        idx = content.find("'problem.desc':")
        if idx >= 0:
            print("Found problem.desc at:", repr(content[idx:idx+100]))
