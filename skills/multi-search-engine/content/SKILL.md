---
name: multi-search-engine
description: Multi-channel search engine aggregation supporting advanced search across major domestic and international search engines. Used when users request searches on different platforms, cross-channel information gathering, multi-engine comparative search, advanced search operators, time filtering, site search, privacy-focused search engines, or knowledge queries.
---

# Multi Search Engine - 多渠道搜索引擎集合

## 技能概述

本技能整合了国内外最全面的搜索引擎资源，支持高级搜索运算符、时间筛选、站点搜索、隐私保护和知识计算等功能。无需API密钥，直接生成可访问的搜索链接。

## 搜索运算符参考

### 通用运算符
| 运算符 | 含义 | 示例 |
|--------|------|------|
| `site:` | 站点限定 | `site:zhihu.com AI发展` |
| `" "` | 精确匹配 | `"人工智能最新进展"` |
| `OR` | 或关系 | `AI OR 人工智能` |
| `-` | 排除词 | `iPhone -评测` |
| `intitle:` | 标题包含 | `intitle:机器学习` |
| `inurl:` | URL包含 | `inurl:python 教程` |

### 时间筛选
| 后缀 | 含义 |
|------|------|
| `&tbs=qdr:d` | 最近24小时 |
| `&tbs=qdr:w` | 最近一周 |
| `&tbs=qdr:m` | 最近一月 |
| `&tbs=qdr:y` | 最近一年 |

## 国内搜索引擎

### 通用搜索

#### 百度搜索
```
https://www.baidu.com/s?wd={keyword}
```
**特点**: 中文搜索龙头，覆盖网页、新闻、图片、视频等

#### 百度高级搜索
```
https://www.baidu.com/s?wd={keyword}&tn=baiduadv&ie=utf-8
```

#### 必应搜索（中国版）
```
https://cn.bing.com/search?q={keyword}&ensearch=0
```

#### 必应搜索（国际版）
```
https://cn.bing.com/search?q={keyword}&ensearch=1
```

#### 360搜索
```
https://www.so.com/s?q={keyword}
```

#### 搜狗搜索
```
https://www.sogou.com/web?query={keyword}
```

#### 神马搜索（移动端优先）
```
https://so.m.sm.cn/s?q={keyword}
```

### 社交媒体搜索

#### 微博搜索
```
https://s.weibo.com/weibo?q={keyword}
```
**变体**: https://s.weibo.com/top/summary （热搜榜）

#### 微信公众号搜索
```
https://wx.sogou.com/weixin?type=2&query={keyword}
```

#### 小红书搜索
```
https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51
```

#### 知乎搜索
```
https://www.zhihu.com/search?type=content&q={keyword}
```

### 视频平台搜索

#### B站（Bilibili）搜索
```
https://search.bilibili.com/all?keyword={keyword}
```
**变体**:
- 直播: https://live.bilibili.com/search?keyword={keyword}
- 用户: https://search.bilibili.com/user?keyword={keyword}

#### 抖音搜索
```
https://www.douyin.com/search/{keyword}
```

#### 快手搜索
```
https://www.kuaishou.com/search/{keyword}
```

#### 视频号搜索（微信）
```
https://weixin.qq.com/search?action=search&keyword={keyword}
```

### 知识与社区搜索

#### 豆瓣搜索
```
https://www.douban.com/search?q={keyword}
```

#### 贴吧搜索
```
https://tieba.baidu.com/f/search/res?ie=utf-8&kw={keyword}
```

#### 简书搜索
```
https://www.jianshu.com/search?q={keyword}&page=1&type=note
```

#### 掘金搜索
```
https://juejin.cn/search?query={keyword}&type=all
```

#### CSDN搜索
```
https://so.csdn.net/so/search/s.do?q={keyword}
```

#### 思否搜索
```
https://segmentfault.com/search?q={keyword}
```

#### V2EX搜索
```
https://www.v2ex.com/search?q={keyword}
```

#### 即刻搜索
```
https://web.okjike.com/search/topic?q={keyword}
```

### 新闻资讯搜索

#### 今日头条搜索
```
https://so.toutiao.com/search?keyword={keyword}
```

#### 腾讯新闻搜索
```
https://search.qq.com/news?q={keyword}
```

#### 网易新闻搜索
```
https://www.163.com/search/?keyword={keyword}
```

#### 搜狐新闻搜索
```
https://www.sohu.com/search/search.jsp?q={keyword}
```

#### 新浪新闻搜索
```
https://search.sina.com.cn/?q={keyword}&c=news
```

#### 凤凰网搜索
```
https://search.ifeng.com/?q={keyword}
```

