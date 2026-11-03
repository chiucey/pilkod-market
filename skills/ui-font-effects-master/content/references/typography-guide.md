# 中文字体排版指南

## 1. 字体选择原则

### 1.1 字体分类与适用场景

| 字体类型 | 特点 | 适用场景 |
|----------|------|----------|
| 无衬线体 | 简洁、现代、清晰 | 界面正文、标题、按钮 |
| 衬线体 | 优雅、传统、正式 | 文章正文、长文本、高端品牌 |
| 手写体 | 亲和、个性、艺术 | 装饰、标题、特效 |
| 等宽字体 | 规整、对齐 | 代码、数据、表格 |

### 1.2 推荐字体组合

#### 中文
```css
/* 现代简约风格 */
--font-cn-primary: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
--font-cn-display: 'Noto Serif SC', 'Songti SC', serif;

/* 科技风格 */
--font-cn-tech: 'Source Han Sans SC', 'HarmonyOS Sans SC', sans-serif;

/* 优雅风格 */
--font-cn-elegant: 'ZCOOL XiaoWei', 'LXGW WenKai', cursive;
```

#### 英文
```css
/* 通用无衬线 */
--font-en-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* 展示字体 */
--font-en-display: 'Playfair Display', 'DM Serif Display', serif;

/* 科技字体 */
--font-en-tech: 'Space Grotesk', 'Outfit', sans-serif;

/* 等宽字体 */
--font-en-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

## 2. 字号规范

### 2.1 移动端字号
```
标题 H1: 28px / 1.2 line-height
标题 H2: 24px / 1.3
标题 H3: 20px / 1.4
正文大: 18px / 1.6
正文: 16px / 1.6
辅助: 14px / 1.5
小字: 12px / 1.4
```

### 2.2 桌面端字号
```
标题 H1: 48px / 1.1
标题 H2: 36px / 1.2
标题 H3: 28px / 1.3
正文大: 18px / 1.6
正文: 16px / 1.6
辅助: 14px / 1.5
小字: 12px / 1.4
```

## 3. 字重规范

| 字重值 | CSS关键字 | 适用场景 |
|--------|-----------|----------|
| 100 | Thin | 超细装饰 |
| 300 | Light | 辅助说明 |
| 400 | Regular | 正文默认 |
| 500 | Medium | 按钮、标签 |
| 600 | Semibold | 强调标题 |
| 700 | Bold | 主标题、关键 |
| 900 | Black | 超重装饰 |

## 4. 字体间距

### 4.1 字间距
```css
/* 中文一般不加字间距，保持自然 */
--letter-spacing-tight: -0.02em;   /* 紧凑，用于大标题 */
--letter-spacing-normal: 0;          /* 默认，中文正文 */
--letter-spacing-wide: 0.02em;       /* 宽松，用于英文标题 */
--letter-spacing-wider: 0.05em;      /* 更宽，字母大写 */
```

### 4.2 行间距
```css
/* 行高根据字号调整 */
--leading-solid: 1;        /* 最小行高，用于大标题 */
--leading-heading: 1.2;    /* 标题行高 */
--leading-normal: 1.5;     /* 标准行高 */
--leading-relaxed: 1.75;  /* 宽松行高，用于长文本阅读 */
```

## 5. 段落排版

### 5.1 段落间距
```css
/* 段落之间空出一行的高度 */
--paragraph-gap: 1em;

/* 示例 */
p + p {
  margin-top: var(--paragraph-gap);
}
```

### 5.2 文本对齐
```css
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-justify { text-align: justify; }  /* 两端对齐，用于正文 */
```

### 5.3 文本缩进
```css
/* 首行缩进，中文规范 */
.text-indent {
  text-indent: 2em;  /* 两个中文字符宽度 */
}
```

## 6. 字幕排版规范

### 6.1 短视频字幕
```
字号: 20-24px
位置: 底部居中，距底边 10-15%
背景: 半透明黑色圆角矩形
行数: 最多2行
```

```css
.subtitle-video {
  font-size: clamp(18px, 4vw, 24px);
  text-align: center;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}
```

### 6.2 网页标题字幕
```
字号: 32-48px
位置: 垂直居中或偏上
样式: 简洁有力
```

```css
.title-subtitle {
  font-size: clamp(24px, 5vw, 48px);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
}
```

### 6.3 弹窗提示字幕
```
字号: 14-16px
位置: 居中
颜色: 次要文字色
```

```css
.toast-subtitle {
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-secondary);
}
```

## 7. 竖排文字规范

```css
.writing-mode-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

/* 竖排时的字间距和行间距需要调整 */
.writing-mode-vertical {
  letter-spacing: 0.5em;
  line-height: 1.8;
}
```

## 8. 特殊排版效果

### 8.1 渐变文字
```css
.text-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### 8.2 发光文字
```css
.text-glow {
  color: #fff;
  text-shadow:
    0 0 10px rgba(99, 102, 241, 0.8),
    0 0 20px rgba(99, 102, 241, 0.6),
    0 0 30px rgba(99, 102, 241, 0.4);
}
```

### 8.3 描边文字
```css
.text-outline {
  color: transparent;
  -webkit-text-stroke: 1px white;
  text-stroke: 1px white;
}
```

## 9. 字体加载与回退

```html
<!-- Google Fonts 预连接 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- 加载字体 -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
```

### 回退策略
```css
font-family:
  'Inter',              /* 首选西文字体 */
  'Noto Sans SC',       /* 中文字体 */
  -apple-system,        /* 系统字体 */
  BlinkMacSystemFont,
  'Segoe UI',
  sans-serif;           /* 最终回退 */
```

## 10. 无障碍字体规范

```css
/* 最小字号不小于 14px（可点击文本 16px） */
body {
  font-size: 16px;  /* 避免太小影响阅读 */
}

/* 足够对比度 */
.text-primary { color: #1E293B; }
.text-secondary { color: #64748B; }  /* 最小对比度 4.5:1 */

/* 行宽限制，提高阅读舒适度 */
.prose {
  max-width: 65ch;  /* 最佳阅读宽度 */
  line-height: 1.75;
}
```

## 11. 常见排版错误避免

| 错误类型 | 问题 | 正确做法 |
|----------|------|----------|
| 字号混乱 | 层级不清 | 统一字号系统 |
| 字重混乱 | 视觉疲劳 | 限制使用2-3种字重 |
| 行高过紧 | 阅读困难 | 正文行高≥1.5 |
| 行宽过长 | 阅读跳行 | 限制max-width |
| 间距不均 | 排版杂乱 | 使用间距系统变量 |
