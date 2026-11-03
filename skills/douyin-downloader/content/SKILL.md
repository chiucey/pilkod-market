---
name: douyin-downloader
description: 抖音短视频批量下载专家技能，专注于抖音（含抖音火山版、TikTok）短视频的去水印下载、直播录屏及批量采集。当用户要求下载抖音视频、批量采集短视频、提取背景音乐或解决视频下载问题时使用。
---

# Douyin Downloader - 抖音短视频下载专家

## 1. Role Definition 角色定义

**Identity**: 移动端逆向专家 / 视频处理工程师，专注于抖音短视频的去水印下载与批量采集。

**Core Competencies**:
- 无水印下载（Watermark Removal）
- 批量处理（Batch Processing）
- 直播录制（Live Recording）
- 音乐提取（Audio Extraction）
- 工具配置（Tool Configuration）

**Technical Stack**:
| 类别 | 技术/工具 |
|------|----------|
| 编程语言 | Python / JavaScript / Go |
| 视频处理 | FFmpeg / M3U8合并 |
| 逆向工程 | X-Bogus / X-Khronos签名算法 |
| 下载工具 | IDM / yt-dlp / 第三方库 |
| 浏览器插件 | 猫抓 / Video DownloadHelper |

## 2. Warning & Compliance 警告与合规

### 2.1 Important Warnings 重要警告

```
⚠️ 水印限制说明

1. 抖音算法严格，部分视频可能无法100%去除所有水印
2. 贴纸水印、动态水印属于高级防护，无法完全去除
3. 下载前请确认原视频水印情况

⚠️ 风控机制

1. "一机一号"原则：避免多账号同时操作
2. 请求间隔：建议设置3-5秒延时
3. IP限制：大量下载时使用代理IP
4. User-Agent：模拟真实移动端设备

⚠️ 法律合规

1. 仅限下载用户原创或已授权内容
2. 严禁下载分发未授权的版权内容（影视剧、综艺片段）
3. 下载内容仅供个人学习研究使用
4. 遵守抖音平台服务协议
```

## 3. Download Scenarios 下载场景

### 3.1 Scenario Classification 场景分类

| 场景 | 描述 | 适用方法 |
|------|------|---------|
| 单个视频 | 下载指定链接的视频 | 在线解析 / API调用 |
| 主页批量 | 下载作者主页所有视频 | 批量爬虫脚本 |
| 话题标签 | 下载指定话题下的视频 | 关键词搜索爬取 |
| 合集下载 | 下载合集内所有视频 | 合集API解析 |
| 直播录制 | 录制正在直播的内容 | M3U8流捕获 |
| 音乐提取 | 提取视频的背景音乐 | 音频分离技术 |

### 3.2 Download URL Formats 下载链接格式

```
抖音分享链接格式：
├── 标准格式：https://v.douyin.com/xxxxx
├── 完整URL：https://www.douyin.com/video/7xxxxxxxxxx
├── 火星版：https://share.huoshan.com/hotsoon/xxxxx
└── TikTok：https://www.tiktok.com/@user/video/xxxxxxxxxx

主页链接格式：
├── 标准主页：https://www.douyin.com/user/xxxxxxxxxx
├── 短链接：https://v.douyin.com/user/xxxxx
└── 抖音号主页：https://www.douyin.com/discovery?search=xxxxx
```

## 4. Online Tools 在线工具

### 4.1 Recommended Online Parsers 推荐在线解析

| 工具名称 | 网址 | 特点 |
|---------|------|------|
| 抖音视频解析 | https://www.douyin.wtf/ | 简洁高效 |
| 哼哼猫 | https://www.hhm660.com/ | 支持批量 |
| 维讯解析 | https://www.wxsp.com/ | 稳定快速 |
| 视频解析下载 | https://www.jijidown.com/ | 功能丰富 |

**使用方法**：
1. 复制抖音视频分享链接
2. 粘贴到解析网站输入框
3. 点击解析，获取无水印视频地址
4. 复制地址到浏览器下载或使用IDM下载

### 4.2 Browser Extensions 浏览器插件

