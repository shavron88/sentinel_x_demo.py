"""
Check dict completeness for the rebuilt i18n.js
"""
import re

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all three dicts
def extract_dict_keys(text, dict_name):
    pattern = rf"dicts\.{dict_name}\s*=\s*\{{(.*?)\n\s*\}};"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        # Try without trailing ;
        pattern = rf"dicts\.{dict_name}\s*=\s*\{{(.*?)\n\s*\}}"
        match = re.search(pattern, text, re.DOTALL)
    if not match:
        print(f"Could not find dict.{dict_name}")
        return set()
    
    keys = set(re.findall(r"'([^']+)':\s*", match.group(1)))
    return keys

en_keys = extract_dict_keys(content, 'en')
zh_keys = extract_dict_keys(content, 'zh')
ur_keys = extract_dict_keys(content, 'ur')

print(f"EN: {len(en_keys)} keys")
print(f"ZH: {len(zh_keys)} keys")
print(f"UR: {len(ur_keys)} keys")

# Dashboard/login/signup keys
dash_keys = {k for k in en_keys if k.startswith('dash.') or k.startswith('login.') or k.startswith('signup.')}
print(f"Dashboard/login/signup keys: {len(dash_keys)}")

# Landing page keys
landing_keys = en_keys - dash_keys
missing_ur = landing_keys - ur_keys
print(f"\nMissing UR landing keys ({len(missing_ur)}):")
for k in sorted(missing_ur):
    print(f"  {k}")

missing_zh = en_keys - zh_keys
print(f"\nMissing ZH keys ({len(missing_zh)}):")
for k in sorted(missing_zh):
    print(f"  {k}")

# Check for any duplicate keys or syntax issues
en_match = re.search(r"dicts\.en\s*=\s*\{(.*?\n\s*\});", content, re.DOTALL)
if en_match:
    # Check for consecutive commas
    if ',,' in content[en_match.start():en_match.end()]:
        print("\nWARNING: Double commas found in EN dict")
    # Check for sec.* titles
    for m in re.finditer(r"'sec\.[^']+\.title':\s*'([^']+)'", en_match.group(1)):
        print(f"  EN sec title: {m.group(1)}")
