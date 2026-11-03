---
module: 01
title: 核心基础 — 地球、相机、坐标系、时间、场景
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://cesium.com/learn/cesiumjs-fundamentals/, https://cesium.com/docs/tutorials/quick-start]
status: stable
---

# 01 · 核心基础

> **本模块覆盖**:地球模型 / 相机控制 / 坐标系转换 / 时间轴 / 场景配置。
> **何时加载**:第一次接触 Cesium、坐标系混用报错、相机不知道用哪个 API、时序数据无从下手。

---

## 1.1 地球(Ellipsoid / Globe)

Cesium 默认使用 **WGS84 椭球**(长半轴 6378137 m)。

```js
// 默认椭球
Cesium.Ellipsoid.WGS84

// 切换(月球 / 火星)
Cesium.Ellipsoid.default = Cesium.Ellipsoid.MOON   // 1.133+ 支持火星
```

**Globe** 负责渲染地形 + 影像:

```js
viewer.scene.globe.depthTestAgainstTerrain = true      // 地形深度测试
viewer.scene.globe.translucency.enabled = true        // 透明地表(underground)
viewer.scene.globe.undergroundColor = Cesium.Color.BLACK  // 地下背景色
viewer.scene.globe.show = true                         // 是否显示地球
```

> 💡 **`depthTestAgainstTerrain` 是地下模式 / 视域分析的关键开关**,默认 false。

---

## 1.2 相机(Camera)

```js
// 瞬时定位
viewer.camera.setView({
  destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 1000),
  orientation: { heading: 0, pitch: -Cesium.Math.PI_OVER_TWO, roll: 0 }
})

// 平滑飞行
viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(...),
  orientation: { ... },
  duration: 3.0,    // 秒
  easingFunction: Cesium.EasingFunction.QUADRATIC_IN_OUT
})

// 飞到对象
viewer.zoomTo(entity)              // Entity
viewer.flyTo(tileset)              // 3D Tileset
viewer.flyToBoundingSphere(bounds) // 包围球

// 锁定目标
viewer.camera.lookAt(target, new Cesium.HeadingPitchRange(0, -π/4, 1000))
viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY)  // 解除锁定
```

### Heading / Pitch / Roll 含义

| 轴 | 含义 | 0° 朝向 |
|---|---|---|
| **Heading** | 绕 Z(上)旋转 | 正北(顺时针+) |
| **Pitch** | 绕 Y(东)旋转 | 水平(-90° 朝下) |
| **Roll** | 绕 X(北)旋转 | 水平 |

### 常见坑

- ❌ **`flyTo` 频繁调用卡顿** → 加防抖(300ms)
- ❌ **`lookAt` 后无法 setView** → 必须先 `lookAtTransform(IDENTITY)` 解除
- ❌ **没设置 orientation 时相机方向不确定** → 必填 heading/pitch

---

## 1.3 坐标系(Coordinate Systems)

### 三层坐标

| 层 | 类 | 单位 | 用途 |
|---|---|---|---|
| 地理 | `Cartographic` | 弧度 + 米 | 经纬高(人类友好) |
| 球面笛卡尔 | `Cartesian3` | 米 | 3D 计算 / GPU |
| 屏幕 | `Cartesian2` | 像素 | 鼠标交互 |

### 互转

```js
// 经纬度 → Cartesian3(最常用)
const pos = Cesium.Cartesian3.fromDegrees(lng, lat, h)

// Cartesian3 → 经纬度
const carto = Cesium.Ellipsoid.WGS84.cartesianToCartographic(pos)
const lng = Cesium.Math.toDegrees(carto.longitude)
const lat = Cesium.Math.toDegrees(carto.latitude)

// 数组批量
const positions = Cesium.Cartesian3.fromDegreesArray([lng1, lat1, lng2, lat2, ...])
const positions3D = Cesium.Cartesian3.fromDegreesArrayHeights([lng1, lat1, h1, ...])
```

### ENU 局部坐标系

```js
// 在某点建立 ENU 局部坐标系(模型朝向常用)
const origin = Cesium.Cartesian3.fromDegrees(lng, lat, h)
const enuMatrix = Cesium.Transforms.eastNorthUpToFixedFrame(origin)
// 矩阵列: [east, north, up, origin]

// 模型放置
const hpr = new Cesium.HeadingPitchRoll(
  Cesium.Math.toRadians(90),  // heading
  0,                           // pitch
  0                            // roll
)
const modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(origin, hpr)
```

> ⚠️ **本地高程 vs 椭球高程**:WGS84 是椭球面高度,不是海拔。差几十米很正常。

### 火星坐标系(GCJ02)怎么办?

Cesium 默认 WGS84,但国内地图常用 GCJ02(火星坐标)/ BD09(百度)。如果数据来自高德/百度,需要反向纠偏才能正确显示。详见 `modules/09-pitfalls-and-traps.md`。

---

## 1.4 时间(Clock / JulianDate)

### 时钟

