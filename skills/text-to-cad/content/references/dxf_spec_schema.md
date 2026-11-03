# DXF Drawing Spec Schema v5.1
# 依据: ISO 8015, ISO 128, ISO 129-1, ISO 1101, ISO 1302, ISO 5457, ISO 7200,
#       ISO 2768, ISO 286, ISO 5458, ISO 7573, ASME Y14.5, ANSI Y14.3
# v5.1 修正: ★默认值统一为 standard="GB", projection="first"
# v5.0 新增: datum_chain(基准链标注), general_tolerance_block(ISO 2768),
#           datum_system(基准体系), unit_system(英制/米制), gps_standard,
#           ISO 7573 BOM, interference_check

---

## 顶层结构

```json
{
  "dxf_version": "R2010",
  "standard": "GB",
  "projection": "first",
  "unit_system": "metric",
  "gps_standard": "ISO 8015",
  "general_tolerance": "ISO 2768-mK",
  "description": "用户原始需求描述（可选）",
  "datum_system": {
    "primary": {"letter": "A", "type": "plane", "description": "Bottom face"},
    "secondary": {"letter": "B", "type": "plane", "description": "Front face"},
    "tertiary": {"letter": "C", "type": "axis", "description": "Bore center axis"}
  },
  "layers": [ ... ],
  "entities": [ ... ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `dxf_version` | string | 否 | DXF 版本，默认 `"R2010"` |
| `standard` | string | 否 | 标准体系：`"GB"`（国标，★默认）或 `"ISO"`（国际）|
| `projection` | string | 否 | 投影方式：`"first"`（第一角，★默认）或 `"third"`（第三角）|
| `unit_system` | string | 否 | 单位体系：`"metric"`（mm，★默认）或 `"imperial"`（inch） ★v9.0 |
| `gps_standard` | string | 否 | GPS 标准：`"ISO 8015"`（默认） ★v9.0 |
| `general_tolerance` | string | 否 | 通用公差等级：`"ISO 2768-mK"` 等 ★v9.0 |
| `description` | string | 否 | 文字说明 |
| `datum_system` | object | 否 | 基准体系定义（三基准系统） ★v9.0 |
| `layers` | array | 否 | 自定义图层（可覆盖默认图层） |
| `entities` | array | 是 | 图形实体列表 |

---

## 国标图层（自动创建，可覆盖）

| 图层名 | 线型 | 颜色 | 线宽(mm) | 用途 |
|--------|------|------|----------|------|
| OUTLINE | Continuous | 白(7) | **0.50** | 可见轮廓线 |
| HIDDEN | DASHED | 蓝(5) | 0.25 | 不可见轮廓线 |
| CENTER | CENTER | 红(1) | 0.25 | 中心线、轴线 |
| DIM | Continuous | 绿(3) | 0.25 | 尺寸标注 |
| TEXT | Continuous | 黄(2) | 0.25 | 文字注释 |
| HATCH | Continuous | 青(4) | 0.25 | 剖面填充 |
| BORDER | Continuous | 白(7) | **0.50** | 图框、标题栏 |
| SECTION | CENTER | 品红(6) | **0.50** | 剖切线 |
| PHANTOM | PHANTOM | 品红(6) | 0.25 | 假想线 |
| SURFACE | Continuous | 绿(3) | 0.25 | 粗糙度符号 |
| TOLERANCE | Continuous | 绿(3) | 0.25 | 形位公差框 |

### 图层 schema

```json
{
  "name": "MY_LAYER",
  "color": 1,
  "linetype": "Continuous",
  "lineweight": 25
}
```

---

## 图框与图幅（GB/T 14689）

### `border` — 标准图框

```json
{
  "type": "border",
  "size": "A3",
  "x": 0, "y": 0,
  "binding": true,
  "zone_marks": true,
  "layer": "BORDER"
}
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `size` | string | "A3" | A0/A1/A2/A3/A4 |
| `binding` | bool | true | 是否留装订边（左25mm） |
| `zone_marks` | bool | true | 是否画分区标记 |

**图幅尺寸（mm）**：
- A0: 1189×841  A1: 841×594  A2: 594×420  A3: 420×297  A4: 297×210

### `title_block` — 国标标题栏（GB/T 10609.1）

```json
{
  "type": "title_block",
  "size": "A3",
  "binding": true,
  "title": "法兰盘",
  "drawing_no": "MJ-001-2026",
  "scale": "1:1",
  "material": "45钢",
  "unit": "某某机械厂",
  "designer": "张三",
  "design_date": "2026-05-12",
  "checker": "李四",
  "check_date": "2026-05-13",
  "paper_size": "A3",
  "sheet": "1",
  "total_sheets": "1",
  "layer": "BORDER"
}
```

> ⚠️ 标题栏自动定位于图框内框右下角，无需手动指定 x/y。

