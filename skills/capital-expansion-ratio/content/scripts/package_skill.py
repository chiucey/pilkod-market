"""
技能打包脚本 - capital-expansion-ratio

将技能目录打包为 .skill 格式（ZIP 归档）

用法:
    python scripts/package_skill.py [输出目录]

示例:
    python scripts/package_skill.py
    python scripts/package_skill.py /tmp/dist
"""

import os
import sys
import json
import zipfile
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL_NAME = "capital-expansion-ratio"

# 排除文件/目录列表
EXCLUDE_PATTERNS = {
    "__pycache__", ".DS_Store", "*.pyc", "*.pyo",
    ".git", ".svn", ".env", "*.log",
    "node_modules", ".venv", "dist",
    "Thumbs.db", ".idea", ".vscode",
}

EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".log"}


def should_exclude(path: Path) -> bool:
    """判断是否应排除此路径"""
    for part in path.parts:
        if part in EXCLUDE_PATTERNS:
            return True
        for pat in EXCLUDE_PATTERNS:
            if pat.startswith("*") and path.name.endswith(pat[1:]):
                return True
    if path.suffix in EXCLUDE_EXTENSIONS:
        return True
    return False


def run_validation() -> bool:
    """运行验证脚本，返回是否通过"""
    validate_script = SKILL_DIR / "scripts" / "quick_validate.py"
    if not validate_script.exists():
        print("[WARN] 验证脚本不存在，跳过验证")
        return True
    result = subprocess.run(
        [sys.executable, str(validate_script)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True


def package_skill(output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""

    # 读取 meta 信息
    meta_path = SKILL_DIR / "_meta.json"
    if not meta_path.exists():
        print("[ERROR] _meta.json 不存在，无法打包")
        sys.exit(1)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    version = meta.get("version", "1.0.0")
    skill_id = meta.get("id", "unknown")

    # 确定输出路径
    if output_dir is None:
        output_dir = str(SKILL_DIR.parent)

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{SKILL_NAME}_v{version}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 收集文件
    files_to_pack = []
    for file_path in SKILL_DIR.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(SKILL_DIR)
            if not should_exclude(rel):
                files_to_pack.append((file_path, rel))

    print(f"\n正在打包技能：{SKILL_NAME} v{version}")
    print(f"技能 ID：{skill_id}")
    print(f"包含文件：{len(files_to_pack)} 个")
    print("-" * 40)

    # 创建 ZIP 归档
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_path, rel_path in files_to_pack:
            arcname = os.path.join(SKILL_NAME, str(rel_path))
            zf.write(abs_path, arcname)
            print(f"  + {arcname}")

    file_size = os.path.getsize(output_path)
    print("-" * 40)
    print(f"\n✅ 打包完成！")
    print(f"   输出文件：{output_path}")
    print(f"   文件大小：{file_size / 1024:.1f} KB")
    print(f"\n内容验证（试运行解压）：")

    # 验证归档可正常打开
    with zipfile.ZipFile(output_path, "r") as zf:
        names = zf.namelist()
        print(f"   归档包含 {len(names)} 个条目")
        # 检查关键文件
        expected_key_files = [
            f"{SKILL_NAME}/SKILL.md",
            f"{SKILL_NAME}/_meta.json",
            f"{SKILL_NAME}/scripts/fetch_and_calc.py",
        ]
        for key_file in expected_key_files:
            if key_file in names:
                print(f"   ✓ {key_file}")
            else:
                print(f"   ✗ 缺失：{key_file}")

    return output_path


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None

    print("Step 1: 运行质量验证...")
    if not run_validation():
        print("\n[ABORT] 验证失败，拒绝打包。请先修复所有错误。")
        sys.exit(1)

    print("\nStep 2: 打包技能...")
    output_path = package_skill(output_dir)
    print(f"\n🎉 技能包已准备就绪：{output_path}")
