# 微信公众号排版规范参考

## 一、标题规范

### 1.1 文章标题
- 字数：建议 14-40 字
- 避免：标题党、夸大其词、过度煽情
- 推荐：开门见山、点明价值、制造好奇

### 1.2 多级标题
- 一级标题：`##` 或 `#`（字号28-32px）
- 二级标题：`###`（字号22-26px）
- 三级标题：`####`（字号18-20px）

## 二、正文排版

### 2.1 字体字号
- 正文字号：15-17px（推荐16px）
- 行间距：1.6-2.0（推荐1.8）
- 字间距：0-1px
- 段落间距：15-20px

### 2.2 颜色规范
- 正文颜色：#3e3e3e（深灰，保护视力）
- 标题颜色：#1a1a1a（纯黑，醒目）
- 强调颜色：#e74c3c 或品牌色
- 辅助颜色：#888888（灰色用于次要信息）

### 2.3 对齐方式
- 正文：两端对齐
- 引用块：居中或左对齐
- 图片说明：居中，灰色小字

## 三、图片规范

### 3.1 封面图
- 尺寸：900 x 383 像素（2.35:1）
- 格式：jpg/png
- 大小：不超过5MB
- 内容：清晰、有冲击力、避免过多文字

### 3.2 正文配图
- 宽度：建议 600-1080 像素
- 高度：自适应
- 格式：jpg/png/gif
- 大小：单张不超过10MB
- 说明：添加图注，解释图片内容

### 3.3 图片位置
- 章节开头配图（头图）
- 重要内容后配图
- 避免连续多图无文字间隔

## 四、特殊样式

### 4.1 引用块
```
padding: 15px 20px
border-left: 4px solid #品牌色
background: #f9f9f9
font-style: italic
```

### 4.2 代码块
```
background: #f5f5f5
padding: 10px 15px
border-radius: 5px
font-family: monospace
```

### 4.3 分割线
- 样式：居中虚线或小星星
- 颜色：#e0e0e0
- 间距：上下各15px

### 4.4 重点标注
- 加粗：`font-weight: bold`
- 颜色高亮：`background: #fff5d7`
- 特殊标记：使用emoji或特殊符号

## 五、交互元素

### 5.1 引导关注
- 位置：文首或文末
- 内容：公众号名称+二维码
- 话术：简洁有力

### 5.2 往期推荐
- 位置：文末
- 形式：图文卡片或文字链接

### 5.3 留言引导
- 位置：文末
- 话术：开放式问题引发讨论

## 六、完整HTML模板结构

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>文章标题</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #3e3e3e;
    max-width: 1080px;
    margin: 0 auto;
    padding: 20px;
  }
  h1 { font-size: 30px; color: #1a1a1a; text-align: center; margin-bottom: 30px; }
  h2 { font-size: 24px; color: #1a1a1a; margin-top: 40px; }
  h3 { font-size: 20px; color: #2c2c2c; margin-top: 30px; }
  p { text-align: justify; margin: 15px 0; }
  img { max-width: 100%; height: auto; display: block; margin: 20px auto; }
  blockquote {
    padding: 15px 20px;
    border-left: 4px solid #e74c3c;
    background: #f9f9f9;
    font-style: italic;
    margin: 20px 0;
  }
  .highlight { background: #fff5d7; padding: 2px 5px; }
</style>
</head>
<body>
  <!-- 内容区域 -->
</body>
</html>
```