---

## 基础图元

### `line` — 线段

```json
{
  "type": "line",
  "start": [0, 0],
  "end": [100, 0],
  "layer": "OUTLINE"
}
```

### `circle` — 圆

```json
{
  "type": "circle",
  "center": [50, 50],
  "radius": 25,
  "layer": "OUTLINE"
}
```

### `arc` — 圆弧（角度逆时针）

```json
{
  "type": "arc",
  "center": [0, 0],
  "radius": 30,
  "start_angle": 0,
  "end_angle": 180,
  "layer": "OUTLINE"
}
```

### `rectangle` — 矩形

```json
{
  "type": "rectangle",
  "origin": [10, 10],
  "width": 100,
  "height": 60,
  "layer": "OUTLINE"
}
```

`origin` = 左下角, `width` 向右, `height` 向上

### `polyline` — 折线

```json
{
  "type": "polyline",
  "points": [[0,0],[50,0],[50,30],[0,30]],
  "closed": true,
  "layer": "OUTLINE"
}
```

### `polygon` — 正多边形

```json
{
  "type": "polygon",
  "cx": 0, "cy": 0,
  "n": 6,
  "sides": 6,
  "radius": 50,
  "start_angle": -90,
  "layer": "OUTLINE"
}
```

### `ellipse` — 椭圆

```json
{
  "type": "ellipse",
  "center": [100, 100],
  "major_axis": [50, 0],
  "ratio": 0.5,
  "layer": "OUTLINE"
}
```

### `spline` — 样条曲线

```json
{
  "type": "spline",
  "points": [[0,0],[25,20],[50,5],[75,30],[100,0]],
  "layer": "OUTLINE"
}
```

---

## 文字与注释

### `text` — 单行文字

```json
{
  "type": "text",
  "content": "零件名称：齿轮",
  "position": [10, 5],
  "height": 3.5,
  "rotation": 0,
  "layer": "TEXT"
}
```

**标准字高**：1.8, 2.5, **3.5**, 5, 7, 10（mm），正文推荐 3.5

### `mtext` — 多行文字

```json
{
  "type": "mtext",
  "content": "技术要求\n1. 未注倒角 C0.5\n2. 表面处理：发黑",
  "position": [10, 10],
  "width": 100,
  "height": 3.5,
  "layer": "TEXT"
}
```

### `leader` — 引线标注（箭头→折→文字）

```json
{
  "type": "leader",
  "points": [[50, 60], [50, 30], [30, 30]],
  "text": "Ra1.6",
  "layer": "TEXT"
}
```

---

## 尺寸标注（GB/T 4458.4）

> ⚠️ 国标规则：小尺寸靠近轮廓，大尺寸在外；尺寸线偏移轮廓 ≥10mm

### `dim_linear` — 线性标注

```json
{
  "type": "dim_linear",
  "p1": [0, 0],
  "p2": [100, 0],
  "dimline_offset": 12,
  "angle": 0,
  "layer": "DIM"
}
```

`angle`: 0=水平标注, 90=垂直标注

### `dim_aligned` — 对齐标注

```json
{
  "type": "dim_aligned",
  "p1": [0, 0],
  "p2": [100, 50],
  "offset": 12,
  "layer": "DIM"
}
```

### `dim_radius` — 半径标注（R前缀）

```json
{
  "type": "dim_radius",
  "center": [50, 50],
  "radius": 25,
  "layer": "DIM"
}
```

### `dim_diameter` — 直径标注（Φ前缀）

```json
{
  "type": "dim_diameter",
  "center": [50, 50],
  "radius": 25,
  "angle": 45,
  "layer": "DIM"
}
```

### `dim_angular` — 角度标注

```json
{
  "type": "dim_angular",
  "vertex": [50, 50],
  "start_pt": [80, 50],
  "end_pt": [50, 80],
  "layer": "DIM"
}
```

---

## 剖面与填充

### `hatch` — 剖面填充（GB/T 4457.5）

```json
{
  "type": "hatch",
  "boundary": [[0,0],[100,0],[100,60],[0,60]],
  "pattern": "ANSI31",
  "scale": 1.0,
  "angle": 0,
  "layer": "HATCH"
}
```

| pattern | 用途 |
|---------|------|
| ANSI31 | 金属材料（默认, 45°细线） |
| ANSI37 | 非金属/塑料 |
| AR-CONC | 混凝土 |
| WOOD | 木材（纵剖） |
| SOLID | 黑色填充（橡胶等） |

---

## 国标专用图元

### `surface_roughness` — 表面粗糙度（GB/T 131）

```json
{
  "type": "surface_roughness",
  "x": 50, "y": 0,
  "ra": 1.6,
  "symbol_type": "removal",
  "orientation": "up",
  "symbol_height": 4,
  "layer": "SURFACE"
}
```

