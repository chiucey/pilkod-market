---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f8e1cca9872f6a89de30e8b331378eb0
    PropagateID: f8e1cca9872f6a89de30e8b331378eb0
    ReservedCode1: 3046022100af5b253d892801a67b514ecebdbfe77518d16f9d3dd7fe073eb26d0a365159c40221008cac997577077e8d51b7a9ebfa9f3e5acadcccd57c358cd40fb681b85f7b6720
    ReservedCode2: 3046022100849c001fc76ceb5fce588225a83b103c166e3c37ee4da183447b9f096d86b6e2022100ff23316f2a70e82b6caf712bce6b9114aa567561d517d008e6858bb77e7dea19
description: 微信公众号文章排版技能。当用户需要将文章内容转换为微信公众号适配的精美排版格式时使用，支持标题、段落、引用、列表、图片等多种元素的美化。
name: wechat-article-formatter
---

# 微信公众号文章排版技能

## 设计理念

**"优秀的排版是无形的"** —— 通过精准的字体、间距与色彩控制，引导读者自然阅读，提升内容传达效率。

## 核心设计系统

### 色彩规范
| 用途 | 色值 |
|------|------|
| 主色调（标题/强调） | `#003d80` |
| 正文色 | `#333333` |
| 辅助文字 | `#666666` |
| 次要文字 | `#999999` |
| 卡片背景-浅灰 | `#f7f7f7` |
| 卡片背景-浅蓝 | `#f0f4f8` |
| 分割线 | `#dddddd` |

### 字体系统
```css
font-family: -apple-system-font, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif;
line-height: 1.8;
letter-spacing: 1px;
```

## 排版模板代码

### 基础框架
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>文章标题</title>
</head>
<body style="background-color: #ffffff; margin: 0; padding: 0;">
<div style="margin: 20px 15px; font-family: -apple-system-font, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif; line-height: 1.8; letter-spacing: 1px; color: #333; background-color: #ffffff;">
  <!-- 文章内容 -->
</div>
</body>
</html>
```

### 导语卡片
```html
<div style="margin-bottom: 30px; padding: 15px; background-color: #f7f7f7; border-left: 4px solid #003d80;">
  <p style="font-size: 14px; color: #666; margin: 0;">
    <strong>导读：</strong> 这里是导语内容...
  </p>
</div>
```

### 章节标题
```html
<div style="margin: 40px 0 20px; text-align: center;">
  <div style="display: inline-block; padding: 0 10px; border-bottom: 2px solid #003d80;">
    <h2 style="font-size: 20px; color: #003d80; margin-bottom: 5px;">01 章节标题</h2>
  </div>
  <p style="font-size: 12px; color: #999; text-transform: uppercase; margin-top: 5px;">English Title</p>
</div>
```

### 引言卡片
```html
<div style="margin: 30px 0; padding: 25px; background-color: #f0f4f8; text-align: center;">
  <p style="font-size: 18px; color: #003d80; font-weight: bold; font-style: italic;">
    "简洁是终极的细腻。"
  </p>
  <p style="font-size: 13px; color: #888; margin-top: 10px;">—— 作者名</p>
</div>
```

### 小标题（带左侧装饰线）
```html
<div style="margin: 30px 0 15px;">
  <div style="width: 4px; height: 18px; background-color: #003d80; margin-bottom: 10px;"></div>
  <h3 style="font-size: 18px; font-weight: bold; color: #333; margin-top: 0;">小标题内容</h3>
</div>
```

### 列表
```html
<div style="font-size: 15px; color: #444;">
  <ul style="padding-left: 20px; margin: 0;">
    <li style="margin-bottom: 10px; color: #003d80;">
      <strong style="color: #003d80;">标题：</strong> 内容描述...
    </li>
  </ul>
</div>
```

### 强调文字
```html
<!-- 蓝色强调 -->
<span style="color: #003d80;">需要强调的内容</span>

<!-- 加粗 -->
<strong>加粗文字</strong>
```

### 分割线
```html
<!-- 虚线分割 -->
<div style="border-top: 1px dashed #ddd; margin: 40px 0; padding-top: 20px; text-align: center; color: #bbb; font-size: 12px;">
  <p style="margin: 5px 0;">分割内容</p>
</div>
```

### 图片
```html
<div style="margin: 25px 0; text-align: center;">
  <img src="图片URL" alt="描述" style="max-width: 100%; border-radius: 8px;">
  <p style="font-size: 12px; color: #999; margin-top: 10px;">图片说明</p>
</div>
```

## 使用说明

1. **内容保护原则**：仅优化视觉呈现，绝不擅自改动文章原意
2. **色彩统一**：全文主色调统一使用 `#003d80`
3. **间距控制**：合理使用 `margin` 控制段落间距
4. **响应式适配**：所有尺寸使用相对单位确保移动端适配

## 排版规范

| 元素 | 字号 | 颜色 | 说明 |
|------|------|------|------|
| 章节标题 | 20px | #003d80 | 带英文副标题 |
| 小标题 | 18px | #333 | 带左侧装饰线 |
| 正文 | 15-16px | #333 | 行高1.8 |
| 列表项 | 15px | #003d80 | 带蓝色圆点 |
| 引用 | 18px | #003d80 | 斜体+浅蓝背景 |
| 导语 | 14px | #666 | 灰底+左侧蓝线 |
| 注释 | 12-13px | #888 | 用于出处说明 |
