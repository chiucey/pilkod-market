---
module: 03
title: 核心 API 速查 — Entity vs Primitive 决策表
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://juejin.cn/post/7638459369085747227, https://cesium.com/learn/cesiumjs-fundamentals/]
status: stable
---

# 03 · 核心 API 速查(决策导向)

> **本模块覆盖**:Entity vs Primitive 选型 / 各类图元的取舍 / 拾取结果区分。
> **何时加载**:不知道用哪个 API / Entity 卡顿 / 想优化但不知道从哪改。

---

## 3.1 Entity vs Primitive(灵魂之问)

> 这是 Cesium 开发者最高频的决策问题。

### 决策表

| 数据规模 | 时间动态 | 交互复杂度 | 推荐 |
|---|---|---|---|
| **< 100** | 否 | 简单 | **Entity** |
| **< 100** | 是 | 任意 | **Entity**(自带 Property + 时间) |
| **100 ~ 1000** | 否 | 简单 | **Entity** 或 PrimitiveCollection |
| **1000 ~ 10000** | 任意 | 简单 | **Primitive + 专用 Collection** |
| **> 10000** | 否 | 简单 | **Primitive**(必须) |
| **> 10000** | 是 | 任意 | **Primitive + 手动管理** |
| **任何规模** | 任意 | 复杂 | **Entity**(Property + 时间免费) |

### 性能差异(实测参考)

