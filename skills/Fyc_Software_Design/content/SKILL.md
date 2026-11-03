---
name: Fyc_Software_Design
description: 可视化大屏 + 智能应用综合开发模板。保留 v1 全部能力（cream 配色 / 8 大图表 / 1920×1080 / 13 踩坑 / 自适应缩放），新增 9 条硬性原则、3 个新场景（AI 智能问图 / SSE 实时大屏 / MCP 多 server 聚合）、18 个 AI-GIS 实战踩坑、6 个必问问题。基于 AI-GIS 智能问图平台 v0.4.0 实战沉淀（2026-08）+ 9 档主题（cream/dark-tech/light-blue/bright-portal/green-fresh/orange-energy/purple-elegant/pink-creative/dark-portal，3×3 九宫格预览）+ 5 色胶囊按钮组件库。仅前端 HTML/JS/CSS + Python FastAPI 后端，不包含 Java/Spring 后端代码。Trigger:用户给参考图，要求"做大屏 / 智能问图 / 实时大屏 / B 端管理门户 / 拷贝这张图 / 应用门户首页 / 浅色多色风格 / 选个主题"。
---

# Fyc_Software_Design - 可视化大屏 + 智能应用综合开发模板

> **定位**:不只做大屏,还做"大屏 + AI 对话 + 实时流"复合应用。
> **来源**:v1 (风力能源监控 cream 模板) + AI-GIS 智能问图平台 v0.4.0 实战沉淀(2026-08)
> **核心变化**:从"单大屏"→"大屏 + 智能问答"双 tab 模式,新增 SSE 实时流 / MCP 聚合 / 三级等保 / 国产化部署

## ⚡ 能力边界(2026-08-30 明确)

**能做**:
- HTML + CSS + JS 全静态大屏(ECharts / echarts-gl)
- **双 Tab 复合应用**:大屏 + AI 问答(templates/ai-chat.html)
- **SSE 实时流大屏**(templates/sse-dashboard.html)
- **FastAPI + MCP 多 server 聚合**(templates/mcp-server.py)
- TypeScript + Vite 工程化(见 references/tech-stack.md)
- Python 自检脚本 + FastAPI 安全中间件(security-config.py)
- 三级等保安全检查 + 国产化(鲲鹏/麒麟)部署

**不能做**(如需这些能力,请用其他技能/人工接手):
- ❌ **Java / Spring Boot 后端** —— 本技能后端用 Python FastAPI,不输出 Java 代码
- ❌ Java Swing / JavaFX 桌面应用
- ❌ Kotlin / Scala / Go / Rust —— 生态不匹配
- ❌ 移动端 H5 —— 响应式 layout 不匹配大屏 1920×1080 固定设计
- ❌ 单个简单图表 —— 过度设计,直接 ECharts 即可

**场景 A:对接 Java 后端 API**(2026-07 约定,跨技能合作):
- 本技能负责:前端 HTML + ECharts + `data/sample.json`(字段契约)
- 后端团队负责:照 `sample.json` 写 Java API,返相同 JSON 结构
- 拼接方式:前端 `fetch('/api/xxx')` 换源,业务逻辑不动

**场景 B:全栈本技能栈**(v2 独有,2026-08 实战):
- 前端:HTML + ECharts(本技能)
- 后端:Python FastAPI + SSE(real-time)
- AI 网关:MCP 多 server 聚合(templates/mcp-server.py)
- 部署:HTML + FastAPI + Docker + 鲲鹏/麒麟

---

## 🎨 默认实现:**"双 Tab 复合应用"模式**(2026-08 确认)

**所有"数据可视化 + AI"复合应用默认按这个模式实现**。除非用户明确指定其他风格,否则:

### 双 Tab 模式(Dashboard + AI 问图)
- **Tab 1 - Dashboard**:经典大屏(ECharts 8 大图表 / cream 配色 / 地图满屏 / 联动)
- **Tab 2 - AI 智能问答**:聊天界面 + 流式输出 + 自动触发地图/图表
- **切换**:顶部 tab 切换,带底部蓝色弧形发光阴影
- **Tab 1 激活态**:底部 3px 蓝线(`box-shadow: inset 0 -4px 0 0 rgba(96, 165, 250, 0.85)`)上提一点
- **跨 tab 记忆**:AI 问答生成的图层 / 高亮保留,切回 dashboard 仍可见

