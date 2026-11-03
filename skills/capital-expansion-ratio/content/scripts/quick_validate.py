"""
技能结构验证脚本 - capital-expansion-ratio

检查项：
1. SKILL.md 存在且包含有效 frontmatter（name + description）
2. Frontmatter 在文件第一行
3. _meta.json 存在且包含 id + version
4. scripts/fetch_and_calc.py 存在
5. name 与文件夹名称匹配
6. 无中文或特殊字符路径

用法: python scripts/quick_validate.py
"""

import os
import sys
import json
import re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_NAME_EXPECTED = "capital-expansion-ratio"

errors = []
warnings_list = []


def check(condition, msg, is_warning=False):
    if not condition:
        if is_warning:
            warnings_list.append(f"[WARN] {msg}")
        else:
            errors.append(f"[ERROR] {msg}")
    return condition


# ── 1. 检查 SKILL.md ──
skill_md_path = os.path.join(SKILL_DIR, "SKILL.md")
check(os.path.isfile(skill_md_path), f"SKILL.md 不存在：{skill_md_path}")

if os.path.isfile(skill_md_path):
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查 frontmatter 在第一行
    check(
        content.startswith("---"),
        "SKILL.md frontmatter 必须以 '---' 开头（第一行）"
    )

    # 解析 frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if check(fm_match is not None, "SKILL.md 缺少有效的 YAML frontmatter 块"):
        fm_text = fm_match.group(1)

        # 检查 name 字段
        name_match = re.search(r"^name:\s*(.+)$", fm_text, re.MULTILINE)
        if check(name_match is not None, "frontmatter 缺少 'name' 字段"):
            skill_name = name_match.group(1).strip()
            check(
                skill_name == SKILL_NAME_EXPECTED,
                f"frontmatter name '{skill_name}' 与文件夹名称 '{SKILL_NAME_EXPECTED}' 不匹配"
            )
            check(
                bool(re.match(r"^[a-z][a-z0-9\-]{0,63}$", skill_name)),
                f"name '{skill_name}' 不符合连字符格式（hyphen-case）"
            )

        # 检查 description 字段
        desc_match = re.search(r"^description:\s*(.+)$", fm_text, re.MULTILINE)
        check(desc_match is not None, "frontmatter 缺少 'description' 字段")
        if desc_match:
            desc = desc_match.group(1).strip()
            check(len(desc) > 20, "description 过短，应包含触发短语（>20字符）", is_warning=True)

    # 检查是否有 # 标题在 frontmatter 之前
    check(
        not content.lstrip().startswith("#"),
        "SKILL.md 不能以 Markdown 标题 '#' 开头（frontmatter 必须在最前面）"
    )

# ── 2. 检查 _meta.json ──
meta_path = os.path.join(SKILL_DIR, "_meta.json")
check(os.path.isfile(meta_path), "_meta.json 不存在")

if os.path.isfile(meta_path):
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        check("id" in meta, "_meta.json 缺少 'id' 字段")
        check("version" in meta, "_meta.json 缺少 'version' 字段")
        if "id" in meta:
            check(str(meta["id"]).strip() != "", "_meta.json 的 id 不能为空")
        if "version" in meta:
            check(
                bool(re.match(r"^\d+\.\d+\.\d+$", str(meta["version"]))),
                f"version '{meta['version']}' 不符合语义化版本格式 (x.y.z)"
            )
    except json.JSONDecodeError as e:
        errors.append(f"[ERROR] _meta.json JSON 解析失败：{e}")

# ── 3. 检查必要脚本 ──
required_scripts = ["scripts/fetch_and_calc.py"]
for script in required_scripts:
    script_path = os.path.join(SKILL_DIR, script)
    check(os.path.isfile(script_path), f"必要脚本不存在：{script}")

# ── 4. 检查路径名称仅为英文 ──
for root, dirs, files in os.walk(SKILL_DIR):
    for name in dirs + files:
        full_path = os.path.join(root, name)
        rel_path = os.path.relpath(full_path, SKILL_DIR)
        # 检查是否包含中文或非ASCII字符（排除文件内容）
        if not all(ord(c) < 128 for c in rel_path):
            errors.append(f"[ERROR] 路径包含非英文字符：{rel_path}")

# ── 5. 检查文件夹名称 ──
folder_name = os.path.basename(SKILL_DIR)
check(
    folder_name == SKILL_NAME_EXPECTED,
    f"技能文件夹名称 '{folder_name}' 应为 '{SKILL_NAME_EXPECTED}'"
)

# ── 输出结果 ──
print("=" * 60)
print(f"技能验证报告：{SKILL_NAME_EXPECTED}")
print("=" * 60)

if warnings_list:
    print("\n⚠️  警告：")
    for w in warnings_list:
        print(f"  {w}")

if errors:
    print("\n❌ 验证失败：")
    for e in errors:
        print(f"  {e}")
    print(f"\n共发现 {len(errors)} 个错误，请修复后重新验证。")
    sys.exit(1)
else:
    print("\n✅ 验证通过！所有检查项均符合规范。")
    if warnings_list:
        print(f"（{len(warnings_list)} 个警告，建议关注）")
    sys.exit(0)
