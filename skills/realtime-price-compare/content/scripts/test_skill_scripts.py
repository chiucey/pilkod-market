#!/usr/bin/env python3
"""回归测试：校验器（quick_validate）与打包器（package_skill）。

运行：
    python3 scripts/test_skill_scripts.py

覆盖：
- 真实技能目录通过校验
- 各类破坏性改动会被校验器拦截（frontmatter 缺失、目录名不匹配、非法 name 等）
- 打包器产出可正常打开的 .skill，且包含预期文件、不含垃圾文件
"""

import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from package_skill import package_skill  # noqa: E402
from quick_validate import validate_skill  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DISPLAY_NAME = "全网实时比价"
EXPECTED_NAME = "realtime-price-compare"


class TestRealSkillValidates(unittest.TestCase):
    def test_skill_directory_passes_validation(self):
        ok, message = validate_skill(SKILL_ROOT)
        self.assertTrue(ok, message)

    def test_display_name_is_chinese_product_name(self):
        meta = json.loads((SKILL_ROOT / "_meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["display_name"], EXPECTED_DISPLAY_NAME)
        self.assertEqual(meta["name"], EXPECTED_NAME)

    def test_frontmatter_name_matches_folder_and_slug(self):
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"), "SKILL.md 必须以 frontmatter 开头")
        frontmatter = content.split("---", 2)[1]
        self.assertIn(f"name: {EXPECTED_NAME}", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_manual_reference_is_linked_and_present(self):
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/tool-manual.md", content)
        self.assertTrue((SKILL_ROOT / "references" / "tool-manual.md").exists())

    def test_script_declares_matching_skill_name(self):
        script = (SKILL_ROOT / "scripts" / "shop_search.py").read_text(encoding="utf-8")
        self.assertIn(f'SKILL_NAME = "{EXPECTED_NAME}"', script)


class TestValidatorRejectsBrokenSkills(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.skill = self.tmp / EXPECTED_NAME
        shutil.copytree(SKILL_ROOT, self.skill)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_missing_frontmatter_fails(self):
        path = self.skill / "SKILL.md"
        path.write_text("# 没有 frontmatter\n", encoding="utf-8")
        ok, _ = validate_skill(self.skill)
        self.assertFalse(ok)

    def test_missing_description_fails(self):
        path = self.skill / "SKILL.md"
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace("description: |", "notdescription: |"), encoding="utf-8")
        ok, _ = validate_skill(self.skill)
        self.assertFalse(ok)

    def test_chinese_frontmatter_name_fails(self):
        path = self.skill / "SKILL.md"
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace(f"name: {EXPECTED_NAME}", "name: 全网实时比价"), encoding="utf-8")
        ok, message = validate_skill(self.skill)
        self.assertFalse(ok)
        self.assertIn("hyphen-case", message)

    def test_folder_name_mismatch_fails(self):
        renamed = self.tmp / "wrong-folder"
        self.skill.rename(renamed)
        ok, message = validate_skill(renamed)
        self.assertFalse(ok)
        self.assertIn("must match frontmatter name", message)

    def test_missing_meta_fails(self):
        (self.skill / "_meta.json").unlink()
        ok, message = validate_skill(self.skill)
        self.assertFalse(ok)
        self.assertIn("_meta.json", message)

    def test_invalid_version_fails(self):
        meta_path = self.skill / "_meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["version"] = "v1"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        ok, message = validate_skill(self.skill)
        self.assertFalse(ok)
        self.assertIn("semver", message)


class TestPackaging(unittest.TestCase):
    def test_package_creates_readable_archive(self):
        out = Path(tempfile.mkdtemp())
        try:
            archive = package_skill(SKILL_ROOT, out)
            self.assertIsNotNone(archive)
            self.assertTrue(archive.exists())
            with zipfile.ZipFile(archive) as zf:
                names = set(zf.namelist())
                self.assertIn(f"{EXPECTED_NAME}/SKILL.md", names)
                self.assertIn(f"{EXPECTED_NAME}/_meta.json", names)
                self.assertIn(f"{EXPECTED_NAME}/scripts/shop_search.py", names)
                self.assertIn(f"{EXPECTED_NAME}/references/tool-manual.md", names)
                self.assertFalse([n for n in names if "__pycache__" in n or n.endswith(".pyc")])
                self.assertFalse([n for n in names if ".DS_Store" in n])
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_package_refuses_broken_skill(self):
        broken = Path(tempfile.mkdtemp()) / EXPECTED_NAME
        broken.mkdir(parents=True)
        try:
            archive = package_skill(broken, broken.parent)
            self.assertIsNone(archive)
        finally:
            shutil.rmtree(broken.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
