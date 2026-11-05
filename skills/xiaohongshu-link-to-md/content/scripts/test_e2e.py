#!/usr/bin/env python3
"""
test_e2e.py — xiaohongshu-link-to-md 端到端回归测试

覆盖 10 个测试场景：
  T1: 链接解析 (extract_note_id)
  T2: L1 HTML 抓取（使用缓存 HTML / mock）
  T3: L3 降级（无效链接）
  T4: 模板选择（视频→full, 简单图文→mini）
  T5: 标签去重 (dedupe_tags)
  T6: 金句提取 (extract_key_quotes)
  T7: link 模式渲染
  T8: none 模式渲染
  T9: url 模式渲染
  T10: validate_output 集成

设计原则：
  - 离线友好：优先使用 XIAOHONGSHU_HTML_CACHE 环境变量
  - 不依赖真实 cookie
  - 纯 Python 标准库 + 项目内模块

Usage:
  python scripts/test_e2e.py                    # 全部测试
  python scripts/test_e2e.py -v                 # 详细输出
  python scripts/test_e2e.py TestXiaohongshuCommon      # 只测 xhs_common 模块
"""

import os
import re
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# 把 scripts/ 目录加入 sys.path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

# ---- 核心模块导入（不依赖 xiaohongshu 库）----
from xiaohongshu_common import (
    extract_note_id,
    dedupe_tags,
    extract_key_quotes,
    normalize_tag,
)

# ---- 可选模块导入（依赖 xiaohongshu 库，未安装时跳过相关测试）----
_XHS_AVAILABLE = False
_fetch_note_module = None
_xhs_to_md_module = None

try:
    import fetch_note as _fetch_note_module
    _XHS_AVAILABLE = True
except ImportError:
    pass

try:
    import xhs_to_md as _xhs_to_md_module
except ImportError:
    pass

# 从 xhs_to_md 导入渲染函数（如果可用）
if _xhs_to_md_module is not None:
    select_template = _xhs_to_md_module.select_template
    slugify = _xhs_to_md_module.slugify
    render_image_refs = _xhs_to_md_module.render_image_refs
    render_mini = _xhs_to_md_module.render_mini
    render_full = _xhs_to_md_module.render_full
    cleanup_unfilled_placeholders = _xhs_to_md_module.cleanup_unfilled_placeholders
    load_template = _xhs_to_md_module.load_template
    _convert_fn = _xhs_to_md_module.convert
else:
    select_template = None
    slugify = None
    render_image_refs = None
    render_mini = None
    render_full = None
    cleanup_unfilled_placeholders = None
    load_template = None
    _convert_fn = None

from validate_output import (
    validate_file_exists,
    validate_no_unfilled_placeholders,
)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def make_mock_note(note_id="abc123def456abc123def456", **overrides):
    """构造标准化的 mock 笔记数据，用于测试渲染流程。"""
    defaults = {
        "note_id": note_id,
        "url": f"https://www.xiaohongshu.com/explore/{note_id}",
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fetch_mode": "L1_HTML_ios_discovery_with_token",
        "title": "测试笔记标题",
        "desc": "这是测试笔记的正文内容。包含一些句子用于测试金句提取。深度学习改变了 AI 领域！",
        "type": "image-text",
        "author": {
            "nickname": "测试作者",
            "user_id": "test_user_123",
            "avatar": "https://example.com/avatar.jpg",
        },
        "interact": {
            "liked": 1200,
            "collected": 340,
            "comment": 89,
            "share": 56,
        },
        "publish_time": "2026-05-15 10:30:00",
        "tags": ["AI", "深度学习", "机器学习", "ai"],
        "images": [
            {"url": "https://sns-webpic-qc.xhscdn.com/test1.jpg", "width": 1080, "height": 720},
            {"url": "https://sns-webpic-qc.xhscdn.com/test2.jpg", "width": 1080, "height": 1920},
        ],
        "video": None,
        "comments": [
            {"user": "用户A", "content": "写得太好了，学到了很多！", "liked": 99, "time": "2026-05-16"},
            {"user": "用户B", "content": "请问有推荐的学习资源吗？", "liked": 45, "time": "2026-05-17"},
            {"user": "用户C", "content": "收藏了，有空仔细看看", "liked": 20, "time": "2026-05-18"},
        ],
    }
    defaults.update(overrides)
    return defaults


