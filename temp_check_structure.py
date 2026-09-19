"""
Check the structure of i18n.js dicts
"""
import re

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find dict boundaries
en_start = content.find('dicts.en = {')
zh_start = content.find('dicts.zh = {')
ur_start = content.find('dicts.ur = {')

# Find closing }; for each dict
# Look for "  };" at start of line (2 spaces indent)
def find_closing(s, start):
    """Find the closing }; that's at the dict level (2-space indent)"""
    pos = start
    while pos < len(s):
        match = re.search(r'\n  \};', s[pos:])
        if match:
            return pos + match.start()
        return -1

en_close = find_closing(content, en_start)
zh_close = find_closing(content, zh_start)
ur_close = find_closing(content, ur_start)

print(f"EN: start={en_start}, close={en_close}")
print(f"ZH: start={zh_start}, close={zh_close}")
print(f"UR: start={ur_start}, close={ur_close}")

# Show last few lines of EN dict
if en_close:
    print("\nEN dict last lines:")
    print(repr(content[en_close-100:en_close+50]))

if zh_close:
    print("\nZH dict last lines:")
    print(repr(content[zh_close-100:zh_close+50]))

if ur_close:
    print("\nUR dict last lines:")
    print(repr(content[ur_close-100:ur_close+50]))
