# AI热门知识收集 - 参考标准

## 信誉度评估详细标准

### A+ 级别（权重1.0）
- arXiv / Nature / Science 等权威学术平台论文
- 官方API文档（OpenAI, Anthropic, Google AI等）
- 顶级会议论文（ NeurIPS, ICML, ICLR, CVPR等）
- 官方产品发布公告
- 知名研究机构官方博客

### A 级别（权重0.8）
- 知名开发者/研究者技术博客
- 主流科技媒体深度报道（Wired, The Verge, TechCrunch等）
- GitHub trending 项目（有大量stars和活跃维护）
- Hacker News / Lobsters 高评分讨论
- 知名AI社区官方公告

### B 级别（权重0.6）
- 产品发布/更新公告（创业公司、中型公司）
- Reddit r/MachineLearning 热门讨论
- Twitter/X 开发者社区讨论
- YouTube 技术教程（知名频道）
- Medium /DEV.to 优质技术文章

### C 级别（权重0.3）
- 社交媒体普通讨论
- 未经验证的传言
- 小众论坛讨论
- 个人博客（无专业背书）

## 质量门槛规则

1. **最低标准**：每个收录的term必须有至少1个B级来源
2. **推荐标准**：优先收录有A级以上来源的term
3. **时间门槛**：所有来源必须是过去7天内的内容
4. **多样性**：每个term应包含2-3个不同来源的交叉验证

## 热门term识别关键词

### 技术类
- "breakthrough", "new model", "released", "announced"
- "open source", "research paper", "architecture"
- "benchmark", "state-of-the-art", "performance"

### 产品类
- "launch", "available now", "beta", "update"
- "pricing", "free tier", "API", "integration"

### 社区类
- "trending", "viral", "discussion"
- "opinion", "review", "comparison"
- "tutorial", "how to", "guide"

## 输出格式模板

```markdown
# AI热门知识摘要 - [日期范围]

## 概览
- 识别热门terms数量：X个
- 可信度分布：A+级 X个 | A级 X个 | B级 X个
- 主要领域：...

---

## [Term 1: 术语名称]

**可信度评级**：⭐⭐⭐⭐⭐ (A+)

**定义**：
[2-3句话的精确定义]

**权威来源**：
- [来源名称](URL) - [来源类型]

**使用示例**：

```python
# Python示例
import relevant_lib

# 核心功能展示
result = relevant_lib.function(input_data)
print(result)
```

**社区反响**：
- 👍 正面：[简述正面评价]
- 👎 质疑：[简述质疑/批评]
- 💡 实际应用：[真实应用场景]

**验证链接**：
[原始来源链接]

---

*收集时间：[具体时间] | 可信度阈值：B级以上*
```