| 参数 | 说明 |
|------|------|
| `ra` | Ra 值（μm），如 0.8, 1.6, 3.2, 6.3, 12.5 |
| `symbol_type` | `basic`=基本符号 / `removal`=去除材料 / `no_removal`=不去除 |
| `orientation` | `up`（指向下方轮廓）/ `down` / `left` / `right` |
| `symbol_height` | 符号高度，默认 4mm |

### `tolerance_frame` — 形位公差框（GB/T 1182）

```json
{
  "type": "tolerance_frame",
  "x": 10, "y": 10,
  "tolerances": [
    {"symbol": "⊥", "value": "0.05", "datum": "A"},
    {"symbol": "∥", "value": "0.02", "datum": "A-B"}
  ],
  "row_height": 8,
  "layer": "TOLERANCE"
}
```

**常用形位公差符号**：`─`(直线度), `□`(平面度), `○`(圆度), `∥`(平行度), `⊥`(垂直度), `⊙`(同轴度), `◎`(同心度), `∿`(圆跳动), `↗`(位置度)

### `weld_symbol` — 焊接符号（GB/T 324）

```json
{
  "type": "weld_symbol",
  "x": 20, "y": 20,
  "ref_x": 50, "ref_y": 35,
  "weld_type": "fillet",
  "arrow_side": true,
  "size": "5",
  "layer": "WELD"
}
```

`weld_type`: `fillet`(角焊缝) / `butt`(对接) / `seam`(缝焊) / `plug`(塞焊)

### `break_line` — 断裂线（GB/T 4457）

```json
{
  "type": "break_line",
  "start": [0, 0],
  "end": [100, 0],
  "amplitude": 3,
  "style": "wavy",
  "layer": "OUTLINE"
}
```

`style`: `wavy`(波浪线) / `zigzag`(锯齿线)

### `section_line` — 剖切符号（带字母 A-A）

```json
{
  "type": "section_line",
  "p1": [0, 50],
  "p2": [100, 50],
  "label": "A",
  "arrow_offset": 6,
  "layer": "SECTION"
}
```

### `center_mark` — 中心十字线（超出轮廓3-5mm）

```json
{
  "type": "center_mark",
  "cx": 50, "cy": 50,
  "size": 15,
  "overshoot": 3,
  "layer": "CENTER"
}
```

### `center_hole` — 中心孔符号（GB/T 4459.5）

```json
{
  "type": "center_hole",
  "x": 0, "y": 0,
  "type": "A",
  "d": 2,
  "D": 4.25,
  "layer": "OUTLINE"
}
```

---

## 机械零件图元

### `bolt_circle` — 均布螺栓孔

```json
{
  "type": "bolt_circle",
  "cx": 0, "cy": 0,
  "pcd": 75,
  "holes": 6,
  "hole_diameter": 9,
  "draw_pcd": true,
  "draw_center_lines": true,
  "layer": "OUTLINE"
}
```

> 孔从 90°（顶部）开始均布，符合国标对称布孔规范

### `counterbore` — 沉孔

```json
{
  "type": "counterbore",
  "cx": 0, "cy": 0,
  "c_bore_diameter": 16,
  "pilot_diameter": 10,
  "layer": "OUTLINE"
}
```

### `countersink` — 埋头孔

```json
{
  "type": "countersink",
  "cx": 0, "cy": 0,
  "outer_diameter": 20,
  "inner_diameter": 10,
  "sink_angle": 90,
  "layer": "OUTLINE"
}
```

### `keyway` — 键槽（GB/T 1095）

```json
{
  "type": "keyway",
  "origin": [10, 10],
  "width": 8,
  "height": 4,
  "rounded": true,
  "layer": "OUTLINE"
}
```

### `gear` — 直齿圆柱齿轮（GB/T 4459.2 规定画法）

```json
{
  "type": "gear",
  "cx": 0, "cy": 0,
  "outer_radius": 50,
  "root_radius": 42,
  "pitch_radius": 46,
  "hub_radius": 15,
  "bore_radius": 8,
  "num_teeth": 24,
  "draw_web_holes": true,
  "layer": "OUTLINE"
}
```

> 画法: 齿顶圆=粗实线, 分度圆=细点画线(CENTER层), 齿根圆=细实线

### `screw_thread` — 螺纹（GB/T 4459.1）

```json
{
  "type": "screw_thread",
  "cx": 0, "cy": 0,
  "radius": 10,
  "length": 40,
  "type": "external",
  "layer": "OUTLINE"
}
```

`type`: `external`(外螺纹) / `internal`(内螺纹)

### `spring` — 压缩弹簧前视图

```json
{
  "type": "spring",
  "cx": 0, "cy": 0,
  "outer_radius": 20,
  "wire_diameter": 3,
  "coils": 8,
  "length": 80,
  "layer": "OUTLINE"
}
```

