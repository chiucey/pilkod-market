#!/usr/bin/env python3
"""
French Learning Tutor - 打包脚本
将技能打包为可分发的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_step(msg):
    print(f"\n{'─'*50}")
    print(f"📦 {msg}")
    print(f"{'─'*50}")

def clean_directory(dir_path):
    """清理目录，移除 __pycache__ 等"""
    for root, dirs, files in os.walk(dir_path):
        # 移除 Python 缓存
        if '__pycache__' in dirs:
            shutil.rmree(os.path.join(root, '__pycache__'))
        # 移除 .pyc 文件
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        # 移除临时文件
        for file in files:
            if file.startswith('.') and file not in ['.gitkeep']:
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass

def verify_structure(skill_dir):
    """验证技能结构"""
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            print_error(f"缺少必需文件: {file}")
            return False
    return True

def validate_meta(meta_path):
    """验证 _meta.json"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_keys = ['id', 'version', 'name']
        for key in required_keys:
            if key not in meta:
                print_error(f"缺少字段: {key}")
                return False

        print_success(f"元数据验证通过 - ID: {meta['id']}, Version: {meta['version']}")
        return True
    except Exception as e:
        print_error(f"元数据验证失败: {e}")
        return False

def create_package(skill_dir, output_dir="."):
    """创建技能包"""
    print_step("开始打包")

    # 获取技能名称和版本
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = meta.get('name', os.path.basename(skill_dir))
    skill_version = meta.get('version', '1.0.0')

    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"{skill_name}-{skill_version}-{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 清理技能目录
    print_info(f"清理目录: {skill_dir}")
    clean_directory(skill_dir)

    # 创建 ZIP 包
    print_info(f"创建包文件: {output_filename}")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 跳过隐藏目录和 __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

                # 显示进度
                relative_path = os.path.relpath(file_path, skill_dir)
                print_info(f"  + {relative_path}")

    # 验证包内容
    print_info("\n验证包内容...")
    with zipfile.ZipFile(output_path, 'r') as zipf:
        file_list = zipf.namelist()
        print_success(f"包含 {len(file_list)} 个文件/目录")

        # 检查必需文件
        required_in_package = ['SKILL.md', '_meta.json']
        for required in required_in_package:
            if required not in file_list:
                print_error(f"包中缺少: {required}")
                return None

    # 计算文件大小
    file_size = os.path.getsize(output_path)
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"
    else:
        size_str = f"{file_size / 1024:.2f} KB"

    print_step("打包完成")
    print_success(f"技能包: {output_path}")
    print_success(f"大小: {size_str}")
    print_success(f"版本: {skill_version}")

    # 返回包信息
    return {
        "path": output_path,
        "name": skill_name,
        "version": skill_version,
        "size": size_str,
        "files": len(file_list)
    }

def generate_readme(skill_dir, package_info):
    """生成安装说明 README"""
    readme_content = f"""# {package_info['name']} - 法语学习技能

## 版本信息
- **版本**: {package_info['version']}
- **大小**: {package_info['size']}
- **文件数**: {package_info['files']}

## 安装方法

### 方法一：导入到 AI 软件
1. 下载 `.skill` 文件
2. 在目标 AI 软件中导入技能
3. 激活并开始使用

### 方法二：手动安装
1. 解压 `.skill` 文件（实际是 ZIP 格式）
2. 将内容复制到技能目录
3. 重启 AI 软件

## 功能特性

- ✅ 每日法语学习计划（A1-B2）
- ✅ TV5Monde 练习资源
- ✅ 口语练习（语音检测）
- ✅ 听力练习（慢速/常速）
- ✅ 遗忘曲线复习系统
- ✅ 学习进度追踪
- ✅ 飞书集成（可选）

## 使用说明

### 每日学习流程
1. 查看今日练习推送
2. 完成 TV5Monde 练习
3. 进行听说训练
4. 完成复习任务
5. 获取学习总结

### 口语练习
- 点击"开始口语练习"
- 朗读指定内容
- 获取发音反馈

### 听力练习
- 选择慢速或常速
- 完成练习后确认
- 获取知识回顾

### 飞书集成（如需）
1. 配置飞书 Webhook
2. 启用每日推送
3. 在飞书中学习

## 文件结构

```
french-learning-tutor/
├── SKILL.md          # 主技能文件
├── _meta.json        # 元数据
├── scripts/          # 辅助脚本
├── references/       # 参考文档
└── assets/           # 学习资源
```

## 版本历史

- **{package_info['version']}** - 初始版本
  - 每日学习计划
  - TV5Monde 集成
  - 听说训练
  - 遗忘曲线复习
  - 飞书集成

---

*由 MiniMax Agent 生成 | {datetime.now().strftime('%Y-%m-%d')}*
"""

    readme_path = os.path.join(os.path.dirname(package_info['path']), f"{package_info['name']}_README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    return readme_path

def main():
    # 获取技能目录
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"\n{'='*60}")
    print(f"🎓 French Learning Tutor - 打包工具")
    print(f"{'='*60}\n")

    print_info(f"技能目录: {skill_dir}")
    print_info(f"输出目录: {output_dir}")

    # 验证结构
    if not verify_structure(skill_dir):
        print_error("结构验证失败")
        sys.exit(1)

    # 验证元数据
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not validate_meta(meta_path):
        print_error("元数据验证失败")
        sys.exit(1)

    # 创建包
    package_info = create_package(skill_dir, output_dir)
    if not package_info:
        print_error("打包失败")
        sys.exit(1)

    # 生成 README
    readme_path = generate_readme(skill_dir, package_info)
    print_success(f"安装说明: {readme_path}")

    print(f"\n{'='*60}")
    print("🎉 打包成功！")
    print(f"{'='*60}\n")

    print("📋 下一步:")
    print("  1. 将 .skill 文件分享给其他用户")
    print("  2. 用户在 AI 软件中导入技能")
    print("  3. 开始法语学习之旅")

if __name__ == "__main__":
    main()