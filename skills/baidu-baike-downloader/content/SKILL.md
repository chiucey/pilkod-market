---
name: baidu-baike-downloader
description: 下载百度百科页面并解析成JSON格式。当用户要求获取百度百科词条内容、提取百科信息、下载百度百科数据时使用。
---

# 百度百科下载器

## 功能概述

这是一个用于下载百度百科页面并将其解析为结构化JSON数据的技能。它能够提取词条的标题、简介、目录结构、内容段落、图片等信息，并以易用的JSON格式输出。

## 使用方法

```bash
python baidu_baike_downloader.py <词条名称>
```

## 输出示例

```json
{
  "title": "词条名称",
  "url": "https://baike.baidu.com/item/词条名称",
  "summary": "词条简介",
  "categories": ["分类1", "分类2"],
  "sections": [
    {
      "title": "章节标题",
      "content": "章节内容..."
    }
  ],
  "images": [
    {
      "url": "图片URL",
      "caption": "图片说明"
    }
  ],
  "references": [
    {
      "title": "参考来源标题",
      "url": "参考链接"
    }
  ]
}
```

## 技术实现

- 使用 requests 库进行HTTP请求
- 使用 BeautifulSoup4 解析HTML
- 支持自动重试和错误处理
- 编码自动检测（优先使用UTF-8）

## 依赖

- requests
- beautifulsoup4
- lxml
