---
name: agent-reach
description: >
  让你的AI助手拥有洞察整个互联网的能力。7500+ GitHub stars。
  支持搜索和读取14个平台：Twitter/X、Reddit、YouTube、GitHub、Bilibili（B站）、
  小红书、抖音、微博、微信公众号、LinkedIn、Instagram、RSS订阅源、Exa网络搜索
  以及任意网页。一键安装，8个渠道零配置，agent-reach doctor用于诊断排障。
  适用场景：(1) 用户要求搜索或读取以上任一平台；(2) 用户分享了支持平台的链接；
  (3) 用户要求搜索网页、查找信息或研究主题；(4) 用户要求在支持平台发帖、评论或互动；
  (5) 用户要求配置或设置平台渠道。
  触发词：搜推特、搜小红书、看视频、搜一下、上网搜、帮我查、全网搜索、search twitter、
  read tweet、youtube transcript、search reddit、read this link、看这个链接、B站、
  bilibili、抖音视频、微信文章、公众号、LinkedIn、GitHub issue、RSS、微博、
  search online、web search、find information、research、帮我配、configure twitter、
  configure proxy、帮我安装。
metadata:
  openclaw:
    homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — 使用指南

支持 13+ 平台的上游工具。可直接调用。

运行 `agent-reach doctor` 检查哪些渠道可用。

## 工作空间规则

**不要在工作空间创建文件。** 使用 `/tmp/` 输出临时文件，使用 `~/.agent-reach/` 存储持久数据。

## 网页 — 任意URL

```bash
curl -s "https://r.jina.ai/URL"
```

## 网络搜索 (Exa)

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
mcporter call 'exa.get_code_context_exa(query: "code question", tokensNum: 3000)'
```

## Twitter/X (xreach)

```bash
xreach search "query" -n 10 --json          # 搜索
xreach tweet URL_OR_ID --json                # 读取推文（支持 /status/ 和 /article/ URL）
xreach tweets @username -n 20 --json         # 用户时间线
xreach thread URL_OR_ID --json               # 完整线程
```

## YouTube (yt-dlp)

```bash
yt-dlp --dump-json "URL"                     # 视频元数据
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"
                                             # 下载字幕，然后读取 .vtt 文件
yt-dlp --dump-json "ytsearch5:query"         # 搜索
```

## Bilibili (yt-dlp)

```bash
yt-dlp --dump-json "https://www.bilibili.com/video/BVxxx"
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --convert-subs vtt --skip-download -o "/tmp/%(id)s" "URL"
```

> 服务器IP可能被返回412。使用 `--cookies-from-browser chrome` 或配置代理。

## Reddit

```bash
curl -s "https://www.reddit.com/r/SUBREDDIT/hot.json?limit=10" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.reddit.com/search.json?q=QUERY&limit=10" -H "User-Agent: agent-reach/1.0"
```

> 服务器IP可能被返回403。请通过 Exa 搜索，或配置代理。

## GitHub (gh CLI)

```bash
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo
gh search code "query" --language python
gh issue list -R owner/repo --state open
gh issue view 123 -R owner/repo
```

## 小红书 (mcporter)

```bash
mcporter call 'xiaohongshu.search_feeds(keyword: "query")'
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy")'
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy", load_all_comments: true)'
mcporter call 'xiaohongshu.publish_content(title: "标题", content: "正文", images: ["/path/img.jpg"], tags: ["tag"])'
```

> 需要登录。使用 Cookie-Editor 导入 cookies。

## 抖音 (mcporter)

```bash
mcporter call 'douyin.parse_douyin_video_info(share_link: "https://v.douyin.com/xxx/")'
mcporter call 'douyin.get_douyin_download_link(share_link: "https://v.douyin.com/xxx/")'
```

> 无需登录。

## 微信公众号

**搜索** (miku_ai):
```python
python3 -c "
import asyncio
from miku_ai import get_wexin_article
async def s():
    for a in await get_wexin_article('query', 5):
        print(f'{a[\"title\"]} | {a[\"url\"]}')
asyncio.run(s())
"
```

**读取** (Camoufox — 绕过微信反爬):
```bash
cd ~/.agent-reach/tools/wechat-article-for-ai && python3 main.py "https://mp.weixin.qq.com/s/ARTICLE_ID"
```

> 微信公众号无法用 Jina Reader 或 curl 读取。必须使用 Camoufox。

## LinkedIn (mcporter)

```bash
mcporter call 'linkedin.get_person_profile(linkedin_url: "https://linkedin.com/in/username")'
mcporter call 'linkedin.search_people(keyword: "AI engineer", limit: 10)'
```

备选方案: `curl -s "https://r.jina.ai/https://linkedin.com/in/username"`

## RSS (feedparser)

```python
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

## 故障排除

- **渠道不工作？** 运行 `agent-reach doctor` — 显示状态和修复说明。
- **Twitter 获取失败？** 确保已安装 `undici`：`npm install -g undici`。配置代理：`agent-reach configure proxy URL`。

## 设置渠道 ("帮我配 XXX")

如果某渠道需要设置（cookies、Docker等），获取安装指南：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

用户只需提供 cookies。其他由你负责。
