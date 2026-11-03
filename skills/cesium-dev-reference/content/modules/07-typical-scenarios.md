---
module: 07
title: 典型场景 — 测量、剖面、淹没、轨迹回放、地下模式
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://cesium.com/learn, https://blog.csdn.net/pz890123/article/details/153009796, https://blog.csdn.net/sam99/article/details/154221315]
status: stable
---

# 07 · 典型场景模板

> **本模块覆盖**:测量 / 剖面分析 / 视域分析 / 通视分析 / 淹没模拟 / 轨迹回放 / 地下模式。
> **何时加载**:做某个具体业务场景。详细代码见 `recipes/` 子目录,本模块讲思路与决策。

---

## 7.1 测量(距离 / 面积)

**核心**:拾取点 → `Cartesian3.distance` 累加 / `turf.js` 计算面积。

```js
const positions = []  // 顺序点位
let totalDistance = 0
let totalArea = 0

handler.setInputAction(event => {
  const ray = viewer.camera.getPickRay(event.position)
  const cartesian = viewer.scene.globe.pick(ray, viewer.scene)
  if (!cartesian) return

  positions.push(cartesian)

  if (positions.length >= 2) {
    totalDistance += Cesium.Cartesian3.distance(
      positions[positions.length - 2],
      positions[positions.length - 1]
    )
  }

  // 面积计算(需 turf.js)
  if (positions.length >= 3) {
    const coords = positions.map(p => {
      const carto = Cesium.Ellipsoid.WGS84.cartesianToCartographic(p)
      return [Cesium.Math.toDegrees(carto.longitude), Cesium.Math.toDegrees(carto.latitude)]
    })
    coords.push(coords[0])  // 闭合
    const polygon = turf.polygon([coords])
    totalArea = turf.area(polygon)
  }

  // 实时显示
  document.getElementById('measure-info').innerHTML = `
    距离: ${totalDistance.toFixed(1)} m<br>
    面积: ${totalArea.toFixed(1)} m²
  `
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

**详细实现** → `recipes/measure-distance.md`

---

## 7.2 地形剖面分析(Terrain Profile)

**核心**:沿两点间均匀采样 → `Cesium.sampleTerrainMostDetailed` 获取高程 → 绘制剖面图。

```js
async function drawProfile(start, end, samples = 100) {
  const cartos = []
  for (let i = 0; i <= samples; i++) {
    const t = i / samples
    const lon = Cesium.Math.lerp(start.lon, end.lon, t)
    const lat = Cesium.Math.lerp(start.lat, end.lat, t)
    cartos.push(Cesium.Cartographic.fromDegrees(lon, lat))
  }
  const updated = await Cesium.sampleTerrainMostDetailed(
    viewer.terrainProvider,
    cartos
  )

  const heights = updated.map(c => c.height)
  const distances = updated.map((_, i) => i * totalDistance / samples)

  // 用 ECharts / Chart.js 画剖面
  chart.setOption({
    xAxis: { type: 'category', data: distances },
    yAxis: { type: 'value', name: '海拔(m)' },
    series: [{ type: 'line', data: heights, areaStyle: {} }]
  })

  // 同时画到 3D 场景
  viewer.entities.add({
    polyline: {
      positions: Cesium.Cartesian3.fromDegreesArrayHeights(
        updated.flatMap(c => [
          Cesium.Math.toDegrees(c.longitude),
          Cesium.Math.toDegrees(c.latitude),
          c.height + 50  // 抬高避免被遮挡
        ])
      ),
      width: 2,
      material: Cesium.Color.YELLOW
    }
  })
}
```

**详细实现** → `recipes/terrain-profile.md`

---

## 7.3 视域分析(Viewshed)

**核心**:从观察点向四周发射射线,判断哪些方向可见。

### 两点通视(line-of-sight)

```js
function checkLineOfSight(start, end) {
  const direction = Cesium.Cartesian3.subtract(end, start, new Cesium.Cartesian3())
  const distance = Cesium.Cartesian3.magnitude(direction)
  Cesium.Cartesian3.normalize(direction, direction)

  const ray = new Cesium.Ray(start, direction)
  const hit = viewer.scene.pickFromRay(ray)

  if (Cesium.defined(hit)) {
    const hitDistance = Cesium.Cartesian3.distance(start, hit.position)
    if (hitDistance < distance - 0.1) {
      return { visible: false, blocker: hit }
    }
  }
  return { visible: true }
}
```

> ⚠️ **`scene.globe.depthTestAgainstTerrain = true`** 必须,否则射线穿透山体永远"可见"。

### 区域视域(扇区扫描)

```js
async function viewshedAnalysis(centerPos, maxRadius, ringStep = 50, angleStep = 5) {
  const results = []
  for (let r = ringStep; r <= maxRadius; r += ringStep) {
    for (let a = 0; a < 360; a += angleStep) {
      const azimuth = Cesium.Math.toRadians(a)
      const dx = r * Math.cos(azimuth)
      const dy = r * Math.sin(azimuth)

      // 转 ENU → ECEF
      const carto = Cesium.Cartographic.fromCartesian(centerPos)
      const target = Cesium.Cartesian3.fromRadians(
        carto.longitude + dx / (6378137 * Math.cos(carto.latitude)),
        carto.latitude + dy / 6378137,
        carto.height
      )

      const result = checkLineOfSight(centerPos, target)
      results.push({ angle: a, radius: r, visible: result.visible })
    }
  }

  // 绘制可视扇区
  const visibleSector = results.filter(r => r.visible)
  // ... PolygonHierarchy 构造 + Entity

  // 计算可视率
  const ratio = visibleSector.length / results.length
  console.log(`可视率: ${(ratio * 100).toFixed(1)}%`)
  return ratio
}
```

**详细实现** → `recipes/viewshed-analysis.md`

---

## 7.4 通视分析(Line-of-Sight)

> 与 7.3 的两点通视基本一致,通常指"基站选址 / 瞭望塔点位复核"等单点 A→B 是否可见。

**关键差异**:目标点要抬高(避免目标点本身是塔底/基站底面,被自身挡住)。

```js
function checkLineOfSightWithOffset(start, target, targetHeightOffset = 30) {
  // 抬高目标点(模拟塔顶)
  const carto = Cesium.Cartographic.fromCartesian(target)
  carto.height += targetHeightOffset
  const liftedTarget = Cesium.Cartographic.toCartesian(carto)

  return checkLineOfSight(start, liftedTarget)
}
```

> 📦 详细实现见 `recipes/viewshed-analysis.md`(包含 3D 视线路径绘制)。

---

## 7.5 动态淹没分析(Flood Inundation)

**核心**:CallbackProperty 驱动多边形 `extrudedHeight` 动态变化。

### 第一步:获取地形极值

```js
async function getTerrainExtremum(positions, sampleDensity = 10000) {
  const lonLats = positions.map(c => {
    const carto = Cesium.Ellipsoid.WGS84.cartesianToCartographic(c)
    return [Cesium.Math.toDegrees(carto.longitude), Cesium.Math.toDegrees(carto.latitude)]
  })

  // 用 turf 生成均匀采样点
  const bbox = turf.bbox(turf.polygon([lonLats]))
  const grid = turf.pointGrid(bbox, 0.005, { units: 'degrees' })

  const cartos = grid.features.map(f =>
    Cesium.Cartographic.fromDegrees(f.geometry.coordinates[0], f.geometry.coordinates[1])
  )

  const updated = await Cesium.sampleTerrainMostDetailed(
    viewer.terrainProvider,
    cartos
  )
  const heights = updated.map(c => c.height)

  return {
    min: Math.min(...heights),
    max: Math.max(...heights)
  }
}
```

### 第二步:动态上涨

```js
let currentHeight = minHeight  // 从地形最低点开始
const targetHeight = 100        // 目标水位(米)
const riseSpeed = 0.1           // 米/帧