```
推荐插件：
├── 猫抓（Cat-Catch）
│   ├── 支持平台：Chrome/Edge
│   ├── 功能：自动嗅探页面视频/音频
│   └── 下载：右键另存为
│
├── Video DownloadHelper
│   ├── 支持平台：Chrome/Firefox
│   ├── 功能：检测M3U8/HLS流
│   └── 下载：点击插件图标下载
│
└── 短视频下载助手
    ├── 支持平台：Chrome
    ├── 功能：专门针对抖音/快手优化
    └── 下载：一键解析下载
```

## 5. Python Scripts Python脚本

### 5.1 Single Video Download 单视频下载

```python
# -*- coding: utf-8 -*-
"""
抖音单视频下载脚本
功能：根据分享链接下载无水印视频

依赖安装：
    pip install requests httpx pyquery

⚠️ 注意事项：
    - 请遵守平台协议，仅下载授权内容
    - 添加适当延时，避免触发风控
    - 部分视频可能无法下载（版权/地区限制）
"""

import requests
import re
import os
import time
import json
from urllib.parse import urlencode
from pathlib import Path

# 配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
                  "Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.douyin.com/",
}

OUTPUT_DIR = "./downloads"


def resolve_short_url(short_url: str) -> str:
    """
    解析短链接，获取完整URL

    Args:
        short_url: 抖音短链接

    Returns:
        重定向后的完整URL
    """
    try:
        response = requests.head(short_url, headers=HEADERS, allow_redirects=True, timeout=10)
        return response.url

    except requests.RequestException as e:
        print(f"解析短链接失败: {e}")
        return ""


def extract_aweme_id(url: str) -> str:
    """
    从URL中提取Aweme ID

    Args:
        url: 完整视频URL

    Returns:
        Aweme ID
    """
    # 匹配多种URL格式
    patterns = [
        r'/video/(\d+)',
        r'share/video/(\d+)',
        r'aweme_id=(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""


def get_video_info(aweme_id: str) -> dict:
    """
    获取视频信息（通过旧版API）

    Args:
        aweme_id: 视频ID

    Returns:
        视频信息字典
    """
    api_url = f"https://www.iesdouyin.com/share/video/{aweme_id}/"

    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)

        # 从页面中提取视频信息（正则匹配）
        patterns = {
            "play_addr": r'"playApi":"([^"]+)"',
            "video_url": r'"playwm_addr":"([^"]+)"',
            "title": r'"desc":"([^"]+)"',
            "author": r'"nickname":"([^"]+)"',
        }

        result = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, response.text)
            if match:
                result[key] = match.group(1).replace("\\u002F", "/")

        return result

    except requests.RequestException as e:
        print(f"获取视频信息失败: {e}")
        return {}


def get_video_url_new_api(share_url: str) -> dict:
    """
    通过分享链接获取无水印视频（新版API）

    Args:
        share_url: 视频分享链接

    Returns:
        视频信息
    """
    api_url = "https://www.douyin.com/aweme/v1/web/share/item/"

    params = {
        "device_platform": "ios",
        "aid": "6383",
        "channel": "App Store",
        "aweme_id": extract_aweme_id(share_url),
        "version_code": "170400",
        "version_name": "17.4.0",
    }

    try:
        response = requests.get(
            api_url,
            params=params,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("statusCode") == 0:
                video_info = data.get("aweme_detail", {})

                # 获取无水印视频URL
                video_list = video_info.get("video", {}).get("bitrateInfo", [])

                if video_list:
                    # 获取最高清的版本
                    best_quality = max(
                        video_list,
                        key=lambda x: x.get("play_addr", {}).get("bitrate", 0)
                    )
                    video_url = best_quality.get("play_addr", {}).get("url_list", [0])

                    return {
                        "title": video_info.get("desc", ""),
                        "author": video_info.get("author", {}).get("nickname", ""),
                        "video_url": video_url[0] if video_url else "",
                        "cover_url": video_info.get("video", {}).get("cover", {}).get("url_list", [""])[0],
                    }

        return {}

    except requests.RequestException as e:
        print(f"API请求失败: {e}")
        return {}


def download_video(url: str, filename: str, output_dir: str = OUTPUT_DIR) -> bool:
    """
    下载视频

    Args:
        url: 视频URL
        filename: 保存文件名
        output_dir: 输出目录

    Returns:
        是否成功
    """
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filepath = os.path.join(output_dir, f"{filename}.mp4")

    try:
        print(f"正在下载: {filename}")

        response = requests.get(url, headers=HEADERS, stream=True, timeout=60)

        if response.status_code != 200:
            print(f"下载失败，状态码: {response.status_code}")
            return False

        # 保存文件
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"下载完成: {filepath}")
        return True

    except requests.RequestException as e:
        print(f"下载异常: {e}")
        return False


def process_single_video(share_url: str, output_dir: str = OUTPUT_DIR) -> bool:
    """
    处理单个视频下载

    Args:
        share_url: 视频分享链接
        output_dir: 输出目录

    Returns:
        是否成功
    """
    print("=" * 50)
    print(f"处理链接: {share_url}")

    # 解析短链接
    if "v.douyin.com" in share_url:
        full_url = resolve_short_url(share_url)
        print(f"完整URL: {full_url}")
    else:
        full_url = share_url

    # 提取视频信息
    aweme_id = extract_aweme_id(full_url)

    if not aweme_id:
        print("无法提取视频ID")
        return False

    print(f"视频ID: {aweme_id}")

    # 获取视频URL（尝试新版API）
    video_info = get_video_url_new_api(full_url)

    if not video_info.get("video_url"):
        # 降级到旧版API
        print("尝试旧版API...")
        old_info = get_video_info(aweme_id)
        video_info["video_url"] = old_info.get("play_addr", "").replace("playwm", "play")
        video_info["title"] = old_info.get("desc", aweme_id)

    if not video_info.get("video_url"):
        print("无法获取视频地址，可能视频不支持下载或需要登录")
        return False

    # 生成文件名
    title = video_info.get("title", aweme_id)
    # 清理文件名中的非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]

    # 添加延时
    time.sleep(2)

    # 下载视频
    return download_video(video_info["video_url"], filename, output_dir)


def main():
    """主函数"""
    print("=" * 50)
    print("抖音视频下载工具")
    print("=" * 50)

    # 示例链接
    test_url = input("请输入抖音视频链接（直接回车使用测试链接）: ").strip()

    if not test_url:
        test_url = "https://v.douyin.com/xxxxx"  # 替换为实际链接

    success = process_single_video(test_url)

    if success:
        print("\n下载成功！")
    else:
        print("\n下载失败，请检查链接或稍后重试")


if __name__ == "__main__":
    main()
```

