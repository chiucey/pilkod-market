# -*- coding: utf-8 -*-
"""
Skill 打包脚本
将 Skill 目录打包为可分发的 .zip 包
生成发布清单 (manifest.json)
"""
import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


def calculate_file_hash(file_path, algorithm='sha256'):
    """计算文件哈希值"""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_skill_metadata(skill_dir):
    """从 SKILL.md 提取元数据"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {}

    content = skill_md.read_text(encoding='utf-8')

    metadata = {}

    # 提取 frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            for line in frontmatter.split('\n'):
                if ':' in line and not line.startswith(' '):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value == '|':
                        # 多行值，取下一行
                        continue
                    metadata[key] = value

    # 提取 description 多行
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            desc_match = None
            for line in frontmatter.split('\n'):
                if line.startswith('description:'):
                    if '|' in line:
                        # 收集多行
                        lines = []
                        in_desc = True
                        for l in frontmatter.split('\n'):
                            if l.startswith('description:'):
                                continue
                            if l.startswith('  '):
                                lines.append(l.strip())
                            else:
                                if lines:
                                    break
                        metadata['description'] = '\n'.join(lines)
                        break
                    else:
                        metadata['description'] = line.split(':', 1)[1].strip()
                        break

    return metadata


def create_manifest(skill_dir, output_dir):
    """创建发布清单 manifest.json"""
    metadata = get_skill_metadata(skill_dir)

    # 收集所有文件信息
    files_info = []
    total_size = 0

    for file_path in skill_dir.rglob('*'):
        if file_path.is_file():
            # 跳过某些文件
            if any(skip in file_path.name for skip in ['.pyc', '__pycache__', 'test_output']):
                continue

            rel_path = file_path.relative_to(skill_dir)
            size = file_path.stat().st_size
            total_size += size

            file_info = {
                "path": str(rel_path).replace('\\', '/'),
                "size_bytes": size,
                "size_human": format_size(size),
                "sha256": calculate_file_hash(file_path),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            files_info.append(file_info)

    # 创建 manifest
    manifest = {
        "manifest_version": "1.0.0",
        "skill": {
            "name": metadata.get('name', skill_dir.name),
            "skill_id": metadata.get('skill_id', ''),
            "version": "1.0.0",
            "author": metadata.get('author', 'Matrix Agent'),
            "description": metadata.get('description', ''),
            "category": "亚马逊 / 电商设计 / RC 攀爬车",
            "tags": ["亚马逊", "设计需求", "RC攀爬车", "Excel", "FMS", "主图", "A+"],
            "license": "MIT",
            "homepage": "",
            "repository": "",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        },
        "requirements": {
            "python": ">=3.9",
            "dependencies": ["openpyxl>=3.0.0"],
            "platform": ["Windows", "macOS", "Linux"]
        },
        "package": {
            "total_files": len(files_info),
            "total_size_bytes": total_size,
            "total_size_human": format_size(total_size),
            "files": files_info
        },
        "installation": {
            "type": "local",
            "target_dir": "~/.minimaxagent/skills/{name}/",
            "method": "auto-load",
            "notes": "将解压后的文件夹移动到 ~/.minimaxagent/skills/ 即可自动加载"
        }
    }

    # 保存 manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest, manifest_path


def create_readme(skill_dir, output_dir, manifest):
    """创建 README.md（发布用）"""
    skill_name = manifest['skill']['name']
    description = manifest['skill']['description']

    readme_content = f"""# {skill_name}

{description}

## 📦 包含内容

- `SKILL.md` - Skill 主说明文件
- `scripts/generate_requirements.py` - Excel 生成核心脚本
- `scripts/validate.py` - Skill 验证脚本
- `scripts/package.py` - 打包脚本（本文件）
- `examples/118L01_Ford_F-100_示例.json` - 使用示例
- `assets/template_structure.md` - 文档结构说明
- `manifest.json` - 发布清单

## 🚀 安装方法

### 方式 1：本地自动加载（推荐）

将本文件夹解压后，移动到：

```
~/.minimaxagent/skills/{skill_name}/
```

下次开启 minimax Agent 会话时自动加载。

### 方式 2：技能广场安装

在 minimax 技能广场搜索 `amazon-image-requirements` 或 `FMS 设计需求`，点击安装。

## 📋 使用方法

### 快速使用

提供以下 5 类信息：

1. **基础信息**：产品名称/型号、比例、电机类型
2. **车型/外观**：车型、官方授权、颜色、外观风格
3. **核心卖点**：5-7 个核心卖点（按优先级）
4. **技术参数**：尺寸、轴距、离地间隙、电池/电机
5. **素材情况**：是否已有素材、是否需要场景图

