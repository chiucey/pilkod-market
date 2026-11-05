#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号智能排版配图工具 - 配置示例

使用方法：
1. 复制此文件为 config.json
2. 填入您的API密钥
3. 修改配置参数
"""

{
    "image_search": {
        "unsplash_api_key": "YOUR_UNSPLASH_API_KEY",
        "pexels_api_key": "YOUR_PEXELS_API_KEY",
        "default_count": 10,
        "exclude_watermarked": true
    },

    "ai_generation": {
        "enabled": true,
        "minimax_api_key": "YOUR_MINIMAX_API_KEY",
        "preferred_method": "minimax",
        "default_style": "photorealistic"
    },

    "local_stable_diffusion": {
        "enabled": false,
        "api_url": "http://localhost:7860",
        "model": "AnythingV5",
        "steps": 30
    },

    "watermark_removal": {
        "enabled": true,
        "auto_detect": true,
        "strength": "medium"
    },

    "formatting": {
        "color_scheme": "auto",
        "font_family": "PingFang SC, Hiragino Sans GB, Microsoft YaHei",
        "body_font_size": 15,
        "line_height": 1.9,
        "paragraph_indent": 2,
        "show_author": true,
        "author_info": ""
    },

    "logo": {
        "enabled": false,
        "path": "",
        "position": "bottom-right",
        "opacity": 0.85
    },

    "output": {
        "format": "html",
        "css_inline": true,
        "save_images": false,
        "images_folder": "./article_images"
    }
}
