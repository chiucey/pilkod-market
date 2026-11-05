# Three.js 本地化部署指南(2026-07-07)

**回答用户问题**:Three.js 可以像 ECharts 一样本地化部署,有三种方式,**推荐方式 A 或 B**。

---

## 一、三种本地化方式

### 方式 A: Vite/Webpack 自动打包(**推荐**)

适用: 有 Node 环境 + 构建工具的项目

```bash
# 安装依赖
npm install three @react-three/fiber @react-three/drei

# 或 pnpm
pnpm add three @react-three/fiber @react-three/drei
```

```ts
// src/main.tsx
import * as THREE from 'three';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Box } from '@react-three/drei';

// 直接使用,Vite 会打包到 dist/
function ThreeScene() {
  return (
    <Canvas>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <Box position={[0, 0, 0]}>
        <meshStandardMaterial color="#4a7bb8" />
      </Box>
      <OrbitControls />
    </Canvas>
  );
}
```

**优势**:
- 零配置(装完即用)
- 自动 tree-shake(只打包用到的部分,通常 100-200 KB gzipped)
- HMR(热更新)开发体验好
- TypeScript 类型完美

**劣势**:
- 需要 Node 工具链(Vite/npm)
- 本技能 wind-dashboard.zip 是纯静态 HTML,需要构建后才能用方式 A

---

### 方式 B: 直接下载 three.module.js 到 assets/(纯静态项目)

适用: 没有 Node 环境,纯前端 HTML 项目

```bash
# 进入项目 assets 目录
cd wind-dashboard/assets

# 核心库(必装,~600KB)
curl -sSL "https://unpkg.com/three@0.160.0/build/three.module.js" -o three.module.js

# 可选:控件/加载器等扩展(按需,~5MB)
mkdir -p three-addons
curl -sSL "https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js" \
  -o three-addons/OrbitControls.js
curl -sSL "https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js" \
  -o three-addons/GLTFLoader.js
# ... 按需添加更多
```

然后在 HTML 里用 ES module import map:

```html
<!-- index.html -->
<script type="importmap">
{
  "imports": {
    "three": "./assets/three.module.js",
    "three/addons/": "./assets/three-addons/"
  }
}
</script>

<script type="module">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/OrbitControls.js';

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 1000);
  // ...
</script>
```

**优势**:
- 完全纯静态,跟 ECharts 一样本地
- 文件级可控(40+ MB,但都是 JS)
- 离线可用

**劣势**:
- 手动下载 + 维护更新
- 文件大(gzipped 后约 1-2 MB)
- importmap 在老浏览器不支持(Safari 16.4+, Chrome 89+)

---

### 方式 C: CDN(**本技能不推荐**)

```html
<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
```

**为什么不推荐**:跟 ECharts 硬性原则冲突 — CDN 被墙就 empty。前面踩过这个坑(用户反馈"empty"),不再犯。

---

## 二、本项目方式选择

本技能默认交付物 `wind-dashboard/` 是**纯静态 HTML** 项目,适合 **方式 B**(本地 assets)。

如果将来改成 Vite 构建的项目,迁移到方式 A。

---

## 三、方式 B 实操(pure-HTML 模式)

### 文件清单(完成 three 本地化)

```
wind-dashboard/
├── index.html
├── assets/
│   ├── echarts.min.js            # ECharts 核心 (1.0 MB)
│   ├── echarts-gl.min.js         # ECharts 3D (0.6 MB)
│   ├── china.json                # 中国地图 (0.6 MB)
│   ├── three.module.js           # Three.js 核心 (0.6 MB)  ← 新增
│   └── three-addons/             # ← 新增目录
│       ├── OrbitControls.js      # (2.3 KB)
│       ├── GLTFLoader.js         # (16 KB) - 加载 3D 模型
│       └── ...                   # 按需
└── js/
    └── three-scene.js            # ← 新增:用 THREE 渲染场景
```

**总大小**:加 three 后从 3.0 MB → ~4.5 MB(增加 ~1.5 MB)

### 完整 HTML 示例

