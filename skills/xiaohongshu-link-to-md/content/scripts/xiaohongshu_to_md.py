"""
xiaohongshu_to_md.py — 一键集成脚本：URL → 完整 Markdown 文档

端到端流程：
  1. 解析 URL，提取 noteId
  2. 抓取笔记元信息（自动选 HTML 或 API 模式）
  3. 抓取评论（如果有 cookie）
  4. 下载媒体（图片 / 视频）到本地缓存 —— 默认行为
  5. 选择模板（full / mini）
  6. 渲染 Markdown（图片模式：link/embed/url/none）
  7. 保存到文件

用法：
  python xiaohongshu_to_md.py <URL>
  python xiaohongshu_to_md.py <URL> --image-mode link          # 默认：本地链接
  python xiaohongshu_to_md.py <URL> --image-mode embed         # 嵌入 base64（文件大）
  python xiaohongshu_to_md.py <URL> --image-mode url           # 保留原 URL（不下载）
  python xiaohongshu_to_md.py <URL> --image-mode none          # 不放任何图
  python xiaohongshu_to_md.py <URL> --no-images                # 跳过下载（等价 --image-mode url 且不下载）
  python xiaohongshu_to_md.py <URL> --output-dir ./my-notes
  python xiaohongshu_to_md.py <URL> --template full
  python xiaohongshu_to_md.py urls.txt                         # 批量

输出：
  ./xiaohongshu-notes/2026-06-02-{标题slug}.md
  媒体：.cache/xiaohongshu-link-to-md/{noteId}/image_NN.jpg
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import fetch_note
from download_media import download_note_media
from xiaohongshu_common import (
    cookie_available,
    decide_mode,
    dedupe_tags,
    extract_key_quotes,
    fetch_strategy,
    extract_note_id,
)


# ===== 模板选择 =====
def select_template(note: dict) -> str:
    """根据笔记复杂度选择模板版本"""
    if note.get("type") == "video":
        return "full"
    if len(note.get("images", [])) > 6:
        return "full"
    if len(note.get("desc", "")) > 1000:
        return "full"
    return "mini"


# ===== 工具函数 =====
def slugify(text: str, max_len: int = 30) -> str:
    """把标题转成安全的文件名 slug"""
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip())
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] if text else "untitled"


def load_template(name: str, template_dir: Path) -> str:
    """加载模板文件"""
    template_path = template_dir / f"{name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"模板不存在: {template_path}")
    return template_path.read_text(encoding="utf-8")


# ===== 图片引用渲染 =====
def render_image_refs(
    note: dict,
    image_mode: str,
    media_dir: Path,
    output_md_path: Path,
) -> list[dict]:
    """
    根据 image_mode 渲染图片引用

    Returns:
        list of {"index": 1, "ref": "![...](path)", "local_path": Path | None, "error": str | None}
    """
    images = note.get("images", [])
    refs = []

    for i, img in enumerate(images, 1):
        url = img.get("url", "")
        entry = {"index": i, "url": url, "local_path": None, "ref": "", "error": None}

        if image_mode == "url":
            # 保留原 URL
            entry["ref"] = f"![图片 {i}]({url})"
        elif image_mode == "embed":
            # 嵌入 base64 —— 需要先确保本地有文件
            local = media_dir / f"image_{i:02d}.jpg"
            if local.exists():
                try:
                    data = base64.b64encode(local.read_bytes()).decode("ascii")
                    ext = local.suffix.lstrip(".").lower() or "jpeg"
                    entry["ref"] = f"![图片 {i}](data:image/{ext};base64,{data})"
                    entry["local_path"] = local
                except Exception as e:
                    entry["error"] = f"base64 编码失败: {e}"
                    entry["ref"] = f"![图片 {i}]({url})"  # fallback 到 url
            else:
                entry["error"] = "本地文件不存在，base64 失败"
                entry["ref"] = f"![图片 {i}]({url})"
        elif image_mode == "link":
            # 相对路径链接（使用 os.path.relpath 正确计算跨目录树路径）
            local = media_dir / f"image_{i:02d}.jpg"
            if local.exists():
                rel = os.path.relpath(str(local), str(output_md_path.parent))
                entry["ref"] = f"![图片 {i}]({rel})"
                entry["local_path"] = local
            else:
                entry["error"] = "本地文件不存在，回退到原 URL"
                entry["ref"] = f"![图片 {i}]({url})"
        elif image_mode == "none":
            # 完全不放图
            entry["ref"] = ""
        else:
            entry["ref"] = f"![图片 {i}]({url})"

        refs.append(entry)
    return refs


# ===== 公共替换函数 =====
def _safe_replace(text: str, key: str, value: str) -> str:
    """安全的占位符替换（空值时不替换）"""
    if value:
        return text.replace(key, value)
    return text


# ===== Mini 模板渲染 =====
def render_mini(note: dict, template: str, image_refs: list[dict], image_mode: str) -> str:
    """迷你版渲染：摘要 + 要点 + 评论 + 信息卡"""
    result = template

    # 基础信息
    result = _safe_replace(result, "{{原标题}}", note.get("title", ""))
    result = _safe_replace(result, "{{作者昵称}}", note.get("author", {}).get("nickname", ""))
    result = _safe_replace(result, "{{原文链接}}", note.get("url", ""))
    result = _safe_replace(result, "{{发布时间}}", (note.get("publish_time", "") or "")[:10])
    result = _safe_replace(result, "{{整理时间}}", (note.get("fetched_at", "") or "")[:10] or datetime.now().strftime("%Y-%m-%d"))
    result = _safe_replace(result, "{{noteId}}", note.get("note_id", ""))

    # 互动数据
    interact = note.get("interact", {})
    result = result.replace("{{点赞数}}", str(interact.get("liked", 0)))
    result = result.replace("{{收藏数}}", str(interact.get("collected", 0)))
    result = result.replace("{{评论数}}", str(interact.get("comment", 0)))

    # 类型
    is_video = note.get("type") == "video"
    result = _safe_replace(result, "{{图文/视频}}", "视频" if is_video else "图文")
    if is_video:
        video = note.get("video", {}) or {}
        dur = int(video.get("duration", 0))
        result = _safe_replace(result, "{{X分X秒}}", f"{dur // 60}分{dur % 60}秒")
    else:
        result = _safe_replace(result, "{{N张}}", f"{len(note.get('images', []))}张")

    # 标签（真去重）—— v2.0 修复：正确处理 # 前缀
    raw_tags = note.get("tags", [])
    deduped = dedupe_tags(raw_tags, max_main=5, max_long_tail=10, max_original=3)
    for i, t in enumerate(deduped["main"] + [""] * 5, 1):
        if t:
            t_clean = t.lstrip("#")
            result = result.replace(f"{{{{主词{i}}}}}", t_clean)
    for i, t in enumerate(deduped["long_tail"] + [""] * 10, 1):
        if t:
            t_clean = t.lstrip("#")
            result = result.replace(f"{{{{长尾词{i}}}}}", t_clean)
    for i, t in enumerate(deduped["original"] + [""] * 3, 1):
        if t:
            t_clean = t.lstrip("#")
            result = result.replace(f"{{{{独有标签{i}}}}}", t_clean)

    # 核心摘要
    desc = note.get("desc", "").strip()
    first_sentence = re.split(r"[。!?\n]", desc, maxsplit=1)[0] if desc else "（无正文）"
    result = _safe_replace(result, "{{核心观点}}", first_sentence)
    result = _safe_replace(result, "{{目标读者}}", "（待补充）")
    result = _safe_replace(result, "{{看完后可以做什么}}", "（待补充）")

    # 正文要点（3-5 个 bullet 来自 desc 句子）
    bullets = _split_to_bullets(desc, max_count=5)
    for i, b in enumerate(bullets, 1):
        result = _safe_replace(result, f"{{{{要点 {i}}}}}", b)
    for i in range(len(bullets) + 1, 6):
        result = result.replace(f"- {{{{要点 {i}}}}}", "")

    # 图片信息（图1/2/3 描述）
    for i in range(1, 4):
        ref = image_refs[i - 1]["ref"] if i - 1 < len(image_refs) else ""
        if ref:
            result = result.replace(f"{{{{图{i}/帧 {i}}}}}", ref)
        else:
            result = result.replace(f"{{{{图{i}/帧 {i}}}}}", f"图 {i}（无）")
        result = result.replace(f"{{{{视觉描述 + 关键文字}}}}", "（待图片分析）")

    # 评论 Top 3
    comments = note.get("comments", [])[:3]
    for i in range(3):
        if i < len(comments):
            c = comments[i]
            user_key = f"{{{{用户{chr(65 + i)}}}}}"
            content_key = "{{评论内容}}"
            like_key = "{{点赞数}}"
            result = result.replace(user_key, c.get("user", "匿名"))
            result = result.replace(content_key, c.get("content", ""))
            result = result.replace(like_key, str(c.get("liked", 0)))
        else:
            user_key = f"{{{{用户{chr(65 + i)}}}}}"
            result = result.replace(user_key, "暂无数据")

    # 信息卡
    result = _safe_replace(result, "{{采集时间}}", note.get("fetched_at", ""))
    result = _safe_replace(result, "{{采集模式}}", note.get("fetch_mode", "?"))
    result = _safe_replace(result, "{{图片模式}}", image_mode)

    return result


# ===== 完整版渲染 =====
def render_full(note: dict, template: str, image_refs: list[dict], image_mode: str) -> str:
    """完整版渲染：包含正文、评论、原文附录"""
    result = template

    # 标题区
    result = _safe_replace(result, "{{原标题}}", note.get("title", ""))
    result = _safe_replace(result, "{{作者昵称}}", note.get("author", {}).get("nickname", ""))
    result = _safe_replace(result, "{{原文链接}}", note.get("url", ""))
    result = _safe_replace(result, "{{发布时间}}", (note.get("publish_time", "") or "")[:10])
    result = _safe_replace(result, "{{整理时间}}", (note.get("fetched_at", "") or "")[:10] or datetime.now().strftime("%Y-%m-%d"))
    result = _safe_replace(result, "{{noteId}}", note.get("note_id", ""))
    result = _safe_replace(result, "{{URL}}", note.get("url", ""))

    # 互动数据
    interact = note.get("interact", {})
    result = result.replace("{{点赞数}}", str(interact.get("liked", 0)))
    result = result.replace("{{收藏数}}", str(interact.get("collected", 0)))
    result = result.replace("{{评论数}}", str(interact.get("comment", 0)))

    # 视频/图片
    is_video = note.get("type") == "video"
    video = note.get("video", {}) or {}
    if is_video:
        dur = int(video.get("duration", 0))
        result = _safe_replace(result, "{{X分X秒}}", f"{dur // 60}分{dur % 60}秒")
        result = _safe_replace(result, "{{视频 / 图文}}", "视频")
        result = _safe_replace(result, "{{X分X秒}}（仅视频）", f"{dur // 60}分{dur % 60}秒（仅视频）")
        result = _safe_replace(result, "{{X张}}（仅图文）", "N/A（视频）")
    else:
        result = _safe_replace(result, "{{X分X秒}}", "无（图文）")
        result = _safe_replace(result, "{{视频 / 图文}}", "图文")
        result = _safe_replace(result, "{{X分X秒}}（仅视频）", "N/A（图文）")
        result = _safe_replace(result, "{{X张}}（仅图文）", f"{len(note.get('images', []))}张（仅图文）")
    result = result.replace("{{X张}}", f"{len(note.get('images', []))}张")

    # 标签（真去重）
    raw_tags = note.get("tags", [])
    deduped = dedupe_tags(raw_tags, max_main=5, max_long_tail=10, max_original=3)
    for i, t in enumerate(deduped["main"] + [""] * 5, 1):
        if t:
            t_clean = t.lstrip("#")
            result = result.replace(f"{{{{主词{i}}}}}", t_clean)
    for i, t in enumerate(deduped["long_tail"] + [""] * 10, 1):
        if t:
            t_clean = t.lstrip("#")
            result = result.replace(f"{{{{长尾词{i}}}}}", t_clean)
    for i, t in enumerate(deduped["original"] + [""] * 3, 1):
        if t:
            t_clean = t.lstrip("#")
            result = result.replace(f"{{{{独有原文标签{i}}}}}", t_clean)

    # 核心摘要
    desc = note.get("desc", "").strip()
    first_sentence = re.split(r"[。!?\n]", desc, maxsplit=1)[0] if desc else "（无正文）"
    result = _safe_replace(result, "{{一句话概括笔记主旨}}", first_sentence)
    result = _safe_replace(result, "{{目标读者}}", "（待补充）")
    result = _safe_replace(result, "{{看完后可以立刻做什么}}", "（待补充）")
    result = _safe_replace(result, '{{需要注意的坑/误区（若无则写"无"）}}', '无')

    # 内容重构
    result = _safe_replace(result, "{{段落标题 1}}", "正文")
    result = _safe_replace(result, "{{关键内容提炼_1 / 口播原文转写}}", desc or "（无正文）")
    result = result.replace("{{00:00:00}}", "00:00:00")
    result = _safe_replace(result, "{{视觉信息_1}}", "（需要 images_understand 分析图片后填充）")
    result = _safe_replace(result, "{{原文语音转写_1}}", "（需要 videos_understand 分析视频后填充）")

    # 关键帧位置（用图片列表填充）
    for i in range(1, 6):
        idx_in_imgs = i - 1
        if idx_in_imgs < len(image_refs) and image_refs[idx_in_imgs]["ref"]:
            ref = image_refs[idx_in_imgs]["ref"]
            err = image_refs[idx_in_imgs].get("error", "")
            img_label = f"图片 {idx_in_imgs + 1}"
            result = result.replace(f"{{{{段落标题 {i + 1}}}}}", img_label)
            result = result.replace(f"{{{{关键内容提炼_{i + 1}}}}}", f"\n{err + chr(10) if err else ''}{ref}\n")
            result = result.replace(f"{{{{时间点_{i + 1}}}}}", f"图 {idx_in_imgs + 1}")
            result = result.replace(f"{{{{视觉信息_{i + 1}}}}}", f"{img_label}（已下载到本地缓存，路径见信息卡）")
        else:
            result = result.replace(f"{{{{段落标题 {i + 1}}}}}", "")
            result = result.replace(f"{{{{关键内容提炼_{i + 1}}}}}", "")
            result = result.replace(f"{{{{时间点_{i + 1}}}}}", "")
            result = result.replace(f"{{{{视觉信息_{i + 1}}}}}", "")

    # 金句提取（自动从 desc 里抽）
    quotes = extract_key_quotes(desc, max_count=4)
    for i, q in enumerate(quotes, 1):
        result = _safe_replace(result, f"{{{{金句 {i}原文}}}}", q)
    for i in range(len(quotes) + 1, 5):
        result = result.replace(f'"{{{{金句 {i}原文}}}}"', "")

    # 评论 Top 3
    comments = note.get("comments", [])[:3]
    for i in range(3):
        user_key = f"{{{{用户{chr(65 + i)}}}}}"
        content_key = f"{{{{评论内容_{chr(65 + i)}}}}}"
        like_key = f"{{{{点赞数_{chr(65 + i)}}}}}"
        if i < len(comments):
            c = comments[i]
            result = result.replace(user_key, c.get("user", "匿名"))
            result = result.replace(content_key, c.get("content", ""))
            result = result.replace(like_key, str(c.get("liked", 0)))
        else:
            result = result.replace(user_key, "暂无数据")
            result = result.replace(content_key, "（评论数不足 3 条）")
            result = result.replace(like_key, "0")

    # 关键段落摘录
    key_para = _extract_key_paragraph(desc, quotes)
    result = _safe_replace(result, "{{完整段落原文，保持换行和标点。优先选择内容重构时未完整引用的部分。}}", key_para)

    # 信息卡
    result = _safe_replace(result, "{{采集工具}}", "xiaohongshu-link-to-md v2.0")
    result = _safe_replace(result, "{{采集时间}}", note.get("fetched_at", ""))
    result = _safe_replace(result, "{{YYYY-MM-DD HH:MM:SS}}", note.get("fetched_at", ""))
    result = _safe_replace(result, "{{采集模式}}", note.get("fetch_mode", "?"))
    result = _safe_replace(result, "{{图片模式}}", image_mode)

    # 图片清单（v2.0 新增）
    image_listing = _build_image_listing(image_refs, note)
    result = _safe_replace(result, "{{图片清单}}", image_listing)

    return result


# ===== 辅助函数 =====
def _split_to_bullets(desc: str, max_count: int = 5) -> list[str]:
    """把正文拆成 bullet 列表"""
    if not desc:
        return []
    sentences = re.split(r"[。!?\n]+", desc)
    bullets = [s.strip() for s in sentences if s.strip() and len(s.strip()) >= 4]
    return bullets[:max_count]


def _extract_key_paragraph(desc: str, already_quoted: list[str]) -> str:
    """提取一个没被金句引用过的关键段落"""
    if not desc:
        return "（无原文）"
    paragraphs = [p.strip() for p in desc.split("\n") if p.strip()]
    if not paragraphs:
        return "（无原文）"
    longest = max(paragraphs, key=len)
    if longest in already_quoted:
        for p in sorted(paragraphs, key=len, reverse=True):
            if p not in already_quoted:
                return p
    return longest


def _build_image_listing(image_refs: list[dict], note: dict) -> str:
    """生成图片清单（v2.0 新增）"""
    if not image_refs:
        return "（本笔记无图片）"
    lines = []
    for ref in image_refs:
        i = ref["index"]
        local = ref.get("local_path")
        err = ref.get("error", "")
        url = ref.get("url", "")
        if local:
            lines.append(f"- **图片 {i}**：本地 `{local.name}` | 原 URL：[{url[:60]}...]({url})")
        else:
            lines.append(f"- **图片 {i}**：[{url[:60]}...]({url})" + (f" ⚠️ {err}" if err else ""))
    return "\n".join(lines)


def cleanup_unfilled_placeholders(md: str) -> str:
    """
    清理未填充的占位符

    策略：
    - `#{{xxx}}` （未填的标签占位符）：直接删除，避免遗留 #
    - `{{xxx}}` （未填的普通占位符）：替换为 _待填充_
    - 清理连续空行
    """
    # 1. 标签里的占位符：`#{{xxx}}` → 删除整个（含前导 #）
    md = re.sub(r'#\{\{[^}]+\}\}', '', md)
    # 2. 清理连续 # # 模式（未填标签间）
    md = re.sub(r'(#\s+){2,}#?', '', md)
    # 3. 清理行首尾多余的 #
    md = re.sub(r'^[ \t]*#[ \t]*$', '', md, flags=re.MULTILINE)
    # 4. 清理普通占位符
    md = re.sub(r'\{\{[^}]+\}\}', '_待填充_', md)
    # 5. 清理连续空行
    md = re.sub(r'\n{3,}', '\n\n', md)
    # 6. 清理行尾空格
    md = re.sub(r'[ \t]+$', '', md, flags=re.MULTILINE)
    return md


# ===== 失败卡片 =====
def _generate_failure_card(url: str, error: str, output_dir: Path) -> Path:
    """生成抓取失败的说明卡片"""
    output_dir.mkdir(parents=True, exist_ok=True)
    note_id_match = re.search(r'/([a-f0-9]{24})', url)
    note_id = note_id_match.group(1) if note_id_match else "unknown"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.now().strftime("%Y-%m-%d")

    content = f"""# ⚠️ 笔记抓取失败