#### 36氪搜索
```
https://36kr.com/search/articles/{keyword}
```

#### 虎嗅搜索
```
https://www.huxiu.com/search.html?query={keyword}
```

#### 钛媒体搜索
```
https://www.tmtpost.com/search?q={keyword}
```

### 电商购物搜索

#### 淘宝搜索
```
https://s.taobao.com/search?q={keyword}
```

#### 京东搜索
```
https://search.jd.com/Search?keyword={keyword}
```

#### 拼多多搜索
```
https://youhui.pinduoduo.com/search result?keyword={keyword}
```

#### 苏宁搜索
```
https://search.suning.com/{keyword}/
```

### 学术资源搜索

#### 积微搜索
```
https://www.jisilu.cn/explore/?keyword={keyword}
```

#### 百度学术
```
https://xueshu.baidu.com/s?wd={keyword}
```

#### CNKI学术搜索
```
https://search.cnki.net/Search/Index?searchword={keyword}
```

## 国际搜索引擎

### 通用搜索

#### Google搜索
```
https://www.google.com/search?q={keyword}
```

#### Google香港
```
https://www.google.com.hk/search?q={keyword}
```

#### Google高级搜索
```
https://www.google.com/advanced_search?q={keyword}
```

#### 必应国际
```
https://www.bing.com/search?q={keyword}
```

#### Yahoo搜索
```
https://search.yahoo.com/search?p={keyword}
```

### 隐私保护搜索引擎

#### DuckDuckGo
```
https://duckduckgo.com/html/?q={keyword}
```
**特点**: 不追踪用户隐私，无个性化广告

#### Startpage
```
https://www.startpage.com/sp/search?query={keyword}
```
**特点**: 谷歌搜索结果但保护隐私

#### Brave Search
```
https://search.brave.com/search?q={keyword}
```
**特点**: Brave浏览器内置，尊重隐私

#### Ecosia
```
https://www.ecosia.org/search?q={keyword}
```
**特点**: 搜索收益用于植树造林

#### Qwant
```
https://www.qwant.com/?q={keyword}
```
**特点**: 法国隐私搜索引擎，不追踪用户

#### Mojeek
```
https://www.mojeek.com/search?q={keyword}
```
**特点**: 独立的隐私搜索引擎

#### Swisscows
```
https://swisscows.com/web?query={keyword}
```
**特点**: 瑞士服务器，不存储用户数据

### 知识计算引擎

#### WolframAlpha
```
https://www.wolframalpha.com/input?i={keyword}
```
**用途**: 数学计算、单位换算、数据分析、知识问答

#### Perplexity
```
https://www.perplexity.ai/search?q={keyword}
```
**特点**: AI驱动的对话式搜索引擎

### 社交媒体搜索

#### X (Twitter) 搜索
```
https://twitter.com/search?q={keyword}
```
**变体**:
- 高级搜索: https://twitter.com/search-advanced?lang=zh
- 趋势: https://twitter.com/i/trends

#### Facebook 搜索
```
https://www.facebook.com/search/top?q={keyword}
```

#### LinkedIn 搜索
```
https://www.linkedin.com/search/results/all/?keywords={keyword}
```

#### Reddit 搜索
```
https://www.reddit.com/search/?q={parameter}
```

#### Instagram 搜索
```
https://www.instagram.com/explore/search/?q={keyword}
```

### 视频平台搜索

#### YouTube搜索
```
https://www.youtube.com/results?search_query={keyword}
```
**变体**:
- 频道: https://www.youtube.com/channel/{channel_id}/search?query={keyword}
- 播放列表: https://www.youtube.com/results?sp= EgQYAQ%3D%3D&q={keyword}

#### Vimeo搜索
```
https://vimeo.com/search?q={keyword}
```

### 图片搜索

#### Google图片
```
https://www.google.com/search?q={keyword}&tbm=isch
```

#### Bing图片
```
https://www.bing.com/images/search?q={keyword}
```

#### Pinterest
```
https://www.pinterest.com/search/pins/?q={keyword}
```

#### Flickr
```
https://www.flickr.com/search/?text={keyword}
```

### 新闻搜索

#### Google新闻
```
https://news.google.com/search?q={keyword}
```

#### Bing新闻
```
https://www.bing.com/news/search?q={keyword}
```

#### Yahoo新闻
```
https://news.search.yahoo.com/search?p={keyword}
```

#### News.google
```
https://news.google.com/rss/search?q={keyword}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans
```

### 学术搜索

#### Google Scholar
```
https://scholar.google.com/scholar?q={keyword}
```

#### Semantic Scholar
```
https://www.semanticscholar.org/search?q={keyword}
```

