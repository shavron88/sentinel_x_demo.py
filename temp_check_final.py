"""Check dict completeness"""
import re

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

def extract_dict_keys(text, dict_name):
    pattern = rf"dicts\.{dict_name}\s*=\s*\{{(.*?)\n\s*\}}".replace("\\\\", "\\\\")
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        match = re.search(rf"dicts\.{dict_name}\s*=\s*\{{(.*?)\}}", text, re.DOTALL)
    if not match:
        return set()
    return set(re.findall(r"'([^']+)':\s*", match.group(1)))

en_keys = extract_dict_keys(content, 'en')
zh_keys = extract_dict_keys(content, 'zh')
ur_keys = extract_dict_keys(content, 'ur')

print(f"EN: {len(en_keys)} keys")
print(f"ZH: {len(zh_keys)} keys")
print(f"UR: {len(ur_keys)} keys")

dash_keys = {k for k in en_keys if k.startswith('dash.') or k.startswith('login.') or k.startswith('signup.')}
landing_keys = en_keys - dash_keys
missing_ur = landing_keys - ur_keys
missing_zh = en_keys - zh_keys

print(f"\nMissing UR landing keys: {len(missing_ur)}")
if missing_ur:
    for k in sorted(missing_ur):
        print(f"  {k}")

print(f"\nMissing ZH keys: {len(missing_zh)}")
if missing_zh:
    for k in sorted(missing_zh):
        print(f"  {k}")
