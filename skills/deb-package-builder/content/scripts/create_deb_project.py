#!/usr/bin/env python3
"""
DEB Package Project Generator

Creates a standard Debian package structure with all necessary files.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime


def create_deb_project(
    package_name: str,
    version: str,
    maintainer: str,
    description: str,
    architecture: str = "amd64",
    section: str = "utils",
    priority: str = "optional",
    depends: list = None,
    files: dict = None,
    preinst_script: str = None,
    postinst_script: str = None,
    prerm_script: str = None,
    postrm_script: str = None,
    output_dir: str = "/workspace/output/deb-projects"
):
    """
    Create a DEB package project structure.

    Args:
        package_name: Name of the package
        version: Version string
        maintainer: Maintainer info (Name <email>)
        description: Package description
        architecture: Target architecture (amd64, i386, all)
        section: Package section
        priority: Package priority
        depends: List of dependencies
        files: Dict mapping source paths to target paths
        preinst_script: Pre-installation script content
        postinst_script: Post-installation script content
        prerm_script: Pre-removal script content
        postrm_script: Post-removal script content
        output_dir: Output directory
    """
    depends = depends or []
    files = files or {}

    # Create project directory
    project_dir = Path(output_dir) / package_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    debian_dir = project_dir / "DEBIAN"
    debian_dir.mkdir(exist_ok=True)

    # Create package directories based on files
    for target_path in files.values():
        if target_path.startswith("/"):
            target_path = target_path[1:]
        full_path = project_dir / target_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate control file
    control_content = generate_control_file(
        package_name=package_name,
        version=version,
        maintainer=maintainer,
        description=description,
        architecture=architecture,
        section=section,
        priority=priority,
        depends=depends
    )
    (debian_dir / "control").write_text(control_content)

    # Generate scripts
    if preinst_script:
        script_path = debian_dir / "preinst"
        script_path.write_text(preinst_script)
        os.chmod(script_path, 0o755)

    if postinst_script:
        script_path = debian_dir / "postinst"
        postinst = postinst_script.replace("{{PACKAGE_NAME}}", package_name)
        script_path.write_text(postinst)
        os.chmod(script_path, 0o755)

    if prerm_script:
        script_path = debian_dir / "prerm"
        prerm = prerm_script.replace("{{PACKAGE_NAME}}", package_name)
        script_path.write_text(prerm)
        os.chmod(script_path, 0o755)

    if postrm_script:
        script_path = debian_dir / "postrm"
        postrm = postrm_script.replace("{{PACKAGE_NAME}}", package_name)
        script_path.write_text(postrm)
        os.chmod(script_path, 0o755)

    # Create placeholder files
    for source, target in files.items():
        if target.startswith("/"):
            target = target[1:]
        full_target = project_dir / target
        full_target.parent.mkdir(parents=True, exist_ok=True)
        if not full_target.exists():
            full_target.touch()

    # Generate README.md
    readme_content = generate_readme(
        package_name=package_name,
        version=version,
        maintainer=maintainer,
        description=description,
        architecture=architecture,
        depends=depends,
        files=files,
        has_scripts=any([preinst_script, postinst_script, prerm_script, postrm_script])
    )
    (project_dir / "README.md").write_text(readme_content)

    # Generate build script
    build_script = generate_build_script(package_name, output_dir)
    (project_dir / "build.sh").write_text(build_script)
    os.chmod(project_dir / "build.sh", 0o755)

    # Generate md5sums
    generate_md5sums(project_dir, files)

    # Set proper permissions for DEBIAN directory
    os.chmod(debian_dir, 0o755)

    return str(project_dir)


def generate_control_file(
    package_name: str,
    version: str,
    maintainer: str,
    description: str,
    architecture: str,
    section: str,
    priority: str,
    depends: list
) -> str:
    """Generate DEBIAN/control file content."""
    lines = [
        f"Package: {package_name}",
        f"Version: {version}",
        f"Section: {section}",
        f"Priority: {priority}",
        f"Architecture: {architecture}",
    ]

    if depends:
        lines.append(f"Depends: {', '.join(depends)}")

    lines.extend([
        f"Maintainer: {maintainer}",
        f"Description: {description}"
    ])

    return "\n".join(lines) + "\n"


def generate_readme(
    package_name: str,
    version: str,
    maintainer: str,
    description: str,
    architecture: str,
    depends: list,
    files: dict,
    has_scripts: bool
) -> str:
    """Generate README.md for the DEB project."""
    files_list = "\n".join([f"    - `{src}` → `{dst}`" for src, dst in files.items()]) if files else "    (No files specified)"

    scripts_section = ""
    if has_scripts:
        scripts_section = """
