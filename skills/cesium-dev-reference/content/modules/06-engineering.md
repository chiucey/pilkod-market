---
module: 06
title: 工程化 — Vite/Webpack、Vue3/React、TypeScript、SSR、部署
cesium_version: 1.145+
last_verified: 2026-09-22
source_url: [https://github.com/CesiumGS/cesium-vite-example, https://github.com/CesiumGS/cesium-webpack-example]
status: stable
---

# 06 · 工程化

> **本模块覆盖**:构建工具(Vite/Webpack) / 框架绑定(Vue/React) / TypeScript / SSR / 微前端 / 部署。
> **何时加载**:脚手架选型 / 静态资源 404 / 框架集成 / WebGL 上下文泄漏 / 热重载失效。

---

## 6.1 构建工具选择

| 工具 | 推荐 | 备注 |
|---|---|---|
| **Vite** | ⭐⭐⭐ 首选 | 快、热重载快、社区插件多 |
| **Webpack** | ⭐⭐ 备选 | 官方有 example,生态成熟 |
| **Rspack** | ⭐⭐ Webpack 替代 | 兼容 Webpack 生态,快很多 |
| **Rollup** | ⭐ 库场景 | 不太适合应用开发 |

---

## 6.2 Vite 集成

### 推荐方案:`vite-plugin-cesium`

```bash
npm install cesium
npm install -D vite-plugin-cesium
```

```js
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import cesium from 'vite-plugin-cesium'

export default defineConfig({
  plugins: [vue(), cesium()]
})
```

### 备选方案:手动配置

```bash
npm install cesium
npm install -D vite-plugin-static-copy
```

```js
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteStaticCopy } from 'vite-plugin-static-copy'

export default defineConfig({
  plugins: [
    vue(),
    viteStaticCopy({
      targets: [
        { src: 'node_modules/cesium/Build/Cesium/Workers', dest: 'cesium' },
        { src: 'node_modules/cesium/Build/Cesium/ThirdParty', dest: 'cesium' },
        { src: 'node_modules/cesium/Build/Cesium/Assets', dest: 'cesium' },
        { src: 'node_modules/cesium/Build/Cesium/Widgets', dest: 'cesium' }
      ]
    })
  ]
})
```

```js
// main.js
window.CESIUM_BASE_URL = '/cesium/'
import 'cesium/Build/Cesium/Widgets/widgets.css'
```

### ⚠️ 1.114 以下版本

需要额外配置(`rollupOptions.external`):

```js
build: {
  rollupOptions: {
    external: ['http', 'https', 'url', 'zlib']
  }
}
```

参考:[cesium-vite-example](https://github.com/CesiumGS/cesium-vite-example)

---

## 6.3 Webpack 集成

```bash
npm install --save-dev copy-webpack-plugin webpack-cli
```

```js
// webpack.config.js
const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpack = require('webpack')

const cesiumSource = 'node_modules/cesium/Source'
const cesiumWorkers = '../Build/Cesium/Workers'

module.exports = {
  entry: { app: './src/index.js' },
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, 'dist'),
    sourcePrefix: ''
  },
  amd: { toUrlUndefined: true },  // 兼容 Cesium AMD
  resolve: {
    alias: { cesium: path.resolve(__dirname, cesiumSource) },
    mainFiles: ['module', 'main', 'Cesium']
  },
  module: {
    rules: [
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      { test: /\.(png|gif|jpg|jpeg|svg|xml|json)$/, use: ['url-loader'] }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({ template: 'src/index.html' }),
    new CopyWebpackPlugin({
      patterns: [
        { from: path.join(cesiumSource, cesiumWorkers), to: 'Workers' },
        { from: path.join(cesiumSource, 'Assets'), to: 'Assets' },
        { from: path.join(cesiumSource, 'Widgets'), to: 'Widgets' }
      ]
    }),
    new webpack.DefinePlugin({ CESIUM_BASE_URL: JSON.stringify('') })
  ]
}
```

---

## 6.4 Vue 3 集成

### 方案 1:vue-cesium(组件库)

```bash
npm install vue-cesium
```

```js
// main.ts
import { createApp } from 'vue'
import VueCesium from 'vue-cesium'
import 'vue-cesium/dist/index.css'

const app = createApp(App)
app.use(VueCesium, {
  cesiumPath: 'https://unpkg.com/cesium@1.124.0/Build/Cesium/Cesium.js',
  accessToken: 'your-ion-token'
})
```

```vue
<template>
  <vc-viewer :scene-mode="3" @ready="onReady">
    <vc-entity :position="position" :billboard="billboard"></vc-entity>
  </vc-viewer>
</template>
```

### 方案 2:手写 Composition(更可控)

```vue
<!-- CesiumViewer.vue -->
<template>
  <div ref="container" class="cesium-viewer"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'

const container = ref(null)
let viewer = null
const handlers = []

onMounted(() => {
  viewer = new Cesium.Viewer(container.value, {
    // 配置项
  })

  // 推荐:把 viewer 挂到全局变量(防 Vue 响应式劫持)
  window._cesiumViewer = viewer
})

onBeforeUnmount(() => {
  // 解绑所有 handler
  handlers.forEach(h => h.destroy())
  handlers.length = 0

  if (viewer && !viewer.isDestroyed()) {
    viewer.destroy()
  }
  viewer = null
  delete window._cesiumViewer
})

defineExpose({ viewer })
</script>

<style scoped>
.cesium-viewer {
  width: 100%;
  height: 100vh;
}
</style>
```

> ⚠️ **不要把 viewer 放进 Vue 的 ref() 或 reactive()** — Vue 的响应式 Proxy 会劫持所有属性读写,导致 FPS 暴跌。

---

## 6.5 React 集成

### resium(声明式)

```bash
npm install resium
```

```tsx
import { Viewer, Entity, PointGraphics } from 'resium'

function App() {
  return (
    <Viewer full>
      <Entity
        name="Tokyo"
        position={Cartesian3.fromDegrees(139.7670, 35.6814, 100)}
        point={{ pixelSize: 10, color: Color.RED }}
      />
    </Viewer>
  )
}
```

### 手写 Hook

```tsx
import { useEffect, useRef } from 'react'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'

export function useCesium(containerRef: React.RefObject<HTMLDivElement>) {
  const viewerRef = useRef<Cesium.Viewer | null>(null)

  useEffect(() => {
    if (!containerRef.current) return
    const viewer = new Cesium.Viewer(containerRef.current, {})
    viewerRef.current = viewer
    return () => {
      if (viewer && !viewer.isDestroyed()) viewer.destroy()
      viewerRef.current = null
    }
  }, [])

  return viewerRef
}
```

> ⚠️ **React StrictMode 双调用问题**:`useEffect` 在开发模式会运行两次。第一次创建的 viewer 要先 destroy 避免上下文泄漏。

---

## 6.6 TypeScript

```bash
npm install cesium  # 自带类型
```

```ts
import * as Cesium from 'cesium'

const position: Cesium.Cartesian3 = Cesium.Cartesian3.fromDegrees(116.4, 39.9)
const color: Cesium.Color = Cesium.Color.RED

// 自定义属性
interface DeviceProps {
  id: string
  status: 'normal' | 'warning' | 'error'
}

const entity = viewer.entities.add({
  position,
  point: { pixelSize: 10 },
  properties: {
    id: 'device-001',
    status: 'normal'
  } as DeviceProps
})

// 类型断言
const props = entity.properties as Cesium.PropertyBag<DeviceProps>
console.log(props.id.getValue())
```

> CesiumJS 从 1.108+ 起自带 TypeScript 类型(无需 `@types/cesium`)。

---

## 6.7 热重载(HMR)

### Vite 默认不需配置

Vite 默认 HMR 工作良好,Cesium viewer 实例在 HMR 时会被销毁重建。

### 防白屏技巧

```ts
// 开发环境挂全局,代码改动 viewer 不重建
if (import.meta.env.DEV) {
  // 把 viewer 挂到 window.__cesiumViewer
  ;(window as any).__cesiumViewer = viewer
}
```

但这有副作用(viewer 状态可能不一致),生产环境务必销毁。

---

## 6.8 SSR(服务端渲染)

**CesiumJS 不能 SSR**,只能在 client side 运行。

```ts
// Nuxt 3 / Next.js 等 SSR 框架:
if (process.client) {  // Nuxt 3
  const Cesium = await import('cesium')
}

// 或动态 import + ssr: false
definePageMeta({ ssr: false })
```

---

## 6.9 微前端(qiankun / micro-app)

### Cesium 单例问题

微前端场景下,每个子应用都可能引入 Cesium → 全局污染。

**解法**:
1. 把 Cesium 放到主应用(基座),子应用通过 props 传递 viewer
2. 子应用按需引入,且 CESIUM_BASE_URL 不能重复设置

### iframe 隔离(可选)

每个子应用 iframe,自管理 Cesium。缺点:viewer 间无法互通。

---

## 6.10 部署

### 静态托管

```bash
# 构建
npm run build

# 输出
dist/
├── index.html
├── assets/              # 你的 JS/CSS
└── cesium/              # Cesium 静态资源(Workers/Assets/Widgets/ThirdParty)
```

```nginx
# Nginx 配置(CORS + 缓存)
server {
  listen 80;
  root /var/www/cesium-app/dist;

  location / {
    try_files $uri $uri/ /index.html;
  }

  # 缓存静态资源
  location ~* \.(js|css|png|svg|woff|woff2|ttf)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # CORS(如果你的数据 API 在另一个域)
  location /api/ {
    add_header 'Access-Control-Allow-Origin' '*';
    proxy_pass http://api-server/;
  }

  # CORS for 3D Tiles 跨域(必需!)
  location /tiles/ {
    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
    alias /var/www/3dtiles-data/;
  }
}
```

> ⚠️ **3D Tiles 必须 CORS**!否则浏览器拒绝加载跨域瓦片。

### CDN 加载(更快)

```html
<script src="https://cdn.jsdelivr.net/npm/cesium@1.124.0/Build/Cesium/Cesium.js"></script>
<link href="https://cdn.jsdelivr.net/npm/cesium@1.124.0/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
```

---

## 6.11 移动端

```js
const viewer = new Cesium.Viewer('cesiumContainer', {
  // 移动端优化
  sceneModePicker: false,
  baseLayerPicker: false,
  geocoder: false,
  animation: false,
  timeline: false,
  homeButton: false,
  fullscreenButton: false,
  navigationHelpButton: false
})

// 性能开关
if (Cesium.FeatureDetection.isMobile()) {
  viewer.scene.maximumScreenSpaceError = 4    // 粗一点
  viewer.scene.requestRenderMode = true      // 必开
  viewer.scene.fog.density = 0.0002          // 远雾更强
}
```

---

## 下一步

- 典型场景 → `modules/07-typical-scenarios.md`
- 国产替代 → `modules/08-domestic-alternatives.md`
- 避雷清单 → `modules/09-pitfalls-and-traps.md`