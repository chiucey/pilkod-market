---
module: 09
title: 避雷清单 — CORS、坐标系、token、内存、性能坑
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://cesium.com/docs, https://github.com/CesiumGS/cesium]
status: stable
---

# 09 · 避雷清单(Pitfalls & Traps)

> **本模块覆盖**:开发中真实踩过的坑、典型报错、排查思路。
> **何时加载**:场景"诡异"地不显示 / 报错信息看不懂 / 性能莫名下降 / 坐标系错位。

---

## 9.1 报错速查表

| 报错 | 根本原因 | 解决方案 |
|---|---|---|
| `TypeError: Cannot read property 'destroy' of null` | `destroy()` 被调用两次 | 加 `if (viewer && !viewer.isDestroyed())` |
| `Failed to execute 'texImage2D' on 'WebGLRenderingContext': The image element contains cross-origin data` | 图片资源跨域 | `<img crossorigin="anonymous">` 或服务端 CORS |
| `Entity with id 'xxx' already exists` | 重复添加同 ID | 先 `getById` → 存在则 `remove` |
| `Uncaught TypeError: identifier 'cesium' has already been declared` | 多次 `import * as Cesium from 'cesium'` | 全项目只一处 `import`,其他地方按需引入 |
| `Cesium is not defined` | Webpack 没把 Cesium 暴露为全局 | `externals: { cesium: 'Cesium' }` |
| 404 `/cesium/Workers/...` | `CESIUM_BASE_URL` 没设置 | `window.CESIUM_BASE_URL = '/cesium/'` |
| `Cannot read property 'length' of undefined` (MVT) | TileJSON 缺 `vector_layers` 字段 | QGIS 导出勾选 "Include vector layers metadata" |
| 球体被压扁 / 不显示地球 | 椭球设置错 | 确认 `Ellipsoid.default = Ellipsoid.WGS84` |
| pick 永远返回 `undefined` | Entity 在 viewer.entities 但被遮挡 / 缩放太小 | 拉近相机 / 改 entity 的 `id` |

---

## 9.2 CORS(跨域问题)

### 现象
浏览器 Console 出现 `Access to XMLHttpRequest at '...' has been blocked by CORS policy`,瓦片加载 404。

### 解决:Nginx 反代添加 CORS 头

```nginx
location /3dtiles/ {
  add_header 'Access-Control-Allow-Origin' '*';
  add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
  alias /var/www/3dtiles-data/;
}
```

或服务端 Java/Python/Node:

```python
# Flask
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
```

### 3D Tiles 必须 CORS
跨域的 tileset.json 和 .b3dm/.glb 必须全部 CORS。任意一个失败都会让瓦片集加载不全。

---

## 9.3 坐标系混用

### WGS84 vs GCJ02 vs BD09

| 坐标系 | 来源 | 偏移(相对 WGS84) |
|---|---|---|
| **WGS84** | GPS / 国际标准 | 0 |
| **GCJ02**(火星坐标) | 国测局加密算法 | 国内 50~500m |
| **BD09** | 百度再次加密 | 国内 100~1000m |

> 💡 **Cesium 内部一律 WGS84**。如果数据来自高德/腾讯,必须反向纠偏(GCJ02 → WGS84);百度数据要 BD09 → GCJ02 → WGS84。

### 纠偏代码

```js
// GCJ02 → WGS84 (反向算法)
function gcj02ToWgs84(lng, lat) {
  const a = 6378245.0
  const ee = 0.00669342162296594323
  let dLat = transformLat(lng - 105.0, lat - 35.0)
  let dLng = transformLng(lng - 105.0, lat - 35.0)
  const radLat = lat / 180.0 * Math.PI
  let magic = Math.sin(radLat)
  magic = 1 - ee * magic * magic
  const sqrtMagic = Math.sqrt(magic)
  dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI)
  dLng = (dLng * 180.0) / (a / sqrtMagic * Math.cos(radLat) * Math.PI)
  return [lng - dLng, lat - dLat]
}
```

### WGS84 vs 局部 ENU

