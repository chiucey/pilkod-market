# Fyc_Software_Design

> 可视化大屏 + 智能应用综合开发模板
> 来源:AI-GIS 智能问图平台 v0.4.0 实战沉淀(2026-08)

## 升级亮点

| 维度 | v1 (2026-07) | v2 (2026-08) | v3 (2026-10-14) |
|---|---|---|---|
| 应用类型 | 单大屏 | 双 Tab (大屏 + AI 问答) | + B 端应用门户 |
| 场景数 | 1 (大屏) | 3 (+ AI 问图 + SSE 实时 + MCP 聚合) | + 多色活力主题 |
| 必问问题 | 3 个 | 6 个 | 7 个 (+业务类型选主题) |
| 硬性原则 | 6 条 | 9 条 (+ 3 条独有) | 9 条不变 |
| 踩坑数 | 13 个 (ECharts) | 13 + 18 = 31 个 (+ AI-GIS) | 31 个不变 |
| **配色主题** | **3 档** (cream/dark/light) | 3 档 | **4 档** (+ bright-portal) | **9 套** (4 色 + 5 色彩理论, 36 色色板, 3×3 九宫格) |
| **按钮组件库** | — | — | **🆕 5 色 × 4 尺寸胶囊** |
| **新增 UI 模式** | — | — | **🆕 9 种** (蜂窝背景/波浪/大色块/环形大数/应用卡/徽章/侧栏/气泡/导航) |
| 部署 | 纯静态 HTML | HTML + FastAPI + Docker + 国产化 | 不变 |
| 安全 | 无 | 三级等保 7 项 + token 三层防御 | 不变 |

## 目录结构

`
Fyc_Software_Design/
├── SKILL.md                       # 入口(必读)
├── README.md                      # 本文件
├── references/                    # 深度文档
│   ├── pitfalls.md                # v1 13 踩坑(ECharts)
│   ├── development-process.md     # v1 7 版迭代回放
│   ├── style-spec.md              # v1 视觉样式
│   ├── tech-stack.md              # v1 技术栈
│   ├── three-local-deploy.md      # v1 Three.js 三方式
│   ├── layout-system.md           # v1 布局
│   ├── color-*.md                 # v1 配色(3 档)
│   ├── ai-gis-pitfalls.md         # 🆕 18 个 AI-GIS 踩坑
│   ├── security-checklist.md      # 🆕 三级等保 + token 安全
│   ├── domestic-deployment.md     # 🆕 国产化(鲲鹏/麒麟)
│   ├── mcp-aggregation.md         # 🆕 MCP 多 server 聚合
│   ├── sse-streaming.md           # 🆕 SSE 实时流
│   ├── dual-tab-pattern.md        # 🆕 双 Tab 模式
│   ├── case-study-bright-mode.md  # 🆕 4 张 B 端门户图提炼 (5 色渐变 + 9 种 UI)
│   └── case-study-beijing-idc.md  # 北京 IDC 运维大屏 9 种新图表模式
├── templates/                     # 代码片段
│   ├── charts.md                  # v1 八大图表
│   ├── ai-chat.html               # 🆕 AI 问答界面
│   ├── sse-dashboard.html         # 🆕 SSE 实时大屏
│   ├── security-config.py         # 🆕 FastAPI 安全中间件
│   ├── mcp-server.py              # 🆕 MCP 聚合网关
│   ├── indicator-card.md          # 4 资源剩余风格指标卡
│   ├── design-proposal.md         # 设计方案模板
│   ├── capsule-buttons.md         # 🆕 5 色 × 4 尺寸胶囊按钮组件库
│   ├── theme-preview.html         # 🆕 9 套主题 SVG 预览(3×3 九宫格,用户选主题用)
│   └── random-theme-generator.html # 🆕 随机配色生成器(4 色 + 锁色 + 历史回溯)
└── assets/                        # 实战素材
    └── js/
        ├── fit-scale.js           # v1 等比缩放
        ├── marquee.js             # v1 跑马灯
        ├── check.js               # v1 浏览器自检
        ├── self-check.py          # v1 Playwright 自检
        └── map-mode-switch.js     # v1 2D/3D 切换
`

## 能力边界(2026-08-30 明确)