### `o_ring` — O形圈（GB/T 3452.1）

```json
{
  "type": "o_ring",
  "cx": 0, "cy": 0,
  "outer_diameter": 60,
  "cord_diameter": 5,
  "layer": "OUTLINE"
}
```

### `fillet` — 圆角

```json
{
  "type": "fillet",
  "origin": [0, 0],
  "width": 30,
  "height": 30,
  "radius": 5,
  "layer": "OUTLINE"
}
```

---

## 建筑图元

### `wall` — 墙体

```json
{
  "type": "wall",
  "x": 0, "y": 0,
  "width": 5000,
  "height": 240,
  "fill": false,
  "layer": "WALL"
}
```

### `door_arc` — 平开门

```json
{
  "type": "door_arc",
  "x": 2000, "y": 0,
  "width": 900,
  "opens_left": false,
  "layer": "DOOR"
}
```

### `window` — 窗户

```json
{
  "type": "window",
  "x": 3000, "y": 0,
  "width": 1500,
  "height": 240,
  "layer": "WINDOW"
}
```

### `stairs` — 楼梯踏步

```json
{
  "type": "stairs",
  "x": 0, "y": 0,
  "width": 2400,
  "height": 1500,
  "steps": 10,
  "layer": "WALL"
}
```

---

## 电气符号（GB/T 4728 / IEC 60617）

### 通用参数

| 参数 | 说明 |
|------|------|
| `x`, `y` | 符号左端或中心 |
| `length` | 符号总长（含引线），默认 50mm |
| `layer` | 默认 `SYMBOL` |

### 各类电气符号

```json
{"type": "wire",      "start": [0,0], "end": [50,0], "layer": "WIRE"}
{"type": "bus_line",  "start": [0,0], "end": [200,0]}
{"type": "resistor",  "x": 0, "y": 0, "length": 50}
{"type": "capacitor", "x": 0, "y": 0, "length": 50}
{"type": "inductor",  "x": 0, "y": 0, "length": 50, "coils": 4}
{"type": "diode",     "x": 0, "y": 0, "length": 50}
{"type": "switch_no", "x": 0, "y": 0, "length": 50}
{"type": "gnd",       "x": 0, "y": 0, "size": 20}
{"type": "terminal",  "x": 0, "y": 0, "radius": 4}
{"type": "node_dot",  "x": 0, "y": 0, "radius": 2}
{"type": "transformer","x": 0, "y": 0, "length": 40, "coils": 4, "core": true}
{"type": "transistor","x": 0, "y": 0, "length": 50}
{"type": "ic_chip",   "x": 0, "y": 0, "width": 60, "height": 40, "pins_left": 4, "pins_right": 4, "label": "U1"}
{"type": "connector", "cx": 0, "cy": 0, "width": 20, "height": 40, "pin_count": 4}
```

---

## P&ID 管道仪表图元

```json
{"type": "pipe",       "start": [0,0],    "end": [100,0]}
{"type": "pipe_elbow", "cx": 100, "cy": 0, "radius": 20, "clockwise": false}
{"type": "valve",      "cx": 50, "cy": 0,  "size": 20, "angle": 0}
{"type": "pump",       "cx": 0, "cy": 0,   "size": 25}
{"type": "tank",       "cx": 0, "cy": 0,   "width": 60, "height": 120}
```

---

## 表格

### `bom` — 明细表（GB/T 10609.2）

```json
{
  "type": "bom",
  "x": 0, "y": 0,
  "headers": ["序号", "代号", "名称", "数量", "材料", "备注"],
  "col_widths": [15, 40, 55, 15, 35, 30],
  "row_height": 8,
  "rows": [
    ["1", "MJ-001", "法兰盘", "1", "45钢", ""],
    ["2", "MJ-002", "螺栓", "6", "35钢", "M10×30"]
  ]
}
```

### `revision_table` — 更改区

```json
{
  "type": "revision_table",
  "x": 0, "y": 0,
  "revisions": [
    {"rev": "A", "change_no": "", "desc": "初版发布", "date": "2026-05-12", "author": "张三"},
    {"rev": "B", "change_no": "CR-001", "desc": "修改孔径", "date": "2026-05-15", "author": "李四"}
  ]
}
```

### `tolerance_frame` — 形位公差框

见上方"国标专用图元"章节。

---

## 坐标系约定

- 所有坐标单位：**mm**（毫米）
- 原点 `[0, 0]`：图幅左下角
- X 轴朝右，Y 轴朝上（标准二维制图坐标系）
- 角度：度（°），从正 X 轴逆时针计量

---

## 完整示例：法兰盘（A3 横幅，含国标图框和标题栏）

