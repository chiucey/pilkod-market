#!/usr/bin/env python3
"""
打包技能脚本 - 将技能打包为可分发的.skill文件
"""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


def scan_sensitive_patterns(content: str) -> list[str]:
    """检测敏感内容"""
    patterns = [
        (r"password\s*=", "hardcoded password"),
        (r"api[_-]?key\s*=", "hardcoded API key"),
        (r"secret\s*=", "hardcoded secret"),
        (r"-----BEGIN.*PRIVATE KEY-----", "private key"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    ]

    findings = []
    for pattern, description in patterns:
        import re
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(description)

    return findings


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为.skill文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 读取meta信息
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        version = meta.get("version", "1.0.0")
    else:
        version = "1.0.0"

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = Path(output_dir) / f"{skill_name}_v{version}_{timestamp}.skill"

    # 创建ZIP包
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                # 跳过隐藏文件和敏感文件
                if any(part.startswith(".") for part in file_path.parts):
                    continue

                # 检查敏感内容
                try:
                    content = file_path.read_text(encoding="utf-8")
                    sensitive = scan_sensitive_patterns(content)
                    if sensitive:
                        print(f"⚠️  Skipping {file_path}: contains {', '.join(sensitive)}")
                        continue
                except:
                    pass

                # 添加到包
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"\n✅ Skill packaged: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.2f} KB")

    return str(output_file)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    output = package_skill(skill_path, output_dir)
    print(f"\n📦 Package created: {output}")


if __name__ == "__main__":
    main()
