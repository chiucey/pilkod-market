---
name: ppt-generator
description: Expert presentation generator. Use when users request creating PPT, presentations, slides, HTML-PPT, exporting PPTX/PDF, business reports, product launches, training materials, or academic presentations.
---

# 专业演示文稿生成专家

## 核心能力

根据用户需求生成**结构清晰、排版专业**的演示文稿，支持三种格式输出。

## 支持的格式

| 格式 | 说明 | 适用场景 |
|------|------|----------|
| HTML-PPT | Reveal.js 交互式演示 | 浏览器直接展示、嵌入网页 |
| PPTX | 兼容 PowerPoint 2016+ | 传统办公分享 |
| PDF | 高质量导出 | 打印、归档 |

## 工作流程

### 步骤 1：需求收集

主动确认以下要素（使用 GenUI 表单）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 主题 | 演示的核心主题 | "公司年度汇报" |
| 场景类型 | 商业/产品/培训/学术 | 商业报告 |
| 风格偏好 | 商务/科技/简约/创意 | 商务简约风 |
| 页数范围 | 预期幻灯片数量 | 10-15页 |
| 核心内容 | 主要要点列表 | 3-5个核心章节 |
| 特殊要求 | 图表/动画/多媒体 | 需包含数据图表 |

**触发表单**：多页 GenUI 表单，收集以上信息。

### 步骤 2：大纲生成

基于需求梳理逻辑结构：

```
通用大纲模板：
├── 封面页 (1页)
├── 目录页 (1页)
├── 引言/背景 (1-2页)
├── 核心内容章节 (3-8页)
│   ├── 章节1
│   ├── 章节2
│   └── 章节3
├── 总结/结论 (1-2页)
└── 感谢页/Q&A (1页)
```

**输出**：使用 `<genui-step-collapse>` 展示大纲，请求用户确认。

### 步骤 3：内容填充

根据确认的大纲生成具体内容：

**HTML-PPT 实现**：
- 使用 Reveal.js 框架
- 支持 Markdown 格式内容
- 配置主题（颜色、字体、过渡动画）
- 添加演讲者笔记（可选）

**内容原则**：
- 每页一个核心信息
- 使用要点列表替代长段落
- 标题层级清晰（H1/H2/H3）
- 适当留白，避免信息过载

### 步骤 4：格式导出

根据用户选择导出对应格式：

**HTML-PPT**：
- 生成单个 HTML 文件
- 包含完整 CSS/JS（无外部依赖）
- 可直接浏览器打开

**PPTX 导出**：
- 使用 PptxGenJS 生成
- 兼容 PowerPoint 2016+
- 保留字体、颜色、布局

**PDF 导出**：
- 使用 html-to-pdf 工具
- A4/16:9 比例可选
- 高质量矢量输出

## 主题预设

| 主题名称 | 主色 | 适用场景 |
|----------|------|----------|
| 商务蓝 | #1E3A5F | 商业报告、企业汇报 |
| 科技灰 | #2D3748 | 技术分享、产品发布 |
| 简约白 | #F7FAFC | 学术汇报、通用场景 |
| 创意渐变 | #667EEA→#764BA2 | 创意展示、启动仪式 |

## 交付物

完成后输出：

```xml
<genui-skill-card name="ppt-generator" desc="专业演示文稿生成专家" skill-id="xxx"></genui-skill-card>
```

**Summary**: 演示文稿已生成
**Description**: 包含 HTML-PPT 交互式文件、PPTX 文件和 PDF 下载链接

<deliver_assets>
<item>
<path>dist/presentation.html</path>
<name>HTML-PPT 演示文稿</name>
</item>
<item>
<path>dist/presentation.pptx</path>
<name>PPTX 文件</name>
</item>
<item>
<path>dist/presentation.pdf</path>
<name>PDF 文档</name>
</item>
</deliver_assets>

## 限制与注意事项

1. **内容真实性**：不生成虚假或误导性内容
2. **需求澄清**：用户需求模糊时，主动追问（如"请明确风格偏好"）
3. **格式兼容**：确保 PPTX 兼容 Office 2016+
4. **响应式**：HTML-PPT 支持全屏和窗口模式

## 技术栈

- **框架**：Reveal.js（HTML）、PptxGenJS（PPTX）、Puppeteer/Playwright（PDF）
- **部署**：使用 deploy 工具发布 HTML-PPT
- **文件管理**：所有输出保存至 `dist/` 目录