```json
{
  "dxf_version": "R2010",
  "description": "法兰盘 DN100 × t10，6×M10螺栓孔",
  "entities": [
    {"type": "border",     "size": "A3", "binding": true, "zone_marks": true},
    {"type": "title_block","size": "A3", "binding": true,
     "title": "法兰盘", "drawing_no": "MJ-001", "scale": "1:1",
     "material": "45钢", "unit": "某机械厂", "designer": "张三",
     "design_date": "2026-05-12", "paper_size": "A3", "sheet": "1", "total_sheets": "1"},

    {"type": "circle",      "center": [200, 148], "radius": 50,  "layer": "OUTLINE"},
    {"type": "circle",      "center": [200, 148], "radius": 20,  "layer": "OUTLINE"},
    {"type": "bolt_circle", "cx": 200, "cy": 148, "pcd": 75,
     "holes": 6, "hole_diameter": 9, "layer": "OUTLINE"},
    {"type": "center_mark", "cx": 200, "cy": 148, "size": 55, "overshoot": 5},

    {"type": "dim_diameter","center": [200,148], "radius": 50, "angle": 135, "layer": "DIM"},
    {"type": "dim_diameter","center": [200,148], "radius": 20, "angle": 45,  "layer": "DIM"},
    {"type": "dim_diameter","center": [200,148], "radius": 37.5,"angle": 90, "layer": "DIM"},

    {"type": "surface_roughness","x": 260,"y": 148,"ra": 1.6,"orientation": "left"},
    {"type": "surface_roughness","x": 200,"y": 200,"ra": 3.2,"orientation": "up"},

    {"type": "mtext",
     "content": "技术要求\n1. 未注倒角 C0.5\n2. 热处理: 调质 HRC28-32\n3. 去除毛刺，锐边倒钝",
     "position": [20, 20], "width": 120, "height": 3.5, "layer": "TEXT"}
  ]
}
```

---

## 错误处理

| 警告信息 | 原因 | 解决方式 |
|----------|------|---------|
| `[WARN] Unknown entity type: xxx` | 未识别的图元类型 | 触发 evolution_engine（Route C）或检查拼写 |
| `[WARN] Skipping xxx` | 图元字段缺失或非法 | 检查必填字段（参考本文档） |
| `[PLUGIN] Failed to load xxx.py` | 插件文件错误 | 检查插件语法 |
| `[WARN] Dimension skipped` | ezdxf 标注创建失败 | 检查 p1/p2 坐标，或降级为 dim_linear |

---

## v3.0 新增国标图元

### `datum_mark` — 基准符号（GB/T 1182）

用于标注形位公差的基准要素。由粗实线方框 + 大写字母 + 细实线连线 + 实心三角形组成。

```json
{
  "type": "datum_mark",
  "x": 50, "y": 100,
  "letter": "A",
  "orientation": "up",
  "leader_length": 10,
  "triangle_size": 5,
  "box_size": 7,
  "layer": "TOLERANCE"
}
```

| 参数 | 说明 |
|------|------|
| `letter` | 基准字母，如 "A", "B", "C"（大写） |
| `orientation` | `up`(三角朝上) / `down` / `left` / `right` |
| `leader_length` | 引线长度（从方框到三角尖端），默认 10mm |
| `triangle_size` | 三角形边长，默认 5mm |
| `box_size` | 方框边长，默认 7mm |

### `view_label` — 视图名称标注

用于在视图上方标注视图名称（如"主视图"、"A-A"、"B向"）。

```json
{
  "type": "view_label",
  "text": "A-A",
  "x": 150, "y": 200,
  "height": 5,
  "layer": "TEXT"
}
```

### `part_number` — 零件序号标注（装配图专用）

在装配图中标注零件序号。由引线 + 圆圈 + 序号数字组成。

```json
{
  "type": "part_number",
  "number": 1,
  "target": [100, 150],
  "label_pos": [120, 180],
  "circle_radius": 4,
  "layer": "TEXT"
}
```

| 参数 | 说明 |
|------|------|
| `number` | 序号数字 |
| `target` | 箭头指向的零件位置 |
| `label_pos` | 序号圆圈中心位置 |
| `circle_radius` | 序号圆圈半径，默认 4mm |

---

## 多视图布局概念（v3.0 新增）

多视图不在 spec 中以独立实体表示，而是通过 Agent 计算各视图的坐标偏移，将所有图元的坐标直接指定到正确位置。

### 视图区域划分（A3 横幅示例）

```
A3 内框: (25, 5) → (395, 292), 即 iw=370, ih=287

┌─────────────────────────────────────────────────────────┐
│  内框顶部                                              │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │              │  │              │                   │
│  │   主视图     │  │   左视图     │                   │
│  │  (Front)     │  │  (Left Side) │                   │
│  │              │  │              │                   │
│  └──────────────┘  └──────────────┘                   │
│         ↕ view_gap=20                                  │
│  ┌──────────────┐  ┌──────────────────┐              │
│  │              │  │   剖面图          │              │
│  │   俯视图     │  │   (Section)       │              │
│  │  (Top)       │  │                   │              │
│  │              │  └──────────────────┘              │
│  └──────────────┘                                     │
│  ┌─────────────────────────┐                         │
│  │ 技术要求                 │   ┌──────────────────┐  │
│  │                         │   │   标题栏          │  │
│  └─────────────────────────┘   └──────────────────┘  │
│  内框底部                                              │
└─────────────────────────────────────────────────────────┘
```