> **原文链接**：[{url}]({url})
> **尝试时间**：{timestamp}
> **失败原因**：{error}

---

## 抓取失败说明

经过 4 级降级尝试（HTML → API → 降级 → Playwright），均未能成功获取笔记内容。

## 可能原因

- **笔记被作者删除** — 最常见原因
- **笔记被平台下架** — 违规、投诉
- **链接已过期** — 短链长期未访问失效
- **笔记 ID 错误** — 链接本身有误
- **作者设为仅好友可见** — 登录账号无权访问
- **服务被风控** — 同一 IP 短时间内请求过多

## 建议下一步

- [ ] 打开小红书 App，手动访问原链接确认笔记是否还在
- [ ] 如果笔记还在，可能是 cookie 失效或风控，稍后重试
- [ ] 如果链接由 `xiaohongshu-collector` 产出，回到那一步过滤掉

---

## 📎 原始元数据

- **noteId**：`{note_id}`
- **URL**：`{url}`
- **尝试时间**：{timestamp}
- **采集工具**：xiaohongshu-link-to-md v2.0
"""
    output_path = output_dir / f"{date}-FAILED-{note_id[:8]}.md"
    output_path.write_text(content, encoding="utf-8")
    print(f"  💾 失败卡片已保存: {output_path}", file=sys.stderr)
    return output_path


# ===== Playwright L4 兜底 =====
def _try_playwright_l4_fallback(
    url: str,
    note: dict,
    mode: str = "auto",
    with_comments: bool = True,
) -> dict:
    """L1/L2/L3 全部失败时，尝试 Playwright L4 浏览器兜底"""
    note_id = note.get("note_id") or extract_note_id(url) or "unknown"
    print(f"  ⚠️ L1/L2/L3 均失败，尝试 Playwright L4 兜底...", file=sys.stderr)

    try:
        import importlib
        try:
            fetch_note_pw = importlib.import_module("fetch_note_pw")
        except ImportError:
            print(f"  ⚠️ fetch_note_pw.py 未找到，跳过 L4 兜底", file=sys.stderr)
            return note

        if not fetch_note_pw.is_available():
            print(f"  ⚠️ Playwright 未安装，跳过 L4 兜底", file=sys.stderr)
            print(f"     安装方法: pip install playwright playwright-stealth && playwright install chromium", file=sys.stderr)
            return note

        pw_result = asyncio.run(
            fetch_note_pw.fetch_via_playwright(
                url,
                note_id,
                headless=True,
                with_comments=with_comments,
            )
        )

        if pw_result.get("fetch_mode", "").startswith("L4_Playwright_FAILED") or \
           pw_result.get("fetch_mode") in ("L4_NOT_AVAILABLE", "L4_Playwright_NO_DATA"):
            print(f"  ❌ Playwright L4 也失败了: {pw_result.get('error', '未知错误')}", file=sys.stderr)
            return note

        print(f"  ✅ Playwright L4 成功！({pw_result.get('fetch_mode')})", file=sys.stderr)
        return pw_result

    except Exception as e:
        print(f"  ❌ Playwright L4 异常: {type(e).__name__}: {e}", file=sys.stderr)
        return note


# ===== 主入口 =====
def convert(
    url: str,
    output_dir: Path = Path("./xiaohongshu-notes"),
    template: Optional[str] = None,
    mode: str = "auto",
    with_comments: bool = True,
    image_mode: str = "link",
    cache_root: Path = Path(".cache/xiaohongshu-link-to-md"),
) -> Optional[Path]:
    """
    单条 URL → Markdown 文件
    返回生成的文件路径，失败返回 None
    """
    print(f"\n📥 开始处理: {url}", file=sys.stderr)
    print(f"  📷 图片模式: {image_mode}", file=sys.stderr)

    # 1. 抓取
    note = fetch_note.fetch(url, mode=mode, with_comments=with_comments)
    if note.get("fetch_mode") == "L3_FAILED":
        # 尝试 Playwright L4 兜底
        note = _try_playwright_l4_fallback(url, note, mode, with_comments)
        # 如果 L4 也失败，生成失败卡片
        if note.get("fetch_mode") in (
            "L3_FAILED", "L4_Playwright_FAILED",
            "L4_Playwright_NO_DATA", "L4_NOT_AVAILABLE",
        ):
            print(f"  ❌ 完全失败: {note.get('error')}", file=sys.stderr)
            return _generate_failure_card(url, note.get("error", "未知错误"), output_dir)

    print(f"  ✅ 抓取成功（{note.get('fetch_mode')}）", file=sys.stderr)
    print(f"     标题: {note.get('title', '')[:50]}", file=sys.stderr)
    print(f"     作者: {note.get('author', {}).get('nickname', '')}", file=sys.stderr)
    print(f"     互动: 👍 {note.get('interact', {}).get('liked', 0)} | 💬 {len(note.get('comments', []))}", file=sys.stderr)

    # 2. 下载媒体（除非 url 或 none 模式不需要本地文件）
    note_id = note.get("note_id", "unknown")
    media_dir = cache_root / note_id
    image_refs = []

    images_count = len(note.get("images", []))
    has_video = note.get("type") == "video"

    if image_mode in ("link", "embed") and (images_count > 0 or has_video):
        print(f"  ⬇️ 下载媒体到 {media_dir}...", file=sys.stderr)
        try:
            media_result = download_note_media(note, output_dir=cache_root)
            saved_images = media_result.get("image_paths", [])
            saved_video = media_result.get("video_path")
            print(f"     图片: {len(saved_images)}/{images_count} 成功", file=sys.stderr)
            if saved_video:
                print(f"     视频: {saved_video}", file=sys.stderr)
        except Exception as e:
            print(f"     ⚠️ 下载异常: {e}", file=sys.stderr)
            saved_images = []
            saved_video = None
    else:
        saved_images = []
        saved_video = None

    # 3. 选模板
    if template is None:
        template = select_template(note)
    print(f"  📄 模板: {template}.md", file=sys.stderr)

    template_dir = Path(__file__).parent.parent / "templates"
    template_text = load_template(template, template_dir)

    # 4. 渲染图片引用
    output_dir.mkdir(parents=True, exist_ok=True)
    date = (note.get("fetched_at", "")[:10] or datetime.now().strftime("%Y-%m-%d"))
    slug = slugify(note.get("title", "untitled"))
    output_path = output_dir / f"{date}-{slug}.md"
    image_refs = render_image_refs(note, image_mode, media_dir, output_path)

    # 5. 渲染 Markdown
    if template == "full":
        rendered = render_full(note, template_text, image_refs, image_mode)
    else:
        rendered = render_mini(note, template_text, image_refs, image_mode)

    # 6. 清理未填充的占位符
    rendered = cleanup_unfilled_placeholders(rendered)

    # 7. 保存
    output_path.write_text(rendered, encoding="utf-8")
    print(f"  💾 已保存: {output_path}", file=sys.stderr)

    # 8. 报告图片本地路径
    if image_mode in ("link", "embed") and saved_images:
        print(f"  📂 媒体缓存: {media_dir}（含 {len(saved_images)} 张图片）", file=sys.stderr)
        print(f"     不需要图片时可用: --image-mode none", file=sys.stderr)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="小红书链接 → Markdown 一键转换")
    parser.add_argument("input", help="单个 URL 或 URL 列表文件（每行一个）")
    parser.add_argument("--output-dir", "-o", default="./xiaohongshu-notes", help="输出目录")
    parser.add_argument("--mode", choices=["auto", "html", "api"], default="auto", help="抓取模式")
    parser.add_argument("--template", choices=["full", "mini", "auto"], default="auto", help="模板版本")
    parser.add_argument("--no-comments", action="store_true", help="不抓评论")

    # v2.0 新增参数
    parser.add_argument(
        "--image-mode",
        choices=["link", "embed", "url", "none"],
        default="link",
        help="图片处理模式：link(默认，本地链接) | embed(嵌入base64) | url(保留原URL) | none(不放图)",
    )
    parser.add_argument(
        "--cache-dir",
        default="./.cache/xiaohongshu-link-to-md",
        help="媒体缓存根目录（默认 ./.cache/xiaohongshu-link-to-md/）",
    )

    args = parser.parse_args()

    # 判断输入是 URL 还是文件
    input_path = Path(args.input)
    if input_path.exists() and input_path.is_file():
        urls = [line.strip() for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        print(f"📋 批量模式: {len(urls)} 个链接", file=sys.stderr)
    else:
        urls = [args.input]

    success, failed = 0, 0
    for url in urls:
        try:
            output_path = convert(
                url,
                output_dir=Path(args.output_dir),
                template=None if args.template == "auto" else args.template,
                mode=args.mode,
                with_comments=not args.no_comments,
                image_mode=args.image_mode,
                cache_root=Path(args.cache_dir),
            )
            if output_path:
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ 异常: {type(e).__name__}: {e}", file=sys.stderr)
            failed += 1

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"📊 汇总: 成功 {success} / 失败 {failed} / 总 {len(urls)}", file=sys.stderr)


if __name__ == "__main__":
    main()