const floodEntity = viewer.entities.add({
  polygon: {
    hierarchy: new Cesium.PolygonHierarchy(positions),
    extrudedHeight: new Cesium.CallbackProperty((time, result) => {
      currentHeight += riseSpeed
      if (currentHeight > targetHeight) currentHeight = targetHeight
      return currentHeight
    }, false),  // false = 每帧求值
    material: Cesium.Color.BLUE.withAlpha(0.6),
    perPositionHeight: true
  }
})
```

**详细实现** → `recipes/flood-inundation.md`

---

## 7.6 轨迹回放(Trajectory Replay)

**两种实现**:

### 方案 A:CZML(声明式)

```json
[{
  "id": "document",
  "clock": {
    "interval": "2026-09-22T00:00:00Z/2026-09-22T01:00:00Z",
    "currentTime": "2026-09-22T00:00:00Z",
    "multiplier": 60
  }
}, {
  "id": "car-1",
  "availability": "2026-09-22T00:00:00Z/2026-09-22T01:00:00Z",
  "position": {
    "epoch": "2026-09-22T00:00:00Z",
    "cartographicDegrees": [
      0, 116.4, 39.9, 0,
      60, 116.5, 39.9, 0,
      120, 116.6, 39.9, 0
    ]
  },
  "model": { "gltf": "/models/car.glb" }
}]
```

```js
const ds = await Cesium.CzmlDataSource.load(czmlData)
viewer.dataSources.add(ds)
viewer.clock.shouldAnimate = true
```

### 方案 B:SampledPositionProperty(代码构造)

```js
const prop = new Cesium.SampledPositionProperty()
const startTime = Cesium.JulianDate.fromIso8601('2026-09-22T00:00:00Z')
dataPoints.forEach((p, i) => {
  const time = Cesium.JulianDate.addSeconds(startTime, p.t, new Cesium.JulianDate())
  prop.addSample(time, Cesium.Cartesian3.fromDegrees(p.lng, p.lat, p.h))
})

