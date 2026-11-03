---
module: 04
title: 交互与可视化 — 拾取、标注、Popup、特效
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://cesium.com/learn/cesiumjs-fundamentals/, https://cesium.com/docs/tutorials/creating-entities]
status: stable
---

# 04 · 交互与可视化

> **本模块覆盖**:鼠标事件 / 拾取 / 标注 / Popup / 信息窗体 / 动态属性 / 简单特效。
> **何时加载**:点击交互 / 高亮 / 自定义 Tooltip / 鼠标悬停提示 / 动态更新属性。

---

## 4.1 鼠标事件(ScreenSpaceEventHandler)

```js
const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)

// 左键点击
handler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  console.log('click', picked)
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)

// 右键 / 鼠标移动 / 滚轮
Cesium.ScreenSpaceEventType.LEFT_CLICK          // 左键
Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK   // 左键双击
Cesium.ScreenSpaceEventType.LEFT_DOWN / UP      // 按下/抬起
Cesium.ScreenSpaceEventType.RIGHT_CLICK
Cesium.ScreenSpaceEventType.RIGHT_DOWN / UP
Cesium.ScreenSpaceEventType.MIDDLE_CLICK
Cesium.ScreenSpaceEventType.MOUSE_MOVE          // 移动
Cesium.ScreenSpaceEventType.WHEEL               // 滚轮
Cesium.ScreenSpaceEventType.PINCH_START / END   // 触摸缩放

// 销毁(组件卸载必须)
handler.destroy()
```

### ScreenSpaceEventHandler vs 相机控件

注意:**滚轮事件默认被相机控制占用**(缩放)。要监听滚轮且不被相机拦截:

```js
viewer.scene.screenSpaceCameraController.enableZoom = false  // 禁用相机滚轮
// 或使用 MOUSE_MOVE + 自定义逻辑
```

---

## 4.2 拾取三层(pick / drillPick / pickFromRay)

| API | 用途 | 返回 |
|---|---|---|
| `scene.pick(pos)` | 单点拾取 | 最先命中(从前往后) |
| `scene.drillPick(pos)` | 穿透拾取 | 所有命中的数组 |
| `scene.pickFromRay(ray)` | 沿射线拾取 | 第一个命中(常用于通视) |

```js
// 鼠标位置 → 世界坐标
function mouseToWorld(windowPos) {
  return viewer.scene.pickEllipsoid(
    windowPos,
    viewer.scene.globe.ellipsoid
  )
}

// 射线构造(用于自定义 3D 拾取)
const ray = viewer.camera.getPickRay(windowPos)  // 关键 API!
const picked = viewer.scene.pickFromRay(ray)
```

> 🔧 **pickFromRay 必须先 getPickRay** 才能拿到相机出发的射线。pickEllipsoid 只命中椭球面。

### pick vs drillPick 性能

- pick 单次,drillPick 多次(每次下一层)
- 鼠标移动高频触发 → 用 pick + 节流 16ms
- 关键操作 → drillPick 保证不漏

---

## 4.3 标注(billboard / label)

### Billboard(图标)

```js
viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(116.4, 39.9),
  billboard: {
    image: '/icons/fire-station.png',
    scale: 1.0,
    rotation: 0,                      // 旋转(弧度)
    pixelOffset: new Cesium.Cartesian2(0, -16),  // 像素偏移
    eyeOffset: new Cesium.Cartesian3(0, 0, -100),  // 视角深度偏移
    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
    horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
    heightReference: Cesium.HeightReference.NONE,
    color: Cesium.Color.WHITE,        // 整体着色(白 = 原图)
    scaleByDistance: new Cesium.NearFarScalar(100, 1.5, 5000, 0.5),
    translucencyByDistance: new Cesium.NearFarScalar(100, 1.0, 5000, 0.0),
    distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 10000),
    disableDepthTestDistance: 0       // 0=深度测试,>0 远于这个距离的图标不深度测试
  }
})
```

