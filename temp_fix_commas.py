"""
Fix missing commas after the last entry in each dict
"""
import re

file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix EN dict: add comma after signup.errorConn
en_pattern = r"('signup\.errorConn':\s*'[^']+'\s*)\n(\s*'problem\.label')"
content = re.sub(en_pattern, r"\1,\n\2", content)
print("Fixed EN dict comma")

# Fix ZH dict: add comma after login.errorConnection  
zh_pattern = r"('login\.errorConnection':\s*'[^']+'\s*)\n(\s*'problem\.label')"
content = re.sub(zh_pattern, r"\1,\n\2", content)
print("Fixed ZH dict comma")

# Fix UR dict: add comma after footer.text
ur_pattern = r"('footer\.text':\s*'[^']+'\s*)\n(\s*'problem\.label')"
content = re.sub(ur_pattern, r"\1,\n\2", content)
print("Fixed UR dict comma")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated")
