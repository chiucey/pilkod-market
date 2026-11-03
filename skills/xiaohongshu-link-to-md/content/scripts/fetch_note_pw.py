#!/usr/bin/env python3
"""
fetch_note_pw.py — Playwright L4 浏览器兜底抓取

当 L1(HTML) / L2(API) / L3(降级) 全部失败后，使用 Playwright 真实浏览器
作为最后的 fallback。

设计原则：
  - 可选依赖：Playwright + playwright-stealth 未安装时不报错，静默跳过
  - 反检测优先：stealth 补丁 + 移动端 UA + 人类行为延迟
  - 数据兼容：输出格式与 fetch_note.py 的 fetch() 完全一致
  - 最小侵入：独立模块，不修改 fetch_note.py

核心函数：
  fetch_via_playwright(url, note_id) → dict  (标准笔记对象)
  is_available() → bool                       (检查 Playwright 是否可用)

Usage:
  python scripts/fetch_note_pw.py "https://www.xiaohongshu.com/explore/{noteId}"

环境要求:
  pip install playwright playwright-stealth
  playwright install chromium
"""

from __future__ import annotations

import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# 把 scripts/ 目录加入 sys.path（从 xiaohongshu_to_md.py 调用时需要）
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def is_available() -> bool:
    """检查 Playwright 和 playwright_stealth 是否可用。"""
    try:
        import playwright  # noqa: F401
        import playwright_stealth  # noqa: F401
        return True
    except ImportError:
        return False


# ---- 常量 ----
# 移动端 User-Agent 列表（随机选择，降低指纹一致性）
_MOBILE_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
]

VIEWPORT = {"width": 390, "height": 844}  # iPhone 14

# 抓取超时设置
NAVIGATION_TIMEOUT = 30000    # 页面加载超时 (ms)
STATE_EXTRACT_TIMEOUT = 15000  # 提取 __INITIAL_STATE__ 超时 (ms)

# 评论选择器（多种备选）
_COMMENT_SELECTORS = [
    ".comment-item",
    ".commentItem",
    '[class*="comment"][class*="item"]',
    '[class*="CommentItem"]',
]


# ---- 数据标准化（与 fetch_note.py 格式完全一致）----
def _safe_int(value) -> int:
    """安全转换数值，处理千位分隔符（如 "1,700" → 1700）。"""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    cleaned = str(value).strip().replace(",", "").replace("，", "")
    try:
        return int(cleaned)
    except (ValueError, TypeError):
        return 0


