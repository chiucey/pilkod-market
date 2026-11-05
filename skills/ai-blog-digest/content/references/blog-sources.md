---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fc46b10dd93bef88665cad8cd3daef8d
    PropagateID: fc46b10dd93bef88665cad8cd3daef8d
    ReservedCode1: 304402200e39dd909819e4cfce955dbd307f107b2c5ddd4ede38037b1ab0df7e7709f5c30220388e65480d6a893cf763a03437afbaff2a9792ddfa82985f4f20c79480112987
    ReservedCode2: 3046022100f7b130961c18b3165d844fbc832c33d9ba0dc9ac180b581df03b1c07f8963f94022100ee7648a045559baea41ea0e7818d7fa3d00adaa0cbf3dd89cd36eef6c6711e55
---

# AI 前沿公司博客来源参考

## 官方博客 URLs

### 1. OpenAI
- **主站**: https://openai.com
- **博客**: https://openai.com/blog
- **RSS**: https://openai.com/api/v1/rss
- **语言**: 英文

### 2. Anthropic
- **官网**: https://www.anthropic.com
- **新闻**: https://www.anthropic.com/news
- **博客**: https://www.anthropic.com/news (同页面)
- **语言**: 英文

### 3. Google AI
- **AI博客**: https://blog.google/technology/ai/
- **DeepMind**: https://deepmind.google/discover/blog/
- **Google Research**: https://blog.google/technology/research/
- **语言**: 英文

### 4. DeepMind
- **博客**: https://deepmind.google/discover/blog/
- **官网**: https://deepmind.google
- **语言**: 英文

### 5. Meta Engineering
- **工程博客**: https://engineering.fb.com
- **Meta AI**: https://ai.meta.com/blog/
- **语言**: 英文

### 6. NVIDIA
- **官方博客**: https://blogs.nvidia.com
- **深度学习**: https://blogs.nvidia.com/blog/category/deep-learning/
- **AI技术**: https://blogs.nvidia.com/blog/category/artificial-intelligence/
- **语言**: 英文

## 抓取策略

### 列表页抓取
每个博客的首页/列表页包含最近5-20篇文章，是主要的抓取入口。

### 内容提取 Prompt 模板

```
提取该博客页面中的文章列表，包括：
1. 文章标题
2. 发布日期
3. 文章链接
4. 简短摘要(如有)

返回JSON格式：
{
  "source": "公司名",
  "articles": [
    {
      "title": "文章标题",
      "date": "YYYY-MM-DD",
      "url": "完整URL",
      "summary": "摘要或预览文字"
    }
  ]
}
```

## 常见问题

### Q: 如何处理付费内容？
A: 仅抓取免费公开内容，标记付费文章。

### Q: 博客结构变化怎么办？
A: 根据实际页面结构调整提取逻辑。

### Q: 抓取频率建议？
A: 每日1次或每周1次，避免过于频繁。
