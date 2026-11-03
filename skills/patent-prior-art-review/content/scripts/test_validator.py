#!/usr/bin/env python3
"""
Patent Prior Art Review Skill - Regression Tests
验证器和打包器的冒烟测试
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加scripts目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from validate_skill import (
    validate_frontmatter,
    validate_meta_json,
    validate_directory_structure
)
from package_skill import (
    create_skill_package,
    validate_before_pack,
    collect_skill_files
)


def create_test_skill(temp_dir: str, with_errors: bool = False) -> str:
    """创建测试用技能目录"""
    skill_dir = os.path.join(temp_dir, "test-skill")
    os.makedirs(skill_dir, exist_ok=True)

    # 创建SKILL.md
    frontmatter = """---
name: test-skill
description: 用于测试的技能，用于验证frontmatter格式是否正确
---
# Test Skill
"""
    if with_errors:
        frontmatter = """# Test Skill (错误：没有frontmatter)
"""
    with open(os.path.join(skill_dir, "SKILL.md"), 'w') as f:
        f.write(frontmatter)

    # 创建_meta.json
    meta = {
        "id": 9999,
        "version": "1.0.0"
    }
    with open(os.path.join(skill_dir, "_meta.json"), 'w') as f:
        json.dump(meta, f)

    return skill_dir


def test_validate_frontmatter():
    """测试frontmatter验证"""
    print("测试 validate_frontmatter...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试正常情况
        skill_dir = create_test_skill(temp_dir, with_errors=False)
        passed, errors = validate_frontmatter(skill_dir)
        assert passed, f"正常情况应通过: {errors}"

        # 测试错误情况
        skill_dir = create_test_skill(temp_dir, with_errors=True)
        passed, errors = validate_frontmatter(skill_dir)
        assert not passed, "错误情况应失败"

    print("✓ validate_frontmatter 测试通过")


def test_validate_meta_json():
    """测试_meta.json验证"""
    print("测试 validate_meta_json...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 正常情况
        skill_dir = create_test_skill(temp_dir, with_errors=False)
        passed, errors = validate_meta_json(skill_dir)
        assert passed, f"正常情况应通过: {errors}"

        # 缺少文件
        empty_dir = os.path.join(temp_dir, "empty-skill")
        os.makedirs(empty_dir)
        passed, errors = validate_meta_json(empty_dir)
        assert not passed, "缺少_meta.json应失败"

    print("✓ validate_meta_json 测试通过")


def test_validate_directory_structure():
    """测试目录结构验证"""
    print("测试 validate_directory_structure...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 正常情况
        skill_dir = create_test_skill(temp_dir, with_errors=False)
        passed, errors = validate_directory_structure(skill_dir)
        assert passed, f"正常情况应通过: {errors}"

        # 缺少必需文件
        empty_dir = os.path.join(temp_dir, "incomplete-skill")
        os.makedirs(empty_dir)
        passed, errors = validate_directory_structure(empty_dir)
        assert not passed, "缺少文件应失败"

    print("✓ validate_directory_structure 测试通过")


def test_collect_skill_files():
    """测试文件收集"""
    print("测试 collect_skill_files...")

    with tempfile.TemporaryDirectory() as temp_dir:
        skill_dir = create_test_skill(temp_dir, with_errors=False)

        # 添加额外文件
        with open(os.path.join(skill_dir, "test.txt"), 'w') as f:
            f.write("test")

        files = collect_skill_files(skill_dir)
        assert len(files) >= 3, f"应至少收集3个文件: {files}"
        assert "test.txt" in files, "应包含test.txt"

    print("✓ collect_skill_files 测试通过")


def test_package_creation():
    """测试打包功能"""
    print("测试 create_skill_package...")

    with tempfile.TemporaryDirectory() as temp_dir:
        skill_dir = create_test_skill(temp_dir, with_errors=False)

        # 打包
        output_file = create_skill_package(skill_dir, temp_dir)
        assert os.path.exists(output_file), "输出文件应存在"
        assert output_file.endswith('.skill'), "输出应为.skill文件"

    print("✓ create_skill_package 测试通过")


def test_validate_before_pack():
    """测试打包前验证"""
    print("测试 validate_before_pack...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 正常情况
        skill_dir = create_test_skill(temp_dir, with_errors=False)
        passed, errors = validate_before_pack(skill_dir)
        assert passed, f"正常情况应通过: {errors}"

    print("✓ validate_before_pack 测试通过")


def main():
    print("=" * 50)
    print("Patent Prior Art Review Skill - 回归测试")
    print("=" * 50)
    print()

    tests = [
        test_validate_frontmatter,
        test_validate_meta_json,
        test_validate_directory_structure,
        test_collect_skill_files,
        test_package_creation,
        test_validate_before_pack
    ]

    passed_count = 0
    for test in tests:
        try:
            test()
            passed_count += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
        except Exception as e:
            print(f"✗ {test.__name__} 出错: {e}")

    print()
    print("=" * 50)
    print(f"测试完成: {passed_count}/{len(tests)} 通过")
    print("=" * 50)

    return 0 if passed_count == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())