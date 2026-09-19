"""
Check what keys exist in EN dict and what's missing from the plan
"""
import re

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract EN dict
en_match = re.search(r"dicts\.en\s*=\s*\{(.*?)\n\s*\};", content, re.DOTALL)
en_keys = set()
if en_match:
    for m in re.finditer(r"'([^']+)':\s*", en_match.group(1)):
        en_keys.add(m.group(1))

# Check for section labels
label_keys = ['problem.label', 'solution.label', 'how.label', 'cap.label', 'lim.label', 
              'use.label', 'preview.label', 'sec.label', 'tech.label', 'future.label']
print("Section label keys in EN:")
for k in label_keys:
    print(f"  {k}: {'YES' if k in en_keys else 'NO'}")

# Check for hero additional keys
hero_keys = ['hero.liveCameras', 'hero.viewDashboard']
print("\nHero additional keys:")
for k in hero_keys:
    print(f"  {k}: {'YES' if k in en_keys else 'NO'}")

# Check for evidence keys
evidence_keys = [k for k in en_keys if k.startswith('evidence.')]
print(f"\nEvidence keys: {evidence_keys}")

# Check for FAQ keys
faq_keys = [k for k in en_keys if k.startswith('faq.')]
print(f"\nFAQ keys: {faq_keys}")

# Check for future roadmap keys
roadmap_keys = [k for k in en_keys if k.startswith('future.roadmap')]
print(f"\nFuture roadmap keys: {roadmap_keys}")

# Check for footer keys
footer_keys = [k for k in en_keys if k.startswith('footer.')]
print(f"\nFooter keys: {footer_keys}")

# Check for sec.* emojis
sec_titles = [k for k in en_keys if k.startswith('sec.') and k.endswith('.title')]
print(f"\nSec titles in EN:")
for k in sec_titles:
    # Find the value
    match = re.search(rf"'{k}':\s*'([^']+)'", en_match.group(1))
    if match:
        print(f"  {k}: {repr(match.group(1)[:50])}")

# Check cap.loitering keys
print(f"\ncap.loitering keys: {[k for k in en_keys if 'loitering' in k]}")

# Print all keys
print(f"\nAll EN keys ({len(en_keys)}):")
for k in sorted(en_keys):
    print(f"  {k}")
