---
module: 05
title: 性能与渲染优化 — LOD、Frustum、Instancing、Pick 调优
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://corvusintell.com/blog/c2-systems/battlefield-visualization-performance, https://blog.csdn.net/weixin_29275257/article/details/159632080]
status: stable
---

# 05 · 性能与渲染优化

> **本模块覆盖**:LOD / Frustum Culling / GPU Instancing / Pick 优化 / 内存管理。
> **何时加载**:场景卡顿 / 内存爆掉 / 大规模点位 / 想用 PerformanceDisplay 排查。

---

## 5.1 性能三板斧

### ① 实体层(Entity)→ Primitive 层(Primitive)

| 数据规模 | 推荐 |
|---|---|
| < 100 | Entity |
| 100~1000 | Entity 或 Primitive |
| 1000~10000 | Primitive + 专用 Collection |
| > 10000 | **必须** Primitive |

### ② requestRenderMode(几乎总是开启)

```js
viewer.scene.requestRenderMode = true  // 仅变化时重绘
viewer.scene.maximumRenderTimeChange = Infinity
```

**效果**:静态场景 0 FPS 开销(真没渲染),变化时才重绘。
**注意**:动画 / CallbackProperty 仍然每帧触发(因为它们在改渲染状态)。

### ③ LOD 阈值

```js
viewer.scene.maximumScreenSpaceError = 2  // 默认 2
// 增大 → 瓦片加载更少 → 流畅但粗糙
// 减小 → 瓦片加载更多 → 精细但卡

// 3D Tiles 加载参数
const tileset = await Cesium.Cesium3DTileset.fromUrl(url, {
  maximumScreenSpaceError: 16,
  maximumMemoryUsage: 512,         // MB 上限
  skipLevelOfDetail: true,          // 跳过中间 LOD
  immediatelyLoadDesiredLevelOfDetail: false,
  loadSiblings: false,
  cullWithChildrenBounds: true
})
```

---

## 5.2 GPU Instancing(批量渲染)

### 批量点

```js
// ❌ 慢:每个 Entity 一个 draw call
for (let i = 0; i < 10000; i++) {
  viewer.entities.add({ position: ..., point: { pixelSize: 6 } })
}

// ✅ 快:一个 draw call
const points = viewer.scene.primitives.add(new Cesium.PointPrimitiveCollection())
for (let i = 0; i < 10000; i++) {
  points.add({
    position: Cesium.Cartesian3.fromDegrees(...),
    pixelSize: 6,
    color: Cesium.Color.RED
  })
}
```

### 批量图标 / 文字

```js
const billboards = viewer.scene.primitives.add(new Cesium.BillboardCollection())
const labels = viewer.scene.primitives.add(new Cesium.LabelCollection())
```

### LOD 标签(关键!)

