# 图像生成提示词模板

## 风格1：铅笔素描风格

```
Convert this industrial equipment assembly drawing into a detailed pencil sketch style illustration. Remove all dimensions, annotations, nozzle labels, leader lines, and measurement markings. Keep only the main structure of the vessel with its cylindrical body, flanged sections, elliptical heads, internal components, nozzles, and manways. Apply paper texture effect with visible paper grain. Add pencil shading strokes and hatching for depth. Create realistic pencil drawing appearance with visible pencil strokes, smudged areas, and hand-drawn quality. White/cream paper background.
```

## 风格2：三维渲染剖面图

```
Convert this industrial equipment assembly drawing into a professional 3D rendered cross-section view (cutaway view). Remove all dimensions, annotations, nozzle labels, leader lines, and measurement markings. Show the internal structure of the vertical vessel with multiple sections, flanged connections, elliptical heads, internal tray/distributor plates, heat exchange coils, manways on the sides, and nozzles. Pure white background. Professional CAD rendering style with clean materials, subtle metallic gray tones, and precise engineering visualization. High quality 3D rendering effect.
```

## 风格3：三维渲染效果图

```
Convert this industrial equipment assembly drawing into a professional 3D rendered exterior view. Remove all dimensions, annotations, nozzle labels, leader lines, and measurement markings. Show the complete external appearance of the vertical pressure vessel with multiple flanged sections, elliptical heads at top and bottom, external nozzles and connections, manways with covers, lifting lugs, support brackets, and all visible attachments. Pure white background. Professional 3D product rendering style with clean materials, subtle metallic gray/steel tones, soft shadows, and photorealistic quality. High-end engineering visualization.
```

## 提示词调整指南

### 针对不同设备类型

| 设备类型 | 关键特征描述 |
|---------|-------------|
| 压力容器/塔器 | 筒体、法兰连接、封头、内件、裙座 |
| 反应釜 | 搅拌轴、夹套、换热元件、人孔 |
| 换热器 | 管束、管板、壳程、封头、接管 |
| 储罐 | 罐体、支座、人孔、清扫孔 |
| 管道系统 | 直管段、弯头、法兰、阀门 |

### 风格参数调整

| 风格 | 背景色 | 材质感 | 阴影 |
|-----|-------|-------|-----|
| 铅笔素描 | 白色/米色纸张 | 手绘质感 | 铅笔阴影排线 |
| 3D剖面图 | 纯白 | 金属灰 | 柔和边缘阴影 |
| 3D效果图 | 纯白 | 光滑金属 | 软阴影、反射 |

## 常见问题处理

1. **标注未完全去除**：增强提示词中"Remove all annotations"的强调
2. **结构变形**：减少复合提示词中的风格描述
3. **背景不纯**：明确指定"pure white background"
4. **比例失调**：保持原始图像宽高比