### 5.2 Batch Download 批量下载

```python
# -*- coding: utf-8 -*-
"""
抖音主页批量下载脚本
功能：批量下载指定用户主页的所有视频

依赖安装：
    pip install requests httpx pyquery aiohttp

⚠️ 注意事项：
    - 遵守平台规则，设置合理延时
    - 建议登录获取更多视频
    - 部分视频可能无法下载
"""

import requests
import re
import os
import time
import json
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
                  "Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": "",  # 可选：添加登录Cookie获取更多视频
}

MAX_WORKERS = 3  # 并发下载数
REQUEST_DELAY = 3  # 请求间隔（秒）
OUTPUT_DIR = "./douyin_batch"


class DouyinBatchDownloader:
    """抖音批量下载器"""

    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_user_info(self, sec_uid: str) -> Dict:
        """
        获取用户信息

        Args:
            sec_uid: 用户SEC UID

        Returns:
            用户信息
        """
        api_url = "https://www.douyin.com/aweme/v1/web/user/profile/other/"

        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "sec_user_id": sec_uid,
            "version_code": "170400",
            "version_name": "17.4.0",
        }

        try:
            response = self.session.get(api_url, params=params, timeout=10)
            data = response.json()

            if data.get("status_code") == 0:
                user_info = data.get("user", {})
                return {
                    "nickname": user_info.get("nickname", ""),
                    "uid": user_info.get("uid", ""),
                    "sec_uid": sec_uid,
                    "follower_count": user_info.get("follower_count", 0),
                }

            return {}

        except requests.RequestException as e:
            print(f"获取用户信息失败: {e}")
            return {}

    def get_user_videos(self, sec_uid: str, max_count: int = 100) -> List[Dict]:
        """
        获取用户视频列表

        Args:
            sec_uid: 用户SEC UID
            max_count: 最大获取数量

        Returns:
            视频列表
        """
        videos = []
        cursor = 0
        api_url = "https://www.douyin.com/aweme/v1/web/aweme/post/"

        print(f"正在获取视频列表...")

        while len(videos) < max_count:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "sec_user_id": sec_uid,
                "max_cursor": cursor,
                "locate_query": "false",
                "show_live_replay": "0",
                "is_pull_up": "0",
                "version_code": "170400",
                "version_name": "17.4.0",
            }

            try:
                response = self.session.get(api_url, params=params, timeout=10)
                data = response.json()

                if data.get("status_code") != 0:
                    print(f"API返回错误: {data}")
                    break

                video_list = data.get("aweme_list", [])

                if not video_list:
                    break

                for video in video_list:
                    videos.append({
                        "aweme_id": video.get("aweme_id", ""),
                        "desc": video.get("desc", ""),
                        "create_time": video.get("create_time", 0),
                        "author": video.get("author", {}).get("nickname", ""),
                    })

                    if len(videos) >= max_count:
                        break

                # 更新cursor
                cursor = data.get("cursor", 0)
                has_more = data.get("has_more", 0)

                if not has_more:
                    break

                # 请求延时
                time.sleep(REQUEST_DELAY)

            except requests.RequestException as e:
                print(f"获取视频列表失败: {e}")
                break

        print(f"获取到 {len(videos)} 个视频")
        return videos[:max_count]

    def get_video_url(self, aweme_id: str) -> Optional[str]:
        """
        获取单个视频的下载地址

        Args:
            aweme_id: 视频ID

        Returns:
            视频URL
        """
        api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/"

        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "aweme_id": aweme_id,
            "version_code": "170400",
            "version_name": "17.4.0",
        }

        try:
            response = self.session.get(api_url, params=params, timeout=10)
            data = response.json()

            if data.get("status_code") == 0:
                video_info = data.get("aweme_detail", {})

                # 尝试获取无水印视频
                video_data = video_info.get("video", {})
                bitrate_list = video_data.get("bitrateInfo", [])

                if bitrate_list:
                    # 获取最高清的版本
                    best = max(bitrate_list, key=lambda x: x.get("play_addr", {}).get("bitrate", 0))
                    url_list = best.get("play_addr", {}).get("url_list", [])
                    if url_list:
                        return url_list[0]

                # 降级：获取有水印版本
                url_list = video_data.get("play_addr", {}).get("url_list", [])
                if url_list:
                    return url_list[0]

            return None

        except requests.RequestException as e:
            print(f"获取视频URL失败: {e}")
            return None

    def download_video(self, video_info: Dict) -> bool:
        """
        下载单个视频

        Args:
            video_info: 视频信息

        Returns:
            是否成功
        """
        aweme_id = video_info["aweme_id"]
        desc = video_info["desc"]

        # 生成文件名
        filename = re.sub(r'[<>:"/\\|?*]', '_', desc)[:80] if desc else aweme_id
        filepath = self.output_dir / f"{filename}_{aweme_id}.mp4"

        # 检查是否已下载
        if filepath.exists():
            print(f"已存在，跳过: {filename}")
            return True

        # 获取视频URL
        video_url = self.get_video_url(aweme_id)

        if not video_url:
            print(f"无法获取视频地址: {aweme_id}")
            return False

        # 下载视频
        try:
            print(f"下载中: {filename}")

            response = self.session.get(video_url, stream=True, timeout=120)

            if response.status_code != 200:
                print(f"下载失败，状态码: {response.status_code}")
                return False

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"下载完成: {filename}")
            return True

        except requests.RequestException as e:
            print(f"下载异常: {e}")
            return False

    def batch_download(self, sec_uid: str, max_count: int = 50) -> Dict:
        """
        批量下载用户视频

        Args:
            sec_uid: 用户SEC UID
            max_count: 最大下载数量

        Returns:
            下载结果统计
        """
        # 获取用户信息
        user_info = self.get_user_info(sec_uid)
        nickname = user_info.get("nickname", "unknown")

        print(f"\n用户: {nickname}")
        print(f"预计下载: {max_count} 个视频")
        print("=" * 50)

        # 创建用户专属目录
        user_dir = self.output_dir / nickname
        user_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = user_dir

        # 获取视频列表
        videos = self.get_user_videos(sec_uid, max_count)

        if not videos:
            print("未获取到视频列表")
            return {"total": 0, "success": 0, "failed": 0}

        # 批量下载
        success = 0
        failed = 0

        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}]")

            if self.download_video(video):
                success += 1
            else:
                failed += 1

            # 请求延时（避免风控）
            time.sleep(REQUEST_DELAY)

        result = {
            "total": len(videos),
            "success": success,
            "failed": failed,
        }

        print("\n" + "=" * 50)
        print(f"下载完成！")
        print(f"总计: {result['total']}")
        print(f"成功: {result['success']}")
        print(f"失败: {result['failed']}")
        print(f"保存目录: {self.output_dir}")

        return result


def extract_sec_uid_from_url(url: str) -> str:
    """
    从主页URL提取SEC UID

    Args:
        url: 用户主页URL

    Returns:
        SEC UID
    """
    # 匹配SEC UID模式
    patterns = [
        r'sec_user_id=([^&]+)',
        r'user/([^/?]+)',
        r'@([^/?]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""


def main():
    """主函数"""
    print("=" * 50)
    print("抖音主页批量下载工具")
    print("=" * 50)

    # 获取用户SEC UID
    url = input("请输入抖音用户主页链接: ").strip()

    if not url:
        print("链接不能为空")
        return

    # 提取SEC UID
    sec_uid = extract_sec_uid_from_url(url)

    if not sec_uid:
        print("无法从链接中提取用户ID")
        return

    print(f"用户ID: {sec_uid}")

    # 设置下载数量
    try:
        max_count = int(input("请输入最大下载数量（默认50）: ").strip() or "50"))
    except ValueError:
        max_count = 50

    # 开始下载
    downloader = DouyinBatchDownloader()
    downloader.batch_download(sec_uid, max_count)


if __name__ == "__main__":
    main()
```

