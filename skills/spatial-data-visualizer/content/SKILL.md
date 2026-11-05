---
name: spatial-data-visualizer
description: 空间数据在线地图可视化工具。当用户上传空间数据文件（Shapefile、GeoJSON、KML 等）并要求生成可视化地图、叠加到地图上展示、将地理数据转换为可交互的 HTML 地图时使用。触发关键词：shapefile, geojson, kml, 空间数据, 地图可视化, GIS, 上传地图, 可视化地理数据
---

# 空间数据可视化技能

将用户上传的空间数据（Shapefile、GeoJSON、KML）转换为可交互的在线地图可视化 HTML 页面。

## 工作流程

### 步骤 1：检测空间数据格式

检查用户提供的文件类型：

| 格式 | 扩展名 | 检测方式 |
|------|--------|----------|
| Shapefile | `.shp` + `.dbf` + `.prj` | 文件组存在 |
| GeoJSON | `.geojson` / `.json` | JSON 结构含 `type: FeatureCollection` |
| TopoJSON | `.topojson` | JSON 结构含 `type: Topology` |
| KML/KMZ | `.kml` / `.kmz` | XML 格式含 `<kml>` 标签 |

### 步骤 2：数据转换为标准格式

**如果输入是 Shapefile：**
1. 读取 `.shp` 文件获取几何数据
2. 读取 `.dbf` 文件获取属性数据
3. 读取 `.prj` 文件获取坐标系信息
4. 转换为 GeoJSON（默认 EPSG:4326 WGS84）

**如果输入是 KML/KMZ：**
1. 解析 XML 结构
2. 提取几何和样式信息
3. 转换为 GeoJSON

### 步骤 3：生成可视化 HTML

创建包含以下内容的 HTML 文件：
- Leaflet 地图引擎（CDN 加载）
- 内嵌 GeoJSON 数据
- 交互式区域显示（点击查看详情）
- 样式控制（颜色、透明度可调）
- 图例说明

### 步骤 4：输出和部署

1. 生成独立的 HTML 文件
2. 提供下载链接或直接部署
3. 返回在线访问 URL（如已部署）

## 执行命令

### 转换 Shapefile 为 GeoJSON

```bash
python scripts/shp2geojson.py <input.shp> [--output <output.geojson>] [--crs 4326]
```

### 生成可视化 HTML

```bash
python scripts/generate_map.py <data.geojson> [--title "地图标题"] [--output <output.html>]
```

### 一键转换+可视化

```bash
python scripts/spatial_visualizer.py <input_file> [--format auto] [--title "标题"]
```

## 数据格式要求

### GeoJSON 输入格式

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], ...]]
      },
      "properties": {
        "name": "区域名称",
        "id": "唯一标识"
      }
    }
  ]
}
```

### Shapefile 要求

- 必须包含：`.shp`, `.dbf`, `.prj`
- 可选：`shx`（提升读取速度）

## 输出说明

生成的 HTML 文件包含：
- 完整的交互式 Leaflet 地图
- 数据叠加层
- 点击交互（显示属性信息）
- 鼠标悬停高亮效果
- 颜色和透明度控制
- 区域筛选功能（如适用）

## 依赖项

脚本需要以下 Python 库：
- `geopandas` - Shapefile 读取
- `shapely` - 几何操作
- `fiona` - 文件格式支持

安装命令：
```bash
pip install geopandas shapely fiona
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 文件不存在 | 提示用户检查路径 |
| 不支持的格式 | 列出支持的格式列表 |
| 坐标系错误 | 尝试自动转换或提示指定目标坐标系 |
| 空数据集 | 提示检查数据内容 |

## 示例

**示例 1：上传 Shapefile**
```
用户：帮我把这个 shapefile 转成地图可视化
-> 检测到 .shp 文件
-> 转换为 GeoJSON
-> 生成 index.html
-> 返回可视化结果
```

**示例 2：直接提供 GeoJSON**
```
用户：这个 GeoJSON 数据帮我生成地图
-> 读取 GeoJSON
-> 检测边界范围
-> 生成可视化 HTML
-> 返回结果
```