```js
const viewer = new Cesium.Viewer('cesiumContainer', {
  animation: true,    // 左下角动画控件
  timeline: true,     // 底部时间轴
  clock: new Cesium.Clock({
    startTime: Cesium.JulianDate.fromIso8601('2026-01-01T00:00:00Z'),
    stopTime:  Cesium.JulianDate.fromIso8601('2026-12-31T23:59:59Z'),
    currentTime: Cesium.JulianDate.now(),
    clockRange: Cesium.ClockRange.LOOP_STOP,
    multiplier: 60,  // 1秒真实 = 60秒仿真
    shouldAnimate: true
  })
})
```

### 时序数据驱动

```js
// 静态位置
entity.position = Cesium.Cartesian3.fromDegrees(...)

// 时序位置(按时间自动插值)
entity.position = new Cesium.SampledPositionProperty()
entity.position.addSample(time1, pos1)
entity.position.addSample(time2, pos2)

// 每帧自定义属性
entity.height = new Cesium.CallbackProperty((time, result) => {
  return Math.sin(Date.now() / 1000) * 100  // 任意逻辑
}, false)
```

> 💡 **CallbackProperty 第二个参数 false = 每帧求值**,true = 只求一次。动态属性必须 false。

### JulianDate 操作

```js
const t1 = Cesium.JulianDate.fromIso8601('2026-09-22T00:00:00Z')
const t2 = Cesium.JulianDate.addSeconds(t1, 3600, new Cesium.JulianDate())  // +1小时
const diff = Cesium.JulianDate.secondsDifference(t2, t1)  // 3600
const isoStr = Cesium.JulianDate.toIso8601(t1)  // '2026-01-01T00:00:00Z'
```

---

## 1.5 场景(Scene)

```js
viewer.scene  // Scene 实例,核心渲染对象

// 渲染参数
viewer.scene.requestRenderMode = true                    // 按需渲染(默认 false 持续)
viewer.scene.maximumRenderTimeChange = Infinity         // 永不强制重绘
viewer.scene.maximumScreenSpaceError = 2                // LOD 阈值(1.5~4)
viewer.scene.fog.enabled = true
viewer.scene.fog.density = 0.0001                       // 雾密度

// 调试
viewer.scene.debugShowFramesPerSecond = true            // 显示 FPS
viewer.scene.globe.show = true                          // 显示地球
viewer.scene.skyAtmosphere.show = true                  // 大气层
viewer.scene.sun.show = true                            // 太阳
viewer.scene.moon.show = true                           // 月亮
viewer.scene.backgroundColor = Cesium.Color.BLACK       // 太空背景

// 后处理
viewer.scene.postProcessStages.fxaa.enabled = true       // FXAA 抗锯齿
viewer.scene.postProcessStages.bloom.enabled = false     // 关闭 bloom
```

### 性能开关

| 开关 | 推荐值 | 备注 |
|---|---|---|
| `requestRenderMode` | **true** | 仅变化时重绘,大幅省 CPU |
| `maximumScreenSpaceError` | 2~4 | 越大越流畅,越小越精细 |
| `fxaa.enabled` | true | 几乎免费的抗锯齿 |
| `depthTestAgainstTerrain` | 按需 | 关闭省性能;开启让 3D 物体与地形正确遮挡 |

---

## 1.6 Widget 配置

Viewer 构造时禁用不需要的控件:

```js
const viewer = new Cesium.Viewer('cesiumContainer', {
  baseLayerPicker: false,    // 不要底图选择器
  geocoder: false,           // 不要地址搜索
  homeButton: false,          // 不要主页按钮
  sceneModePicker: false,     // 不要 2D/3D/Columbus 切换
  navigationHelpButton: false,
  animation: false,          // 不要左下时间动画
  timeline: false,           // 不要底部时间轴
  fullscreenButton: false,
  vrButton: false,
  selectionIndicator: false, // 不要选中指示器
  infoBox: false,            // 不要信息框
  // 中文语言
  // lang: 'zh-CN'  // 1.108+
})
```

---

## 1.7 销毁与生命周期

```js
// 销毁 Viewer(组件卸载时必做!)
function destroyViewer() {
  if (viewer && !viewer.isDestroyed()) {
    // 1. 销毁所有事件处理器
    handlers.forEach(h => h.destroy())
    // 2. 销毁 Viewer
    viewer.destroy()
    viewer = null
  }
}

// React 卸载
useEffect(() => {
  const viewer = new Cesium.Viewer(...)
  return () => {
    if (viewer && !viewer.isDestroyed()) viewer.destroy()
  }
}, [])

// Vue 卸载
onBeforeUnmount(() => {
  if (viewer && !viewer.isDestroyed()) viewer.destroy()
})
```

> ⚠️ **不销毁 viewer 会导致 WebGL 上下文泄漏**,浏览器会自动限制 WebGL 实例数(通常 16 个),泄漏到上限后页面就崩了。

---

## 1.8 进一步阅读

- [CesiumJS Fundamentals](https://cesium.com/learn/cesiumjs-fundamentals/) — 官方入门
- [Coordinate systems in CesiumJS](https://app.studyraid.com/en/read/15463/537296/working-with-coordinate-systems-in-cesiumjs) — 坐标系详细说明
- `references/api-quick-ref.md` — API 速查

## 下一步

- 数据接入 → `modules/02-data-sources.md`
- API 速查 → `modules/03-core-api-cheatsheet.md`
- 典型场景 → `modules/07-typical-scenarios.md`