| 格式 / 场景 | 支持 | 说明 |
|---|---|---|
| HTML + CSS + JS | ✅ 核心 | ECharts / echarts-gl 大屏 |
| 双 Tab 应用 | ✅ 核心 | 大屏 + AI 问答(`templates/ai-chat.html`) |
| SSE 实时流 | ✅ 核心 | `templates/sse-dashboard.html` |
| Python FastAPI 后端 | ✅ 核心 | 含 SSE / MCP 聚合(`templates/mcp-server.py`) |
| FastAPI 安全中间件 | ✅ 核心 | `templates/security-config.py` |
| TypeScript + Vite | ✅ 间接 | `references/tech-stack.md` |
| Python 自检脚本 | ✅ 辅助 | `assets/js/self-check.py` |
| 三级等保安全 | ✅ 实战 | `references/security-checklist.md` |
| 国产化部署(鲲鹏/麒麟) | ✅ 实战 | `references/domestic-deployment.md` |
| 图表库替换 | ✅ 可替换 | Chart.js / D3 / AntV / VChart |
| Vue / React 组件化 | ✅ 可改造 | 按 Vite 模板包装 |

| 格式 / 场景 | 不支持 | 原因 |
|---|---|---|
| **Java / Spring Boot 后端** | ❌ | 本技能后端用 Python FastAPI,不输出 Java |
| Kotlin / Scala / Go / Rust | ❌ | 生态不匹配 |
| Java Swing / JavaFX 桌面 | ❌ | 本技能只输出 Web 应用 |
| 移动端 H5 | ❌ | 响应式 layout 不匹配大屏 1920×1080 |
| 单个简单图表 | ❌ | 过度设计,直接 ECharts 即可 |

**跨技能合作模式**(场景 A 跨 Java / Python 边界):
- 本技能提供:前端 + `data/sample.json` 字段契约
- 后端团队实现:Spring Boot / FastAPI 任一语言,字段名照搬
- 拼接:`fetch('/api/xxx')` 换源即可

## 怎么用

1. **读 SKILL.md** —— 入口,9 原则 + 7 必问 + 3 场景 + 9 档主题
2. **用户没指定主题? 发主题预览图让用户选**
   - 打开 `templates/theme-preview.html`(4 张 SVG 预览,纯静态 HTML,可双击)
   - 用户点击卡片选 cream / dark-tech / light-blue / bright-portal
   - 不选则默认 cream
3. **场景对应读 references/**:
   - 做大屏(单屏 cream) → style-spec.md / pitfalls.md / templates/charts.md
   - 做 B 端应用门户(bright-portal) → case-study-bright-mode.md / templates/capsule-buttons.md
   - 做 AI 问答 → dual-tab-pattern.md / templates/ai-chat.html
   - 做实时流 → sse-streaming.md / templates/sse-dashboard.html
   - 做 MCP 集成 → mcp-aggregation.md / templates/mcp-server.py
   - 做三级等保 → security-checklist.md / templates/security-config.py
   - 做国产化部署 → domestic-deployment.md
   - 案例研究 → case-study-beijing-idc.md(9 种新图表模式)
4. **踩坑速查** → pitfalls.md(13) + ai-gis-pitfalls.md(18) + case-study 里实战踩坑
5. **交付前必走自检** → assets/js/self-check.py

## 与 v1 兼容

- v1 的 8 大图表 / cream 配色 / 1920×1080 / 13 踩坑 / 自适应 全部保留
- v2 多了 AI + 实时流 + 安全 + 国产化 4 大能力
- v3 多了 bright-portal 第 4 档主题 + 5 色胶囊按钮 + 9 种新 UI 模式(蜂窝/波浪/大色块/环形大数/应用卡/徽章/侧栏/气泡/导航)
- v3.4 多了 9 套配色(每套严格 4 色 + 3 色彩理论 + 全部浅底色 + 0 红粉/深底, 36 色色板, 3×3 九宫格预览, 4 张参考图风格)
- 老项目想升级:把 SKILL.md 替换为最新版,加 references/v2-*.md 和 v3 case-study-bright-mode.md 即可

## 来源

AI-GIS 智能问图平台 v0.4.0 实战(2026-08)
