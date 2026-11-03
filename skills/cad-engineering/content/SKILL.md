---
name: cad-engineering
description: CAD工程专家技能，提供CAD系统、文件格式、转换技术和CAD平台互操作性的专业指导。适用于CAD软件选择、DWG/DXF/STEP/IGES等格式转换、PDF转CAD、技术制图分析、3D建模等场景。
---

# CAD工程技能

提供计算机辅助设计(CAD)系统、文件格式、转换技术以及CAD平台间互操作性的专业指导。

## 适用场景

- CAD软件选择与使用指导
- 文件格式转换 (DWG, DXF, STEP, IGES等)
- PDF转CAD转换策略
- 技术制图分析
- 3D建模方法
- 开源与商业CAD系统选择
- CAD自动化与脚本编写
- 跨平台互操作性

## 开源CAD软件专业知识

| 软件 | 功能特点 |
|------|----------|
| **FreeCAD** | 参数化3D建模、Python脚本、工作台定制 |
| **LibreCAD** | 2D制图、DXF/DWG处理、命令行操作 |
| **OpenSCAD** | 编程式3D建模、CSG运算、参数化设计 |
| **QCAD** | 专业2D CAD、脚本接口、批处理 |
| **BRL-CAD** | 实体建模、光线追踪、几何分析 |
| **Blender** | CAD集成、网格转实体、技术可视化 |
| **KiCAD** | PCB设计、电气原理图、3D电路板可视化 |

## 商业CAD软件专业知识

| 软件 | 功能特点 |
|------|----------|
| **AutoCAD** | 完整命令集、AutoLISP/VBA自动化、自定义工具 |
| **SolidWorks** | 特征建模、API编程、PDM集成 |
| **CATIA** | V5/V6平台、复杂曲面、PLM工作流 |
| **Inventor** | 参数化设计、iLogic规则、Vault集成 |
| **Fusion 360** | 云协作、生成式设计、CAM集成 |
| **Creo/Pro-E** | 高级装配、机构设计 |
| **NX** | 高端制造、同步建模技术 |

## 文件格式专业知识

| 类别 | 格式 |
|------|------|
| **原生格式** | DWG, DXF, DGN, IGES, STEP, STL, SAT, Parasolid |
| **交换格式** | IFC, COLLADA, OBJ, FBX, 3DS, VRML, X3D |
| **文档格式** | PDF, SVG, EPS, DWF, 3D PDF |

## PDF转CAD转换

### 转换策略选择

1. **矢量PDF**: 直接矢量提取
2. **扫描图纸**: OCR和矢量化
3. **混合内容**: 混合处理方法
4. **复杂情况**: 手动重建

### 转换工具

| 类别 | 工具 |
|------|------|
| **商业工具** | AutoDWG, AnyDWG, Print2CAD, Scan2CAD, pdf2cad |
| **开源工具** | Inkscape+pstoedit, potrace, autotrace, pdf2dxf |
| **程序库** | OpenCV, Tesseract OCR, CADLib, LibreDWG, TeighaFile |
| **云服务** | Zamzar, CloudConvert, CAD Exchanger |
| **AI/ML工具** | 深度学习图纸识别、神经网络矢量化 |

### PDF分析工作流

```python
from digitalmodel.agents.cad import PDFAnalyzer

# 分析PDF类型
analyzer = PDFAnalyzer()
analysis = analyzer.analyze("drawing.pdf")

print(f"PDF类型: {analysis['type']}")  # vector/raster/hybrid
print(f"创建方法: {analysis['creation_method']}")
print(f"嵌入字体: {analysis['fonts']}")
print(f"图层信息: {analysis['layers']}")
print(f"比例检测: {analysis['detected_scale']}")

# 获取转换建议
recommendation = analyzer.recommend_conversion()
print(f"推荐工具: {recommendation['tool']}")
print(f"预期精度: {recommendation['accuracy']}")
print(f"需要手动清理: {recommendation['cleanup_required']}")
```

### 转换质量优化