## 6. M3U8 Video Processing M3U8视频处理

### 6.1 M3U8 Concept M3U8概念说明

```
什么是M3U8？

M3U8是一种播放列表文件格式，用于HLS（HTTP Live Streaming）流媒体。

抖音直播/部分视频使用M3U8格式，需要用FFmpeg合并为完整MP4。

M3U8文件结构：
#EXTM3U                    ← 文件头
#EXT-X-VERSION:3            ← 版本
#EXT-X-TARGETDURATION:10    ← 单个片段最大时长
#EXT-X-MEDIA-SEQUENCE:1     ← 片段序号
#EXTINF:10.0,              ← 片段1信息
segment1.ts               ← 片段1路径
#EXTINF:10.0,
segment2.ts
#EXT-X-ENDLIST             ← 文件结束
```

### 6.2 FFmpeg Merge Command FFmpeg合并命令

```bash
# 安装FFmpeg（Linux/Mac）
# Ubuntu/Debian
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows: 下载可执行文件 https://ffmpeg.org/download.html

# 基本合并命令
ffmpeg -i "input.m3u8" -c copy -bsf:a aac_adtstoasc output.mp4

# 指定输出格式
ffmpeg -protocol_whitelist "file,http,https,tcp,tls,crypto" \
       -i "input.m3u8" \
       -c copy \
       -bsf:a aac_adtstoasc \
       output.mp4

# 复杂合并（带重试）
ffmpeg -i "input.m3u8" \
       -c:v libx264 -c:a aac \
       -strict experimental \
       output.mp4

# 查看帮助
ffmpeg -h full | less
```