### 配色方案(沿用 v1,扩展深色友好 + 9 档主题,2026-10-14 加)
- **底色(亮)**:cream 奶油白 + 极淡蓝渐变(`radial-gradient(ellipse at top, #e8f1fa 0%, #f5f9fd 50%, #ffffff 100%)`)
- **底色(暗)**:slate-900 + radial(查询 token 时友好,文字用 slate-200+)
- **主文字**: `#1e3a6e`(亮) / `#e2e8f0`(暗)
- **强调**: `#4a7bb8`(主) / `#8fbcff`(亮蓝)
- **面板**: `rgba(255,255,255,0.78)`(亮) / `rgba(30, 41, 59, 0.78)`(暗)
- **警示/高亮**: `#ff9a3c`(橙) / `#4ade80`(绿) / `#f87171`(红)

#### 🆕 9 套配色方案(每套严格 4 色 + 全部浅底色 + 参考 4 张图,2026-10-14)
**4 色 = 主色 + 辅色 + 背景 + 文字 · 36 色色板 · 3 种色彩理论 · 0 红粉/深底**

| # | 主题名 | 色彩理论 | 来源图 | 4 色 | 适用场景 |
|---|---|---|---|---|---|
| 1 | **mono-blue**(默认) | 单色 | — | `#F0F9FF` `#BAE6FD` `#0284C7` `#0C4A6E` | 业务监控 · 工业能源 · 严肃场景 |
| 2 | mono-sky | 单色 | — | `#F0F9FF` `#E0F2FE` `#0EA5E9` `#0C4A6E` | 政企管理 · 金融监控 · 工业能源 |
| 3 | blue-orange | 互补 | — | `#F0F9FF` `#0284C7` `#F97316` `#0F172A` | 应用门户 · KPI 大屏 · 强对比 |
| 4 | **cyan-blue** | 互补 | 📷 图1 General statistics | `#ECFEFF` `#06B6D4` `#0284C7` `#164E63` | 运营总览 · 多区域监控 · 浅蓝科技 |
| 5 | green-cyan | 类比 | — | `#F0FDF4` `#10B981` `#0EA5E9` `#064E3B` | 医疗健康 · 环保 · 农业 |
| 6 | warm-amber | 类比 | — | `#FFFBEB` `#F97316` `#F59E0B` `#7C2D12` | 销售业绩 · 电商 · 营销活动 |
| 7 | **portal-mint** | 类比 | 📷 图2 大数据可视化浅色系 | `#F0FDFA` `#14B8A6` `#0EA5E9` `#134E4A` | 数据分享 · 设计封面 · 清新门户 |
| 8 | **portal-bright** | 混合 | 📷 图3 采购大数据 4 大色卡 | `#F0F9FF` `#4A8BFF` `#10B981` `#0F172A` | 采购监控 · 业务大屏 · 4 大分类 |
| 9 | **gold-bright** | 类比 | 📷 图1 5 色 brand 选黄+绿 | `#FEFCE8` `#F59E0B` `#10B981` `#0F172A` | 业务总览 · 支付监控 · 品牌展示 |

**剔除的 5 套**(用户反馈"偏红粉/深底不好"): mono-dark / triadic-purple / analogous-pink / split-complement-violet

→ 9 张 SVG 预览 + 36 色色板见 `templates/theme-preview.html`(双击打开,3×3 九宫格可点击选)
→ 想再组合? `templates/random-theme-generator.html`(随机生成 + 锁色 + 历史回溯)
→ 详细 9 套配色 + 色彩理论见 `references/case-study-bright-mode.md`
→ 5 色胶囊按钮组件库见 `templates/capsule-buttons.md`

### 字号(默认,沿用 v1)
- 主标题 46 / 时钟 40 / 总计 38 / 卡片 22 / Tab 20 / 面板 18 / 标签 14-15

### 字号(暗色模式额外规则)
- **深色背景上的正文/参数, 必须 `#e2e8f0`(slate-200)及以上**, 不能用 slate-400 及更暗
- **代码片段**: `rgba(96,165,250,0.18)` 底 + `#bfdbfe` 字
- **最低标准**:文字 vs 背景对比度 ≥ 4.5:1

