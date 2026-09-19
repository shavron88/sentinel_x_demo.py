"""
Fix sec.* titles in EN and ZH dicts - remove emoji escape sequences
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
changes = 0

for line in lines:
    # Fix EN sec.* titles - remove emoji escape sequences
    if 'sec.auth.title' in line and 'Authentication' in line:
        if '\\ud83d' in line or '\\u' in line:
            # Replace the entire value with clean version
            line = re.sub(r"'sec\.auth\.title':\s*'[^']+'", "'sec.auth.title': 'Authentication'", line)
            changes += 1
    elif 'sec.protected.title' in line and 'Protected' in line:
        if '\\ud83d' in line or '\\u' in line:
            line = re.sub(r"'sec\.protected\.title':\s*'[^']+'", "'sec.protected.title': 'Protected Dashboard'", line)
            changes += 1
    elif 'sec.access.title' in line and 'Controlled' in line:
        if '\\ud83d' in line or '\\u' in line:
            line = re.sub(r"'sec\.access\.title':\s*'[^']+'", "'sec.access.title': 'Controlled Access'", line)
            changes += 1
    elif 'sec.evidence.title' in line and 'Evidence' in line:
        if '\\ud83d' in line or '\\u' in line:
            line = re.sub(r"'sec\.evidence\.title':\s*'[^']+'", "'sec.evidence.title': 'Evidence Management'", line)
            changes += 1
    elif 'sec.history.title' in line and 'Event History' in line:
        if '\\ud83d' in line or '\\u' in line:
            line = re.sub(r"'sec\.history\.title':\s*'[^']+'", "'sec.history.title': 'Event History'", line)
            changes += 1
    elif 'sec.ai.title' in line and ('Responsible' in line or '负责' in line):
        # Fix both EN and ZH
        line = re.sub(r"'sec\.ai\.title':\s*'[^']+'", "'sec.ai.title': 'Responsible AI'", line)
        changes += 1
    
    output_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"Fixed {changes} sec.* title lines")