> 数据来源:[CSDN 性能对比](https://blog.csdn.net/weixin_29275257/article/details/159632080)

| 指标 | Entity (10000 点) | PrimitiveCollection (10000 点) |
|---|---|---|
| 创建时间 | 1120 ms | 340 ms |
| 帧率 | 24.6 FPS | 58.2 FPS |
| 渲染时间 | 32.8 ms | 12.4 ms |
| 内存占用 | 高 | 低 72% |

**为什么 Primitive 更快?**
- Entity 内部封装了 Property / 时间系统 / 事件
- 每次属性变化触发回调,JS 层开销显著
- Primitive 直接走 WebGL,跳过中间层

---

## 3.2 各类 Primitive 选型

| 场景 | 推荐 |
|---|---|
| 大量静态点(>1k) | `PointPrimitiveCollection` |
| 大量图标(>1k) | `BillboardCollection` |
| 大量文字(>1k) | `LabelCollection` |
| 大量折线 | `PolylineCollection`(空间线)/ `GroundPolylinePrimitive`(贴地线) |
| 大量静态几何 | `Primitive` + `GeometryInstance[]` |
| 贴地区域 | `GroundPrimitive`(地形)/ `ClassificationPrimitive`(3D Tiles) |
| glTF 模型 | `Model.fromGltfAsync`(底层)/ Entity(model)(高层) |
| 3D Tiles | `Cesium3DTileset`(必须用 Primitive 路径) |

### 关键差异表

| 对比项 | Entity | Primitive |
|---|---|---|
| 抽象层级 | 高 | 低 |
| 学习曲线 | 平 | 陡 |
| 时间动画 | ✅ 内置 | ❌ 手动 |
| 数据绑定 | ✅ PropertyBag | ❌ 自管 |
| 拾取 | `picked.id` 即 Entity | `picked.primitive` + `picked.id`(GeometryInstance id) |
| 性能 | 中小数据 OK | 大数据必须 |
| 动态修改 | 直接改属性 | 部分属性需重建 |

---

## 3.3 Entity 常用图形

```js
const entity = viewer.entities.add({
  id: 'unique-id',
  position: Cesium.Cartesian3.fromDegrees(lng, lat, h),
  point: {
    pixelSize: 10,
    color: Cesium.Color.RED,
    outlineColor: Cesium.Color.BLACK,
    outlineWidth: 2,
    heightReference: Cesium.HeightReference.NONE
  },
  billboard: {
    image: '/icons/marker.png',
    scale: 1.0,
    rotation: 0,
    pixelOffset: new Cesium.Cartesian2(0, -16),
    eyeOffset: new Cesium.Cartesian3(0, 0, 0),
    verticalOrigin: Cesium.VerticalOrigin.BOTTOM
  },
  label: {
    text: '北京',
    font: '14px sans-serif',
    fillColor: Cesium.Color.WHITE,
    outlineColor: Cesium.Color.BLACK,
    outlineWidth: 2,
    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
    pixelOffset: new Cesium.Cartesian2(0, -32),
    showBackground: true,
    backgroundColor: Cesium.Color.BLACK.withAlpha(0.5),
    backgroundPadding: new Cesium.Cartesian2(8, 4),
    scaleByDistance: new Cesium.NearFarScalar(100, 1.5, 5000, 0.5),
    translucencyByDistance: new Cesium.NearFarScalar(100, 1.0, 5000, 0.0)
  },
  polyline: {
    positions: Cesium.Cartesian3.fromDegreesArray([lng1, lat1, lng2, lat2]),
    width: 3,
    material: Cesium.Color.BLUE,
    arcType: Cesium.ArcType.GEODESIC,  // 大圆线(默认 GEODESIC,空间直线用 NONE)
    clampToGround: false
  },
  polygon: {
    hierarchy: Cesium.Cartesian3.fromDegreesArray([lng1, lat1, lng2, lat2, lng3, lat3]),
    height: 0,
    extrudedHeight: 100,
    material: Cesium.Color.GREEN.withAlpha(0.5),
    outline: true,
    outlineColor: Cesium.Color.BLACK,
    perPositionHeight: false
  },
  model: {
    uri: '/models/car.glb',
    scale: 1.0,
    minimumPixelSize: 64
  },
  properties: {  // 自定义业务属性
    id: 12345,
    type: 'sensor',
    name: '消防栓 #001'
  }
})

// 动态属性
entity.position = new Cesium.CallbackProperty((time, result) => {
  return Cesium.Cartesian3.fromDegrees(lng + Math.sin(Date.now()/1000)*0.01, lat, h)
}, false)
```

---

## 3.4 Primitive 通用结构

```js
// GeometryInstance:描述单个几何
const instance = new Cesium.GeometryInstance({
  geometry: new Cesium.RectangleGeometry({
    rectangle: Cesium.Rectangle.fromDegrees(116.3, 39.8, 116.5, 40.0),
    vertexFormat: Cesium.PerInstanceColorAppearance.VERTEX_FORMAT,
    height: 0
  }),
  attributes: {
    color: Cesium.ColorGeometryInstanceAttribute.fromColor(
      Cesium.Color.RED.withAlpha(0.5)
    ),
    show: new Cesium.ShowGeometryInstanceAttribute(true),
    distanceDisplayCondition: new Cesium.DistanceDisplayConditionGeometryInstanceAttribute(0, 100000)
  },
  id: 'my-rect-1'  // 拾取标识
})

// Primitive:合并渲染
const primitive = new Cesium.Primitive({
  geometryInstances: instance,
  appearance: new Cesium.PerInstanceColorAppearance({
    translucent: true,
    closed: true,
    flat: false
  }),
  asynchronous: true,              // true=异步创建,生产环境推荐
  allowPicking: true,
  releaseGeometryInstances: true  // 上传 GPU 后释放 CPU 数据
})

viewer.scene.primitives.add(primitive)

// 运行时修改属性(只能改声明过的)
const attrs = primitive.getGeometryInstanceAttributes('my-rect-1')
attrs.color = Cesium.ColorGeometryInstanceAttribute.toValue(Cesium.Color.BLUE)
attrs.show = Cesium.ShowGeometryInstanceAttribute.toValue(false)
```

---

## 3.5 拾取结果区分

`scene.pick()` 返回值类型表:

| 拾取目标 | `picked.primitive` | `picked.id` |
|---|---|---|
| Entity | Entity 实例本身 | Entity(同上) |
| Primitive + GeometryInstance | Primitive | GeometryInstance 的 id |
| PointPrimitive | PointPrimitive | undefined |
| Billboard | Billboard | undefined(业务字段挂 primitive.customData) |
| Label | Label | undefined |
| Cesium3DTileFeature | Cesium3DTileFeature | undefined(用 `getProperty(name)`) |
| Model | Model | Model(可挂自定义属性) |

```js
viewer.screenSpaceEventHandler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (!Cesium.defined(picked)) return

  if (picked.id instanceof Cesium.Entity) {
    // Entity 路径
    console.log('Entity:', picked.id.name, picked.id.properties)
  } else if (picked instanceof Cesium.Cesium3DTileFeature) {
    // 3D Tiles 路径
    console.log('Tile:', picked.getProperty('name'))
  } else if (picked.primitive) {
    // Primitive / Collection 元素
    console.log('Primitive:', picked.primitive.constructor.name)
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

> 🔧 **drillPick** 用于穿透拾取(返回所有命中):
> ```js
> const pickeds = viewer.scene.drillPick(event.position)
> ```

---

## 3.6 常用 Appearance 选型

| Appearance | 用途 | 关键参数 |
|---|---|---|
| `PerInstanceColorAppearance` | 每实例独立颜色 | `translucent`, `closed`, `flat` |
| `MaterialAppearance` | 自定义材质 | `material`(Material 实例) |
| `EllipsoidSurfaceAppearance` | 贴椭球表面 | `material`, `translucent` |
| `PolylineMaterialAppearance` | 折线材质 | `material` |

---

## 3.7 Material 速查

```js
// 颜色
Cesium.Material.fromType('Color', { color: Cesium.Color.RED })

// 影像
Cesium.Material.fromType('Image', { image: '/textures/marble.jpg' })

// 网格 / 线框
Cesium.Material.fromType('Grid', { color: Cesium.Color.YELLOW, cellAlpha: 0.2 })

// 条带
Cesium.Material.fromType('Stripe', { evenColor: Cesium.Color.WHITE, oddColor: Cesium.Color.BLACK })

// 渐变(箭头线)
Cesium.Material.fromType('PolylineArrow', { color: Cesium.Color.CYAN })

// 发光线
Cesium.Material.fromType('PolylineGlow', { color: Cesium.Color.YELLOW, glowPower: 0.2 })

// 虚线
Cesium.Material.fromType('PolylineDash', { color: Cesium.Color.WHITE, dashLength: 16 })

// 自定义 GLSL
new Cesium.Material({
  fabric: {
    type: 'Custom',
    uniforms: { color: Cesium.Color.CYAN },
    source: `czm_material czm_getMaterial(czm_materialInput materialInput) {
      czm_material material = czm_getDefaultMaterial(materialInput);
      material.diffuse = color.rgb;
      material.alpha = color.a;
      return material;
    }`
  }
})
```

---

## 3.8 MVT API 速查(矢量瓦片)

> **版本对照**:1.40+ `VectorTileImageryProvider`(已弃用) → 1.104+ 第三方包 → 1.145+ 官方 `MVTDataProvider`
> **详细用法**:`modules/02-data-sources.md` § MVT

### 官方(1.145+)

| API | 一句话 | 备注 |
|---|---|---|
| `Cesium.MVTDataProvider.fromUrl(url, opts)` | 异步加载 MVT 数据源 | 返回 Promise<MVTDataProvider> |
| `provider.tileset` | 内部 3D Tileset(供 viewer.zoomTo 用) | |
| `opts.minZoom` / `maxZoom` | 瓦片金字塔范围 | 必填 |
| `opts.extent` | 地理范围(Cesium.Rectangle) | 必填 |
| `new Cesium.Resource({ url, queryParameters })` | 带 token 的资源封装 | 用于鉴权 |

### 第三方(1.104+)

| 包 | 入口 | 一句话 |
|---|---|---|
| `mvt-imagery-provider` | `MVTImageryProvider.fromUrl(styleUrl, opts)` | 基于 mapbox-gl-js,样式丰富 |
| `cesium-mvt-imagery-provider` | `new CesiumMVTImageryProvider({ urlTemplate, layerName, style })` | 轻量自实现,简单样式 |

### 早期 API(1.40~1.104,已弃用,不再推荐)

| API | 一句话 | 状态 |
|---|---|---|
| `new Cesium.VectorTileImageryProvider({ url, layer, style, tilingScheme })` | 早期 MVT 影像图层 | ⚠️ 已弃用 |

---

## 3.9 决策流程图

```
开始
  ↓
数据量是否 > 1000?
  ├─ 否 → 用 Entity(省事)
  └─ 是 → 用 Primitive
        ↓
       是否需时间动画?
        ├─ 否 → Primitive + 专用 Collection
        └─ 是 → CallbackProperty 驱动 Primitive(手动管)
              ↓
             是否需要拾取 + 业务属性?
              ├─ 否 → 不挂 id,纯渲染
              └─ 是 → GeometryInstance.id + getGeometryInstanceAttributes
```

---

## 进一步阅读

- [Corvus: 100k tracks @ 60fps](https://corvusintell.com/blog/c2-systems/battlefield-visualization-performance) — 三方实战
- [Primitive 学习笔记](https://juejin.cn/post/7638459369085747227) — 中文系统讲解
- `references/api-quick-ref.md` — 完整 API 索引

## 下一步

- 交互与可视化 → `modules/04-interaction-and-viz.md`
- 性能优化 → `modules/05-performance-and-rendering.md`