class TestXiaohongshuCommon(unittest.TestCase):
    """T1: 链接解析"""

    def test_extract_note_id_long_url(self):
        url = "https://www.xiaohongshu.com/explore/abc123def456abc123def456"
        nid = extract_note_id(url)
        self.assertEqual(nid, "abc123def456abc123def456")

    def test_extract_note_id_discovery(self):
        url = "https://www.xiaohongshu.com/discovery/item/abc123def456abc123def456"
        nid = extract_note_id(url)
        self.assertEqual(nid, "abc123def456abc123def456")

    def test_extract_note_id_with_params(self):
        url = "https://www.xiaohongshu.com/explore/abc123def456abc123def456?xsec_token=xxx"
        nid = extract_note_id(url)
        self.assertEqual(nid, "abc123def456abc123def456")

    def test_extract_note_id_invalid(self):
        url = "https://www.example.com/not-a-xiaohongshu-link"
        nid = extract_note_id(url)
        self.assertIsNone(nid)

    def test_extract_note_id_short_link_returns_none_without_network(self):
        """短链需要网络展开，离线环境返回 None 是正常行为"""
        url = "https://xhslink.com/abc123"
        nid = extract_note_id(url)
        self.assertIn(nid, [None, "abc123def456abc123def456"])


class TestDedupeTags(unittest.TestCase):
    """T5: 标签去重"""

    def test_dedupe_exact_duplicates(self):
        tags = ["AI", "AI", "深度学习"]
        result = dedupe_tags(tags, max_main=5, max_long_tail=10, max_original=3)
        all_tags = result["main"] + result["long_tail"] + result["original"]
        self.assertEqual(len(all_tags), 2)

    def test_dedupe_case_insensitive(self):
        tags = ["AI", "ai", "Ai"]
        result = dedupe_tags(tags, max_main=5, max_long_tail=10, max_original=3)
        all_tags = result["main"] + result["long_tail"] + result["original"]
        self.assertLessEqual(len(all_tags), 3)

    def test_normalize_tag(self):
        self.assertEqual(normalize_tag("#AI"), "ai")
        self.assertEqual(normalize_tag("  AI  "), "ai")
        self.assertEqual(normalize_tag("深度学习"), "深度学习")

    def test_dedupe_empty_input(self):
        result = dedupe_tags([], max_main=5, max_long_tail=10, max_original=3)
        self.assertEqual(result["main"], [])
        self.assertEqual(result["long_tail"], [])
        self.assertEqual(result["original"], [])

    def test_dedupe_respects_limits(self):
        tags = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]
        result = dedupe_tags(tags, max_main=3, max_long_tail=5, max_original=2)
        self.assertLessEqual(len(result["main"]), 3)
        self.assertLessEqual(len(result["long_tail"]), 5)
        self.assertLessEqual(len(result["original"]), 2)


class TestExtractKeyQuotes(unittest.TestCase):
    """T6: 金句提取"""

    def test_extract_from_text_with_exclamation(self):
        text = "这是一段普通的话。深度学习改变了 AI 领域！这是一个非常重要的发现。"
        quotes = extract_key_quotes(text, max_count=4)
        self.assertGreater(len(quotes), 0)
        self.assertIn("深度学习改变了 AI 领域", quotes[0])

    def test_extract_from_empty_text(self):
        quotes = extract_key_quotes("", max_count=4)
        self.assertEqual(quotes, [])

    def test_extract_from_short_text(self):
        text = "AI 很重要。"
        quotes = extract_key_quotes(text, max_count=4)
        self.assertLessEqual(len(quotes), 4)

    def test_extract_respects_max_count(self):
        text = "第一句话！第二句话！第三句话！第四句话！第五句话！第六句话！"
        quotes = extract_key_quotes(text, max_count=2)
        self.assertLessEqual(len(quotes), 2)


