---
recipe: viewshed-analysis
title: 视域分析(两点通视 + 区域扇区)
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 视域分析

> **何时用**:基站选址、瞭望塔点位、监控摄像头覆盖范围评估。

## 一、两点通视(line-of-sight)

```js
function checkLineOfSight(start, end, targetHeightOffset = 0) {
  // 抬高目标点(避免塔底被自身挡住)
  if (targetHeightOffset > 0) {
    const carto = Cesium.Cartographic.fromCartesian(end)
    carto.height += targetHeightOffset
    end = Cesium.Cartographic.toCartesian(carto)
  }

  const direction = Cesium.Cartesian3.subtract(end, start, new Cesium.Cartesian3())
  const distance = Cesium.Cartesian3.magnitude(direction)
  Cesium.Cartesian3.normalize(direction, direction)

  const ray = new Cesium.Ray(start, direction)
  const hit = viewer.scene.pickFromRay(ray)

  const visible = !Cesium.defined(hit) ||
    Cesium.Cartesian3.distance(start, hit.position) >= distance - 0.1

  // 画线
  viewer.entities.add({
    polyline: {
      positions: [start, end],
      width: 3,
      material: visible ? Cesium.Color.LIME : Cesium.Color.RED
    }
  })

  if (!visible && hit) {
    viewer.entities.add({
      position: hit.position,
      point: { pixelSize: 12, color: Cesium.Color.ORANGE }
    })
  }

  return { visible, blocker: hit }
}

// ⚠️ 必须开启地形深度测试!
viewer.scene.globe.depthTestAgainstTerrain = true

// 使用:鼠标选两点
const points = []
handler.setInputAction(event => {
  const ray = viewer.camera.getPickRay(event.position)
  const cart = viewer.scene.globe.pick(ray, viewer.scene)
  if (!cart) return

  points.push(cart)
  if (points.length === 2) {
    // 模拟铁塔(目标点抬高 30m)
    checkLineOfSight(points[0], points[1], 30)
    points.length = 0
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

## 二、区域视域(扇区扫描)

```js
async function viewshedAnalysis(observerPos, maxRadius = 2000, ringStep = 50, angleStep = 5) {
  const results = []
  const ringCount = Math.floor(maxRadius / ringStep)
  const angleCount = Math.floor(360 / angleStep)

  // 1. 采样地形(预计算可见性)
  const observerCarto = Cesium.Cartographic.fromCartesian(observerPos)
  const lonLatToCart = (lon, lat) => Cesium.Cartesian3.fromRadians(lon, lat, observerCarto.height)

  for (let r = ringStep; r <= maxRadius; r += ringStep) {
    for (let a = 0; a < 360; a += angleStep) {
      const azimuth = Cesium.Math.toRadians(a)
      const dx = r * Math.cos(azimuth)
      const dy = r * Math.sin(azimuth)

      const targetPos = lonLatToCart(
        observerCarto.longitude + dx / (6378137 * Math.cos(observerCarto.latitude)),
        observerCarto.latitude + dy / 6378137
      )

      const direction = Cesium.Cartesian3.subtract(targetPos, observerPos, new Cesium.Cartesian3())
      const distance = Cesium.Cartesian3.magnitude(direction)
      Cesium.Cartesian3.normalize(direction, direction)

      const ray = new Cesium.Ray(observerPos, direction)
      const hit = viewer.scene.pickFromRay(ray)

      const visible = !Cesium.defined(hit) ||
        Cesium.Cartesian3.distance(observerPos, hit.position) >= distance - 0.1

      results.push({ angle: a, radius: r, distance, visible, targetPos })
    }
  }

  // 2. 绘制可见扇区(每 5° 一条线)
  const visiblePoints = results.filter(r => r.visible).map(r => r.targetPos)
  if (visiblePoints.length > 0) {
    viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          [observerPos, ...visiblePoints, observerPos]
        ),
        material: Cesium.Color.LIME.withAlpha(0.2),
        outline: true,
        outlineColor: Cesium.Color.LIME
      }
    })
  }

  // 3. 可视率统计
  const ratio = results.filter(r => r.visible).length / results.length
  console.log(`可视率: ${(ratio * 100).toFixed(1)}%`)

  return { ratio, results }
}
```

## 关键点

- ⚠️ `viewer.scene.globe.depthTestAgainstTerrain = true` 必开!否则射线穿透山体
- ⚠️ 目标点要抬高(铁塔高度)避免塔底自遮挡
- ⚠️ 区域视域 ray 数量 = `(maxRadius / ringStep) * (360 / angleStep)`(5000 米 + 5° 步长 ≈ 14400 次)
- ⚠️ 大型场景需性能优化(预计算、Worker、节流)
- ✅ 用 `angleStep: 5°` 快速预览,`1°` 精细评估

## 性能调优

```js
// 角度步长:精度换速度
angleStep = 5  // 5° 步长 ≈ 72 个角度(快速)
angleStep = 1  // 1° 步长 ≈ 360 个角度(精细,5x 慢)

// 环数
ringStep = 100  // 100m 步长 ≈ 20 环(2km 半径)

// 加节流
let lastTime = 0
function throttledViewshed() {
  const now = Date.now()
  if (now - lastTime < 200) return
  lastTime = now
  viewshedAnalysis(...)
}
```

## 应用场景

- 基站选址:可视率 > 70% 算合格
- 瞭望塔点位:确认能覆盖火源监测范围
- 监控摄像头:扇区覆盖评估
- 风电场选址:可视率分析