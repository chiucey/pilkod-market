# 排版样式参考

## 标题样式

```css
/* 主标题 */
.article-title {
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a;
  text-align: center;
  margin: 20px 0;
}

/* 章节标题 */
.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
  margin: 24px 0 16px 0;
  padding-left: 12px;
  border-left: 4px solid #1890ff;
}

/* 子标题 */
.subsection-title {
  font-size: 18px;
  font-weight: bold;
  color: #333333;
  margin: 20px 0 12px 0;
}
```

## 正文样式

```css
.article-content {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: #333333;
  text-align: justify;
}
```

## 引用块样式

```css
.blockquote {
  margin: 16px 0;
  padding: 12px 16px;
  background-color: #f5f5f5;
  border-left: 3px solid #1890ff;
  border-radius: 4px;
}

.blockquote p {
  margin: 0;
  color: #666666;
}
```

## 重点标注样式

```css
.highlight {
  color: #e74c3c;
  font-weight: bold;
}

.strong {
  font-weight: bold;
  color: #1a1a1a;
}
```

## 段落与间距

```css
.article-content p {
  margin: 0 0 16px 0;
  text-indent: 2em;
}

.article-content h2,
.article-content h3 {
  margin-top: 24px;
  margin-bottom: 16px;
}
```

## 公众号适配注意事项

1. **图片宽度**：建议 600px-900px，超宽图会自动缩放
2. **图片间距**：段前段后各留 8px，避免过于紧凑
3. **字体大小**：正文不小于 14px，确保阅读舒适
4. **配色对比度**：正文与背景对比度 ≥ 4.5:1
5. **行高建议**：1.6-1.8，避免文字过于密集