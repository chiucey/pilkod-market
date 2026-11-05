#!/usr/bin/env python3
"""
空间数据可视化主脚本
将 Shapefile/GeoJSON/KML 转换为可交互的在线地图 HTML

用法:
    python spatial_visualizer.py <input_file> [--format auto] [--title "标题"] [--output <output.html>]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# 尝试导入地理数据处理库
try:
    import geopandas as gpd
    from shapely.geometry import mapping
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

try:
    from fastkml import kml
    import xml.etree.ElementTree as ET
    HAS_FASTKML = True
except ImportError:
    HAS_FASTKML = False


class SpatialDataVisualizer:
    """空间数据可视化器"""

    SUPPORTED_FORMATS = {
        '.shp': 'shapefile',
        '.geojson': 'geojson',
        '.json': 'geojson',
        '.kml': 'kml',
        '.kmz': 'kmz',
        '.topojson': 'topojson'
    }

    def __init__(self, input_path: str, title: str = "空间数据可视化"):
        self.input_path = Path(input_path)
        self.title = title
        self.geojson_data = None
        self.bounds = None

    def detect_format(self) -> str:
        """检测文件格式"""
        ext = self.input_path.suffix.lower()
        format_type = self.SUPPORTED_FORMATS.get(ext, 'unknown')

        if format_type == 'unknown':
            if self.input_path.exists():
                with open(self.input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)
                    if '"type"' in content and 'Feature' in content:
                        return 'geojson'
                    elif '<kml' in content.lower():
                        return 'kml'

        return format_type

    def read_shapefile(self) -> Optional[Dict]:
        """读取 Shapefile 并转换为 GeoJSON"""
        if not HAS_GEOPANDAS:
            print("错误: 需要安装 geopandas 才能处理 Shapefile")
            print("运行: pip install geopandas shapely fiona")
            return None

        try:
            gdf = gpd.read_file(str(self.input_path))

            if gdf.crs and gdf.crs.to_epsg() != 4326:
                print(f"转换坐标系: {gdf.crs.to_epsg()} -> 4326 (WGS84)")
                gdf = gdf.to_crs(epsg=4326)

            features = []
            for idx, row in gdf.iterrows():
                feature = {
                    'type': 'Feature',
                    'geometry': mapping(row.geometry),
                    'properties': {k: str(v) if v is not None else '' for k, v in row.items() if k != 'geometry'}
                }
                features.append(feature)

            return {
                'type': 'FeatureCollection',
                'features': features
            }

        except Exception as e:
            print(f"读取 Shapefile 失败: {e}")
            return None

    def read_geojson(self) -> Optional[Dict]:
        """读取 GeoJSON 文件"""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('type') == 'FeatureCollection':
                return data
            elif data.get('type') == 'Feature':
                return {'type': 'FeatureCollection', 'features': [data]}
            else:
                return {'type': 'FeatureCollection', 'features': data.get('features', [])}

        except Exception as e:
            print(f"读取 GeoJSON 失败: {e}")
            return None

    def read_kml(self) -> Optional[Dict]:
        """读取 KML 文件并转换为 GeoJSON"""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            features = []

            root = ET.fromstring(content)

            for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
                name_elem = placemark.find('{http://www.opengis.net/kml/2.2}name')
                name = name_elem.text if name_elem is not None else 'Unknown'

                for geom_type in ['Point', 'LineString', 'Polygon', 'MultiGeometry']:
                    geom_elem = placemark.find('{http://www.opengis.net/kml/2.2}' + geom_type)
                    if geom_elem is not None:
                        coords = self._parse_kml_geometry(geom_elem)
                        if coords:
                            geo_type = geom_type.lower()
                            if geo_type == 'multigeometry':
                                geo_type = 'geometrycollection'
                            features.append({
                                'type': 'Feature',
                                'geometry': {'type': geo_type, 'coordinates': coords},
                                'properties': {'name': name}
                            })
                            break

            return {'type': 'FeatureCollection', 'features': features}

        except Exception as e:
            print(f"读取 KML 失败: {e}")
            return None

    def _parse_kml_geometry(self, geom_elem) -> Any:
        """解析 KML 几何元素"""
        try:
            coord_elem = geom_elem.find('{http://www.opengis.net/kml/2.2}coordinates')
            if coord_elem is not None and coord_elem.text:
                coords_str = coord_elem.text.strip()
                coords_list = []
                for coord in coords_str.split():
                    parts = coord.split(',')
                    if len(parts) >= 2:
                        lng = float(parts[0])
                        lat = float(parts[1])
                        coords_list.append([lng, lat])

                if geom_elem.tag.endswith('Point'):
                    return coords_list[0] if coords_list else[]
                elif geom_elem.tag.endswith('LineString'):
                    return coords_list
                elif geom_elem.tag.endswith('Polygon'):
                    outer = geom_elem.find('.//{http://www.opengis.net/kml/2.2}outerBoundaryIs')
                    if outer is not None:
                        outer_coords = outer.find('.//{http://www.opengis.net/kml/2.2}coordinates')
                        if outer_coords is not None:
                            return [coords_list]
                    return [coords_list]

            return None
        except:
            return None

    def load_data(self, format_type: str = 'auto') -> bool:
        """加载空间数据"""
        if format_type == 'auto':
            format_type = self.detect_format()

        print(f"检测格式: {format_type}")

        if format_type == 'shapefile':
            self.geojson_data = self.read_shapefile()
        elif format_type == 'geojson':
            self.geojson_data = self.read_geojson()
        elif format_type == 'kml':
            self.geojson_data = self.read_kml()
        else:
            print(f"不支持的格式: {format_type}")
            return False

        if self.geojson_data:
            print(f"成功加载 {len(self.geojson_data.get('features', []))} 个要素")
            self._calculate_bounds()
            return True

        return False

    def _calculate_bounds(self):
        """计算数据边界"""
        if not self.geojson_data:
            return

        features = self.geojson_data.get('features', [])
        if not features:
            return

        lats = []
        lngs = []

        for feature in features:
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [])

            def flatten_coords(c):
                if isinstance(c[0], (list, tuple)):
                    for item in c:
                        flatten_coords(item)
                else:
                    lngs.append(c[0])
                    lats.append(c[1])

            flatten_coords(coords)

        if lats and lngs:
            self.bounds = {
                'min_lng': min(lngs),
                'max_lng': max(lngs),
                'min_lat': min(lats),
                'max_lat': max(lats),
                'center_lat': (min(lats) + max(lats)) / 2,
                'center_lng': (min(lngs) + max(lngs)) / 2
            }

    def generate_html(self, output_path: Optional[str] = None) -> str:
        """生成可视化 HTML"""

        if not self.geojson_data:
            raise ValueError("请先加载数据")

        if output_path:
            output_path = Path(output_path)
        else:
            output_path = self.input_path.with_suffix('.html')

        geojson_str = json.dumps(self.geojson_data, ensure_ascii=False)

        center_lat = self.bounds['center_lat'] if self.bounds else 40.0
        center_lng = self.bounds['center_lng'] if self.bounds else -74.0

        feature_count = len(self.geojson_data.get('features', []))

        # 使用普通字符串模板，避免 f-string 中的 JavaScript 语法冲突
        html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>''' + self.title + '''</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f6fa; }

    #header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    #header h1 { font-size: 20px; font-weight: 600; }
    #header p { font-size: 13px; opacity: 0.9; margin-top: 4px; }

    #map { height: calc(100vh - 70px); width: 100%; }

    .info-box {
      position: absolute;
      top: 80px; right: 10px;
      z-index: 1000;
      background: rgba(255,255,255,0.97);
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      min-width: 280px;
      max-width: 350px;
      font-size: 13px;
      max-height: 400px;
      overflow-y: auto;
    }
    .info-box h3 { font-size: 16px; margin-bottom: 8px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 8px; }
    .info-box .prop { margin: 6px 0; padding: 4px 0; border-bottom: 1px solid #eee; display: flex; }
    .info-box .prop-label { font-weight: 600; color: #666; min-width: 100px; }
    .info-box .prop-value { color: #333; flex: 1; word-break: break-all; }

    .controls {
      position: absolute;
      top: 80px; left: 10px;
      z-index: 1000;
      background: rgba(255,255,255,0.97);
      padding: 14px 16px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.12);
      min-width: 180px;
    }
    .controls h4 { margin-bottom: 10px; font-size: 13px; color: #666; border-bottom: 1px solid #eee; padding-bottom: 6px; }
    .controls label { display: block; margin: 8px 0; font-size: 12px; color: #555; }
    .controls label span { display: inline-block; width: 70px; }
    .controls input[type="color"] { width: 60px; height: 28px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
    .controls input[type="range"] { width: 100px; vertical-align: middle; }

    .legend {
      position: absolute;
      bottom: 20px; right: 10px;
      z-index: 1000;
      background: rgba(255,255,255,0.97);
      padding: 14px 18px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.12);
      font-size: 12px;
      max-width: 200px;
    }
    .legend h4 { margin-bottom: 10px; color: #333; }
    .legend-item { display: flex; align-items: center; margin: 6px 0; }
    .legend-color { width: 20px; height: 14px; border-radius: 3px; margin-right: 10px; border: 1px solid rgba(0,0,0,0.1); }
  </style>
</head>
<body>

<div id="header">
  <div>
    <h1>''' + self.title + '''</h1>
    <p>空间数据可视化 | 共 ''' + str(feature_count) + ''' 个要素</p>
  </div>
</div>

<div id="map"></div>

<div class="controls" id="controls">
  <h4>样式控制</h4>
  <label><span>填充颜色</span><input type="color" id="fillColor" value="#e74c3c" /></label>
  <label><span>边界颜色</span><input type="color" id="strokeColor" value="#3388ff" /></label>
  <label><span>透明度</span><input type="range" id="fillOpacity" min="0" max="1" step="0.1" value="0.5" /></label>
  <label><span>边界宽度</span><input type="range" id="strokeWeight" min="1" max="5" step="0.5" value="2" /></label>
</div>

<div class="info-box" id="info-box">
  <h3>要素信息</h3>
  <p style="color:#888;">点击地图上的区域查看详细信息</p>
  <p style="margin-top:10px;">共加载 ''' + str(feature_count) + ''' 个要素</p>
</div>

<div class="legend" id="legend">
  <h4>图例</h4>
  <div class="legend-item"><div class="legend-color" style="background:#e74c3c" id="legendColor"></div> 数据区域</div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  // 空间数据
  const GEOJSON_DATA = ''' + geojson_str + ''';

  // 初始化地图
  const map = L.map('map').setView([''' + str(center_lat) + ''', ''' + str(center_lng) + '''], 11);

  // 添加底图
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap, © CARTO',
    maxZoom: 19
  }).addTo(map);

  // 当前样式
  let currentStyle = {
    color: '#3388ff',
    weight: 2,
    fillColor: '#e74c3c',
    fillOpacity: 0.5
  };

  // 创建 GeoJSON 图层
  const geoLayer = L.geoJSON(GEOJSON_DATA, {
    style: function() { return Object.assign({}, currentStyle); },
    onEachFeature: function(feature, layer) {
      layer.on('click', function() { showInfo(feature); });
      layer.on('mouseover', function() {
        layer.setStyle({
          weight: currentStyle.weight + 2,
          fillOpacity: Math.min(currentStyle.fillOpacity + 0.2, 1)
        });
      });
      layer.on('mouseout', function() {
        geoLayer.resetStyle(layer);
      });
    }
  }).addTo(map);

  // 适应边界
  map.fitBounds(geoLayer.getBounds(), { padding: [30, 30] });

  // 显示信息
  function showInfo(feature) {
    const props = feature.properties || {};
    let html = '<h3>要素信息</h3>';
    for (const key in props) {
      const value = props[key];
      if (value !== null && value !== undefined) {
        html += '<div class="prop"><span class="prop-label">' + key + ':</span><span class="prop-value">' + value + '</span></div>';
      }
    }
    document.getElementById('info-box').innerHTML = html;
  }

  // 样式控制
  document.getElementById('fillColor').addEventListener('input', function(e) {
    currentStyle.fillColor = e.target.value;
    geoLayer.setStyle(currentStyle);
    document.getElementById('legendColor').style.background = e.target.value;
  });

  document.getElementById('strokeColor').addEventListener('input', function(e) {
    currentStyle.color = e.target.value;
    geoLayer.setStyle(currentStyle);
  });

  document.getElementById('fillOpacity').addEventListener('input', function(e) {
    currentStyle.fillOpacity = parseFloat(e.target.value);
    geoLayer.setStyle(currentStyle);
  });

  document.getElementById('strokeWeight').addEventListener('input', function(e) {
    currentStyle.weight = parseFloat(e.target.value);
    geoLayer.setStyle(currentStyle);
  });
</script>
</body>
</html>'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML 可视化文件已生成: {output_path}")
        return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='空间数据可视化工具 - 将 Shapefile/GeoJSON/KML 转换为交互式地图'
    )
    parser.add_argument('input', help='输入文件路径 (.shp, .geojson, .kml 等)')
    parser.add_argument('-o', '--output', help='输出 HTML 文件路径')
    parser.add_argument('-t', '--title', default='空间数据可视化', help='页面标题')
    parser.add_argument('-f', '--format', choices=['auto', 'shapefile', 'geojson', 'kml'],
                        default='auto', help='输入文件格式')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"错误: 文件不存在 {args.input}")
        sys.exit(1)

    visualizer = SpatialDataVisualizer(args.input, args.title)

    if not visualizer.load_data(args.format):
        print("数据加载失败")
        sys.exit(1)

    output = visualizer.generate_html(args.output)
    print(f"完成! 输出文件: {output}")


if __name__ == '__main__':
    main()