### 6.3 Python M3U8 Downloader M3U8下载器

```python
# -*- coding: utf-8 -*-
"""
M3U8视频下载与合并脚本

依赖安装：
    pip install requests ffmpeg-python
"""

import requests
import re
import os
import subprocess
import tempfile
from pathlib import Path


class M3U8Downloader:
    """M3U8视频下载器"""

    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_m3u8(self, m3u8_url: str) -> tuple:
        """
        解析M3U8文件

        Args:
            m3u8_url: M3U8文件URL

        Returns:
            (base_url, segments)
        """
        try:
            response = requests.get(m3u8_url, timeout=30)
            content = response.text

            # 获取基础URL
            base_url = m3u8_url.rsplit('/', 1)[0] + '/'

            # 解析片段
            segments = []
            for line in content.split('\n'):
                if line and not line.startswith('#'):
                    if line.startswith('http'):
                        segments.append(line)
                    else:
                        segments.append(base_url + line)

            return base_url, segments

        except Exception as e:
            print(f"解析M3U8失败: {e}")
            return "", []

    def download_segments(self, segments: list, output_name: str) -> str:
        """
        下载TS片段并合并

        Args:
            segments: TS片段URL列表
            output_name: 输出文件名

        Returns:
            合并后的文件路径
        """
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        temp_files = []

        print(f"共 {len(segments)} 个片段")

        try:
            # 下载所有片段
            for i, segment_url in enumerate(segments, 1):
                if i % 50 == 0:
                    print(f"下载进度: {i}/{len(segments)}")

                try:
                    response = requests.get(segment_url, timeout=30, stream=True)
                    segment_path = os.path.join(temp_dir, f"segment_{i:05d}.ts")

                    with open(segment_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    temp_files.append(segment_path)

                except Exception as e:
                    print(f"下载片段失败: {e}")
                    continue

            # 创建合并列表文件
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, 'w') as f:
                for segment_path in temp_files:
                    f.write(f"file '{segment_path}'\n")

            # 合并视频
            output_path = self.output_dir / f"{output_name}.mp4"

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-bsf:a', 'aac_adtstoasc',
                str(output_path)
            ]

            print("正在合并视频...")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode == 0:
                print(f"合并完成: {output_path}")
                return str(output_path)
            else:
                print(f"合并失败: {result.stderr.decode()}")
                return ""

        finally:
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def download(self, m3u8_url: str, output_name: str) -> str:
        """
        下载并合并M3U8视频

        Args:
            m3u8_url: M3U8 URL
            output_name: 输出文件名

        Returns:
            输出文件路径
        """
        print("解析M3U8...")
        base_url, segments = self.parse_m3u8(m3u8_url)

        if not segments:
            print("未获取到视频片段")
            return ""

        print(f"获取到 {len(segments)} 个片段")

        return self.download_segments(segments, output_name)


def main():
    """使用示例"""
    downloader = M3U8Downloader()

    # M3U8 URL（通常需要从网页或APP中提取）
    m3u8_url = input("请输入M3U8链接: ").strip()

    if m3u8_url:
        output_name = input("请输入输出文件名: ").strip() or "output"
        downloader.download(m3u8_url, output_name)


if __name__ == "__main__":
    main()
```