### Agent 坐标计算参考

详细计算方法参见 `references/view_layout_guide.md`。

简要规则：
1. `view_gap`（视图间距）≥ 20mm
2. 主视图左上角 x = `inner_left + (iw - main_w) / 2`
3. 主视图左上角 y = `inner_top - main_h - 15`（顶部留白 15mm）
4. 俯视图 y = 主视图 y - view_gap - top_h（与主视图左对齐）
5. 左视图 x = 主视图 x + main_w + view_gap（与主视图底部对齐）
6. 所有坐标必须验证不超出内框范围

---

## 钣金展开图概念（v3.0 新增）

钣金零件的 spec 中同时包含成形图和展开图两部分实体。

### 标注约定

- 折弯线：使用 `line` 图元，`layer: "PHANTOM"`（双点画线）
- 折弯方向箭头：使用 `leader` 标注"↑折弯"
- 折弯角度标注：使用 `dim_angular`
- 展开尺寸标注：使用 `dim_linear` / `dim_diameter`
- 板厚标注：使用 `dim_linear`

### 折弯补偿计算

```
展开长度 L = Σ直线段 + Σ折弯补偿
折弯补偿 = π × (R + K × T) × θ / 180

常用 K 因子:
- 软钢/铝: K ≈ 0.35-0.42
- 不锈钢: K ≈ 0.40-0.45
- 黄铜: K ≈ 0.35-0.40
```

---

## 装配图概念（v3.0 新增）

### 零件区分策略

装配图中不同零件通过以下方式区分：
1. 相邻零件剖面线方向不同（hatch angle 交替 0°/90°）
2. 使用引线序号标注（`part_number`）
3. 明细表（`bom`）列出所有零件

### 装配图 spec 模板

```json
{
  "dxf_version": "R2010",
  "description": "XX部件装配图",
  "entities": [
    {"type": "border", "size": "A2", "binding": true},
    {"type": "title_block", "size": "A2", "title": "XX部件", "scale": "1:2", "material": "装配体"},

    // 主视图（剖视图）
    {"type": "section_line", "p1": [x1,y1], "p2": [x2,y2], "label": "A"},
    // 零件1轮廓 + 剖面填充(angle:0)
    {"type": "rectangle", "origin": [...], "width": ..., "height": ..., "layer": "OUTLINE"},
    {"type": "hatch", "boundary": [...], "pattern": "ANSI31", "angle": 0, "layer": "HATCH"},
    // 零件2轮廓 + 剖面填充(angle:90)
    {"type": "rectangle", "origin": [...], "width": ..., "height": ..., "layer": "OUTLINE"},
    {"type": "hatch", "boundary": [...], "pattern": "ANSI31", "angle": 90, "layer": "HATCH"},

    // 视图名称
    {"type": "view_label", "text": "A-A", "x": ..., "y": ..., "height": 5, "layer": "TEXT"},

    // 零件序号标注
    {"type": "part_number", "number": 1, "target": [...], "label_pos": [...], "layer": "TEXT"},
    {"type": "part_number", "number": 2, "target": [...], "label_pos": [...], "layer": "TEXT"},

    // 配合尺寸标注
    {"type": "dim_diameter", "center": [...], "radius": ..., "angle": 45, "layer": "DIM"},

    // 明细表（位于标题栏上方）
    {"type": "bom", "x": ..., "y": ..., "headers": ["序号","代号","名称","数量","材料","备注"],
     "col_widths": [15,40,55,15,35,30], "row_height": 8,
     "rows": [["1","MJ-001","零件A","1","45钢",""],["2","MJ-002","零件B","1","HT200",""]]},

    // 技术要求
    {"type": "mtext", "content": "技术要求\n1. 装配后转动灵活\n2. ...", "position": [...], "width": 120, "height": 3.5, "layer": "TEXT"}
  ]
}
```

---

## 爆炸图概念（v3.0 新增）

爆炸图通常作为单独 DXF 文件输出，沿装配轴向展开各零件。

### 爆炸图 spec 模板

