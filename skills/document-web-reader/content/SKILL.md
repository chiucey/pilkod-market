---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f23b7c4866637f5e47f24880c5bc5e7d
    PropagateID: f23b7c4866637f5e47f24880c5bc5e7d
    ReservedCode1: 3046022100a3cf6ac41e67779ddc9a713de33a989fb7463b6fec7dc9425aecb7868d51f6d502210087c61a64eaa599eea9cf4f21244a4e552526283a32e06dbc1ea08a661e50aa22
    ReservedCode2: 3045022100826d042ce9ee62ca6f69fea40552e03f7b368abdcb0f5344bfe4915d5116293902201f0359f9b93bf8f4d06c4d73fddce5f1e941d9d4efec6bc04d1feb99474e5f3d
description: 将 PDF 或图片转换为适合手机阅读的网页端格式。当用户要求上传文档并在网页阅读、创建可翻页的文档阅读器、PDF/图片转移动端阅读、将文档转换为可滑动翻页的网页时使用。
name: document-web-reader
---

# Document Web Reader - 文档网页阅读器

将 PDF 或图片文件转换为支持目录导航、定位翻页、响应式布局、格式保留和触摸滑动操作的网页阅读器。生成后可**直接联网部署使用**。

## 工作流程

### 1. 文件分析与预处理

**输入支持**：
- PDF 文件（`.pdf`）
- 图片文件（`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`）

**处理策略**：
- **PDF 文件**：使用 `extract_pdfs_full_content` 提取文本内容和布局信息
- **图片文件**：使用 `images_understand` 识别图片中的文本内容
- **保留格式**：识别加粗、颜色、字体大小等富文本属性

### 2. 目录生成

**目录提取规则**：
| 源文件情况 | 处理方式 |
|-----------|---------|
| PDF 已有目录 | 提取原目录结构，保持章节对应关系 |
| 图片/无目录 | 智能分析内容，自动生成目录结构 |

**目录结构规范**：
```html
<!-- 目录侧边栏/抽屉 -->
<nav class="toc" id="tableOfContents">
  <h3>目录</h3>
  <ul>
    <li><a href="#" data-page="1">第一章 概述</a></li>
    <li><a href="#" data-page="5">第二章 核心功能</a></li>
    <li class="sub-item"><a href="#" data-page="5.1">2.1 功能点一</a></li>
  </ul>
</nav>
```

### 3. 网页阅读器生成

生成的网页阅读器必须满足以下要求：

| 功能需求 | 实现要求 |
|---------|---------|
| 目录功能 | 侧边栏或抽屉式目录，支持点击跳转 |
| 翻页功能 | 支持上/下一页按钮切换页面 |
| 定位功能 | 显示当前页码/总页数，可跳转到指定页面 |
| 响应式设计 | 自适应手机屏幕，垂直滚动优先 |
| 格式保留 | 保留原文的加粗、颜色、高亮等格式 |
| 触摸滑动 | 支持左右滑动翻页操作 |
| 加载指示 | 显示加载状态和错误提示 |

### 4. 技术实现规范

**HTML 结构要求**：
```html
<!-- 响应式容器 -->
<div class="reader-container">
  <!-- 顶部导航栏 -->
  <header class="header">
    <button id="menuToggle">目录</button>
    <span class="title">文档标题</span>
  </header>

  <!-- 目录抽屉 -->
  <nav class="toc-drawer" id="tocDrawer">
    <div class="toc-header">
      <h3>目录</h3>
      <button id="closeToc">关闭</button>
    </div>
    <ul class="toc-list" id="tocList"></ul>
  </nav>

  <!-- 页码导航 -->
  <div class="page-indicator">
    <span id="currentPage">1</span> / <span id="totalPages">10</span>
  </div>

  <!-- 内容区域 -->
  <div class="content-area" id="contentArea">
    <!-- 支持富文本内容 -->
    <p><strong>加粗文本</strong></p>
    <p style="color: red;">彩色文本</p>
  </div>

  <!-- 翻页控制 -->
  <div class="pagination">
    <button id="prevPage">上一页</button>
    <input type="number" id="pageInput" min="1">
    <button id="nextPage">下一页</button>
  </div>
</div>
```

**CSS 样式要求**：
- 使用 `@media` 实现移动端适配
- 触摸滑动使用 CSS `scroll-snap` 或 JavaScript 事件
- 文字大小适合移动端阅读（最小 14px）
- 足够的触控区域（按钮高度 >= 44px）
- 目录抽屉使用 `position: fixed` 实现侧滑效果
- 目录项高度足够（>= 40px）便于点击

**JavaScript 功能**：
- `goToPage(n)` - 跳转到指定页
- `nextPage()` - 下一页
- `prevPage()` - 上一页
- `toggleToc()` - 显示/隐藏目录
- `jumpToChapter(pageId)` - 从目录跳转到对应章节
- 触摸事件监听：`touchstart`, `touchmove`, `touchend`
- 滑动方向判断：水平位移 > 垂直位移时触发翻页

### 5. 输出格式与部署

**单文件 HTML**：所有 CSS 和 JS 内联到 HTML 文件中，便于部署和分享。

**部署流程**：
1. 将生成的 HTML 文件放入 `dist/` 目录
2. 使用 `deploy` 工具部署 `dist/` 目录
3. 返回可联网访问的 URL 给用户

**命名规范**：
- 输出目录：`dist/`
- 输出文件：`dist/index.html`
- 如果有图片资源，放在 `dist/imgs/` 子目录

## 验证清单

- [ ] 目录正确显示且可点击跳转
- [ ] 生成的 HTML 文件可独立运行
- [ ] 响应式布局在手机上正常显示
- [ ] 翻页按钮功能正常
- [ ] 页码跳转功能正常
- [ ] 左右滑动翻页响应灵敏
- [ ] 原文格式（加粗、颜色）正确保留
- [ ] 目录抽屉开合动画流畅
- [ ] 部署后可通过 URL 联网访问

## 交付物

1. **网页阅读器 HTML 文件** - 可直接在浏览器打开或部署
2. **可访问的网页链接** - 部署后生成的 URL
3. **使用说明** - 如何打开和操作阅读器

## 示例触发

- "上传这个 PDF，让我可以在手机上阅读"
- "把这份文档转成网页版"
- "创建可翻页的阅读页面"
- "将图片转成手机可读的网页"
- "生成带目录的在线文档"
