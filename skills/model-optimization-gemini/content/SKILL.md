---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fa7c1534bc91fd40da49a803559c67b3
    PropagateID: fa7c1534bc91fd40da49a803559c67b3
    ReservedCode1: 3046022100d30b36c07fa07a20863016067f36570f8bdb587d17f5f27ede34e7882f542bab0221008b4b102dcc9c53ff7d669f927b0fa086dfbf17def195c0d957c8680d289b603f
    ReservedCode2: 3046022100c6d3dd2073ba540929ced87a8dbe3ea1f10047fc3375ce0f0c5ab99f370c0cf7022100d568dfb10fa0d92881f8a1478cc6c03b50bb0508e5a1f76d9a22b0361f447aec
description: Gemini模型优化指南。1M窗口几乎不压缩/并行function calling/原生多模态/Search Grounding。
name: model-optimization-gemini
platforms:
    - OpenClaw
    - Gemini
tags:
    - model-optimization
    - Gemini
    - multi-modal
    - compression
    - parallel-calling
updated: "2026-04-03"
version: 1.1.0
---

# Google Gemini 模型优化 · 核心速查
> 版本：v1.1.0
> 来源：Gemini Claude Code研究 × 源码级优化分析

---

## 一、Gemini特性与优化对照

| 特性 | 值 | 优化动作 |
|------|---|---------|
| function calling | ✅ 并行支持 | 默认并行所有安全工具 |
| 上下文窗口 | **1M-2M tokens** | 几乎不压缩 |
| 多模态 | ✅ 原生 | 图像/视频/音频直接作为工具输入 |
| Google Search Grounding | ✅ | 替代WebSearchTool，减少幻觉 |
| Code Execution | ✅ 内置 | 减少BashTool依赖 |
| 流式 | ✅ | 全链路流 |

---

## 二、压缩策略重大调整（核心区别）

### Claude Code → Gemini 阈值迁移

| 参数 | Claude默认值 | Gemini优化值 | 原因 |
|------|------------|------------|------|
| COMPRESSION_THRESHOLD | 80% | **95%** | 1M窗口几乎不需要 |
| HARD_TRUNCATE | 95% | **99%** | 最后手段，极端保守 |
| SESSION_BUDGET | 50K | **500K** | 500K内不压缩 |
| SNIP_ENABLED | 可选 | **✅ 保留** | 清理僵尸消息仍有价值 |

### 为什么snipCompact仍然需要？

即使窗口很大，**冗余消息仍会降低注意力**：
```
· 连续重复的tool_result（后续覆盖前序）
· 被编辑操作覆盖的旧文件读取结果
· 错误恢复过程中产生的垃圾消息
· 长任务中早已无关的历史状态
```

**Gemini snip规则（精简版）：**
```
□ 连续重复tool_result → 保留最新
□ 被覆盖的文件读取 → 删除旧读结果
□ 连续Bash输出 → 合并
□ 保留关键决策点和用户确认
```

---

## 三、并行函数调用（Gemini独家优势）

### Claude Code限制

```
串行执行：等上一个tool_result，再发下一个
→ 效率低，但容易调试
```

### Gemini优化

```
并行执行：所有安全工具同时发出，同时返回
→ 效率提升3-5倍
→ 适用于无依赖的工具调用
```

**安全并行化的条件：**
```
可并行：
  · Read文件A + Read文件B（无依赖）
  · WebSearch + Bash时间戳（无依赖）
  · 多个独立计算

不可并行：
  · Read文件A + Edit文件A（依赖）
  · 第一个API调用的结果影响第二个输入
  · 涉及共享状态的写操作
```

---

## 四、多模态工具链（Gemini独家优势）

### Claude Code多模态流程

```
图片 → Base64编码 → API调用 → 处理
         ↓
      占用大量token
```

### Gemini原生多模态

```
图片/视频/音频 → 直接作为工具参数传入
             ↓
        原生多模态支持
             ↓
        大幅节省token
```