> 💡 **`disableDepthTestDistance`** 解决"图标被建筑挡住看不见"问题,但滥用会导致穿模感。

### Label(文字)

```js
viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(116.4, 39.9),
  label: {
    text: '故宫博物院',
    font: '14px "Microsoft YaHei", sans-serif',
    fillColor: Cesium.Color.WHITE,
    outlineColor: Cesium.Color.BLACK,
    outlineWidth: 2,
    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
    showBackground: true,
    backgroundColor: Cesium.Color.fromCssColorString('#000').withAlpha(0.7),
    backgroundPadding: new Cesium.Cartesian2(8, 4),
    pixelOffset: new Cesium.Cartesian2(0, -32),
    scaleByDistance: new Cesium.NearFarScalar(100, 1.2, 8000, 0.5),
    translucencyByDistance: new Cesium.NearFarScalar(100, 1.0, 5000, 0.3)
  }
})
```

### 大量标注用 BillboardCollection(性能更好)

```js
const billboards = viewer.scene.primitives.add(new Cesium.BillboardCollection())
for (let i = 0; i < 10000; i++) {
  billboards.add({
    position: Cesium.Cartesian3.fromDegrees(
      116 + Math.random() * 0.1,
      39 + Math.random() * 0.1
    ),
    image: '/icons/sensor.png',
    scale: 0.8,
    color: Cesium.Color.CYAN
  })
}
```

---

## 4.4 Popup / InfoBox

### 方案 1:CSS2DRenderer(DivOverlay)

```js
// 自定义 DOM 浮窗
const popup = document.createElement('div')
popup.className = 'cesium-popup'
popup.style.cssText = `
  position: absolute;
  pointer-events: none;
  background: rgba(0,0,0,0.85);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  display: none;
  z-index: 1000;
`
document.body.appendChild(popup)

handler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (Cesium.defined(picked) && picked.id) {
    const name = picked.id.name || picked.id.id || 'Unknown'
    popup.innerHTML = `<strong>${name}</strong>`
    popup.style.left = (event.position.x + 12) + 'px'
    popup.style.top = (event.position.y + 12) + 'px'
    popup.style.display = 'block'
  } else {
    popup.style.display = 'none'
  }
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE)
```

### 方案 2:跟随实体(每帧更新)

```js
const entity = viewer.entities.add({ ... })

viewer.scene.postRender.addEventListener(() => {
  const screenPos = viewer.cartesianToCanvasCoordinates(entity.position.getValue(viewer.clock.currentTime))
  if (screenPos) {
    popup.style.left = screenPos.x + 'px'
    popup.style.top = screenPos.y + 'px'
  }
})
```

> ⚠️ **`viewer.cartesianToCanvasCoordinates` 已弃用**,用 `viewer.scene.cartesianToCanvasCoordinates`。

---

## 4.5 选中高亮

```js
// 选中状态管理
let selectedEntity = null
const oldColor = new Map()

function selectEntity(entity) {
  if (selectedEntity) {
    // 恢复旧颜色
    if (oldColor.has(selectedEntity)) {
      selectedEntity.billboard.color = oldColor.get(selectedEntity)
      oldColor.delete(selectedEntity)
    }
    selectedEntity = null
  }

  if (entity && entity.billboard) {
    oldColor.set(entity, entity.billboard.color)
    entity.billboard.color = Cesium.Color.YELLOW  // 黄色高亮
    selectedEntity = entity
  }
}

// 3D Tiles 选中用 silhouetteColor
tileset.colorBlendMode = Cesium.ColorBlendMode.HIGHLIGHT
```

---

## 4.6 动态属性(CallbackProperty)

### 核心:每帧调用

```js
let currentTime = 0
const dynamicHeight = new Cesium.CallbackProperty((time, result) => {
  currentTime += 0.016
  return Math.sin(currentTime) * 100 + 200  // 上下浮动
}, false)  // false = 每帧求值

viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 0),
  ellipse: {  // 圆
    semiMinorAxis: 5000,
    semiMajorAxis: 5000,
    height: dynamicHeight,  // 动态高度!
    material: Cesium.Color.BLUE.withAlpha(0.5)
  }
})
```

