#!/usr/bin/env python3
"""
微信公众号文章发布脚本
功能：上传封面图、创建草稿、发布文章

依赖：pip install requests Pillow
"""

import os
import json
import time
import requests
from typing import Optional, Dict, Any
from pathlib import Path


class WeChatArticlePublisher:
    """微信公众号文章发布器"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0

    def _get_access_token(self) -> str:
        """获取或刷新 Access Token"""
        # 检查缓存的 token 是否有效
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "access_token" in data:
            self.access_token = data["access_token"]
            # 提前5分钟过期，留有余量
            self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
            return self.access_token
        else:
            raise Exception(f"获取 Access Token 失败: {data}")

    def upload_cover_image(self, image_path: str) -> str:
        """
        上传封面图到微信公众号素材库
        返回：图片 URL
        """
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self._get_access_token()}"

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        with open(image_path, "rb") as f:
            files = {"media": (os.path.basename(image_path), f, "image/jpeg")}
            response = requests.post(url, files=files, timeout=30)

        data = response.json()

        if "url" in data:
            return data["url"]
        else:
            raise Exception(f"上传封面图失败: {data}")

    def upload_thumb_media(self, image_path: str) -> str:
        """
        上传缩略图（用于草稿封面）
        返回：thumb_media_id
        """
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={self._get_access_token()}&type=image"

        with open(image_path, "rb") as f:
            files = {"media": (os.path.basename(image_path), f, "image/jpeg")}
            response = requests.post(url, files=files, timeout=30)

        data = response.json()

        if "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"上传缩略图失败: {data}")

    def create_draft(self, article: Dict[str, Any]) -> str:
        """
        创建图文草稿
        article 包含: title, author, digest, content, content_source_url, thumb_media_id
        返回：media_id (草稿ID)
        """
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self._get_access_token()}"

        payload = {
            "articles": [
                {
                    "title": article.get("title", ""),
                    "author": article.get("author", ""),
                    "digest": article.get("digest", "")[:54],  # 摘要不超过54字
                    "content": article.get("content", ""),
                    "content_source_url": article.get("content_source_url", ""),
                    "thumb_media_id": article.get("thumb_media_id", ""),
                    "need_open_comment": article.get("need_open_comment", 1),
                    "only_fans_can_comment": article.get("only_fans_can_comment", 0)
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"创建草稿失败: {data}")

    def publish_draft(self, media_id: str) -> str:
        """
        发布草稿
        返回：publish_id，用于查询发布状态
        """
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={self._get_access_token()}"

        payload = {"media_id": media_id}

        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if "publish_id" in data:
            return data["publish_id"]
        else:
            raise Exception(f"发布草稿失败: {data}")

    def get_publish_status(self, publish_id: str) -> Dict[str, Any]:
        """查询发布状态"""
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={self._get_access_token()}"

        params = {"publish_id": publish_id}

        response = requests.get(url, params=params, timeout=10)
        return response.json()


def html_to_wechat_format(content: str) -> str:
    """
    将标准 HTML 转换为微信公众号支持的 HTML 格式
    """
    # 微信公众号支持的 HTML 标签有限
    allowed_tags = ['p', 'h2', 'h3', 'h4', 'strong', 'b', 'em', 'i',
                    'u', 'a', 'img', 'blockquote', 'ul', 'ol', 'li', 'br', 'section']

    # 移除危险的标签和属性
    # 这里简化处理，实际使用时可能需要更完善的 HTML 清洗
    return content


def main():
    """使用示例"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python wechat_publish_script.py <封面图路径>")
        sys.exit(1)

    cover_image = sys.argv[1]

    # 从环境变量获取凭证
    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")

    if not app_id or not app_secret:
        print("错误：请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        sys.exit(1)

    publisher = WeChatArticlePublisher(app_id, app_secret)

    # 示例文章数据
    article = {
        "title": "测试文章标题",
        "author": "作者名",
        "digest": "这是文章摘要，不超过54个字",
        "content": "<p>这是文章正文内容...</p>",
        "content_source_url": "",
        "thumb_media_id": ""  # 将在上传后填充
    }

    try:
        # 1. 上传封面图获取 thumb_media_id
        print("正在上传封面图...")
        thumb_media_id = publisher.upload_thumb_media(cover_image)
        print(f"封面图上传成功，media_id: {thumb_media_id}")
        article["thumb_media_id"] = thumb_media_id

        # 2. 创建草稿
        print("正在创建草稿...")
        media_id = publisher.create_draft(article)
        print(f"草稿创建成功，media_id: {media_id}")

        # 3. 发布草稿
        print("正在发布草稿...")
        publish_id = publisher.publish_draft(media_id)
        print(f"草稿提交成功，publish_id: {publish_id}")

        # 4. 查询发布状态
        print("查询发布状态...")
        status = publisher.get_publish_status(publish_id)
        print(f"发布状态: {status}")

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
