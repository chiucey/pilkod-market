---
recipe: measure-distance
title: 距离 / 面积测量
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 距离 / 面积测量

> **何时用**:测量两点间距离 / 多边形面积 / 实时显示测量结果。
> **依赖**:可选 `turf.js`(用于面积计算)。

## 完整代码

```js
import * as Cesium from 'cesium'
import * as turf from '@turf/turf'

const positions = []      // 顺序点位(Cartesian3)
let totalDistance = 0      // 累计距离(米)
const tempLines = []      // 临时显示线
let areaEntity = null     // 当前多边形
let labelEntity = null    // 实时数值标签

// UI 元素
const resultDiv = document.getElementById('measure-result')

// 切换测量模式
function startMeasure() {
  positions.length = 0
  totalDistance = 0
  tempLines.forEach(l => viewer.entities.remove(l))
  tempLines.length = 0
  if (areaEntity) viewer.entities.remove(areaEntity)
  if (labelEntity) viewer.entities.remove(labelEntity)
}

function stopMeasure() {
  positions.length = 0
}

// 鼠标点击
handler.setInputAction(event => {
  const ray = viewer.camera.getPickRay(event.position)
  const cartesian = viewer.scene.globe.pick(ray, viewer.scene)
  if (!cartesian) return

  positions.push(cartesian)

  // 1. 标记点
  viewer.entities.add({
    position: cartesian,
    point: { pixelSize: 8, color: Cesium.Color.RED, outlineColor: Cesium.Color.WHITE, outlineWidth: 1 }
  })

  // 2. 距离增量
  if (positions.length >= 2) {
    const dist = Cesium.Cartesian3.distance(
      positions[positions.length - 2],
      positions[positions.length - 1]
    )
    totalDistance += dist

    // 显示线段
    const line = viewer.entities.add({
      polyline: {
        positions: [positions[positions.length - 2], positions[positions.length - 1]],
        width: 2,
        material: Cesium.Color.YELLOW,
        clampToGround: true
      }
    })
    tempLines.push(line)
  }

  // 3. 面积计算(≥3 点)
  let area = 0
  if (positions.length >= 3) {
    const coords = positions.map(p => {
      const carto = Cesium.Ellipsoid.WGS84.cartesianToCartographic(p)
      return [
        Cesium.Math.toDegrees(carto.longitude),
        Cesium.Math.toDegrees(carto.latitude)
      ]
    })
    coords.push(coords[0])  // 闭合
    const polygon = turf.polygon([coords])
    area = turf.area(polygon)

    // 显示闭合多边形
    if (areaEntity) viewer.entities.remove(areaEntity)
    areaEntity = viewer.entities.add({
      polygon: {
        hierarchy: positions.map(p => p.clone()),  // 需 clone 避免引用
        material: Cesium.Color.RED.withAlpha(0.3),
        outline: true,
        outlineColor: Cesium.Color.RED,
        clampToGround: true
      }
    })
  }

  // 4. 更新数值
  resultDiv.innerHTML = `
    <strong>测量结果</strong><br>
    距离: ${totalDistance.toFixed(1)} m<br>
    面积: ${area > 0 ? area.toFixed(1) + ' m²' : '—'}
  `
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)

// 双击结束
handler.setInputAction(() => stopMeasure(), Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK)
```

## 关键点

- ✅ `viewer.scene.globe.pick(ray, scene)` 把屏幕坐标转成地球表面坐标
- ✅ `Cartesian3.distance(a, b)` 算两点直线距离
- ✅ `turf.area(polygon)` 算多边形面积(注意单位:平方米)
- ✅ 多边形 `hierarchy` 需要 clone Cartesian3 数组(否则会被引用覆盖)
- ❌ 双击不会触发 LEFT_CLICK?会的,但要 LEFT_DOUBLE_CLICK 先注册

## 扩展

- **测高**:用 `Cartographic.fromCartesian(p).height` 算高程
- **方位角**:用 `Cartesian3.angleBetween` + 方位修正
- **保存测量结果**:序列化成 GeoJSON 输出