### 布局(1920×1080 + transform scale)
- 头部 80px(三栏合并 / logo + 标题 + 时钟)
- 主体:Tab 切换(Dashboard 满屏地图 / AI 问答左右分栏)
- 底部:Tab 浮在中间 + 蓝色发光阴影

---

## 🚨 九大硬性原则(2026-08 升级)

| # | 原则 | 实现方式 | 违反后果 |
|---|---|---|---|
| 1 | **资源全部本地化** | ECharts / echarts-gl / china.json / 字体 / 静态数据 全部 `assets/` | CDN 被墙就 empty |
| 2 | **1920×1080 + transform scale** | 设计稿固定尺寸 + `Math.min(innerWidth/1920, innerHeight/1080)` 算 scale | 200% 系统缩放错位 |
| 3 | **默认 PNG 截图交付** | 不主动 deploy 到公网;用户明确要链接才 deploy | 公网暴露不想公开的内容 |
| 4 | **必走自检工作流** | Playwright 多分辨率截图 + console 错误 + 联动 API 验证 | bug 漏到用户手里 |
| 5 | **联动 API 用 `window.xxxChart`** | `highlight/clear` 双向 + `syncFromXxx` 桥接 | 图表各自为政,大屏失败 |
| 6 | **配色 60/30/10 比例** | 中性 60% / 主色 30% / 强调 10% | 视觉杂乱,失去高级感 |
| 7 | **字号硬性下限** | 标题 36 / 面板 16 / 总计 32 | 用户每次都嫌"小" |
| 8 | **Three.js 默认禁用** | 默认 ECharts 2D,询问后才加 r3f | 包大 + 性能差 + 兼容性差 |
| 9 | **🆕 暗色模式文字 ≥ slate-200** | 深色背景正文禁止 slate-400 及更暗 | 灰字看不清,每次都被骂 |

### 🆕 v2 独有原则
| # | 原则 | 实现方式 | 原因 |
|---|---|---|---|
| A | **SSE 实时流用 `EventSource`** | 后端 `text/event-stream` + 前端 `new EventSource(url)` | 简单场景比 WebSocket 简单 10 倍 |
| B | **token 字段前端永远 masked** | 后端永远返 `***abc`,前端 placeholder 模式输入,服务端守卫检测掩码 | 防止"前几天还好"回归 |
| C | **默认不破坏已有功能/设置** | 新功能默认 OFF,环境变量开启;跑过的老数据兼容 | 加新功能不能"修好一个打坏三个" |
| D | **双电脑工作流友好** | 排除 .venv / __pycache__ / logs;启动脚本第一步 venv check | 拷贝到另一台电脑不用修配置 |

---

## 🚦 六个必问问题(2026-08 升级,原 3 + 新 3)

**所有任务开始前先问,不要先动手**。

| # | 问题 | 必问理由 | 默认答案(用户不答) |
|---|---|---|---|
| 1 | **是否需要 Three.js / 真 3D?** | 默认 ECharts 2D,Three.js 增复杂度+包大 | **否 → ECharts 2D** |
| 2 | **是否需要 deploy 到公网?** | 默认 PNG 截图;deploy 仅在用户明确要时 | **否 → 截图交付** |
| 3 | **是否参考特定风格图?** | 没参考图则按"双 Tab cream"默认;有则 1:1 复刻 | **是 → cream 风格** |
| 3a | **🆕 业务类型是什么?(2026-10-14)** | 决定用哪档主题:大屏/门户/管理后台 三类 | **单屏大屏 → cream;门户/管理 → bright-portal** |
| 4 | **🆕 是否需要 AI 问答 tab?** | AI 智能问答需要 LLM 接入 + 流式输出,非默认能力 | **询问 → 业务是否需要** |
| 5 | **🆕 是否需要实时数据流?** | SSE / WebSocket 跟静态数据架构不同,需要后端配套 | **询问 → 数据更新频率** |
| 6 | **🆕 部署环境是什么?** | 国产化(麒麟/UOS) vs Windows vs 容器 vs 纯静态 HTML,差异巨大 | **询问 → 影响技术栈选型** |
| 7 | **🆕 业务类型是什么?(2026-10-14 加)** | 决定用哪档主题:大屏 / 应用门户 / 管理后台 三类 | **单屏大屏 → cream 主题;门户/管理后台 → bright-portal** |

