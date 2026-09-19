import re

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find login.errorConnection
match = re.search(r"'login\.errorConnection'.*?\n", content)
if match:
    start = max(0, match.start() - 100)
    end = min(len(content), match.end() + 200)
    print("ZH area:")
    print(repr(content[start:end]))

# Find footer.text in UR
match2 = re.search(r"'footer\.text'.*?\n", content)
if match2:
    start = max(0, match2.start() - 50)
    end = min(len(content), match2.end() + 200)
    print("\nUR area:")
    print(repr(content[start:end]))
