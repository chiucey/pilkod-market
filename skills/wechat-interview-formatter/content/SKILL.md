---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022068c9185013c5ecbd3bab387dfd049ea5164e2e299795154a1a49693c84da058b02205a7660cb880acc05e525214274f8b2f3c05545c32bcb84898e922861b7a71baa
    ReservedCode2: 3045022100aa5706c00d16981d102c71ba00bfbadf09b95074cdc396cbc61814ff291273580220321c47e0b832b5ee2b28b91648a32d44fe4e8197554d0f1d893b795383ccab4c
description: 微信公众号采访对话类文章自动排版技能。当用户需要将采访内容转换为微信公众号适配的精美排版格式时使用，支持问答对话、人物介绍、要点提炼等多种采访文章专用元素的美化排版。
name: wechat-interview-formatter
---

# 微信公众号采访对话类文章排版技能

## 设计理念

**"让对话之美跃然屏上"** —— 通过精心设计的视觉层次，清晰呈现采访者与受访者之间的思想交锋，让读者仿佛置身于对话现场。

## 核心设计系统

### 色彩规范
| 用途 | 色值 | 说明 |
|------|------|------|
| 主色调（标题/强调） | `#1a365d` | 深蓝色，传递专业与深度 |
| 记者/采访者标识 | `#2563eb` | 蓝色，代表提问与引导 |
| 受访者标识 | `#f59e0b` | 金色，代表回答与观点 |
| 正文色 | `#374151` | 深灰色，柔和易读 |
| 辅助文字 | `#6b7280` | 中灰色 |
| 卡片背景-受访者 | `#fef3c7` | 浅金色背景 |
| 卡片背景-记者 | `#eff6ff` | 浅蓝色背景 |
| 卡片背景-引言 | `#fef3c7` | 浅金色背景 |
| 分割线 | `#e5e7eb` | 浅灰色 |

### 字体系统
```css
font-family: -apple-system-font, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif;
line-height: 1.8;
letter-spacing: 0.5px;
```

## 排版模板代码

### 基础框架
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>文章标题</title>
</head>
<body style="background-color: #ffffff; margin: 0; padding: 0;">
<div style="margin: 20px 15px; font-family: -apple-system-font, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif; line-height: 1.8; letter-spacing: 0.5px; color: #374151; background-color: #ffffff; font-size: 16px;">
  <!-- 文章内容 -->
</div>
</body>
</html>
```

### 文章头部信息卡
```html
<div style="margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #1a365d 0%, #2d5a87 100%); border-radius: 12px; text-align: center;">
  <h1 style="font-size: 22px; color: #ffffff; margin: 0 0 15px 0; font-weight: bold; line-height: 1.5;">采访标题：探索未知领域</h1>
  <p style="font-size: 14px; color: rgba(255,255,255,0.85); margin: 0;">
    <span style="margin-right: 15px;">采访：张三</span>
    <span>|</span>
    <span style="margin-left: 15px;">2024年1月15日</span>
  </p>
</div>
```

### 导语卡片
```html
<div style="margin-bottom: 30px; padding: 18px 20px; background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 0 8px 8px 0;">
  <p style="font-size: 15px; color: #92400e; margin: 0; line-height: 1.8;">
    <strong style="color: #b45309;">导读：</strong> 这是一段引导性文字，简要介绍本次采访的背景和目的，让读者快速了解文章将要探讨的核心话题...
  </p>
</div>
```

### 人物介绍卡片
```html
<div style="margin: 25px 0; padding: 20px; background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
  <div style="display: flex; align-items: flex-start; gap: 15px;">
    <div style="width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(135deg, #1a365d 0%, #2d5a87 100%); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
      <span style="color: #ffffff; font-size: 24px; font-weight: bold;">李</span>
    </div>
    <div style="flex: 1;">
      <h3 style="font-size: 18px; color: #1a365d; margin: 0 0 5px 0; font-weight: bold;">受访者：李四</h3>
      <p style="font-size: 13px; color: #6b7280; margin: 0 0 8px 0;">XX公司创始人兼CEO | 资深行业专家</p>
      <p style="font-size: 14px; color: #4b5563; margin: 0; line-height: 1.7;">
        简要介绍受访者的背景、成就或独特之处。这段文字帮助读者快速了解受访者的身份和权威性。
      </p>
    </div>
  </div>
