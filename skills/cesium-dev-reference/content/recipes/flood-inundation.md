---
recipe: flood-inundation
title: 动态洪水淹没模拟
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 动态洪水淹没模拟

> **何时用**:应急管理、洪水模拟、水位上涨动画、风险评估。

## 完整代码

```js
import * as Cesium from 'cesium'
import * as turf from '@turf/turf'

// 全局状态
let currentWaterHeight = 0
let floodEntity = null
let floodAnimationId = null

// 第一步:计算地形极值
async function getTerrainExtremum(positions, sampleDensity = 5000) {
  const lonLats = positions.map(c => {
    const carto = Cesium.Ellipsoid.WGS84.cartesianToCartographic(c)
    return [
      Cesium.Math.toDegrees(carto.longitude),
      Cesium.Math.toDegrees(carto.latitude)
    ]
  })

  // 用 turf 生成采样点
  const bbox = turf.bbox(turf.polygon([lonLats]))
  const cellSize = Math.sqrt(
    (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) / sampleDensity
  )
  const grid = turf.pointGrid(bbox, cellSize, { units: 'degrees' })

  const cartos = grid.features.map(f =>
    Cesium.Cartographic.fromDegrees(f.geometry.coordinates[0], f.geometry.coordinates[1])
  )

  const updated = await Cesium.sampleTerrainMostDetailed(
    viewer.terrainProvider,
    cartos
  )

  const heights = updated.map(c => c.height).filter(h => !isNaN(h))
  return {
    min: Math.min(...heights),
    max: Math.max(...heights)
  }
}

// 第二步:启动淹没模拟
async function startFloodSimulation(regionPositions, options = {}) {
  const {
    targetHeight = 50,
    riseSpeed = 0.1,  // 米/帧
    duration = Infinity
  } = options

  const { min, max } = await getTerrainExtremum(regionPositions)

  if (targetHeight < min) {
    console.warn(`目标水位 ${targetHeight}m 低于地形最低点 ${min.toFixed(1)}m,不会产生淹没`)
    return
  }

  currentWaterHeight = min  // 从地形最低点开始

  // 构造 hierarchy(需 clone,避免引用冲突)
  const hierarchy = new Cesium.PolygonHierarchy(regionPositions.map(p => p.clone()))

  // 动态多边形
  floodEntity = viewer.entities.add({
    name: '洪水淹没',
    polygon: {
      hierarchy: hierarchy,
      // 关键:动态属性驱动拉伸高度
      extrudedHeight: new Cesium.CallbackProperty((time, result) => {
        return currentWaterHeight
      }, false),
      // 固定底部高度(地形最低点以下)
      height: min - 10,
      material: new Cesium.Color(0.2, 0.4, 0.8, 0.6),
      outline: true,
      outlineColor: Cesium.Color.fromCssColorString('#1E90FF'),
      perPositionHeight: true
    }
  })

  // 启动上涨循环
  const startTime = Date.now()
  function tick() {
    if (currentWaterHeight < targetHeight) {
      currentWaterHeight += riseSpeed
      if (currentWaterHeight > targetHeight) currentWaterHeight = targetHeight
    }

    if (Date.now() - startTime > duration * 1000) {
      stopFloodSimulation()
      return
    }

    floodAnimationId = requestAnimationFrame(tick)
  }
  tick()

  return { min, max }
}

function stopFloodSimulation() {
  if (floodAnimationId) cancelAnimationFrame(floodAnimationId)
  if (floodEntity) viewer.entities.remove(floodEntity)
  floodAnimationId = null
  floodEntity = null
}

// 使用:绘制多边形后启动
async function start() {
  // regionPositions 由你的绘制工具给出
  await startFloodSimulation(regionPositions, {
    targetHeight: 80,
    riseSpeed: 0.2,
    duration: 30  // 30 秒后自动停止
  })
}
```

## 关键点

- ⚠️ 必须从地形最低点开始涨,否则水体从地下冒出来
- ⚠️ CallbackProperty 第二个参数必须 false(动态)
- ⚠️ 多边形 `height` 固定为 `min - 10`,`extrudedHeight` 动态变化
- ⚠️ `perPositionHeight: true` 让多边形顶面/底面用每个顶点的高度
- ⚠️ `hierarchy` 要传 Cartesian3 数组(不是 Cartographic)
- ✅ 采样密度根据精度需求调整(5000 通常够)
- ✅ 上升速度 0.1~0.5 米/帧,根据目标高度调整

## 物理真实性进阶

```js
// 根据洪水量动态计算上升速率
const volume = 1e8  // 立方米
const floodArea = turf.area(turf.polygon([coords]))  // 平方米
const riseRate = (volume / floodArea) / 3600  // 米/秒

// 根据时间累积
const elapsed = (Date.now() - startTime) / 1000
currentWaterHeight = min + (volume / floodArea) * Math.min(elapsed, totalTime)
```

## 视觉增强

```js
// 1. 加水面波纹(自定义材质)
material: new Cesium.Material({
  fabric: {
    type: 'Water',
    uniforms: {
      normalMap: '/textures/waterNormals.jpg',
      frequency: 1000.0,
      animationSpeed: 0.02,
      amplitude: 10.0
    }
  }
})

// 2. 水面透明度渐变
material: Cesium.Color.BLUE.withAlpha(0.6)  // 半透明

// 3. 加流场箭头(EntityPath)
viewer.entities.add({
  position: floodEntity.position,
  path: {
    material: new Cesium.PolylineGlowMaterialProperty({
      glowPower: 0.2,
      color: Cesium.Color.CYAN
    }),
    width: 4,
    leadTime: 0,
    trailTime: 60
  }
})
```

## 避坑

| 坑 | 解决 |
|------|------|
| 水体从地底冒出来 | 计算 minHeight 后从该值开始涨 |
| 帧率掉 | `requestRenderMode = true`(但 CallbackProperty 每帧触发) |
| 顶点不贴合地形 | 多边形顶点用 ENU 局部坐标 + perPositionHeight |
| 大区域采样慢 | 异步 + Promise.all 并发 |