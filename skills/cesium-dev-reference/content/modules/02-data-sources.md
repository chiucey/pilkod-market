---
module: 02
title: 数据接入 — 影像、地形、矢量、3D Tiles、glTF、时序
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://cesium.com/docs/tutorials/imagery-layers, https://github.com/CesiumGS/3d-tiles]
status: stable
---

# 02 · 数据接入

> **本模块覆盖**:影像图层 / 地形 / 矢量 / 3D 模型 / 3D Tiles / 时序数据。
> **何时加载**:选影像底图、加载倾斜摄影、加载 BIM、加载点云、加自定义 XYZ 瓦片。

---

## 2.1 影像图层(ImageryLayer)

### 选底图

```js
const viewer = new Cesium.Viewer('cesiumContainer', {
  // 方式 1:构造时指定
  baseLayer: Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(3830183)  // Google 2D Satellite
  ),
  baseLayerPicker: false,
})

// 方式 2:动态添加
viewer.imageryLayers.removeAll()  // 清空默认
const layer = viewer.imageryLayers.addImageryProvider(
  new Cesium.UrlTemplateImageryProvider({
    url: 'https://your-tile-server/{z}/{x}/{y}.png',
    credit: '© Your Tile Source',
    maximumLevel: 18
  })
)
```

### 常见影像 Provider

| Provider | 用途 | URL 示例 |
|---|---|---|
| `UrlTemplateImageryProvider` | 自定义 XYZ | `{z}/{x}/{y}.png` |
| `BingMapsImageryProvider` | Bing Maps(需 key) | 微软 API |
| `ArcGisMapServerImageryProvider` | ArcGIS | esri 服务 |
| `OpenStreetMapImageryProvider` | OSM | tile.openstreetmap.org |
| `IonImageryProvider.fromAssetId(id)` | Cesium ion | 需 accessToken |
| `WebMapServiceImageryProvider` | OGC WMS | 标准 WMS |
| `WebMapTileServiceImageryProvider` | OGC WMTS | 标准 WMTS |

### 国内常用底图(XYZ)

```js
// 天地图(需申请 key)
new Cesium.UrlTemplateImageryProvider({
  url: 'https://t{s}.tianditu.gov.cn/img_w/wmts?layer=img&style=default&tilematrixset=w&Service=WMTS&Request=GetTile&Version=1.0.0&Format=tiles&TileMatrix={z}&TileCol={x}&TileRow={y}&tk={yourKey}',
  subdomains: ['0', '1', '2', '3', '4', '5', '6', '7'],
  maximumLevel: 18
})

// 高德(注意:高德是 GCJ02 坐标,需纠偏!)
new Cesium.UrlTemplateImageryProvider({
  url: 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
  subdomains: ['1', '2', '3', '4']
})
```

> ⚠️ **国内瓦片源坐标系多为 GCJ02**,直接加载会偏移 50-500 米。需要做坐标转换。详见 `modules/09-pitfalls-and-traps.md`。

### 图层控制

```js
viewer.imageryLayers.lower(layer)        // 下移一层
viewer.imageryLayers.raise(layer)        // 上移一层
viewer.imageryLayers.remove(layer)       // 移除
layer.alpha = 0.5                          // 透明度
layer.brightness = 2.0                    // 亮度
layer.contrast = 1.2                       // 对比度
layer.gamma = 0.8                          // 伽马
layer.hue = 0.1                            // 色相
layer.saturation = 0.5                     // 饱和度
```

---

## 2.2 地形(Terrain)

### 默认地形

```js
// Cesium ion 全球地形(需 token)
const viewer = new Cesium.Viewer('cesiumContainer', {
  terrain: Cesium.Terrain.fromWorldTerrain()
})

// 或显式
viewer.scene.setTerrain(
  new Cesium.Terrain(Cesium.CesiumTerrainProvider.fromUrl('https://assets.ion.cesium.com/...')))
```

### 自定义 quantized-mesh 地形

