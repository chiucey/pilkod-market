#!/usr/bin/env python3
"""
OpenClaw 完整导出脚本
导出所有技能和记忆为可迁移的打包文件
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 扫描目录配置
SKILL_DIRS = [
    ".claude/skills",
    ".expert/skills",
    "temp-skills"
]

MEMORY_DIR = "/memories"

EXCLUDE_PATTERNS = {
    "node_modules", ".git", "__pycache__", ".DS_Store",
    "*.log", ".env", "secrets", "thumbs.db"
}

def should_exclude(path: str) -> bool:
    """检查路径是否应被排除"""
    path_lower = path.lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*."):
            ext = pattern[1:]
            if path_lower.endswith(ext):
                return True
        elif pattern in path_lower:
            return True
    return False

def scan_directory(base_path: str, extensions: List[str] = None) -> List[Path]:
    """扫描目录获取所有指定扩展名的文件"""
    files = []
    try:
        for root, dirs, filenames in os.walk(base_path):
            # 过滤排除项
            dirs[:] = [d for d in dirs if not should_exclude(d)]

            for filename in filenames:
                if extensions:
                    if any(filename.endswith(ext) for ext in extensions):
                        full_path = Path(root) / filename
                        if not should_exclude(str(full_path)):
                            files.append(full_path)
                else:
                    full_path = Path(root) / filename
                    if not should_exclude(str(full_path)):
                        files.append(full_path)
    except FileNotFoundError:
        pass
    return files

def read_file_content(file_path: Path) -> Dict[str, Any]:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "path": str(file_path),
            "content": content,
            "size": len(content),
            "md5": hashlib.md5(content.encode()).hexdigest()
        }
    except Exception as e:
        return {
            "path": str(file_path),
            "error": str(e)
        }

def scan_skills() -> Dict[str, Any]:
    """扫描所有技能"""
    skills = {}

    for skill_dir in SKILL_DIRS:
        if not os.path.exists(skill_dir):
            continue

        for item in os.listdir(skill_dir):
            skill_path = Path(skill_dir) / item
            if not skill_path.is_dir():
                continue

            skill_files = scan_directory(str(skill_path))
            skill_data = {
                "name": item,
                "source": skill_dir,
                "files": {},
                "meta": None
            }

            for file_path in skill_files:
                rel_path = file_path.relative_to(skill_path)
                content = read_file_content(file_path)

                if file_path.name == "_meta.json":
                    try:
                        skill_data["meta"] = json.loads(content["content"])
                    except:
                        pass

                if file_path.name == "SKILL.md":
                    # 解析 frontmatter
                    lines = content["content"].split("\n")
                    if lines and lines[0] == "---":
                        end_idx = lines[1:].index("---") + 1 if "---" in lines[1:] else 0
                        frontmatter = "\n".join(lines[1:end_idx])
                        try:
                            import yaml
                            skill_data["frontmatter"] = yaml.safe_load(frontmatter)
                        except:
                            pass

                skill_data["files"][str(rel_path)] = content

            if skill_data["files"]:
                skills[item] = skill_data

    return skills

def scan_memories() -> Dict[str, Any]:
    """扫描所有记忆文件"""
    memories = {}

    if os.path.exists(MEMORY_DIR):
        memory_files = scan_directory(MEMORY_DIR, [".md", ".txt", ".json"])

        for file_path in memory_files:
            rel_path = file_path.relative_to(Path(MEMORY_DIR))
            memories[str(rel_path)] = read_file_content(file_path)

    return memories

def generate_manifest(skills: Dict, memories: Dict, config: Dict) -> Dict:
    """生成导出清单"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return {
        "export_time": datetime.now().isoformat(),
        "timestamp": timestamp,
        "version": "1.0.0",
        "summary": {
            "skills_count": len(skills),
            "memories_count": len(memories),
            "config_keys": len(config) if config else 0
        },
        "skills": {
            name: {
                "meta": skill.get("meta"),
                "frontmatter": skill.get("frontmatter"),
                "files_count": len(skill.get("files", {}))
            }
            for name, skill in skills.items()
        },
        "memories": list(memories.keys()),
        "config_sections": list(config.keys()) if config else []
    }

