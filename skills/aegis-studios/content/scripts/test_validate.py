#!/usr/bin/env python3
"""
Aegis Studios 验证脚本测试
"""

import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.quick_validate import (
    validate_frontmatter,
    validate_meta,
    validate_structure
)


def test_frontmatter_validation():
    """测试 frontmatter 验证"""
    skill_path = Path(__file__).parent.parent
    valid, errors = validate_frontmatter(skill_path)

    assert valid, f"Frontmatter 验证失败: {errors}"
    print("✓ Frontmatter 验证测试通过")


def test_meta_validation():
    """测试 _meta.json 验证"""
    skill_path = Path(__file__).parent.parent
    valid, errors = validate_meta(skill_path)

    assert valid, f"_meta.json 验证失败: {errors}"
    print("✓ _meta.json 验证测试通过")

    # 额外检查 id 和 version
    meta_file = skill_path / "_meta.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8"))

    assert "id" in meta, "缺少 id 字段"
    assert "version" in meta, "缺少 version 字段"
    assert meta["id"] == "8978497", f"ID 不匹配: {meta['id']}"
    assert meta["version"] == "1.0.0", f"Version 不匹配: {meta['version']}"


def test_structure_validation():
    """测试目录结构验证"""
    skill_path = Path(__file__).parent.parent
    valid, errors = validate_structure(skill_path)

    assert valid, f"结构验证失败: {errors}"
    print("✓ 目录结构验证测试通过")


def test_required_files():
    """测试必需文件存在"""
    skill_path = Path(__file__).parent.parent

    required = ["SKILL.md", "_meta.json"]
    for filename in required:
        file_path = skill_path / filename
        assert file_path.exists(), f"缺少必需文件: {filename}"

    print("✓ 必需文件检查通过")


def test_skill_content():
    """测试技能内容完整性"""
    skill_path = Path(__file__).parent.parent
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # 检查是否包含15位大师
    masters = [
        "Chief Imagination Architect",
        "AI VFX Director",
        "Chief AI Scientist",
        "Visual Universe Architect",
        "Asset Library Curator",
        "Multimodal Narrative Director",
        "AI Hyperrealistic Character Artist",
        "AI-VFX Compositing Director",
        "Immersive Audio Architect",
        "Master Composer",
        "Master Voice Director",
        "Real-time VP Engineer",
        "AI Workflow TD",
        "AI Compliance Officer",
        "Chief AI Producer"
    ]

    missing = []
    for master in masters:
        if master not in content:
            missing.append(master)

    assert len(missing) == 0, f"缺少大师: {missing}"
    print("✓ 15位大师内容完整性检查通过")


def main():
    print("=" * 50)
    print("Aegis Studios 测试套件")
    print("=" * 50)

    tests = [
        test_required_files,
        test_frontmatter_validation,
        test_meta_validation,
        test_structure_validation,
        test_skill_content,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 异常: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