</div>
```

### 问答对话模块 - 记者提问
```html
<div style="margin: 25px 0 15px 0;">
  <!-- 圆形标识在上 -->
  <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #2563eb; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
      <span style="color: #ffffff; font-size: 14px; font-weight: bold;">问</span>
    </div>
    <p style="font-size: 14px; color: #1e40af; margin: 0; font-weight: 600;">记者提问</p>
  </div>
  <!-- 问题内容框在下 -->
  <div style="margin-left: 0; padding: 15px 18px; background-color: #eff6ff; border-radius: 12px;">
    <p style="font-size: 15px; color: #1e40af; margin: 0; line-height: 1.8;">
      这里是记者的提问内容，表述清晰、逻辑分明，引导受访者深入回答。
    </p>
  </div>
</div>
```

### 问答对话模块 - 受访者回答
```html
<div style="margin: 0 0 25px 0;">
  <!-- 圆形标识在上 -->
  <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #f59e0b; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
      <span style="color: #ffffff; font-size: 14px; font-weight: bold;">答</span>
    </div>
    <p style="font-size: 14px; color: #b45309; margin: 0; font-weight: 600; display: flex; align-items: center; gap: 6px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 20h9"></path>
        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
      </svg>
      受访者回答
    </p>
  </div>
  <!-- 回答内容框在下 -->
  <div style="margin-left: 0; padding: 18px 20px; background-color: #fef3c7; border-radius: 12px; border-left: 3px solid #f59e0b;">
    <p style="font-size: 15px; color: #374151; margin: 0; line-height: 1.9;">
      这里是受访者的详细回答内容。可以包含多个段落，表述受访者的观点、经历或思考。建议回答内容充实、有深度，能够给读者带来有价值的 insights。
    </p>
  </div>
</div>
```

### 章节分隔标题
```html
<div style="margin: 40px 0 25px; text-align: center;">
  <div style="display: inline-block; position: relative; padding: 0 30px;">
    <div style="position: absolute; left: 0; top: 50%; width: 100%; height: 1px; background: linear-gradient(90deg, transparent, #e5e7eb, transparent);"></div>
    <span style="position: relative; background-color: #ffffff; padding: 0 15px; font-size: 14px; color: #6b7280; letter-spacing: 2px;">PART 01</span>
  </div>
  <h2 style="font-size: 20px; color: #1a365d; margin: 15px 0 0 0; font-weight: bold;">章节主题标题</h2>
</div>
```

### 背景说明/过渡段落
```html
<div style="margin: 25px 0; padding: 15px 18px; background-color: #f9fafb; border-radius: 8px; border-left: 3px solid #9ca3af;">
  <p style="font-size: 14px; color: #6b7280; margin: 0; line-height: 1.8;">
    <em>这里是背景说明或过渡性文字，用于连接不同的采访段落，帮助读者理解上下文。</em>
  </p>
</div>
```

### 核心观点提炼卡
```html
<div style="margin: 30px 0; padding: 22px 25px; background-color: #ffffff; border: 2px solid #1a365d; border-radius: 12px; position: relative;">
  <div style="position: absolute; top: -12px; left: 20px; background-color: #1a365d; color: #ffffff; font-size: 12px; padding: 4px 12px; border-radius: 20px; font-weight: bold;">
    核心观点
  </div>
  <p style="font-size: 16px; color: #1a365d; margin: 5px 0 0 0; line-height: 1.9; font-weight: 500;">
    "这是受访者提出的核心观点或关键论断，值得读者特别关注和思考的内容。"
  </p>
  <p style="font-size: 13px; color: #6b7280; margin: 12px 0 0 0; text-align: right;">
    —— 受访者姓名
  </p>
</div>
```

### 小标题（带左侧装饰）
```html
<div style="margin: 30px 0 18px; display: flex; align-items: center; gap: 10px;">
  <div style="width: 4px; height: 20px; background: linear-gradient(180deg, #1a365d, #2563eb); border-radius: 2px;"></div>
  <h3 style="font-size: 18px; color: #1a365d; margin: 0; font-weight: bold;">小节标题</h3>
</div>
```

### 分割线
```html
<div style="text-align: center; margin: 35px 0;">
  <div style="display: inline-flex; align-items: center; gap: 15px;">
    <div style="width: 60px; height: 1px; background-color: #e5e7eb;"></div>
    <div style="width: 8px; height: 8px; background-color: #d1d5db; transform: rotate(45deg);"></div>
    <div style="width: 60px; height: 1px; background-color: #e5e7eb;"></div>
  </div>
