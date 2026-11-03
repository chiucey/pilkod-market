#!/usr/bin/env python3
"""
验证脚本测试套件
"""

import sys
import os
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from quick_validate import SkillValidator


def test_valid_skill():
    """测试有效的技能验证"""
    skill_path = Path(__file__).parent.parent
    validator = SkillValidator(skill_path)

    errors = validator.validate_all()

    # 有效技能应该通过验证
    assert len(validator.errors) == 0, f"存在错误: {validator.errors}"
    print("✅ 测试通过: 有效技能验证")


def test_missing_files():
    """测试缺少文件的情况"""
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建空的技能目录
        skill_path = Path(tmpdir) / "test-skill"
        skill_path.mkdir()

        validator = SkillValidator(skill_path)
        validator.validate_all()

        # 应该报告缺少文件
        assert len(validator.errors) > 0, "应该报告缺少文件错误"
        print("✅ 测试通过: 缺少文件检测")


def test_naming_convention():
    """测试命名规范"""
    # 测试有效命名
    valid_names = ["my-skill", "b2b-marketing-ops", "test123"]

    for name in valid_names:
        import re
        pattern = r'^[a-z0-9-]+$'
        assert re.match(pattern, name), f"应该通过: {name}"

    # 测试无效命名
    invalid_names = ["MySkill", "my_skill", "测试"]

    for name in invalid_names:
        import re
        pattern = r'^[a-z0-9-]+$'
        assert not re.match(pattern, name), f"应该失败: {name}"

    print("✅ 测试通过: 命名规范")


if __name__ == '__main__':
    print("🧪 运行验证脚本测试...")
    print("=" * 50)

    test_valid_skill()
    test_missing_files()
    test_naming_convention()

    print("\n" + "=" * 50)
    print("✅ 所有测试通过!")
