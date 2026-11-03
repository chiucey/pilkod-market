#!/usr/bin/env python3
"""
金融租赁同业项目搜集技能 - 快速验证脚本
验证 SKILL.md 和 _meta.json 的格式与内容完整性
"""
import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
META_JSON = SKILL_DIR / "_meta.json"


def validate_frontmatter(skill_md_path: Path) -> tuple[bool, list[str]]:
    """验证 frontmatter 格式和内容"""
    errors = []
    content = skill_md_path.read_text(encoding="utf-8")

    # 检查文件是否以 --- 开头
    if not content.strip().startswith("---"):
        errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头，第一行不能是 markdown 标题")
        return False, errors

    # 提取 frontmatter
    lines = content.split("\n")
    if len(lines) < 3 or lines[0].strip() != "---":
        errors.append("frontmatter 格式错误：缺少起始 ---")
        return False, errors

    # 找到结束 ---
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("frontmatter 缺少结束 ---")
        return False, errors

    # 解析 frontmatter YAML（去掉起始 --- 和结束 ---）
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = "\n".join(frontmatter_lines)  # lines[1:end_idx] 不含首尾 ---

    required_keys = ["name", "description"]
    for key in required_keys:
        if not re.search(rf"^{key}\s*:", frontmatter_text, re.MULTILINE):
            errors.append(f"frontmatter 缺少必填字段: {key}")

    # 验证 name 格式（连字符，小写英文）
    name_match = re.search(r"^name\s*:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", name_value):
            errors.append(f"name 格式错误: '{name_value}' - 应使用小写英文和连字符")
        # 检查 name 是否包含非英文字符
        if re.search(r"[^\x00-\x7F]", name_value):
            errors.append(f"name 包含非英文字符: '{name_value}'")

    # 验证 description 长度
    desc_match = re.search(r"^description\s*:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append(f"description 过短 (< 20字符)，触发短语不够清晰")
        if re.search(r"[^\x00-\x7F]", desc_value):
            # description 可以包含中文，这是允许的
            pass

    return len(errors) == 0, errors


def validate_meta_json(meta_path: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []

    if not meta_path.exists():
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 解析失败: {e}")
        return False, errors

    required_keys = ["id", "version"]
    for key in required_keys:
        if key not in meta:
            errors.append(f"_meta.json 缺少必填字段: {key}")

    if "id" in meta:
        if not isinstance(meta["id"], int) or meta["id"] <= 0:
            errors.append(f"_meta.json 中 id 应为正整数，当前值: {meta['id']}")

    if "version" in meta:
        if not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
            errors.append(f"_meta.json 中 version 格式应符合语义化版本 (如 1.0.0)，当前值: {meta['version']}")

    return len(errors) == 0, errors


def validate_directory_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查必要的目录和文件
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_dir / f).exists():
            errors.append(f"缺少必要文件: {f}")

    # 检查可选目录
    optional_dirs = ["references", "scripts", "assets"]
    for d in optional_dirs:
        dir_path = skill_dir / d
        if dir_path.exists() and not any(dir_path.iterdir()):
            errors.append(f"目录 {d}/ 存在但为空，建议删除或填充内容")

    return len(errors) == 0, errors


def main():
    print("=" * 50)
    print("金融租赁同业项目搜集技能 - 质量验证")
    print("=" * 50)

    all_passed = True

    # 1. 验证 frontmatter
    print("\n[1/3] 验证 SKILL.md Frontmatter...")
    passed, errors = validate_frontmatter(SKILL_MD)
    if passed:
        print("  ✅ Frontmatter 验证通过")
    else:
        print("  ❌ Frontmatter 验证失败:")
        for e in errors:
            print(f"     - {e}")
        all_passed = False

    # 2. 验证 _meta.json
    print("\n[2/3] 验证 _meta.json...")
    passed, errors = validate_meta_json(META_JSON)
    if passed:
        print("  ✅ _meta.json 验证通过")
    else:
        print("  ❌ _meta.json 验证失败:")
        for e in errors:
            print(f"     - {e}")
        all_passed = False

    # 3. 验证目录结构
    print("\n[3/3] 验证目录结构...")
    passed, errors = validate_directory_structure(SKILL_DIR)
    if passed:
        print("  ✅ 目录结构验证通过")
    else:
        print("  ⚠️  目录结构存在以下问题:")
        for e in errors:
            print(f"     - {e}")
        # 目录结构问题不影响整体通过

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有必填验证通过！技能可进入打包阶段。")
        return 0
    else:
        print("❌ 存在验证失败项，请修复后重试。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
