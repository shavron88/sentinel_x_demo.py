#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Get full lim.4 and lim.5 from ur dict (occurrence #3)
idx4_ur = 77140
idx5_ur = 77424
print("=== lim.4 ur full ===")
print(repr(content[idx4_ur:idx4_ur+300]))
print("\n=== lim.5 ur full ===")
print(repr(content[idx5_ur:idx5_ur+300]))

# Also check solution.pipe.dashboard for the double-escape issue
idx_pd = content.find("'solution.pipe.dashboard'")
print("\n=== solution.pipe.dashboard ===")
print(repr(content[idx_pd:idx_pd+120]))

# Check the en-dict solution.pipe.alert
idx_sa = content.find("'solution.pipe.alert'")
print("\n=== solution.pipe.alert en-dict ===")
print(repr(content[idx_sa:idx_sa+120]))

# Check ur-dict solution.pipe
idx_sa_ur = content.find("'solution.pipe.alert'", 550)
print("\n=== solution.pipe.alert ur-dict ===")
print(repr(content[idx_sa_ur:idx_sa_ur+120]))

# Check zh-dict solution.pipe
idx_sa_zh = content.find("'solution.pipe.alert'", 290)
print("\n=== solution.pipe.alert zh-dict ===")
print(repr(content[idx_sa_zh:idx_sa_zh+120]))