```json
{
  "dxf_version": "R2010",
  "description": "XX部件爆炸图",
  "entities": [
    {"type": "border", "size": "A3", "binding": true},
    {"type": "title_block", "size": "A3", "title": "XX部件-爆炸图", "scale": "1:1"},

    // 装配轴线（PHANTOM 线型）
    {"type": "line", "start": [cx, y_start], "end": [cx, y_end], "layer": "PHANTOM"},

    // 零件1（原始位置 + 偏移 0）
    {"type": "rectangle", "origin": [x1, y1+0], "width": ..., "height": ..., "layer": "OUTLINE"},
    // 零件2（沿轴偏移 40mm）
    {"type": "rectangle", "origin": [x2, y1+40], "width": ..., "height": ..., "layer": "OUTLINE"},
    // 零件3（沿轴偏移 80mm）
    {"type": "circle", "center": [cx, y1+80], "radius": ..., "layer": "OUTLINE"},

    // 序号标注
    {"type": "part_number", "number": 1, "target": [...], "label_pos": [...], "layer": "TEXT"},
    {"type": "part_number", "number": 2, "target": [...], "label_pos": [...], "layer": "TEXT"},

    // 零件清单
    {"type": "bom", "x": ..., "y": ..., "headers": ["序号","名称","数量","材料"],
     "col_widths": [15,60,15,50], "row_height": 8,
     "rows": [["1","零件A","1","45钢"],["2","零件B","1","HT200"]]}
  ]
}
```

---

## v4.0 新增 ISO 国际标准图元

### `projection_symbol` — 投影方式符号（ISO 128-1, v8.0 新增）

用于在标题栏内或标题栏附近绘制投影方式符号。截锥体图形标识。

```json
{
  "type": "projection_symbol",
  "projection": "first",
  "x": 350,
  "y": 30,
  "size": 15,
  "layer": "BORDER"
}
```

| 参数 | 说明 |
|------|------|
| `projection` | `"first"`（第一角投影）或 `"third"`（第三角投影）|
| `x`, `y` | 符号中心位置 |
| `size` | 符号整体尺寸，默认 15mm |
| `layer` | 默认 `BORDER` |

**第一角投影符号绘制方法：**
```
截锥体：上方小圆（俯视图），右方全圆（左视图）
- 顶圆：circle(x, y + size*0.3, size*0.15)，细实线
- 底圆：circle(x, y - size*0.3, size*0.25)，细实线
- 右圆：circle(x + size*0.3, y, size*0.2)，粗实线
- 连线：左斜线 + 右斜线（梯形侧视图）
```

**第三角投影符号绘制方法：**
```
截锥体：下方小圆（俯视图），左方全圆（左视图）
- 顶圆：circle(x, y + size*0.3, size*0.25)，粗实线
- 底圆：circle(x, y - size*0.3, size*0.15)，细实线
- 左圆：circle(x - size*0.3, y, size*0.2)，细实线
- 连线：左斜线 + 右斜线（梯形侧视图）
```

### title_block ISO 模式扩展字段

当 `standard` 为 `"ISO"` 时，title_block 支持以下额外字段：

```json
{
  "type": "title_block",
  "size": "A3",
  "binding": true,
  "standard": "ISO",
  "projection": "first",
  "title": "Flange Plate",
  "drawing_no": "MJ-001",
  "scale": "1:1",
  "material": "AISI 1045",
  "unit": "ABC Engineering Co.",
  "designed_by": "Zhang San",
  "checked_by": "Li Si",
  "date": "2026-05-12",
  "paper_size": "A3",
  "sheet": "1",
  "total_sheets": "1",
  "language": "en"
}
```

| 新增字段 | 说明 |
|---------|------|
| `standard` | `"ISO"` 或 `"GB"`，影响字段标签语言 |
| `projection` | 在标题栏中标注投影方式 |
| `language` | `"en"`（英文）或 `"zh"`（中文），默认 `"zh"` |
| `designed_by` | 设计者（ISO 字段名） |
| `checked_by` | 审核者（ISO 字段名） |

### ISO 直径前缀说明

ISO 标准下，`dim_diameter` 自动使用 `Ø` 前缀（而非 GB 的 `Φ`）。
此行为由 spec 顶层 `standard` 字段控制，无需在 entity 中额外指定。

---

## 第三角投影视图布局概念（v4.0 新增）

第三角投影的视图布局与第一角投影相反：

```
第一角投影 (projection="first"):
  俯视图在主视图下方，左视图在主视图右方

第三角投影 (projection="third"):
  俯视图在主视图上方，左视图在主视图左方
```

Agent 在生成 spec 时，需根据 `projection` 字段调整所有视图实体的坐标位置。
具体坐标计算方法参见 `references/view_layout_guide.md`。

---

## v5.0 新增 GPS 基准体系图元（v9.0）

### `datum_chain` — 基准链闭环标注（ISO 8015 / ISO 5458 / ASME Y14.5）

从基准面出发，依次标注到各加工面，形成封闭尺寸链。所有尺寸从统一基准出发。

