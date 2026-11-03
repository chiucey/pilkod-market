---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 84f8a985f87ff82a620ed61b2052cbdd
    PropagateID: 84f8a985f87ff82a620ed61b2052cbdd
    ReservedCode1: 304502200cde92796782effce4c71b4c9eaa063275dd8f261241674d6ea2a22f30fcde62022100f05ea2c68b122f212b1783fe4b9c59e61a80d3c955c2143500976f757d8611a8
    ReservedCode2: 30440220325cf95336913525aa2bed074b37cb087f7709d708a2e5c9a523dacea1cce04002202421d40270cb197ac35b1d33bea60c47c8b8691aa8e506ea38a73929a5c221da
description: 'Paper presentation generator for group meeting literature reports. Activates when users upload PDF literature or provide paper names requesting group meeting presentation PPT generation. Functions include: reading paper content, extracting key information, and generating complete academic presentation slides (covering all necessary sections such as cover, background, scientific questions, research content, methodology, experimental details, results discussion, and conclusions).'
name: paper-presentation-generator
---

# 文献汇报PPT生成技能

## 触发条件

当用户上传PDF文献或提供文献名称，要求生成组会汇报PPT时激活此技能。

## 工作流程

### 1. 文献输入与读取

**输入方式A - 文件上传：**
- 用户上传PDF文件
- 使用 `extract_pdfs_full_content` 工具提取完整文献内容
- 使用 `extract_pdfs_key_info` 工具提取关键信息（标题、作者、摘要、关键词）

**输入方式B - 文献名称：**
- 用户提供文献标题或DOI
- 使用网络搜索查找文献PDF链接
- 下载并提取文献内容

### 2. 文献深度分析

解析并提取以下关键信息：

| 信息类别 | 具体内容 |
|---------|---------|
| **基础信息** | 标题、作者、期刊、年份、DOI |
| **研究背景** | 领域现状、研究缺口、研究意义 |
| **科学问题** | 待解决的核心问题、研究假设 |
| **研究内容** | 主要研究目标、具体工作 |
| **方法原理** | 技术路线、实验方法、理论模型 |
| **样品信息** | 样品来源、制备方法、表征手段 |
| **数据处理** | 数据校正方法、分析软件、处理流程 |
| **结果图解** | 所有图表的详细解读 |
| **结论** | 主要发现、创新点 |
| **局限性** | 研究不足、未来方向 |

### 3. PPT结构规划

生成的PPT必须包含以下页面：

```
1. 封面页 (Cover)
   - 论文标题
   - 作者信息
   - 汇报人/日期

2. 目录页 (Table of Contents)
   - 汇报大纲

3. 背景介绍 (Background)
   - 研究领域概述
   - 研究现状
   - 存在的问题

4. 科学问题 (Research Questions)
   - 领域关键问题
   - 本文聚焦的问题

5. 研究内容 (Research Content)
   - 研究目标
   - 主要工作概述

6. 方法原理 (Methodology)
   - 技术路线图
   - 方法原理说明

7. 样品与测量 (Samples & Measurements)
   - 样品来源
   - 制备方法
   - 表征手段

8. 数据处理 (Data Processing)
   - 数据校正方法
   - 分析流程
   - 使用的软件/工具

9. 结果与讨论 (Results & Discussion)
   - 每张图/表的详细解读
   - 关键发现
   - 结果分析
   - 与前人工作对比

10. 结论 (Conclusion)
    - 主要结论
    - 创新点
    - 科学贡献

11. 局限性 (Limitations)
    - 研究局限
    - 未来展望

12. 致谢/参考文献 (References)
```

### 4. PPT生成执行

使用 `pptx-generator` 技能生成专业PPT：

**生成命令：**
```
调用 expert-skills:pptx-generator
输入：完整的文献分析内容
输出：HTML/PPTX格式的演示文稿
```

**PPT样式要求：**
- 学术风格：简洁、专业、清晰
- 配色：深色主题或浅色主题可选
- 字体：标题黑体/无衬线，正文清晰易读
- 图表：保留原文献图表，配详细图注

## 质量标准

### 内容完整性
- ✅ 覆盖所有指定章节
- ✅ 图表解释详尽（每个图的X轴、Y轴、趋势、关键数据点均需说明）
- ✅ 方法描述准确

### 表达准确性
- ✅ 忠实于原文内容
- ✅ 专业术语准确使用
- ✅ 数据解读客观

### PPT专业度
- ✅ 布局合理，信息层次清晰
- ✅ 字体大小适中（标题24pt+，正文18pt+）
- ✅ 图表清晰，配色协调

## 输出格式

最终交付物：
1. **HTML演示文稿** - 可在浏览器直接查看
2. **PPTX文件** - 可下载后在本地编辑
3. **文献摘要** - 关键信息汇总文档

## 错误处理

| 场景 | 处理方式 |
|-----|---------|
| PDF提取失败 | 提示用户检查文件格式，尝试重新上传 |
| 文献信息不完整 | 标注缺失内容，基于可用信息生成 |
| 网络搜索无结果 | 请用户提供更多线索或直接上传PDF |

## 快速使用示例

**示例1 - 上传文件：**
```
用户：请帮我生成这篇文献的汇报PPT
附件：xxx.pdf
系统：提取PDF内容 → 分析文献 → 生成完整PPT
```

**示例2 - 提供名称：**
```
用户：帮我汇报这篇文献：Nature 2023 钙钛矿太阳能电池最新进展
系统：搜索文献 → 下载PDF → 提取内容 → 生成PPT
```