**Gemini多模态工具优先使用：**
```
✅ Google Vision API → 直接处理图片
✅ Gemini内置图像理解 → 替代BLIP/VLMEye
✅ 视频帧提取 → Gemini直接处理视频
✅ 音频处理 → Gemini直接处理音频
```

---

## 五、Google Search Grounding（减少幻觉）

### Claude Code流程

```
用户问：最新bug修复方法？
→ WebSearch搜索 → 读取结果 → 整合回答
→ 问题：搜索结果可能过时/幻觉
```

### Gemini + Search Grounding

```
用户问：最新bug修复方法？
→ Google Search Grounding → 直接使用搜索结果
→ 实时数据源，减少幻觉
→ 适用：API文档、技术问题、新闻事件
```

---

## 六、OpenClaw + Gemini配置建议

```json
{
  "model": "gemini-2.0-flash",
  "compression": {
    "enabled": true,
    "snip_threshold": 0.70,
    "auto_compact_threshold": 0.95,
    "hard_truncate": 0.99,
    "session_budget_tokens": 500000
  },
  "tools": {
    "parallel_by_default": true,
    "google_search_grounding": true,
    "multimodal_native": true
  }
}
```

---

## 七、适用场景判断

**用Gemini优化方案，当：**
```
□ 上下文窗口 > 500K tokens
□ 大型代码库分析（>10万行）
□ 多模态任务（图片/视频+文本）
□ 需要减少幻觉（用Search Grounding）
□ 需要并行加速（无依赖工具）
```

**不用Gemini方案，当：**
```
□ 需要KAIROS式自主7×24运行（Claude Code）
□ 需要最强代码补全（Claude Code Sonnet）
□ 窗口 < 200K（用MiMo方案）
```

---

## 八、Gemini 模型家族全景

### 8.1 演进时间线

| 时间 | 版本 | 里程碑 |
|------|------|--------|
| 2023-12 | Gemini 1.0 | 首发，Nano/Pro/Ultra三个尺寸 |
| 2024-02 | Gemini 1.5 Pro | 100万token上下文窗口，MoE架构 |
| 2024-02 | Gemini 1.5 Flash | 轻量快速版，100万token |
| 2024-12 | Gemini 2.0 Flash | 新一代，原生工具调用+多模态增强 |
| 2025-03 | Gemini 2.5 Pro | 推理能力大幅提升，支持thinking模式 |
| 2025-03 | Gemini 2.5 Flash | 速度更快的2.5系列，性价比之选 |

### 8.2 版本能力矩阵

| 能力 | Pro | Flash | Flash-Lite | Thinking (2.5) |
|------|-----|-------|------------|----------------|
| 推理深度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐+ |
| 响应速度 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 编程能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 多模态 | 全部 | 全部 | 图片+文本 | 全部 |
| 上下文窗口 | 1M-2M | 1M | 1M | 1M |
| Function Calling | ✅ | ✅ | ✅ | ✅ |
| Search Grounding | ✅ | ✅ | ✅ | ✅ |
| Code Execution | ✅ | ✅ | ❌ | ✅ |

### 8.3 Token限制/速度/价格对比

| 模型 | 输入上限 | 输出上限 | 输入价格(每M token) | 输出价格(每M token) | 速度评级 |
|------|---------|---------|-------------------|-------------------|---------|
| Gemini 2.5 Pro | 1M | 65K | $1.25-$2.50 | $10-$15 | ⭐⭐⭐ |
| Gemini 2.5 Flash | 1M | 65K | $0.15-$0.60 | $0.60-$3.50 | ⭐⭐⭐⭐ |
| Gemini 2.0 Flash | 1M | 8K | $0.10 | $0.40 | ⭐⭐⭐⭐⭐ |
| Gemini 1.5 Pro | 2M | 8K | $1.25-$2.50 | $5-$10 | ⭐⭐⭐ |
| Gemini 1.5 Flash | 1M | 8K | $0.075-$0.15 | $0.30-$0.60 | ⭐⭐⭐⭐ |

