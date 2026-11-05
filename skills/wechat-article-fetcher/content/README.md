# 微信公众号文章抓取工具

自动抓取微信公众号文章，生成Word文档。**Word文档自动输出到桌面**。

## 快速开始

### 1. 安装依赖

Windows用户双击运行 `install.bat`，或手动执行：

```bash
# Python依赖
pip install selenium requests Pillow

# Node.js依赖
cd wechat-article-fetcher
npm install

# OCR工具（可选）
pip install easyocr
```

### 2. 使用

```bash
python scripts/fetch_article.py "https://mp.weixin.qq.com/s/xxxxxx"
```

### 3. 输出

Word文档自动生成到**桌面**：
- `[文章标题].docx` - Word文档

临时文件在 `output/` 目录：
- `images/` - 图片文件夹
- `article_data.json` - 原始数据

## 功能

- ✅ 提取标题、作者、时间
- ✅ 下载文章图片
- ✅ **图片按原文位置排列**
- ✅ 图片文字识别（OCR）
- ✅ 获取评论区
- ✅ 生成Word文档
- ✅ **输出到桌面**

## 依赖

- Python 3.8+
- Node.js 16+
- Edge 或 Chrome 浏览器

## 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## 更新日志

### v1.1.0 (2026-04-07)
- ✨ 图片按原文位置排列
- ✨ Word文档自动输出到桌面
- 🐛 修复正文内容提取问题

详见 [CHANGELOG.md](./CHANGELOG.md)
