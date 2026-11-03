---
name: baoyu-zhihu
description: 生成知乎风格文案和配套信息图，适合专业讨论、深度观点、知识干货类内容。提供 6 种视觉风格和 5 种内容布局，支持生成知乎回答封面图和配图。触发词：知乎文案、知乎回答、知乎图片、知乎风格、知乎配图、ZhiHu content、知乎干货。
---

# 知乎内容生成技能

生成知乎风格的深度内容：文案 + 配套图片，适合专业讨论、知识干货、行业分析类主题。

## 使用方式

直接描述需求即可：

**提供文章主题**：帮我生成知乎内容，主题是"AI是否会取代程序员"
**提供内容大纲**：帮我把这些要点写成知乎回答格式：[...]
**直接指定风格**：生成知乎图片，主题：产品经理 vs 项目经理

## 核心参数

| 参数 | 选项 |
|------|------|
| `--style` | professional / minimalist / academic / editorial / data-viz / dark-elegant |
| `--layout` | structured / thesis / comparison / narrative / data-heavy |
| 图片数量 | 1-6 张（默认根据内容长度推荐）|

## 风格选择指引

| 内容类型 | 推荐风格 |
|---------|---------|
| 行业分析、商业洞察、数据趋势 | `professional` / `data-viz` |
| 概念解析、知识科普、原理讲解 | `academic` |
| 个人经历分享、观点表达 | `editorial` |
| 简洁清晰、无干扰的专业感 | `minimalist` |
| 科技/互联网/硬核话题 | `dark-elegant` |

## 知乎内容结构策略

**知乎高赞回答的黄金公式**：
1. **开头**（Hook）：一句话激发共鸣或颠覆认知
2. **结论先行**：先给结论，再说原因
3. **逻辑递进**：按重要性或时间顺序层层展开
4. **数据支撑**：引用数据、研究、案例
5. **个人见解**：独特视角，与众不同的判断
6. **行动建议**：读者能做什么

## 输出结构

每轮生成的内容保存在 `zhihu-content/{topic-slug}/` 目录：

```
zhihu-content/{topic-slug}/
├── analysis.md          # 内容分析
├── outline.md            # 最终大纲
├── prompts/              # 各图生成提示词
│   ├── 01-cover-[slug].md
│   └── ...
├── 01-cover-[slug].png  # 封面图
└── ...
```

## 详细参考

- **视觉风格**：`references/presets/` — 各风格的详细定义
- **元素指南**：`references/elements/` — 画布规格、字体装饰、视觉层次
- **工作流**：`references/workflows/` — 内容分析、大纲模板、提示词组装
- **配置**：`references/config/` — 偏好设置
