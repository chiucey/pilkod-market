---
recipe: custom-3dtiles
title: 自定义 3D Tiles 服务搭建
cesium_version: 1.145+
last_verified: 2026-09-22
status: stable
---

# 自定义 3D Tiles 服务

> **何时用**:不想用 Cesium ion(数据敏感、计费、限速)、需要私有化部署。

## 一、数据准备

### 倾斜摄影(OSGB → 3D Tiles)

```bash
# 方案 A:CesiumLab(国产,闭源,简单)
# 拖入 OSGB 文件 → 自动转 3D Tiles → 导出
# 输出目录:
/output/tileset.json
/output/Tile_+000_+000_L23.b3dm   # 或 .glb (1.1)
/output/... (多个瓦片)

# 方案 B:v3dtiles(开源)
git clone https://github.com/Leopard-C/v3dtiles-release
# GUI / CLI 两种方式
```

### 点云(LAS → 3D Tiles)

```bash
# py3dtiles(开源,多核并行)
pip install py3dtiles
py3dtiles convert --files input.las --out output/
```

### BIM(IFC → 3D Tiles)

```bash
# py3dtilers
pip install py3dtilers[ifc]
python -m py3dtilers.CityTiler --files building.ifc --out output_tiles
```

### 单模型(glTF → 3D Tiles)

```bash
# gltf-pipeline(优化)
npx gltf-pipeline -i model.gltf -o model.glb -d   # Draco 压缩

# gltf-to-3d-tiles
gltf-to-3d-tiles -i model.glb -o output/
```

## 二、文件结构

```
/var/www/3dtiles/my-building/
├── tileset.json                  # 入口清单(必需)
├── Tile_+000_+000/
│   ├── Tile_+000_+000_L0.glb     # 1.1 风格(直接 glTF)
│   └── ...
└── Tile_+000_+001/
    └── Tile_+000_+001_L0.glb
```

## 三、Nginx 配置(CORS + 缓存)

```nginx
server {
  listen 80;
  server_name tiles.example.com;

  # CORS 必需!
  location / {
    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'Content-Type';
    
    root /var/www/3dtiles;
    
    # 长缓存(瓦片内容不变)
    location ~* \.(b3dm|i3dm|pnts|glb|gltf|json)$ {
      expires 7d;
      add_header Cache-Control "public";
      add_header 'Access-Control-Allow-Origin' '*';
    }
  }
}
```

## 四、加载到 CesiumJS

```js
const tileset = await Cesium.Cesium3DTileset.fromUrl(
  'https://tiles.example.com/my-building/tileset.json',
  {
    // 性能参数
    maximumScreenSpaceError: 16,    // 默认 16,精细场景调到 4~8
    maximumMemoryUsage: 1024,        // MB 上限
    skipLevelOfDetail: true,         // 跳过中间 LOD
    cullWithChildrenBounds: true,    // 子节点剔除
    loadSiblings: false,             // 不加载兄弟节点
    dynamicScreenSpaceError: false,  // 是否动态 SSE
    
    // 可选:服务端 URL 模板(如果 tileset 用了占位符)
    // urlSchemeFunction: ...
  }
)

viewer.scene.primitives.add(tileset)

// 加载完成
tileset.readyPromise.then(t => {
  console.log('瓦片集加载完成')
  console.log('包围球:', t.root.boundingSphere)
  viewer.flyTo(t)
})

// 加载进度
tileset.loadProgress.addEventListener(remaining => {
  console.log(`剩余 ${remaining} 个瓦片待加载`)
})

// 样式
tileset.style = new Cesium.Cesium3DTileStyle({
  color: 'color("#FF6B6B")',
  show: '${feature["type"]} === "building"',
  pointSize: 5
})
```

## 五、几何变换

```js
// 局部坐标 → 经纬度(常见于 BIM 模型)
const transform = Cesium.Matrix4.fromArray([
  // 4x4 变换矩阵
])
tileset.modelMatrix = transform
```

## 六、3D Tiles 1.1 新特性利用

```js
// 隐式平铺
const tileset = await Cesium.Cesium3DTileset.fromUrl(url)
// 1.1 自动支持隐式平铺(无需额外配置)

// EXT_mesh_features(单 mesh 携带 feature ID)
viewer.screenSpaceEventHandler.setInputAction(event => {
  const picked = viewer.scene.pick(event.position)
  if (picked instanceof Cesium.Cesium3DTileFeature) {
    // 通过 mesh_features 扩展读取 feature
    console.log('Feature ID:', picked.featureId)
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK)
```

## 七、性能监控

```js
// 内存监控
setInterval(() => {
  console.log(`瓦片数: ${tileset._selectedTiles.length}`)
  console.log(`加载队列: ${tileset._workerList.length}`)
}, 5000)
```

## 八、Cesium ion 替代方案

| 需求 | 替代 |
|---|---|
| 全球影像 | 自己切片 OSM / 天地图 |
| 全球地形 | 自建 quantized-mesh(CTB 工具) |
| OSM Buildings | 自建 3D Tiles |
| 全球 3D 实景 | Google Photorealistic 3D Tiles(需 token) |

## 九、常见问题

| 问题 | 解决 |
|---|---|
| 瓦片加载不全 | 检查 CORS、Nginx 配置 |
| 加载慢 | 调大 maximumScreenSpaceError |
| 内存爆 | 设 maximumMemoryUsage |
| 模型位置错 | 检查 tileset.json 的 transform |
| 1.1 隐式平铺不识别 | 确认 CesiumJS >= 1.106 |

## 十、安全

```nginx
# 只允许内网访问
location /private-tiles/ {
  allow 10.0.0.0/8;
  allow 172.16.0.0/12;
  deny all;
}
```

> ⚠️ **不要把没脱敏的私有 3D Tiles 放到公开 URL**。CesiumJS 加载时所有瓦片路径在前端可见。