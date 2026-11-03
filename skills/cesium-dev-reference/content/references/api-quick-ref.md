---
module: ref-api-quick-ref
title: 关键 API 一句话索引
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# Cesium 关键 API 一句话索引

> 每个 API 一行简介。详细用法见 `modules/` 对应章节,完整文档见 [cesium.com/learn/cesiumjs/ref-doc](https://cesium.com/learn/cesiumjs/ref-doc)。

## 坐标 / 数学(Core Math)

| API | 一句话 | 章节 |
|---|---|---|
| `Cartesian3.fromDegrees(lon, lat, h)` | 经纬度 → ECEF 笛卡尔坐标 | 01 |
| `Cartesian3.fromDegreesArray([l1,l2,...])` | 数组批量转换 | 01 |
| `Cartesian3.fromDegreesArrayHeights([l,l,h,l,l,h,...])` | 带高度数组转换 | 01 |
| `Cartesian3.distance(a, b)` | 欧氏距离(米) | 01 |
| `Cartesian3.angleBetween(a, b)` | 两向量夹角(弧度) | 01 |
| `Cartographic.fromDegrees(lon, lat, h)` | WGS84 经纬高 | 01 |
| `Ellipsoid.WGS84.cartographicToCartesian(carto)` | 经纬高 → Cartesian3 | 01 |
| `Ellipsoid.WGS84.cartesianToCartographic(cart)` | Cartesian3 → 经纬高 | 01 |
| `Transforms.eastNorthUpToFixedFrame(origin)` | 原点处 ENU 局部坐标系矩阵 | 01 |
| `Transforms.headingPitchRollToFixedFrame(pos, hpr)` | 位置 + 朝向 → 4x4 矩阵 | 01 |
| `Math.toRadians(deg)` / `Math.toDegrees(rad)` | 度 ↔ 弧度 | 01 |
| `Math.lerp(a, b, t)` / `Math.clamp(v, lo, hi)` | 线性插值 / 钳制 | 01 |

## 时间(Clock)

| API | 一句话 | 章节 |
|---|---|---|
| `Clock` | 时间轴,管理 start/stop/currentTime | 01 |
| `JulianDate` | 时间戳(儒略日) | 01 |
| `SampledPositionProperty` | 时序位置(自动插值) | 04 |
| `CallbackProperty(cb, isConstant)` | 自定义每帧调用的属性 | 04 |

## 相机 / 场景(Camera / Scene)

| API | 一句话 | 章节 |
|---|---|---|
| `camera.setView({ destination, orientation })` | 瞬时定位 | 01 |
| `camera.flyTo({ destination, orientation, duration })` | 平滑飞行 | 01 |
| `camera.zoomTo(entity / tileset)` | 飞到对象包围盒 | 01 |
| `camera.lookAt(target, offset)` | 锁定目标旋转视角 | 01 |
| `scene.globe.depthTestAgainstTerrain` | 地形深度测试开关 | 07 |
| `scene.globe.translucency` | 透明地表(underground 模式) | 07 |
| `scene.globe.undergroundColor` | 地下背景色 | 07 |
| `scene.globe.clippingPlanes` | 地形裁剪平面 | 07 |
| `scene.screenSpaceCameraController.enableCollisionDetection` | 相机碰撞检测 | 07 |
| `scene.requestRenderMode` | 按需渲染(关闭持续渲染省 CPU) | 05 |
| `scene.maximumScreenSpaceError` | 瓦片细节阈值(越小越精细) | 05 |
| `scene.fog.enabled` / `scene.fog.density` | 雾效 | 01 |

## 拾取 / 事件(Pick / Event)

| API | 一句话 | 章节 |
|---|---|---|
| `viewer.scene.pick(windowPos)` | 单点拾取(返回最先命中) | 04 |
| `viewer.scene.drillPick(windowPos)` | 多点拾取(返回所有命中) | 04 |
| `viewer.scene.pickFromRay(ray)` | 沿射线拾取(用于通视) | 04 |
| `ScreenSpaceEventHandler(canvas)` | 屏幕事件处理器 | 04 |
| `event.setInputAction(callback, ScreenSpaceEventType.LEFT_CLICK)` | 绑定事件 | 04 |
| `viewer.clock.onTick.addEventListener(cb)` | 时钟 tick 回调 | 01 |

## Entity(高层 API)

| API | 一句话 | 章节 |
|---|---|---|
| `viewer.entities.add({ position, billboard, label, ... })` | 添加实体 | 03 |
| `viewer.entities.getById(id)` | 按 ID 获取 | 03 |
| `viewer.entities.remove(entity)` | 移除 | 03 |
| `viewer.entities.removeAll()` | 清空(慎用!) | 03 |
| `Entity.position = Cartesian3.fromDegrees(...)` | 实体位置 | 03 |
| `Entity.point` / `billboard` / `label` / `polyline` / `polygon` / `model` | 实体图形 | 03 |
| `PolygonHierarchy` | 多边形带洞层级 | 03 |
| `CallbackProperty` 作为位置 / 高度 → 动态属性 | 动画/驱动 | 04 |

## Primitive(底层 API)

| API | 一句话 | 章节 |
|---|---|---|
| `Primitive({ geometryInstances, appearance })` | 通用图元 | 03 |
| `GeometryInstance({ geometry, attributes, id })` | 单个几何实例 | 03 |
| `PrimitiveCollection` | 图元集合(分层管理) | 03 |
| `BillboardCollection` | 大量图标批量渲染 | 05 |
| `LabelCollection` | 大量文字批量渲染 | 05 |
| `PointPrimitiveCollection` | 大量点批量渲染 | 05 |
| `PolylineCollection` | 大量折线 | 03 |
| `GroundPrimitive` | 贴地形 / 3D Tiles | 03 |
| `GroundPolylinePrimitive` | 贴地折线 | 03 |
| `ClassificationPrimitive` | 分类投影到地形/3D Tiles | 03 |

## 3D Tiles / Model

| API | 一句话 | 章节 |
|---|---|---|
| `Cesium3DTileset.fromUrl(url)` | 加载 3D Tiles | 02 |
| `tileset.style` | 3D Tiles 样式(条件着色) | 02 |
| `tileset.readyPromise.then(t => ...)` | 加载完成回调 | 02 |
| `Model.fromGltfAsync({ url, modelMatrix, scale })` | 加载 glTF/GLB 模型 | 02 |
| `Cesium.createOsmBuildingsAsync()` | 加载全球 OSM 建筑瓦片 | 02 |
| `Cesium.createGooglePhotorealistic3DTileset()` | Google 实景 3D Tiles | 02 |

## 数据接入(Data Sources)

| API | 一句话 | 章节 |
|---|---|---|
| `ImageryLayer.fromProviderAsync(provider)` | 异步影像图层 | 02 |
| `BingMapsImageryProvider` / `ArcGisMapServerImageryProvider` | Bing / ArcGIS 影像 | 02 |
| `OpenStreetMapImageryProvider` | OSM 影像 | 02 |
| `UrlTemplateImageryProvider({ url })` | 自定义 XYZ 瓦片 | 02 |
| `CesiumTerrainProvider.fromUrl(url)` | 加载 quantized-mesh 地形 | 02 |
| `Terrain.fromWorldTerrain()` | Cesium ion 全球地形 | 02 |
| `CzmlDataSource.load(url)` | 加载 CZML | 02 |
| `GeoJsonDataSource.load(url, options)` | 加载 GeoJSON | 02 |
| `KmlDataSource.load(url)` | 加载 KML | 02 |

## 分析(Analysis)

| API | 一句话 | 章节 |
|---|---|---|
| `Cesium.sampleTerrainMostDetailed(terrainProvider, cartos)` | 高精度地形采样 | 07 |
| `Cesium.sampleHeightMostDetailed(globe, cartos)` | 简版地形采样 | 07 |
| `scene.pickFromRay(ray)` | 射线求交(通视分析) | 07 |
| `scene.sampleHeight(cartographic)` | 单点地形高度查询 | 07 |
| `CallbackProperty` + `PolygonHierarchy` | 动态淹没 | 07 |

## 性能诊断(Diagnostic)

| API | 一句话 | 章节 |
|---|---|---|
| `viewer.scene.debugShowFramesPerSecond = true` | 显示 FPS | 05 |
| `viewer.extend(viewerPerformanceWatchdogMixin)` | 性能监视 widget | 05 |
| `viewer.scene.primitives.add(new PerformanceDisplay())` | 性能面板 | 05 |
| `viewer.scene._frameStatistics` | 帧统计(FPS / render time) | 05 |

## UI 控件(Wigets)

| API | 一句话 | 章节 |
|---|---|---|
| `Viewer({ animation, timeline, geocoder, ... })` | 一站式控件配置 | 01 |
| `viewer.zoomTo` / `viewer.flyTo` | 视角控制 | 01 |
| `viewer.trackedEntity = entity` | 锁定实体跟随 | 01 |
| `viewer.selectedEntity = entity` | 高亮选中实体 | 01 |

## 销毁与生命周期(Lifecycle)

| API | 一句话 | 章节 |
|---|---|---|
| `viewer.destroy()` | 销毁 Viewer(必须!) | 06 |
| `viewer.isDestroyed()` | 检查是否已销毁 | 06 |
| `handler.destroy()` | 销毁事件处理器 | 06 |
| `tileset.destroy()` | 销毁 3D Tileset | 06 |
| `model.destroy()` | 销毁 Model | 06 |
| `primitiveCollection.removeAll()` | 清空图元集合 | 06 |
| `viewer.scene.primitives.remove(primitive)` | 移除图元 | 06 |

## 缺哪个 API?

如果上面没找到:
1. 直接查 `modules/` 对应章节
2. 查 [cesium.com/learn/cesiumjs/ref-doc](https://cesium.com/learn/cesiumjs/ref-doc)
3. 查 [Sandcastle](https://sandcastle.cesium.com) 看实际用例
4. 都没有 → 按 `self-evolution/coverage-gap-detector.md` 流程补齐本索引

---

**索引版本**:对应 CesiumJS 1.124+  
**更新机制**:每次 CesiumJS minor 版本发布后,跑 `self-evolution/maintenance-playbook.md` 的 API diff 任务。