> 注：价格按区间表示输入≤128K和>128K两档，实际价格以Google Cloud官网为准。

### 8.4 各版本最佳适用场景

- **Gemini 2.5 Pro**：复杂推理任务、多步规划、高质量代码生成、深度文档分析
- **Gemini 2.5 Flash**：高吞吐API服务、聊天应用、快速原型开发、大批量处理
- **Gemini 2.0 Flash**：轻量级任务、实时交互、成本敏感型项目
- **Gemini 1.5 Pro**：超长文档（>1M tokens）、视频分析、大规模数据集处理
- **Gemini 1.5 Flash**：高频调用场景、简单分类/提取任务

---

## 九、Prompt Engineering 最佳实践

### 9.1 System Prompt 设计模式

**角色设定模板：**
```
You are a [角色]. Your expertise includes [领域1], [领域2].
Always [行为准则1]. Never [行为禁忌1].
When uncertain, [应对策略].
```

**输出格式控制：**
```
Respond in the following format:
---
Summary: [一句话摘要]
Details: [详细说明，2-5段]
Confidence: [High/Medium/Low]
---
```

**边界约束技巧：**
- 使用`## Constraints`部分明确列出限制
- 用负向指令补充正向指令（"Do X. Don't assume Y."）
- 对于安全敏感任务，将约束放在prompt最开头和结尾各一次（首尾效应）

### 9.2 Few-shot 示例设计原则

**3-shot vs 5-shot 选择指南：**

| 场景 | 推荐shot数 | 原因 |
|------|-----------|------|
| 简单格式转换 | 2-3 | 模式简单，少量示例即可 |
| 复杂推理任务 | 4-5 | 需要展示多种推理路径 |
| 分类任务 | 每类至少1个 | 确保所有类别有代表 |
| 创意生成 | 2-3 | 过多示例会限制创造力 |

**示例多样性原则：**
1. 覆盖边界情况（正常 + 边缘 + 异常输入）
2. 长度多样化（简短 + 中等 + 详细输出）
3. 避免示例间过度相似（模型会复制而非泛化）

```python
# 有效few-shot示例结构
examples = [
    {"input": "简单案例", "output": "标准输出"},        # 正常情况
    {"input": "边缘案例", "output": "特殊处理输出"},     # 边界情况
    {"input": "复杂案例", "output": "详细推理输出"},     # 复杂情况
]
```

### 9.3 Chain-of-Thought 推理优化

**显式 CoT（推荐用于复杂任务）：**
```
Think step by step:
1. First, identify the key variables...
2. Then, analyze the relationships...
3. Finally, derive the conclusion...
```

**隐式 CoT（推荐用于简单任务）：**
```
Analyze this and provide your answer.
[模型内部推理，不展示过程]
```

**选择指南：**

| 任务复杂度 | CoT模式 | 原因 |
|-----------|---------|------|
| 简单查询/检索 | 无CoT | 不需要额外推理 |
| 中等分析 | 隐式CoT | 节省输出token |
| 复杂推理/数学 | 显式CoT | 提高准确性10-20% |
| 多步决策 | 显式CoT | 便于审查和调试 |

### 9.4 长上下文 Prompt 组织策略

**128K+ 场景下的信息编排：**

```
# 系统角色定义（放在最前面）
[system prompt]

# 核心任务说明（紧随其后）
[task description]

# 参考文档（中间部分，按重要性排序）
## 文档1：最重要的参考资料
[content]

## 文档2：次要参考资料
[content]

# 输出要求（放在最后，靠近回答生成位置）
[output format requirements]
```

**关键原则：**
- 关键信息放在prompt的**开头和结尾**（Lost in the Middle问题）
- 使用明确的分隔符（`##`, `---`, XML标签）组织不同部分
- 超过500K tokens时，考虑分段处理而非一次输入
- 对长文档添加目录/索引，帮助模型快速定位

### 9.5 多语言 Prompt 优化

