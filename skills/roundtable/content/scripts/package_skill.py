#!/usr/bin/env python3
"""
Roundtable Skill 打包脚本
将技能打包为 .skill 文件用于发布
"""

import os
import sys
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ANSI 颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str, output_dir: Optional[str] = None):
        self.skill_path = Path(skill_path)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.warnings: List[str] = []
        self.info: List[str] = []

    def log_info(self, msg: str):
        self.info.append(msg)
        print(f"{CYAN}ℹ{RESET} {msg}")

    def log_warning(self, msg: str):
        self.warnings.append(msg)
        print(f"{YELLOW}⚠{RESET} {msg}")

    def log_error(self, msg: str):
        print(f"{RED}✗{RESET} {msg}")

    def log_success(self, msg: str):
        print(f"{GREEN}✓{RESET} {msg}")

    def validate_for_packaging(self) -> bool:
        """打包前验证"""
        print(f"\n{BOLD}打包前验证...{RESET}")

        # 检查技能目录
        if not self.skill_path.exists():
            self.log_error(f"技能目录不存在: {self.skill_path}")
            return False

        # 检查必需文件
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.log_error("缺少 SKILL.md 文件")
            return False

        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            self.log_error("缺少 _meta.json 文件")
            return False

        # 验证 SKILL.md frontmatter
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            self.log_error("SKILL.md 必须以 frontmatter (---) 开头")
            return False

        # 验证 _meta.json
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta or 'version' not in meta:
                self.log_error("_meta.json 必须包含 id 和 version 字段")
                return False
        except json.JSONDecodeError as e:
            self.log_error(f"_meta.json 格式错误: {e}")
            return False

        # 检查安全问题
        self.check_security()

        self.log_success("打包前验证通过")
        return True

    def check_security(self):
        """安全检查"""
        print(f"\n{BOLD}安全检查...{RESET}")

        # 检查敏感文件
        sensitive_patterns = ['.env', '.pem', '.key', 'id_rsa', 'credentials']
        for pattern in sensitive_patterns:
            for file in self.skill_path.rglob(f'*{pattern}*'):
                self.log_warning(f"发现敏感文件: {file.relative_to(self.skill_path)}")

        # 检查符号链接
        for file in self.skill_path.rglob('*'):
            if file.is_symlink():
                self.log_warning(f"发现符号链接: {file.relative_to(self.skill_path)}")

        # 检查隐藏文件（排除 .gitkeep）
        for file in self.skill_path.rglob('.*'):
            if file.name not in ['.gitkeep', '.DS_Store'] and not file.is_dir():
                if '.git' not in str(file):
                    self.log_warning(f"发现隐藏文件: {file.relative_to(self.skill_path)}")

        self.log_info("安全检查完成")

    def get_skill_metadata(self) -> Dict:
        """获取技能元数据"""
        meta_json = self.skill_path / "_meta.json"
        meta = json.loads(meta_json.read_text(encoding='utf-8'))

        # 从 SKILL.md 提取信息
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')

        # 提取 description
        import re
        match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
        if match:
            meta['description'] = match.group(1).strip()

        return meta

    def create_package(self) -> Optional[Path]:
        """创建打包文件"""
        if not self.validate_for_packaging():
            return None

        print(f"\n{BOLD}创建 .skill 包...{RESET}")

        # 获取元数据
        metadata = self.get_skill_metadata()
        skill_name = self.skill_path.name
        version = metadata.get('version', '1.0.0')

        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = self.output_dir / f"{skill_name}-{version}.{timestamp}.skill"

        # 创建临时目录用于打包
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 复制文件到临时目录（保持结构）
            import shutil

            # 复制技能文件
            skill_files = []
            for item in self.skill_path.rglob('*'):
                if item.is_file() and not item.is_symlink():
                    # 计算相对路径
                    rel_path = item.relative_to(self.skill_path)

                    # 跳过敏感文件和开发文件
                    skip = False
                    for pattern in ['.env', '.pem', '.key', '__pycache__', '.git', '.DS_Store']:
                        if pattern in str(rel_path):
                            skip = True
                            break

                    if skip:
                        continue

                    dest = temp_path / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
                    skill_files.append(rel_path)

            # 创建包清单
            manifest = {
                'name': skill_name,
                'version': version,
                'packaged_at': datetime.now().isoformat(),
                'files': [str(f) for f in skill_files],
                'file_count': len(skill_files)
            }

            manifest_file = temp_path / '_manifest.json'
            manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

            # 创建 ZIP 文件
            self.log_info(f"打包 {len(skill_files)} 个文件...")
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in temp_path.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(temp_path)
                        zipf.write(file, arcname)

        self.log_success(f"打包完成: {output_file.name}")
        print(f"\n{BOLD}打包摘要{RESET}")
        print(f"{'='*50}")
        print(f"技能名称: {skill_name}")
        print(f"版本: {version}")
        print(f"文件数: {len(skill_files)}")
        print(f"输出路径: {output_file}")
        print(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")

        return output_file

    def verify_package(self, package_path: Path) -> bool:
        """验证打包文件"""
        print(f"\n{BOLD}验证打包文件...{RESET}")

        if not package_path.exists():
            self.log_error("打包文件不存在")
            return False

        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # 检查 ZIP 完整性
                bad_file = zipf.testzip()
                if bad_file:
                    self.log_error(f"ZIP 文件损坏: {bad_file}")
                    return False

                # 检查必需文件
                files = zipf.namelist()
                required = ['SKILL.md', '_meta.json', '_manifest.json']
                for req in required:
                    if req not in files:
                        self.log_error(f"缺少必需文件: {req}")
                        return False

                # 验证 manifest
                manifest_content = zipf.read('_manifest.json')
                manifest = json.loads(manifest_content)

                self.log_success("打包文件验证通过")
                self.log_info(f"包含 {manifest.get('file_count', 0)} 个文件")

                return True

        except zipfile.BadZipFile:
            self.log_error("无效的 ZIP 文件")
            return False
        except Exception as e:
            self.log_error(f"验证失败: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print(f"用法: python package_skill.py <skill_path> [output_dir]")
        print(f"示例: python package_skill.py /workspace/temp-skills/roundtable /workspace/output")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    packager = SkillPackager(skill_path, output_dir)
    package_path = packager.create_package()

    if package_path and packager.verify_package(package_path):
        print(f"\n{GREEN}打包成功！{RESET}")
        print(f"输出文件: {package_path}")
        sys.exit(0)
    else:
        print(f"\n{RED}打包失败！{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
