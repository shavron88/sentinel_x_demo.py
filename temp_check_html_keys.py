"""
Check for data-i18n keys in landing.html that are missing from i18n.js dicts
"""
import re

html_path = r'dashboard\templates\landing.html'
js_path = r'dashboard\static\js\i18n.js'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Extract all data-i18n keys from HTML
html_keys = set(re.findall(r'data-i18n="([^"]+)"', html))
print(f"HTML data-i18n keys: {len(html_keys)}")

# Extract EN dict keys
en_match = re.search(r"dicts\.en\s*=\s*\{(.*?)\n\s*\};", js, re.DOTALL)
en_keys = set(re.findall(r"'([^']+)':\s*", en_match.group(1)))
print(f"EN dict keys: {len(en_keys)}")

# Find HTML keys not in EN
missing = html_keys - en_keys
print(f"\nKeys in HTML but missing from EN ({len(missing)}):")
for k in sorted(missing):
    print(f"  {k}")

# Find EN keys not used in HTML
unused = en_keys - html_keys
print(f"\nKeys in EN but not used in HTML ({len(unused)}):")
for k in sorted(unused):
    print(f"  {k}")
