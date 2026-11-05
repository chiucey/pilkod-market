#!/usr/bin/env python3
"""
B2B市场营销技能打包脚本
将技能打包为 .skill 文件用于分发
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


class SkillPackager:
    def __init__(self, skill_path: str, output_dir: str = None):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir) if output_dir else Path('./dist')
        self.skill_name = self.skill_path.name
        self.manifest = {
            "name": self.skill_name,
            "created_at": datetime.now().isoformat(),
            "files": []
        }

    def package(self) -> Path:
        """执行打包流程"""
        print(f"📦 开始打包技能: {self.skill_name}")
        print("=" * 50)

        # 1. 验证技能结构
        if not self.validate():
            raise ValueError("技能验证失败，无法打包")

        # 2. 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 3. 生成包文件
        output_file = self.output_dir / f"{self.skill_name}.skill"

        # 4. 创建zip包
        self.create_archive(output_file)

        # 5. 生成校验和
        self.generate_checksum(output_file)

        print(f"\n✅ 打包完成: {output_file}")
        return output_file

    def validate(self) -> bool:
        """验证技能结构"""
        print("\n🔍 验证技能结构...")

        required_files = ['SKILL.md', '_meta.json']
        missing = []

        for file in required_files:
            file_path = self.skill_path / file
            if not file_path.exists():
                missing.append(file)

        if missing:
            print(f"  ❌ 缺少必需文件: {', '.join(missing)}")
            return False

        print("  ✅ 必需文件完整")

        # 验证_meta.json
        try:
            meta = json.loads((self.skill_path / '_meta.json').read_text(encoding='utf-8'))
            if 'id' not in meta or 'version' not in meta:
                print("  ❌ _meta.json 缺少 id 或 version")
                return False
            print(f"  ✅ id: {meta['id']}, version: {meta['version']}")
        except Exception as e:
            print(f"  ❌ _meta.json 解析失败: {e}")
            return False

        return True

    def create_archive(self, output_file: Path):
        """创建zip归档"""
        print(f"\n📁 创建归档: {output_file.name}")

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            total_size = 0

            for root, dirs, files in os.walk(self.skill_path):
                # 排除隐藏文件和目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.skill_path)

                    # 检查文件安全性
                    if self.is_safe_file(file_path):
                        zf.write(file_path, arcname)
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        file_count += 1
                        print(f"  ✅ {arcname} ({self.format_size(file_size)})")
                    else:
                        print(f"  ⏭️ 跳过: {arcname} (安全检查)")

                    # 记录到manifest
                    self.manifest["files"].append({
                        "path": str(arcname),
                        "size": file_path.stat().st_size if file_path.exists() else 0
                    })

        self.manifest["file_count"] = file_count
        self.manifest["total_size"] = total_size
        print(f"\n  📊 共 {file_count} 个文件, {self.format_size(total_size)}")

    def is_safe_file(self, file_path: Path) -> bool:
        """检查文件安全性"""
        # 允许的文件类型
        allowed_extensions = {'.md', '.json', '.txt', '.py', '.sh', '.yaml', '.yml'}

        # 检查扩展名
        if file_path.suffix.lower() not in allowed_extensions:
            # 允许无扩展名的配置文件
            if file_path.name not in ['SKILL', '_meta', 'package']:
                return False

        # 检查敏感文件
        sensitive_names = ['.env', '.pem', '.key', 'credentials', 'secrets', 'password']
        if any(s in file_path.name.lower() for s in sensitive_names):
            return False

        # 检查符号链接
        if file_path.is_symlink():
            target = file_path.resolve()
            if not str(target).startswith(str(self.skill_path)):
                return False

        return True

    def generate_checksum(self, output_file: Path):
        """生成校验和"""
        print("\n🔐 生成校验和...")

        sha256_hash = hashlib.sha256()
        with open(output_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        checksum = sha256_hash.hexdigest()
        checksum_file = output_file.with_suffix('.skill.sha256')
        checksum_file.write_text(checksum, encoding='utf-8')

        self.manifest["checksum"] = checksum
        print(f"  ✅ SHA256: {checksum}")

        # 保存manifest
        manifest_file = output_file.with_suffix('.skill.json')
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Manifest: {manifest_file}")

    @staticmethod
    def format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def main():
    if len(sys.argv) < 2:
        # 默认打包当前目录下的技能
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        packager = SkillPackager(skill_path, output_dir)
        output_file = packager.package()
        print(f"\n🎉 技能打包成功!")
        print(f"   路径: {output_file}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