def _normalize_note_pw(raw: dict, note_id: str, url: str, fetch_mode: str) -> dict:
    """把 Playwright 提取的原始数据标准化，与 fetch_note.py 格式一致。

    兼容两种数据格式：
    - __SETUP_SERVER_STATE__: imageList, interactInfo, tagList (camelCase)
    - __INITIAL_STATE__: image_list, interact_info, tag_list (snake_case)
    """
    is_video = "video" in raw or raw.get("type") == "video"

    # 图片
    images = []
    img_list = raw.get("imageList") or raw.get("image_list") or []
    for img in img_list:
        info_list = img.get("infoList") or img.get("info_list") or []
        url_default = img.get("urlDefault") or img.get("url_default") or img.get("url", "")
        if info_list:
            url_default = next(
                (
                    i.get("url", "")
                    for i in info_list
                    if i.get("imageScene") == "WB_DFT"
                    or i.get("image_scene") == "WB_DFT"
                ),
                url_default or (info_list[0].get("url", "") if info_list else ""),
            )
        if not url_default and "url" in img:
            url_default = img.get("url", "")
        images.append(
            {"url": url_default, "width": img.get("width", 0), "height": img.get("height", 0)}
        )

    # 视频
    video = None
    if is_video:
        v = raw.get("video", {}) or {}
        media = v.get("media", {}) or {}
        stream = media.get("stream", {}) or {}

        h264 = stream.get("h264", "")
        if isinstance(h264, dict):
            h264 = h264.get("masterUrl") or h264.get("master_url", "")
        elif isinstance(h264, list) and h264:
            h264 = (
                h264[0].get("masterUrl")
                if isinstance(h264[0], dict)
                else h264[0]
            )

        h265 = stream.get("h265", "")
        if isinstance(h265, dict):
            h265 = h265.get("masterUrl") or h265.get("master_url", "")
        elif isinstance(h265, list) and h265:
            h265 = (
                h265[0].get("masterUrl")
                if isinstance(h265[0], dict)
                else h265[0]
            )

        if not h264:
            direct = v.get("masterUrl") or v.get("master_url", "")
            if isinstance(direct, list) and direct:
                h264 = (
                    direct[0].get("masterUrl")
                    if isinstance(direct[0], dict)
                    else direct[0]
                )
            elif isinstance(direct, str):
                h264 = direct

        duration_ms = v.get("duration") or 0
        if not duration_ms and isinstance(stream.get("h264"), list) and stream["h264"]:
            duration_ms = stream["h264"][0].get("duration") or 0
        elif not duration_ms and isinstance(stream.get("h264"), dict):
            duration_ms = stream["h264"].get("duration") or 0

        video = {
            "master_url": h264 or h265,
            "backup_url": h265 if h264 else "",
            "duration": (duration_ms or 0) / 1000,
            "width": v.get("width", 0),
            "height": v.get("height", 0),
            "cover": (
                (v.get("cover", {}) or {}).get("urlDefault")
                or (v.get("cover", {}) or {}).get("url_default", "")
            ),
        }

    # 互动数据
    interact = raw.get("interactInfo") or raw.get("interact_info") or {}
    user = raw.get("user", {}) or {}

    # 标签
    tags_raw = raw.get("tagList") or raw.get("tag_list") or []
    tags = [t.get("name", "") for t in tags_raw if t.get("name")]

    actual_note_id = raw.get("noteId") or raw.get("note_id") or note_id
    user_nickname = user.get("nickName") or user.get("nickname", "")

    # 时间格式化
    ts = raw.get("time")
    publish_time = ""
    if ts:
        try:
            publish_time = datetime.fromtimestamp(ts / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception:
            publish_time = str(ts)

    return {
        "note_id": actual_note_id,
        "url": url,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fetch_mode": fetch_mode,
        "title": raw.get("title", ""),
        "desc": raw.get("desc", ""),
        "type": "video" if is_video else "image-text",
        "author": {
            "nickname": user_nickname,
            "user_id": user.get("userId") or user.get("user_id", ""),
            "avatar": user.get("avatar", ""),
        },
        "interact": {
            "liked": _safe_int(interact.get("likedCount") or interact.get("liked_count") or 0),
            "collected": _safe_int(
                interact.get("collectedCount") or interact.get("collected_count") or 0
            ),
            "comment": _safe_int(
                interact.get("commentCount") or interact.get("comment_count") or 0
            ),
            "share": _safe_int(interact.get("shareCount") or interact.get("share_count") or 0),
        },
        "publish_time": publish_time,
        "tags": tags,
        "images": images,
        "video": video,
    }


# ---- 核心抓取逻辑 ----
async def _extract_note_from_page(page, note_id: str) -> dict | None:
    """从已渲染的页面中提取笔记原始数据。"""
    import asyncio

    try:
        await page.wait_for_load_state("networkidle", timeout=STATE_EXTRACT_TIMEOUT)
    except Exception:
        pass

    # 方式 1: __SETUP_SERVER_STATE__（新版页面）
    result = await page.evaluate(
        """() => {
        try {
            const s = window.__SETUP_SERVER_STATE__;
            if (s) {
                const pd = s.LAUNCHER_SSR_STORE_PAGE_DATA;
                if (pd && pd.noteData && pd.noteData.noteId) return pd.noteData;
            }
        } catch(e) {}
        return null;
    }"""
    )
    if result:
        return result

    # 方式 2: __INITIAL_STATE__（旧版页面）
    result = await page.evaluate(
        """() => {
        try {
            const s = window.__INITIAL_STATE__;
            if (s && s.note) {
                const map = s.note.noteDetailMap || s.note.note_detail_map;
                return map || null;
            }
        } catch(e) {}
        return null;
    }"""
    )
    if result:
        # result 是 noteDetailMap，按 note_id 索引
        if isinstance(result, dict) and note_id in result:
            note_entry = result[note_id]
            if isinstance(note_entry, dict):
                return note_entry.get("note", note_entry)
        return result

    return None


async def _extract_comments_from_page(page, max_comments: int = 30) -> list[dict]:
    """从页面 DOM 中提取评论数据。"""
    import asyncio

    comments = []
    for scroll_attempt in range(5):
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # 尝试多种选择器
        for selector in _COMMENT_SELECTORS:
            try:
                new_comments = await page.evaluate(
                    f"""(selector) => {{
                    const items = document.querySelectorAll(selector);
                    const results = [];
                    items.forEach(el => {{
                        const userEl = el.querySelector('[class*="nickname"], [class*="Nickname"], [class*="name"], [class*="author"]');
                        const contentEl = el.querySelector('[class*="content"], [class*="Content"], [class*="text"]');
                        const likeEl = el.querySelector('[class*="like"], [class*="Like"]');
                        const user = userEl?.textContent?.trim() || '匿名';
                        const content = contentEl?.textContent?.trim() || '';
                        const liked = parseInt(likeEl?.textContent || '0', 10) || 0;
                        if (content) results.push({{ user, content, liked }});
                    }});
                    return results;
                }}""",
                    selector,
                )
                if new_comments:
                    for c in new_comments:
                        if c not in comments:
                            comments.append(c)
            except Exception:
                continue

        if len(comments) >= max_comments:
            break

        # 向下滚动加载更多
        try:
            await page.mouse.wheel(0, random.randint(300, 600))
        except Exception:
            pass

    return comments[:max_comments]


async def fetch_via_playwright(
    url: str,
    note_id: str,
    headless: bool = True,
    with_comments: bool = True,
    max_comments: int = 30,
) -> dict:
    """Playwright L4 兜底抓取。

    Args:
        url: 小红书笔记完整 URL
        note_id: 已解析的 24 位 hex 笔记 ID
        headless: 是否无头模式（默认 True）
        with_comments: 是否提取评论
        max_comments: 最大评论数

    Returns:
        标准化的笔记 dict（与 fetch_note.fetch() 格式一致），
        失败时返回 fetch_mode="L4_Playwright_FAILED"。
    """
    import asyncio

    started_at = time.time()

    try:
        from playwright.async_api import async_playwright
        from playwright_stealth import stealth_async
    except ImportError:
        return {
            "note_id": note_id,
            "url": url,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fetch_mode": "L4_NOT_AVAILABLE",
            "error": "Playwright 或 playwright-stealth 未安装。请运行: pip install playwright playwright-stealth && playwright install chromium",
            "diagnostics": {
                "tried_paths": ["L4_Playwright"],
                "error_type": "ImportError",
            },
            "title": "",
            "desc": "",
            "type": "unknown",
            "author": {"nickname": "", "user_id": "", "avatar": ""},
            "interact": {"liked": 0, "collected": 0, "comment": 0, "share": 0},
            "publish_time": "",
            "tags": [],
            "images": [],
            "video": None,
            "comments": [],
        }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
            )

            ua = random.choice(_MOBILE_USER_AGENTS)
            context = await browser.new_context(
                viewport=VIEWPORT,
                user_agent=ua,
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
            )

            page = await context.new_page()

            # 注入 stealth 反检测补丁
            try:
                await stealth_async(page)
            except Exception:
                pass  # stealth 失败不阻塞

            # 导航到笔记页
            explore_url = f"https://www.xiaohongshu.com/explore/{note_id}"
            print(f"  🖥️ Playwright L4: 导航到 {explore_url}", file=sys.stderr)

            try:
                await page.goto(
                    explore_url,
                    wait_until="domcontentloaded",
                    timeout=NAVIGATION_TIMEOUT,
                )
            except Exception as e:
                print(f"  ⚠️ 页面导航超时: {e}", file=sys.stderr)

            # 人类行为延迟
            await asyncio.sleep(random.uniform(2.0, 4.0))

            # 提取笔记数据
            raw = await _extract_note_from_page(page, note_id)

            if raw:
                fetch_mode = "L4_Playwright"
                result = _normalize_note_pw(raw, note_id, url, fetch_mode)
            else:
                result = {
                    "note_id": note_id,
                    "url": url,
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fetch_mode": "L4_Playwright_NO_DATA",
                    "error": "Playwright 成功加载页面但无法提取笔记数据（页面可能被拦截或已删除）",
                    "diagnostics": {
                        "tried_paths": ["L4_Playwright"],
                        "ua_used": ua,
                        "duration_ms": int((time.time() - started_at) * 1000),
                    },
                    "title": "",
                    "desc": "",
                    "type": "unknown",
                    "author": {"nickname": "", "user_id": "", "avatar": ""},
                    "interact": {"liked": 0, "collected": 0, "comment": 0, "share": 0},
                    "publish_time": "",
                    "tags": [],
                    "images": [],
                    "video": None,
                    "comments": [],
                }

            # 提取评论
            if with_comments and raw:
                await asyncio.sleep(random.uniform(1.0, 2.0))
                try:
                    result["comments"] = await _extract_comments_from_page(
                        page, max_comments
                    )
                except Exception as e:
                    result["comments"] = []
                    result["fetch_mode_note"] = f"Playwright 评论提取失败: {e}"

            # 添加诊断信息
            result.setdefault("diagnostics", {})
            result["diagnostics"].update(
                {
                    "tried_paths": result.get("diagnostics", {}).get(
                        "tried_paths", []
                    )
                    + ["L4_Playwright"],
                    "ua_used": ua,
                    "duration_ms": int((time.time() - started_at) * 1000),
                    "playwright_success": raw is not None,
                }
            )

            await browser.close()
            return result

    except Exception as e:
        return {
            "note_id": note_id,
            "url": url,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fetch_mode": "L4_Playwright_FAILED",
            "error": f"Playwright L4 异常: {type(e).__name__}: {e}",
            "diagnostics": {
                "tried_paths": ["L4_Playwright"],
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration_ms": int((time.time() - started_at) * 1000),
            },
            "title": "",
            "desc": "",
            "type": "unknown",
            "author": {"nickname": "", "user_id": "", "avatar": ""},
            "interact": {"liked": 0, "collected": 0, "comment": 0, "share": 0},
            "publish_time": "",
            "tags": [],
            "images": [],
            "video": None,
            "comments": [],
        }