## 7. Audio Extraction 音乐提取

### 7.1 Extract Audio with FFmpeg FFmpeg提取音频

```bash
# 从MP4提取MP3
ffmpeg -i input.mp4 -vn -ar 44100 -ac 2 -b:a 192k output.mp3

# 从视频提取音频并转换格式
ffmpeg -i input.mp4 -vn -c:a libmp3lame -q:a 2 output.mp3

# 高质量提取（保留原始音频编码）
ffmpeg -i input.mp4 -vn -c:a copy output.aac

# 批量提取
for file in *.mp4; do
    ffmpeg -i "$file" -vn -ar 44100 -ac 2 -b:a 192k "${file%.mp4}.mp3"
done
```

### 7.2 Python Audio Extractor 音频提取脚本

```python
# -*- coding: utf-8 -*-
"""
抖音视频音乐提取脚本

依赖安装：
    pip install moviepy
"""

import os
import subprocess
from pathlib import Path


def extract_audio(input_file: str, output_file: str = None, format: str = "mp3") -> bool:
    """
    从视频中提取音频

    Args:
        input_file: 输入视频文件
        output_file: 输出音频文件（可选）
        format: 输出格式（mp3/aac/wav）

    Returns:
        是否成功
    """
    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
        return False

    # 生成默认输出文件名
    if not output_file:
        input_path = Path(input_file)
        output_file = str(input_path.with_suffix(f".{format}"))

    # FFmpeg命令
    if format == "mp3":
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vn', '-ar', '44100', '-ac', '2',
            '-b:a', '192k',
            '-f', 'mp3',
            output_file
        ]
    elif format == "aac":
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vn', '-c:a', 'copy',
            '-f', 'adts',
            output_file
        ]
    else:
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vn', '-c:a', 'pcm_s16le',
            '-f', 'wav',
            output_file
        ]

    try:
        print(f"正在提取音频...")

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode == 0:
            print(f"提取完成: {output_file}")
            return True
        else:
            print(f"提取失败: {result.stderr.decode()}")
            return False

    except FileNotFoundError:
        print("错误: 未找到FFmpeg，请先安装")
        return False


def batch_extract_audio(directory: str, format: str = "mp3"):
    """
    批量提取音频

    Args:
        directory: 视频目录
        format: 输出格式
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_dir = Path(directory)

    if not video_dir.exists():
        print(f"目录不存在: {directory}")
        return

    video_files = [
        f for f in video_dir.iterdir()
        if f.suffix.lower() in video_extensions
    ]

    if not video_files:
        print(f"目录中没有找到视频文件: {directory}")
        return

    print(f"找到 {len(video_files)} 个视频文件")

    for i, video_file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}]")

        output_name = str(video_file.with_suffix(f".{format}"))

        if Path(output_name).exists():
            print(f"已存在，跳过: {output_name}")
            continue

        extract_audio(str(video_file), output_name, format)

    print("\n批量提取完成！")


def main():
    """主函数"""
    print("抖音视频音乐提取工具")
    print("=" * 50)

    choice = input("1. 单文件提取\n2. 批量提取\n请选择（1/2）: ").strip()

    if choice == "1":
        input_file = input("请输入视频文件路径: ").strip()
        output_file = input("请输入输出文件路径（直接回车自动命名）: ").strip() or None
        extract_audio(input_file, output_file)

    elif choice == "2":
        directory = input("请输入视频目录路径: ").strip()
        batch_extract_audio(directory)


if __name__ == "__main__":
    main()
```

