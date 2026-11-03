---
module: ref-glossary
title: Cesium 术语表
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# Cesium 术语表(Glossary)

> 中英对照 + 简释。版式:`英文(中文) — 简释`

## 基础概念

- **Cesium** — CesiumGS 公司开发的三维地理空间可视化引擎家族(CesiumJS + Cesium ion + Cesium Native)。
- **CesiumJS** — Apache 2.0 开源的 JavaScript 3D 地球库,浏览器中运行。
- **Cesium ion** — CesiumGS(现属 Bentley)的云平台,处理 + 托管 3D Tiles。
- **Cesium Native** — 底层 C++ 库,支撑 Cesium for Unreal / Unity / Omniverse。

## 数据 / 格式

- **3D Tiles** — OGC 社区标准,大规模异构 3D 地理空间数据流式传输格式。
- **3D Tiles 1.0** — 2018-12 通过,基于 b3dm/i3dm/pnts/cmpt 四种瓦片格式。
- **3D Tiles 1.1** — 2022-12 通过,**隐式平铺 + 结构化元数据 + 直接 glTF 内容**,原四种格式被弃用。
- **3D Tiles 2.0** — 开发中。
- **b3dm** — Batched 3D Model,1.0 时代的批量 3D 模型瓦片(建筑物)。
- **i3dm** — Instanced 3D Model,1.0 时代的实例化 3D 模型(灯杆/树)。
- **pnts** — Point Cloud,点云瓦片。
- **cmpt** — Composite,复合瓦片(可打包多个 b3dm/i3dm/pnts)。
- **glTF** — Khronos 的运行时 3D 模型格式(JSON 或二进制 .glb)。
- **KTX2** — GPU 压缩纹理格式,Cesium 推荐用于 3D Tiles 纹理。
- **Draco** — Google 的几何压缩算法,3D Tiles 1.0 默认开启。
- **quantized-mesh** — Cesium 的高程瓦片格式(三角形网格,流式)。
- **CZML** — Cesium Language,JSON 子集,描述时间动态场景。
- **KML** — Keyhole Markup Language,Google Earth 时代的矢量格式。
- **GeoJSON** — 通用地理矢量 JSON 格式。
- **MVT** — Mapbox Vector Tile,矢量瓦片格式(`.pbf`/`.mvt`)。Google Protocol Buffers 编码,EPSG:3857(Web Mercator)坐标系。支持运行时改样式 + 拾取属性。在 CesiumJS 中三种加载方式:1.40~1.104 的 `VectorTileImageryProvider`(已弃用) / 1.104+ 的 `mvt-imagery-provider` 第三方包 / 1.145+ 的官方 `MVTDataProvider`。
- **PBF** — Protocol Buffers 二进制格式,MVT 的实际编码格式。
- **tippecanoe** — Mapbox 官方推荐的 MVT 生成工具,把 GeoJSON 转 `.mbtiles` / MVT。
- **MBTiles** — SQLite 单文件瓦片容器格式,内含 MVT 元数据 + 缩略图。

## 坐标 / 几何

- **WGS84** — World Geodetic System 1984,GPS 用的全球大地坐标系。
- **ECEF** — Earth-Centered Earth-Fixed,地心地固坐标系,Cesium 内部计算用。
- **Cartesian3** — Cesium 的 3D 笛卡尔坐标类(x, y, z 米)。
- **Cartesian2** — 屏幕坐标类(x, y 像素)。
- **Cartesian4** — 4 维坐标,主要用于矩阵变换。
- **Cartographic** — 地理坐标类(longitude/latitude/height,弧度)。
- **ENU** — East-North-Up,局部切平面坐标系(东/北/上)。
- **ECI** — Earth-Centered Inertial,用于卫星轨道计算(与 ECEF 区别:不随地球自转)。
- **ITRF** — International Terrestrial Reference Frame,高精度的全球参考框架(毫米级)。
- **Heading-Pitch-Roll (HPR)** — 偏航/俯仰/翻滚,物体姿态描述。
- **Ellipsoid** — 椭球体,Cesium 默认 WGS84 椭球(长半轴 6378137 m)。

