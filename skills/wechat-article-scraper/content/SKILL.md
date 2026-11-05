---
name: wechat-article-scraper
description: 微信公众号文章爬虫工具。当用户要求爬取微信公众号文章、提取微信文章内容、获取微信文章标题作者正文时使用。支持通过URL爬取并输出JSON/Text/Markdown格式。
---

# 微信公众号文章爬虫

通过模拟手机UA绕过微信PC端反爬机制，提取公众号文章的标题、描述、作者和正文内容。

## 核心原理

| 步骤 | 方法 | 说明 |
|------|------|------|
| **1. UA伪装** | 使用手机端User-Agent | 绕过PC端JS渲染+反爬拦截 |
| **2. 发送请求** | `requests`带Header跟进重定向 | 微信手机版接口检查Header即放行 |
| **3. 正文提取** | 解析og:title/og:description/meta标签 | 关键信息在meta里，p标签读取正文 |

## 使用方式

### 命令行调用

```bash
python scripts/wechat_scraper.py "文章链接" -f json -o result.json
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `url` | 微信文章链接（必填） | `https://mp.weixin.qq.com/s/xxx` |
| `-o, --output` | 输出文件路径 | `article.json` |
| `-f, --format` | 输出格式 | `json`(默认)/`text`/`markdown` |

### 返回数据结构

```json
{
  "title": "文章标题",
  "description": "文章描述/摘要",
  "author": "作者名称",
  "content": "正文内容（段落用\\n\\n分隔）",
  "word_count": 1234
}
```

## 实现细节

### 手机UA列表

```python
MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)
```

### 请求头设置

```python
headers = {
    "User-Agent": MOBILE_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
```

### HTML解析策略

1. 优先提取 `<meta property="og:title">` 和 `<meta property="og:description">`
2. 正文区域：`article` 标签或 `id="js_content"` 元素
3. 过滤：`script`、`style` 标签内容
4. 段落保留：`p`、`blockquote`、`h1-h4` 标签文本

## 注意事项

- 仅支持 `mp.weixin.qq.com` 域名链接
- 部分文章需要关注后阅读，可能提取失败
- 建议设置适当延时避免频繁请求
- 商业使用请遵守微信服务条款