</div>
```

### 结尾总结卡片
```html
<div style="margin: 35px 0 30px; padding: 25px; background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%); border-radius: 12px; text-align: center;">
  <p style="font-size: 16px; color: #1a365d; margin: 0 0 15px 0; font-weight: bold;">采访结语</p>
  <p style="font-size: 14px; color: #4b5563; margin: 0; line-height: 1.9;">
    这里是采访的总结性陈述，可以回顾核心内容、展望未来，或留下思考空间。
  </p>
</div>
```

### 文章底部信息
```html
<div style="margin-top: 40px; padding-top: 25px; border-top: 1px solid #e5e7eb; text-align: center;">
  <p style="font-size: 13px; color: #9ca3af; margin: 0 0 10px 0;">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 5px;">
      <path d="M12 20h9"></path>
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
    </svg>
    本文完
  </p>
  <p style="font-size: 12px; color: #d1d5db; margin: 0;">
    未经授权禁止转载 | 图文均为原创
  </p>
</div>
```

## 排版规范速查表

| 元素 | 字号 | 颜色 | 背景色 | 说明 |
|------|------|------|--------|------|
| 文章标题 | 22px | #ffffff | 渐变蓝 | 居中，白字 |
| 导语 | 15px | #92400e | #fef3c7 | 浅金底+橙色左边线 |
| 人物介绍卡 | 15-18px | #1a365d | 白底 | 带头像圆标 |
| 记者提问 | 15px | #1e40af | #eff6ff | 问圆标+蓝色内容框 |
| 受访者回答 | 15px | #374151 | #fef3c7 | 答圆标+金色内容框 |
| 核心观点 | 16px | #1a365d | 白底 | 深蓝边框+标签 |
| 章节标题 | 20px | #1a365d | 无 | PART标签 |
| 小节标题 | 18px | #1a365d | 无 | 左侧装饰线 |
| 背景说明 | 14px | #6b7280 | #f9fafb | 灰色斜体 |
| 结尾信息 | 13-14px | #9ca3af | 无 | 居中对齐 |

## 使用说明

### 内容保护原则
- **原意至上**：仅优化视觉呈现，绝不擅自改动采访原意
- **对话完整**：保持问答完整，避免删减重要内容
- **观点中立**：不添加个人立场或评论

### 排版流程建议
1. **确定结构**：先分析采访内容结构（人物介绍、多个问答段落、总结）
2. **提取关键**：识别核心观点和精彩语句
3. **分块排版**：按结构分段处理，每块独立样式
4. **统一风格**：确保全文色彩和间距一致

### 移动端适配
- 所有尺寸使用相对单位（px为辅，%为主）
- 图片最大宽度 100%
- 内边距适中，避免边缘过窄
- 字体大小不低于 14px

## 示例：完整采访文章结构

```
┌─────────────────────────────────┐
│        文章头部信息卡            │
│   (标题 + 采访者 + 日期)        │
├─────────────────────────────────┤
│        导语卡片                  │
│   (背景介绍 + 导读)             │
├─────────────────────────────────┤
│        人物介绍卡片              │
│   (头像 + 姓名 + 职位 + 简介)   │
├─────────────────────────────────┤
│        PART 01 章节标题         │
│   ┌─────────────────────────┐   │
│   │ 背景说明（灰色过渡段落）  │   │
│   └─────────────────────────┘   │
│   ┌─────────────────────────┐   │
│   │ 核心观点提炼卡            │   │
│   │ (深蓝边框高亮展示)        │   │
│   └─────────────────────────┘   │
│   ┌─────────────────────────┐   │
│   │ 问 + 记者提问（标签行）   │   │
│   ├─────────────────────────┤   │
│   │ 蓝色内容框               │   │
│   └─────────────────────────┘   │
│   ┌─────────────────────────┐   │
│   │ 答 + 受访者回答（标签行）   │   │
│   ├─────────────────────────┤   │
│   │ 金色内容框               │   │
│   └─────────────────────────┘   │
├─────────────────────────────────┤
│        PART 02 章节标题         │
│   (更多问答内容...)              │
├─────────────────────────────────┤
│        采访结语                  │
├─────────────────────────────────┤
│        底部版权信息              │
└─────────────────────────────────┘
```