**中英混排最佳实践：**
- 指令语言与期望输出语言一致（中文指令→中文输出）
- 技术术语可保留英文（API、SDK、function calling等）
- 在prompt中明确指定输出语言：`用中文回答，专业术语保留英文原文`

**术语一致性技巧：**
```
术语表（请在输出中保持一致）：
- "machine learning" → 机器学习
- "fine-tuning" → 微调
- "inference" → 推理（不要用"推断"）
- "prompt" → 提示词（不要用"提示"）
```

---

## 十、多模态专项指南

### 10.1 图片分析 Prompt 设计

不同分析目标需要不同的prompt策略：

**场景描述型：**
```
Describe this image in detail. Include:
- Objects and their positions
- Colors, lighting, and atmosphere
- Text content if any (exact transcription)
- Overall scene context
```

**OCR/文字提取型：**
```
Extract ALL text visible in this image.
Preserve original formatting and layout.
Mark uncertain characters with [?].
```

**图表/数据提取型：**
```
Analyze this chart/graph:
1. What type of chart is this?
2. List all data points with exact values
3. Identify trends and outliers
4. Provide the data in table format
```

**流程图/架构图型：**
```
Parse this diagram:
1. List all nodes/blocks with labels
2. Describe connections and data flow
3. Identify decision points
4. Convert to structured text representation
```

### 10.2 视频理解技巧

**帧采样策略：**

| 场景 | 建议FPS | 原因 |
|------|---------|------|
| 演示/教程视频 | 1fps | 每秒都有新信息 |
| 对话/访谈 | 0.2fps | 内容变化慢，关注音频 |
| 动作/运动 | 2-4fps | 捕捉连续动作 |
| 监控/安全 | 0.1fps | 只需关键时刻 |

**时序推理prompt：**
```
Watch this video and answer:
1. What happens in chronological order?
2. At what timestamp does [事件] occur?
3. Are there any sudden changes or transitions?
4. Describe the cause-effect relationships.
```

### 10.3 音频处理场景

**转录优化prompt：**
```
Transcribe this audio exactly as spoken.
- Preserve filler words and pauses
- Mark inaudible sections as [inaudible]
- Identify different speakers as Speaker A, Speaker B
- Include timestamps every 30 seconds
```

**情绪分析prompt：**
```
Analyze the emotional tone of this audio:
- Primary emotion: [happy/sad/angry/neutral/...]
- Intensity: [1-10]
- Tone shifts: list timestamps where emotion changes
- Confidence level for each assessment
```

### 10.4 代码+图表联合分析

```
Analyze this screenshot of a [IDE/dashboard/terminal]:
1. Extract all visible code
2. Identify the programming language
3. Note any error messages or warnings
4. If there's a chart/visualization, describe the data it shows
5. Suggest improvements based on what you see
```

### 10.5 多模态 Token 计算

| 内容类型 | Token计算方式 |
|---------|-------------|
| 图片 | 约258-1032 tokens/张（取决于分辨率和细节） |
| 视频 | 按帧数×每帧token + 音频token |
| 音频 | 约32 tokens/秒 |
| PDF | 按页转换为图片后计算 |
| 文本 | 标准tokenization（1汉字≈2 tokens） |

**成本优化建议：**
- 图片：适当降低分辨率可节省50-75% tokens
- 视频：只采样关键帧而非全帧率
- 音频：长音频分段处理，每段5-10分钟

---

## 十一、实战案例对比

### 11.1 代码生成对比

**任务：实现一个LRU缓存**

**Prompt：**
```
Implement an LRU cache in Python with O(1) get and put operations.
Include type hints and docstrings.
```

| 维度 | Gemini 2.5 Pro | Claude Sonnet 4 | GPT-4o |
|------|---------------|----------------|--------|
| 代码质量 | 使用OrderedDict，简洁 | 手写双向链表，完整 | OrderedDict，含单元测试 |
| 类型提示 | ✅ 完整 | ✅ 完整 | ✅ 完整 |
| 文档 | 中等详细 | 详细 | 最详细 |
| 边界处理 | 基本 | 完善 | 完善 |

