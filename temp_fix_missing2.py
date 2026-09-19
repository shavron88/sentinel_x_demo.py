#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'dashboard\static\js\i18n.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# ═══════════════════════════════════════════════════════
# FIX 1: Add missing ZH dict keys
# ═══════════════════════════════════════════════════════

zh_start = content.find('dicts.zh = {')
depth = 0
i = content.find('{', zh_start)
while i < len(content):
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            zh_close = i
            break
    i += 1

# Find insertion point
insert_point = zh_close
while insert_point > 0 and content[insert_point-1] in ' \t\n\r':
    insert_point -= 1

zh_missing = {
    'tech.python': "核心運行時",
    'tech.flask': "Web 框架",
    'tech.opencv': "視頻處理",
    'tech.yolo': "目標檢測",
    'tech.bytetrack': "目標跟蹤",
    'tech.sqlite': "數據存儲",
    'tech.jscss': "儀表板 UI",
    'future.edgeDesc': "專用於邊緣計算設備的硬件，用於將 Sentinel-X AI 處理部署在更靠近攝像頭基礎設施的位置 — 減少對集中計算的依賴，並可能提高部署靈活性、降低延遲和帶寬使用。",
    'future.cctv': "CCTV 攝像頭",
    'future.edgeNode': "Sentinel-X 邊緣盒子",
    'future.aiProc': "AI 處理",
    'future.alerts': "警報與事件",
    'future.cloud': "雲端儀表板",
    'future.disclaimer': "邊緣盒子是計劃中的未來工作。當前的 Sentinel-X 版本是純軟件平台。",
    'footer.text': "Sentinel-X AI 邊緣監控平台 · 版本 1.0 · 使用 Python、Flask、OpenCV、YOLO11 构建",
    'faq.5.q': "Sentinel-X 已經可以投入生產使用了嗎？",
    'faq.5.a': "它是一個功能完整的 MVP（版本 1.0） — 管道端對端運行，但限制是真實的：AI檢測可能會錯過事件，網絡可靠性很重要，實時吞吐量需要 GPU 加速。它已準備好評估，但尚未準備好完全信任。",
    'faq.6.q': "Sentinel-X 建立在什麼基礎上？",
    'faq.6.a': "Python、Flask、OpenCV 和 YOLO11 用於檢測，配合 ByteTrack 進行物體跟蹤。儀表板是您可以從任何現代瀏覽器訪問的 Web 界面。",
}

zh_lines = []
for key, val in zh_missing.items():
    zh_lines.append(f"    '{key}': '{val}',")
insert_text = "\n" + "\n".join(zh_lines) + "\n  "
content = content[:insert_point] + insert_text + content[zh_close:]
print(f"  Added {len(zh_missing)} missing ZH keys")

# ═══════════════════════════════════════════════════════
# FIX 2: Fix UR solution.pipe.dashboard double-backslash
# The file has \\u0688 (double backslash) -> should be \u0688 (single)
# ═══════════════════════════════════════════════════════

# Find the UR solution.pipe.dashboard value
idx = content.find("'solution.pipe.dashboard'", content.find('dicts.ur ='))
if idx >= 0:
    end = content.find("',\n", idx)
    old_val = content[idx:end+2]
    print(f"\n  UR solution.pipe.dashboard before: {repr(old_val[:80])}")
    # Fix the double backslash
    new_val = old_val.replace("\\\\u0688", "\\u0688")
    content = content.replace(old_val, new_val, 1)
    new_end = content.find("',\n", idx)
    print(f"  UR solution.pipe.dashboard after:  {repr(content[idx:new_end][:80])}")

# ═══════════════════════════════════════════════════════
# FIX 3: Verify no double commas remain
# ═══════════════════════════════════════════════════════
dc = content.count(',,')
print(f"\nDouble commas remaining: {dc}")

# ═══════════════════════════════════════════════════════
# FIX 4: Check for any English text in UR sec.* values
# ═══════════════════════════════════════════════════════
# Already fixed in previous script run

# ═══════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone. File saved.")

# ═══════════════════════════════════════════════════════
# VERIFY: Count keys in each dict
# ═══════════════════════════════════════════════════════
ur_start = content.find('dicts.ur = {')
zh_start = content.find('dicts.zh = {')

for name, start in [('EN', 0), ('ZH', zh_start), ('UR', ur_start)]:
    depth = 0
    i = content.find('{', start)
    dict_end = 0
    while i < len(content):
        if content[i] == '{': depth += 1
        elif content[i] == '}': 
            depth -= 1
            if depth == 0:
                dict_end = i
                break
        i += 1
    section = content[start:dict_end+1]
    key_count = len(re.findall(r"'[\w.]+'\s*:", section))
    print(f"  {name} dict: {key_count} keys")
