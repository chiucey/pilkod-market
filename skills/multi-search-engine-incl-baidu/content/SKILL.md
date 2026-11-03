---
name: multi-search-engine-incl-baidu
description: 多搜索引擎聚合工具，支持Bing、Google、百度搜索，集成高级搜索运算符、时间筛选、站点搜索、隐私搜索、知识查询能力，满足全场景的搜索需求。Triggers: search, multi-engine search, baidu, google, bing, privacy search, advanced search, site search.
---

# Multi Search Engine incl. Baidu - 多搜索引擎聚合工具(含百度)

## 技能概述

多搜索引擎聚合工具，支持Bing、Google、百度搜索三大主流引擎。集成高级搜索运算符、时间筛选、站点搜索、隐私搜索、知识查询能力，满足全场景的搜索需求。支持通过API密钥扩展更多高级功能，同时保留无需API的URL模板搜索能力。

## 函数接口

### universal_search

通用多引擎搜索接口，支持切换不同搜索引擎，内置高级搜索、时间筛选、站点搜索能力。

#### 参数定义

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 是 | - | 搜索查询词，支持所有引擎的高级搜索运算符 |
| `engine` | string | 否 | bing | 选择搜索引擎：bing, google, baidu |
| `count` | integer | 否 | 10 | 返回结果数量，范围1-50 |
| `freshness` | string | 否 | null | 时间范围筛选，仅百度引擎生效 |

#### 参数详情

**query** - 搜索查询词
```
支持所有引擎的高级搜索运算符：
- site:指定站点
- filetype:指定文件类型
- intitle:标题匹配
- inurl:链接匹配
- "精确匹配"
- OR 或运算
- -排除词

可用于：知识查询、隐私搜索、新闻搜索等场景
```

**engine** - 搜索引擎选择
```
可选值：bing, google, baidu
默认值：bing

- bing: Microsoft Bing搜索，全球覆盖
- google: Google搜索，索引最全（需要API密钥）
- baidu: 百度搜索，中文首选（支持时间筛选）
```

**count** - 结果数量
```
范围：1-50
默认值：10
返回对应数量的搜索结果
```

**freshness** - 时间范围筛选
```
仅百度引擎生效，支持两种格式：

1. 日期范围：
   YYYY-MM-DDtoYYYY-MM-DD
   例如：2025-09-01to2025-09-08

2. 快捷时间：
   pd - 过去24小时
   pw - 过去7天
   pm - 过去31天
   py - 过去365天
```

#### HTTP Handler 配置

```yaml
handler:
  type: http
  request:
    # 百度搜索
    if: "{{engine}} == 'baidu'"
    then:
      url: https://qianfan.baidubce.com/v1/search
      method: POST
      headers:
        Authorization: "Bearer {{BAIDU_API_KEY}}"
        Content-Type: application/json
      body:
        query: "{{query}}"
        count: "{{count}}"
        freshness: "{{freshness}}"

    # Bing搜索
    else:
      if: "{{engine}} == 'bing'"
      then:
        url: https://api.bing.microsoft.com/v7.0/search
        method: GET
        headers:
          Ocp-Apim-Subscription-Key: "{{BING_API_KEY}}"
        params:
          q: "{{query}}"
          count: "{{count}}"

      # Google搜索
      else:
        url: https://www.googleapis.com/customsearch/v1
        method: GET
        headers:
          X-Goog-Api-Key: "{{GOOGLE_API_KEY}}"
        params:
          q: "{{query}}"
          num: "{{count}}"

  response:
    # 百度响应解析
    if: "{{engine}} == 'baidu'"
    then:
      results: "{{body.items}}"
      summary: "搜索到{{body.items.length}}条结果，来自百度搜索"

    # Bing响应解析
    else:
      if: "{{engine}} == 'bing'"
      then:
        results: "{{body.webPages.value}}"
        summary: "搜索到{{body.webPages.value.length}}条结果，来自Bing搜索"

      # Google响应解析
      else:
        results: "{{body.items}}"
        summary: "搜索到{{body.items.length}}条结果，来自Google搜索"
```

#### 返回结果格式

