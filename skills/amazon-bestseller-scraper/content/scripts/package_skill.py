#!/usr/bin/env python3
"""打包 Amazon Bestseller Scraper 技能"""

import json
import shutil
import sys
from pathlib import Path
import tempfile
import zipfile

def package_skill():
    skill_dir = Path("/workspace/temp-skills/amazon-bestseller-scraper")
    output_dir = Path("/workspace/temp-skills")

    # 驗證必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_dir / f).exists():
            print(f"❌ 缺少必需文件: {f}")
            sys.exit(1)

    # 讀取 meta
    with open(skill_dir / "_meta.json") as f:
        meta = json.load(f)

    skill_id = meta.get("id", "unknown")
    version = meta.get("version", "1.0.0")
    skill_name = skill_dir.name

    # 創建輸出文件名
    output_name = f"{skill_name}_{version}.skill"
    output_path = output_dir / output_name

    # 創建臨時目錄
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 複製文件（排除測試和臨時文件）
        exclude_patterns = {"__pycache__", ".pyc", ".git", ".DS_Store"}

        for item in skill_dir.rglob("*"):
            if item.is_file():
                # 檢查是否應該排除
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(item):
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                # 計算相對路徑
                rel_path = item.relative_to(skill_dir)
                dest_path = tmp_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)

        # 創建 ZIP 文件
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in tmp_path.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(tmp_path)
                    zf.write(item, arcname)

    print(f"✅ 技能已打包: {output_path}")
    print(f"   ID: {skill_id}")
    print(f"   Version: {version}")
    return str(output_path)

if __name__ == "__main__":
    package_skill()