### 编程方式

```python
from generate_requirements import generate_amazon_image_requirements

product_info = {{
    "model": "118L01",
    "product_name": "Ford F-100",
    "full_name": "FMS 1:18 FCXII 118L01 Ford F-100",
    "scale": "1/18",
    "motor_type": "有刷",
    "vehicle_model": "福特F100",
    "license": "Ford",
    "colors": ["黑白", "蒂芙尼蓝", "红白"],
    "features": [
        "全新FCX18二代低重心(LCG)底盘",
        "多品牌授权，福特官方授权仿真车壳",
        "磁吸快拆结构",
        "全球首推1/18福特F-100攀爬车"
    ],
    "dimensions": "330*145*147mm",
    "wheelbase": "199mm",
    "ground_clearance": "31mm",
    "battery_motor": "180有刷",
    "has_source_assets": True,
    "need_scene_images": True,
    "need_shooting": False,
    "output_dir": "./"
}}

generate_amazon_image_requirements(product_info)
```

## 🛠️ 工具脚本

### 验证

```bash
python scripts/validate.py
```

### 打包

```bash
python scripts/package.py
```

## 📊 生成的文档结构

- **主图**（3 张，1600×1600，黄色标识）
- **副图**（7 张，1600×1600，绿色标识）
- **A+ 产品长图**（2 个尺寸，橙色标识）
- **A+ Banner**（3 个尺寸）
- **A+ 导航栏**（3 张 × 3 尺寸）
- **配件清单**（3 个尺寸）
- **场景图**（3 个尺寸）
- **细节图**（4-5 张，2600×1400）

## 📄 许可证

MIT License

## 👤 作者

Matrix Agent

## 🔖 版本

v{manifest['skill']['version']} ({datetime.now().strftime('%Y-%m-%d')})
"""
    readme_path = output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    return readme_path


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def package_skill(skill_dir, output_dir=None):
    """打包 Skill"""
    skill_dir = Path(skill_dir)
    if not skill_dir.exists():
        print(f"❌ Skill 目录不存在: {skill_dir}")
        return None

    skill_name = skill_dir.name
    if output_dir is None:
        output_dir = skill_dir.parent / "dist"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print(f"  📦 Skill 打包工具")
    print(f"  源目录: {skill_dir}")
    print(f"  输出目录: {output_dir}")
    print("="*70)

    # 1. 创建 manifest.json
    print("\n[1/4] 生成 manifest.json...")
    manifest, manifest_path = create_manifest(skill_dir, output_dir)
    print(f"  ✅ {manifest_path.name}")

    # 2. 创建 README.md
    print("\n[2/4] 生成 README.md...")
    readme_path = create_readme(skill_dir, output_dir, manifest)
    print(f"  ✅ {readme_path.name}")

    # 3. 创建 zip 包
    print("\n[3/4] 创建 zip 包...")
    version = manifest['skill']['version']
    zip_name = f"{skill_name}-v{version}.zip"
    zip_path = output_dir / zip_name

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # 跳过验证报告
                if 'validation_report.json' in file_path.name:
                    continue
                # 跳过测试输出
                if 'test_output' in str(file_path):
                    continue
                rel_path = file_path.relative_to(skill_dir)
                zipf.write(file_path, f"{skill_name}/{rel_path}")

        # 添加 manifest
        zipf.write(manifest_path, f"{skill_name}/manifest.json")
        # 添加 README
        zipf.write(readme_path, f"{skill_name}/README.md")

    zip_size = zip_path.stat().st_size
    print(f"  ✅ {zip_name} ({format_size(zip_size)})")

    # 4. 计算包哈希
    print("\n[4/4] 计算包哈希...")
    package_hash = calculate_file_hash(zip_path)
    print(f"  ✅ SHA256: {package_hash}")

    # 输出总结
    print("\n" + "="*70)
    print("  📋 打包完成")
    print("="*70)
    print(f"  📦 包文件:   {zip_path}")
    print(f"  📊 大小:     {format_size(zip_size)}")
    print(f"  🔐 哈希:     {package_hash[:16]}...")
    print(f"  📄 Manifest: {manifest_path}")
    print(f"  📖 README:   {readme_path}")
    print("="*70)

    return {
        "zip_path": str(zip_path),
        "manifest_path": str(manifest_path),
        "readme_path": str(readme_path),
        "zip_size": zip_size,
        "package_hash": package_hash,
        "manifest": manifest
    }


def main():
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = Path(__file__).parent.parent

    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = None

    result = package_skill(skill_dir, output_dir)
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