def export_all(output_dir: str = None) -> Dict[str, Any]:
    """执行完整导出"""
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"openclaw-backup-{timestamp}"

    os.makedirs(output_dir, exist_ok=True)

    print(f"[1/4] 扫描技能目录...")
    skills = scan_skills()
    print(f"      发现 {len(skills)} 个技能")

    print(f"[2/4] 扫描记忆目录...")
    memories = scan_memories()
    print(f"      发现 {len(memories)} 个记忆文件")

    print(f"[3/4] 扫描配置文件...")
    config = {}
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
                # 只导出非敏感配置
                safe_keys = ["skills", "plugins", "gateway"]
                config = {k: v for k, v in raw_config.items() if k in safe_keys}
        except Exception as e:
            print(f"      配置读取失败: {e}")

    print(f"[4/4] 生成导出包...")

    # 创建输出结构
    skills_dir = Path(output_dir) / "skills"
    memories_dir = Path(output_dir) / "memories"
    config_dir = Path(output_dir) / "config"

    skills_dir.mkdir(parents=True, exist_ok=True)
    memories_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    # 导出技能
    for skill_name, skill_data in skills.items():
        skill_out = skills_dir / skill_name
        skill_out.mkdir(parents=True, exist_ok=True)

        for file_rel_path, file_data in skill_data.get("files", {}).items():
            if "error" in file_data:
                continue

            out_file = skill_out / file_rel_path
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(file_data["content"])

    # 导出记忆
    for mem_rel_path, mem_data in memories.items():
        if "error" in mem_data:
            continue

        out_file = memories_dir / mem_rel_path
        out_file.parent.mkdir(parents=True, exist_ok=True)

        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(mem_data["content"])

    # 导出配置
    if config:
        with open(config_dir / "openclaw-export.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    # 生成清单
    manifest = generate_manifest(skills, memories, config)
    with open(Path(output_dir) / "manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # 生成导入脚本
    import_script = '''#!/bin/bash
# OpenClaw 导出包导入脚本
# 使用方法: bash import.sh <目标openclaw的skills目录>

TARGET_DIR=${1:-"$HOME/.claude/skills"}
EXPORT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "导入技能到: $TARGET_DIR"

# 复制技能
for skill_dir in "$EXPORT_DIR/skills/"*/; do
    skill_name=$(basename "$skill_dir")
    echo "  导入技能: $skill_name"
    cp -r "$skill_dir" "$TARGET_DIR/"
done

# 复制记忆
if [ -d "$EXPORT_DIR/memories" ]; then
    echo "导入记忆文件..."
    cp -r "$EXPORT_DIR/memories/"* /memories/ 2>/dev/null || true
fi

echo "导入完成!"
'''

    with open(Path(output_dir) / "import.sh", 'w', encoding='utf-8') as f:
        f.write(import_script)
    os.chmod(Path(output_dir) / "import.sh", 0o755)

    # 统计大小
    total_size = sum(
        f.get("size", 0)
        for skill in skills.values()
        for f in skill.get("files", {}).values()
    ) + sum(
        m.get("size", 0)
        for m in memories.values()
    )

    result = {
        "success": True,
        "output_dir": output_dir,
        "manifest": manifest,
        "total_size_bytes": total_size,
        "total_size_formatted": f"{total_size / 1024:.1f} KB"
    }

    print(f"\n导出完成!")
    print(f"输出目录: {output_dir}")
    print(f"技能数量: {len(skills)}")
    print(f"记忆文件: {len(memories)}")
    print(f"总大小: {result['total_size_formatted']}")

    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw 完整导出工具")
    parser.add_argument("-o", "--output", help="输出目录")
    args = parser.parse_args()

    result = export_all(args.output)
    print(json.dumps(result, indent=2, ensure_ascii=False))