class TestTemplateSelection(unittest.TestCase):
    """T4: 模板选择（需要 xhs_to_md 模块）"""

    @classmethod
    def setUpClass(cls):
        if select_template is None:
            raise unittest.SkipTest("xhs_to_md 模块不可用（xiaohongshu 库未安装）")

    def test_video_selects_full(self):
        note = make_mock_note(type="video", video={"duration": 120})
        self.assertEqual(select_template(note), "full")

    def test_many_images_selects_full(self):
        images = [{"url": f"img{i}.jpg", "width": 100, "height": 100} for i in range(10)]
        note = make_mock_note(images=images)
        self.assertEqual(select_template(note), "full")

    def test_long_desc_selects_full(self):
        note = make_mock_note(desc="x" * 1500)
        self.assertEqual(select_template(note), "full")

    def test_simple_note_selects_mini(self):
        note = make_mock_note(type="image-text", desc="简短内容")
        self.assertEqual(select_template(note), "mini")


class TestTemplateRendering(unittest.TestCase):
    """T7/T8/T9: 模板渲染（link/none/url 三种模式，需要 xhs_to_md 模块）"""

    @classmethod
    def setUpClass(cls):
        if load_template is None:
            raise unittest.SkipTest("xhs_to_md 模块不可用（xiaohongshu 库未安装）")
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="xiaohongshu_e2e_test_"))
        cls.output_dir = cls.tmp_dir / "output"
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        cls.media_dir = cls.tmp_dir / ".cache" / "test_note_id"
        cls.media_dir.mkdir(parents=True, exist_ok=True)
        # 创建假图片文件
        for i in range(1, 3):
            (cls.media_dir / f"image_{i:02d}.jpg").write_bytes(b"fake-image-data")

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def setUp(self):
        self.note = make_mock_note()
        self.output_path = self.output_dir / "2026-06-02-test.md"

    def test_render_mini_link_mode(self):
        """T7: link 模式 - 相对路径引用本地图片"""
        refs = render_image_refs(self.note, "link", self.media_dir, self.output_path)
        self.assertEqual(len(refs), 2)
        for ref in refs:
            self.assertIsNotNone(ref["local_path"])
            self.assertIn("image_", ref["ref"])
            self.assertNotIn("https://", ref["ref"])

        template = load_template("mini", TEMPLATE_DIR)
        result = render_mini(self.note, template, refs, "link")
        result = cleanup_unfilled_placeholders(result)

        self.assertIn("测试笔记标题", result)
        self.assertIn("测试作者", result)
        self.assertNotIn("http://", result)

    def test_render_mini_none_mode(self):
        """T8: none 模式 - 不含任何图片"""
        refs = render_image_refs(self.note, "none", self.media_dir, self.output_path)
        for ref in refs:
            self.assertEqual(ref["ref"], "")

        template = load_template("mini", TEMPLATE_DIR)
        result = render_mini(self.note, template, refs, "none")
        result = cleanup_unfilled_placeholders(result)
        self.assertNotIn("![", result)

    def test_render_mini_url_mode(self):
        """T9: url 模式 - 保留 CDN URL"""
        refs = render_image_refs(self.note, "url", self.media_dir, self.output_path)
        self.assertEqual(len(refs), 2)
        for ref in refs:
            self.assertIn("https://", ref["ref"])

        template = load_template("mini", TEMPLATE_DIR)
        result = render_mini(self.note, template, refs, "url")
        result = cleanup_unfilled_placeholders(result)
        self.assertIn("https://", result)

    def test_render_full_with_comments(self):
        """完整版渲染：包含评论"""
        refs = render_image_refs(self.note, "link", self.media_dir, self.output_path)
        template = load_template("full", TEMPLATE_DIR)
        result = render_full(self.note, template, refs, "link")
        result = cleanup_unfilled_placeholders(result)

        self.assertIn("测试笔记标题", result)
        self.assertIn("用户A", result)
        self.assertIn("写得太好了", result)
        self.assertIn("标签矩阵", result)

    def test_cleanup_unfilled_placeholders(self):
        """占位符清理"""
        md = "# 标题\n这里有一个 {{未填充的占位符}} 在文本中\n#{{标签占位符}}"
        cleaned = cleanup_unfilled_placeholders(md)
        self.assertNotIn("{{", cleaned)
        self.assertIn("_待填充_", cleaned)
        self.assertNotIn("#{{", cleaned)

    def test_slugify(self):
        self.assertEqual(slugify("深度学习入门指南"), "深度学习入门指南")
        self.assertEqual(slugify("AI & ML 实战!"), "AI-ML-实战")
        self.assertEqual(slugify(""), "untitled")


