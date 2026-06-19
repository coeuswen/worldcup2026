"""
自动更新 index.html 中的 ANALYSIS 数组
在生成报告后运行：python scripts/update_index.py YYYY-MM-DD
"""
import sys
import re
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

if len(sys.argv) < 2:
    print("用法: python update_index.py YYYY-MM-DD")
    sys.exit(0)

target_date = sys.argv[1]
REPO_ROOT = Path(__file__).parent.parent

# 检查报告文件是否存在
report_file = REPO_ROOT / "分析" / f"2026-{target_date}-分析报告.html"
if not report_file.exists():
    print(f"  报告文件不存在，跳过 index.html 更新: {report_file}")
    sys.exit(0)

# 读取index.html
index_path = REPO_ROOT / "index.html"
if not index_path.exists():
    print("  index.html 不存在，跳过")
    sys.exit(0)

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 格式化日期
d = datetime.strptime(target_date, "%Y-%m-%d")
date_cn = f"{d.month}/{d.day}"

# 检查是否已有该日期的条目
if f"2026-{target_date}-分析报告" in content:
    print(f"  index.html 已包含 {target_date} 的条目，跳过")
    sys.exit(0)

# 在ANALYSIS数组第一个元素前插入新条目
# 格式: { date: "6/21", matches: "...", href: "分析/2026-06-21-分析报告.html" },
new_entry = f'        {{ date: "{date_cn}", matches: "世界杯赛事", href: "分析/2026-{target_date}-分析报告.html" }},'

# 找到ANALYSIS数组的第一个元素并在前面插入
pattern = r'(const ANALYSIS\s*=\s*\[)'
replacement = r'\1\n' + new_entry

if re.search(pattern, content):
    new_content = re.sub(pattern, replacement, content, count=1)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  ✅ index.html 已更新，添加 {target_date} 条目")
else:
    print("  ⚠️ 未找到 ANALYSIS 数组，无法自动更新 index.html")

sys.exit(0)
