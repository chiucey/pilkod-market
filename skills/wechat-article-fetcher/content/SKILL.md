---
name: wechat-article-fetcher
description: 微信公众号文章抓取工具。当用户需要抓取微信公众号文章、提取内容、下载图片、OCR识别文字或生成Word文档时使用。支持自动排版和桌面输出。
---

# 微信公众号文章抓取工具

自动抓取微信公众号文章，提取文章信息、下载图片、识别图片文字，并生成排版精美的Word文档。

## 功能特性

- ✅ 自动提取文章标题、作者、发布时间
- ✅ 下载文章中的所有图片
- ✅ 支持图片文字识别（OCR）
- ✅ 自动过滤公众号水印和推广文字
- ✅ 生成格式规范的Word文档
- ✅ **图片按原文位置排列**
- ✅ **Word文档自动输出到桌面**
- ✅ 支持评论区抓取
- ✅ 智能排版，便于阅读

## 依赖环境

### 必需依赖
- **Python 3.8+**
- **Node.js 16+**（用于生成Word文档）
- **Edge浏览器**（Windows自带，用于抓取页面）

### Python 库
```bash
pip install selenium requests Pillow
```

### Node.js 库
```bash
npm install -g docx
```
或在本技能目录下：
```bash
cd wechat-article-fetcher
npm install
```

### 可选依赖（用于OCR）
如需图片文字识别功能，请安装以下任一工具：

**方案一：EasyOCR（推荐）**
```bash
pip install easyocr
```

**方案二：PaddleOCR**
```bash
pip install paddlepaddle paddleocr
```

**方案三：Tesseract OCR**
- Windows: 下载安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- 添加到系统PATH

## 使用方法

### 基本用法

```python
from scripts.fetch_article import WechatArticleFetcher

# 创建抓取器
fetcher = WechatArticleFetcher()

# 抓取文章
article_url = "https://mp.weixin.qq.com/s/xxxxxx"
result = fetcher.fetch(article_url)

# 生成Word文档（自动输出到桌面）
output_path = fetcher.generate_docx(result)
print(f"文档已生成: {output_path}")
```

### 命令行用法

```bash
python scripts/fetch_article.py "https://mp.weixin.qq.com/s/xxxxxx"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 微信公众号文章链接 | 必填 |
| `-o, --output` | 临时文件输出目录 | `./output` |
| `--no-ocr` | 禁用OCR | - |
| `--headless` | 使用无头模式 | - |
| `--max-comments` | 最大评论数 | `10` |

## 输出文件

抓取完成后，Word文档会自动输出到**桌面**：

```
桌面/
├── [文章标题].docx        # Word文档（主输出）
```

临时文件保存在输出目录：

```
output/
├── article_data.json      # 文章原始数据
├── images/                # 图片文件夹
│   ├── image_01.jpg
│   ├── image_02.jpg
│   └── ...
└── ocr_results.json       # OCR识别结果（如果启用）
```

## Word文档结构

生成的Word文档包含以下内容：

1. **文章标题** - 居中显示
2. **元信息** - 发布时间、作者、原文链接
3. **正文内容** - 按原文顺序排列：
   - 文字段落
   - 图片（保持原始位置）
   - 图片说明
4. **评论区** - 热门评论（如有）
5. **文档信息** - 抓取时间

## 工作流程

```
1. 启动浏览器 (Edge)
   ↓
2. 访问文章页面
   ↓
3. 等待页面加载完成
   ↓
4. 提取文章信息
   ├── 标题
   ├── 作者/公众号
   ├── 发布时间
   └── 正文文字
   ↓
5. 下载图片
   ├── 查找所有图片元素
   ├── 过滤头像/图标
   └── 保存到本地
   ↓
6. 图片文字识别 (可选)
   ├── 加载OCR引擎
   ├── 识别图片文字
   └── 过滤水印/推广
   ↓
7. 获取评论 (可选)
   ├── 滚动到评论区
   └── 提取热门评论
   ↓
8. 生成Word文档
   ├── 按原文顺序排列内容
   ├── 插入图片到正确位置
   └── 输出到桌面
```

## 注意事项

### 微信反爬机制

微信公众号文章有反爬机制，抓取时需要注意：

1. **使用真实浏览器** - 本工具使用Edge浏览器模拟真实用户访问
2. **等待加载时间** - 图片和动态内容需要时间加载
3. **评论限制** - 部分文章的评论需要登录才能查看

### OCR 准确性

OCR识别效果取决于图片质量：

- 清晰的文字识别率 > 95%
- 手写字体识别率较低
- 复杂背景可能影响识别效果

### 频率限制

建议每次抓取间隔 **5秒以上**，避免触发反爬机制。

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 浏览器启动失败 | Edge未安装或版本过低 | 更新Edge浏览器 |
| 图片下载失败 | 网络超时 | 重试或检查网络 |
| OCR识别失败 | OCR工具未安装 | 安装EasyOCR或Tesseract |
| Word生成失败 | docx库未安装 | `npm install docx` |

## 配置文件

可在 `config/config.yaml` 中自定义配置：

```json
{
  "browser": {
    "type": "edge",
    "headless": false,
    "timeout": 30000
  },
  "ocr": {
    "enabled": true,
    "engine": "easyocr",
    "filter_watermark": true
  },
  "output": {
    "format": "docx",
    "image_quality": "high",
    "include_comments": true
  }
}
```

## 示例

查看 `examples/` 目录中的示例代码：

- `basic_usage.py` - 基本用法
- `batch_fetch.py` - 批量抓取

## 更新日志

### v1.1.1 (2026-04-07)
- 🐛 修复：图片下载数量不对（优先使用data-src属性）
- 🐛 修复：图片位置不对（按HTML位置排序穿插）
- 📝 新增：经验教训文档 LESSONS_LEARNED.md

### v1.1.0 (2026-04-07)
- ✨ 图片按原文位置排列
- ✨ Word文档自动输出到桌面
- 🐛 修复正文内容提取问题
- 🐛 修复编码问题

### v1.0.0 (2026-04-07)
- 初始版本
- 支持文章抓取和图片下载
- 支持OCR文字识别
- 支持Word文档生成

## 常见问题与解决方案

### 问题1：正文内容为空

**原因**：微信文章有两种类型，脚本没有正确识别

**解决**：已修复，优先检测 `#js_content`（普通文章），再回退到图片文章

### 问题2：图片数量不对

**原因**：微信图片主要通过 `data-src` 属性加载，`src` 可能为空

**解决**：已修复，优先获取 `data-src` 属性

### 问题3：图片位置不对

**原因**：Word生成时没有按HTML位置排序

**解决**：已修复，分析HTML中图片和段落的位置，按顺序渲染

## 技术要点

### 微信文章结构

```html
<!-- 普通文章 -->
<div id="js_content">
  <p>文字段落</p>
  <img data-src="图片URL">
  <p>继续文字</p>
</div>

<!-- 图片文章 -->
<div id="js_image_content">
  <img src="图片URL">
</div>
```

### 图片获取要点

1. **优先使用 data-src**：微信图片懒加载，`src` 可能是占位图
2. **限定正文区域**：避免获取头像、图标等非正文图片
3. **按位置排序**：根据HTML中的位置决定渲染顺序

详细经验教训请查看 [LESSONS_LEARNED.md](./LESSONS_LEARNED.md)

## 许可证

MIT License

## 相关技能

- `docx` - Word文档处理
- `pdf` - PDF转换
- `browser-cdp` - 浏览器自动化
