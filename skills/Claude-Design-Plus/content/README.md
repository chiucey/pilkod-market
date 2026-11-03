# Claude-Design-Plus

🎨 **让 AI 成为你的设计伙伴** — 通过自然语言对话即可生成专业级设计稿、可交互原型和演示文稿。

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![Platform](https://img.shields.io/badge/platform-Claude%20Code-orange.svg)]()

## 特性

- 🌍 **50+ 设计系统内置** — 国际大厂 + 中国知名企业全覆盖
- 🎯 **自然语言驱动** — 说出想法，AI 帮你做设计
- ⚡ **所见即所得** — HTML 原型可交互，Tweak 实时调整
- 📊 **多格式导出** — PPTX、PDF、HTML
- 🇨🇳 **中国设计系统** — 微信、支付宝、抖音、Ant Design 等

## 内置设计系统

### 🏢 开发工具
GitHub, Linear, Vercel, Stripe, Figma, Cursor, Arco Design, Tencent CDC

### 🤖 AI & 大模型
Anthropic, OpenAI, Cohere, ElevenLabs, 百度 AI, 阿里通义千问

### 💬 社交通讯
Discord, Slack, Telegram, 微信, 钉钉

### 🛒 电商零售
Shopify, Pinterest, 淘宝, 京东, 美团, 小红书

### 💰 金融支付
Coinbase, Stripe Payments, 支付宝, 微信支付

### 📱 内容媒体
YouTube, Spotify, Medium, 抖音, B站, Netflix

### 💻 OS 硬件
Apple HIG, Google Material, Microsoft Fluent, 华为 HarmonyOS, 小米 MIUI

### ⚡ 效率工具
Notion, Canva, Zoom, 飞书, Ant Design, Element Plus

### 🎮 游戏娱乐
Twitch, Epic Games, 米哈游, 腾讯游戏

## 快速开始

### 启动 Skill

```
/Claude-Design-Plus
```

### 示例命令

**设计登录页面**
```
"帮我设计一个电商 App 的登录页面，使用 Ant Design 风格"
```

**制作产品介绍 PPT**
```
"做一个 SaaS 产品介绍 PPT，包含功能介绍、价格方案、客户案例"
```

**创建可交互原型**
```
"设计一个抖音风格短视频 App 的个人主页原型"
```

**切换设计风格**
```
"把这个设计从 Stripe 风格切换到 Apple 风格"
"试试支付宝的视觉风格"
```

## 工作流程

```
1️⃣ 描述需求 → 2️⃣ 选择设计系统 → 3️⃣ 探索变体 → 4️⃣ 精细调整 → 5️⃣ 导出交付
```

## 导出格式

| 格式 | 适用场景 | 说明 |
|------|----------|------|
| HTML | 可交互原型 | 最灵活，可分享链接 |
| PPTX | 演示文稿 | 可编辑，适合演讲 |
| PDF | 打印/导出 | 高保真，适合交付 |

## 安装

### Claude Code

```bash
claude plugin marketplace add https://github.com/YOUR_USERNAME/Claude-Design-Plus
```

### 手动安装

1. 克隆此仓库
2. 将 `designs/` 目录复制到你的项目
3. 在 Claude Code 中加载 `SKILL.md`

## 项目结构

```
Claude-Design-Plus/
├── SKILL.md              # 主技能文件
├── README.md             # 本文件
└── designs/              # 内置设计系统
    ├── index.md          # 设计系统索引
    ├── github.md         # GitHub 设计系统
    ├── stripe.md         # Stripe 设计系统
    ├── ant-design.md     # Ant Design
    ├── wechat.md         # 微信设计
    └── ...               # 更多设计系统
```

## 设计原则

### DO ✅
- 描述你的用户是谁、需求是什么
- 说明设计的使用场景
- 提供品牌素材或参考链接
- 要求多个变体进行比较

### DON'T ❌
- 不要只说"做个好看的设计"
- 不要期望 AI 完全猜对你的意图

## 常见问题

**Q: 需要设计经验吗？**
A: 不需要。你只需要描述你的想法。

**Q: 支持自定义设计系统吗？**
A: 支持。提供 Figma 文件、设计规范文档即可。

## 参考资源

- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)
- [Ant Design](https://ant.design/)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design](https://m3.material.io/)

## License

MIT