## 渲染 / 性能

- **LOD** — Level of Detail,根据视距动态切换细节层级。
- **Frustum Culling** — 视锥剔除,视野外的物体不渲染。
- **DistanceDisplayCondition** — 距离显示条件,远近阈值控制可见性。
- **screenSpaceError** — 屏幕空间误差,3D Tiles LOD 切换阈值(默认 2)。
- **maximumScreenSpaceError** — 最大屏幕空间误差,越小越精细,越大越流畅。
- **Instancing** — GPU 实例化,单次 draw call 绘制多个相同物体。
- **DrawCall** — 一次绘制调用,衡量渲染开销的核心指标。
- **BatchedMesh** — 批量网格,1.109+ 引入的高性能点/线/面渲染。
- **Primitive** — Cesium 底层渲染对象。
- **Entity** — Cesium 高层封装,内置 Property / 时间 / 事件。
- **requestRenderMode** — 按需渲染(默认 false 持续渲染,true 后只在场景变化时渲染)。
- **WebGL** — 浏览器 3D 渲染 API,CesiumJS 基于此(支持 WebGL 2)。
- **WebGPU** — WebGL 继任者,Cesium 实验性支持(Scene.useWebGPU)。
- **Draco Compression** — 几何压缩,3D Tiles 默认开启。
- **Meshopt** — 现代 GPU 友好压缩,3D Tiles 1.1 选项。

## 3D Tiles 关键概念

- **tileset.json** — 3D Tiles 入口清单,描述瓦片金字塔。
- **tileset** — 一组有空间索引的瓦片集合。
- **tile** — 单个瓦片,含 boundingVolume + content URI。
- **bounding volume** — 包围体,Cesium 用于视锥剔除。
- **geometricError** — 几何误差,用于 LOD 决策。
- **refinement** — 精化策略(Replacement / Additive)。
- **implicit tiling** — 隐式平铺(1.1),tileset.json 不再列举每个瓦片。
- **EXT_mesh_features** — glTF 扩展,给 mesh 携带要素 ID。
- **EXT_structural_metadata** — glTF 扩展,结构化元数据(1.1 强依赖)。

## 分析 / 交互

- **Pick** — 拾取,屏幕坐标 → 命中对象。
- **drillPick** — 穿透拾取,返回所有命中(而非最先命中)。
- **pickFromRay** — 沿射线拾取,常用于通视分析。
- **ScreenSpaceEventHandler** — 屏幕事件处理器(鼠标/触摸)。
- **CallbackProperty** — 回调函数驱动的动态属性(每帧求值)。
- **SampledProperty** — 时序采样属性(按 JulianDate 索引)。
- **time-dynamic** — 时间动态,数据随时间变化(飞机/卫星)。
- **viewshed** — 视域,从某点观察可见的区域。
- **line-of-sight** — 通视,两点之间是否可见。
- **flood inundation** — 洪水淹没分析。
- **terrain profile** — 地形剖面。

## 工程 / 构建

- **CESIUM_BASE_URL** — Cesium 静态资源根 URL(Vite/Webpack 必须设置)。
- **copy-webpack-plugin** — Webpack 拷贝 Cesium 静态资源。
- **vite-plugin-cesium / unplugin-cesium** — Vite/多打包器通用插件。
- **viewer.destroy()** — 销毁 Viewer(防 WebGL 上下文泄漏)。
- **HMR** — Hot Module Replacement,热重载。
- **Tree shaking** — 摇树,Cesium 支持 ES module 按需引入。
- **CDN** — Content Delivery Network,Cesium 可从 CDN 加载。

## 业务领域

