#!/usr/bin/env python3
"""
fetch_note.py — 主抓取脚本

决策流程：
  1. L0: 智能选择模式（auto 模式默认 HTML，失败再上 API）
  2. L1 HTML: get_note_by_id_from_html（无 cookie，移动端 UA 已在库内）
  3. L2 API:  get_note_by_id（带 cookie，自动 X-s 签名）
  4. L3 降级: 输出 L1 抓到的部分数据 + 错误说明

用法：
  python fetch_note.py <URL>                           # auto 模式
  python fetch_note.py <URL> --mode html               # 强制 HTML 模式（无 cookie）
  python fetch_note.py <URL> --mode api                # 强制 API 模式（需 cookie）
  python fetch_note.py <URL> --no-comments             # 不抓评论
  python fetch_note.py <URL> --output path/to/note.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from xhs import XhsClient
from xhs.exception import DataFetchError, IPBlockError, SignError

from xiaohongshu_common import (
    cookie_available,
    decide_mode,
    fetch_strategy,
    load_cookie,
    polite_sleep,
    extract_note_id,
)


# ===== 统一输出结构 =====
def _safe_int(value) -> int:
    """安全转换数值，处理千位分隔符（如 "1,700" → 1700）。"""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    # 移除千位分隔符和其他非数字字符（保留负号）
    cleaned = str(value).strip().replace(",", "").replace("，", "")
    try:
        return int(cleaned)
    except (ValueError, TypeError):
        return 0


def _normalize_note(raw: dict, note_id: str, url: str, fetch_mode: str) -> dict:
    """把 xiaohongshu 库返回的 dict 标准化成我们的统一结构

    v2.1 修复：兼容两种数据格式
    - xiaohongshu 库格式：image_list, interact_info, tag_list (snake_case)
    - __SETUP_SERVER_STATE__ 格式：imageList, interactInfo, tagList (camelCase)
    """
    is_video = "video" in raw or raw.get("type") == "video"

    images = []
    # 兼容两种字段名
    img_list = raw.get("imageList") or raw.get("image_list") or []
    for img in img_list:
        # 兼容两种字段名
        info_list = img.get("infoList") or img.get("info_list") or []
        url_default = img.get("urlDefault") or img.get("url_default") or img.get("url", "")
        if info_list:
            # 优先选 WB_DFT scene 的
            url_default = next(
                (i.get("url", "") for i in info_list if i.get("imageScene") == "WB_DFT" or i.get("image_scene") == "WB_DFT"),
                url_default or (info_list[0].get("url", "") if info_list else ""),
            )
        if not url_default and "url" in img:
            url_default = img.get("url", "")
        images.append({
            "url": url_default,
            "width": img.get("width", 0),
            "height": img.get("height", 0),
        })

    video = None
    if is_video:
        v = raw.get("video", {}) or {}
        media = v.get("media", {}) or {}
        stream = media.get("stream", {}) or {}

        # v2.1 修复：masterUrl 可能是字符串或 list
        h264 = stream.get("h264", "")
        if isinstance(h264, dict):
            h264 = h264.get("masterUrl") or h264.get("master_url", "")
        elif isinstance(h264, list) and h264:
            h264 = h264[0].get("masterUrl") if isinstance(h264[0], dict) else h264[0]

        h265 = stream.get("h265", "")
        if isinstance(h265, dict):
            h265 = h265.get("masterUrl") or h265.get("master_url", "")
        elif isinstance(h265, list) and h265:
            h265 = h265[0].get("masterUrl") if isinstance(h265[0], dict) else h265[0]

        # 备选：可能 masterUrl 直接在 video 对象上
        if not h264:
            direct = v.get("masterUrl") or v.get("master_url", "")
            if isinstance(direct, list) and direct:
                h264 = direct[0].get("masterUrl") if isinstance(direct[0], dict) else direct[0]
            elif isinstance(direct, str):
                h264 = direct

        # v2.1 修复：duration 在 stream.h264[0].duration 里
        duration_ms = v.get("duration") or 0
        if not duration_ms and isinstance(stream.get("h264"), list) and stream["h264"]:
            duration_ms = stream["h264"][0].get("duration") or 0
        elif not duration_ms and isinstance(stream.get("h264"), dict):
            duration_ms = stream["h264"].get("duration") or 0

        video = {
            "master_url": h264 or h265,
            "backup_url": h265 if h264 else "",
            "duration": (duration_ms or 0) / 1000,  # ms → s
            "width": v.get("width", 0),
            "height": v.get("height", 0),
            "cover": (v.get("cover", {}) or {}).get("urlDefault") or (v.get("cover", {}) or {}).get("url_default", ""),
        }

    # 兼容两种字段名
    interact = raw.get("interactInfo") or raw.get("interact_info") or {}
    user = raw.get("user", {}) or {}

    # 标签也兼容两种字段名
    tags_raw = raw.get("tagList") or raw.get("tag_list") or []
    tags = [t.get("name", "") for t in tags_raw if t.get("name")]

    # 用 noteId 兜底（如果 raw 里没给）
    actual_note_id = raw.get("noteId") or raw.get("note_id") or note_id

    # v2.1 修复：user 字段可能是 nickName（新版） / nickname（旧版）
    user_nickname = user.get("nickName") or user.get("nickname", "")

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
            "collected": _safe_int(interact.get("collectedCount") or interact.get("collected_count") or 0),
            "comment": _safe_int(interact.get("commentCount") or interact.get("comment_count") or 0),
            "share": _safe_int(interact.get("shareCount") or interact.get("share_count") or 0),
        },
        "publish_time": _format_time(raw.get("time")),
        "tags": tags,
        "images": images,
        "video": video,
    }


def _format_time(ts) -> str:
    """把小红书时间戳（毫秒）格式化为字符串"""
    if not ts:
        return ""
    try:
        from datetime import datetime
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


# ===== 三级抓取 =====
import requests as _requests
import re as _re


# 多个备选路径（按成功率从高到低）
# v2.0 重要修复：必须带 Accept: */* 头，否则会被 302 到 404 页面
_HTML_FETCH_VARIANTS = [
    # 1. iOS Safari + /discovery/item/ + xsec_token （实测唯一能拿 200 的）
    {
        "name": "ios_discovery_with_token",
        "url_template": "https://www.xiaohongshu.com/discovery/item/{note_id}?xsec_token={xsec_token}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": "https://www.xiaohongshu.com/",
        },
    },
    # 2. iOS Safari + /discovery/item/ 无 token
    {
        "name": "ios_discovery_no_token",
        "url_template": "https://www.xiaohongshu.com/discovery/item/{note_id}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": "https://www.xiaohongshu.com/",
        },
    },
    # 3. iOS Safari + /explore/
    {
        "name": "ios_explore",
        "url_template": "https://www.xiaohongshu.com/explore/{note_id}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": "https://www.xiaohongshu.com/",
        },
    },
    # 4. Android + /explore/
    {
        "name": "android_explore",
        "url_template": "https://www.xiaohongshu.com/explore/{note_id}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.xiaohongshu.com/",
        },
    },
    # 5. Desktop + /explore/ (xiaohongshu 库默认路径)
    {
        "name": "desktop_explore",
        "url_template": "https://www.xiaohongshu.com/explore/{note_id}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.xiaohongshu.com/",
        },
    },
]


def _extract_xsec_token(url: str) -> str:
    """从 URL 里提取 xsec_token 参数"""
    from urllib.parse import urlparse, parse_qs
    return parse_qs(urlparse(url).query).get("xsec_token", [""])[0]


def _try_fetch_html_once(note_id: str, url: str, variant: dict, xsec_token: str = "") -> Optional[dict]:
    """试一次 HTML 抓取，返回 None 表示失败"""
    target_url = variant["url_template"].format(note_id=note_id, xsec_token=xsec_token)
    try:
        # v2.0 修复：allow_redirects=True（之前是 False，导致 302 直接失败）
        # 注意：虽然 302 在 v1 是失败标记，但带 Accept: */* 后大部分情况直接 200
        resp = _requests.get(
            target_url,
            headers=variant["headers"],
            timeout=15,
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return None
        # 检查是否被 redirect 到 404 页面
        if "/404/" in resp.url or "404" in resp.url:
            return None

        return _extract_note_from_html(resp.text, note_id)
    except Exception:
        return None


def _extract_note_from_html(html: str, note_id: str) -> Optional[dict]:
    """从 HTML 字符串中提取笔记数据
    v2.1 重构：从 _try_fetch_html_once 抽出来，供离线模式和在线模式共用
    """
    import json

    def _try_extract_from_script(script_name: str, data_extractor) -> dict | None:
        """从指定 script 块提取数据"""
        start_match = _re.search(rf"window\.{script_name}\s*=\s*", html)
        if not start_match:
            return None
        start = start_match.end()
        end_match = _re.search(r"\}\s*</script>", html[start:])
        if not end_match:
            return None
        end = start + end_match.start() + 1

        state = html[start:end].rstrip().rstrip(";").rstrip()
        # JS 特有的 undefined / NaN 转成 JSON 兼容的 null
        state = _re.sub(r":\s*undefined\b", ": null", state)
        state = _re.sub(r",\s*undefined\b", ", null", state)
        state = _re.sub(r"\[\s*undefined\b", "[ null", state)
        state = _re.sub(r":\s*NaN\b", ": null", state)

        try:
            data = json.loads(state)
        except json.JSONDecodeError:
            return None

        return data_extractor(data)

    # 1. 优先从 __SETUP_SERVER_STATE__ 拿（新版页面 + 服务端渲染）
    def from_setup_state(data):
        page_data = data.get("LAUNCHER_SSR_STORE_PAGE_DATA", {})
        note_data = page_data.get("noteData", {})
        if not note_data or not note_data.get("noteId"):
            return None
        return note_data

    result = _try_extract_from_script("__SETUP_SERVER_STATE__", from_setup_state)
    if result:
        return result

    # 2. 回退到 __INITIAL_STATE__（旧版页面）
    def from_initial_state(data):
        note_map = (
            data.get("note", {}).get("noteDetailMap", {})  # 驼峰
            or data.get("note", {}).get("note_detail_map", {})  # 下划线
        )
        if note_id not in note_map:
            return None
        return note_map[note_id].get("note", {})

    result = _try_extract_from_script("__INITIAL_STATE__", from_initial_state)
    return result


def fetch_via_html(note_id: str, url: str) -> dict:
    """
    L1: HTML 路径（无 cookie）

    策略：依次尝试多个 UA/路径变体，碰到一个成功就返回
    v2.1 修复：变体间加 polite sleep，避免被 xiaohongshu 限流

    支持 HTML 缓存模式：设置 XIAOHONGSHU_HTML_CACHE 环境变量为 HTML 文件路径，
    从文件读取 HTML 而不是联网拉取。用于调试 / 重跑同一笔记。
    """
    import os as _os

    # v2.1 新增：支持从缓存文件读取（避开限流）
    html_cache = _os.environ.get("XIAOHONGSHU_HTML_CACHE")
    if html_cache and Path(html_cache).exists():
        raw = _extract_note_from_html(Path(html_cache).read_text(encoding='utf-8'), note_id)
        if raw:
            return _normalize_note(raw, note_id, url, fetch_mode="L1_HTML_from_cache")
        return None

    xsec_token = _extract_xsec_token(url)

    for i, variant in enumerate(_HTML_FETCH_VARIANTS):
        # 如果需要 xsec_token 但没拿到，跳过这个变体
        if "{xsec_token}" in variant["url_template"] and not xsec_token:
            continue

        # 变体间礼貌延迟（1.5-2.5s），避免被 xiaohongshu 限流
        if i > 0:
            polite_sleep(1.5)

        raw = _try_fetch_html_once(note_id, url, variant, xsec_token)
        if raw:
            return _normalize_note(raw, note_id, url, fetch_mode=f"L1_HTML_{variant['name']}")

    # 所有变体都失败，尝试 xiaohongshu 库（作为最后兑底，可能拿到不同格式的数据）
    try:
        client = XhsClient()
        raw = client.get_note_by_id_from_html(note_id)
        return _normalize_note(raw, note_id, url, fetch_mode="L1_HTML_xhs_lib_fallback")
    except Exception:
        pass

    # 全失败 → 抛错
    raise DataFetchError(f"所有 HTML 变体都未能成功获取 {note_id}（可能笔记对当前 IP 不可见）")


def fetch_via_api(note_id: str, url: str, cookie: str) -> dict:
    """L2: API 路径（带 cookie，X-s 签名由 xiaohongshu 库自动生成）"""
    client = XhsClient(cookie=cookie)
    raw = client.get_note_by_id(note_id)
    return _normalize_note(raw, note_id, url, fetch_mode="L2_API")


def fetch_comments(note_id: str, cookie: str, max_count: int = 30) -> list:
    """带 cookie 时拿完整评论"""
    client = XhsClient(cookie=cookie)
    try:
        all_comments = client.get_note_all_comments(note_id, crawl_interval=1)
    except Exception as e:
        print(f"  ⚠️ 评论抓取失败: {e}", file=sys.stderr)
        return []

    comments = []
    for c in (all_comments or [])[:max_count]:
        comments.append({
            "user": (c.get("user_info") or {}).get("nickname", "匿名"),
            "content": c.get("content", ""),
            "liked": c.get("like_count", 0),
            "time": _format_time(c.get("create_time")),
            "replies": [
                {
                    "user": (r.get("user_info") or {}).get("nickname", "匿名"),
                    "content": r.get("content", ""),
                }
                for r in (c.get("sub_comments") or [])
            ],
        })
    return comments


# ===== 主入口 =====
def fetch(
    url: str,
    mode: str = "auto",
    with_comments: bool = True,
    max_comments: int = 30,
) -> dict:
    """
    主抓取函数

    v2.0 改进：
    - 与 decide_mode() 行为对齐：auto 模式永远先 L1 HTML（不依赖 cookie）
    - 失败后才 fallback 到 L2 API（需要 cookie）
    - 增加 diagnostics 字段，记录每条路径的尝试情况

    Args:
        url: 小红书笔记 URL
        mode: "auto" | "html" | "api"
        with_comments: 是否抓评论
        max_comments: 评论最大数

    Returns:
        标准化的笔记 dict（含 fetch_mode 标识走的哪条路径 + diagnostics 诊断信息）
    """
    import time as _time
    started_at = _time.time()
    note_id = extract_note_id(url)
    if not note_id:
        raise ValueError(f"无法从 URL 提取 noteId: {url}")

    # 决策第一步走哪条路径（v2.0 修复：decide_mode 与实际行为对齐）
    first_step = decide_mode(mode)
    print(f"  📊 策略: {fetch_strategy(first_step)}（第一步）", file=sys.stderr)

    cookie = load_cookie() if cookie_available() else None
    last_error = None
    diagnostics = {
        "tried_paths": [],
        "ua_variants_tried": [],
        "cookie_present": cookie is not None,
        "xsec_token_in_url": bool(_extract_xsec_token(url)),
    }

    # ===== L1: HTML 路径 =====
    if first_step == "html":
        diagnostics["tried_paths"].append("L1_HTML")
        try:
            print(f"  → 尝试 L1 (HTML 模式，无需 cookie)...", file=sys.stderr)
            result = fetch_via_html(note_id, url)
            result["diagnostics"] = {**diagnostics, "html_success": True, "duration_ms": int((_time.time() - started_at) * 1000)}

            # 拿到数据后，尝试补充评论（如果有 cookie 且需要）
            if with_comments and cookie:
                try:
                    polite_sleep(1.0)
                    result["comments"] = fetch_comments(note_id, cookie, max_comments)
                    if result.get("fetch_mode", "").startswith("L1_HTML"):
                        result["fetch_mode"] = "L1_HTML+L2_API_COMMENTS"
                except Exception as e:
                    result["comments"] = []
                    result["fetch_mode_note"] = f"评论抓取失败: {e}"
            else:
                result["comments"] = []  # 无 cookie 时评论留空
                if not cookie:
                    result["fetch_mode_note"] = "无 cookie，未抓取评论（HTML 模式仅含 0-3 条预览，App 端查看完整）"
            return result
        except (DataFetchError, IPBlockError, SignError) as e:
            last_error = e
            print(f"  ❌ L1 失败: {e}", file=sys.stderr)
        except Exception as e:
            last_error = e
            print(f"  ❌ L1 异常: {type(e).__name__}: {e}", file=sys.stderr)

        # L1 失败 → 看要不要 fallback 到 L2
        if mode == "html":
            # 用户强制 HTML 模式，不 fallback
            pass
        else:
            diagnostics["tried_paths"].append("L2_API_fallback")
            # auto 模式且 L1 失败时，如果有 cookie 才会试 L2
            if cookie:
                try:
                    print(f"  → L1 失败，fallback 到 L2 (API 模式，带 cookie)...", file=sys.stderr)
                    result = fetch_via_api(note_id, url, cookie)
                    if with_comments:
                        polite_sleep(1.0)
                        try:
                            result["comments"] = fetch_comments(note_id, cookie, max_comments)
                        except Exception as e:
                            result["comments"] = []
                            result["fetch_mode_note"] = f"评论抓取失败: {e}"
                    result["diagnostics"] = {**diagnostics, "l2_fallback_used": True, "duration_ms": int((_time.time() - started_at) * 1000)}
                    return result
                except (DataFetchError, IPBlockError, SignError) as e:
                    last_error = e
                    print(f"  ❌ L2 失败: {e}", file=sys.stderr)
                except Exception as e:
                    last_error = e
                    print(f"  ❌ L2 异常: {type(e).__name__}: {e}", file=sys.stderr)
            else:
                print(f"  ⚠️ 无 cookie 可 fallback 到 L2", file=sys.stderr)

    # ===== L2: API 路径（用户强制 api 模式时）=====
    if first_step == "api":
        if not cookie:
            raise RuntimeError("API 模式需要 cookie，但未配置。请配置 XIAOHONGSHU_COOKIE 环境变量或 ~/.config/xiaohongshu-link-to-md/cookie")
        diagnostics["tried_paths"].append("L2_API")
        try:
            print(f"  → 尝试 L2 (API 模式，带 cookie)...", file=sys.stderr)
            result = fetch_via_api(note_id, url, cookie)
            if with_comments:
                polite_sleep(1.0)
                try:
                    result["comments"] = fetch_comments(note_id, cookie, max_comments)
                    result["fetch_mode"] = "L2_API"
                except Exception as e:
                    result["comments"] = []
                    result["fetch_mode_note"] = f"笔记 OK 但评论抓取失败: {e}"
            result["diagnostics"] = {**diagnostics, "duration_ms": int((_time.time() - started_at) * 1000)}
            return result
        except (DataFetchError, IPBlockError, SignError) as e:
            last_error = e
            print(f"  ❌ L2 失败: {e}", file=sys.stderr)
        except Exception as e:
            last_error = e
            print(f"  ❌ L2 异常: {type(e).__name__}: {e}", file=sys.stderr)

    # ===== L3: 完全失败 — 但仍返回一个最小结构体（让调用方决定是否生成失败卡片）=====
    return {
        "note_id": note_id,
        "url": url,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fetch_mode": "L3_FAILED",
        "error": f"L1 和 L2 都失败: {last_error}",
        "diagnostics": {**diagnostics, "duration_ms": int((_time.time() - started_at) * 1000)},
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


# ===== CLI =====
def main():
    parser = argparse.ArgumentParser(description="抓取小红书笔记（智能选择 HTML/API 模式）")
    parser.add_argument("url", help="小红书笔记链接")
    parser.add_argument("--mode", choices=["auto", "html", "api"], default="auto",
                        help="抓取模式：auto (默认，HTML 优先失败上 API) | html (强制无 cookie) | api (强制带 cookie)")
    parser.add_argument("--no-comments", action="store_true", help="不抓评论")
    parser.add_argument("--max-comments", type=int, default=30, help="最多抓多少条评论")
    parser.add_argument("--output", "-o", help="输出文件路径（默认 stdout）")

    args = parser.parse_args()

    try:
        result = fetch(
            args.url,
            mode=args.mode,
            with_comments=not args.no_comments,
            max_comments=args.max_comments,
        )
        output = json.dumps(result, ensure_ascii=False, indent=2)

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"\n✅ 已保存到 {args.output}", file=sys.stderr)
            print(f"   fetch_mode: {result.get('fetch_mode', '?')}", file=sys.stderr)
        else:
            print(output)
    except Exception as e:
        print(f"\n❌ 抓取失败: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