#### ResearchGate
```
https://www.researchgate.net/search/researcher?q={keyword}
```

#### arXiv
```
https://arxiv.org/search/?searchby=all_query&query={keyword}
```

#### PubMed
```
https://pubmed.ncbi.nlm.nih.gov/?term={keyword}
```

#### IEEE Xplore
```
https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={keyword}
```

### 开发者资源搜索

#### GitHub
```
https://github.com/search?q={keyword}
```
**变体**:
- 代码: https://github.com/search?q={keyword}&type=code
- 用户: https://github.com/search?q={keyword}&type=user

#### Stack Overflow
```
https://stackoverflow.com/search?q={keyword}
```

#### npm搜索
```
https://www.npmjs.com/search?q={keyword}
```

#### PyPI搜索
```
https://pypi.org/search/?q={keyword}
```

## 高级搜索功能

### 站点内搜索

| 平台 | 语法 | 示例 |
|------|------|------|
| 通用 | `site:domain.com {keyword}` | `site:github.com python教程` |
| 百度 | `site:baidu.com {keyword}` | `site:baidu.com 人工智能` |
| Google | `site:*.edu.cn {keyword}` | `site:*.edu.cn 机器学习` |

### 文件类型搜索

| 语法 | 说明 |
|------|------|
| `filetype:pdf {keyword}` | PDF文档 |
| `filetype:doc {keyword}` | Word文档 |
| `filetype:xls {keyword}` | Excel表格 |
| `filetype:ppt {keyword}` | PPT演示文稿 |
| `filetype:pdf site:*.gov.cn {keyword}` | 政府PDF文档 |

### 价格与购物搜索

| 语法 | 说明 |
|------|------|
| `{keyword} 价格` | 基础价格搜索 |
| `{keyword} site:jd.com` | 京东价格 |
| `{keyword} site:taobao.com` | 淘宝价格 |

## 使用示例

### 场景1: 跨平台信息搜集
```
用户: "帮我搜索'人工智能最新进展'，覆盖国内外主要平台"

执行策略:
1. 国内: 百度、微博、知乎、微信公众号、B站
2. 国际: Google、Bing、YouTube、Google Scholar
```

### 场景2: 隐私搜索
```
用户: "我不想被追踪，用隐私搜索引擎搜索..."

推荐使用:
- DuckDuckGo
- Startpage
- Brave Search
- Ecosia
```

### 场景3: 社交媒体热点追踪
```
用户: "搜索'某事件'在微博和Twitter上的讨论"

执行:
- 微博热搜: https://s.weibo.com/weibo?q={keyword}
- Twitter: https://twitter.com/search?q={keyword}
```

### 场景4: 开发者资源查找
```
用户: "找Python Web框架的最佳实践"

执行:
- GitHub: https://github.com/search?q=python+web+framework
- Stack Overflow: https://stackoverflow.com/search?q=python+web+framework
- Google Scholar: https://scholar.google.com/scholar?q=python+web+framework
```

## 输出格式

当用户请求搜索时，输出以下格式：

```markdown
## 多渠道搜索结果 - [{关键词}]

### 🔍 国内平台

| 平台 | 搜索链接 | 备注 |
|------|----------|------|
| 百度 | [链接] | 基础搜索 |
| 微博 | [链接] | 社交媒体 |
| 知乎 | [链接] | 知识社区 |
| B站 | [链接] | 视频资源 |
| 小红书 | [链接] | 生活分享 |

### 🌐 国际平台

| 平台 | 搜索链接 | 备注 |
|------|----------|------|
| Google | [链接] | 全球搜索 |
| DuckDuckGo | [链接] | 隐私搜索 |
| YouTube | [链接] | 视频资源 |
| Twitter | [链接] | 社交动态 |

### 💡 高级搜索建议

- 时间筛选: 添加 `&tbs=qdr:m` 限定最近一月
- 精确匹配: 使用 `"关键词"`
- 站点限定: `site:example.com 关键词`
```

## 注意事项

1. **链接生成**: 所有链接直接生成，用户点击即可在新标签页打开
2. **无需认证**: 本技能不依赖任何API密钥
3. **跨平台覆盖**: 尽可能覆盖用户指定的或相关的所有平台
4. **隐私保护**: 如用户有隐私需求，优先推荐隐私搜索引擎
5. **实时更新**: 链接基于当前平台URL规则，如有变动请反馈

## 维护日志

- 2024-03: 初始版本，整合国内外主流搜索引擎
- 支持搜索运算符、时间筛选、站点搜索等高级功能
- 涵盖社交媒体、视频平台、知识社区、学术资源等全品类
