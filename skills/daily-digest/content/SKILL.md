---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 85a0b1fa555e591d0196aa70aa1359c8
    PropagateID: 85a0b1fa555e591d0196aa70aa1359c8
    ReservedCode1: 30460221009a18c51549c6758a64c6afb01ab4f5ef5b0d219535a19920a7aedf81be9d08b3022100c14f48aed9e41f087ec730fc613e52376c2d9fa918c034231aec6d51c86f51aa
    ReservedCode2: 304502202b01cef9d2da16960c67bbae963b25fe8a2c176978d5651272196d041115a981022100d9708b70d319281dfdef01a49d2a0b9f206e1f16f322f934ef86973e5435577e
description: 每日行业动态收集技能。每天自动收集前一天的全球金融、科技和财务公司行业动态，整理成结构化摘要报告。当用户说"帮我收集今天的动态"、"每天行业动态"、"行业日报"、"今日财经要闻"、"财务公司行业动态"时触发此技能。
name: daily-digest
---

# 每日行业动态收集

## 功能说明

每天自动收集前一天的三个方向动态：
1. **金融动态**：全球金融行业重大新闻，≤20条
2. **科技动态**：全球科技行业重要新闻，≤20条
3. **财务公司行业动态**：企业集团财务公司行业和同行新闻，≤10条

无重大新闻时，对近期财务公司行业趋势进行总结，并标注数据来源日期。

## 输出格式

将结果写入 `~/.openclaw/daily-digest/[前一天日期].json`，格式如下：

```json
{
  "date": "[前一天日期，YYYY-MM-DD]",
  "generatedAt": "[生成时间，ISO8601]",
  "financial": {
    "summary": "一句话总结今日金融形势",
    "items": [
      {
        "title": "新闻标题",
        "source": "来源媒体",
        "summary": "50字以内摘要",
        "url": "原文链接"
      }
    ]
  },
  "tech": {
    "summary": "一句话总结今日科技形势",
    "items": [...]
  },
  "treasury": {
    "summary": "一句话总结今日财务公司行业动态",
    "items": [...]
  }
}
```

## 搜索策略

### 金融动态
用 `batch_web_search` 并发搜索（数据范围：前一天）：
- `"[日期] global financial news"`
- `"[日期] central bank monetary policy"`
- `"[日期] banking industry news"`
- `"[日期] stock market global"`
- `"[日期] financial regulation"`

用 `extract_content_from_websites` 提取重要文章的完整内容。

### 科技动态
用 `batch_web_search` 并发搜索（数据范围：前一天）：
- `"[日期] tech industry news"`
- `"[日期] AI artificial intelligence news"`
- `"[日期] technology company earnings"`
- `"[日期] startup funding news"`
- `"[日期] semiconductor chip news"`

### 财务公司行业动态
用 `batch_web_search` 并发搜索：
- `"企业集团财务公司 [日期] 行业动态"`
- `"财务公司 资金管理 司库 [日期]"`
- `"treasury management financial company China [日期]"`
- `"企业财务公司 监管 动态"`

若搜索结果少于5条，扩大搜索时间范围至近7天；若仍不足，补充近期行业趋势内容（不超过5条），注明**数据来源日期**。

## 日期计算

**重要**：每次执行前先运行：
```bash
date -u "+%Y-%m-%d"
```
得出当天 UTC 日期后减1天，即为"前一天"。

## 内容筛选标准

- 金融：央行政策、大型银行/机构动态、重大监管变化、系统性市场事件优先
- 科技：AI/半导体/头部科技公司/融资并购/监管动态优先
- 财务公司：企业集团财务公司、司库管理、资金池、监管政策、行业趋势优先

## 交付方式

1. 将 JSON 文件写入 `~/.openclaw/daily-digest/`
2. 在当前会话回复结构化摘要（markdown 格式）
3. 若有内容，优先展示"一句话总结 + 标题列表"