### 询问模板

```
问题 1 (Three.js):
> 你的应用要 Three.js 真 3D 渲染吗?
> - 是: 引入 React-Three-Fiber,有立体感但稍重
> - 否: 默认 ECharts 2D,轻量全浏览器兼容 ← 默认

问题 2 (deploy):
> 完成后 deploy 到公网给你看吗?
> - 是: 给你一个 URL 链接
> - 否: 直接给截图(zip)看效果 ← 默认

问题 3 (风格参考 + 业务类型, 2026-10-14 升级):
> 你的业务类型是什么? 这决定用哪档主题。
> - 单屏监控大屏 → cream 主题(默认)
> - 数据中心深色仪表盘 → dark-tech
> - 工业能源冷色调 → light-blue
> - B 端应用门户/管理后台 → bright-portal
>
> **没把握? 先发主题预览图让用户选**
> → 打开 `templates/theme-preview.html`,9 张 SVG 预览(3×3 九宫格,cream/dark-tech/light-blue/bright-portal/green-fresh/orange-energy/purple-elegant/pink-creative/dark-portal),每张标注适用场景
> → 用户点击卡片即确认主题
> → 想「再随机看看」? 打开 `templates/random-theme-generator.html`(随机 4 色 + 锁色 + 历史回溯,自动协调)
>
> 完整描述: 有具体参考图/参考网站吗?
> - 有: 告诉我(发图或 URL),1:1 复刻
> - 没有: 按"双 Tab cream"风格默认(cream + 8 大图表 + AI 问答) ← 默认

问题 4 (AI 问答):
> 需要 AI 智能问答 tab 吗?
> - 是: 加 LLM 接入 + SSE 流式输出,需要 API key
> - 否: 保持纯 dashboard ← 默认

问题 5 (实时数据流):
> 数据需要实时更新吗(SSE/WebSocket)?
> - 是: 加实时流管线
> - 否: 静态数据 + 手动刷新 ← 默认

问题 6 (部署环境):
> 部署到哪种环境?
> - 国产化(麒麟/UOS/鲲鹏): 需 Python 4 级 fallback + pathlib 跨平台
> - Windows: 标准 Python venv
> - 容器(Docker): 加 Dockerfile + .dockerignore
> - 纯静态 HTML: 无后端,直接 browser 打开
```

### 走默认的判定
- 任一不答 → 走默认
- 4 不答 → 走纯 dashboard(无 AI tab)
- 5 不答 → 走静态数据
- 6 不答 → 走 Windows 标准(最常见)

---

## 📦 标准交付结构(双 Tab 模式)

```
project/
├── index.html                  # 入口(双 Tab 切换)
├── css/
│   ├── style.css               # 全局 + dashboard 样式
│   ├── chat.css                # AI 问答 tab 样式
│   └── table.css
├── js/
│   ├── data.js                 # 静态数据
│   ├── chat.js                 # AI 问答客户端(SSE 流式)
│   ├── chart-top10.js
│   ├── chart-line.js
│   ├── chart-table.js
│   ├── chart-map.js
│   ├── chart-summary.js
│   ├── chart-quarter.js
│   ├── chart-equipment.js
│   └── main.js                 # 时钟 + 跑马灯 + 联动 + 自适应 + Tab 切换
├── assets/
│   ├── echarts.min.js          # 必须本地
│   ├── echarts-gl.min.js       # 必须本地
│   ├── china.json              # 必须本地(DataV GeoJSON)
│   └── preview.png
├── backend/                    # (可选) FastAPI 服务
│   ├── app.py
│   ├── crypto.py               # PBKDF2 + Fernet 加密
│   ├── security.py             # IP 白名单 / 审计 / 限流
│   ├── audit_middleware.py
│   └── scripts/
│       ├── check_venv.py       # 双电脑 venv 自检
│       └── pre_sync_cleanup.py # 拷贝前清理(.venv / __pycache__)
└── docs/
    ├── README.md
    ├── QUICKSTART.md
    ├── SECURITY.md             # 三级等保
    ├── DOMESTIC.md             # 国产化
    └── ...
```

---

## 🎯 三大新场景(2026-08 新增)

