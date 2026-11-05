---
name: douyin-watermark-remover
description: 抖音/快手等短视频平台视频去水印解析工具。当用户需要下载无水印视频、解析视频直链、获取视频下载地址时使用。触发短语包括："去水印"、"视频解析"、"下载视频"、"抖音视频"、"快手视频"、"视频直链"等。
---

# 短视频去水印工具

## 功能概述

支持解析抖音、快手等主流短视频平台的视频，提取无水印直链下载地址。

## 支持平台

| 平台 | 支持状态 | 说明 |
|------|----------|------|
| 抖音 | ✅ 全面支持 | 抖音短视频/直播回放 |
| 快手 | ✅ 全面支持 | 快手短视频 |
| 视频号 | 🔄 开发中 | 微信视频号支持 |
| 小红书 | 🔄 开发中 | 小红书视频支持 |
| B站 | 🔄 开发中 | 哔哩哔哩视频支持 |

## 核心函数

### parse_video_tool

```python
def parse_video_tool(link: str) -> dict:
    """
    传入视频链接（抖音/快手等），返回解析后的真实地址
    :param link: 视频原始链接
    :return: 解析结果字典
    """
```

## 使用示例

### 示例1：解析抖音视频

**输入：**
```
https://v.douyin.com/xxxxx
```

**输出：**
```json
{
  "success": true,
  "title": "视频标题",
  "cover_url": "封面图地址",
  "video_url": "无水印视频直链",
  "duration": 15.5,
  "author": "作者昵称",
  "platform": "douyin"
}
```

### 示例2：解析快手视频

**输入：**
```
https://v.kuaishou.com/xxxxx
```

**输出：**
```json
{
  "success": true,
  "title": "视频标题",
  "cover_url": "封面图地址",
  "video_url": "无水印视频直链",
  "duration": 20.0,
  "author": "作者昵称",
  "platform": "kuaishou"
}
```

## 错误处理

### 链接格式错误

```json
{
  "success": false,
  "error_code": "INVALID_URL",
  "message": "链接格式不正确，请输入完整的视频分享链接"
}
```

### 平台不支持

```json
{
  "success": false,
  "error_code": "UNSUPPORTED_PLATFORM",
  "message": "暂不支持该平台，请输入抖音或快手视频链接"
}
```

### 视频已下架/不可用

```json
{
  "success": false,
  "error_code": "VIDEO_UNAVAILABLE",
  "message": "视频不存在或已下架，无法解析"
}
```

### 请求超时

```json
{
  "success": false,
  "error_code": "TIMEOUT",
  "message": "请求超时，请稍后重试"
}
```

## 代码实现

```python
import requests
import json
import re
from urllib.parse import urlparse

# ====================== 平台识别 ======================
def identify_platform(url: str) -> str:
    """识别视频链接的平台类型"""
    if "douyin.com" in url:
        return "douyin"
    elif "kuaishou.com" in url or "ksurl.cn" in url:
        return "kuaishou"
    elif "bilibili.com" in url or "b23.tv" in url:
        return "bilibili"
    elif "xiaohongshu.com" in url or "xhslink.com" in url:
        return "xiaohongshu"
    elif "weixin.qq.com" in url:
        return "video"
    else:
        return "unknown"

# ====================== 核心解析逻辑 ======================
def _parse_video_core(link: str) -> dict:
    """
    通用视频解析核心函数
    :param link: 视频原始链接
    :return: 解析结果字典
    """
    api_url = "https://link.apadog.com/pocketDog/video/get"

    headers = {
        "aut": "RuoYouShiWu",
        "openid": "wx6faa203f7810f01b",
    }

    print(f"正在解析视频链接: {link}")

    # 平台识别
    platform = identify_platform(link)
    print(f"识别平台: {platform}")

    if platform == "unknown":
        return {
            "success": False,
            "error_code": "UNSUPPORTED_PLATFORM",
            "message": "暂不支持该平台，请输入抖音或快手视频链接"
        }

    # 请求参数
    params = {
        "shareUrl": link
    }

    try:
        # 发送GET请求
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()

        # 处理返回结果
        if result.get("code") == 0 or result.get("success"):
            return {
                "success": True,
                "title": result.get("title", "无标题"),
                "cover_url": result.get("cover", ""),
                "video_url": result.get("video_url") or result.get("url", ""),
                "duration": result.get("duration", 0),
                "author": result.get("author", {}).get("name", "") if isinstance(result.get("author"), dict) else result.get("author", ""),
                "platform": platform
            }
        else:
            return {
                "success": False,
                "error_code": "PARSE_FAILED",
                "message": result.get("msg", "解析失败，请检查链接是否正确")
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_code": "TIMEOUT",
            "message": "请求超时，请稍后重试"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "message": f"网络请求失败: {str(e)}"
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "error_code": "PARSE_ERROR",
            "message": "解析响应失败，请稍后重试"
        }

# ====================== MCP 工具函数 ======================
def parse_video_tool(link: str) -> dict:
    """
    传入视频链接（抖音/快手等），返回解析后的真实地址
    :param link: 视频原始链接
    :return: 解析结果字典
    """
    return _parse_video_core(link)
```

## 使用限制

1. **每日调用次数**：建议控制在合理范围内
2. **链接有效期**：部分平台链接有时效性，过期链接无法解析
3. **清晰度选择**：默认返回最高清晰度版本
4. **版权提醒**：请尊重视频创作者版权，下载仅供个人学习使用

## 常见问题

### Q: 为什么解析失败？
A: 可能是以下原因：
- 链接已过期或视频已下架
- 视频设置了仅好友可见或私密
- 该平台暂未支持

### Q: 如何获取正确的视频链接？
A: 在抖音/快手APP中，点击分享 → 复制链接，获取完整的分享链接。

### Q: 下载的视频有水印怎么办？
A: 确保使用的是无水印直链，`video_url` 字段返回的即为无水印地址。

### Q: 解析速度较慢？
A: 视频资源较大时解析需要一定时间，建议耐心等待或稍后重试。