### 驱动时间轴 / 外部数据

```js
// 从 WebSocket 推数据
const ws = new WebSocket('wss://...')
const dynamicPos = new Cesium.CallbackProperty((time, result) => {
  return latestPosition || Cesium.Cartesian3.fromDegrees(0, 0, 0)
}, false)

viewer.entities.add({
  position: dynamicPos,
  point: { pixelSize: 12, color: Cesium.Color.LIME }
})
```

> 💡 **CallbackProperty 第二个参数必为 false**,true 表示常量,只求一次。

---

## 4.7 简单特效

### 后处理(高斯模糊、辉光等)

```js
// Bloom(场景光晕)
const bloom = viewer.scene.postProcessStages.bloom
bloom.enabled = true
bloom.uniforms.glowOnly = false
bloom.uniforms.contrast = 128
bloom.uniforms.brightness = 0
bloom.uniforms.delta = 1.0
bloom.uniforms.sigma = 3.78
bloom.uniforms.stepSize = 5.0

// 环境光遮蔽
viewer.scene.postProcessStages.ambientOcclusion.enabled = true
viewer.scene.postProcessStages.ambientOcclusion.uniforms.intensity = 3

// FXAA(几乎免费的抗锯齿)
viewer.scene.postProcessStages.fxaa.enabled = true
```

### 大气 / 光照

```js
viewer.scene.globe.enableLighting = true       // 启用光照(白天黑夜)
viewer.scene.globe.dynamicAtmosphereLighting = true
viewer.scene.skyAtmosphere.show = true
viewer.scene.sun.show = true
viewer.scene.fog.enabled = true
viewer.scene.fog.density = 0.0001
```

### 流动线(自定义材质)

```js
const lineEntity = viewer.entities.add({
  polyline: {
    positions: Cesium.Cartesian3.fromDegreesArray([
      lng1, lat1, lng2, lat2, lng3, lat3
    ]),
    width: 3,
    material: new Cesium.PolylineGlowMaterialProperty({
      glowPower: 0.2,
      taperPower: 1.0,
      color: Cesium.Color.CYAN
    })
  }
})
```

---

## 4.8 经纬度/方位角标记工具

### 鼠标 → 经纬度显示

```js
const lonLatDiv = document.getElementById('lonlat')

handler.setInputAction(event => {
  const carto = viewer.scene.camera.positionCartographic
  const lon = Cesium.Math.toDegrees(carto.longitude).toFixed(4)
  const lat = Cesium.Math.toDegrees(carto.latitude).toFixed(4)
  const h = carto.height.toFixed(0)
  lonLatDiv.textContent = `经度:${lon}°  纬度:${lat}°  高度:${h}m`
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE)

// 或者用屏幕坐标 → 经纬度
handler.setInputAction(event => {
  const ray = viewer.camera.getPickRay(event.position)
  const carto = viewer.scene.globe.pick(ray, viewer.scene)
  if (carto) {
    const lon = Cesium.Math.toDegrees(carto.longitude).toFixed(4)
    const lat = Cesium.Math.toDegrees(carto.latitude).toFixed(4)
    console.log(`${lon}, ${lat}`)
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

---

## 4.9 常见交互模式

| 模式 | 实现 |
|---|---|
| 点击高亮 | pick → 改 billboard.color |
| 鼠标悬停 Popup | MOUSE_MOVE + pick + 浮窗 |
| 跟随实体飞 | `viewer.trackedEntity = entity` |
| 双击聚焦 | LEFT_DOUBLE_CLICK → viewer.zoomTo |
| 实体选中指示器 | `selectionIndicator: true`(默认) |

---

## 下一步

- 性能优化 → `modules/05-performance-and-rendering.md`
- 工程化(框架集成)→ `modules/06-engineering.md`
- 典型场景(测量/视域/淹没)→ `modules/07-typical-scenarios.md`