```js
// 用 Cesium Terrain Builder 把 DEM 转 quantized-mesh
// 然后用 CesiumTerrainProvider 加载
const provider = await Cesium.CesiumTerrainProvider.fromUrl('https://your-server/terrain/')
viewer.scene.setTerrain(new Cesium.Terrain(provider))
```

> 🔧 **DEM → quantized-mesh 推荐工具**:[tumgis/ctb-quantized-mesh](https://github.com/tumgis/ctb-quantized-mesh)(Docker 镜像)

### 关闭地形(纯椭球)

```js
viewer.scene.globe.terrainProvider = new Cesium.EllipsoidTerrainProvider()
```

---

## 2.3 矢量数据(Vector)

### GeoJSON

```js
const dataSource = await Cesium.GeoJsonDataSource.load('/path/to/data.geojson', {
  stroke: Cesium.Color.RED,
  fill: Cesium.Color.RED.withAlpha(0.5),
  strokeWidth: 2,
  clampToGround: true  // 贴地
})
viewer.dataSources.add(dataSource)
```

### KML

```js
const kml = await Cesium.KmlDataSource.load('/path/to/file.kml', {
  camera: viewer.camera,
  canvas: viewer.scene.canvas
})
viewer.dataSources.add(kml)
```

### CZML(时序)

```js
const czml = await Cesium.CzmlDataSource.load('/path/to/file.czml')
viewer.dataSources.add(czml)
// CZML 自带时间动画,需要 viewer.clock.shouldAnimate = true
```

> 📦 **CZML 示例**:飞机轨迹、卫星轨道、车辆移动。详见 `recipes/trajectory-replay.md`。

---

## 2.4 glTF / GLB 模型

```js
// 方式 1:Entity(简单)
viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(lng, lat, 0),
  model: {
    uri: '/models/car.glb',
    scale: 1.0,
    minimumPixelSize: 64,        // 最小像素(远距不会消失)
    maximumScale: 20000,         // 最大缩放
    silhouetteColor: Cesium.Color.YELLOW,  // 选中轮廓
    silhouetteSize: 2.0
  }
})

// 方式 2:Model Primitive(更底层,适合大量模型)
const model = await Cesium.Model.fromGltfAsync({
  url: '/models/tree.glb',
  modelMatrix: Cesium.Transforms.headingPitchRollToFixedFrame(
    Cesium.Cartesian3.fromDegrees(lng, lat, 0),
    new Cesium.HeadingPitchRoll(0, 0, 0)
  ),
  scale: 1.0
})
viewer.scene.primitives.add(model)
```

> 📦 **glTF 标准由 Khronos 维护**,所有模型转换工具的输出格式。详见 `references/glossary.md`。

---

## 2.5 3D Tiles(大规模)

### 加载

```js
// 异步加载 + readyPromise
const tileset = await Cesium.Cesium3DTileset.fromUrl(
  '/data/tiles/tileset.json',
  {
    maximumScreenSpaceError: 16,           // LOD 阈值(越大越粗)
    maximumMemoryUsage: 512,                // 显存上限(MB)
    skipLevelOfDetail: true,                // 跳过中间 LOD(性能优化)
    immediatelyLoadDesiredLevelOfDetail: false,
    loadSiblings: false,
    cullWithChildrenBounds: true
  }
)
viewer.scene.primitives.add(tileset)
viewer.flyTo(tileset)

// 加载完成回调
tileset.readyPromise.then(t => {
  console.log('瓦片集加载完成', t.root.boundingSphere)
})
```

### 来源

- **Cesium ion**:全球 OSM Buildings / Google Photorealistic 3D Tiles
- **自建**:用 CesiumLab / py3dtiles / py3dtilers 把数据转成 3D Tiles
- **第三方**:Maxar / Aerometrex / Nearmap 等数据商

### 样式与拾取

```js
// 样式(条件着色)
tileset.style = new Cesium.Cesium3DTileStyle({
  color: 'color("red")',
  show: '${feature["type"]} === "building"',
  pointSize: 5
})

// 单 feature 拾取
viewer.screenSpaceEventHandler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (picked instanceof Cesium.Cesium3DTileFeature) {
    console.log('属性:', picked.getProperty('name'))
    console.log('所有属性:', picked.cesium3DTileFeature.getPropertyNames())
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

### 3D Tiles 1.1 新特性

| 特性 | 用途 |
|---|---|
| **Implicit Tiling** | 大幅减小 tileset.json 体积 |
| **EXT_mesh_features** | 每个 mesh 携带 feature ID |
| **EXT_structural_metadata** | 结构化元数据(分类、属性) |
| **Multi-content tiles** | 一个 tile 含多种内容类型 |

> 详见 `references/glossary.md` 和 [3D Tiles 1.1 规范](https://docs.ogc.org/cs/22-025r4/22-025r4.html)。

---

## 2.6 时序数据

### CZML(推荐)

```js
const czml = [
  {
    id: 'document',
    name: '飞机',
    version: '1.0',
    clock: {
      interval: '2026-09-22T00:00:00Z/2026-09-22T01:00:00Z',
      currentTime: '2026-09-22T00:00:00Z',
      multiplier: 60
    }
  },
  {
    id: 'plane-1',
    availability: '2026-09-22T00:00:00Z/2026-09-22T01:00:00Z',
    position: {
      epoch: '2026-09-22T00:00:00Z',
      cartographicDegrees: [
        0, 116.4, 39.9, 10000,    // t=0秒:北京上空 1 万米
        60, 117.4, 39.9, 10000,   // t=60秒:向东 100km
        120, 118.4, 39.9, 10000
      ]
    },
    model: { gltf: '/models/plane.glb' }
  }
]

Cesium.CzmlDataSource.load(czml).then(ds => viewer.dataSources.add(ds))
```

### SampledProperty(纯 JS 时序)

```js
const prop = new Cesium.SampledPositionProperty()
prop.addSample(Cesium.JulianDate.fromIso8601('2026-09-22T00:00:00Z'),
  Cesium.Cartesian3.fromDegrees(116.4, 39.9, 100))
prop.addSample(Cesium.JulianDate.fromIso8601('2026-09-22T01:00:00Z'),
  Cesium.Cartesian3.fromDegrees(120.4, 39.9, 100))

entity.position = prop  // 自动按当前时间插值
```

> 详见 `recipes/trajectory-replay.md`。

---

## 2.6 MVT 矢量瓦片(Mapbox Vector Tile)

> **MVT 适用版本**(对应本技能 CesiumJS 基线 1.145+):
> - **1.142+**:官方 `MVTDataProvider` 已稳定(2026-06 引入,**新项目首选**)
> - **1.104 ~ 1.141**:用第三方包 `mvt-imagery-provider`(官方未支持前的兼容方案)
> **何时用**:加载建筑轮廓、行政区划、道路网等矢量数据,需要**运行时改样式 + 拾取属性**时,远胜 GeoJSON。
> **数据格式**:`.pbf` / `.mvt`(Protobuf 编码的矢量瓦片,Google Protocol Buffers)

### 三种方案对照

| 方案 | 适用版本 | 渲染方式 | 推荐度 |
|---|---|---|---|
| **官方 `MVTDataProvider`** | 1.145+ | 内部 PBF 解析 + 3D Tiles 渲染 | ⭐⭐⭐ 新项目首选 |
| **`mvt-imagery-provider`(hongfaqiu)** | 1.104+ | 借力 mapbox-gl-js 渲染 | ⭐⭐ 老项目首选 |
| **`cesium-mvt-imagery-provider`(reearth)** | 1.40+ | 轻量自实现 | ⭐ 简单样式场景 |
| ~~`VectorTileImageryProvider`~~ | 1.40~1.104 | 已弃用 | ❌ 不推荐 |

### 方案 A:官方 MVTDataProvider(1.145+ 推荐)

```js
// 1. 创建 MVT 数据源
const provider = await Cesium.MVTDataProvider.fromUrl(
  'https://example.com/tiles/{z}/{x}/{y}.pbf',  // 标准 XYZ URL 模板
  {
    minZoom: 6,                                  // 起始缩放
    maxZoom: 14,                                  // 终止缩放
    extent: Cesium.Rectangle.fromDegrees(5.9, 45.8, 10.5, 47.8)  // 范围(瑞士示例)
  }
)

// 2. 加到场景
viewer.scene.primitives.add(provider)

// 3. 缩放到覆盖范围
await viewer.zoomTo(provider.tileset)
```

> 📦 **官方教程**:[cesium.com/learn/cesiumjs-learn/load-mapbox-vector-tiles-in-cesiumjs](https://cesium.com/learn/cesiumjs-learn/load-mapbox-vector-tiles-in-cesiumjs)

**带 token 的资源**:

```js
const provider = await Cesium.MVTDataProvider.fromUrl(
  new Cesium.Resource({
    url: 'https://example.com/tiles/{z}/{x}/{y}.pbf',
    queryParameters: { api_key: 'your_key' }
  }),
  { minZoom: 6, maxZoom: 14, extent: ... }
)
```

**URL 模板要求**:
- 必须含 `{z}/{x}/{y}` 占位符(Web Mercator XYZ)
- 扩展名不限:`.pbf` / `.mvt` / 无扩展名都可,只要返回 MVT 二进制

### 方案 B:`mvt-imagery-provider`(1.104+ 老项目首选)

```bash
npm install --save mvt-imagery-provider
```

```js
import * as Cesium from 'cesium'
import MVTImageryProvider from 'mvt-imagery-provider'

const viewer = new Cesium.Viewer('cesiumContainer')

// 方式 1:从 style URL 加载(推荐)
const provider = await MVTImageryProvider.fromUrl(
  'https://demotiles.maplibre.org/style.json',  // Mapbox Style Spec
  {
    accessToken: 'your_mapbox_token',  // 私有样式需要
    tileSize: 512,                      // 256 或 512
    maximumLevel: 18,
    minimumLevel: 0,
    enablePickFeatures: true,           // 启用属性拾取
    tilingScheme: new Cesium.WebMercatorTilingScheme()
  }
)
viewer.imageryLayers.addImageryProvider(provider)

// 方式 2:旧 API(1.104+ 已 deprecated)
const provider2 = new MVTImageryProvider({
  style: '/path/to/style.json'
})
provider2.readyPromise.then(() => {
  viewer.imageryLayers.addImageryProvider(provider2)
})
```

> 💡 **优势**:底层用 mapbox-gl-js 渲染,样式丰富(图层混合、表达式等 Mapbox Style Spec 全集)
> ⚠️ **局限**:依赖 mapbox-gl-js,bundle 体积大(~700KB);EPSG:4326 数据暂不支持

### 方案 C:`cesium-mvt-imagery-provider`(1.40+ 轻量)

```bash
npm install cesium-mvt-imagery-provider
```

```js
import CesiumMVTImageryProvider from 'cesium-mvt-imagery-provider'

const provider = new CesiumMVTImageryProvider({
  urlTemplate: 'http://localhost:8080/mvt/{z}/{x}/{y}.mvt',
  layerName: 'buildings',  // 或多个: 'layer1,layer2'
  style: feature => ({
    fillStyle: '#4FC3F7',
    strokeStyle: '#0288D1',
    lineWidth: 1
  }),
  onSelectFeature: feature => console.log('clicked:', feature),
  credit: 'MVT Data'
})

const layer = viewer.imageryLayers.addImageryProvider(provider)
layer.alpha = 0.5  // 透明度可调
```

> ✅ **优势**:轻量、API 简单、可自定义渲染
> ⚠️ **局限**:样式表达能力弱(只能简单填色和描边)

### 完整示例:加载建筑 MVT

```js
// 1. 加载底图(影像)
const imageryProvider = await Cesium.IonImageryProvider.fromAssetId(2)
viewer.imageryLayers.addImageryProvider(imageryProvider)

// 2. 加载 MVT(建筑矢量)
const mvtProvider = await Cesium.MVTDataProvider.fromUrl(
  'https://tiles.example.com/buildings/{z}/{x}/{y}.pbf',
  {
    minZoom: 12,
    maxZoom: 18,
    extent: Cesium.Rectangle.fromDegrees(116.30, 39.85, 116.50, 40.05)
  }
)
viewer.scene.primitives.add(mvtProvider)

// 3. 拾取属性
viewer.screenSpaceEventHandler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (picked && picked.content && picked.content.tile) {
    // 通过 tile 获取 feature
    console.log('Tile content:', picked.content.tile)
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

### 自建 MVT 服务(GeoJSON → MVT)

```bash
# 1. 用 tippecanoe 生成 .mbtiles
tippecanoe -o buildings.mbtiles -z 14 -Z 10 buildings.geojson \
  --read-parallel --no-tile-size-limit

# 2. 提取 .pbf 到 z/x/y 目录
mb-util --image_format=pbf buildings.mbtiles ./tiles

# 3. Nginx 服务 ./tiles + CORS(必加!)
location /tiles/ {
  add_header 'Access-Control-Allow-Origin' '*';
  alias /var/www/mvt-data/;
}
```

> 📦 **推荐工具**:[tippecanoe](https://github.com/felt/tippecanoe) · [mb-util](https://github.com/mapbox/mbutil)

### 关键点

- ⚠️ MVT 坐标系默认 **EPSG:3857**(Web Mercator),不支持 4326(除非用 cesium-mvt-imagery-provider 的特殊配置)
- ⚠️ 服务端必须配 **CORS**,否则浏览器拒绝跨域加载 PBF
- ⚠️ layer 名称必须与 PBF 内的图层名严格一致(大小写敏感)
- ⚠️ 用 `ogrinfo -so your.mbtiles` 检查 MBTiles 内图层名(踩坑常见原因)
- ✅ MVT 比 GeoJSON 小 90%+(分块 + 二进制压缩)
- ✅ 运行时改样式不需要重新生成数据

### 常见坑

| 现象 | 原因 | 解决 |
|---|---|---|
| 瓦片加载 404 | CORS 没配 | Nginx 加 `Access-Control-Allow-Origin` |
| 加载了但一片空白 | layer 名称错误 | 用 `ogrinfo -so` 查实际图层名 |
| 样式不生效 | style 字段名拼错 | 参考 Mapbox Style Spec 字段名 |
| 1.40~1.103 找不到 MVTDataProvider | 该版本未内置 | 用第三方包 `mvt-imagery-provider` |
| 1.145 以下不能用 `MVTDataProvider` | 该版本未引入 | 用第三方包 |

> 📦 **详细实现**:[recipes/load-mvt.md](../recipes/load-mvt.md)

---

## 2.7 选择指南

| 数据类型 | 推荐格式 | 加载 API |
|---|---|---|
| 全球卫星影像 | Cesium ion Bing / Google | `IonImageryProvider.fromAssetId(id)` |
| 自定义切片 | XYZ | `UrlTemplateImageryProvider` |
| 标准地图服务 | WMS / WMTS | `WebMapServiceImageryProvider` |
| 全球地形 | Cesium ion World Terrain | `Terrain.fromWorldTerrain()` |
| 自定义 DEM | quantized-mesh | `CesiumTerrainProvider.fromUrl` |
| 矢量(省/市界) | GeoJSON | `GeoJsonDataSource.load` |
| 时序(航班/卫星) | CZML | `CzmlDataSource.load` |
| 单模型(车/树) | glTF/GLB | `Entity.model` / `Model.fromGltfAsync` |
| 大规模倾斜摄影 | 3D Tiles | `Cesium3DTileset.fromUrl` |
| 点云(LiDAR) | 3D Tiles (pnts) / Potree | `Cesium3DTileset.fromUrl` |
| BIM(建筑) | glTF → 3D Tiles | `Cesium3DTileset.fromUrl` |

---

## 下一步

- API 速查 → `modules/03-core-api-cheatsheet.md`
- 性能优化 → `modules/05-performance-and-rendering.md`
- 典型场景 → `modules/07-typical-scenarios.md`
- 数据转换工具 → `modules/08-domestic-alternatives.md`(CesiumLab/py3dtiles)