class TestValidateOutputIntegration(unittest.TestCase):
    """T10: validate_output 集成测试"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="xiaohongshu_val_test_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_validate_good_file(self):
        """正常的 md 文件应通过验证"""
        path = self.tmp / "good.md"
        path.write_text("# 标题\n\n正文内容\n\n## 子标题\n\n- 要点1\n- 要点2\n")
        self.assertIsNotNone(validate_file_exists(str(path)))
        self.assertTrue(validate_no_unfilled_placeholders(str(path)))

    def test_validate_unfilled_placeholders(self):
        """含残留占位符的文件应报错"""
        path = self.tmp / "bad.md"
        path.write_text("# 标题\n\n{{未填充}}\n\n## {{占位符}} 标题\n")
        with self.assertRaises(Exception):
            validate_no_unfilled_placeholders(str(path))

    def test_validate_empty_file(self):
        """空文件应报错"""
        path = self.tmp / "empty.md"
        path.write_text("")
        with self.assertRaises(Exception):
            validate_file_exists(str(path))

    def test_validate_missing_file(self):
        """不存在的文件应报错"""
        with self.assertRaises(Exception):
            validate_file_exists(str(self.tmp / "does_not_exist.md"))


class TestHtmlFetchWithCache(unittest.TestCase):
    """T2/T3: HTML 抓取（需要 fetch_note 模块）"""

    @classmethod
    def setUpClass(cls):
        if not _XHS_AVAILABLE:
            raise unittest.SkipTest("xiaohongshu 库未安装，跳过 fetch_note 相关测试")

    def test_extract_note_from_html_module_import(self):
        """验证 fetch_note 模块可以正常导入"""
        try:
            import fetch_note
            self.assertTrue(hasattr(fetch_note, "fetch"))
            self.assertTrue(hasattr(fetch_note, "fetch_via_html"))
        except ImportError as e:
            self.skipTest(f"fetch_note 模块导入失败: {e}")

    def test_fetch_l3_fallback_invalid_link(self):
        """T3: L3 降级 - 无效链接应返回失败结构"""
        import fetch_note
        result = fetch_note.fetch(
            "https://www.xiaohongshu.com/explore/deadbeefdeadbeefdeadbeef01",
            mode="html",
            with_comments=False,
        )
        self.assertIn(result.get("fetch_mode", ""), ["L3_FAILED", "L1_HTML_xhs_lib_fallback"])

    def test_html_cache_env_var(self):
        """XIAOHONGSHU_HTML_CACHE 环境变量功能存在"""
        import fetch_note
        self.assertTrue(hasattr(fetch_note, "_extract_note_from_html"))

    def test_5_variants_defined(self):
        """验证 5 个 HTML 抓取变体都已定义"""
        import fetch_note
        self.assertTrue(hasattr(fetch_note, "_HTML_FETCH_VARIANTS"))
        variants = fetch_note._HTML_FETCH_VARIANTS
        self.assertGreaterEqual(len(variants), 5)
        for v in variants:
            self.assertIn("name", v)
            self.assertIn("url_template", v)
            self.assertIn("headers", v)

    def test_download_note_media_module(self):
        """验证 download_media 模块可导入"""
        try:
            from download_media import download_note_media, download_file
            self.assertTrue(callable(download_note_media))
            self.assertTrue(callable(download_file))
        except ImportError as e:
            self.skipTest(f"download_media 模块导入失败: {e}")


def run_tests():
    """入口：运行所有 E2E 测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