```json
{
  "results": [
    {
      "title": "结果标题",
      "url": "https://...",
      "snippet": "结果摘要/描述"
    }
  ],
  "summary": "搜索到N条结果，来自XXX搜索",
  "engine": "当前使用的搜索引擎",
  "query": "原始查询词"
}
```

---

## 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `BING_API_KEY` | Bing搜索API密钥，用于使用Bing搜索功能 | 否 |
| `GOOGLE_API_KEY` | Google搜索API密钥，用于使用Google搜索功能 | 否 |
| `BAIDU_API_KEY` | 百度搜索API密钥，用于使用百度搜索功能，可在百度智能云控制台申请 | 否 |

### API密钥申请

**Bing API Key**
- 申请地址：https://azure.microsoft.com/services/cognitive-services/bing-web-search-api/
- 定价：免费层1000次/月

**Google API Key**
- 申请地址：https://console.cloud.google.com/apis/credentials
- 需要启用Custom Search API

**Baidu API Key**
- 申请地址：https://cloud.baidu.com/product/search.html
- 百度智能云搜索服务

---

## 高级搜索运算符

### 通用运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `site:{domain}` | 站点限定 | `site:github.com python` |
| `filetype:{ext}` | 文件类型 | `filetype:pdf AI发展` |
| `"{phrase}"` | 精确匹配 | `"人工智能最新进展"` |
| `{keyword} OR {keyword2}` | 或运算 | `AI OR 人工智能` |
| `{keyword} -{exclude}` | 排除词 | `iPhone -评测` |
| `intitle:{keyword}` | 标题包含 | `intitle:机器学习` |
| `inurl:{keyword}` | URL包含 | `inurl:python 教程` |

### 百度专有

| 运算符 | 说明 |
|--------|------|
| `{关键词} inurl:{路径}` | URL路径匹配 |
| `{关键词} rn:{数量}` | 结果数量限定 |

### Google专有

| 运算符 | 说明 |
|--------|------|
| `cache:{url}` | 查看网页缓存 |
| `related:{url}` | 相关页面 |
| `info:{url}` | 网站信息 |

### Bing专有

| 运算符 | 说明 |
|--------|------|
| `{keyword} location:{地区}` | 地区限定 |
| `{keyword} language:{语言}` | 语言限定 |

---

## 搜索模板库

### 国内搜索引擎

| 引擎 | URL模板 | 特点 |
|------|---------|------|
| 百度 | `https://www.baidu.com/s?wd={keyword}` | 中文搜索首选 |
| Bing CN | `https://cn.bing.com/search?q={keyword}` | 微软必应中国 |
| 360搜索 | `https://www.so.com/s?q={keyword}` | 安全浏览器 |
| 搜狗 | `https://www.sogou.com/web?query={keyword}` | 微信内容搜索 |
| 神马 | `https://so.m.sm.cn/s?q={keyword}` | 移动端优先 |

### 国际搜索引擎

| 引擎 | URL模板 | 特点 |
|------|---------|------|
| Google | `https://www.google.com/search?q={keyword}` | 全球索引最全 |
| DuckDuckGo | `https://duckduckgo.com/html/?q={keyword}` | 隐私保护 |
| Yahoo | `https://search.yahoo.com/search?p={keyword}` | 门户搜索 |
| Bing | `https://www.bing.com/search?q={keyword}` | 微软搜索 |

### 隐私搜索引擎

| 引擎 | URL模板 | 隐私等级 |
|------|---------|----------|
| DuckDuckGo | `https://duckduckgo.com/html/?q={keyword}` | ⭐⭐⭐⭐⭐ |
| Startpage | `https://www.startpage.com/sp/search?query={keyword}` | ⭐⭐⭐⭐⭐ |
| Brave | `https://search.brave.com/search?q={keyword}` | ⭐⭐⭐⭐ |
| Ecosia | `https://www.ecosia.org/search?q={keyword}` | ⭐⭐⭐⭐ |

### 知识计算引擎

| 引擎 | URL模板 | 用途 |
|------|---------|------|
| WolframAlpha | `https://www.wolframalpha.com/input?i={keyword}` | 数学/单位/汇率 |

### 社交媒体搜索