```json
{
  "type": "datum_chain",
  "dimensions": [
    {
      "p1": [100, 100],
      "p2": [150, 100],
      "value": "50",
      "datum_ref": "A",
      "tolerance": "±0.05",
      "dimline_offset": 10,
      "angle": 0
    },
    {
      "p1": [150, 100],
      "p2": [200, 100],
      "value": "50",
      "tolerance": "±0.03",
      "dimline_offset": 18,
      "angle": 0
    },
    {
      "p1": [200, 100],
      "p2": [100, 100],
      "value": "100",
      "tolerance": "±0.08",
      "dimline_offset": 26,
      "angle": 0
    }
  ],
  "chain_label": "DATUM CHAIN A",
  "closed": true,
  "layer": "DIM"
}
```

| 参数 | 说明 |
|------|------|
| `dimensions` | 尺寸链中各环的标注列表 |
| `dimensions[].p1` | 标注起点坐标 |
| `dimensions[].p2` | 标注终点坐标 |
| `dimensions[].value` | 标注文字（覆盖自动计算值）|
| `dimensions[].datum_ref` | 基准参考字母（可选）|
| `dimensions[].tolerance` | 公差文字（可选）|
| `dimensions[].dimline_offset` | 尺寸线偏移量 |
| `dimensions[].angle` | 0=水平标注, 90=垂直标注 |
| `chain_label` | 基准链标识文字 |
| `closed` | 是否验证闭环（默认 true）|

### `general_tolerance_block` — ISO 2768 通用公差等级标注块

在技术要求区域或标题栏附近放置通用公差等级说明。

```json
{
  "type": "general_tolerance_block",
  "x": 20,
  "y": 20,
  "class": "mK",
  "unit_system": "metric",
  "height": 3.5,
  "title_height": 5,
  "box_width": 65,
  "box_height": 35,
  "layer": "TEXT"
}
```

| 参数 | 说明 |
|------|------|
| `class` | ISO 2768 等级: `"mK"`, `"fK"`, `"cK"`, `"vK"`, `"m"`, `"f"`, `"c"`, `"v"`, `"H"` |
| `unit_system` | `"metric"`(mm) 或 `"imperial"`(inch) |
| `box_width` | 标注块宽度，默认 65mm |
| `box_height` | 标注块高度，默认 35mm |

### 顶层 `datum_system` 字段（v9.0 新增）

在 spec 顶层定义零件的三基准体系：

```json
{
  "datum_system": {
    "primary": {"letter": "A", "type": "plane", "description": "Bottom mounting face"},
    "secondary": {"letter": "B", "type": "plane", "description": "Front alignment face"},
    "tertiary": {"letter": "C", "type": "axis", "description": "Main bore center axis"}
  }
}
```

| 字段 | 说明 |
|------|------|
| `primary` | 主基准（第一基准，如底面）|
| `secondary` | 副基准（第二基准，如侧面）|
| `tertiary` | 第三基准（辅助定位，如轴线）|
| `letter` | 基准代号（A/B/C）|
| `type` | 基准类型: `"plane"`(面), `"axis"`(轴线) |
| `description` | 基准描述（英文）|

### 顶层 `unit_system` 字段（v9.0 新增）

```json
{
  "unit_system": "metric"
}
```

| 值 | 说明 | 尺寸单位 | 适用场景 |
|----|------|---------|---------|
| `"metric"` | 米制（默认）| mm | ISO 国际标准 |
| `"imperial"` | 英制 | inch | ASME Y14.5 / ANSI 标准 |

### 顶层 `gps_standard` 字段（v9.0 新增）

```json
{
  "gps_standard": "ISO 8015"
}
```

### 顶层 `general_tolerance` 字段（v9.0 新增）

```json
{
  "general_tolerance": "ISO 2768-mK"
}
```

---

## 坐标系约定（v9.0 更新）

- **默认单位**: mm（毫米），`unit_system: "imperial"` 时为 inch
- 原点 `[0, 0]`：图幅左下角
- X 轴朝右，Y 轴朝上（标准二维制图坐标系）
- 角度：度（°），从正 X 轴逆时针计量
- **英制图纸坐标仍使用 mm**（内部计算），但尺寸标注显示值自动转换为 inch

---

## ISO 7573 BOM 格式（v9.0 更新）

当 `standard: "ISO"` 时，BOM 使用英文字段：

```json
{
  "type": "bom",
  "x": 0,
  "y": 0,
  "standard": "ISO",
  "headers": ["Item", "Part No.", "Description", "Qty", "Material", "Mass (kg)", "Notes"],
  "col_widths": [12, 35, 50, 12, 30, 18, 25],
  "row_height": 8,
  "rows": [
    ["1", "FLG-001", "Flange DN100", "1", "AISI 1045", "2.5", "Normalized"],
    ["2", "BSH-006", "Hex Bolt M10×30", "6", "Grade 8.8", "0.03", "Zn plated"]
  ]
}
```