# ---- CLI ----
async def _main_async():
    import argparse

    parser = argparse.ArgumentParser(
        description="Playwright L4 兜底：小红书笔记抓取"
    )
    parser.add_argument("url", help="小红书笔记 URL")
    parser.add_argument(
        "--no-comments", action="store_true", help="不提取评论"
    )
    parser.add_argument(
        "--headless", action="store_true", default=True, help="无头模式（默认）"
    )
    parser.add_argument(
        "--no-headless", action="store_true", help="显示浏览器窗口"
    )
    parser.add_argument("--output", "-o", help="输出 JSON 文件路径")

    args = parser.parse_args()

    # 提取 note_id
    match = re.search(r"/(?:explore|discovery/item)/([a-f0-9]{24})", args.url)
    if not match:
        print("❌ 无法从 URL 提取 noteId", file=sys.stderr)
        sys.exit(1)
    note_id = match.group(1)

    headless = not args.no_headless

    result = await fetch_via_playwright(
        args.url,
        note_id,
        headless=headless,
        with_comments=not args.no_comments,
    )

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 已保存到 {args.output}", file=sys.stderr)
    else:
        print(output)

    # 根据 fetch_mode 决定退出码
    if result.get("fetch_mode", "").startswith("L4_Playwright_FAILED"):
        sys.exit(1)
    elif result.get("fetch_mode") in ("L4_NOT_AVAILABLE", "L4_Playwright_NO_DATA"):
        sys.exit(2)


def main():
    import asyncio

    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
