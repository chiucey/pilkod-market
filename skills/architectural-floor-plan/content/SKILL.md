---
name: architectural-floor-plan
description: 顶级建筑平面图生成引擎。当用户要求创建建筑平面图、住宅布局图、室内设计图、空间规划图、房间分布图、精确建筑图纸等建筑绘图需求时使用。支持住宅、商业、公共建筑等多种类型，提供SVG矢量格式的高精度平面图。
---

# Architectural Floor Plan Generator
## 顶级建筑平面图生成引擎

### Core Capabilities

**Precision Drawing System**
- 支持精确到毫米的尺寸标注
- 标准建筑模数系统（3M、6M、12M网格系统）
- 符合国家标准的图例和符号规范
- 支持1:50、1:100、1:200等多种比例尺

**Building Types Supported**

| 类型 | 子类别 | 典型应用 |
|------|--------|----------|
| 住宅建筑 | 公寓、别墅、民居 | 住宅平面布局 |
| 商业建筑 | 办公室、店铺、餐厅 | 商业空间规划 |
| 公共建筑 | 学校、医院、图书馆 | 公共设施设计 |
| 工业建筑 | 厂房、仓库 | 工业空间布局 |

### Drawing Standards

**Wall System**
- 承重墙：240mm标准砖墙 / 200mm混凝土墙
- 隔墙：120mm砖墙 / 100mm轻质隔墙
- 墙体符号：双线表示，外墙加粗

**Opening Standards**
- 门：标准门洞 900mm×2100mm
- 窗：窗台高 900mm，窗高 1500mm（可调）
- 走廊：最小净宽 1200mm

**Dimension System**
- 轴线间距标注
- 总尺寸线（外包尺寸）
- 内部尺寸线（分隔尺寸）
- 标高标注（±0.000基准）

### Design Principles

**顶级建筑师思维**

1. **功能优先原则**
   - 动静分区明确
   - 洁污分离设计
   - 私密性层级递进

2. **人体工程学应用**
   - 常用操作区域黄金三角
   - 家具布置符合人体尺度
   - 无障碍通行空间保障

3. **空间效率优化**
   - 过道空间最小化
   - 收纳空间系统化
   - 空间利用率最大化

4. **光线与通风**
   - 自然采光优化布局
   - 南北通透的通风设计
   - 景观视线引导

### SVG Output Specifications

**Layer Structure**
```xml
<svg viewBox="0 0 width height">
  <g id="walls">墙体层</g>
  <g id="doors">门窗层</g>
  <g id="furniture">家具层</g>
  <g id="dimensions">标注层</g>
  <g id="labels">标签层</g>
</svg>
```

**Style Conventions**
- 墙体：stroke-width 2-4px, stroke #000000
- 门窗：stroke-width 1-2px, stroke #333333
- 家具：stroke-width 1px, stroke #666666, fill #f5f5f5
- 标注：font-size 12-14px, font-family "Arial", fill #333333

### Usage Workflow

1. **需求收集**
   - 建筑类型与用途
   - 建筑面积与形状要求
   - 功能房间列表
   - 特殊设计需求

2. **概念设计**
   - 功能分区规划
   - 动线设计
   - 采光通风分析

3. **精确绘图**
   - 墙体系统绘制
   - 门窗开口定位
   - 家具布置
   - 尺寸标注

4. **审核优化**
   - 规范符合性检查
   - 空间效率评估
   - 细节完善

### Output Formats

- **Primary**: SVG矢量图（可无限缩放）
- **Secondary**: 高清PNG图像
- **Documentation**: 设计说明文档

### Precision Guarantees

- 所有尺寸均可追溯到标准模数
- 符合《建筑制图标准》GB/T 50104-2010
- 图例符号符合国家标准
- 支持导出到CAD软件进行深化设计

---

**Design Philosophy**: 融合现代建筑大师的空间智慧，追求功能性、美学性与实用性的完美统一。每一份平面图都经过严谨的空间推演，确保"形式追随功能"的核心原则。
