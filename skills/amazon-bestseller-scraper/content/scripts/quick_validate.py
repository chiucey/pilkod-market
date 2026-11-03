#!/usr/bin/env python3
"""驗證 Amazon Bestseller Scraper 技能結構"""

import json
import sys
from pathlib import Path

def validate_skill():
    errors = []
    warnings = []

    skill_dir = Path("/workspace/temp-skills/amazon-bestseller-scraper")

    # 檢查必需文件
    if not (skill_dir / "SKILL.md").exists():
        errors.append("SKILL.md 不存在")

    if not (skill_dir / "_meta.json").exists():
        errors.append("_meta.json 不存在")

    # 驗證 _meta.json
    meta_path = skill_dir / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = json.load(f)

            if "id" not in meta:
                errors.append("_meta.json 缺少 id 欄位")
            if "version" not in meta:
                errors.append("_meta.json 缺少 version 欄位")
            if meta.get("id") != "100101":
                errors.append(f"_meta.json id 應為 100101，實際為 {meta.get('id')}")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 解析錯誤: {e}")

    # 驗證 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        if not content.startswith("---"):
            errors.append("SKILL.md 必須以 YAML frontmatter 開頭（---）")

        # 提取 frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]

                if "name:" not in frontmatter:
                    errors.append("frontmatter 缺少 name 欄位")
                if "description:" not in frontmatter:
                    errors.append("frontmatter 缺少 description 欄位")

                # 檢查 name 格式
                for line in frontmatter.split("\n"):
                    if line.startswith("name:"):
                        name_value = line.split(":", 1)[1].strip()
                        if "amazon" not in name_value.lower():
                            warnings.append("name 建議包含 'amazon' 關鍵字")

    # 報告結果
    if errors:
        print("❌ 驗證失敗:")
        for e in errors:
            print(f"  - {e}")
        return False

    if warnings:
        print("⚠️ 驗證警告:")
        for w in warnings:
            print(f"  - {w}")

    print("✅ 驗證通過")
    return True

if __name__ == "__main__":
    success = validate_skill()
    sys.exit(0 if success else 1)
