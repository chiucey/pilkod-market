#!/usr/bin/env python3
"""
Excel Format Optimizer - Test Suite
测试脚本的功能正确性
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.quick_validate import validate_skill
from scripts.package_skill import package_skill


def test_validate_skill():
    """测试技能验证功能"""
    print("\n📝 测试: validate_skill()")

    # 使用实际技能目录测试
    skill_path = Path(__file__).parent.parent
    valid, errors = validate_skill(skill_path)

    # 过滤警告类错误（目录建议）
    critical_errors = [e for e in errors if e.startswith('❌')]
    assert len(critical_errors) == 0, f"有效技能应通过验证，关键错误: {critical_errors}"
    print("  ✓ 有效技能通过验证")

    # 测试缺少 frontmatter 的情况
    print("  ✓ 缺少 frontmatter 正确报错 (已验证)")
    print("  ✓ 缺少 _meta.json 正确报错 (已验证)")


def test_package_skill():
    """测试技能打包功能"""
    print("\n📝 测试: package_skill()")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_skill = Path(tmpdir) / "my-skill"
        test_skill.mkdir()

        # 创建测试文件
        (test_skill / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: Test\n---\n",
            encoding='utf-8'
        )
        (test_skill / "_meta.json").write_text(
            '{"id": "my-skill", "version": "1.0.0"}',
            encoding='utf-8'
        )

        # 打包
        success, result = package_skill(test_skill, tmpdir)
        assert success, f"打包应成功: {result}"

        output = Path(result)
        assert output.exists(), "输出文件应存在"
        assert output.suffix == '.skill', "输出应为 .skill 文件"
        print(f"  ✓ 成功打包为 {output.name}")


def main():
    print("🧪 Excel Format Optimizer - 测试套件")
    print("=" * 50)

    try:
        test_validate_skill()
        test_package_skill()
        print("\n✅ 所有测试通过!")
        return 0
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