### 维护脚本

此包包含以下维护脚本：

| 脚本 | 说明 |
|------|------|
| `preinst` | 安装/升级前执行 |
| `postinst` | 安装/升级后执行 |
| `prerm` | 移除前执行 |
| `postrm` | 移除后执行 |

"""

    depends_section = ""
    if depends:
        depends_section = f"""
### 依赖关系

此包依赖以下包：
{chr(10).join([f"- `{dep}`" for dep in depends])}

"""

    return f"""# {package_name} DEB包工程

## 概述

- **包名称**: {package_name}
- **版本**: {version}
- **维护者**: {maintainer}
- **架构**: {architecture}
- **描述**: {description}

## 目录结构

```
{package_name}/
├── DEBIAN/
│   ├── control        # 包控制信息
│   ├── preinst        # 安装前脚本 (可选)
│   ├── postinst       # 安装后脚本 (可选)
│   ├── prerm          # 移除前脚本 (可选)
│   ├── postrm         # 移除后脚本 (可选)
│   └── md5sums        # 文件校验和
├── etc/
│   └── {package_name}/
│       └── config.conf  # 配置文件
├── usr/
│   ├── bin/
│   │   └── {package_name}   # 可执行文件
│   └── share/
│       └── {package_name}/
│           └── ...          # 应用资源
├── README.md           # 本文档
└── build.sh            # 构建脚本
```

## 文件清单

{files_list}

{depends_section}{scripts_section}
## 构建DEB包

### 方法一：使用构建脚本

```bash
cd {package_name}
./build.sh
```

### 方法二：手动构建

```bash
# 1. 设置目录权限
sudo chmod 755 DEBIAN
sudo chmod 755 DEBIAN/*

# 2. 生成文件校验和
cd ..
dpkg-deb --build {package_name}
```

### 方法三：完整构建流程

```bash
# 检查构建依赖
dpkg-checkbuilddeps

# 构建包
dpkg-deb --build {package_name} {package_name}_{version}_{architecture}.deb

# 验证包内容
dpkg-deb --contents {package_name}_{version}_{architecture}.deb
dpkg-deb --info {package_name}_{version}_{architecture}.deb
```

## 安装与测试

### 本地安装测试

```bash
# 安装DEB包
sudo dpkg -i {package_name}_{version}_{architecture}.deb

# 或使用apt（支持依赖自动安装）
sudo apt install ./{package_name}_{version}_{architecture}.deb
```

### 验证安装

```bash
# 检查包信息
dpkg -s {package_name}

# 列出包内文件
dpkg -L {package_name}

# 验证文件完整性
dpkg --verify
```

### 卸载

```bash
# 移除包（保留配置）
sudo dpkg -r {package_name}

# 完全清除（包含配置）
sudo dpkg --purge {package_name}
```

## 自定义修改

### 修改包信息

编辑 `DEBIAN/control` 文件：

```
Package: {package_name}
Version: <新版本>
Maintainer: <维护者>
...
```

### 添加新文件

1. 将文件放入对应目录
2. 更新 `build.sh` 中的文件列表
3. 重新构建包

### 修改维护脚本

编辑 `DEBIAN/` 下的脚本文件：
- `preinst`: 安装前执行
- `postinst`: 安装后执行（设置权限、启动服务等）
- `prerm`: 移除前执行（停止服务等）
- `postrm`: 移除后执行（清理数据等）

## 常见问题

### Q: 权限被拒绝
确保DEBIAN目录及其内容权限为755：
```bash
sudo chmod 755 DEBIAN
sudo chmod 755 DEBIAN/*
```

