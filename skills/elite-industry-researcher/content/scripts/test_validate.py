#!/usr/bin/env python3
"""
测试脚本 - 回归测试
"""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from quick_validate import validate_frontmatter, validate_meta_json, validate_structure


def test_valid_skill():
    """测试有效技能结构"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_path = Path(tmpdir)

        # 创建有效结构
        (skill_path / "SKILL.md").write_text("""---
name: test-skill
description: Test skill description
---

# Test Skill
Content here.
""", encoding='utf-8')

        (skill_path / "_meta.json").write_text("""{
  "id": "123456",
  "version": "1.0.0"
}
""", encoding='utf-8')

        # 验证
        assert validate_structure(skill_path)[0], "Structure validation failed"
        assert validate_frontmatter(skill_path)[0], "Frontmatter validation failed"
        assert validate_meta_json(skill_path)[0], "Meta validation failed"

        print("✓ test_valid_skill passed")


def test_invalid_frontmatter():
    """测试无效frontmatter"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_path = Path(tmpdir)

        # 无效：没有frontmatter
        (skill_path / "SKILL.md").write_text("# Test\nContent", encoding='utf-8')
        (skill_path / "_meta.json").write_text('{"id": "1", "version": "1.0.0"}', encoding='utf-8')

        assert not validate_frontmatter(skill_path)[0], "Should fail without frontmatter"
        print("✓ test_invalid_frontmatter passed")


def test_missing_name():
    """测试缺少name字段"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_path = Path(tmpdir)

        (skill_path / "SKILL.md").write_text("""---
description: Test
---

Content
""", encoding='utf-8')
        (skill_path / "_meta.json").write_text('{"id": "1", "version": "1.0.0"}', encoding='utf-8')

        assert not validate_frontmatter(skill_path)[0], "Should fail without name"
        print("✓ test_missing_name passed")


def test_name_too_long():
    """测试name过长"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_path = Path(tmpdir)

        long_name = "a" * 65  # 超过64字符
        (skill_path / "SKILL.md").write_text(f"""---
name: {long_name}
description: Test
---

Content
""", encoding='utf-8')
        (skill_path / "_meta.json").write_text('{"id": "1", "version": "1.0.0"}', encoding='utf-8')

        assert not validate_frontmatter(skill_path)[0], "Should fail with name > 64 chars"
        print("✓ test_name_too_long passed")


if __name__ == "__main__":
    test_valid_skill()
    test_invalid_frontmatter()
    test_missing_name()
    test_name_too_long()
    print("\n✓ All tests passed!")
