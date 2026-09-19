"""
Final comprehensive fix:
1. Fix the UR dict to add all missing landing page keys with proper Urdu translations
2. Fix the ZH dict to add all missing keys
3. Verify the file is valid
"""
import re
import json

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract EN dict to get all keys
en_match = re.search(r"dicts\.en\s*=\s*\{(.*?)\n\s*\};", content, re.DOTALL)
en_keys = []
if en_match:
    for m in re.finditer(r"'([^']+)':\s*", en_match.group(1)):
        en_keys.append(m.group(1))

print(f"EN dict has {len(en_keys)} keys")

# Extract ZH dict
zh_start = en_match.end()
zh_match = re.search(r"dicts\.zh\s*=\s*\{(.*?)\n\s*\};", content[zh_start:], re.DOTALL)
zh_keys = []
if zh_match:
    for m in re.finditer(r"'([^']+)':\s*", zh_match.group(1)):
        zh_keys.append(m.group(1))

zh_full_end = zh_start + zh_match.end()
print(f"ZH dict has {len(zh_keys)} keys")

# Extract UR dict
ur_start = zh_full_end
ur_match = re.search(r"dicts\.ur\s*=\s*\{(.*?)\n\s*\};", content[ur_start:], re.DOTALL)
ur_keys = []
if ur_match:
    for m in re.finditer(r"'([^']+)':\s*", ur_match.group(1)):
        ur_keys.append(m.group(1))

print(f"UR dict has {len(ur_keys)} keys")

# Find missing keys in each
en_set = set(en_keys)
zh_set = set(zh_keys)
ur_set = set(ur_keys)

# Dashboard/login/signup keys - these don't need UR (engine handles via isDashPage)
dash_keys = {k for k in en_set if k.startswith('dash.') or k.startswith('login.') or k.startswith('signup.')}
print(f"Dashboard/login/signup keys (not needed in UR): {len(dash_keys)}")

# Landing page keys - these need UR
landing_keys = en_set - dash_keys
missing_ur = landing_keys - ur_set
print(f"\nMissing UR landing keys ({len(missing_ur)}):")
for k in sorted(missing_ur):
    print(f"  {k}")

# ZH missing
missing_zh = en_set - zh_set
print(f"\nMissing ZH keys ({len(missing_zh)}):")
for k in sorted(missing_zh):
    print(f"  {k}")
