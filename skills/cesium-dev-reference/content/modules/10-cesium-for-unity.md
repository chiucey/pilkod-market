---
module: 10
title: Cesium for Unity v1.24.0 — Unity 集成 3D Tiles / 全球地理
cesium_version: N/A (独立 SDK,基线 v1.24.0)
last_verified: 2026-09-22
source_url: [https://cesium.com/learn/cesium-unity/ref-doc/changes.html, https://github.com/CesiumGS/cesium-unity]
status: stable
---

# 10 · Cesium for Unity v1.24.0

> **本模块覆盖**:Cesium for Unity SDK 的安装、核心组件、数据加载、典型场景、与 CesiumJS 协同。
> **何时加载**:Unity 项目需要全球地理、3D Tiles、Cesium ion 资源集成。
> **基线版本**:**v1.24.0**(2026-07-01),最新 v1.25.1(2026-09-01),内置 cesium-native v0.62.0。

---

## 10.1 Cesium for Unity 是什么?

Cesium for Unity 是 CesiumGS 官方提供的 Unity 插件,把 **3D 地理空间能力** 带入 Unity 游戏引擎:

- ✅ 真实 WGS84 全球地球(精确比例)
- ✅ 3D Tiles 加载与渲染(倾斜摄影 / 建筑 / BIM / 点云)
- ✅ Cesium ion 资源集成(全球地形 / 影像 / OSM Buildings / Google Photorealistic 3D Tiles)
- ✅ 物理引擎集成(Unreal Physics / 碰撞 / 角色交互)
- ✅ 时间动态数据
- ✅ Unity URP / 内置渲染管线双支持

**典型场景**:数字孪生、AEC 建筑可视化、智慧城市、游戏化 GIS、无人机巡检可视化、训练模拟器。

**License**:Apache 2.0(免费商用)。

---

## 10.2 安装与项目初始化

### 支持的平台

| 平台 | 支持 |
|---|---|
| Windows (x86-64) | ✅ |
| macOS (x86-64 / Apple Silicon) | ✅ |
| Android (ARM64 / x86-64) | ✅ |
| iOS | ✅ |
| Universal Windows Platform (ARM64 / x86-64) | ✅ |
| Web | ✅ (Unity 6+ 实验性) |
| Linux (x86-64) | ✅ (v1.25.0+) |

### 三种安装方式

#### 方式 A:Unity Package Manager(推荐)

1. 打开 Unity Hub → Open 项目
2. `Window > Package Manager`
3. 点 `+` → `Add package from git URL`
4. 输入 `https://github.com/CesiumGS/cesium-unity.git#v1.24.0`
5. 等待导入完成

#### 方式 B:Unity Asset Store

[Unity Asset Store: Cesium for Unity](https://assetstore.unity.com/packages/2d/textures-materials/cesium-for-unity-251636)

#### 方式 C:GitHub Release ZIP

下载 [v1.24.0 release](https://github.com/CesiumGS/cesium-unity/releases) → 解压到项目 `Packages/` 目录。

### Cesium ion Token 设置

`Edit > Project Settings > Cesium` → 填入 Cesium ion access token(从 [ion.cesium.com](https://ion.cesium.com/) 获取)。

---

## 10.3 核心组件(蓝图 / Component)

### 10.3.1 `CesiumGeoreference`(地理参考)

场景中的"地理坐标原点"。所有 3D Tiles / 实体都相对它定位。

```csharp
// 创建方式:GameObject → Add Component → CesiumGeoreference
// 关键属性:
- longitude / latitude / height: 地球上的锚点经纬高(默认 0,0,0 大西洋)
- scale: 地球整体缩放(默认 1.0)
- ellipsoid: 椭球模型(默认 WGS84)

// C# 代码设置:
var geoRef = GetComponent<CesiumGeoreference>();
geoRef.latitude = 39.9;
geoRef.longitude = 116.4;
geoRef.height = 50.0;
```

### 10.3.2 `Cesium3DTileset`(3D Tiles 加载)

```csharp
// 添加方式:GameObject → 3D Object → Cesium → 3D Tile From URL / Asset
// 或者代码:
var tilesetGO = new GameObject("MyBuilding");
var tileset = tilesetGO.AddComponent<Cesium3DTileset>();

// 从 URL 加载
tileset.url = "https://your-server/tiles/tileset.json";

// 从 Cesium ion Asset ID 加载
tileset.fromIon = true;
tileset.ionAssetID = 9617;  // 例如 Bing Maps Aerial

// 关键属性:
- url: 瓦片集 URL
- maximumScreenSpaceError: LOD 阈值(默认 2)
- maximumMemoryUsage: 显存上限 MB
- cullWithChildrenBounds: 子节点剔除
- preloadSiblings: 预加载兄弟节点
- enableCollision: 是否参与物理碰撞
```

### 10.3.3 `CesiumCameraController`(相机控制)

```csharp
// 替换默认 CameraController 以获得地球感知控制
var cam = Camera.main;
var controller = cam.gameObject.AddComponent<CesiumCameraController>();

// 控制相机移动:
controller.transform.position = ...;  // 相对地球原点的 Unity 坐标
```

> 💡 CesiumCameraController 在地球上下平移时自动调整经纬高。

### 10.3.4 `CesiumGlobeAnchor`(物体锚定)

把 Unity GameObject 锚定到地球表面指定经纬高。

```csharp
var anchor = myGameObject.AddComponent<CesiumGlobeAnchor>();
anchor.longitude = 116.4;
anchor.latitude = 39.9;
anchor.height = 100.0;

// 移动 Unity 物体 → 自动同步经纬高
myGameObject.transform.position = new Vector3(0, 100, 0);  // 仍锚定原经纬高
```

### 10.3.5 `CesiumRasterOverlay`(栅格图层)

叠加在 3D Tiles / 地形上的影像:

```csharp
// 现有类型:
- CesiumIonRasterOverlay: Cesium ion 资源
- BingMapsRasterOverlay: Bing Maps
- BingMapsAerial / BingMapsRoads
- CesiumGoogleMapTilesRasterOverlay(v1.19.0+): Google Maps
- CesiumAzureMapsRasterOverlay(v1.19.0+): Azure Maps
- UrlTemplateRasterOverlay: 自定义 XYZ 瓦片
- TileMapServiceRasterOverlay: TMS 标准
- WebMapServiceRasterOverlay: OGC WMS
- WebMapTileServiceRasterOverlay: OGC WMTS
```

```csharp
// 添加到 3D Tileset
var overlay = tilesetGO.AddComponent<CesiumIonRasterOverlay>();
overlay.ionAssetID = 2;  // Bing Maps Aerial
overlay.alpha = 0.8;
```

### 10.3.6 `CesiumGeoJsonDocument` / `CesiumGeoJsonDocumentRasterOverlay`(v1.23.0+)

把 GeoJSON 栅格化叠加在 3D Tiles 上:

```csharp
var geoJson = tilesetGO.AddComponent<CesiumGeoJsonDocumentRasterOverlay>();
geoJson.geoJson = LoadGeoJsonFromFile("buildings.geojson");
geoJson.style = new CesiumVectorStyle {
  fillColor = new Color(0.31f, 0.76f, 0.97f, 0.6f),
  lineColor = new Color(0.01f, 0.53f, 0.82f, 1.0f)
};
```

### 10.3.7 `CesiumIonTokenTroubleshootingWindow`(v1.21.0+)

UI 弹窗诊断 token 过期 / 配额问题。

---

## 10.4 CesiumNative 简介

Cesium for Unity / Unreal / Omniverse 都基于同一个 C++ 核心库 **cesium-native**。

| 项 | v1.24.0 内置 |
|---|---|
| **cesium-native 版本** | **v0.62.0** |
| 上游 | [github.com/CesiumGS/cesium-native](https://github.com/CesiumGS/cesium-native) |
| 用途 | 3D Tiles 解码 / glTF 加载 / 几何处理 / 异步任务 |
| License | Apache 2.0 |

Unity / Unreal / Omniverse 三个产品**共用同一个 cesium-native 版本**更新节奏。所以:
- v1.24.0 (Unity) + v2.28.0 (Unreal) + v0.29.0 (Omniverse) **都内置 cesium-native v0.62.0**
- 解码性能 / 修复一致

---

## 10.5 关键工作流

### 10.5.1 从 Cesium ion 加载 Bing 影像 + 全球地形

```
Step 1: Cesium ion token 填入 Project Settings
Step 2: GameObject → 3D Object → Cesium → World Terrain + Bing Imagery
        (Cesium World Terrain 是 Cesium ion 的全球 quantized-mesh 地形服务)
Step 3: Play → 看到地球
```

### 10.5.2 加载自定义 3D Tiles(自托管)

```
Step 1: GameObject → 3D Object → Cesium → Blank 3D Tiles Tileset
Step 2: Inspector → Cesium3DTileset URL → 填入 https://your-server/tiles/tileset.json
Step 3: 调整 maximumScreenSpaceError (默认 2,大规模调 8-16)
Step 4: 加载 CesiumIonRasterOverlay 或 BingMapsAerial 作为底图
```

### 10.5.3 实时从 GPS 设备更新 CesiumGlobeAnchor

```csharp
// 在 Update() 中:
var anchor = playerGO.GetComponent<CesiumGlobeAnchor>();
anchor.longitude = gpsDevice.longitude;
anchor.latitude = gpsDevice.latitude;
anchor.height = gpsDevice.altitude;
```

### 10.5.4 添加交互式 3D 物体(锚定在地面)

```csharp
// 1. 创建 3D 物体 (Cube)
var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);

// 2. 添加 CesiumGlobeAnchor
var anchor = cube.AddComponent<CesiumGlobeAnchor>();
anchor.longitude = 116.4;
anchor.latitude = 39.9;
anchor.height = 0;

// 3. cube 自动跟随地球,移动 Unity 坐标不影响经纬高
```

---

## 10.6 Cesium for Unity v1.24.0 vs 最新版(v1.25.1)

| 版本 | 日期 | 关键变更 |
|---|---|---|
| **v1.24.0**(基线) | 2026-07-01 | glTF 线图元渲染支持;cesium-native v0.61.0 → v0.62.0 |
| v1.24.1+ | 2026-08+ | Linux x86-64 平台支持;Unity 6.5 编译支持 |
| v1.25.0 | 2026-08-03 | Linux 平台 + Unity 6.5;cesium-native v0.62.0 → v0.63.0 |
| v1.25.1 | 2026-09-01 | GeoJSON Point 样式支持;cesium-native v0.63.0 → v0.64.0 |

> ✅ v1.24.0 适合生产项目;v1.25.x 有新功能但需要更新的 Unity 6.5+ 支持。

---

## 10.7 与 CesiumJS 协同

| 场景 | 推荐工具 |
|---|---|
| Web 端快速预览 | CesiumJS(浏览器打开) |
| Unity 项目集成 | Cesium for Unity |
| 跨平台分发(Web + 桌面 / 移动) | CesiumJS + 共享 3D Tiles 资源 |
| 高保真渲染(UE5) | Cesium for Unreal(见 `modules/11`) |
| NVIDIA Omniverse 集成 | Cesium for Omniverse |

**共享资源**:
- 同一个 3D Tileset URL 三个产品都能用
- Cesium ion asset ID 通用
- 坐标系 WGS84 一致,无转换

---

## 10.8 性能优化

### 显存

```csharp
// 在 Cesium3DTileset Inspector:
- maximumMemoryUsage: 默认 256 MB(大规模场景调 512-1024)
- skipLevelOfDetail: 启用
- preloadSiblings: 关闭(节省内存)
- loadSiblings: 关闭
```

### CPU

- 用 `Cesium3DTileset.cullWithChildrenBounds = true`
- 关闭 `preloadAncestors`(不必要的预加载)
- 使用 LOD 驱动的 object pooling(默认开启)

### 物理碰撞

```csharp
// 启用 Mesh collider(性能开销大,按需)
tileset.enableCollision = true;
// 复杂场景考虑用简化 collision mesh
```

---

## 10.9 已知坑

| 现象 | 原因 | 解决 |
|---|---|---|
| Play 后地球黑屏 | Cesium ion token 未设或失效 | Project Settings → Cesium → Token |
| 3D Tiles 不显示 | URL 不可达 / CORS | Nginx 加 CORS 头 |
| 物体浮在地面以上 | CesiumGlobeAnchor.height 设错 | 用 0 表示地面 |
| Linux 启动崩溃 | 老版本不支持 Linux | 升级到 v1.25.0+ |
| Web 平台部分功能不可用 | Web 是 v1.20.0+ 实验性 | 桌面端调试 |
| iOS 链接错误 | iOS 库关联错 | 升级到 v1.20.0+ |

---

## 10.10 进一步阅读

- [Cesium for Unity Quickstart](https://cesium.com/learn/cesium-unity)
- [Cesium for Unity Change Log](https://cesium.com/learn/cesium-unity/ref-doc/changes.html)
- [Cesium for Unity Tutorials](https://cesium.com/learn/cesium-unity)
- [GitHub: CesiumGS/cesium-unity](https://github.com/CesiumGS/cesium-unity)
- [cesium-native 仓库](https://github.com/CesiumGS/cesium-native)
- [Cesium for Unreal 章节](./11-cesium-for-unreal.md)

---

## 下一步

- Unreal 项目集成 → `modules/11-cesium-for-unreal.md`
- CesiumJS Web 端 → `modules/01-foundation.md`
- 国产封装 → `modules/08-domestic-alternatives.md`