## 8. Troubleshooting 故障排查

### 8.1 Common Issues 问题矩阵

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 视频不支持下载 | 版权/地区限制/登录要求 | 尝试登录账号/修改IP |
| 获取不到视频URL | 接口变动/风控拦截 | 添加Cookie/更换UA |
| 下载速度慢 | 网络问题/CDN距离 | 使用代理/更换节点 |
| 视频有水印 | 接口返回有水印版本 | 尝试其他API/工具 |
| 批量下载中断 | IP被封/请求超时 | 添加延时/使用代理 |
| M3U8合并失败 | FFmpeg未安装/路径错误 | 安装FFmpeg/检查路径 |

### 8.2 Advanced Solutions 高级解决方案

```
【解决地区限制】
1. 使用代理IP（推荐住宅IP）
2. 修改请求头中的地区参数
3. 使用VPN/机场服务

【解决风控问题】
1. 添加登录Cookie
2. 更换User-Agent
3. 设置请求间隔3-5秒
4. 使用代理IP池

【获取登录Cookie】
1. 在浏览器中登录抖音
2. 打开开发者工具（F12）
3. 切换到Network标签
4. 复制任意请求的Cookie头
```

### 8.3 TikTok下载特别说明

```
TikTok国际版下载注意事项：

1. 域名不同
   - 国内：douyin.com
   - 国际：tiktok.com

2. 接口可能不同
   - TikTok使用不同的签名算法
   - 可能需要X-Bogus参数

3. 地区限制更严格
   - 建议使用代理
   - 部分国家内容无法下载

4. 推荐使用yt-dlp
   pip install yt-dlp

   # TikTok下载命令
   yt-dlp "https://www.tiktok.com/@user/video/xxxxx"

   # 去水印
   yt-dlp --watermark none "https://www.tiktok.com/@user/video/xxxxx"
```

---

**Version**: 2.0
**Last Updated**: 2026-03-27
**Author**: 移动端逆向专家 / MiniMax Agent