```js
// 错误:把局部坐标当世界坐标
viewer.entities.add({
  position: new Cesium.Cartesian3(0, 0, 0),  // 地心!
  model: { uri: 'tree.glb' }
})

// 正确:在 ENU 原点上用 modelMatrix
const origin = Cesium.Cartesian3.fromDegrees(lng, lat, 0)
const modelMatrix = Cesium.Transforms.eastNorthUpToFixedFrame(origin)
// modelMatrix × 局部坐标 = 世界坐标
```

---

## 9.4 token 失效 / 配额耗尽

### 现象
- Console 警告:`Failed to load resource: 401 Unauthorized`
- 影像 / 地形 / OSM Buildings 全黑

### 排查

```js
// 检查 token 是否设置
console.log(Cesium.Ion.defaultAccessToken)

// 手动测试 token
fetch('https://assets.ion.cesium.com/v1/assets/1/endpoint?access_token=YOUR_TOKEN')
  .then(r => r.json())
  .then(console.log)
```

### 解决

1. **申请新 token**:[ion.cesium.com](https://ion.cesium.com/) → Access Tokens
2. **后端代理注入**(避免硬编码):

```js
// 前端
fetch('/api/cesium-token').then(r => r.json()).then(({ token }) => {
  Cesium.Ion.defaultAccessToken = token
})

// 后端 (Node.js Express)
app.get('/api/cesium-token', (req, res) => {
  res.json({ token: process.env.CESIUM_ION_TOKEN })
})
```

3. **国内替代**:不用 ion,改自建瓦片服务

---

## 9.5 内存泄漏

### 检查清单

```js
// 1. viewer.destroy() 调用?
onBeforeUnmount(() => {
  if (viewer && !viewer.isDestroyed()) {
    viewer.destroy()  // 必做!
  }
})

// 2. Handler 销毁?
const handler = new Cesium.ScreenSpaceEventHandler(canvas)
// ...
handler.destroy()

// 3. 3D Tileset 销毁?
tileset.destroy()

// 4. Model 销毁?
model.destroy()

// 5. removeAll() 慎用!
viewer.scene.primitives.removeAll()  // 会把地形、3D Tiles 都删掉
```

### 排查工具

Chrome DevTools → Memory → Take Heap Snapshot → Comparison:
- 关注 `Cesium3DTileset` / `Entity` / `Primitive` 数量
- 持续增长 = 泄漏

---

## 9.6 性能突然下降

### 排查三板斧

```js
// 1. FPS?
viewer.scene.debugShowFramesPerSecond = true

// 2. 性能监视
viewer.extend(Cesium.viewerPerformanceWatchdogMixin)
viewer.scene.primitives.add(new Cesium.PerformanceDisplay())

// 3. Chrome DevTools Performance 录制
```

### 常见诱因

| 诱因 | 排查 |
|---|---|
| Entity 数量爆炸 | `viewer.entities.values.length` 看 |
| 巨型 glTF / 3D Tiles | 看瓦片内存 |
| Label 全开 | 看 Label 渲染 |
| CallbackProperty 死循环 | 看 JS 执行时间 |
| 后处理全开 | FXAA / Bloom / AO 占用 GPU |
| MOUSE_MOVE 高频 | 加节流 |

---

## 9.7 模型不显示 / 位置错乱

### 模型不显示

```js
// 1. URL 是否正确?浏览器能直接打开吗?
// 2. 模型坐标系是否正确?(局部 vs 世界)
// 3. 是否被遮挡?拉远相机看
// 4. minimumPixelSize 是否设太大?

viewer.entities.add({
  model: {
    uri: '/models/tree.glb',
    minimumPixelSize: 64,
    maximumScale: 20000
  }
})
```

### 模型飞到了地心

```js
// ❌ 错:直接给局部坐标
position: new Cesium.Cartesian3(0, 0, 0)

// ✅ 对:用 modelMatrix
const modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(
  Cesium.Cartesian3.fromDegrees(lng, lat, h),
  new Cesium.HeadingPitchRoll(0, 0, 0)
)
```

### glTF 旋转不对

```js
// 用 HeadingPitchRollQuaternion
const orientation = Cesium.Transforms.headingPitchRollQuaternion(
  Cesium.Cartesian3.fromDegrees(lng, lat, h),
  new Cesium.HeadingPitchRoll(
    Cesium.Math.toRadians(90),  // 偏航:正北顺时针
    0,
    0
  )
)

viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(lng, lat, h),
  orientation: orientation,  // ← 这个!
  model: { uri: 'plane.glb' }
})
```

---

## 9.8 时间不动态

### 现象
数据没动 / 轨迹不前进。

### 排查

```js
// 1. 时钟是否启动?
viewer.clock.shouldAnimate = true

// 2. 时钟 multiplier 是否合理?
viewer.clock.multiplier = 60  // 1秒真实 = 60秒仿真

// 3. CZML 的 clock 是否设置?
// 4. SampledProperty 的时间范围覆盖当前时间?
```

---

## 9.9 Cesium ion 服务异常

### 现象
- 影像加载慢 / 部分黑块
- 出现 rate limit 警告

### 解决

1. **缓存**:Nginx 设长 expires
2. **替换底图**:用国内天地图 / ArcGIS 替代
3. **自托管**:下载 OSM 切片自建服务

```nginx
location /ion-tiles/ {
  proxy_pass https://assets.ion.cesium.com/;
  proxy_cache_valid 200 30d;
  add_header X-Cache-Status $upstream_cache_status;
  expires 30d;
}
```

---

## 9.10 浏览器兼容性

| 浏览器 | 支持情况 |
|---|---|
| Chrome / Edge | ✅ 最佳 |
| Firefox | ✅ 良好 |
| Safari | ✅ 良好(部分 glTF 扩展慢) |
| 移动 Chrome / Safari | ⚠️ 性能受限,必须开启 requestRenderMode |
| IE 11 | ❌ 不支持(WebGL 缺失) |

### WebGL 检测

```js
if (!window.WebGLRenderingContext) {
  alert('请使用支持 WebGL 的现代浏览器')
}
```

---

## 9.11 安全 / 信息泄露

### token 泄漏

```js
// ❌ 错:硬编码 token 在前端
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1...'

// ✅ 对:后端代理 + 注入
// 后端读环境变量 → 返回给前端 → 前端设置
```

### 私有数据暴露

3D Tiles 自托管时,**不要把没脱敏的数据放到公开 URL**。

```nginx
# 只允许内网访问
location /private-tiles/ {
  allow 10.0.0.0/8;
  deny all;
  alias /data/private/;
}
```

---

## 9.12 部署期陷阱

| 陷阱 | 解决 |
|---|---|
| 静态资源 404 | Nginx 路径配对 |
| HTTPS 下 HTTP 资源被拦截 | 全部 HTTPS 或 CORS |
| 浏览器 CSP 阻止 WebGL | `Content-Security-Policy: ... script-src 'self' 'unsafe-eval'` |
| 大文件 502 | Nginx `client_max_body_size 100m;` |
| 频繁 502 | 后端加缓存 + gzip |

---

## 9.13 紧急调试技巧

```js
// 1. 加载慢?看 Network 面板的瓦片请求
// 2. 不显示?强制 viewer.resize() / viewer.scene.requestRender()
// 3. 看 FPS / 几何数 / 纹理数
viewer.scene.primitives.add(new Cesium.PerformanceDisplay())

// 4. 看 Entity / Primitive 数量
console.log('Entities:', viewer.entities.values.length)
console.log('Primitives:', viewer.scene.primitives.length)

// 5. 拾取调试
viewer.scene.debugShowFramesPerSecond = true
// 配合 scene.pick(windowPos) 看返回值
```

---

## 下一步

- 回头看 `modules/05-performance-and-rendering.md` 加固
- 回头看 `modules/06-engineering.md` 检查构建配置
- 提交问题到 [Cesium 论坛](https://community.cesium.com/)