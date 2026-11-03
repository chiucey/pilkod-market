---
module: 08
title: 国产封装与替代 — mars3d、dc-sdk、SuperMap、CesiumLab、py3dtiles
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://mars3d.cn, https://github.com/marsgis/mars3d, https://github.com/SuperMap/iClient3D-for-WebGL]
status: stable
---

# 08 · 国产封装与替代

> **本模块覆盖**:基于 Cesium 的国产二次封装 / 数据转换工具 / 选型决策。
> **何时加载**:选框架 / 比较 mars3d vs 原生 / 看数据转换工具链。

---

## 8.1 主流国产封装对照

| 维度 | CesiumJS 原生 | mars3d | DC-SDK | SuperMap iClient3D | Earth SDK |
|---|---|---|---|---|---|
| **底层** | CesiumJS | CesiumJS | CesiumJS | 自主 WebGL/WebGPU | 自有 + UE |
| **语言/封装** | JS 库 | Vue 3 组件 + 插件 | 集成库 | 完整 SDK | 双引擎 |
| **生态** | 国际 | 国内主流 | 国内 | 政务/信创主流 | 双平台 |
| **上手成本** | 高(陡学习曲线) | 中(Vue 友好) | 中 | 中(商业文档) | 中 |
| **覆盖功能** | 通用 | 智慧城市、数字孪生 | 三维场景工具 | 全栈 GIS | 双引擎可视化 |
| **是否闭源** | ❌ Apache 2.0 | ✅ 核心开源,完整版付费 | ✅ 开源 | ❌ 闭源 | 部分开源 |
| **中文文档** | ⚠️ 半中半英 | ✅ 完善 | ✅ 完善 | ✅ 完善 | ✅ |
| **生产案例** | 大量 | 大量(智慧城市) | 中等 | 政务/水利/国土 | 仿真 |

---

## 8.2 mars3d(火星科技)

### 定位
国内最主流的 Cesium 二次封装,Vue 3 生态友好,提供大量现成示例和模板。

### 适用场景
- 智慧城市 / 园区 / 数字孪生
- 智慧园区 / 智慧工地 / 智慧水利
- 需要快速搭建项目的中小团队
- 中文社区为主

### 上手

```bash
npm install mars3d
# 或
npm install mars3d mars3d-cesium
```

```vue
<template>
  <mars-map :url="configUrl" map-key="your-key" />
</template>

<script setup>
import { ref } from 'vue'
const configUrl = '/config/map-config.json'
</script>
```

### 与超图融合

```bash
npm install mars3d mars3d-supermap
```

```js
import 'mars3d-supermap'
// 自动加载 S3M 格式
```

### 优势
- ✅ 大量现成示例(250+ 场景)
- ✅ Vue 3 组件化,符合国内前端主流
- ✅ 国内生态完善(QQ 群、文档、视频)
- ✅ 智慧城市相关功能封装好

### 局限
- ❌ 深度定制需要绕过封装层
- ❌ 完整功能付费
- ❌ 部分修改 Mars3D 的 Cesium 后,与原生 Cesium 兼容性变差

