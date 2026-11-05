# 空间数据可视化 - 参考文档

## 支持的空间数据格式

### 1. Shapefile (.shp)

ESRI Shapefile 是最常用的地理空间数据格式。

**必需文件：**
- `.shp` - 几何数据
- `.dbf` - 属性数据
- `.prj` - 坐标系定义

**可选文件：**
- `.shx` - 索引文件（提升读取速度）
- `.cpg` - 编码文件

**处理说明：**
- 脚本会自动检测坐标系并转换到 WGS84 (EPSG:4326)
- 支持点、线、面等多种几何类型
- 属性数据会自动保留

### 2. GeoJSON (.geojson / .json)

基于 JSON 的地理空间数据格式。

**标准格式：**
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
        "value": 100
      }
    }
  ]
}
```

**支持的几何类型：**
- Point（点）
- LineString（线）
- Polygon（面）
- MultiPoint（多点）
- MultiLineString（多线）
- MultiPolygon（多面）
- GeometryCollection（几何集合）

### 3. KML/KMZ (.kml / .kmz)

Google Earth 使用的水球格式。

**注意：** KMZ 是压缩格式，需要先解压。

**处理说明：**
- 提取 Placemark 元素的名称和几何
- 目前仅支持 Point、LineString、Polygon
- 样式信息会被忽略

### 4. TopoJSON (.topojson)

GeoJSON 的拓扑优化格式。

**特点：**
- 共享边界只存储一次
- 文件更小
- 支持对象合并

**转换说明：** 转换为标准 GeoJSON 时会展开为独立要素。

## 坐标系转换

脚本自动处理以下常用坐标系统：

| EPSG | 名称 | 说明 |
|------|------|------|
| 4326 | WGS84 | 默认输出坐标系 |
| 3857 | Web Mercator | Web 地图常用 |
| 2263 | NAD83 / NY State Plane | 纽约州平面坐标系 |
| 26918 | UTM Zone 18N | UTM 坐标系 |

**手动指定目标坐标系：**
```bash
python spatial_visualizer.py input.shp --crs 3857
```

## HTML 输出说明

生成的 HTML 文件包含以下功能：

### 地图功能
- Leaflet 交互式地图
- CARTO Light 底图
- 自动边界适应
- 缩放/平移控制

### 数据叠加
- GeoJSON 矢量图层
- 点击查看属性信息
- 鼠标悬停高亮

### 样式控制
- 填充颜色（color picker）
- 边界颜色（color picker）
- 透明度（range slider）
- 边界宽度（range slider）

### 交互信息框
- 显示要素所有属性
- 点击交互更新内容

## 依赖安装

```bash
# 基础依赖
pip install geopandas shapely fiona

# 可选：KML 解析
pip install fastkml

# 验证安装
python -c "import geopandas; print('GeoPandas OK')"
```

## 故障排除

### 问题：ImportError: No module named 'geopandas'

**解决：**
```bash
pip install geopandas
```

### 问题：Shapefile 读取失败

**检查：**
1. 文件是否存在
2. 是否包含必需文件（.shp, .dbf, .prj）
3. 文件名是否包含中文或特殊字符

### 问题：地图显示空白

**检查：**
1. GeoJSON 坐标是否为 [经度, 纬度] 顺序
2. 坐标范围是否合理（经度 -180~180，纬度 -90~90）
3. 数据是否为空

### 问题：坐标偏移

**解决：**
1. 检查原始数据的坐标系
2. 使用 `--crs` 参数指定正确的目标坐标系
3. 对于 Web Meractor (EPSG:3857) 数据，Leaflet 会自动处理

## 使用示例

### 示例 1：转换 Shapefile

```bash
python scripts/spatial_visualizer.py "path/to/data.shp" --title "我的地图"
```

输出：
- data.geo.json
- data.html

### 示例 2：处理 GeoJSON

```bash
python scripts/spatial_visualizer.py "path/to/data.geojson" --title "北京区域"
```

### 示例 3：批量处理

```bash
for f in *.shp; do
    python scripts/spatial_visualizer.py "$f"
done
```