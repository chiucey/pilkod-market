#!/usr/bin/env python3
"""
auto-driving-test-qa 技能打包脚本
将技能打包为可分发的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# ANSI 颜色码
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"{BOLD}ℹ {msg}{RESET}")


class SkillPacker:
    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir).absolute()
        self.output_dir = self.skill_dir / 'dist'

    def validate_before_pack(self) -> bool:
        """打包前验证"""
        required_files = ['SKILL.md', '_meta.json']
        for f in required_files:
            if not (self.skill_dir / f).exists():
                print_error(f"缺少必需文件: {f}")
                return False

        # 验证_meta.json
        try:
            with open(self.skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if 'id' not in meta or 'version' not in meta:
                    print_error("_meta.json缺少id或version字段")
                    return False
        except Exception as e:
            print_error(f"_meta.json验证失败: {e}")
            return False

        return True

    def pack(self) -> Path:
        """打包技能"""
        # 读取元数据
        with open(self.skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)

        skill_id = meta['id']
        version = meta['version']
        skill_name = self.skill_dir.name

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = self.output_dir / f"{skill_name}_v{version}_{timestamp}.skill"

        # 创建zip包
        print_info(f"正在打包技能: {skill_name}")

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加清单文件
            manifest = {
                'skill_id': skill_id,
                'skill_name': skill_name,
                'version': version,
                'packaged_at': datetime.now().isoformat(),
                'files': []
            }

            for file_path in self.skill_dir.rglob('*'):
                if file_path.is_file():
                    # 跳过输出目录
                    if 'dist' in file_path.parts:
                        continue

                    arcname = file_path.relative_to(self.skill_dir)
                    zf.write(file_path, arcname)
                    manifest['files'].append(str(arcname))
                    print_info(f"  添加: {arcname}")

            # 添加清单到zip
            manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
            zf.writestr('manifest.json', manifest_json)

        print_success(f"打包完成: {output_file}")

        # 打印包内容摘要
        print("\n" + BOLD + "包内容摘要:" + RESET)
        print(f"  技能ID: {skill_id}")
        print(f"  技能名称: {skill_name}")
        print(f"  版本: {version}")
        print(f"  文件数量: {len(manifest['files'])}")
        print(f"  包大小: {output_file.stat().st_size / 1024:.1f} KB")

        return output_file

    def clean_dist(self):
        """清理dist目录"""
        if self.output_dir.exists():
            for f in self.output_dir.glob('*.skill'):
                f.unlink()
            print_info("已清理旧的打包文件")


def main():
    if len(sys.argv) < 2:
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    if not skill_dir.exists():
        print_error(f"技能目录不存在: {skill_dir}")
        sys.exit(1)

    packer = SkillPacker(skill_dir)

    print_info("开始打包技能...")
    print("=" * 50)

    if not packer.validate_before_pack():
        print_error("打包前验证失败")
        sys.exit(1)

    output_path = packer.pack()
    print_success("打包成功!")
    print(f"\n输出文件: {output_path}")
    print(f"完整路径: {output_path.absolute()}")


if __name__ == '__main__':
    main()