| 平台 | URL模板 |
|------|---------|
| 微博 | `https://s.weibo.com/weibo?q={keyword}` |
| 知乎 | `https://www.zhihu.com/search?type=content&q={keyword}` |
| 微信公众号 | `https://wx.sogou.com/weixin?type=2&query={keyword}` |
| Twitter/X | `https://twitter.com/search?q={keyword}` |
| YouTube | `https://www.youtube.com/results?search_query={keyword}` |

### 开发者资源

| 平台 | URL模板 |
|------|---------|
| GitHub | `https://github.com/search?q={keyword}` |
| Stack Overflow | `https://stackoverflow.com/search?q={keyword}` |
| Google Scholar | `https://scholar.google.com/scholar?q={keyword}` |

---

## 使用场景

### 场景1: 基础多引擎搜索
```
调用 universal_search:
  query: "人工智能最新进展"
  engine: "bing"
  count: 10

结果：返回Bing搜索的10条相关结果
```

### 场景2: 站点限定搜索
```
调用 universal_search:
  query: "site:github.com python教程"
  engine: "google"
  count: 20

结果：返回GitHub上的Python教程相关结果
```

### 场景3: 时间范围筛选
```
调用 universal_search:
  query: "AI发展趋势"
  engine: "baidu"
  count: 10
  freshness: "pm"  # 过去31天

结果：返回百度搜索最近一个月的AI发展趋势
```

### 场景4: 隐私搜索
```
直接访问 DuckDuckGo URL:
  https://duckduckgo.com/html/?q=敏感话题

结果：不追踪搜索历史，保护隐私
```

### 场景5: 知识计算
```
直接访问 WolframAlpha URL:
  https://www.wolframalpha.com/input?i=100+USD+to+CNY

结果：返回美元兑换人民币汇率计算结果
```

---

## 输出格式

### 函数调用结果

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "title": "搜索结果标题",
        "url": "https://example.com",
        "snippet": "搜索结果摘要内容..."
      }
    ],
    "total": 10,
    "engine": "bing",
    "query": "原始查询词"
  },
  "message": "搜索到10条结果，来自Bing搜索"
}
```

### 错误处理

```json
{
  "success": false,
  "error": {
    "code": "API_KEY_MISSING",
    "message": "使用此搜索引擎需要配置API密钥，请先设置环境变量"
  }
}
```

---

## 触发词

| 类别 | 触发词 |
|------|--------|
| 搜索 | 搜索, 多引擎搜索, 全网搜索 |
| 国内引擎 | 百度搜索, 搜狗搜索, 360搜索 |
| 国际引擎 | Google搜索, 谷歌搜索, Bing搜索, Yahoo搜索 |
| 隐私搜索 | 隐私搜索, 无追踪搜索, 匿名搜索 |
| 高级搜索 | 高级搜索, 站点搜索, 文件搜索, 时间筛选 |
| 知识计算 | 汇率转换, 单位换算, 数学求解 |

---

## 安全规则

```yaml
data_isolation: true            # 数据隔离 - 搜索数据不跨会话共享
sensitive_keyword_filter: true  # 敏感词过滤 - 自动过滤敏感查询
privacy_engine_optional: true   # 隐私引擎可选 - 尊重用户隐私选择
search_log_record: true        # 搜索日志 - 仅本地记录便于学习
no_data_exfiltration: true     # 无数据外泄 - 不向第三方传输数据
```

---

## 注意事项

1. **API密钥可选**: 不配置密钥也可使用URL模板搜索
2. **数据隔离**: 搜索数据不跨会话共享
3. **隐私优先**: 敏感查询建议使用DuckDuckGo/Startpage
4. **结构化输出**: 支持多种输出格式定制
5. **容错处理**: API不可用时自动回退到URL模板搜索

---

## 版本历史

- **2.0.0**: 添加函数接口定义，支持API密钥集成，统一Bing/Google/百度三大引擎
- **2.0.2**: 扩展搜索引擎库至60+
- **2.0.1**: 全面重构执行逻辑，添加依赖模块与安全规则
- **1.0.0**: 初始版本，整合国内外主流搜索引擎