### Q: 依赖缺失
检查并安装构建依赖：
```bash
dpkg-checkbuilddeps
sudo apt install <缺失的依赖>
```

### Q: 文件冲突
使用 `--force-overwrite` 标志（谨慎使用）：
```bash
dpkg --force-overwrite -i {package_name}.deb
```

## 更多信息

- [Debian New Maintainers' Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [Debian Policy Manual](https://www.debian.org/doc/debian-policy/)
- [dpkg-deb man page](https://man7.org/linux/man-pages/man1/dpkg-deb.1.html)

---
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    return readme_content


def generate_build_script(package_name: str, output_dir: str) -> str:
    """Generate build script for the DEB package."""
    return f"""#!/bin/bash
# {package_name} DEB Package Build Script

set -e

PACKAGE_NAME="{package_name}"
OUTPUT_DIR="{output_dir}"
ARCHITECTURE="amd64"

# Get version from control file
if [ -f "DEBIAN/control" ]; then
    VERSION=$(grep "^Version:" DEBIAN/control | cut -d' ' -f2)
else
    echo "Error: DEBIAN/control not found"
    exit 1
fi

echo "Building ${{PACKAGE_NAME}} v${{VERSION}}..."

# Set proper permissions
echo "Setting permissions..."
sudo chmod 755 DEBIAN
sudo chmod 755 DEBIAN/* 2>/dev/null || true

# Update md5sums
echo "Generating checksums..."
find . -type f ! -path './DEBIAN/*' -exec md5sum {{}} \\; > DEBIAN/md5sums

# Build the package
echo "Building DEB package..."
cd ..
dpkg-deb --build "${{PACKAGE_NAME}}" "${{PACKAGE_NAME}}_${{VERSION}}_${{ARCHITECTURE}}.deb"

echo ""
echo "Build complete: ${{PACKAGE_NAME}}_${{VERSION}}_${{ARCHITECTURE}}.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${{PACKAGE_NAME}}_${{VERSION}}_${{ARCHITECTURE}}.deb"
echo ""
echo "To verify contents:"
echo "  dpkg-deb --contents ${{PACKAGE_NAME}}_${{VERSION}}_${{ARCHITECTURE}}.deb"
"""


def generate_md5sums(project_dir: Path, files: dict):
    """Generate md5sums file."""
    md5sums_path = project_dir / "DEBIAN" / "md5sums"
    lines = []

    for source, target in files.items():
        if target.startswith("/"):
            target = target[1:]
        full_path = project_dir / target
        if full_path.exists():
            md5 = __import__("hashlib").md5(full_path.read_bytes()).hexdigest()
            lines.append(f"{md5}  {target}")

    md5sums_path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Create DEB package project")
    parser.add_argument("--package-name", required=True, help="Package name")
    parser.add_argument("--version", required=True, help="Package version")
    parser.add_argument("--maintainer", required=True, help="Maintainer info")
    parser.add_argument("--description", required=True, help="Package description")
    parser.add_argument("--architecture", default="amd64", help="Target architecture")
    parser.add_argument("--section", default="utils", help="Package section")
    parser.add_argument("--priority", default="optional", help="Package priority")
    parser.add_argument("--depends", nargs="*", default=[], help="Dependencies")
    parser.add_argument("--files", type=json.loads, default={}, help="Files dict as JSON")
    parser.add_argument("--preinst", help="Pre-installation script")
    parser.add_argument("--postinst", help="Post-installation script")
    parser.add_argument("--prerm", help="Pre-removal script")
    parser.add_argument("--postrm", help="Post-removal script")
    parser.add_argument("--output-dir", default="/workspace/output/deb-projects", help="Output directory")

    args = parser.parse_args()

    project_dir = create_deb_project(
        package_name=args.package_name,
        version=args.version,
        maintainer=args.maintainer,
        description=args.description,
        architecture=args.architecture,
        section=args.section,
        priority=args.priority,
        depends=args.depends,
        files=args.files,
        preinst_script=args.preinst,
        postinst_script=args.postinst,
        prerm_script=args.prerm,
        postrm_script=args.postrm,
        output_dir=args.output_dir
    )

    print(f"DEB project created at: {project_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