**优化版本prompt（针对Gemini）：**
```
Implement an LRU cache in Python.
Requirements:
- O(1) for both get and put
- Type hints on all methods
- Docstrings with Args/Returns/Raises
- Thread-safe version included
- Unit tests for edge cases
- Use collections.OrderedDict
```

### 11.2 长文档分析

**任务：分析500页技术白皮书**

**分段策略：**
```python
# 推荐的分段处理流程
1. 先用摘要prompt获取全局概览（1次调用）
2. 按章节分批处理（每次≤100K tokens）
3. 对每段提取关键信息并结构化
4. 最后汇总生成综合分析
```

**Gemini优势：** 1M窗口可一次性处理完整文档，避免分段导致的信息丢失。

### 11.3 数据分析

**任务：处理复杂嵌套JSON/CSV**

**Prompt优化：**
```
Analyze this dataset:
[paste data]

Steps:
1. Identify schema and data types
2. Detect missing values and outliers
3. Compute summary statistics
4. Suggest 3-5 visualizations
5. Provide insights in bullet points
```

**Gemini优势：** Code Execution内置，可直接运行pandas/numpy代码处理数据。

### 11.4 创意写作对比

| 维度 | Gemini | Claude | GPT |
|------|--------|--------|-----|
| 风格控制 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 情感表达 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 长篇连贯性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 中文自然度 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

**Gemini创意写作优化prompt：**
```
Write a [genre] story with:
- Tone: [specific tone word]
- Pacing: [fast/meditative/varied]
- Avoid: [cliché patterns to avoid]
- Style reference: [author or work name]
```

---

## 十二、常见坑与避雷

### 12.1 幻觉高风险场景

| 场景 | 风险等级 | 缓解措施 |
|------|---------|---------|
| 最新API文档引用 | 🔴 高 | 使用Search Grounding |
| 数值计算 | 🔴 高 | 使用内置Code Execution |
| 法律/医疗建议 | 🔴 高 | 明确要求引用来源+免责声明 |
| 小众技术栈 | 🟡 中 | 提供上下文参考文档 |
| 历史事件细节 | 🟡 中 | 使用Search Grounding验证 |

### 12.2 过度拒绝处理

当Gemini错误拒绝合理请求时：
1. 重新表述请求，避免触发关键词
2. 添加上下文说明合法用途
3. 使用更具体的prompt替代泛化prompt
4. 如使用API，检查Safety Settings配置

```json
// 降低误拒的safety配置
{
  "safety_settings": [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
  ]
}
```

### 12.3 JSON输出可靠性

**提升JSON稳定性的技巧：**
1. 在prompt中提供完整JSON schema
2. 使用`response_mime_type: "application/json"`参数（API）
3. 包含1-2个few-shot示例
4. 避免要求嵌套过深的结构（建议≤3层）

```python
# API调用时指定JSON输出
response = model.generate_content(
    prompt,
    generation_config={"response_mime_type": "application/json"}
)
```

### 12.4 API vs 网页版差异

| 维度 | API | 网页版(Gemini App) |
|------|-----|-------------------|
| 上下文窗口 | 完整（1M-2M） | 可能有限制 |
| Search Grounding | 需显式启用 | 默认启用 |
| Code Execution | 需显式启用 | 内置可用 |
| Safety Settings | 可自定义 | 固定配置 |
| 文件上传 | 通过API参数 | 拖拽上传 |
| 价格 | 按token计费 | 免费/Premium订阅 |

### 12.5 模型切换注意事项

从其他模型迁移到Gemini时：
- **从Claude迁移**：Gemini并行function calling更强，但创意写作风格控制可能不如Claude细腻
- **从GPT迁移**：Gemini多模态更强，但某些格式控制（如严格的Markdown）可能需要额外约束
- **从MiMo迁移**：Gemini窗口大得多，可减少压缩，但成本也显著更高
- **通用建议**：迁移后先跑一遍核心任务的benchmark，对比输出质量

---

*版本：v1.1.0 | 2026-04-03*
