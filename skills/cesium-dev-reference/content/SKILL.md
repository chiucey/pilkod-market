---
name: cesium-dev-reference
title: Cesium 综合技能参考大全
version: 1.3.2
cesium_baseline: 1.145+ (CesiumJS · 主线 · 2026-09-02 release)
cesium_for_unity_baseline: 1.24.0 (Cesium for Unity · 当前 stable)
cesium_for_unreal_baseline: 2.28.0 (Cesium for Unreal · UE 5.5 最后支持版本)
last_verified: 2026-09-22
status: stable
audience: 前端 / GIS / Unity / Unreal 工程师
---

# Cesium 综合技能参考大全 — SKILL.md(主入口)

## 角色定位

本技能是 **Cesium 三维地理空间开发的"技术参考文档"**,不是开发规范。

- ✅ 用于:在做 GIS / 数字孪生 / 智慧城市 / 倾斜摄影 / 通视分析等需求时,**按模块加载、按章节对照、按 recipes 复用**。
- ❌ 不用于:把本技能当作硬规范,严格照搬开发。实际开发需结合项目版本、业务、硬件自行调整。

## ⚠️ 使用边界(必读)

**本技能是"参考",不是"死规则"**。Mavis 加载本技能后,还要做综合判断,不是直接照搬。

### 边界 1 — 版本可能过期
- 本技能记录的版本基线(当前 CesiumJS `1.145+`)是该技能**最近一次核验**的版本,实际写代码前请用 `web_search` 查当前 latest release
- 月度 cron 会自动跑版本对齐,但**当前会话写代码时,以网上最新为准**
- 例:某 API 在 1.145 改名 / 弃用 → 本技能可能没及时更新 → 写代码前要查最新文档

### 边界 2 — API 可能变化
- CesiumJS 活跃迭代中,minor 版本常引入新 API(如 1.142 引入 `MVTDataProvider`,1.145 引入 `ClippingPolygon` holes 支持)
- 本技能**记录的是核验时点的 API**,实际开发时可能已经变
- 例:1.141 时代推荐用 `mvt-imagery-provider` 第三方包,1.142+ 官方 `MVTDataProvider` 已稳定 → 优先用官方

### 边界 3 — 综合知识 + 网上资料 > 技能记录
- Mavis 自己的综合知识(`knowledge cutoff 2026-01`) + `web_search` 实时结果 + 技能记录 = 综合判断
- 技能没记录的(新特性 / 新坑 / 新社区方案),要靠综合知识 + 网上资料补
- 技能记录错的(罕见但有),要以网上最新为准

### 标准做法(Mavis 加载技能后的工作流)
1. **加载技能** → 选对应 modules + recipes(获得结构化框架)
2. **`web_search` 验证** → 查当前 latest 版本 + 关键 API 是否变动 + 是否有更新的社区方案
3. **综合判断** → 技能 + 网上 + 综合知识,挑最优
4. **写代码时标注来源** → 引用某 API 时写明"截至 [日期] 来自 [cesium.com / npm / GitHub]"

---

## 何时调用本技能

| 场景 | 应该加载的模块 |
|---|---|
| 第一次接触 Cesium,要了解基础 | `modules/01-foundation.md` + `architecture.md` |
| 要做视域分析 / 通视 / 剖面 / 淹没 | `modules/07-typical-scenarios.md` + 对应 `recipes/` |
| 加载 3D Tiles / 影像 / 地形 / glTF 出问题 | `modules/02-data-sources.md` + `modules/09-pitfalls-and-traps.md` |
| 加载 MVT 矢量瓦片(Mapbox Vector Tile) | `modules/02-data-sources.md` § MVT + `recipes/load-mvt.md` |
| Unity 项目集成 3D Tiles / 全球地理 | `modules/10-cesium-for-unity.md` |
| Unreal 项目集成 3D Tiles / 全球地理 | `modules/11-cesium-for-unreal.md` |
| 场景卡顿、内存爆掉 | `modules/05-performance-and-rendering.md` |
| Vue / React 项目集成 | `modules/06-engineering.md` |
| 选框架:Cesium 原生 vs mars3d vs dc-sdk vs SuperMap | `modules/08-domestic-alternatives.md` |
| 对照 API 速查 | `references/api-quick-ref.md` |
| 看不懂术语 | `references/glossary.md` |
| Cesium 升版本 / 模块过期了 | `self-evolution/changelog.md` |
| 想加新模块 | `self-evolution/extension-contract.md` |
| 要补完版本追踪 | `self-evolution/maintenance-playbook.md` |

## 能力清单(模块索引)

### 核心架构与基础
- `architecture.md` — Cesium 技术体系 8 层架构图(Mermaid)
- `modules/01-foundation.md` — 地球、相机、坐标系、时间、场景、渲染管线

### 数据接入
- `modules/02-data-sources.md` — 影像 / 地形 / 矢量 / **MVT** / 3D Tiles / glTF / 时序
- `modules/03-core-api-cheatsheet.md` — 核心 API 速查表(含 **MVT API**)

