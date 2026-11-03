---
recipe: terrain-profile
title: 地形剖面分析
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 地形剖面分析

> **何时用**:沿线段查看地形起伏(公路选线、管线规划、可视化辅助)。

## 完整代码

```js
async function drawTerrainProfile(startCart, endCart, samples = 100) {
  // 1. 计算沿线均匀采样点
  const startCarto = Cesium.Cartographic.fromCartesian(startCart)
  const endCarto = Cesium.Cartographic.fromCartesian(endCart)

  const startLon = startCarto.longitude
  const startLat = startCarto.latitude
  const endLon = endCarto.longitude
  const endLat = endCarto.latitude

  const cartos = []
  for (let i = 0; i <= samples; i++) {
    const t = i / samples
    const lon = Cesium.Math.lerp(startLon, endLon, t)
    const lat = Cesium.Math.lerp(startLat, endLat, t)
    cartos.push(Cesium.Cartographic.fromRadians(lon, lat, 0))
  }

  // 2. 采样地形高度(异步,需要 terrain provider)
  const updated = await Cesium.sampleTerrainMostDetailed(
    viewer.terrainProvider,
    cartos
  )

  // 3. 计算累计距离
  const totalDistance = Cesium.Cartesian3.distance(startCart, endCart)
  const profile = updated.map((carto, i) => {
    const dist = i * totalDistance / samples
    return {
      distance: dist,
      height: carto.height,
      longitude: carto.longitude,
      latitude: carto.latitude
    }
  })

  // 4. 在 3D 场景绘制剖面线(抬高避免遮挡)
  viewer.entities.add({
    polyline: {
      positions: profile.flatMap(p => [
        Cesium.Cartesian3.fromRadians(p.longitude, p.latitude, p.height + 200)
      ]),
      width: 3,
      material: Cesium.Color.YELLOW
    },
    name: '剖面'
  })

  // 5. 绘制到 2D 图表(ECharts)
  drawProfileChart(profile)

  return profile
}

// ECharts 图表
function drawProfileChart(profile) {
  const chart = echarts.init(document.getElementById('profile-chart'))
  chart.setOption({
    title: { text: '地形剖面', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `距离: ${p.data[0].toFixed(0)}m<br>海拔: ${p.data[1].toFixed(1)}m`
      }
    },
    xAxis: {
      type: 'value',
      name: '距离(m)',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: '海拔(m)',
      nameLocation: 'middle',
      nameGap: 40
    },
    series: [{
      type: 'line',
      data: profile.map(p => [p.distance, p.height]),
      areaStyle: { color: 'rgba(135, 206, 250, 0.5)' },
      lineStyle: { color: '#FFA500', width: 2 },
      symbol: 'none'
    }]
  })
}
```

## 关键点

- ⚠️ `sampleTerrainMostDetailed` 需要 `viewer.terrainProvider` 已加载完成
- ⚠️ 异步调用 — 用 `async/await` 或 Promise
- ⚠️ 剖面线抬高 200m(避免被地形/3D Tiles 遮挡)
- ✅ 采样数 100 通常够用,精确场景用 200
- ✅ 用 ECharts/Chart.js/D2 任何图表库都行

## 扩展

- **多段折线剖面**:循环调用 `drawTerrainProfile`
- **挖填方计算**:剖面 + 设计高程 → 面积积分
- **可视域沿线评估**:对每个采样点做通视判断