---
recipe: load-mvt
title: MVT 矢量瓦片加载(三方案对照)
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# MVT 矢量瓦片加载

> **何时用**:加载建筑轮廓、行政区划、道路网等矢量数据,需要**运行时改样式 + 拾取属性**时。
> **数据格式**:`.pbf` / `.mvt`(Google Protocol Buffers 编码矢量瓦片)
> **对应版本**:1.40+ / 1.104+ / 1.145+(三套方案)

---

## 一、方案速选

| 你的情况 | 推荐方案 |
|---|---|
| 新项目 / CesiumJS ≥ 1.145 | **官方 `MVTDataProvider`** |
| 老项目 / CesiumJS ≥ 1.104 / 需要丰富样式 | **`mvt-imagery-provider`** 第三方包 |
| 老项目 / CesiumJS 1.40~1.104 / 简单样式 | **`cesium-mvt-imagery-provider`** 第三方包 |
| CesiumJS < 1.40 | 不可用,升级 Cesium |

---

## 二、方案 A:官方 `MVTDataProvider`(1.145+)

> **教程**:[cesium.com/learn/cesiumjs-learn/load-mapbox-vector-tiles-in-cesiumjs](https://cesium.com/learn/cesiumjs-learn/load-mapbox-vector-tiles-in-cesiumjs)

### 最小可用

```js
import * as Cesium from 'cesium'

Cesium.Ion.defaultAccessToken = 'your_token'

const viewer = new Cesium.Viewer('cesiumContainer', {
  terrain: Cesium.Terrain.fromWorldTerrain()
})

// 1. 加载 MVT
const provider = await Cesium.MVTDataProvider.fromUrl(
  'https://example.com/tiles/{z}/{x}/{y}.pbf',
  {
    minZoom: 6,
    maxZoom: 14,
    extent: Cesium.Rectangle.fromDegrees(5.9, 45.8, 10.5, 47.8)  // 瑞士
  }
)

// 2. 加到场景
viewer.scene.primitives.add(provider)

// 3. 缩放到覆盖范围
await viewer.zoomTo(provider.tileset)
```

### 带 token 的资源

```js
const provider = await Cesium.MVTDataProvider.fromUrl(
  new Cesium.Resource({
    url: 'https://example.com/tiles/{z}/{x}/{y}.pbf',
    queryParameters: { api_key: 'your_key' }
  }),
  { minZoom: 6, maxZoom: 14, extent: ... }
)
```

### URL 要求

- 模板必须含 `{z}`、`{x}`、`{y}` 三个占位符(Web Mercator XYZ)
- 扩展名不限:`.pbf` / `.mvt` / 无扩展名均可,只要返回 MVT 二进制

### 拾取属性

```js
viewer.screenSpaceEventHandler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (Cesium.defined(picked)) {
    // MVT feature 通过 Cesium3DTileFeature 暴露
    if (picked instanceof Cesium.Cesium3DTileFeature) {
      console.log('Feature ID:', picked.featureId)
      // 用 propertyNames + getProperty 读取属性
      console.log('属性:', picked.getProperty('name'))
    }
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

> 💡 `MVTDataProvider` 内部走的是 3D Tiles 渲染管线,所以拾取返回 `Cesium3DTileFeature`。

---

## 三、方案 B:`mvt-imagery-provider`(1.104+,最常用)

> **仓库**:[github.com/hongfaqiu/MVTImageryProvider](https://github.com/hongfaqiu/MVTImageryProvider)

### 安装

```bash
npm install --save mvt-imagery-provider
```

### 加载(推荐 fromUrl)

```js
import * as Cesium from 'cesium'
import MVTImageryProvider from 'mvt-imagery-provider'

const viewer = new Cesium.Viewer('cesiumContainer')

const provider = await MVTImageryProvider.fromUrl(
  'https://demotiles.maplibre.org/style.json',  // Mapbox Style Spec
  {
    accessToken: 'your_mapbox_token',
    tileSize: 512,                      // 256 或 512
    maximumLevel: 18,
    minimumLevel: 0,
    enablePickFeatures: true,           // 启用属性拾取
    tilingScheme: new Cesium.WebMercatorTilingScheme()
  }
)
viewer.imageryLayers.addImageryProvider(provider)
```

### 旧 API(1.104+ 已 deprecated)

```js
const provider = new MVTImageryProvider({
  style: '/path/to/style.json'
})
provider.readyPromise.then(() => {
  viewer.imageryLayers.addImageryProvider(provider)
})
```

### 自定义 style.json

```json
{
  "version": 8,
  "sources": {
    "my-buildings": {
      "type": "vector",
      "tiles": ["https://tiles.example.com/buildings/{z}/{x}/{y}.pbf"],
      "maxzoom": 18,
      "minzoom": 10
    }
  },
  "layers": [
    {
      "id": "buildings-fill",
      "type": "fill",
      "source": "my-buildings",
      "source-layer": "buildings",
      "paint": {
        "fill-color": "#4FC3F7",
        "fill-opacity": 0.6
      }
    },
    {
      "id": "buildings-line",
      "type": "line",
      "source": "my-buildings",
      "source-layer": "buildings",
      "paint": {
        "line-color": "#0288D1",
        "line-width": 1
      }
    }
  ]
}
```

### 拾取属性

```js
viewer.screenSpaceEventHandler.setInputAction(async event => {
  const picked = viewer.scene.pick(event.position)
  if (Cesium.defined(picked)) {
    console.log('Picked:', picked)
  }
  // 或用 provider.pickFeatures
  const features = await provider.pickFeatures(
    event.position.x, event.position.y,
    14, lng, lat  // zoom, lon, lat
  )
  console.log('Features:', features)
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

### 优点 vs 局限

- ✅ **样式丰富**:完整 Mapbox Style Spec(图层混合、表达式、icon-font 等)
- ✅ 拾取功能完善(`pickFeatures` API)
- ❌ bundle 体积大(依赖 mapbox-gl-js,~700KB)
- ❌ 不支持 EPSG:4326 数据

---

## 四、方案 C:`cesium-mvt-imagery-provider`(1.40+ 轻量)

> **仓库**:[github.com/reearth/cesium-mvt-imagery-provider](https://github.com/reearth/cesium-mvt-imagery-provider)

### 安装

```bash
npm install cesium cesium-mvt-imagery-provider
```

### 加载

```js
import CesiumMVTImageryProvider from 'cesium-mvt-imagery-provider'

const imageryProvider = new CesiumMVTImageryProvider({
  urlTemplate: 'http://localhost:8080/mvt/{z}/{x}/{y}.mvt',
  layerName: 'buildings',  // 单个图层名,多个用逗号: 'layer1,layer2'
  style: feature => ({
    fillStyle: '#4FC3F7',
    strokeStyle: '#0288D1',
    lineWidth: 1
  }),
  onSelectFeature: feature => {
    console.log('选中 feature:', feature)
  },
  credit: 'MVT Buildings Data'
})

const layer = viewer.imageryLayers.addImageryProvider(imageryProvider)
layer.alpha = 0.5  // 可调透明度
```

### 优点 vs 局限

- ✅ 轻量(自实现 PBF 解析,无 mapbox-gl-js 依赖)
- ✅ API 简单
- ❌ 样式表达力弱(只能 fill / stroke / lineWidth)

---

## 五、自建 MVT 服务(GeoJSON → MVT)

### 1. 准备数据

```bash
# 安装 tippecanoe(MVT 生成器)
# macOS
brew install tippecanoe
# Linux
git clone https://github.com/felt/tippecanoe.git && cd tippecanoe && make -j
```

### 2. GeoJSON → MBTiles

```bash
tippecanoe \
  --output buildings.mbtiles \
  --minimum-zoom 10 \
  --maximum-zoom 14 \
  --base-zoom 14 \
  --read-parallel \
  --no-tile-size-limit \
  --layer buildings \
  buildings.geojson
```

### 3. MBTiles → z/x/y 目录

```bash
# 安装 mb-util
git clone https://github.com/mapbox/mbutil.git && cd mbutil && pip install -r requirements.txt

# 提取
mb-util --image_format=pbf buildings.mbtiles ./tiles

# 输出:
# tiles/10/163/395.pbf
# tiles/10/163/396.pbf
# ...
```

### 4. Nginx 服务(必须 CORS)

```nginx
server {
  listen 80;
  
  location /mvt-tiles/ {
    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
    alias /var/www/mvt-data/;
    
    location ~* \.pbf$ {
      expires 7d;
      add_header Cache-Control "public";
    }
  }
}
```

> ⚠️ **CORS 是 MVT 加载失败的 #1 原因**——浏览器拒绝跨域加载 PBF 必然导致白屏。

---

## 六、关键检查清单

加载 MVT 失败时,按以下顺序排查:

- [ ] **CORS**:浏览器 Network 面板检查 `Access-Control-Allow-Origin` 响应头
- [ ] **layer 名**:用 `ogrinfo -so buildings.mbtiles` 查 MBTiles 内实际图层名
- [ ] **坐标系**:MVT 默认 EPSG:3857(Web Mercator),确认 source 数据已投影
- [ ] **URL 模板**:含 `{z}` `{x}` `{y}` 三占位符
- [ ] **服务可达**:浏览器直接打开 `https://server/{z}/{x}/{y}.pbf` 能下载到二进制
- [ ] **Content-Type**:服务端返回 `application/x-protobuf` 或 `application/octet-stream`
- [ ] **CESIUM_BASE_URL**:Cesium 静态资源 404 也会影响 PBF 解析 worker 加载
- [ ] **版本兼容**:1.40~1.104 没有 `MVTDataProvider`,需用第三方包

---

## 七、决策树

```
你的 CesiumJS 版本是?
│
├─ 1.145+ → MVTDataProvider(官方)
│            │
│            └─ 需要丰富 Mapbox Style? → 1.104+ 也可叠加 mvt-imagery-provider
│
├─ 1.104~1.144 → mvt-imagery-provider(首选)
│                  │
│                  └─ 仅需简单 fill/stroke? → cesium-mvt-imagery-provider(更轻量)
│
├─ 1.40~1.103 → cesium-mvt-imagery-provider(轻量方案)
│                │
│                └─ 需要完整 Mapbox Style? → 升级 Cesium 到 1.104+
│
└─ < 1.40 → 升级 Cesium(MVT 不可用)
```

---

## 八、性能

| 数据规模 | 推荐方案 | 备注 |
|---|---|---|
| < 1000 features | 任意方案 | 差异不大 |
| 1000 ~ 100k | `mvt-imagery-provider` | mapbox-gl-js 优化好 |
| > 100k | 官方 `MVTDataProvider`(1.145+) | 内部用 3D Tiles 管线,极致 LOD |
| 全球数据 | 官方 + 分区域加载 | 用 `extent` 限制范围 |

---

## 九、参考

- [CesiumJS 官方教程: Load Mapbox Vector Tiles](https://cesium.com/learn/cesiumjs-learn/load-mapbox-vector-tiles-in-cesiumjs)
- [hongfaqiu/MVTImageryProvider](https://github.com/hongfaqiu/MVTImageryProvider) — 主流第三方包
- [reearth/cesium-mvt-imagery-provider](https://github.com/reearth/cesium-mvt-imagery-provider) — 轻量第三方
- [felt/tippecanoe](https://github.com/felt/tippecanoe) — MVT 生成器
- [mapbox/mbutil](https://github.com/mapbox/mbutil) — MBTiles 解压
- [Mapbox Style Spec v0.43](https://mapbox.com/mapbox-gl-js/style-spec) — style.json 规范