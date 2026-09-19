"""Debug UR dict - write to file"""
import re, sys

with open(r'dashboard\static\js\i18n.js', 'r', encoding='utf-8') as f:
    content = f.read()

engine_idx = content.find('/* ===')
ur_section_start = content.rfind('dicts.ur = {', 0, engine_idx)
ur_section = content[ur_section_start:engine_idx]

restapi_pos = ur_section.rfind("'tech.restapi.role'")

output = []
output.append(f"restapi_pos: {restapi_pos}")

if restapi_pos > 0:
    start = max(0, restapi_pos - 20)
    end = min(len(ur_section), restapi_pos + 200)
    context = ur_section[start:end]
    output.append(f"Context length: {len(context)}")
    output.append(f"Context repr: {repr(context[:200])}")

output.append(f"End of UR section: {repr(ur_section[-50:])}")

# Find closing };
for i in range(len(ur_section) - 2):
    if ur_section[i:i+2] == '};':
        output.append(f"Found closing at position {i}")
        context = ur_section[i-50:i+20]
        output.append(f"Context: {repr(context)}")
        break

with open('debug_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print("Done - check debug_output.txt")
