---
recipe: underground-mode
title: 地下模式四件套
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 地下模式(Underground Mode)

> **何时用**:地下管线、地质勘探、隧道工程、地下空间可视化。

## 四件套配置

```js
// 第 1 件:关碰撞检测,允许相机下穿地形
viewer.scene.screenSpaceCameraController.enableCollisionDetection = false

// 第 2 件:开地形深度测试,让地下物体被地表正确遮挡
viewer.scene.globe.depthTestAgainstTerrain = true

// 第 3 件:设地下背景色(避免穿透后一片黑)
viewer.scene.globe.undergroundColor = Cesium.Color.fromCssColorString('#2F4F4F')
viewer.scene.globe.undergroundColorAlphaByDistance = new Cesium.NearFarScalar(
  1000, 0.0,    // 近处透明
  10000, 1.0    // 远处显示
)

// 第 4 件:裁剪平面切剖面
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

## 半透明地表

```js
viewer.scene.globe.translucency = {
  enabled: true,
  alpha: 0.3,           // 近处透明
  backFaceAlpha: 0.1    // 背面更透明
}
```

效果:从远处看地形正常,飞到近处地形变透明,地下物体透出来。

## 添加地下物体

```js
// 1. 地下管线
viewer.entities.add({
  polyline: {
    positions: Cesium.Cartesian3.fromDegreesArrayHeights([
      lng1, lat1, -50,   // 地下 50 米
      lng2, lat2, -60,
      lng3, lat3, -45
    ]),
    width: 8,
    material: new Cesium.PolylineGlowMaterialProperty({
      glowPower: 0.2,
      color: Cesium.Color.fromCssColorString('#1E90FF')
    })
  }
})

// 2. 地质层(多层)
const layers = [
  { name: '土壤层', top: 0, bottom: -50, color: '#8B4513' },
  { name: '砂岩层', top: -50, bottom: -200, color: '#DAA520' },
  { name: '基岩层', top: -200, bottom: -500, color: '#696969' }
]

layers.forEach(layer => {
  viewer.entities.add({
    name: layer.name,
    polygon: {
      hierarchy: Cesium.Cartesian3.fromDegreesArray([
        lng1, lat1, lng2, lat2, lng3, lat3
      ]),
      height: layer.bottom,
      extrudedHeight: layer.top,
      material: Cesium.Color.fromCssColorString(layer.color).withAlpha(0.6),
      outline: true,
      outlineColor: Cesium.Color.BLACK
    }
  })
})

// 3. 地下隧道模型
viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(lng, lat, -30),  // 地下 30m
  orientation: Cesium.Transforms.headingPitchRollQuaternion(
    Cesium.Cartesian3.fromDegrees(lng, lat, -30),
    new Cesium.HeadingPitchRoll(Cesium.Math.toRadians(90), 0, 0)
  ),
  model: {
    uri: '/models/tunnel.glb',
    minimumPixelSize: 128
  }
})
```

## 多边形剖切窗口(更灵活)

```js
// 沿任意多边形轮廓裁剪(不是盒子)
const regionHierarchy = new Cesium.PolygonHierarchy([
  Cesium.Cartesian3.fromDegrees(116.39, 39.91),
  Cesium.Cartesian3.fromDegrees(116.41, 39.91),
  Cesium.Cartesian3.fromDegrees(116.41, 39.89),
  Cesium.Cartesian3.fromDegrees(116.39, 39.89)
])

const clippingPolygons = new Cesium.ClippingPolygonCollection({
  polygons: [
    new Cesium.ClippingPolygon({
      positions: regionHierarchy.positions
    })
  ],
  inverse: false  // false=区域内显示, true=区域外显示
})

viewer.scene.globe.clippingPolygons = clippingPolygons
```

## 双屏对比(地表 + 地下)

```js
// 左半屏显示完整地表,右半屏显示地下剖面
viewer.scene.splitPosition = 0.5
```

## 关键点

- ⚠️ `enableCollisionDetection = false` 必须,否则相机被顶回地表
- ⚠️ `depthTestAgainstTerrain = true` 必须,否则穿透的山体不遮挡地下物体
- ⚠️ 裁剪平面的"距离"是从原点开始计算的(负值方向)
- ✅ 4 件套全部配置才能看到完整地下效果
- ✅ 性能:地下场景通常加载瓦片少,反而流畅

## 常见坑

| 现象 | 原因 | 解决 |
|---|---|---|
| 相机下不去,被弹回 | 没关碰撞检测 | `enableCollisionDetection = false` |
| 地下纯黑 | 没设 undergroundColor | 设任意非黑色 |
| 物体穿透地表显示 | depthTestAgainstTerrain 仍是 false | 改为 true |
| 剖切面穿模 / 锯齿 | 没开背脸剔除 + 裙边 | `backFaceCulling: true`, `showSkirts: true` |
| 地形半透明看不到地下物体 | translucency alpha 设太大 | 调到 0.3 以下 |

## 进阶:动态剖切动画

```js
// 沿 X 轴方向缓慢移动剖切平面
let offset = -700
viewer.scene.preRender.addEventListener(() => {
  offset += 0.5
  clippingPlanes.planes[0].distance = offset
})
```