---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8a3f487891a9ae125503ec5d214357d0
    PropagateID: 8a3f487891a9ae125503ec5d214357d0
    ReservedCode1: 3046022100faa24fea6dd6cf4a53e800dd278239b6a279d07da7c7ce099fbc24cdbc6c05ab022100d780059d836823c9eef6d5fab7d02e60c32ee7b7464dc6dcec2f6092446f1ec9
    ReservedCode2: 30450221009ed817c7a2a363ca960e87c83b074e2b2a8a437a6e417bbedf34541160833e77022077ab17efbf107961a712bce528828d9ab2ad3b02c0ad839e714c9fad735fa166
description: 将政策文件文本转换为政策解读长图HTML页面。当用户发送政策原文或政策解读内容，要求生成政策解读长图、政策解读信息图、政策解读海报、政策解读H5长页面时使用。支持学习参考长图风格后自动匹配生成。
name: policy-long-image-generator
---

# 政策解读长图生成器

本技能帮助用户将政策文件转换为适合手机端浏览和长图截图的政策解读页面。

## 工作流程

### 步骤1：接收并分析用户输入

**方式A - 提供参考长图：**
用户发送政策解读长图参考图 + 政策文件原文文本

**方式B - 仅提供政策文本：**
用户直接发送政策文件原文文本

### 步骤2：学习参考长图风格（如用户提供）

分析参考图的关键视觉要素：

| 维度 | 分析内容 |
|------|----------|
| **配色方案** | 主色调、辅色、强调色、背景色 |
| **字体规范** | 标题字体、字号层级、正文字体 |
| **布局结构** | 页面宽度、边距设置、卡片间距 |
| **标题层级** | H1/H2/H3的字号和样式差异 |
| **图标风格** | 图标类型（线性/填充）、大小、颜色 |
| **分隔元素** | 分隔线样式、装饰元素、留白比例 |
| **卡片设计** | 圆角、阴影、边框、背景色 |

### 步骤3：提炼政策核心信息

从政策文本中提取以下关键信息：

```
- 政策标题
- 政策编号/发文字号
- 发布机构
- 发布日期
- 核心要点（3-5条）
- 关键条款解读
- 亮点分析
- 适用范围
- 实施时间
- 重要数据指标
- 注意事项
```

### 步骤4：生成HTML长图页面

根据学习到的风格生成HTML页面，遵循以下规范：

**HTML结构规范：**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>/* 内嵌CSS样式 */</style>
</head>
<body>
  <!-- 长图内容 -->
</body>
</html>
```

**页面布局要求：**
- 宽度固定（建议 750px 或 1080px）
- 高度自适应内容
- 竖向滚动布局
- 无需外部依赖

**视觉规范：**
- 层级清晰：使用不同字号区分标题级别
- 重点突出：使用色块、图标、数字标注
- 留白合理：保持呼吸感的间距
- 风格统一：所有元素遵循参考风格

### 步骤5：输出交付

生成完整的可直接运行的 HTML 文件：
- 内嵌所有 CSS 样式
- 图片位置使用占位符 `[图片占位]` 或 `<img>` 标签预留
- 代码结构清晰易读
- 便于直接整屏截图

## HTML生成模板结构

```html
<!-- 页眉区域 -->
<header class="page-header">
  <div class="policy-badge">政策解读</div>
  <h1 class="main-title">政策标题</h1>
  <div class="policy-meta">发文字号 | 发布机构 | 发布日期</div>
</header>

<!-- 核心要点区域 -->
<section class="key-points">
  <h2 class="section-title">核心要点</h2>
  <div class="point-card">要点1</div>
  <div class="point-card">要点2</div>
  <!-- ... -->
</section>

<!-- 详细解读区域 -->
<section class="details">
  <h2 class="section-title">政策解读</h2>
  <div class="detail-block">
    <h3>小标题</h3>
    <p>详细解读内容...</p>
  </div>
</section>

<!-- 页脚区域 -->
<footer class="page-footer">
  <div class="footer-note">适用信息 | 注意事项</div>
</footer>
```

## 配色方案参考示例

**政务蓝色系：**
```css
--primary-color: #1a56db;    /* 主色-深蓝 */
--secondary-color: #3b82f6;  /* 辅色-亮蓝 */
--accent-color: #f59e0b;    /* 强调色-金色 */
--bg-color: #f8fafc;        /* 背景色-浅灰 */
--text-primary: #1e293b;    /* 主文字-深灰 */
--text-secondary: #64748b;  /* 辅文字-中灰 */
```

**政策绿色系：**
```css
--primary-color: #059669;    /* 主色-深绿 */
--secondary-color: #10b981;  /* 辅色-亮绿 */
--accent-color: #f97316;     /* 强调色-橙色 */
```

## 注意事项

1. **图片占位**：所有需要图片的位置使用 `<div class="img-placeholder">[图片占位]</div>`
2. **图标风格**：优先使用 SVG 内嵌图标，支持 Unicode 符号作为备选
3. **字体回退**：使用系统字体栈确保各平台显示一致
4. **响应式**：固定宽度设计，方便截图
5. **无交互**：纯展示型静态页面，无需 JavaScript 交互

## 输出文件

生成单个 HTML 文件，包含：
- 完整的 `<style>` 内嵌样式
- 语义化的 HTML 结构
- 清晰的注释说明
- 可直接复制使用
