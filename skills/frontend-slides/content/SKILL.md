---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7a085fa6e844aeebc18986995002c730
    PropagateID: 7a085fa6e844aeebc18986995002c730
    ReservedCode1: 304402203e64f69f0e4e8e906f7959e3d99866a3a744f6304d3c0f63aa761fc770697dc202201b87f33e8d4acb3169ce7c92746aa07eba7dd88bcc4455b4b4bfadb26f4fa5bc
    ReservedCode2: 3045022100a05bee1e20b7d6e18309e93788ff3e2e342fdae86863180974625b832cd42e8b02200de6a5afa43adc6e21eb8ec7e231b303830969554f99b3a3d72eafd64c9009f5
description: 当用户要求创建 HTML 演示文稿、制作幻灯片、将 PowerPoint 转换为网页演示文稿、创建具有动画效果的网页幻灯片，或需要视觉风格的演示文稿时使用。
name: frontend-slides
---

# Frontend Slides - HTML 演示文稿创建技能

创建精美、动画丰富的 HTML 演示文稿，支持从头创建或从 PowerPoint 转换。

## 工作流程

### 1. 收集用户需求

**必须收集的信息：**
- **内容**：幻灯片数量、每个幻灯片的标题和要点、是否包含图片
- **风格偏好**：用户能描述想要的感觉（专业、活泼、简约、技术感）吗？
- **PPT 文件**：用户是否有现有 PowerPoint 需要转换？

**询问技巧：**
- 如果用户无法描述风格偏好 → 提供 3 种风格预览选项
- 如果用户提供 PPT 文件 → 提取内容后让用户确认

### 2. 选择视觉风格

**可用风格（10 种预设）：**

**深色主题：**
- **Neon Cyber** — 未来科技感、粒子效果
- **Midnight Executive** — 高端企业风、可信赖
- **Deep Space** — 电影感、浩瀚宇宙
- **Terminal Green** — 开发者风格、黑客美学

**浅色主题：**
- **Paper & Ink** — 编辑风格、文学精致
- **Swiss Modern** — 极简几何、Bauhaus 风格
- **Soft Pastel** — 友好活泼、创意十足
- **Warm Editorial** — 杂志风格、摄影为主

**特色风格：**
- **Brutalist** — 原始粗犷、引人注目
- **Gradient Wave** — 现代 SaaS 渐变风格

**如果用户不确定风格：**
1. 根据内容主题推荐 3 种最适合的风格
2. 生成每种风格的预览示例
3. 让用户选择最喜欢的

### 3. 创建演示文稿

#### 从头创建

```
标题：[演示文稿标题]

幻灯片结构：
1. [第一张：开场/标题]
2. [第二张：问题陈述]
3. [第三张：解决方案]
...

风格选择：[用户选择或推荐的风格]
```

#### 转换 PowerPoint

1. **提取 PPT 内容：**
   - 读取用户提供的 .pptx 文件
   - 提取每张幻灯片的标题、正文、备注
   - 提取所有嵌入图片

2. **内容确认：**
   - 向用户展示提取的内容
   - 确认是否需要调整顺序或内容

3. **选择风格并生成**

### 4. 生成 HTML 文件

每个演示文稿输出为**单一 HTML 文件**，包含：

```html
<!-- 必需特性 -->
- 键盘导航（方向键、空格键）
- 触摸滑动支持
- 鼠标滚轮滚动
- 进度条显示
- 导航圆点
- 滚动触发动画
- 响应式设计
- 减少动画偏好支持（prefers-reduced-motion）
```

**HTML 结构要求：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示文稿标题</title>
    <style>
        /* 所有 CSS 内联，无外部依赖 */
        /* 包含动画、响应式、减少动画媒体查询 */
    </style>
</head>
<body>
    <!-- 每张幻灯片为一个 section -->
    <section class="slide" data-slide="1">
        <h1>标题</h1>
        <p>内容...</p>
    </section>
    <!-- 更多幻灯片... -->

    <nav class="progress-bar">...</nav>
    <nav class="dots">...</nav>

    <script>
        // 内联 JavaScript
        // 键盘事件、触摸事件、滚动动画
    </script>
</body>
</html>
```

### 5. 交付与预览

1. 生成 HTML 文件
2. 告知用户文件路径
3. 说明操作方式：
   - **浏览器打开**：直接在浏览器中打开 HTML 文件
   - **编辑**：用户可修改 HTML 中的文本内容
   - **样式调整**：修改 `<style>` 标签中的 CSS

## 设计风格代码模板

### 深色主题基础

```css
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #161622;
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
    --accent: #00ff88;
}
```

### 浅色主题基础

```css
:root {
    --bg-primary: #fafafa;
    --bg-secondary: #ffffff;
    --text-primary: #1a1a2e;
    --text-secondary: #666680;
    --accent: #6366f1;
}
```

### 动画配置

```css
/* 滚动触发动画 */
.slide {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}

.slide.visible {
    opacity: 1;
    transform: translateY(0);
}

/* 减少动画支持 */
@media (prefers-reduced-motion: reduce) {
    .slide {
        opacity: 1;
        transform: none;
        transition: none;
    }
}
```

## 质量检查清单

生成后验证：

- [ ] 每张幻灯片内容完整
- [ ] 键盘导航正常工作
- [ ] 触摸滑动正常
- [ ] 进度条显示正确
- [ ] 导航圆点可点击
- [ ] 动画流畅
- [ ] 响应式布局正常
- [ ] 无外部依赖文件

## 常见问题处理

**Q: 用户不知道想要什么风格？**
A: 询问演示文稿的用途（商务/创意/技术），然后推荐 3 种风格并生成预览。

**Q: 内容很长怎么办？**
A: 建议用户将长内容拆分为多张幻灯片，保持每张幻灯片简洁。

**Q: 用户有图片需要添加？**
A: 询问图片路径或让用户提供 base64 编码的图片数据。

**Q: 需要添加动画效果？**
A: 使用 CSS 动画和 Intersection Observer API 实现滚动触发动画。

## 哲学原则

1. **无需设计技能也能创造美**：用户只需选择喜欢的风格
2. **零依赖**：单一 HTML 文件确保长期可用性
3. **独特性**：避免 AI 常见的紫色渐变风格
4. **代码即文档**：代码中包含详细注释
