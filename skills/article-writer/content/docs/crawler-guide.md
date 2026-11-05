# 文档爬虫系统使用指南

> 自动爬取文档网站，建立结构化知识库

## 快速开始

### 1. 安装依赖

```bash
cd /Users/coso/Documents/dev/ai/wordflowlab/article-writer
npm install
```

这将自动安装所有需要的依赖，包括：
- cheerio (HTML 解析)
- axios (HTTP 请求)
- turndown (HTML 转 Markdown)
- puppeteer (动态页面支持)
- pdf-parse (PDF 提取)

### 2. 爬取第一个文档站

```bash
bash scripts/bash/research-docs.sh \
  --name "vue" \
  --url "https://vuejs.org/guide/" \
  --max-pages 50
```

### 3. 查看结果

```bash
# 查看索引
cat _knowledge_base/indexed/vue-index.md

# 查看特定分类
cat _knowledge_base/indexed/vue-getting-started.md
cat _knowledge_base/indexed/vue-api.md
```

---

## 使用场景

### 场景 1: 爬取技术文档

适合爬取 React、Vue、TypeScript 等官方文档。

```bash
# Vue.js 文档
bash scripts/bash/research-docs.sh \
  --name "vue3" \
  --url "https://vuejs.org/guide/" \
  --max-pages 200

# React 文档
bash scripts/bash/research-docs.sh \
  --name "react" \
  --url "https://react.dev/learn" \
  --max-pages 200

# TypeScript 文档
bash scripts/bash/research-docs.sh \
  --name "typescript" \
  --url "https://www.typescriptlang.org/docs/" \
  --max-pages 150
```

### 场景 2: 动态页面支持

如果文档站使用 React/Vue 渲染（SPA），需要添加 `--dynamic` 参数：

```bash
bash scripts/bash/research-docs.sh \
  --name "nextjs" \
  --url "https://nextjs.org/docs" \
  --dynamic \
  --max-pages 200
```

**注意**: 动态爬虫会启动 Puppeteer（Chromium），首次使用会下载浏览器（~200MB）。

### 场景 3: 提取 PDF 文档

```bash
# 基础 PDF 提取
bash scripts/bash/research-docs.sh \
  --name "manual" \
  --pdf "~/Downloads/product-manual.pdf"

# 大型 PDF
bash scripts/bash/research-docs.sh \
  --name "handbook" \
  --pdf "~/Documents/employee-handbook.pdf"
```

---

## 配置说明

### 参数详解

| 参数 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `--name` | ✅ | 项目名称（用于文件命名） | 无 |
| `--url` | * | 文档网站 URL | 无 |
| `--pdf` | * | PDF 文件路径 | 无 |
| `--dynamic` | ❌ | 使用动态爬虫（Puppeteer） | false |
| `--max-pages` | ❌ | 最大爬取页数 | 200 |

*注: `--url` 和 `--pdf` 必须提供其中之一

### 预设配置

系统内置了常见框架的预设配置：

```typescript
// Vue.js
{
  name: 'vue',
  baseUrl: 'https://vuejs.org/guide/',
  maxPages: 200,
  selectors: {
    mainContent: '.vt-doc, article',
    title: 'h1',
    codeBlocks: 'pre code'
  }
}

// React
{
  name: 'react',
  baseUrl: 'https://react.dev/learn',
  maxPages: 200,
  selectors: {
    mainContent: 'article, .content',
    title: 'h1',
    codeBlocks: 'pre code'
  }
}
```

查看所有预设：`src/crawler/config.ts`

---

## 输出结构

### 原始数据 (`_knowledge_base/raw/`)

```
_knowledge_base/raw/vue/
├── pages/
│   ├── 001-introduction.json
│   ├── 002-quick-start.json
│   └── ...
└── summary.json
```

每个 JSON 文件包含：
```json
{
  "url": "https://vuejs.org/guide/introduction.html",
  "title": "Introduction",
  "content": "Markdown 格式的内容...",
  "codeExamples": [...],
  "category": "getting-started",
  "scrapedAt": "2025-10-26T10:30:00.000Z",
  "links": [...]
}
```

### 知识库 (`_knowledge_base/indexed/`)

按分类生成的 Markdown 文件：

```
_knowledge_base/indexed/
├── vue-index.md              # 总索引
├── vue-getting-started.md    # 入门指南
├── vue-guide.md              # 使用指南
├── vue-api.md                # API 参考
└── ...
```

**AI 如何使用知识库：**
- AI 写作时会自动读取 `_knowledge_base/indexed/` 下的 Markdown 文件
- 使用 grep/ripgrep 等工具快速搜索内容

---

## 在 AI 命令中使用

### 方式 1: 通过 `/research` 命令

在 AI 助手中直接使用：

```
/research "Vue 3 官方文档" --url https://vuejs.org/guide/
```

