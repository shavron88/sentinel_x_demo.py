"""
Fix ZH sec.* titles - remove emoji escape sequences (proper version)
"""
file_path = r'dashboard\static\js\i18n.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ZH sec.* titles to fix - replace with clean values
zh_sec_fixes = {
    'sec.auth.title': '身份验证',
    'sec.protected.title': '受保护的仪表盘',
    'sec.access.title': '受控件访问',
    'sec.evidence.title': '证据管理',
    'sec.history.title': '事件历史',
}

changes = 0
for i, line in enumerate(lines):
    for key, clean_value in zh_sec_fixes.items():
        # Check if this line is for one of the keys we want to fix
        if f"'{key}'" in line and '\\u' in line:
            lines[i] = f"    '{key}': '{clean_value}',\n"
            changes += 1
            break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Fixed {changes} ZH sec.* title lines")