> 数据来源:[Corvus 100k tracks](https://corvusintell.com/blog/c2-systems/battlefield-visualization-performance)

10 万个 PointPrimitive 流畅,10 万个 Label 直接卡死。原因:Label 走 SDF 字形路径,既占字形图集又是独立 draw batch。

**解法:距离驱动的标签可见性**
```js
// 只在视距 < 5000 时显示标签
label.distanceDisplayCondition = new Cesium.DistanceDisplayCondition(0, 5000)

// 或用 LOD:近处显示标签,远处聚合显示
label.translucencyByDistance = new Cesium.NearFarScalar(500, 1.0, 5000, 0.0)
```

**典型操作员屏幕**:只显示 50~200 个标签(其余隐藏)。

---

## 5.3 Frustum Culling(视锥剔除)

Cesium 自动开启,但需正确配置:

```js
viewer.scene.farToNearRatio = 10000   // 默认
viewer.scene.fog.enabled = true        // 远处雾化也是变相裁剪
```

### 自定义裁剪平面

```js
// 在某高度以上不渲染(例如排除大气层外)
const clippingPlane = new Cesium.ClippingPlane(
  new Cesium.Cartesian3(0, 0, -1),  // 法向(向下)
  100000  // 距离(米)
)
viewer.scene.globe.clippingPlanes = new Cesium.ClippingPlaneCollection({
  planes: [clippingPlane],
  enabled: true
})
```

> 详见 `recipes/underground-mode.md` 和 `recipes/viewshed-analysis.md`。

---

## 5.4 Pick 优化

### 何时用 pick / drillPick

| 操作 | API | 频率 |
|---|---|---|
| 点击 | `pick` | 一次性 |
| 悬停 | `pick` + 节流 | 16ms 节流 |
| 高亮大量重叠对象 | `drillPick` | 谨慎 |
| 通视分析 | `pickFromRay` | 200ms 节流 |

### pick 性能瓶颈

- 单次 pick 在 100k Entity 场景:~3-5ms(可接受)
- drillPick 命中 5 层以上:可能 10ms+(需优化层级)
- MOUSE_MOVE + 高频 pick:**必加节流**

```js
let lastPickTime = 0
handler.setInputAction(event => {
  const now = Date.now()
  if (now - lastPickTime < 32) return  // ~30fps 节流
  lastPickTime = now
  const picked = viewer.scene.pick(event.position)
  // ...
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE)
```

---

## 5.5 内存管理

### 销毁时机

```js
// ❌ 不要依赖 removeAll()(会把所有都删掉,包括地形/3D Tiles)

// ✅ 引用跟踪
const myLayer = viewer.entities.add({ ... })
// 不用时
viewer.entities.remove(myLayer)

// ✅ 销毁 3D Tileset
tileset.destroy()  // 释放 GPU 资源

// ✅ 销毁 Model
model.destroy()

// ✅ 销毁 Viewer
viewer.destroy()  // 卸载整个 WebGL 上下文
```

### 泄漏检查

```js
// Chrome DevTools → Memory → Take Heap Snapshot → Comparison
// 关键对象:
// - Cesium3DTileset 数量不应持续增长
// - Entity 数量不应持续增长(除非业务要增)
// - Primitive 数量应稳定
```

### 何时触发 GC

```js
// 主动释放
tileset.destroy()
model.destroy()
viewer.entities.remove(tempEntity)

// 让浏览器 GC 跑
requestIdleCallback(() => { /* 等待 GC */ })
```

---

## 5.6 性能诊断工具

### PerformanceDisplay(内置面板)

```js
const pd = new Cesium.PerformanceDisplay({
  container: document.getElementById('perf-panel')
})
viewer.scene.primitives.add(pd)
// 显示:FPS、几何/纹理/着色器数量、内存
```

### FPS 显示

```js
viewer.scene.debugShowFramesPerSecond = true  // 左上角显示 FPS
```

### Performance Watchdog

```js
viewer.extend(Cesium.viewerPerformanceWatchdogMixin)
// 自动监控,低 FPS 时弹警告
```

### Chrome DevTools 三板斧

| 工具 | 排查 |
|---|---|
| **Performance 面板** | JS 执行 / 渲染时间 / FPS |
| **Memory 面板** | Heap Snapshot 看对象增长 |
| **Network 面板** | 瓦片下载时间(>5s 异常) |

---

## 5.7 渲染调优清单

```js
// 高频启用
viewer.scene.requestRenderMode = true
viewer.scene.maximumScreenSpaceError = 2
viewer.scene.fog.enabled = true
viewer.scene.postProcessStages.fxaa.enabled = true

// 按需
viewer.scene.globe.depthTestAgainstTerrain = false  // 关闭省性能(精确遮挡场景才开)

// 数据层
- 优先 PrimitiveCollection(>1000 必须)
- 大规模 Label 必有 LOD
- 大量 3D Tiles 用 skipLevelOfDetail

// 释放层
- 及时 destroy
- 不用的 callback 解绑
```

---

## 5.8 实测参考数据

> 数据来源:[CSDN 性能对比](https://blog.csdn.net/weixin_29275257/article/details/159632080)

| 场景 | Entity | Primitive | 提升 |
|---|---|---|---|
| 10000 Billboard 创建 | 1120 ms | 340 ms | 3.3x |
| 10000 Billboard 渲染 | 32.8 ms | 12.4 ms | 2.6x |
| 10000 Billboard 帧率 | 24.6 FPS | 58.2 FPS | 2.4x |
| 内存占用 | 100% | 28% | 72% 节省 |

---

## 5.9 常见性能坑

| 坑 | 现象 | 解决 |
|---|---|---|
| 大量 Entity 卡顿 | FPS 暴跌 | 改 Primitive + Collection |
| Label 全开 | 帧率 < 10 | 距离驱动的 LOD |
| 巨型 3D Tiles | 加载慢 | skipLevelOfDetail + 调 SSE |
| 频繁 flyTo | 卡顿 | 防抖 300ms |
| MOUSE_MOVE 高频拾取 | 帧率掉 | 节流 30fps |
| depthTestAgainstTerrain 全开 | 每帧 10⁶ 次高程查询 | 关闭,3D Tiles 内部处理 |
| CallbackProperty 复杂逻辑 | JS 主线程阻塞 | 简化逻辑或用 SampledProperty |
| 模型未压缩 | GPU 内存爆 | glTF Draco / Meshopt |

---

## 下一步

- 工程化 → `modules/06-engineering.md`
- 典型场景 → `modules/07-typical-scenarios.md`
- 避雷清单 → `modules/09-pitfalls-and-traps.md`