### 场景 1: AI 智能问图(基于 AI-GIS 实战)
- **前端**:聊天界面 + 输入框 + 流式输出 + 自动解析 LLM 返回的"工具调用"触发地图/图表
- **后端**:FastAPI + LLM(OpenAI / 通义 / 文心 / 自建) + MCP 多 server 聚合
- **关键能力**:
  - 自然语言查"浙江省的 POI"→ 自动调 LLM → 解析工具名 → 调 GIS API → 在地图渲染
  - 流式输出(SSE)逐字显示,边生成边执行工具
  - 对话历史(切 tab 保留,F5 刷新清空)

详细:references/dual-tab-pattern.md

### 场景 2: SSE 实时数据大屏
- **后端**:FastAPI `StreamingResponse` + `text/event-stream`
- **前端**: `new EventSource('/api/stream')` + onmessage 更新图表
- **典型场景**:实时监控(IoT 传感器 / 告警 / 计数器 / sparkline 滚动)
- **降级**:断线自动重连(`EventSource` 原生支持)

详细:references/sse-streaming.md

### 场景 3: MCP 多 server 聚合
- **架构**:1 个主 MCP server (stdio) + 多个子 server(GIS / QGIS / 数据库 / ...)
- **关键能力**:
  - 工具名空间隔离(server_name__tool_name)
  - 动态加载/卸载子 server
  - 跨 server 工具调用编排
  - 健康检查 + 故障转移

详细:references/mcp-aggregation.md

---

## 📚 18 个 AI-GIS 实战踩坑(2026-08 新增)

**完整 18 个踩坑见 references/ai-gis-pitfalls.md**。这里列核心 12 个:

| # | 踩坑 | 根因 | 解决 |
|---|---|---|---|
| 1 | **F5 刷新后 AI 记忆清空** | 浏览器内存,无持久化 | 默认行为;需持久化用 IndexedDB |
| 2 | **天地图 POI 一直不显示** | `clearMap` 传 null 导致 Cesium 抛错 | try-catch 容错,Cesium 兼容 |
| 3 | **token 在 config 里被覆盖成掩码** | 后端返 `***xxx` → 前端填回去 → 保存写回 | placeholder 模式 + 服务端守卫 |
| 4 | **Python venv 跨电脑爆炸** | `pyvenv.cfg` 锁旧电脑 Python 路径 | 启动脚本第一步 `check_venv.py --check` |
| 5 | **dashboard 底边框差一点点** | 用户视觉误差"差一点点" | 加粗 + 上提 4px,变成 inset shadow |
| 6 | **WebSocket 重连风暴** | 网络抖动导致指数级重连 | 退避策略 + 心跳 + 最大重试 |
| 7 | **大模型流式输出 buffer 太大** | EventSource 不限速 → 内存爆 | 后端限速 + 前端 throttle 显示 |
| 8 | **国产化平台 cryptography 装不上** | pip 编译要 glibc | 降版本 + 4 级 fallback 文档 |
| 9 | **SSE nginx 反代 buffer** | nginx 默认 proxy_buffering on → SSE 卡住 | `proxy_buffering off` + `X-Accel-Buffering: no` |
| 10 | **Cesium Ion token 过期** | 试用 30 天 | 用天地图 token 替代(国内项目) |
| 11 | **GeoJSON 文件太大,加载慢** | 100+ MB 省级边界 | 只加载用到的省 + 简化(100 KB) |
| 12 | **CSS @import 跨域失败** | CORS 限制 | 走 `<link>` 标签,不用 @import |

完整 6 个扩展踩坑见 references/ai-gis-pitfalls.md

---

## 🛡️ 三级等保 + 国产化(2026-08 新增)

### 三级等保 7 项覆盖(基于 AI-GIS v0.4.0 实战)