viewer.entities.add({
  position: prop,
  orientation: new Cesium.VelocityOrientationProperty(prop),  // 自动朝向运动方向
  model: { uri: '/models/car.glb', minimumPixelSize: 32 }
})
```

**详细实现** → `recipes/trajectory-replay.md`

---

## 7.7 地下模式(Underground Mode)

**四件套**:

```js
// 1. 允许相机下穿地形
viewer.scene.screenSpaceCameraController.enableCollisionDetection = false

// 2. 地形深度测试(让地下物体被地表正确遮挡)
viewer.scene.globe.depthTestAgainstTerrain = true

// 3. 地下背景色(替代黑色)
viewer.scene.globe.undergroundColor = Cesium.Color.LIGHTSLATEGRAY
viewer.scene.globe.undergroundColorAlphaByDistance = new Cesium.NearFarScalar(
  1000, 0.0,    // 近处透明
  10000, 1.0    // 远处显示
)

// 4. 裁剪平面切剖面
const clippingPlanes = new Cesium.ClippingPlaneCollection({
  planes: [
    new Cesium.ClippingPlane(new Cesium.Cartesian3(1, 0, 0), -700),
    new Cesium.ClippingPlane(new Cesium.Cartesian3(0, 1, 0), -700),
    new Cesium.ClippingPlane(new Cesium.Cartesian3(0, 0, 1), -500)
  ],
  edgeWidth: 1.0,
  edgeColor: Cesium.Color.WHITE
})
viewer.scene.globe.clippingPlanes = clippingPlanes
```

### 半透明地表(看穿地面)

```js
viewer.scene.globe.translucency = {
  enabled: true,
  alpha: 0.3,
  backFaceAlpha: 0.1
}
```

**详细实现** → `recipes/underground-mode.md`

---

## 7.8 倾斜摄影展示

```js
// 加载 OSGB → 3D Tiles 转换后的数据
const tileset = await Cesium.Cesium3DTileset.fromUrl('/tiles/osgb-building/tileset.json', {
  maximumScreenSpaceError: 16,
  skipLevelOfDetail: true,
  cullWithChildrenBounds: true
})
viewer.scene.primitives.add(tileset)

// 单体化拾取
viewer.screenSpaceEventHandler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (picked instanceof Cesium.Cesium3DTileFeature) {
    const name = picked.getProperty('name')
    const height = picked.getProperty('height')
    console.log(`${name}: ${height}m`)
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

---

## 7.9 场景矩阵

| 场景 | 关键 API | 数据规模 | 性能要求 |
|---|---|---|---|
| 距离/面积测量 | `Cartesian3.distance` + `turf.area` | 个位数点 | 低 |
| 地形剖面 | `sampleTerrainMostDetailed` + 图表库 | 100~200 采样 | 中 |
| 两点通视 | `scene.pickFromRay` | 1 次/事件 | 低 |
| 区域视域 | 循环 `pickFromRay` | 1000~5000 次 | 中高 |
| 动态淹没 | `CallbackProperty` + `extrudedHeight` | 1 个多边形 | 中 |
| 轨迹回放 | CZML 或 SampledPositionProperty | 任意 | 视密度 |
| 地下模式 | 4 件套配置 | 全局 | 低 |
| 倾斜摄影 | `Cesium3DTileset` | 全局 | 取决于瓦片 LOD |

---

## 下一步

- 国产替代 → `modules/08-domestic-alternatives.md`
- 避雷清单 → `modules/09-pitfalls-and-traps.md`
- 具体场景 recipes:`recipes/` 目录