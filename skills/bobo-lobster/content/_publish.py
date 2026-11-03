#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号草稿箱发布脚本
波波虾专用 - 正确处理中文编码

关键点：使用 json.dumps(data, ensure_ascii=False) 防止中文转义
"""

import requests
import json
import os
import re

# ============== 配置区域（请根据实际情况修改）==============
APP_ID = "wxa09c70eda62bc1d2"
APP_SECRET = "dd764aa76e22ef2807a8678917e567b9"
# =========================================================

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"
UPLOAD_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"


def get_access_token():
    """获取Access Token"""
    params = {"grant_type": "client_credential", "appid": APP_ID, "secret": APP_SECRET}
    response = requests.get(TOKEN_URL, params=params)
    result = response.json()
    if "access_token" in result:
        print("[OK] 获取Access Token成功")
        return result["access_token"]
    else:
        print(f"[ERROR] 获取失败: {result}")
        return None


def upload_image(access_token, image_path):
    """上传封面图到微信素材库"""
    print(f"[INFO] 上传图片: {image_path}")
    url = f"{UPLOAD_URL}?access_token={access_token}&type=image"
    try:
        with open(image_path, "rb") as f:
            files = {"media": (os.path.basename(image_path), f, "image/png")}
            response = requests.post(url, files=files)
        result = response.json()
        if "media_id" in result:
            print(f"[OK] 上传成功, media_id: {result['media_id'][:20]}...")
            return result.get("media_id", "")
        else:
            print(f"[ERROR] 上传失败: {result}")
            return ""
    except Exception as e:
        print(f"[ERROR] 处理失败: {e}")
        return ""


def create_draft(access_token, title, author, content, thumb_media_id):
    """
    创建草稿

    重要：必须使用 data=json.dumps(data, ensure_ascii=False)
    否则中文会被转义成 Unicode 编码（如 \u4e2d\u6587）
    """
    articles = [{
        "title": title,
        "author": author,
        "digest": title[:30] if len(title) > 30 else title,  # 摘要不超过30字
        "content": content,
        "content_source_url": "",
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }]

    data = {"articles": articles}
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token}

    # ========== 关键修复 ==========
    # 使用 ensure_ascii=False 确保中文不被转义
    response = requests.post(
        DRAFT_URL,
        headers=headers,
        params=params,
        data=json.dumps(data, ensure_ascii=False)
    )
    # ===============================

    result = response.json()
    if result.get("errcode") == 0 or "media_id" in result:
        print(f"[OK] 草稿创建成功! media_id: {result.get('media_id', '')[:30]}...")
        return True
    else:
        print(f"[ERROR] 草稿创建失败: {result.get('errmsg')}")
        return False


def publish_article(html_file, title, author, cover_image):
    """
    发布文章到微信草稿箱

    Args:
        html_file: HTML文件路径（包含文章内容）
        title: 文章标题
        author: 作者名称（建议2-8字）
        cover_image: 封面图路径
    """
    print("=" * 50)
    print("波波虾 - 微信公众号草稿发布")
    print("=" * 50)

    # 1. 获取Token
    access_token = get_access_token()
    if not access_token:
        return False

    # 2. 上传封面图
    thumb_media_id = upload_image(access_token, cover_image)
    if not thumb_media_id:
        print("[ERROR] 封面图上传失败")
        return False

    # 3. 读取HTML内容
    print(f"[INFO] 读取文章: {html_file}")
    if not os.path.exists(html_file):
        print(f"[ERROR] 文件不存在: {html_file}")
        return False

    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取body内容
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    if body_match:
        content = body_match.group(1)

    # 4. 创建草稿
    success = create_draft(access_token, title, author, content, thumb_media_id)

    if success:
        print("\n" + "=" * 50)
        print("[OK] 发布成功!")
        print("请登录微信公众平台 -> 内容与互动 -> 草稿箱查看")
        print("=" * 50)
        return True
    else:
        print("\n[ERROR] 发布失败")
        return False


def main():
    import sys

    if len(sys.argv) >= 4:
        html_file = sys.argv[1]
        title = sys.argv[2]
        author = sys.argv[3]
        cover_image = sys.argv[4]
    else:
        # 默认配置
        html_file = "/workspace/article.html"
        title = "文章标题"
        author = "作者"
        cover_image = "/workspace/cover.png"

    publish_article(html_file, title, author, cover_image)


if __name__ == "__main__":
    main()
