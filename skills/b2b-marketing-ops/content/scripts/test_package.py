#!/usr/bin/env python3
"""
打包脚本测试套件
"""

import sys
import os
import zipfile
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from package_skill import SkillPackager


def test_package_creation():
    """测试打包创建"""
    skill_path = Path(__file__).parent.parent
    output_dir = Path(__file__).parent.parent / 'dist'

    packager = SkillPackager(skill_path, output_dir)
    output_file = packager.package()

    # 检查输出文件存在
    assert output_file.exists(), "输出文件应该存在"

    # 检查是有效的zip文件
    with zipfile.ZipFile(output_file, 'r') as zf:
        names = zf.namelist()
        assert 'SKILL.md' in names, "应该包含 SKILL.md"
        assert '_meta.json' in names, "应该包含 _meta.json"

    print("✅ 测试通过: 打包创建")


def test_checksum_generation():
    """测试校验和生成"""
    skill_path = Path(__file__).parent.parent
    output_dir = Path(__file__).parent.parent / 'dist'

    packager = SkillPackager(skill_path, output_dir)
    output_file = packager.package()

    # 检查校验和文件
    checksum_file = output_file.with_suffix('.skill.sha256')
    assert checksum_file.exists(), "校验和文件应该存在"

    # 检查校验和格式
    checksum = checksum_file.read_text().strip()
    assert len(checksum) == 64, "SHA256校验和应该是64字符"

    print("✅ 测试通过: 校验和生成")


def test_security_checks():
    """测试安全检查"""
    packager = SkillPackager('.')

    # 测试允许的文件
    assert packager.is_safe_file(Path('test.md')) == True
    assert packager.is_safe_file(Path('SKILL.md')) == True
    assert packager.is_safe_file(Path('_meta.json')) == True

    # 测试拒绝的文件
    assert packager.is_safe_file(Path('.env')) == False
    assert packager.is_safe_file(Path('credentials.json')) == False
    assert packager.is_safe_file(Path('passwords.txt')) == False

    print("✅ 测试通过: 安全检查")


if __name__ == '__main__':
    print("🧪 运行打包脚本测试...")
    print("=" * 50)

    test_package_creation()
    test_checksum_generation()
    test_security_checks()

    print("\n" + "=" * 50)
    print("✅ 所有测试通过!")