| # | 三级等保要求 | 实现方式 | AI-GIS 文件 |
|---|---|---|---|
| 1 | **身份鉴别(密码加密存储)** | PBKDF2-HMAC-SHA256 200k 迭代 + 32 字节 salt | `crypto.py` |
| 2 | **敏感信息加密存储** | Fernet AES-128-CBC 自动检测明文/密文 | `crypto.py` + `config_store.py` |
| 3 | **访问控制(IP 白名单)** | `GIS_IP_WHITELIST` 环境变量,默认 OFF | `security.py` |
| 4 | **安全审计(操作日志)** | `GIS_AUDIT_LOG=1` 写 `logs/audit.log` | `audit_middleware.py` |
| 5 | **恶意代码防范(输入校验)** | Pydantic schema + 长度限制 | FastAPI 自动 |
| 6 | **数据完整性(config hash)** | `data/.sha256` 校验,损坏从 `.bak` 回滚 | `config_store.py` |
| 7 | **备份恢复** | save 时自动 `.bak` 备份 | `config_store.py` |

**详细**: references/security-checklist.md

### 国产化部署(鲲鹏/飞腾/麒麟/UOS)

| 平台 | CPU | OS | Python | Node | 关键差异 |
|---|---|---|---|---|---|
| 鲲鹏 920 | ARM64 | 麒麟 V10 / UOS 1050 | 3.8+ (4 级 fallback) | 18+ ARM64 | cryptography 需选 `*-manylinux2014_aarch64` |
| 飞腾 2000 | ARM64 | 银河麒麟 | 3.8+ | 18+ ARM64 | 同上 |
| 海光 7285 | x86_64 | UOS 1050 | 标准 | 标准 | 兼容 |
| 兆芯 KH-30000 | x86_64 | 麒麟 V10 | 标准 | 标准 | 兼容 |

**4 级 fallback**(无网络或编译失败时):
1. `cryptography` (首选,二进制 wheel)
2. `pycryptodome` (备选,pure python)
3. `hashlib + secrets` (内置,只支持摘要,不支持对称加密)
4. 文档明文警告(最差,需手动管理)

**详细**: references/domestic-deployment.md

---

## 🔄 双电脑文件夹拷贝工作流(2026-08 新增)

**针对单位/家里双电脑,不用 git 的简单工作流**。

### 拷贝前必跑清理
```bash
# 排除 .venv (~130MB) + __pycache__ (~180个) + logs + *.log
python scripts/pre_sync_cleanup.py --apply --target E:\Work\Minimax\AI_GIS_copy
```

### 拷贝后必跑 venv 检查
```bash
# 检查 .venv 路径是否还指旧电脑
python scripts/check_venv.py --check
# exit ≠ 0 → 自动删 .venv 重建
```

### 跨电脑日志处理
- 各自电脑的 logs/ **不进版本管理**,也不拷贝
- 跨电脑混一起会乱(时间戳/路径不一致)

**详细**: 根目录的 AI-GIS `AGENTS.md` 中"双电脑工作流"小节

---

## 🧰 自检工作流(沿用 v1,扩展到 AI 场景)

```bash
# 1. 启动本地服务(静态或 FastAPI)
cd project && python -m http.server 8000
# 或
.\.venv\Scripts\pythonw.exe app.py

# 2. 跑自检(Playwright)
python assets/js/self-check.py

# 3. AI 场景额外跑对话链路测试
python tests/test_ai_chat.py
```

自检脚本会:
1. 访问 4 个分辨率(1920 / 3840 / 1366 / 2560)
2. 截图保存到 `.check-*.png`
3. 抓取 console errors + pageerrors
4. 检查所有 `window.xxxChart` API 是否暴露
5. 检查关键 DOM 元素是否存在
6. 模拟点击地图/TOP10/表格,验证联动
7. 按 Esc 验证清空
8. 抓取 `--scale` CSS 变量值
9. **🆕** AI 场景:发送 query → 等响应 → 验证工具被调用 → 验证地图有变化
10. **🆕** 双 Tab 切换:点 Tab 2 → 验证 AI 界面渲染 → 点回 Tab 1 → 验证 dashboard 恢复
11. 输出 ✓/✗ 报告

**自检不通过不交付。**

---

## 📜 文档索引

### 核心文件
- `SKILL.md` (本文件) - 入口 + 9 原则 + 6 必问 + 3 场景