```python
from digitalmodel.agents.cad import CADConverter

converter = CADConverter()

# 扫描PDF预处理
converter.preprocess(
    input_file="scanned_drawing.pdf",
    operations=[
        "denoise",      # 降噪
        "deskew",       # 校正倾斜
        "contrast_enhance"  # 增强对比度
    ]
)

# 带参数调优的矢量化
result = converter.convert(
    input_file="scanned_drawing.pdf",
    output_file="drawing.dxf",
    options={
        "line_tolerance": 0.5,
        "arc_detection": True,
        "text_recognition": True,
        "dimension_extraction": True
    }
)

# 后处理清理
converter.postprocess(
    file="drawing.dxf",
    operations=[
        "remove_duplicates",    # 删除重复
        "close_gaps",           # 闭合间隙
        "standardize_layers"    # 标准化图层
    ]
)
```

## 格式转换示例

### STEP转DXF

```python
from digitalmodel.agents.cad import FormatConverter

converter = FormatConverter()

# 带投影的STEP转DXF
result = converter.convert(
    input_file="model.step",
    output_file="drawing.dxf",
    projection="front",  # top, front, right, isometric
    scale=1.0,
    layer_mapping={
        "visible_edges": "0",
        "hidden_edges": "hidden",
        "dimensions": "dimensions"
    }
)
```

### DWG版本转换

```python
# 不同DWG版本间转换
result = converter.convert(
    input_file="drawing_2024.dwg",
    output_file="drawing_2010.dwg",
    target_version="2010"  # 用于兼容性
)
```

### 批量格式转换

```python
from digitalmodel.agents.cad import BatchConverter

batch = BatchConverter()

# 将所有STEP文件转换为IGES
results = batch.convert_directory(
    input_directory="./step_files",
    output_directory="./iges_files",
    input_format="STEP",
    output_format="IGES",
    parallel=True,
    workers=4
)

# 生成转换报告
batch.generate_report(results, "conversion_report.html")
```

## 技术制图分析

```python
from digitalmodel.agents.cad import DrawingAnalyzer

analyzer = DrawingAnalyzer()

# 分析技术图纸
analysis = analyzer.analyze("technical_drawing.dxf")

# 提取信息
print(f"图纸比例: {analysis['scale']}")
print(f"单位: {analysis['units']}")
print(f"图层: {analysis['layers']}")
print(f"图块: {analysis['blocks']}")
print(f"尺寸标注: {len(analysis['dimensions'])}")
print(f"文字注释: {len(analysis['text'])}")

# 按标准验证
validation = analyzer.validate(
    standard="ISO",  # 或 "ANSI", "DIN", "JIS"
    checks=["layer_naming", "line_types", "dimensions"]
)
```

## 最佳实践

### 格式选择

1. **STEP**: 3D几何交换的最佳选择
2. **IGES**: 旧版支持，尽可能使用STEP
3. **DXF**: 2D CAD互操作性的最佳选择
4. **STL**: 仅用于3D打印和可视化

### 转换质量

1. 转换后始终验证尺寸精度
2. 检查丢失的实体（圆弧、样条曲线、文字）
3. 验证图层结构是否保留
4. 批处理前先用小样本测试

### 自动化

1. 使用Python脚本处理重复任务
2. 为标准工作流创建转换模板
3. 在CI/CD流程中实现质量检查
4. 记录转换参数以便复现

## 常见问题

### 有损转换

```python
# 检查转换损失
losses = converter.check_losses(
    original="model.step",
    converted="model.iges"
)

if losses["geometry_count_diff"] > 0:
    print(f"丢失了 {losses['geometry_count_diff']} 个实体")
if losses["accuracy_loss"] > 0.01:
    print(f"精度损失: {losses['accuracy_loss']*100:.1f}%")
```

### 版本兼容性

```python
# 转换前检查格式版本
info = converter.get_format_info("drawing.dwg")
print(f"DWG版本: {info['version']}")
print(f"创建软件: {info['application']}")
print(f"兼容版本: {info['compatible_versions']}")
```

## 参考资料

- DWG/DXF规范: Open Design Alliance
- STEP标准: ISO 10303
- IGES标准: ASME Y14.26M