AI 会自动：
1. 检测到是文档网站 URL
2. 调用爬虫系统
3. 显示进度
4. 保存到知识库
5. 转换为 Markdown 格式

### 方式 2: AI 自动引用

爬取完成后，在写作时 AI 会自动读取知识库：

```
/write
```

AI 会自动读取 `_knowledge_base/indexed/` 目录中的 Markdown 文件并引用相关内容。

---

## 高级用法

### 自定义爬取配置

创建自定义配置文件：

```typescript
// my-config.ts
import type { CrawlerConfig } from './src/crawler/types';

const config: CrawlerConfig = {
  name: 'my-framework',
  baseUrl: 'https://myframework.dev/docs/',
  maxPages: 300,
  concurrency: 10,
  rateLimit: 300,
  selectors: {
    mainContent: '.documentation-content',
    title: 'h1.page-title',
    codeBlocks: 'pre.highlight code'
  },
  urlPatterns: {
    include: ['/docs/', '/api/'],
    exclude: ['/blog/', '/changelog/']
  }
};

export default config;
```

### 程序化调用

```typescript
import { CrawlerManager } from './src/crawler/crawler-manager';

const manager = new CrawlerManager();

await manager.executeCrawl({
  name: 'vue',
  url: 'https://vuejs.org/guide/',
  outputDir: './_knowledge_base',
  maxPages: 200,
  useDynamic: false
});

---

## 性能和限制

### 爬取速度

| 页数 | 并发数 | 预计时间 |
|------|--------|----------|
| 50 | 5 | 2-3 分钟 |
| 100 | 5 | 5-8 分钟 |
| 200 | 5 | 10-15 分钟 |
| 500 | 10 | 15-25 分钟 |

### 磁盘占用

| 页数 | 原始数据 | 知识库 | 总计 |
|------|---------|--------|------|
| 50 | ~5 MB | ~2 MB | ~7 MB |
| 200 | ~20 MB | ~8 MB | ~28 MB |
| 500 | ~50 MB | ~20 MB | ~70 MB |

### 限制和建议

- **最大页数**: 建议不超过 500 页（避免过度爬取）
- **并发数**: 默认 5，可调整至 10（避免被封禁）
- **速率限制**: 默认 500ms/页（尊重服务器）
- **超时时间**: 10 秒/页（动态页面可能更长）

---

## 故障排查

### 问题 1: 无法提取内容

**症状**: 爬取完成，但内容为空

**原因**: CSS 选择器不匹配

**解决**:
1. 打开目标网站
2. 检查 DevTools 找到正确的选择器
3. 自定义配置或修改预设

### 问题 2: 动态页面爬取失败

**症状**: 动态模式下报错或超时

**解决**:
1. 确保已安装 Puppeteer: `npm install puppeteer`
2. 首次使用会下载 Chromium (~200MB)
3. 检查系统是否有足够内存 (建议 4GB+)
4. 如果仍失败，回退到静态模式

### 问题 3: 被网站封禁

**症状**: 大量 403/429 错误

**解决**:
1. 增加速率限制: `--rate-limit 1000`
2. 减少并发数
3. 添加更真实的 User-Agent
4. 遵守网站的 robots.txt

### 问题 4: PDF 提取乱码

**症状**: PDF 中文显示为乱码

**解决**:
1. 确保 PDF 不是扫描版（图片）
2. 如需 OCR，安装 tesseract: `brew install tesseract`
3. 使用 `--ocr` 参数（需要额外实现）

---

## 最佳实践

### 1. 先小规模测试

```bash
# 先爬取 20 页测试
bash scripts/bash/research-docs.sh \
  --name "test" \
  --url "https://example.com/docs/" \
  --max-pages 20

# 验证内容质量
cat _knowledge_base/indexed/test-*.md

# 满意后再增加页数
```

### 2. 使用进度缓存

如果爬取中断，删除后重新运行会从头开始。未来可添加断点续传功能。

### 3. 定期更新

```bash
# 每月更新一次文档
crontab -e
# 添加: 0 0 1 * * bash /path/to/research-docs.sh --name vue --url https://vuejs.org/guide/
```

### 4. 备份重要数据

```bash
# 备份知识库
tar -czf knowledge-backup-$(date +%Y%m%d).tar.gz _knowledge_base/
```

---

## API 参考

详细 API 文档请参考：
- `src/crawler/types.ts` - 类型定义
- `src/crawler/doc-crawler.ts` - 静态爬虫
- `src/crawler/dynamic-crawler.ts` - 动态爬虫
- `src/crawler/crawler-manager.ts` - 管理器
- `src/crawler/knowledge-converter.ts` - Markdown 转换器

---

## 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/wordflowlab/article-writer/issues)
- **文档**: [查看更多文档](../README.md)
- **示例**: [查看示例项目](../examples/)

---

**Happy Crawling! 🚀**

