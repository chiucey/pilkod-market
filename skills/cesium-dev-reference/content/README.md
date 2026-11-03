---
module: root-readme
title: 项目总览
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# Cesium 综合技能参考大全

> 给前端 / GIS / Web3D 工程师的一份 Cesium 速查参考,不是开发规范。

## 这是什么

一份**按需查阅**的 Cesium 技术参考文档,涵盖:

- 8 层架构 + **11** 个核心模块(含 Unity/Unreal 集成)
- **9** 个可直接复用的代码片段(recipes)
- 4 个自扩展机制(self-evolution)
- 3 个速查手册(references)

## 不是什么

- ❌ 不是 Cesium 教程(那是 [cesium.com/learn](https://cesium.com/learn) 的事)
- ❌ 不是 API 文档(那是 [cesium.com/learn/cesiumjs/ref-doc](https://cesium.com/learn/cesiumjs/ref-doc) 的事)
- ❌ 不是某个项目的实现代码
- ❌ 不保证能直接拷贝运行(版本/环境差异需自行调整)

## 怎么用

```
打开 SKILL.md
   ↓
按"何时调用本技能"表格选模块
   ↓
模块 + recipes 双加载
   ↓
复制片段,改字段,跑起来
   ↓
踩坑 → 查 modules/09-pitfalls-and-traps.md
```

## 目录速览

```
cesium-dev-reference/
├── SKILL.md                          ← 主入口(从这开始)
├── README.md                         ← 本文件
├── architecture.md                   ← 8 层架构图(Mermaid)
├── modules/
│   ├── 01-foundation.md              ← 基础概念
│   ├── 02-data-sources.md            ← 数据接入(含 MVT)
│   ├── 03-core-api-cheatsheet.md     ← API 速查
│   ├── 04-interaction-and-viz.md     ← 交互与可视化
│   ├── 05-performance-and-rendering.md
│   ├── 06-engineering.md             ← 工程化
│   ├── 07-typical-scenarios.md       ← 典型场景
│   ├── 08-domestic-alternatives.md   ← 国产封装对比
│   ├── 09-pitfalls-and-traps.md      ← 避雷
│   ├── 10-cesium-for-unity.md        ← Cesium for Unity v1.24.0
│   └── 11-cesium-for-unreal.md       ← Cesium for Unreal v2.28.0
├── recipes/                          ← 可复用代码片段
│   ├── measure-distance.md
│   ├── terrain-profile.md
│   ├── viewshed-analysis.md
│   ├── flood-inundation.md
│   ├── trajectory-replay.md
│   ├── underground-mode.md
│   ├── custom-3dtiles.md
│   ├── ion-token-rotation.md
│   └── load-mvt.md                   ← MVT 矢量瓦片加载
├── self-evolution/                   ← 自扩展机制⭐
│   ├── changelog.md
│   ├── coverage-gap-detector.md
│   ├── extension-contract.md
│   └── maintenance-playbook.md
├── references/
│   ├── official-sites.md             ← 15+ 权威站点
│   ├── api-quick-ref.md              ← API 一句话索引
│   └── glossary.md                   ← 术语表
├── scripts/                          ← 自检脚本(自动化)
│   ├── health-check.sh               ← 一键 QC
│   ├── check-baseline.sh             ← 版本对齐检测
│   ├── check-coverage.sh             ← 缺口自检
│   ├── check-links.sh                ← 链接存活检测
│   ├── release-diff.sh               ← release notes 抓取
│   └── install.sh                    ← 一键初始化
└── .github/workflows/                ← CI 自动化(推到 GitHub 激活)
    ├── weekly-health.yml             ← 周跑基础 QC
    ├── monthly-links.yml             ← 月跑链接检查
    └── quarterly-baseline.yml        ← 季跑版本对齐
```

## ⚠️ 使用边界(必读)

**本技能是"参考",不是"死规则"** — 用户 2026-09-22 明确指示。

| 维度 | 边界说明 |
|---|---|
| **版本基线** | 记录的版本是该技能**最近一次核验**的版本;写代码前请用 `web_search` 查当前 latest release |
| **API** | CesiumJS 活跃迭代,minor 版本常引入/弃用 API(如 1.142 引入 `MVTDataProvider`);以网上最新文档为准 |
| **综合判断** | Mavis 综合知识 + `web_search` 实时结果 + 技能记录 = 综合判断;技能没记录的也要补 |

**Mavis 标准做法**:加载技能 → 选 modules + recipes → `web_search` 验证当前 latest → 综合判断 → 写代码。

---

## 版本基线

| 项 | 值 | 来源 |
|---|---|---|
| CesiumJS | **1.145+**(2026-09-02 release,2026-09-22 核验) | [cesium.com/blog/2026/09/02/cesium-releases-in-september-2026](https://cesium.com/blog/2026/09/02/cesium-releases-in-september-2026) |
| Cesium for Unity | **v1.24.0**(2026-07-01) | [cesium.com/learn/cesium-unity/ref-doc/changes](https://cesium.com/learn/cesium-unity/ref-doc/changes.html) |
| Cesium for Unreal | **v2.28.0**(2026-07-01) | [cesium.com/learn/cesium-unreal](https://cesium.com/learn/cesium-unreal/ref-doc) |
| Cesium for Omniverse | v0.29.0(2026-07-01) | [cesium.com/learn/omniverse](https://cesium.com/learn/omniverse/) |
| 3D Tiles | **1.1**(OGC Community Standard, 2022-12 通过) | [docs.ogc.org/cs/22-025r4](https://docs.ogc.org/cs/22-025r4/22-025r4.html) |
| MVT 矢量瓦片 | **1.142+ 官方**(`MVTDataProvider`)/ 1.104+ 兼容(第三方包) | [cesium.com/blog/2026/09/02/cesium-releases-in-september-2026](https://cesium.com/blog/2026/09/02/cesium-releases-in-september-2026) |
| Cesium ion | 与 CesiumJS 1.145+ 匹配 | [cesium.com/ion](https://cesium.com/ion) |
| Cesium 所有权 | **Bentley Systems**(2024-09-06 收购) | [bentley.com/news](https://www.bentley.com/news/bentley-systems-acquires-3d-geospatial-company-cesium/) |
| CesiumJS License | **Apache 2.0** | 永久开源(收购后承诺不变) |

> ⚠️ **MVT 推荐基线**:**1.142+** 起官方有 `Cesium.MVTDataProvider`(性能 / 集成更优,优于第三方 `mvt-imagery-provider`);仅当项目必须停在 1.142 之前时,才用第三方包。
> ⚠️ **Cesium for Unreal 版本号**:用户原话 "v.29" 经核实为 **笔误** — Cesium for Unreal 走 v2.x 编号,目前最新是 v2.28.0;v0.29.0 是 Cesium for Omniverse(同期)。本技能以 v2.28.0 为基线。
> ⚠️ **本表版本号是该技能最近核验时点的版本**,Mavis 在新会话写代码前,应 `web_search` 再查一次当前 latest。

## 维护与扩展

详见 `self-evolution/`。一句话:**模块挂载看 extension-contract,缺口补齐看 coverage-gap-detector,周期任务看 maintenance-playbook**。

## License & 免责声明

- 本参考文档以 CC BY-NC-SA 4.0 发布,代码片段以 MIT 发布
- 引用的官方文档、博客内容归原作者所有,链接见 `references/official-sites.md`
- 不构成任何形式的技术保证;请按官方文档为准
- "Cesium"、"3D Tiles"、"Cesium ion" 是 Cesium GS, Inc.(Bentley Systems 子公司)的商标