参考:[mars3d.cn](http://mars3d.cn/) | [github.com/marsgis/mars3d](https://github.com/marsgis/mars3d)

---

## 8.3 DC-SDK(数字视觉)

### 定位
集成 Turf、Heatmap、ECharts 等常用可视化库,提供 250+ 开发示例。

### 适用场景
- 二三维一体化项目
- 需要集成 ECharts 可视化
- 数据驱动型项目

### 特点
- 基于 CesiumJS 二次封装
- 内置 Turf.js(几何运算)、ECharts(图表)、Heatmap.js(热力图)
- 250+ 开源示例

### 局限
- 社区规模小于 mars3d
- 主要维护者是数字视觉公司一家

参考:[dvgis.github.io/dc-sdk](http://dvgis.github.io/dc-sdk)

---

## 8.4 SuperMap iClient3D(超图)

### 定位
超图软件的三维 Web GIS 客户端,**两条路线**:
1. **iClient3D for Cesium** — 基于 CesiumJS 扩展,支持 S3M 国产瓦片
2. **iClient3D for WebGL/WebGPU** — 自研 WebGL 引擎,**不依赖 Cesium**

### 适用场景
- 政务 / 国土 / 水利 / 住建 / 交通
- 信创 / 国产化要求
- 需要 S3M 格式(超图自家格式)
- 已有超图 iServer / iDesktopX 数据

### 关键差异

| 项 | iClient3D for Cesium | iClient3D for WebGL/WebGPU |
|---|---|---|
| 底层 | CesiumJS + S3M 插件 | 自主 WebGL 引擎 |
| 数据格式 | S3M + 3D Tiles | S3M 为主 |
| 推荐度 | 老项目过渡 | **新项目首选**(超图官方推荐) |

### S3M vs 3D Tiles

| 维度 | S3M | 3D Tiles |
|---|---|---|
| 提出方 | 超图 | CesiumGS / OGC |
| 标准化 | 国内行业标准 | OGC 国际标准 |
| 数据更新 | 支持**局部更新** | 整体重发 |
| 文件大小 | 较小 | 较大 |
| 渲染性能 | 高 | 中 |

> 🔧 **S3M ↔ 3D Tiles 互转工具**:超图开源提供。

参考:[github.com/SuperMap](https://github.com/SuperMap/iClient3D-for-WebGL)

---

## 8.5 Earth SDK(西部世界)

### 定位
**双引擎** SDK:Web 前端 + Unreal Engine 5。一套代码两端跑。

### 适用场景
- Web + UE 同时部署
- 数字孪生 + 仿真
- 需要 UE 高保真渲染

### 特点
- 支持 Web + UE5 双端
- 数字孪生生态完整
- 前端友好

### 局限
- UE 部分对硬件要求高
- 学习曲线较陡

---

## 8.6 数据转换工具链

### CesiumLab(国产闭源)

**最强桌面转换工具**,闭源免费 + 部分高级功能付费。

**支持格式**:
- 影像 → 瓦片
- 地形 → 切片
- OSGB → 3D Tiles(倾斜摄影)
- BIM → 3D Tiles
- OBJ/FBX → 3D Tiles
- 点云 → 3D Tiles

**优势**:
- ✅ 拖拽式操作
- ✅ 自带 HTTP 分发服务
- ✅ 处理大工程倾斜摄影稳定

**局限**:
- ❌ 闭源
- ❌ 部分高级功能(压缩、轻量化)付费

参考:[cesiumlab.com](https://www.cesiumlab.com/)

### 开源替代方案

| 工具 | 范围 | 优势 | 局限 |
|---|---|---|---|
| **py3dtiles** | 点云 / LAS/LAZ | Python 生态,最活跃 | 偏点云 |
| **py3dtilers** | OBJ / GeoJSON / IFC / CityGML | 来源 3DCityDB | 复杂依赖 |
| **v3dtiles** | OSGB / Shapefile / GDB / FBX | 接近 CesiumLab,带 WebGUI | 中等成熟度 |
| **Obj2Tiles** | OBJ → 3D Tiles | 轻量,OpenDroneMap 维护 | 仅 OBJ |
| **objTo3d-tiles** | OBJ → 3D Tiles | 纯 JS | 仅 OBJ |

参考:[github.com/CesiumGS/3d-tiles/blob/main/RESOURCES.md](https://github.com/CesiumGS/3d-tiles/blob/main/RESOURCES.md)

---

## 8.7 选型决策树

```
你要做什么?
│
├─ 海外项目 / 国际化 / 标准要求严格
│  └─ 选 CesiumJS 原生
│
├─ 国内政务 / 信创 / 国土 / 水利
│  └─ SuperMap iClient3D(首选 WebGL/WebGPU,数据已有超图生态选 for Cesium)
│
├─ 智慧城市 / 数字孪生 / 园区 / 快速交付
│  └─ mars3d(中文社区、组件化、模板多)
│
├─ 二三维一体化 + 大量 ECharts 可视化集成
│  └─ DC-SDK
│
├─ Web + UE 双端 / 数字孪生 + 高保真
│  └─ Earth SDK
│
├─ 大型 BIM / 倾斜摄影处理 + 自行托管 3D Tiles
│  └─ CesiumJS 原生 + CesiumLab/py3dtiles
│
├─ 想要"什么都能干"的统一方案
│  └─ 重新审视:这种需求通常需要多个框架组合,不存在银弹
│
└─ 学术科研 / 实验项目
   └─ CesiumJS 原生(灵活度最大)
```

---

## 8.8 转换工具选型

```
数据格式 → 目标格式
│
├─ OSGB(倾斜摄影) → 3D Tiles
│  ├─ 大工程 + 不在乎闭源 → CesiumLab
│  └─ 开源 → v3dtiles
│
├─ LAS/LAZ(点云) → 3D Tiles
│  ├─ 大数据 + 性能要求 → py3dtiles(多核并行)
│  └─ 轻量 → Obj2Tiles 类
│
├─ BIM(IFC/Revit) → 3D Tiles
│  ├─ IFC → py3dtilers
│  └─ Revit → Cesium ion(上传自动转换)
│
├─ OBJ/FBX → 3D Tiles
│  ├─ OBJ → Obj2Tiles
│  └─ FBX → py3dtilers 或 v3dtiles
│
└─ GeoJSON → 3D Tiles
   └─ py3dtilers
```

---

## 8.9 Bentley 收购后的考量

2024-09-06 Bentley Systems 收购 CesiumGS。**对开发者的影响**:

| 维度 | 现状 | 趋势 |
|---|---|---|
| CesiumJS 开源 | ✅ Apache 2.0(承诺不变) | 持续开源 |
| Cesium ion 价格 | 按需付费 | 商业化运作 |
| 3D Tiles 标准 | OGC 社区标准 | OGC 标准强化 |
| 与 iTwin 整合 | 进行中 | 数字孪生方向更紧 |

**结论**:CesiumJS 本身仍可放心用;Cesium ion 商业化程度会提升;如果项目对数据敏感(国内),可考虑自建 3D Tiles 服务 + CesiumJS 原生。

参考:[bentley.com/news](https://www.bentley.com/news/bentley-systems-acquires-3d-geospatial-company-cesium/)

---

## 进一步阅读

- [osgeo 中文分会:轻量 Web 架构三维 GIS 平台](https://osgeo.cn/post/1c67f)
- [超腾开源:三维 GIS 开发工具清单](https://www.hylab.cn/blog/detail/7502279144022085632)
- [5 个超强大的 3D 地球开发框架](https://www.mvrlink.com/5-super-powerful-3d-earth-development-frameworks)

## 下一步

- 避雷清单 → `modules/09-pitfalls-and-traps.md`
- 数据接入 → `modules/02-data-sources.md`