- **CIM** — City Information Modeling,城市信息模型。
- **数字孪生(Digital Twin)** — 物理实体的数字镜像。
- **倾斜摄影(Photogrammetry)** — 无人机多角度拍摄重建 3D 模型。
- **BIM** — Building Information Modeling,建筑信息模型(IFC / Revit)。
- **点云(Point Cloud)** — LiDAR / 摄影测量产生的三维点集合。
- **智慧城市(Smart City)** — 城市运行管理的数字化。
- **GIS** — Geographic Information System,地理信息系统。

## Unity / Unreal 集成

- **Cesium for Unity** — CesiumGS 官方 Unity 插件,基线 v1.24.0(2026-07-01),内置 cesium-native v0.62.0。Apache 2.0 商用免费。
- **Cesium for Unreal** — CesiumGS 官方 Unreal Engine 插件,基线 v2.28.0(2026-07-01),走 v2.x 编号,**不存在 v0.29**。同样内置 cesium-native v0.62.0。
- **Cesium for Omniverse** — NVIDIA Omniverse 集成,v0.29.0(2026-07-01)。常被误称为"Cesium for Unreal v0.29",实为另一产品。
- **cesium-native** — C++ 核心库,Unity / Unreal / Omniverse 三个产品共用,负责 3D Tiles 解码 / glTF 加载 / 几何处理 / 异步任务。v0.62.0 是 Unity v1.24.0 + Unreal v2.28.0 同期发布的版本。
- **CesiumGeoreference** — Unity 中定义场景"地理坐标原点"的组件,所有 3D Tiles / 物体相对它定位。
- **CesiumGlobeAnchor** — Unity 中把 GameObject 锚定到地球表面指定经纬高的组件。
- **ACesiumGeoreference** — Unreal 中地理参考 Actor(命名约定:Actor 前缀 A)。
- **UCesiumGlobeAnchorComponent** — Unreal 中物体锚定 Component(命名约定:Component 前缀 U)。
- **ACesium3DTileset** — Unreal 中加载 3D Tiles 的 Actor。
- **Cesium3DTileset** — Unity 中加载 3D Tiles 的 Component。
- **RasterOverlay** — 栅格图层(影像 / 地形),叠加在 3D Tiles 上(Bing / Google / ion / WMS / WMTS / 自定义 XYZ)。
- **EXT_mesh_features** — glTF 扩展,3D Tiles 1.1 起用于 feature ID 标识。
- **EXT_structural_metadata** — glTF 扩展,3D Tiles 1.1 起用于结构化元数据(Unreal v2.0+ 全面支持)。

---

## 国产封装(国内常见)

- **Mars3D** — 火星科技基于 Cesium 的三维可视化平台。
- **DC-SDK** — 数字视觉基于 Cesium 的封装。
- **SuperMap iClient3D** — 超图三维 WebGL/WebGPU 客户端。
- **Earth SDK** — 西部世界的双引擎(Web + UE)SDK。
- **CesiumLab** — 国产 3D Tiles 转换平台(闭源)。
- **S3M** — 超图提出的三维瓦片格式,与 3D Tiles 可互转。
- **I3S** — Esri 提出的三维瓦片格式,CesiumJS 1.106+ 支持。

## 公司 / 组织

- **Cesium GS, Inc.** — 原 Cesium 公司,2024-09 被 Bentley 收购。
- **Bentley Systems** — 基础设施工程软件公司,2024-09 收购 Cesium。
- **AGI** — Analytical Graphics, Inc.,Cesium 最初由其开源。
- **OGC** — Open Geospatial Consortium,3D Tiles 标准的官方维护方。
- **Khronos Group** — glTF / WebGL / WebGPU 标准制定方。

---

**版本**:对应 CesiumJS 1.124+ / 3D Tiles 1.1 / Bentley 收购后

**引用来源**:综合自 cesium.com/learn/glossary、3D Tiles 规范、各国产封装官方文档。详见 `references/official-sites.md`。