### 应用层
- `modules/04-interaction-and-viz.md` — 拾取 / 标注 / 测量 / 分析 / 特效
- `modules/05-performance-and-rendering.md` — LOD / Frustum / Instancing / Pick 优化 / GPU 调优
- `modules/06-engineering.md` — Vite/Webpack / TypeScript / Vue/React / SSR / 微前端 / 部署
- `modules/07-typical-scenarios.md` — 测量 / 剖面 / 视域 / 淹没 / 轨迹回放 / 地下模式

### 生态
- `modules/08-domestic-alternatives.md` — mars3d / dc-sdk / SuperMap iClient3D / CesiumLab / py3dtiles
- `modules/09-pitfalls-and-traps.md` — CORS / 坐标系混用 / token 失效 / 性能瓶颈 / 内存泄漏
- `modules/10-cesium-for-unity.md` — **Cesium for Unity v1.24.0**(核心组件 + RasterOverlay + 场景)
- `modules/11-cesium-for-unreal.md` — **Cesium for Unreal v2.28.0**(核心组件 + UE 版本兼容矩阵)

### Recipes(可直接复用的代码片段)
- `recipes/measure-distance.md` — 距离 / 面积测量
- `recipes/terrain-profile.md` — 地形剖面分析
- `recipes/viewshed-analysis.md` — 视域分析(两点 + 区域)
- `recipes/flood-inundation.md` — 动态洪水淹没模拟
- `recipes/trajectory-replay.md` — 轨迹回放(车辆/航班)
- `recipes/underground-mode.md` — 地下模式四件套
- `recipes/custom-3dtiles.md` — 自定义 3D Tiles 服务
- `recipes/ion-token-rotation.md` — Cesium ion token 轮换 + 国内替代
- `recipes/load-mvt.md` — **MVT 矢量瓦片加载(1.40+ / 1.104+ / 1.145+ 三方案)**

### 自扩展机制(self-evolution/)⭐ 必装
- `changelog.md` — 变更日志(Cesium 升版本时 diff)
- `coverage-gap-detector.md` — 缺口识别(过期/缺失/错误时怎么办)
- `extension-contract.md` — 模块挂载规范(frontmatter + status)
- `maintenance-playbook.md` — 维护者手册(月度/季度任务)

### References
- `references/official-sites.md` — 15+ 权威站点清单
- `references/api-quick-ref.md` — 关键 API 一句话索引
- `references/glossary.md` — 术语表

## 三个调用示例

### 示例 1:我要做视域分析
→ 加载 `modules/07-typical-scenarios.md` + `recipes/viewshed-analysis.md`  
→ 关键 API:`Cesium.sampleTerrainMostDetailed` / `Cesium.Ray` / `scene.pickFromRay` / `CallbackProperty`

### 示例 2:Cesium 升级到 1.124 后 Entity 渲染变慢
→ 加载 `modules/05-performance-and-rendering.md` + `modules/09-pitfalls-and-traps.md` + `self-evolution/changelog.md`  
→ 检查:`PrimitiveCollection` 是否替换 `Entity`、`BillboardCollection` 替代 Entity.billboard

### 示例 3:对比 mars3d 和原生 Cesium 的取舍
→ 加载 `modules/08-domestic-alternatives.md`  
→ 决策维度:中文生态 / 现成组件 / 定制深度 / 长期维护 / 数据合规

## 自扩展机制摘要(详见 `self-evolution/`)

| 机制 | 作用 | 文件 |
|---|---|---|
| **版本字段** | 维护 cesium 官方基线,每个模块注明对应版本 | `SKILL.md` frontmatter |
| **缺口识别** | 超出当前覆盖时,提示并给出再查入口 | `self-evolution/coverage-gap-detector.md` |
| **模块挂载契约** | 新模块按统一 frontmatter 写入,否则加载告警 | `self-evolution/extension-contract.md` |
| **维护者手册** | 月度/季度抓 release notes + Sandcastle 新示例 | `self-evolution/maintenance-playbook.md` |

## 约束与禁止

- ❌ 不许把本技能当硬规范照搬
- ❌ 不许把"未来版本计划"写进 stable 模块
- ❌ 不许省略 self-evolution 四个机制中的任何一个
- ❌ 不许编造 API、参数、版本号;凡引用必须可追溯到 `references/official-sites.md` 的权威链接
- ❌ 不许把国产封装贬低或吹捧;按事实陈述差异
- ✅ 允许按需修改具体代码片段以适配业务
- ✅ 鼓励按 `extension-contract.md` 添加新模块

## 维护者

本技能遵循 `self-evolution/maintenance-playbook.md` 中的周期任务清单。每季度抓一次 Cesium release notes、每月检查一次 Sandcastle 新示例,并更新 `references/official-sites.md`。

如发现过期内容、缺失模块、错误引用,按 `coverage-gap-detector.md` 流程补齐。