import re

filepath = r'C:\Users\haroon traders\OneDrive\Desktop\sentinel_x_demo.py\dashboard\templates\landing.html'

with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Fix lines 2071-2125 (1-indexed)
# The reports preview page structure:
# 8 spaces: <div class="preview-page" data-page="reports">
# 10 spaces: <div class="preview-page-desc">
# 10 spaces: <div class="preview-reports">
# 12 spaces: <div class="preview-report-toolbar">
# 14 spaces: toolbar children
# 12 spaces: </div> (toolbar close)
# 12 spaces: <div class="preview-stats-grid">
# 14 spaces: stat cards
# 12 spaces: </div> (stats-grid close)
# 12 spaces: <div class="preview-report-section">
# 14 spaces: h4
# 14 spaces: table
# 16 spaces: thead
# 16 spaces: tbody
# 18 spaces: tr/td
# 16 spaces: </tbody>
# 14 spaces: </table>
# 12 spaces: </div> (section close)
# 12 spaces: <div class="preview-export-buttons">
# 14 spaces: buttons
# 12 spaces: </div> (export-buttons close)
# 10 spaces: </div> (preview-reports close)
# 8 spaces: </div> (preview-page close)

new_lines = []
for i, line in enumerate(lines):
    idx = i + 1  # 1-indexed

    if idx == 2071:
        new_lines.append('        <div class="preview-page" data-page="reports">\n')
    elif idx == 2072:
        new_lines.append('          <div class="preview-page-desc">Generate and review structured security reports.</div>\n')
    elif idx == 2073:
        new_lines.append('          <div class="preview-reports">\n')
    elif idx == 2074:
        new_lines.append('            <div class="preview-report-toolbar">\n')
    elif idx in [2075, 2076, 2077]:
        new_lines.append('              ' + line.lstrip())
    elif idx == 2078:
        new_lines.append('            </div>\n')
    elif idx == 2079:
        new_lines.append('            <div class="preview-stats-grid">\n')
    elif idx in [2080, 2081, 2082, 2083]:
        new_lines.append('              ' + line.lstrip())
    elif idx == 2084:
        new_lines.append('            </div>\n')
    elif idx == 2085:
        new_lines.append('            <div class="preview-report-section">\n')
    elif idx == 2086:
        new_lines.append('              ' + line.lstrip())
    elif idx == 2087:
        new_lines.append('              <table class="preview-report-table">\n')
    elif idx == 2088:
        new_lines.append('                ' + line.lstrip())
    elif idx in [2089, 2090, 2091, 2092, 2093, 2094]:
        new_lines.append('                  ' + line.lstrip())
    elif idx == 2095:
        new_lines.append('                </tbody>\n')
    elif idx == 2096:
        new_lines.append('              </table>\n')
    elif idx == 2097:
        new_lines.append('            </div>\n')
    elif idx == 2098:
        new_lines.append('            <div class="preview-report-section">\n')
    elif idx == 2099:
        new_lines.append('              ' + line.lstrip())
    elif idx == 2100:
        new_lines.append('              <table class="preview-report-table">\n')
    elif idx == 2101:
        new_lines.append('                ' + line.lstrip())
    elif idx in [2102, 2103, 2104, 2105, 2106]:
        new_lines.append('                  ' + line.lstrip())
    elif idx == 2107:
        new_lines.append('                </tbody>\n')
    elif idx == 2108:
        new_lines.append('              </table>\n')
    elif idx == 2109:
        new_lines.append('            </div>\n')
    elif idx == 2110:
        new_lines.append('            <div class="preview-report-section">\n')
    elif idx == 2111:
        new_lines.append('              ' + line.lstrip())
    elif idx == 2112:
        new_lines.append('              <table class="preview-report-table">\n')
    elif idx == 2113:
        new_lines.append('                ' + line.lstrip())
    elif idx in [2114, 2115, 2116]:
        new_lines.append('                  ' + line.lstrip())
    elif idx == 2117:
        new_lines.append('                </tbody>\n')
    elif idx == 2118:
        new_lines.append('              </table>\n')
    elif idx == 2119:
        new_lines.append('            </div>\n')
    elif idx == 2120:
        new_lines.append('            <div class="preview-export-buttons">\n')
    elif idx in [2121, 2122, 2123]:
        new_lines.append('              ' + line.lstrip())
    elif idx == 2124:
        new_lines.append('            </div>\n')
    elif idx == 2125:
        new_lines.append('          </div>\n')
    else:
        new_lines.append(line)

with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
    f.writelines(new_lines)

print('Done fixing Reports preview page indentation')