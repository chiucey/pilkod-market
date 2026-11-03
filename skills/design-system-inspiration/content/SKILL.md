---
name: design-system-inspiration
description: 提供设计系统灵感，帮助创建像素级精确的 UI。当用户需要为项目选择设计风格、参考知名公司设计规范、创建 DESIGN.md 设计文档，或要求生成符合特定品牌调性的界面时使用。关键词：设计系统、设计规范、DESIGN.md、设计灵感、Stripe 设计、Linear 设计、颜色规范、字体规范。
---

# Design System Inspiration

提供 58+ 知名科技公司的设计系统灵感，帮助生成像素级精确的 UI 界面。

## 工作流程

### 1. 理解用户需求

用户可能需要：
- 选择特定品牌的设计风格（如 Stripe、Linear、Figma）
- 参考多个设计系统来创建自定义方案
- 基于某品牌创建完整 DESIGN.md 文档

### 2. 查找设计系统

访问 `/workspace/temp-extract/awesome-design-md-main/design-md/` 目录下的设计系统：

**AI & Machine Learning**
- claude, cohere, elevenlabs, minimax, mistral.ai, ollama, opencode.ai, replicate, runwayml, together.ai, voltagent, x.ai

**Developer Tools**
- cursor, expo, linear.app, lovable, mintlify, posthog, raycast, resend, sentry, supabase, superhuman, vercel, warp, zapier

**Infrastructure & Cloud**
- clickhouse, composio, hashicorp, mongodb, sanity, stripe

**Design & Productivity**
- airtable, cal.com, clay, figma, framer, intercom, miro, notion, pinterest, webflow

**Fintech & Crypto**
- coinbase, kraken, revolut, wise

**Enterprise & Consumer**
- airbnb, apple, ibm, nvidia, spacex, spotify, uber

**Car Brands**
- bmw, ferrari, lamborghini, renault, tesla

### 3. 提供设计参考

读取选定的 DESIGN.md 文件，提供以下关键信息：

1. **视觉主题**：品牌调性、核心特征
2. **色彩系统**：主色、辅色、强调色、渐变色
3. **字体规范**：字体族、字号层级、字重、行高、字间距
4. **组件样式**：按钮、卡片、输入框、导航
5. **阴影系统**：层级、颜色、偏移量
6. **布局原则**：间距、圆角、响应式策略
7. **Do's and Don'ts**：设计禁区
8. **Agent 提示模板**：可直接使用的组件代码提示

### 4. 生成设计建议

根据用户项目需求，从设计系统中提取：
- 适合的色彩方案
- 字体搭配建议
- 组件样式代码
- 具体的设计实现提示

## 快速参考

### 热门设计系统特点

| 品牌 | 特点 | 典型色值 |
|------|------|----------|
| Stripe | 金标金融设计，蓝调阴影，weight 300 | #533afd, #061b31 |
| Linear | 暗色原生，Inter Variable，510字重 | #5e6ad2, #08090a |
| Figma | 变量字体，胶囊按钮，黑白界面 | #000000, #ffffff |
| Vercel | 极简黑白，Geist字体 | #000000, #ffffff |
| Notion | 温暖极简衬线标题 | #000000, #ffffff |
| Supabase | 暗色翡翠绿，代码优先 | #3ecf8e, #1c1e21 |

## 示例使用

**用户请求**："我想要一个类似 Linear 的暗色主题"

**响应流程**：
1. 读取 `linear.app/DESIGN.md`
2. 提取关键规范：
   - 背景色：`#08090a`
   - 主文字：`#f7f8f8`
   - 强调色：`#5e6ad2` / `#7170ff`
   - 字体：Inter Variable，OpenType cv01/ss03
   - 字重：510（签名字重）
3. 提供具体组件提示代码

## 输出格式

提供：
1. 设计系统概览
2. 关键色彩代码（可直接复制）
3. 字体配置
4. 组件 CSS 片段
5. 设计禁区提醒
