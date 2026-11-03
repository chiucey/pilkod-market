"""
download_media.py — 下载小红书视频 / 图片到本地

v2.0 改进：
- 新增重试逻辑（指数退避，最多 3 次）
- 强制 Referer header（xhscdn CDN 必需）
- 友好的进度报告
- 返回结构化的成功/失败清单

用法：
  python download_media.py <noteId> --note-json path/to/note.json
  python download_media.py <noteId> --note-json path/to/note.json --output-dir .cache/xiaohongshu
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

from xiaohongshu_common import polite_sleep  # noqa


DEFAULT_CACHE_DIR = Path(".cache/xiaohongshu-link-to-md")
CHUNK_SIZE = 1024 * 64  # 64KB
MAX_RETRIES = 3


def download_file(
    url: str,
    dest: Path,
    headers: Optional[dict] = None,
    timeout: int = 60,
    max_retries: int = MAX_RETRIES,
) -> Path:
    """
    流式下载文件，支持断点续传 + 指数退避重试

    Args:
        url: 文件 URL
        dest: 保存路径（父目录会自动创建）
        headers: 请求头（默认会注入 xiaohongshu Referer）
        timeout: 超时秒数
        max_retries: 最大重试次数

    Returns:
        实际保存的 Path
    """
    dest.parent.mkdir(parents=True, exist_ok=True)

    # 强制注入 xiaohongshu Referer（xhscdn CDN 必需）
    req_headers = {
        "Referer": "https://www.xiaohongshu.com/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    }
    if headers:
        req_headers.update(headers)

    last_error = None
    for attempt in range(max_retries):
        try:
            # 断点续传：检查已有大小
            mode = "wb"
            existing_size = 0
            if dest.exists() and attempt == 0:
                existing_size = dest.stat().st_size
                if existing_size > 0:
                    req_headers["Range"] = f"bytes={existing_size}-"
                    mode = "ab"

            with requests.get(url, headers=req_headers, stream=True, timeout=timeout) as resp:
                # v2.1 修复：416 Range Not Satisfiable → 文件已完整下载
                if resp.status_code == 416 and dest.exists():
                    return dest
                resp.raise_for_status()

                # 服务端不支持断点续传 → 重新下载
                if resp.status_code == 200 and existing_size > 0 and mode == "ab":
                    existing_size = 0
                    mode = "wb"

                with open(dest, mode) as f:
                    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
            return dest  # 成功

        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            last_error = e
            if attempt < max_retries - 1:
                # 指数退避：1s, 2s, 4s
                wait = 2 ** attempt
                print(f"     ⚠️ 重试 {attempt + 1}/{max_retries}（{wait}s 后）：{type(e).__name__}: {e}", file=sys.stderr)
                time.sleep(wait)
        except Exception as e:
            last_error = e
            break  # 非网络错误，不重试

    # 全部重试失败
    raise RuntimeError(f"下载失败（已重试 {max_retries} 次）: {last_error}")


def download_note_media(note: dict, output_dir: Path = DEFAULT_CACHE_DIR) -> dict:
    """
    根据 fetch_note.py 输出的 JSON，下载所有媒体

    Returns:
        {
          "video_path": "/path/to/video.mp4",
          "image_paths": ["/path/to/img1.jpg", ...],
          "failed": [{"type": "video", "url": "...", "error": "..."}],
          "stats": {"video_ok": bool, "images_total": N, "images_ok": M}
        }
    """
    note_id = note["note_id"]
    work_dir = output_dir / note_id
    work_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "video_path": None,
        "image_paths": [],
        "failed": [],
        "stats": {"video_ok": False, "images_total": 0, "images_ok": 0},
    }

    # 1. 下载视频
    video = note.get("video")
    if video:
        # v2.1 修复：master_url 可能是字符串或 list（多个码率）
        master_url = video.get("master_url")
        if isinstance(master_url, list):
            # 取第一个的 masterUrl
            if master_url and isinstance(master_url[0], dict):
                master_url = master_url[0].get("masterUrl") or master_url[0].get("master_url")
            else:
                master_url = master_url[0] if master_url else None
        if master_url:
            try:
                ext = ".mp4"
                dest = work_dir / f"video{ext}"
                download_file(master_url, dest)
                result["video_path"] = str(dest)
                result["stats"]["video_ok"] = True
                print(f"     ✅ 视频: {dest.name}", file=sys.stderr)
            except Exception as e:
                print(f"     ❌ 视频失败: {e}", file=sys.stderr)
                result["failed"].append({"type": "video", "url": master_url, "error": str(e)})
        else:
            print(f"     ⊙ 无视频 URL", file=sys.stderr)
    else:
        print(f"     ⊙ 无视频", file=sys.stderr)

    # 2. 下载图片
    images = note.get("images", [])
    result["stats"]["images_total"] = len(images)

    if not images:
        print(f"     ⊙ 无图片", file=sys.stderr)
        return result

    print(f"     ⬇️ 下载 {len(images)} 张图片...", file=sys.stderr)
    for idx, img in enumerate(images, 1):
        url = img.get("url", "")
        if not url:
            continue

        try:
            # 从 URL 推断扩展名
            ext = Path(urlparse(url).path).suffix or ".jpg"
            dest = work_dir / f"image_{idx:02d}{ext}"
            download_file(url, dest)
            result["image_paths"].append(str(dest))
            result["stats"]["images_ok"] += 1
            print(f"     ✅ 图片 {idx}/{len(images)}: {dest.name}", file=sys.stderr)
            polite_sleep(0.5)  # 图片多时礼貌延迟
        except Exception as e:
            print(f"     ❌ 图片 {idx} 失败: {e}", file=sys.stderr)
            result["failed"].append({"type": "image", "url": url, "error": str(e)})

    return result


# ===== CLI =====
def main():
    parser = argparse.ArgumentParser(description="下载小红书笔记的媒体文件")
    parser.add_argument("--note-json", required=True, help="fetch_note.py 输出的 JSON 路径")
    parser.add_argument("--output-dir", default=str(DEFAULT_CACHE_DIR), help="保存根目录")

    args = parser.parse_args()

    note_path = Path(args.note_json)
    if not note_path.exists():
        print(f"❌ 找不到笔记 JSON: {note_path}", file=sys.stderr)
        sys.exit(1)

    note = json.loads(note_path.read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir)
    result = download_note_media(note, output_dir)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
