"""
技能打包脚本
将技能打包为可发布的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Tuple

# 颜色定义
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"📦 {msg}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"  {msg}")


class SkillPackager:
    """技能打包器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.output_path = Path("/workspace/temp-skills/output")
        self.exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            ".DS_Store",
            "*.log",
            ".env",
            "node_modules",
            ".venv"
        ]

    def validate_before_packaging(self) -> bool:
        """打包前验证"""
        print_step("打包前验证")

        # 检查SKILL.md
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            print_error("SKILL.md不存在，无法打包")
            return False
        print_success("SKILL.md存在")

        # 检查_meta.json
        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            print_error("_meta.json不存在，无法打包")
            return False
        print_success("_meta.json存在")

        # 验证meta内容
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta or 'version' not in meta:
                print_error("_meta.json缺少必需字段(id, version)")
                return False
            print_success(f"meta信息: id={meta['id']}, version={meta['version']}")

        except Exception as e:
            print_error(f"读取_meta.json失败: {e}")
            return False

        return True

    def collect_files(self) -> list:
        """收集要打包的文件"""
        print_step("收集文件")

        files_to_pack = []

        for root, dirs, files in os.walk(self.skill_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]

            for file in files:
                if self._should_exclude(file):
                    continue

                src_path = Path(root) / file
                rel_path = src_path.relative_to(self.skill_path)
                files_to_pack.append((src_path, rel_path))

                # 显示文件
                size = src_path.stat().st_size
                size_str = self._format_size(size)
                print_info(f"{rel_path} ({size_str})")

        print_success(f"共收集 {len(files_to_pack)} 个文件")
        return files_to_pack

    def _should_exclude(self, name: str) -> bool:
        """检查是否应排除"""
        for pattern in self.exclude_patterns:
            if pattern in name or name.startswith('.'):
                return True
        return False

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}GB"

    def create_package(self, files: list) -> Path:
        """创建技能包"""
        print_step("创建技能包")

        # 读取meta信息
        meta_json = self.skill_path / "_meta.json"
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 生成包名
        skill_name = meta.get('name', 'unknown')
        version = meta.get('version', '1.0.0')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        package_name = f"{skill_name}_v{version}_{timestamp}.skill"

        # 确保输出目录存在
        self.output_path.mkdir(parents=True, exist_ok=True)
        package_path = self.output_path / package_name

        # 创建zip包
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for src_path, rel_path in files:
                # 计算相对路径，确保在skill目录下
                arcname = f"{skill_name}/{rel_path}"
                zf.write(src_path, arcname)

        # 获取包大小
        package_size = package_path.stat().st_size
        print_success(f"技能包已创建: {package_path.name}")
        print_info(f"路径: {package_path}")
        print_info(f"大小: {self._format_size(package_size)}")

        return package_path

    def create_unpacked_structure(self, files: list) -> Path:
        """创建未打包的目录结构"""
        print_step("创建技能目录结构")

        # 读取meta信息
        meta_json = self.skill_path / "_meta.json"
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        skill_name = meta.get('name', 'unknown')
        unpacked_path = self.output_path / skill_name

        # 清理已存在的目录
        if unpacked_path.exists():
            shutil.rmtree(unpacked_path)

        # 创建目录结构
        unpacked_path.mkdir(parents=True, exist_ok=True)

        for src_path, rel_path in files:
            dst_path = unpacked_path / rel_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)

        print_success(f"目录结构已创建: {unpacked_path}")
        return unpacked_path

    def generate_readme(self, unpacked_path: Path):
        """生成README"""
        readme_content = f"""# {self.skill_path.name}

A股市场实时分析预测系统

## 功能特性

- 实时行情分析
- 智能预测模型
- 专业报告生成
- 数据管理中心

## 文件结构

```
{self.skill_path.name}/
├── SKILL.md          # 技能定义
├── _meta.json        # 元数据
├── scripts/          # 自动化脚本
│   ├── data_manager.py
│   ├── model_trainer.py
│   └── quick_validate.py
└── references/       # 参考文档
    ├── data-sources.md
    ├── model-config.md
    └── report-templates.md
```

## 使用说明

1. 将技能添加到系统
2. 配置数据源
3. 初始化模型
4. 开始分析

## 版本

v1.0.0

---
Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        readme_path = unpacked_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print_success("README.md已生成")

    def package(self) -> Tuple[Path, Path]:
        """执行打包"""
        # 验证
        if not self.validate_before_packaging():
            raise Exception("打包前验证失败")

        # 收集文件
        files = self.collect_files()

        # 创建技能包
        package_path = self.create_package(files)

        # 创建目录结构
        unpacked_path = self.create_unpacked_structure(files)

        # 生成README
        self.generate_readme(unpacked_path)

        return package_path, unpacked_path

    def clean_output(self):
        """清理输出目录"""
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
            print_info("已清理输出目录")


def main():
    """主函数"""
    print(f"\n{'#'*60}")
    print(f"# 技能打包工具")
    print(f"{'#'*60}")

    # 获取技能路径
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = "/workspace/temp-skills/a-share-realtime-analyst"

    print(f"\n技能路径: {skill_path}")

    try:
        packager = SkillPackager(skill_path)
        package_path, unpacked_path = packager.package()

        print_step("打包完成")
        print_success(f"技能包: {package_path}")
        print_success(f"目录结构: {unpacked_path}")

        print(f"\n{GREEN}打包成功!{RESET}")
        print(f"\n下一步:")
        print(f"  1. 测试技能功能")
        print(f"  2. 验证输出")
        print(f"  3. 发布到社区")

    except Exception as e:
        print_error(f"打包失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
