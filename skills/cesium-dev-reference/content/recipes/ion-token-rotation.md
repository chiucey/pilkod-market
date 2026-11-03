---
recipe: ion-token-rotation
title: Cesium ion token 轮换 + 国内替代
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# Cesium ion Token 轮换 + 国内替代

> **何时用**:避免 token 硬编码、token 轮换策略、国内服务自托管。

## 一、为什么不能硬编码 token?

- ❌ token 在前端明文,任何人可见
- ❌ 多个项目用同一个 token,无法追踪用量
- ❌ 离职员工泄漏 token
- ✅ 后端代理 + 动态注入

## 二、后端代理方案(推荐)

### Node.js Express

```js
// server.js
app.get('/api/cesium-token', authenticate, (req, res) => {
  // 1. 验证用户身份
  // 2. 返回 token(可加 IP / 域名限制)
  res.json({ token: process.env.CESIUM_ION_TOKEN })
})

app.get('/api/cesium-token/refresh', authenticate, async (req, res) => {
  // 定期轮换 token
  const newToken = await rotateToken()
  res.json({ token: newToken })
})
```

### Python Flask

```python
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/api/cesium-token')
def get_token():
    # 实际生产应该验证用户身份
    return jsonify({
        'token': os.environ['CESIUM_ION_TOKEN'],
        'expires_at': '2026-12-31T23:59:59Z'
    })
```

## 三、前端注入

```js
// main.js
async function initCesium() {
  // 1. 获取 token
  const { token } = await fetch('/api/cesium-token').then(r => r.json())

  // 2. 设置 token
  Cesium.Ion.defaultAccessToken = token

  // 3. 创建 Viewer
  const viewer = new Cesium.Viewer('cesiumContainer', {
    terrain: Cesium.Terrain.fromWorldTerrain()
  })

  return viewer
}

initCesium()
```

## 四、Token 轮换策略

```js
// 前端定时刷新
async function setupTokenRotation(viewer) {
  // 每 30 分钟刷新一次
  setInterval(async () => {
    try {
      const { token } = await fetch('/api/cesium-token/refresh').then(r => r.json())
      Cesium.Ion.defaultAccessToken = token
      console.log('Token 已刷新')
    } catch (e) {
      console.error('Token 刷新失败', e)
    }
  }, 30 * 60 * 1000)
}

// 主动失效时刷新
viewer.scene.globe.tileLoadProgressEvent.addEventListener(remaining => {
  if (remaining === 0) {
    // 所有瓦片加载完,可以刷新一次
  }
})
```

## 五、按域名/IP 限制 token

```js
// 后端 middleware
function checkOrigin(req, res, next) {
  const allowed = ['https://your-app.com', 'https://staging.your-app.com']
  const origin = req.headers.origin || req.headers.referer
  if (allowed.includes(origin)) {
    next()
  } else {
    res.status(403).json({ error: 'Forbidden' })
  }
}
```

## 六、完全不用 Cesium ion 的方案

### 1. 自托管影像

```js
const viewer = new Cesium.Viewer('cesiumContainer', {
  baseLayer: Cesium.ImageryLayer.fromProviderAsync(
    Cesium.IonImageryProvider.fromAssetId(2)  // 不要这个
  )
})

// 替换为自托管
viewer.imageryLayers.removeAll()
viewer.imageryLayers.addImageryProvider(
  new Cesium.UrlTemplateImageryProvider({
    url: 'https://your-tile-server/{z}/{x}/{y}.png'
  })
)
```

### 2. 自托管地形

```js
// 不要用 Terrain.fromWorldTerrain()
// 改用自托管 quantized-mesh
const provider = await Cesium.CesiumTerrainProvider.fromUrl(
  'https://your-server/terrain/'
)
viewer.scene.setTerrain(new Cesium.Terrain(provider))
```

### 3. 不用 ion 资源(OSM Buildings 等)

```js
// ❌ 不要用
const buildingTileset = await Cesium.createOsmBuildingsAsync()

// ✅ 自建
const customTileset = await Cesium.Cesium3DTileset.fromUrl(
  'https://your-server/your-buildings/tileset.json'
)
viewer.scene.primitives.add(customTileset)
```

### 4. 国内替代清单

| Cesium ion | 国内替代 |
|---|---|
| Bing Maps Aerial | 天地图 / ArcGIS Online(中国) |
| Cesium World Terrain | 自主 DEM → quantized-mesh |
| OSM Buildings | 自建 3D Tiles |
| Google Photorealistic 3D Tiles | (无国内替代,Google 资源) |

## 七、CI/CD 中 token 管理

```yaml
# GitHub Actions 示例
env:
  CESIUM_ION_TOKEN: ${{ secrets.CESIUM_ION_TOKEN }}

jobs:
  build:
    steps:
      - name: Build
        run: |
          # 构建时 token 不进 bundle
          npm run build

      - name: Deploy
        run: |
          # 通过 Secrets Manager 注入到服务器
          aws ssm put-parameter --name "/cesium/token" --value "$CESIUM_ION_TOKEN" --type SecureString
```

## 八、监控用量

```js
// 后端定期查询 ion 用量
async function getIonUsage() {
  const response = await fetch('https://api.cesium.com/v1/usage', {
    headers: { 'Authorization': `Bearer ${process.env.CESIUM_ION_TOKEN}` }
  })
  return response.json()
}

// 定时检查
setInterval(async () => {
  const usage = await getIonUsage()
  if (usage.used > usage.limit * 0.8) {
    sendAlert(`Cesium ion 用量已达 ${(usage.used/usage.limit*100).toFixed(1)}%`)
  }
}, 60 * 60 * 1000)
```

## 九、错误兜底

```js
// token 失效时降级到无 token 模式
viewer.scene.renderError.addEventListener((scene, error) => {
  console.error('渲染错误:', error)
  if (error.message.includes('401')) {
    // token 失效,刷新
    refreshTokenAndReload()
  }
})

// ion 服务不可达时显示提示
Cesium.Resource.fetchImage = (function (original) {
  return async function (...args) {
    try {
      return await original.apply(this, args)
    } catch (e) {
      showOfflineTip('Cesium ion 服务不可达,部分瓦片可能无法加载')
      throw e
    }
  }
})(Cesium.Resource.fetchImage)
```

## 十、参考

- [Cesium ion Access Tokens](https://ion.cesium.com/tokens)
- [Cesium Forum: Token Management](https://community.cesium.com/)
- [recipes/custom-3dtiles.md](./custom-3dtiles.md) — 完整自托管 3D Tiles 服务