### references/ (深度文档)
- `pitfalls.md` - **v1 13 个 ECharts 踩坑**(完整保留)
- `development-process.md` - **v1 7 版迭代实战回放**
- `style-spec.md` - **v1 视觉样式规范**
- `tech-stack.md` - **v1 技术栈规范**
- `three-local-deploy.md` - **v1 Three.js 本地化三种方式**
- `layout-system.md` - v1 布局规则
- `color-themes.md` / `color-refined.md` / `color-analysis.md` - v1 配色
- `🆕 ai-gis-pitfalls.md` - **18 个 AI-GIS 实战踩坑**
- `🆕 security-checklist.md` - **三级等保 7 项覆盖 + token 三层防御**
- `🆕 domestic-deployment.md` - **鲲鹏/飞腾/麒麟/UOS 适配**
- `🆕 mcp-aggregation.md` - **多 server 聚合模式**
- `🆕 sse-streaming.md` - **SSE 实时数据流**
- `🆕 dual-tab-pattern.md` - **大屏 + AI 问答双 Tab 模式**

### templates/ (代码片段)
- `charts.md` - v1 八大图表代码片段
- `🆕 ai-chat.html` - AI 问答界面完整模板
- `🆕 sse-dashboard.html` - SSE 实时数据大屏模板
- `🆕 security-config.py` - FastAPI 安全中间件模板
- `🆕 mcp-server.py` - MCP 多 server 聚合模板

### assets/ (实战素材)
- `js/fit-scale.js` - v1 等比缩放
- `js/marquee.js` - v1 跑马灯
- `js/check.js` - v1 浏览器端自检
- `js/self-check.py` - v1 Playwright 多分辨率自检
- `js/map-mode-switch.js` - v1 2D/3D 地图模式切换
- `🆕 js/ai-chat-client.js` - AI 问答客户端(SSE 流式)
- `🆕 js/dual-tab-controller.js` - 双 Tab 切换控制器

---

## 📦 结果交付(沿用 v1,扩展到 AI 应用)

**硬性规则**:默认是 **PNG 截图**,**不主动 deploy 到公网**。

### 默认行为
- 生成后用 Playwright 截 1920×1080 + 3840×2160 + 1366×768 三张 PNG
- **AI 应用**:再截一张 Tab 2 (AI 问答) 的 PNG,展示对话状态
- 给用户看结果,如果需要调整 → 修改迭代
- **不要主动** deploy 到公网 URL

### deploy 仅以下情况才用
- 用户明确说 "发我个链接" / "我要测试交互" / "给个在线地址"
- 需要跨设备访问(手机看大屏场景)
- 需要长期保存的访问入口

### 交付物清单
- `project.zip` (源码)
- `preview-1920.png` (主截图)
- `preview-3840.png` (高清 200% 缩放)
- `preview-1366.png` (小屏)
- `preview-ai-chat.png` (🆕 AI 问答 tab)
- `README.md` (运行说明)

---

## 🆚 v1 vs v2 对比速查

| 维度 | v1 (2026-07) | v2 (2026-08) |
|---|---|---|
| 应用类型 | 单大屏 | 双 Tab (大屏 + AI 问答) |
| 场景数 | 1 (大屏) | 3 (+ AI 问图 + SSE 实时 + MCP 聚合) |
| 必问问题 | 3 个 | 6 个 |
| 硬性原则 | 6 条 | 9 条 (+ 3 条独有) |
| 踩坑数 | 13 个 (ECharts) | 13 + 18 = 31 个 (+ AI-GIS) |
| 数据源 | 静态 JSON | 静态 + SSE 流 + LLM 工具调用 |
| 部署 | 纯静态 HTML | HTML + FastAPI + Docker + 国产化 |
| 安全 | 无 | 三级等保 7 项 + token 三层防御 |
| 跨平台 | Windows | Windows + Linux + ARM64 + 国产化 |
| 双电脑 | 不涉及 | 完整工作流 + venv 自检 |
| 暗色模式 | 不涉及 | 文字 ≥ slate-200 硬性规则 |

**v2 完全兼容 v1**:大屏场景的所有 v1 模板可直接用,只是多了 AI + 实时流 + 安全的扩展能力。

---

## 已知限制(2026-08)
- LLM 工具调用需后端解析,前端只做"展示"不解析
- SSE 单连接限 6 个 / 浏览器(超出需分页)
- 国产化平台 cryptography 编译需 30-60 秒
- 双 Tab 切换不带记忆,刷新页面回到默认 Tab
- IndexedDB 持久化对话历史**未实现**(v0.4.0 仅内存)