```html
<!DOCTYPE html>
<html>
<head>
  <title>Three.js 本地化大屏</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>

<!-- ECharts 地图 -->
<div id="mapChart"></div>

<!-- Three.js 3D 场景层(浮在地图上) -->
<div id="threeOverlay"></div>

<!-- ECharts 本地 -->
<script src="assets/echarts.min.js"></script>

<!-- Three.js 本地 - 用 importmap -->
<script type="importmap">
{
  "imports": {
    "three": "./assets/three.module.js",
    "three/addons/": "./assets/three-addons/"
  }
}
</script>

<!-- Three.js 场景脚本 -->
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';

const container = document.getElementById('threeOverlay');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, container.clientWidth/container.clientHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshBasicMaterial({ color: 0x4a7bb8 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 5;
new OrbitControls(camera, renderer.domElement);

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
</script>

</body>
</html>
```

---

## 四、性能对比(本项目场景)

| 库 | gzipped | 首屏加载 | 适用范围 |
|---|---|---|---|
| ECharts | ~340 KB | 快 | 95% 数据可视化 |
| ECharts GL (map3D 模式) | ~210 KB | 中 | 伪 3D,数据可视化 |
| **Three.js 核心** | ~150 KB | **慢**(WebGL init) | 真 3D 场景 |
| **+ r3f + drei** | ~60 KB | - | React 封装 |

**结论**:Three.js 库本身不重,但 WebGL 初始化开销大,且**测试 / 截图 / 兼容性** 都更麻烦。除非真要"模型浏览 / 3D 场景",否则用 ECharts 3D 已够。

---

## 五、文件路径清单

| 资源 | URL | 大小 | 备注 |
|---|---|---|---|
| Three.js 核心 | https://unpkg.com/three@0.160.0/build/three.module.js | 600 KB | 必装 |
| OrbitControls | unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js | 2.3 KB | 鼠标交互 |
| GLTFLoader | .../loaders/GLTFLoader.js | 16 KB | 加载模型 |
| Stats.js | .../libs/stats.module.js | 4 KB | 性能监控 |
| EffectComposer | .../postprocessing/EffectComposer.js | 13 KB | 后处理 |

更多 examples/jsm/ 模块可在 unpkg 上按需下载。

---

## 六、Three.js 在大屏里的典型用法

### 1. 3D 地球替代中国地图
```js
// 创建地球
const sphere = new THREE.SphereGeometry(5, 64, 64);
const material = new THREE.MeshPhongMaterial({
    map: new THREE.TextureLoader().load('earth.jpg'),
    specularMap: new THREE.TextureLoader().load('earth-spec.jpg')
});
const earth = new THREE.Mesh(sphere, material);
scene.add(earth);

// 添加标注点
const pointGeo = new THREE.SphereGeometry(0.05, 16, 16);
const pointMat = new THREE.MeshBasicMaterial({ color: 0xff9a3c });
// 在地球表面加 16 个省份标注
```

### 2. 数据 3D 柱状图(代替 ECharts bar3D)
```js
// 每个省份一根柱子,高度 = 装机容量
provinces.forEach((p, i) => {
    const h = p.value / 5000;
    const geo = new THREE.BoxGeometry(0.5, h, 0.5);
    const mat = new THREE.MeshPhongMaterial({ color: 0x4a7bb8 });
    const bar = new THREE.Mesh(geo, mat);
    bar.position.set(...lngLat[i], h/2);
    scene.add(bar);
});
```

### 3. 粒子背景
```js
// 5000 个粒子缓慢漂浮,作为大屏背景
const particles = new THREE.Points(
    new THREE.BufferGeometry().setAttribute(
        'position', new THREE.Float32BufferAttribute([...5000 dots], 3)
    ),
    new THREE.PointsMaterial({ color: 0x8fbcff, size: 0.02, transparent: true, opacity: 0.6 })
);
scene.add(particles);
```

---

## 七、什么时候从 ECharts 切到 Three.js

决策清单(全部满足才考虑切):

1. ☐ 用户明确说"用 Three.js" 或"真 3D"
2. ☐ 视觉效果上 ECharts 真的做不到(如 GLTF 模型 / 复杂几何)
3. ☐ 目标用户用桌面端 Chrome / Safari,接受 WebGL
4. ☐ 已经穷尽 ECharts 3D 系列(map3D / bar3D / surface / scatter3D)都达不到效果
5. ☐ 有 2-3 周时间投入和性能优化

只要**任一**不满足,继续用 ECharts。