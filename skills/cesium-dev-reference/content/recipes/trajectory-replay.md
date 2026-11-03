---
recipe: trajectory-replay
title: 轨迹回放(车辆 / 航班 / 卫星)
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 轨迹回放

> **何时用**:车辆监控、航班轨迹、卫星轨道、迁徙路径回放。

## 方案 A:SampledPositionProperty(代码构造)

```js
// 数据格式
const trajectory = [
  { t: 0, lng: 116.4, lat: 39.9, h: 0, speed: 60 },     // 0 秒,北京
  { t: 60, lng: 117.4, lat: 39.9, h: 0, speed: 80 },    // 60 秒,东移 100km
  { t: 120, lng: 118.4, lat: 39.9, h: 0, speed: 100 },  // 120 秒
  { t: 180, lng: 119.4, lat: 39.9, h: 0, speed: 80 }
]

// 1. 构造时间属性
const positionProperty = new Cesium.SampledPositionProperty()
const velocityProperty = new Cesium.SampledProperty(Number)

const startTime = Cesium.JulianDate.fromIso8601('2026-09-22T00:00:00Z')
const stopTime = Cesium.JulianDate.addSeconds(
  startTime,
  trajectory[trajectory.length - 1].t,
  new Cesium.JulianDate()
)

trajectory.forEach(p => {
  const time = Cesium.JulianDate.addSeconds(startTime, p.t, new Cesium.JulianDate())
  positionProperty.addSample(time, Cesium.Cartesian3.fromDegrees(p.lng, p.lat, p.h))
  velocityProperty.addSample(time, p.speed)
})

// 2. 配置时钟
viewer.clock.startTime = startTime.clone()
viewer.clock.stopTime = stopTime.clone()
viewer.clock.currentTime = startTime.clone()
viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP
viewer.clock.multiplier = 30  // 30x 速
viewer.clock.shouldAnimate = true

// 3. 添加实体(自动按当前时间插值)
viewer.entities.add({
  name: '车辆',
  position: positionProperty,
  // 自动按速度方向调整朝向
  orientation: new Cesium.VelocityOrientationProperty(positionProperty),
  model: {
    uri: '/models/car.glb',
    minimumPixelSize: 32,
    scale: 1.0
  },
  // 路径尾巴(可选)
  path: {
    resolution: 1,
    material: new Cesium.PolylineGlowMaterialProperty({
      glowPower: 0.1,
      color: Cesium.Color.fromCssColorString('#00FF7F')
    }),
    width: 3,
    leadTime: 0,    // 不画未来
    trailTime: 60   // 画过去 60 秒
  },
  // 标签
  label: {
    text: '京 A12345',
    font: '14px sans-serif',
    pixelOffset: new Cesium.Cartesian2(0, -32),
    fillColor: Cesium.Color.WHITE,
    outlineColor: Cesium.Color.BLACK,
    outlineWidth: 2,
    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
    showBackground: true,
    backgroundColor: Cesium.Color.BLACK.withAlpha(0.6),
    backgroundPadding: new Cesium.Cartesian2(8, 4)
  },
  properties: {
    speed: velocityProperty,
    type: 'car'
  }
})
```

## 方案 B:CZML(声明式,适合服务端下发)

```js
const czmlData = [
  {
    id: 'document',
    name: '车辆回放',
    version: '1.0',
    clock: {
      interval: '2026-09-22T00:00:00Z/2026-09-23T00:00:00Z',
      currentTime: '2026-09-22T00:00:00Z',
      multiplier: 30,
      range: 'LOOP_STOP',
      step: 'SYSTEM_CLOCK_MULTIPLIER'
    }
  },
  {
    id: 'car-1',
    name: '京 A12345',
    availability: '2026-09-22T00:00:00Z/2026-09-22T08:00:00Z',
    description: '<p>车辆轨迹回放</p>',
    position: {
      epoch: '2026-09-22T00:00:00Z',
      cartographicDegrees: [
        // [t0, lng, lat, h, t1, lng, lat, h, ...]
        0, 116.4, 39.9, 0,
        60, 117.4, 39.9, 0,
        120, 118.4, 39.9, 0,
        180, 119.4, 39.9, 0
      ]
    },
    orientation: {
      velocityReference: '#position'  // 自动用速度方向
    },
    model: {
      gltf: '/models/car.glb',
      scale: 1.0
    },
    path: {
      material: {
        polylineGlow: {
          color: { rgba: [0, 255, 127, 200] },
          glowPower: 0.1
        }
      },
      width: 3,
      leadTime: 0,
      trailTime: 60
    },
    label: {
      text: '京 A12345',
      fillColor: { rgba: [255, 255, 255, 255] },
      outlineColor: { rgba: [0, 0, 0, 255] },
      outlineWidth: 2,
      style: 'FILL_AND_OUTLINE',
      showBackground: true,
      backgroundColor: { rgba: [0, 0, 0, 178] },
      font: '14px sans-serif',
      pixelOffset: { cartesian2: [0, -32] }
    }
  }
]

Cesium.CzmlDataSource.load(czmlData).then(ds => {
  viewer.dataSources.add(ds)
  viewer.flyTo(ds)
})
```

## 关键点

- ⚠️ SampledPositionProperty 必须有 startTime + stopTime 在 clock 内,否则不可见
- ⚠️ `VelocityOrientationProperty` 只对 Entity 有效(Primitive 不支持)
- ⚠️ CZML 时间用 ISO 8601 字符串
- ⚠️ CZML `cartographicDegrees` 是 `[t, lng, lat, h, t, lng, lat, h, ...]` 交替格式
- ✅ 用 `path` 自动画尾巴
- ✅ 用 `clockRange: LOOP_STOP` 让动画循环播放

## 控制面板

```html
<div id="controls">
  <button id="play">▶</button>
  <button id="pause">⏸</button>
  <button id="reset">⟲</button>
  <input type="range" id="speed" min="1" max="300" value="30">
  <span id="speed-val">30x</span>
  <input type="range" id="time-scrub" min="0" max="100" value="0">
</div>

<script>
document.getElementById('play').onclick = () => viewer.clock.shouldAnimate = true
document.getElementById('pause').onclick = () => viewer.clock.shouldAnimate = false
document.getElementById('reset').onclick = () => {
  viewer.clock.currentTime = viewer.clock.startTime.clone()
}
document.getElementById('speed').oninput = e => {
  viewer.clock.multiplier = +e.target.value
  document.getElementById('speed-val').textContent = e.target.value + 'x'
}
</script>
```

## 多车辆方案

```js
// 数组结构
trajectories.forEach((traj, idx) => {
  const positionProperty = new Cesium.SampledPositionProperty()
  traj.points.forEach(p => {
    const time = Cesium.JulianDate.addSeconds(startTime, p.t, new Cesium.JulianDate())
    positionProperty.addSample(time, Cesium.Cartesian3.fromDegrees(p.lng, p.lat, p.h))
  })

  viewer.entities.add({
    id: `car-${idx}`,
    position: positionProperty,
    orientation: new Cesium.VelocityOrientationProperty(positionProperty),
    model: { uri: '/models/car.glb', minimumPixelSize: 24 },
    properties: { id: traj.id, name: traj.name }
  })
})
```

## 性能

- 100 个车:60fps(用 Entity 路径)
- 1000+ 车:必须 PrimitiveCollection + 手动管理
- CZML 大文件:用 Gzip + 分块加载