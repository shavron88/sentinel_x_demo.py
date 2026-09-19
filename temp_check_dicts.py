import re

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract EN dict keys
en_match = re.search(r"dicts\.en\s*=\s*\{(.+?)\n\s*\};", content, re.DOTALL)
en_dict = {}
if en_match:
    for m in re.finditer(r"'([^']+)':\s*(.+?),\s*\n", en_match.group(1)):
        en_dict[m.group(1)] = m.group(2)

# Extract ZH dict keys
zh_start = en_match.end() if en_match else 0
zh_match = re.search(r"dicts\.zh\s*=\s*\{(.+?)\n\s*\};", content[zh_start:], re.DOTALL)
zh_dict = {}
if zh_match:
    for m in re.finditer(r"'([^']+)':\s*(.+?),\s*\n", zh_match.group(1)):
        zh_dict[m.group(1)] = m.group(2)

# Extract UR dict keys
ur_start = zh_start + (zh_match.end() if zh_match else 0)
ur_match = re.search(r"dicts\.ur\s*=\s*\{(.+?)\n\s*\};", content[ur_start:], re.DOTALL)
ur_dict = {}
if ur_match:
    for m in re.finditer(r"'([^']+)':\s*(.+?),\s*\n", ur_match.group(1)):
        ur_dict[m.group(1)] = m.group(2)

print(f"EN: {len(en_dict)} keys")
print(f"ZH: {len(zh_dict)} keys")
print(f"UR: {len(ur_dict)} keys")

# Find missing keys
en_keys = set(en_dict.keys())
zh_keys = set(zh_dict.keys())
ur_keys = set(ur_dict.keys())

print(f"\nZH missing ({len(en_keys - zh_keys)}): {sorted(en_keys - zh_keys)}")
print(f"UR missing ({len(en_keys - ur_keys)}): {sorted(en_keys - ur_keys)}")
