#!/usr/bin/env python3
"""
cad_generator.py v7.0 - Text-to-CAD ISO/GB Dual Engine (Production-Grade Standards-Compliant)
Converts structured drawing specs (JSON) into DXF files via ezdxf.

New in v7.0 (v11.0 Skill companion):
  - ★ 修复 draw_keyway: rounded 模式正确绘制端铣半圆弧键槽（原代码仅画矩形）
  - ★ 修复 draw_chamber: 倒角弧线宽统一为 LW_THICK（原缺少线宽属性）
  - ★ 修复 draw_bom_table: 默认标准从 ISO 改为 GB（与 v10 全局默认值一致）
  - 保留 v6.1 全部能力

New in v6.1 (v10.0 Skill companion):
  - ★ 默认投影改回第一角投影（ISO 128-1 / GB/T 17451，中国/欧洲国际通用）
  - ★ 默认标准改为 GB（国内生产图纸）
  - ★ 强化铁律执行注释：禁止随意改尺寸/非标绘制
  - ★ 默认通用公差改为 GB/T 1804-m（国内标准）
  - 保留第三角投影支持（外贸/ASME 场景，spec 中指定 projection="third"）

New in v6.0 (v9.0 Skill companion):
  - 新增 datum_chain（ISO 8015 / ISO 5458 基准链闭环标注）
  - 新增 general_tolerance_block（ISO 2768 通用公差等级标注）
  - 新增英制单位支持（inch/feet，ANSI Y14.5 标准）
  - 新增 ISO 7573 国际 BOM 模板（英文字段）
  - 新增 GPS 基准体系支持（datum_system 顶层字段）
  - 新增 DIMSTYLE 支持 ISO/ANSI 双箭头样式
  - 新增 ANSI 标准图幅尺寸（A/B/C/D/E）
  - 强化: 公差配置按 ISO 286 标准配合制选配
  - 强化: 基准链闭环验证（检测开口尺寸链）

New in v5.0 (v8.0 Skill companion):
  - 新增 projection_symbol（投影方式符号 ISO 128-1）
  - 新增 ISO 7200 标题栏模式（standard="ISO" 时自动切换英文字段）
  - 新增顶层 standard / projection 字段支持
  - ISO 直径前缀 Ø vs GB 前缀 Φ 自动适配
  - 支持 third angle projection 视图布局

New in v4.1 (v7.0 Skill companion):
  - 新增 datum_mark（基准符号 ISO 1101 / ASME Y14.5）
  - 新增 view_label（视图名称标注）
  - 新增 part_number（零件序号标注，装配图专用）

Usage:
    python cad_generator.py <spec.json> [--output output.dxf]

Spec JSON format: see references/dxf_spec_schema.md + references/gps_datum_system.md
"""

import argparse
import json
import sys
import math
import importlib.util
from pathlib import Path

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment, MTextParagraphAlignment
    from ezdxf import units
except ImportError:
    print("[ERROR] ezdxf not installed. Run: pip install ezdxf", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────
# 国标常量
# ─────────────────────────────────────────────

# 标准图幅尺寸 (宽 x 高, mm)
PAPER_SIZES = {
    "A0": (1189, 841),
    "A1": (841, 594),
    "A2": (594, 420),
    "A3": (420, 297),
    "A4": (297, 210),
}

# ANSI 标准图幅尺寸 (宽 x 高, mm) — v9.0 新增
ANSI_PAPER_SIZES = {
    "A": (279.4, 215.9),    # 11" × 8.5"
    "B": (431.8, 279.4),    # 17" × 11"
    "C": (558.8, 431.8),    # 22" × 17"
    "D": (838.2, 558.8),    # 33" × 22"
    "E": (1066.8, 838.2),   # 42" × 33"
}

# 英制/米制转换 — v9.0 新增
MM_PER_INCH = 25.4

# 标准图框边距 (左, 下, 右, 上) - 有装订边版本
FRAME_MARGINS_WITH_BINDING = {
    "A0": (25, 10, 10, 10),
    "A1": (25, 10, 10, 10),
    "A2": (25, 10, 10, 10),
    "A3": (25, 5, 5, 5),
    "A4": (25, 5, 5, 5),
}

# 标准图框边距 - 无装订边版本
FRAME_MARGINS_NO_BINDING = {
    "A0": (10, 10, 10, 10),
    "A1": (10, 10, 10, 10),
    "A2": (10, 10, 10, 10),
    "A3": (5, 5, 5, 5),
    "A4": (5, 5, 5, 5),
}

# 标准线宽 (mm -> lineweight code *100)
LW_THICK  = 50   # 0.5mm 粗实线
LW_MEDIUM = 35   # 0.35mm 中线
LW_THIN   = 25   # 0.25mm 细实线
LW_HAIR   = 18   # 0.18mm 极细线

# 标准字高序列 (mm)
TEXT_HEIGHT_TITLE    = 5.0   # 图名
TEXT_HEIGHT_BODY     = 3.5   # 正文/尺寸文字
TEXT_HEIGHT_SMALL    = 2.5   # 辅助/签字
TEXT_HEIGHT_NOTE     = 3.5   # 技术要求


# ─────────────────────────────────────────────
# 国标图层默认配置
# ─────────────────────────────────────────────

GB_LAYER_DEFS = [
    {"name": "OUTLINE",   "color": 7,  "linetype": "Continuous", "lineweight": LW_THICK},
    {"name": "HIDDEN",    "color": 5,  "linetype": "DASHED",     "lineweight": LW_THIN},
    {"name": "CENTER",    "color": 1,  "linetype": "CENTER",     "lineweight": LW_THIN},
    {"name": "DIM",       "color": 3,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "TEXT",      "color": 2,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "HATCH",     "color": 4,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "BORDER",    "color": 7,  "linetype": "Continuous", "lineweight": LW_THICK},
    {"name": "SECTION",   "color": 6,  "linetype": "CENTER",     "lineweight": LW_THICK},
    {"name": "PHANTOM",   "color": 6,  "linetype": "PHANTOM",    "lineweight": LW_THIN},
    {"name": "WELD",      "color": 2,  "linetype": "Continuous", "lineweight": LW_MEDIUM},
    {"name": "SURFACE",   "color": 3,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "TOLERANCE", "color": 3,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "SYMBOL",    "color": 2,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "WALL",      "color": 7,  "linetype": "Continuous", "lineweight": LW_THICK},
    {"name": "DOOR",      "color": 3,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "WINDOW",    "color": 4,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "PIPE",      "color": 7,  "linetype": "Continuous", "lineweight": LW_THICK},
    {"name": "WIRE",      "color": 1,  "linetype": "Continuous", "lineweight": LW_THIN},
    {"name": "GRID",      "color": 9,  "linetype": "Continuous", "lineweight": LW_HAIR},
    {"name": "DATUM",     "color": 3,  "linetype": "Continuous", "lineweight": LW_THIN},  # v9.0: 基准标注层
]


# ─────────────────────────────────────────────
# 基础绘图工具函数
# ─────────────────────────────────────────────

def _attribs(entity: dict, default_layer: str = "0", lineweight: int = None) -> dict:
    """Build common dxfattribs from entity dict."""
    layer = entity.get("layer", default_layer)
    color = entity.get("color", None)
    lw    = entity.get("lineweight", lineweight)
    a = {"layer": layer}
    if color is not None:
        a["color"] = color
    if lw is not None:
        a["lineweight"] = lw
    return a


# ─────────────────────────────────────────────
# Drawing primitives dispatcher
# ─────────────────────────────────────────────

def draw_line(msp, entity: dict):
    """Draw a line segment."""
    start = tuple(entity["start"])
    end   = tuple(entity["end"])
    msp.add_line(start, end, dxfattribs=_attribs(entity, "OUTLINE"))


def draw_circle(msp, entity: dict):
    center = tuple(entity["center"])
    radius = entity["radius"]
    msp.add_circle(center, radius, dxfattribs=_attribs(entity, "OUTLINE"))


def draw_arc(msp, entity: dict):
    center      = tuple(entity["center"])
    radius      = entity["radius"]
    start_angle = entity["start_angle"]
    end_angle   = entity["end_angle"]
    msp.add_arc(center, radius, start_angle, end_angle,
                dxfattribs=_attribs(entity, "OUTLINE"))


def draw_rectangle(msp, entity: dict):
    """Draw a rectangle via lwpolyline (国标: 矩形用闭合折线)."""
    x, y = entity["origin"]
    w    = entity["width"]
    h    = entity["height"]
    points = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    msp.add_lwpolyline(points, close=True,
                       dxfattribs=_attribs(entity, "OUTLINE"))


def draw_polyline(msp, entity: dict):
    points = [tuple(p) for p in entity["points"]]
    closed = entity.get("closed", False)
    msp.add_lwpolyline(points, close=closed,
                       dxfattribs=_attribs(entity, "OUTLINE"))


def draw_text(msp, entity: dict):
    content  = entity["content"]
    position = tuple(entity["position"])
    height   = entity.get("height", TEXT_HEIGHT_BODY)
    rotation = entity.get("rotation", 0)
    layer    = entity.get("layer", "TEXT")
    color    = entity.get("color", None)
    attribs  = {"layer": layer, "height": height, "rotation": rotation}
    if color is not None:
        attribs["color"] = color
    msp.add_text(content, dxfattribs=attribs).set_placement(
        position, align=TextEntityAlignment.LEFT
    )


def draw_dimension_linear(msp, doc, entity: dict):
    """
    Linear dimension — GB/T 4458.4 compliant.
    p1, p2: measured points
    dimline_offset: distance of dim line from measured edge (positive = outward)
    angle: 0=horizontal, 90=vertical
    """
    p1    = tuple(entity["p1"])
    p2    = tuple(entity["p2"])
    base  = entity.get("dimline_offset", 10)
    layer = entity.get("layer", "DIM")
    angle = entity.get("angle", 0)
    dimstyle = entity.get("dimstyle", "EZDXF")
    # Calculate base point (offset from midpoint, perpendicular to dim line direction)
    if angle == 0:
        # Horizontal dimension: offset vertically
        base_point = ((p1[0] + p2[0]) / 2, max(p1[1], p2[1]) + base)
    elif angle == 90:
        # Vertical dimension: offset horizontally
        base_point = (max(p1[0], p2[0]) + base, (p1[1] + p2[1]) / 2)
    else:
        base_point = ((p1[0] + p2[0]) / 2, max(p1[1], p2[1]) + base)
    try:
        dim = msp.add_linear_dim(
            base=base_point, p1=p1, p2=p2, angle=angle,
            dimstyle=dimstyle, dxfattribs={"layer": layer},
        )
        dim.render()
    except Exception as e:
        print(f"[WARN] Linear dimension skipped: {e}", file=sys.stderr)


def draw_hatch(msp, entity: dict):
    """
    Fill a closed boundary — GB/T 4457.5 剖面线规范.
    Default pattern: ANSI31 (金属, 45°细线, 间距约3mm).
    """
    pattern = entity.get("pattern", "ANSI31")
    layer   = entity.get("layer", "HATCH")
    scale   = entity.get("scale", 1.0)
    angle   = entity.get("angle", 0)      # 附加旋转角
    points  = [tuple(p) for p in entity["boundary"]]
    hatch   = msp.add_hatch(dxfattribs={"layer": layer})
    hatch.set_pattern_fill(pattern, scale=scale, angle=angle)
    hatch.paths.add_polyline_path(points, is_closed=True)


def draw_spline(msp, entity: dict):
    points = [tuple(p) for p in entity["points"]]
    msp.add_spline(points, dxfattribs=_attribs(entity, "OUTLINE"))


def draw_ellipse(msp, entity: dict):
    center      = tuple(entity["center"])
    major_axis  = tuple(entity.get("major_axis", (entity.get("rx", 10), 0)))
    ratio       = entity.get("ratio", 0.5)
    msp.add_ellipse(center=center, major_axis=major_axis, ratio=ratio,
                    dxfattribs=_attribs(entity, "OUTLINE"))


# ═══════════════════════════════════════════════════════
#  国标几何图元
# ═══════════════════════════════════════════════════════

def draw_polygon(msp, entity: dict):
    """正多边形（推荐 n=3,4,6,8）."""
    cx      = entity.get("cx", 0)
    cy      = entity.get("cy", 0)
    sides   = entity.get("sides", entity.get("n", 6))
    radius  = entity["radius"]
    # 起始角: 平底六边形从 -30° (平边朝下)，其余从 -90° (顶点朝上)
    start_angle = entity.get("start_angle", -90 if sides != 6 else -90)
    pts = []
    for i in range(sides):
        a = math.radians(start_angle + 360 / sides * i)
        pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    msp.add_lwpolyline(pts, close=True, dxfattribs=_attribs(entity, "OUTLINE"))


def draw_polygon_hole(msp, entity: dict):
    """正多边形孔 (内孔轮廓)."""
    draw_polygon(msp, {**entity, "layer": entity.get("layer", "OUTLINE")})


def draw_bolt_circle(msp, entity: dict):
    """
    均布螺栓孔圆 (GB/T 4458 标准画法).
    孔从 90° (顶部) 开始均布，避免与水平轴重合。
    """
    cx      = entity.get("cx", 0)
    cy      = entity.get("cy", 0)
    pcd     = entity["pcd"]             # 节圆直径
    holes   = entity.get("holes", entity.get("n", 4))
    h_dia   = entity.get("hole_diameter", 10)
    layer   = entity.get("layer", "OUTLINE")
    c_layer = entity.get("center_layer", "CENTER")
    # 节圆 (中心圆, 细点画线)
    if entity.get("draw_pcd", True):
        msp.add_circle((cx, cy), pcd / 2, dxfattribs={"layer": c_layer,
                                                         "lineweight": LW_THIN})
    # 螺栓孔，从 90° 开始，保证无孔与水平轴线重合
    for i in range(holes):
        angle = math.radians(90 + 360 / holes * i)
        hx = cx + (pcd / 2) * math.cos(angle)
        hy = cy + (pcd / 2) * math.sin(angle)
        msp.add_circle((hx, hy), h_dia / 2,
                       dxfattribs={"layer": layer})
    # 中心标记
    if entity.get("draw_center_lines", True):
        cl_attr = {"layer": c_layer, "lineweight": LW_THIN}
        ext = pcd / 2 + h_dia + 5
        msp.add_line((cx - ext, cy), (cx + ext, cy), dxfattribs=cl_attr)
        msp.add_line((cx, cy - ext), (cx, cy + ext), dxfattribs=cl_attr)


def draw_center_mark(msp, entity: dict):
    """
    圆形中心标记 (十字中心线, GB/T 4458 规范).
    中心线应超过轮廓线约 3-5mm。
    """
    cx   = entity.get("cx", entity.get("center", [0, 0])[0])
    cy   = entity.get("cy", entity.get("center", [0, 0])[1])
    size = entity.get("size", 10)
    overshoot = entity.get("overshoot", 3)  # 超出量
    layer  = entity.get("layer", "CENTER")
    attr   = {"layer": layer, "lineweight": LW_THIN}
    total  = size + overshoot
    # 中心线要超出轮廓线外约 3-5mm
    msp.add_line((cx - total, cy), (cx + total, cy), dxfattribs=attr)
    msp.add_line((cx, cy - total), (cx, cy + total), dxfattribs=attr)


def draw_counterbore(msp, entity: dict):
    """
    沉孔（counterbore）——两个同心圆 + 深度符号.
    按国标，在视图中表示为两个同心圆。
    cx/cy or center: 孔中心
    c_bore_diameter / bore_dia: 沉孔直径
    pilot_diameter / hole_dia: 通孔直径
    """
    if "center" in entity:
        cx, cy = entity["center"][0], entity["center"][1]
    else:
        cx = entity.get("cx", 0)
        cy = entity.get("cy", 0)
    c_dia = entity.get("c_bore_diameter", entity.get("bore_dia", 20))
    p_dia = entity.get("pilot_diameter",  entity.get("hole_dia", 10))
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer}
    msp.add_circle((cx, cy), c_dia / 2, dxfattribs=attr)
    msp.add_circle((cx, cy), p_dia / 2, dxfattribs=attr)
    # 中心标记
    ext = c_dia / 2 + 5
    cl  = {"layer": "CENTER", "lineweight": LW_THIN}
    msp.add_line((cx - ext, cy), (cx + ext, cy), dxfattribs=cl)
    msp.add_line((cx, cy - ext), (cx, cy + ext), dxfattribs=cl)


def draw_countersink(msp, entity: dict):
    """
    埋头孔（countersink）——两个同心圆.
    outer_diameter / sink_dia: 大径
    inner_diameter / hole_dia: 小径
    sink_angle: 锥角 (默认90°)
    """
    if "center" in entity:
        cx, cy = entity["center"][0], entity["center"][1]
    else:
        cx = entity.get("cx", 0)
        cy = entity.get("cy", 0)
    o_dia = entity.get("outer_diameter", entity.get("sink_dia", 20))
    i_dia = entity.get("inner_diameter", entity.get("hole_dia", 10))
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer}
    msp.add_circle((cx, cy), o_dia / 2, dxfattribs=attr)
    msp.add_circle((cx, cy), i_dia / 2, dxfattribs=attr)
    ext = o_dia / 2 + 5
    cl  = {"layer": "CENTER", "lineweight": LW_THIN}
    msp.add_line((cx - ext, cy), (cx + ext, cy), dxfattribs=cl)
    msp.add_line((cx, cy - ext), (cx, cy + ext), dxfattribs=cl)


def draw_chamber(msp, entity: dict):
    """轴端退刀槽 / 倒角槽."""
    ox    = entity.get("origin", [0, 0])[0]
    oy    = entity.get("origin", [0, 0])[1]
    width = entity.get("width", 30)
    depth = entity.get("depth", 5)
    h     = entity.get("height", 5)
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer, "lineweight": LW_THICK}
    msp.add_lwpolyline(
        [(ox, oy), (ox + width, oy), (ox + width, oy + h), (ox, oy + h)],
        close=True, dxfattribs=attr
    )
    r = min(depth, h) * 0.3
    if r > 0:
        msp.add_arc((ox + r, oy + r), r, 180, 270, dxfattribs=attr)
        msp.add_arc((ox + width - r, oy + r), r, 270, 360, dxfattribs=attr)


def draw_keyway(msp, entity: dict):
    """
    键槽（GB/T 1095）——矩形槽 + 圆角端.
    origin = 槽左下角; width = 槽宽; height = 槽深; rounded = 两端半圆
    v7.0 修复: rounded 模式正确绘制端铣半圆弧键槽
    """
    ox    = entity.get("origin", [0, 0])[0]
    oy    = entity.get("origin", [0, 0])[1]
    w     = entity.get("width", 8)
    h     = entity.get("height", 4)
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer, "lineweight": LW_THICK}
    if entity.get("rounded", True):
        # 端铣键槽: 两端为半圆弧（圆弧半径 = h/2）
        r = h / 2
        # 左端半圆弧中心
        cx1 = ox + r
        cy1 = oy + r
        # 右端半圆弧中心
        cx2 = ox + w - r
        cy2 = oy + r
        # 上边直线（从左弧顶到右弧顶）
        msp.add_line((cx1, oy + h), (cx2, oy + h), dxfattribs=attr)
        # 下边直线（从左弧底到右弧底）
        msp.add_line((cx2, oy), (cx1, oy), dxfattribs=attr)
        # 左端半圆弧（从下到上，逆时针）
        msp.add_arc((cx1, cy1), r, 180, 0, dxfattribs=attr)
        # 右端半圆弧（从上到下，逆时针）
        msp.add_arc((cx2, cy2), r, 0, 180, dxfattribs=attr)
    else:
        # 平底键槽: 纯矩形
        msp.add_lwpolyline(
            [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)],
            close=True, dxfattribs=attr
        )


def draw_leader(msp, entity: dict):
    """
    引线标注（GB/T 4458 规范: 箭头→折线→文字）.
    points: 箭头端 → 弯折点 → 文字端
    text: 注释文字
    """
    points = [tuple(p) for p in entity["points"]]
    text   = entity.get("text", "")
    layer  = entity.get("layer", "TEXT")
    attr   = {"layer": layer, "lineweight": LW_THIN}
    msp.add_leader(points, dxfattribs=attr)
    if text:
        last_pt = points[-1]
        msp.add_text(text, dxfattribs={"layer": layer, "height": TEXT_HEIGHT_BODY}).set_placement(
            (last_pt[0] + 1, last_pt[1] + 1), align=TextEntityAlignment.LEFT
        )


def draw_mtext(msp, entity: dict):
    """多行文字（MTEXT）."""
    text     = entity["content"]
    position = tuple(entity["position"])
    width    = entity.get("width", 100)
    height   = entity.get("height", TEXT_HEIGHT_BODY)
    layer    = entity.get("layer", "TEXT")
    attr     = {"layer": layer, "char_height": height}
    mtxt = msp.add_mtext(text, dxfattribs=attr)
    mtxt.set_location(position, column_width=width)


def draw_wire(msp, entity: dict):
    """电气导线（水平/垂直, IEC 规范）."""
    start = tuple(entity["start"])
    end   = tuple(entity["end"])
    layer = entity.get("layer", "WIRE")
    msp.add_line(start, end, dxfattribs={"layer": layer, "lineweight": LW_THIN})


def draw_bus_line(msp, entity: dict):
    """电气总线（粗实线）."""
    start = tuple(entity["start"])
    end   = tuple(entity["end"])
    layer = entity.get("layer", "WIRE")
    msp.add_line(start, end, dxfattribs={"layer": layer, "lineweight": LW_THICK})


def draw_grid(msp, entity: dict):
    """参考网格（细实线）."""
    x_min   = entity.get("x", entity.get("x_min", 0))
    y_min   = entity.get("y", entity.get("y_min", 0))
    x_max   = entity.get("x_max", x_min + entity.get("width", 100))
    y_max   = entity.get("y_max", y_min + entity.get("height", 100))
    spacing = entity.get("spacing", 10)
    layer   = entity.get("layer", "GRID")
    attr    = {"layer": layer, "lineweight": LW_HAIR}
    x = x_min
    while x <= x_max + 1e-6:
        msp.add_line((x, y_min), (x, y_max), dxfattribs=attr)
        x += spacing
    y = y_min
    while y <= y_max + 1e-6:
        msp.add_line((x_min, y), (x_max, y), dxfattribs=attr)
        y += spacing


# ═══════════════════════════════════════════════════════
#  国标图框与标题栏（GB/T 14689 + GB/T 10609.1）
# ═══════════════════════════════════════════════════════

def draw_border(msp, entity: dict):
    """
    标准图框（GB/T 14689）:
    外框（细实线） + 内框（粗实线）+ 分区标记
    支持 size: A0/A1/A2/A3/A4, binding: True/False
    """
    size       = entity.get("size", "A3")
    binding    = entity.get("binding", True)    # 是否留装订边
    zone_marks = entity.get("zone_marks", True) # 是否画分区标记
    layer      = entity.get("layer", "BORDER")

    if size in PAPER_SIZES:
        w, h = PAPER_SIZES[size]
    else:
        w = entity.get("width", 420)
        h = entity.get("height", 297)

    # 偏移原点
    ox = entity.get("x", 0)
    oy = entity.get("y", 0)

    # 选边距
    if binding:
        margins = FRAME_MARGINS_WITH_BINDING.get(size, (25, 5, 5, 5))
    else:
        margins = FRAME_MARGINS_NO_BINDING.get(size, (10, 5, 5, 5))
    ml, mb, mr, mt = margins

    # 外框（细实线）
    outer_attr = {"layer": layer, "lineweight": LW_THIN}
    msp.add_lwpolyline(
        [(ox, oy), (ox+w, oy), (ox+w, oy+h), (ox, oy+h)],
        close=True, dxfattribs=outer_attr
    )

    # 内框（粗实线）
    inner_attr = {"layer": layer, "lineweight": LW_THICK}
    ix, iy = ox + ml, oy + mb
    iw, ih = w - ml - mr, h - mb - mt
    msp.add_lwpolyline(
        [(ix, iy), (ix+iw, iy), (ix+iw, iy+ih), (ix, iy+ih)],
        close=True, dxfattribs=inner_attr
    )

    # 分区标记（可选）
    if zone_marks:
        zone_attr = {"layer": layer, "lineweight": LW_HAIR}
        zone_h = 5
        n_cols = max(4, int(w / 50))
        n_rows = max(2, int(h / 50))
        for i in range(1, n_cols):
            zx = ox + w * i / n_cols
            msp.add_line((zx, oy), (zx, oy + zone_h), dxfattribs=zone_attr)
            msp.add_line((zx, oy + h - zone_h), (zx, oy + h), dxfattribs=zone_attr)
        for j in range(1, n_rows):
            zy = oy + h * j / n_rows
            msp.add_line((ox, zy), (ox + zone_h, zy), dxfattribs=zone_attr)
            msp.add_line((ox + w - zone_h, zy), (ox + w, zy), dxfattribs=zone_attr)
        # 列标号 (1,2,3...)
        text_a = {"layer": "TEXT", "height": 3}
        for i in range(n_cols):
            zx = ox + w * (i + 0.5) / n_cols
            msp.add_text(str(i+1), dxfattribs=text_a).set_placement(
                (zx - 1.5, oy + zone_h * 0.3), align=TextEntityAlignment.LEFT)
            msp.add_text(str(i+1), dxfattribs=text_a).set_placement(
                (zx - 1.5, oy + h - zone_h + 0.5), align=TextEntityAlignment.LEFT)
        # 行标号 (A,B,C...)
        letters = "ABCDEFGHI"
        for j in range(n_rows):
            zy = oy + h * (j + 0.5) / n_rows
            ch = letters[j] if j < len(letters) else str(j+1)
            msp.add_text(ch, dxfattribs=text_a).set_placement(
                (ox + zone_h * 0.3, zy - 1.5), align=TextEntityAlignment.LEFT)
            msp.add_text(ch, dxfattribs=text_a).set_placement(
                (ox + w - zone_h + 0.3, zy - 1.5), align=TextEntityAlignment.LEFT)


def draw_title_block(msp, doc, entity: dict):
    """
    标题栏（ISO 7200 / GB/T 10609.1 双规范）.
    当 standard="ISO" 时使用英文字段标签，否则使用 GB 中文标签。
    按 GB/ISO 标准: 位于图框内框右下角, 总宽180mm, 总高56mm.
    支持字段: title, drawing_no, scale, material, unit, designer,
              checker, approver, date, paper_size, sheet, total_sheets,
              projection, standard
    也支持自定义 rows/cols 简化表格模式（legacy）。
    """
    # 参数
    size      = entity.get("size", "A3")
    binding   = entity.get("binding", True)
    layer     = entity.get("layer", "BORDER")
    t_layer   = entity.get("text_layer", "TEXT")
    standard  = entity.get("standard", "GB")        # v8.0: ISO 或 GB
    projection = entity.get("projection", "first")   # v8.0: first 或 third

    if size in PAPER_SIZES:
        pw, ph = PAPER_SIZES[size]
    else:
        pw = entity.get("width",  entity.get("paper_width",  420))
        ph = entity.get("height", entity.get("paper_height", 297))

    ox = entity.get("x", 0)
    oy = entity.get("y", 0)

    if binding:
        margins = FRAME_MARGINS_WITH_BINDING.get(size, (25, 5, 5, 5))
    else:
        margins = FRAME_MARGINS_NO_BINDING.get(size, (10, 5, 5, 5))
    ml, mb, mr, mt = margins

    # 内框右下角坐标
    ix = ox + ml
    iy = oy + mb
    iw = pw - ml - mr
    ih = ph - mb - mt

    tb_w = min(180, iw)    # 标题栏宽
    tb_h = 56              # 标题栏高

    # 标题栏左下角
    tbx = ix + iw - tb_w
    tby = iy

    b_attr = {"layer": layer, "lineweight": LW_THICK}

    def cell_rect(x, y, w, h, thin=False):
        """Draw a cell rectangle."""
        lw = LW_THIN if thin else LW_THICK
        msp.add_lwpolyline(
            [(x, y), (x+w, y), (x+w, y+h), (x, y+h)],
            close=True,
            dxfattribs={"layer": layer, "lineweight": lw}
        )

    def cell_text(text, x, y, h=TEXT_HEIGHT_BODY, vcenter=None):
        """Draw text in a cell (bottom-left padded)."""
        pad = 1.5
        ty  = vcenter if vcenter is not None else y + pad
        msp.add_text(str(text), dxfattribs={"layer": t_layer, "height": h}).set_placement(
            (x + pad, ty), align=TextEntityAlignment.LEFT
        )

    # ── 布局定义 (ISO 7200 / GB/T 10609.1 简化, 从底向上) ──────────────
    # 行高: 8mm × 7行 = 56mm
    rh = 8.0

    # v8.0: 根据标准体系选择字段标签
    if standard == "ISO":
        headers1 = ["Part No.", "Designation", "Material", "Phase", "Mass", "Remark"]
    else:
        headers1 = ["件号", "名称", "材料", "阶段标记", "重量", "备注"]

    # 第1行（底部）: 件号(20) | 名称(60) | 材料(30) | 阶段(20) | 重量(15) | 备注(35)
    col_w = [20, 60, 30, 20, 15, tb_w - 145]

    row1_y = tby
    x_cur  = tbx
    values1  = [
        entity.get("part_no", ""),
        entity.get("title",   ""),
        entity.get("material",""),
        entity.get("stage",   ""),
        entity.get("weight",  ""),
        entity.get("remark",  ""),
    ]
    for i, (cw, hdr, val) in enumerate(zip(col_w, headers1, values1)):
        cell_rect(x_cur, row1_y, cw, rh)
        cell_text(hdr,   x_cur, row1_y + rh * 0.55, h=2.5)  # 上半行标签
        cell_text(val,   x_cur, row1_y,              h=TEXT_HEIGHT_BODY)  # 下半行值
        x_cur += cw

    # 第2行: 图号(100) | 比例(40) | 图幅(40)
    row2_y = tby + rh
    cell_rect(tbx,       row2_y, 100, rh)
    cell_rect(tbx + 100, row2_y, 40,  rh)
    cell_rect(tbx + 140, row2_y, tb_w - 140, rh)
    if standard == "ISO":
        cell_text("Drawing No.", tbx,       row2_y + rh * 0.55, h=2.5)
        cell_text("Scale",       tbx + 100, row2_y + rh * 0.55, h=2.5)
        cell_text("Size",        tbx + 140, row2_y + rh * 0.55, h=2.5)
    else:
        cell_text("图号",  tbx,       row2_y + rh * 0.55, h=2.5)
        cell_text("比例",  tbx + 100, row2_y + rh * 0.55, h=2.5)
        cell_text("图幅",  tbx + 140, row2_y + rh * 0.55, h=2.5)
    cell_text(entity.get("drawing_no", ""), tbx,       row2_y, h=TEXT_HEIGHT_BODY)
    cell_text(entity.get("scale",      ""), tbx + 100, row2_y, h=TEXT_HEIGHT_BODY)
    cell_text(entity.get("paper_size", size), tbx + 140, row2_y, h=TEXT_HEIGHT_BODY)

    # 第3行: 单位名称(100) | 共X张第X张(80)
    row3_y = tby + 2 * rh
    cell_rect(tbx,       row3_y, 100,          rh)
    cell_rect(tbx + 100, row3_y, tb_w - 100,   rh)
    if standard == "ISO":
        cell_text("Organization", tbx,        row3_y + rh * 0.55, h=2.5)
        cell_text("Sheet",        tbx + 100,  row3_y + rh * 0.55, h=2.5)
    else:
        cell_text("单位",    tbx,        row3_y + rh * 0.55, h=2.5)
        cell_text("图纸序号", tbx + 100,  row3_y + rh * 0.55, h=2.5)
    cell_text(entity.get("unit", ""), tbx,       row3_y, h=TEXT_HEIGHT_BODY)
    total_s = entity.get("total_sheets", "")
    sheet_s = entity.get("sheet", "")
    cell_text(f"共{total_s}张第{sheet_s}张" if total_s or sheet_s else "",
              tbx + 100, row3_y, h=TEXT_HEIGHT_BODY)

    # 第4-7行: 签字区 (设计/校对/审核/批准, 各一行)
    if standard == "ISO":
        sig_labels = ["Designed", "Checked", "Reviewed", "Approved"]
        date_label = "Date"
    else:
        sig_labels = ["设计", "校对", "审核", "批准"]
        date_label = "日期"

    sig_rows = [
        (sig_labels[0], entity.get("designer", entity.get("designed_by", "")),
                       entity.get("design_date",  "")),
        (sig_labels[1], entity.get("checker",  entity.get("checked_by",  "")),
                       entity.get("check_date",   "")),
        (sig_labels[2], entity.get("reviewer", ""), entity.get("review_date",  "")),
        (sig_labels[3], entity.get("approver", ""), entity.get("approve_date", "")),
    ]
    for idx, (label, name, date) in enumerate(sig_rows):
        ry = tby + (3 + idx) * rh
        cell_rect(tbx,       ry, 30,          rh)
        cell_rect(tbx + 30,  ry, 40,          rh)
        cell_rect(tbx + 70,  ry, 30,          rh)
        cell_rect(tbx + 100, ry, tb_w - 100,  rh)
        cell_text(label, tbx,       ry, h=TEXT_HEIGHT_BODY)
        cell_text(name,  tbx + 30,  ry, h=TEXT_HEIGHT_BODY)
        cell_text(date_label, tbx + 70,  ry + rh * 0.55, h=2.5)
        cell_text(date,  tbx + 70,  ry, h=TEXT_HEIGHT_SMALL)
        # 第4行右侧: 图样标题大字
        if idx == 0:
            # 大标题文字（图名）竖跨 4 行右侧区域
            t_name = entity.get("title", "未命名图样")
            msp.add_text(t_name,
                dxfattribs={"layer": t_layer, "height": TEXT_HEIGHT_TITLE}).set_placement(
                (tbx + 100 + 2, tby + 3 * rh + 2), align=TextEntityAlignment.LEFT
            )

    # 最外轮廓粗线框
    cell_rect(tbx, tby, tb_w, tb_h, thin=False)


# ═══════════════════════════════════════════════════════
#  标注系列（GB/T 4458 国标规范）
# ═══════════════════════════════════════════════════════

def draw_dimension_aligned(msp, doc, entity: dict):
    """对齐标注（平行于被测要素）."""
    p1    = tuple(entity["p1"])
    p2    = tuple(entity["p2"])
    offset = entity.get("offset", entity.get("dimline_offset", 10))
    layer  = entity.get("layer", "DIM")
    dimstyle = entity.get("dimstyle", "EZDXF")
    # 计算垂直偏移方向
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    nx = -dy / length * offset
    ny =  dx / length * offset
    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2
    base = (mid_x + nx, mid_y + ny)
    try:
        dim = msp.add_aligned_dim(p1=p1, p2=p2, distance=offset,
                                   dimstyle=dimstyle,
                                   dxfattribs={"layer": layer})
        dim.render()
    except Exception:
        try:
            dim = msp.add_linear_dim(base=base, p1=p1, p2=p2,
                                      dimstyle=dimstyle, dxfattribs={"layer": layer})
            dim.render()
        except Exception as e:
            print(f"[WARN] Aligned dim skipped: {e}", file=sys.stderr)


def draw_dimension_radius(msp, doc, entity: dict):
    """半径标注（R前缀）."""
    cx       = tuple(entity["center"])
    radius   = entity["radius"]
    layer    = entity.get("layer", "DIM")
    dimstyle = entity.get("dimstyle", "EZDXF")
    try:
        dim = msp.add_radial_dim(center=cx, radius=radius, leader=10,
                                  dimstyle=dimstyle, dxfattribs={"layer": layer})
        dim.render()
    except Exception as e:
        print(f"[WARN] Radius dim skipped: {e}", file=sys.stderr)


def draw_dimension_diameter(msp, doc, entity: dict):
    """直径标注（Φ前缀, GB 标准）."""
    cx       = tuple(entity["center"])
    radius   = entity["radius"]
    angle    = entity.get("angle", 45)
    layer    = entity.get("layer", "DIM")
    dimstyle = entity.get("dimstyle", "EZDXF")
    try:
        dim = msp.add_diameter_dim(center=cx, radius=radius,
                                    angle=math.radians(angle),
                                    dimstyle=dimstyle, dxfattribs={"layer": layer})
        dim.render()
    except Exception as e:
        print(f"[WARN] Diameter dim skipped: {e}", file=sys.stderr)


def draw_dimension_angular(msp, doc, entity: dict):
    """角度标注（度数）."""
    vertex   = tuple(entity["vertex"])
    start_pt = tuple(entity.get("start_pt", entity.get("p1", (0, 0))))
    end_pt   = tuple(entity.get("end_pt",   entity.get("p2", (1, 0))))
    layer    = entity.get("layer", "DIM")
    dimstyle = entity.get("dimstyle", "EZDXF")
    try:
        dim = msp.add_angular_dim(base=vertex, line1=start_pt, line2=end_pt,
                                   dimstyle=dimstyle, dxfattribs={"layer": layer})
        dim.render()
    except Exception as e:
        print(f"[WARN] Angular dim skipped: {e}", file=sys.stderr)


# ═══════════════════════════════════════════════════════
#  国标新增: 粗糙度、公差、焊接、断裂线
# ═══════════════════════════════════════════════════════

def draw_surface_roughness(msp, entity: dict):
    """
    表面粗糙度符号（GB/T 131）.
    x, y: 符号顶点（接触轮廓的点）
    ra: Ra 值，如 1.6, 3.2, 6.3
    symbol_type: 'basic'=基本, 'no_removal'=不去除, 'removal'=去除材料
    orientation: 'up'(默认,指向下方轮廓), 'down', 'left', 'right'
    """
    x    = entity.get("x", 0)
    y    = entity.get("y", 0)
    ra   = entity.get("ra", entity.get("Ra", 3.2))
    sym  = entity.get("symbol_type", "basic")
    ori  = entity.get("orientation", "up")
    h    = entity.get("symbol_height", 4)    # 符号高度
    layer = entity.get("layer", "SURFACE")
    attr  = {"layer": layer, "lineweight": LW_THIN}

    # 各方向旋转角
    rot_map = {"up": 0, "right": 90, "down": 180, "left": 270}
    angle_deg = rot_map.get(ori, 0)
    angle_rad = math.radians(angle_deg)

    def rotated(px, py):
        rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
        ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
        return (x + rx, y + ry)

    # 基本符号 (60° V形, 顶点在(x,y))
    half_w = h * math.tan(math.radians(30))   # 底部半宽 = h·tan30°
    left_top  = rotated(-half_w, h)
    right_top = rotated(+half_w, h)
    msp.add_line(left_top,  (x, y), dxfattribs=attr)
    msp.add_line((x, y),    right_top, dxfattribs=attr)

    # 水平延伸线（从右斜线顶端向右延伸）
    h_ext = entity.get("extension", h * 1.5)
    ext_end = rotated(half_w + h_ext, h)
    msp.add_line(right_top, ext_end, dxfattribs=attr)

    # 去除材料符号 (在左斜线顶加水平短线)
    if sym == "removal":
        left_ext = rotated(-half_w - h * 0.5, h)
        msp.add_line(left_top, left_ext, dxfattribs=attr)

    # Ra 文字
    ra_text_pos = rotated(half_w + 1, h + 1.5)
    msp.add_text(f"Ra{ra}",
                 dxfattribs={"layer": "TEXT", "height": TEXT_HEIGHT_SMALL}).set_placement(
        ra_text_pos, align=TextEntityAlignment.LEFT
    )


def draw_tolerance_frame(msp, entity: dict):
    """
    形位公差框格（GB/T 1182）.
    标准格式: [符号格(8×8)] [公差值格(变宽×8)] [基准格(8×8)可选]
    x, y: 框格左下角
    tolerances: list of {symbol, value, datum}
    """
    x    = entity.get("x", 0)
    y    = entity.get("y", 0)
    tols = entity.get("tolerances", [{"symbol": "⊥", "value": "0.05", "datum": "A"}])
    row_h = entity.get("row_height", 8)
    layer = entity.get("layer", "TOLERANCE")
    attr  = {"layer": layer, "lineweight": LW_THIN}

    for i, t in enumerate(tols):
        ry     = y + row_h * i
        sym    = t.get("symbol", "□")
        val    = t.get("value", "")
        datum  = t.get("datum", "")
        # 估算各格宽度
        sym_w  = 8
        val_w  = max(20, len(str(val)) * 3.5 + 4)
        dat_w  = 8 if datum else 0
        total_w = sym_w + val_w + dat_w

        # 符号格
        msp.add_lwpolyline(
            [(x, ry), (x+sym_w, ry), (x+sym_w, ry+row_h), (x, ry+row_h)],
            close=True, dxfattribs=attr)
        msp.add_text(sym, dxfattribs={"layer": layer, "height": 4}).set_placement(
            (x + 1, ry + 2), align=TextEntityAlignment.LEFT)

        # 公差值格
        msp.add_lwpolyline(
            [(x+sym_w, ry), (x+sym_w+val_w, ry),
             (x+sym_w+val_w, ry+row_h), (x+sym_w, ry+row_h)],
            close=True, dxfattribs=attr)
        msp.add_text(str(val), dxfattribs={"layer": layer, "height": TEXT_HEIGHT_BODY}).set_placement(
            (x+sym_w+2, ry+2), align=TextEntityAlignment.LEFT)

        # 基准格（可选）
        if datum:
            msp.add_lwpolyline(
                [(x+sym_w+val_w, ry), (x+total_w, ry),
                 (x+total_w, ry+row_h), (x+sym_w+val_w, ry+row_h)],
                close=True, dxfattribs=attr)
            msp.add_text(str(datum),
                         dxfattribs={"layer": layer, "height": TEXT_HEIGHT_BODY}).set_placement(
                (x+sym_w+val_w+1, ry+2), align=TextEntityAlignment.LEFT)


def draw_weld_symbol(msp, entity: dict):
    """
    焊接符号（GB/T 324）.
    x, y: 箭头端; ref_x, ref_y: 另一端
    weld_type: 'butt'(对接), 'fillet'(角焊), 'plug', 'seam'
    arrow_side: 符号在箭头侧(True)或另一侧(False)
    size: 焊缝尺寸 (mm)
    """
    x   = entity.get("x", 0)
    y   = entity.get("y", 0)
    rx  = entity.get("ref_x", x + 30)
    ry2 = entity.get("ref_y", y + 15)
    weld_type  = entity.get("weld_type", "fillet")
    arrow_side = entity.get("arrow_side", True)
    size       = entity.get("size", "")
    layer      = entity.get("layer", "WELD")
    attr       = {"layer": layer, "lineweight": LW_THIN}

    # 引线（带箭头）
    msp.add_line((x, y), (rx, ry2), dxfattribs=attr)
    # 箭头
    dx = rx - x; dy = ry2 - y
    length = math.hypot(dx, dy)
    if length > 1e-9:
        ux, uy = dx/length, dy/length
        px, py = -uy, ux   # 垂直方向
        al = 3  # 箭头长度
        msp.add_line((x, y), (x + al*ux + 0.8*al*px, y + al*uy + 0.8*al*py), dxfattribs=attr)
        msp.add_line((x, y), (x + al*ux - 0.8*al*px, y + al*uy - 0.8*al*py), dxfattribs=attr)

    # 基准线（水平，在参考端）
    msp.add_line((rx, ry2), (rx + 20, ry2), dxfattribs=attr)
    msp.add_line((rx, ry2 + 0.5), (rx + 20, ry2 + 0.5), dxfattribs={"layer": layer, "lineweight": LW_HAIR})

    # 焊接符号绘制
    sy  = ry2 if arrow_side else ry2 + 5
    sym_x = rx + 2
    if weld_type == "fillet":
        # 角焊符号：三角形
        tri = [(sym_x, sy), (sym_x+4, sy), (sym_x, sy+4)]
        msp.add_lwpolyline(tri, close=True, dxfattribs=attr)
    elif weld_type == "butt":
        # 对接符号：竖线
        msp.add_line((sym_x+2, sy-3), (sym_x+2, sy+3), dxfattribs=attr)
    elif weld_type == "seam":
        # 缝焊：两平行线
        msp.add_line((sym_x, sy+1), (sym_x+6, sy+1), dxfattribs=attr)
        msp.add_line((sym_x, sy+3), (sym_x+6, sy+3), dxfattribs=attr)

    # 焊缝尺寸文字
    if size:
        msp.add_text(str(size), dxfattribs={"layer": layer, "height": TEXT_HEIGHT_SMALL}).set_placement(
            (rx + 2, ry2 - 5 if arrow_side else ry2 + 5), align=TextEntityAlignment.LEFT)


def draw_break_line(msp, entity: dict):
    """
    断裂线（GB/T 4457: 用于截断过长视图）.
    start, end: 两端点
    amplitude: 波浪幅度 (默认3mm)
    style: 'wavy'(波浪线) 或 'zigzag'(锯齿线)
    """
    start = tuple(entity["start"])
    end   = tuple(entity["end"])
    amp   = entity.get("amplitude", 3)
    style = entity.get("style", "wavy")
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer, "lineweight": LW_THIN}

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    ux, uy = dx/length, dy/length
    px, py = -uy, ux   # 垂直方向

    n_cycles = max(3, int(length / 10))
    pts = []
    if style == "wavy":
        for i in range(n_cycles * 8 + 1):
            t = i / (n_cycles * 8)
            along = t * length
            perp  = amp * math.sin(t * n_cycles * 2 * math.pi)
            pts.append((start[0] + along * ux + perp * px,
                        start[1] + along * uy + perp * py))
    else:  # zigzag
        for i in range(n_cycles * 2 + 1):
            t = i / (n_cycles * 2)
            along = t * length
            perp  = amp * (1 if i % 2 == 0 else -1)
            pts.append((start[0] + along * ux + perp * px,
                        start[1] + along * uy + perp * py))

    if pts:
        msp.add_lwpolyline(pts, dxfattribs=attr)


def draw_section_line(msp, entity: dict):
    """
    剖切符号线（GB/T 4457: 切割面标记 + 字母 + 箭头方向）.
    p1, p2: 剖切线端点
    label: 字母标记，如 "A" → 生成 A-A
    arrow_offset: 箭头偏移量 (默认 6)
    """
    p1    = tuple(entity["p1"])
    p2    = tuple(entity["p2"])
    label = entity.get("label", "A")
    arrow = entity.get("arrow_offset", 6)
    layer = entity.get("layer", "SECTION")
    attr  = {"layer": layer, "lineweight": LW_THICK}

    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    nx = -dy / length * arrow; ny = dx / length * arrow

    # 主切割线（粗点画线用 SECTION 图层 CENTER 线型）
    msp.add_line(p1, p2, dxfattribs={"layer": layer, "lineweight": LW_THICK})

    # 箭头线（显示剖视方向）- 两端
    for pt in [p1, p2]:
        msp.add_line((pt[0] + nx, pt[1] + ny), pt, dxfattribs=attr)
        msp.add_line((pt[0] - nx, pt[1] - ny), pt, dxfattribs=attr)

    # 字母标记
    if label:
        t_attr = {"layer": "TEXT", "height": TEXT_HEIGHT_TITLE}
        offset = arrow + 5
        msp.add_text(label,
                     dxfattribs=t_attr).set_placement(
            (p1[0] + nx + offset, p1[1] + ny + offset),
            align=TextEntityAlignment.LEFT)
        msp.add_text(label,
                     dxfattribs=t_attr).set_placement(
            (p2[0] + nx + offset, p2[1] + ny + offset),
            align=TextEntityAlignment.LEFT)


def draw_center_hole(msp, entity: dict):
    """
    中心孔符号（GB/T 4459.5）.
    x, y: 轴端面中心
    type: 'A'(无护锥), 'B'(有护锥), 'R'(弧形)
    d: 导入孔径; D: 锥孔大径
    """
    x    = entity.get("x", 0)
    y    = entity.get("y", 0)
    htype = entity.get("type", "A")
    d    = entity.get("d", 2)
    D    = entity.get("D", d * 2.12)   # 60°锥时 D = d/sin30° ≈ 2d
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer, "lineweight": LW_THIN}

    # 简化：画两个同心圆 + 标注
    msp.add_circle((x, y), d / 2, dxfattribs=attr)
    msp.add_circle((x, y), D / 2, dxfattribs={"layer": layer, "lineweight": LW_HAIR})
    label = f"{htype}{d}/{D:.2f}"
    msp.add_text(label, dxfattribs={"layer": "TEXT", "height": TEXT_HEIGHT_SMALL}).set_placement(
        (x + D / 2 + 2, y + 1), align=TextEntityAlignment.LEFT)


# ═══════════════════════════════════════════════════════
#  机械零件（修复精度）
# ═══════════════════════════════════════════════════════

def draw_spring(msp, entity: dict):
    """
    螺旋压缩弹簧前视图（正弦波剪影）.
    修复: y1 坐标加上 cy 偏移（v5.0 bug）
    cx, cy: 中心点; outer_radius, wire_diameter, coils, length
    """
    cx      = entity.get("cx", 0)
    cy      = entity.get("cy", 0)
    r_outer = entity.get("outer_radius", 40)
    r_wire  = entity.get("wire_diameter", 4) / 2
    coils   = entity.get("coils", 8)
    total_h = entity.get("length", 80)
    layer   = entity.get("layer", "OUTLINE")
    attr    = {"layer": layer, "lineweight": LW_THICK}
    steps   = max(int(coils * 36), 72)

    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        x0 = cx + r_outer * math.cos(t0 * coils * 2 * math.pi)
        y0 = cy + t0 * total_h + r_wire * math.sin(t0 * coils * 2 * math.pi)
        x1 = cx + r_outer * math.cos(t1 * coils * 2 * math.pi)
        y1 = cy + t1 * total_h + r_wire * math.sin(t1 * coils * 2 * math.pi)   # 修复: 加 cy
        try:
            msp.add_line((x0, y0), (x1, y1), dxfattribs=attr)
        except Exception:
            pass

    # 两端死圈（水平直线, 粗实线）
    msp.add_line((cx - r_outer, cy),           (cx + r_outer, cy),           dxfattribs=attr)
    msp.add_line((cx - r_outer, cy + total_h), (cx + r_outer, cy + total_h), dxfattribs=attr)
    # 包络线（细实线）
    env = {"layer": layer, "lineweight": LW_THIN}
    msp.add_line((cx - r_outer, cy), (cx - r_outer, cy + total_h), dxfattribs=env)
    msp.add_line((cx + r_outer, cy), (cx + r_outer, cy + total_h), dxfattribs=env)


def draw_gear(msp, entity: dict):
    """
    直齿圆柱齿轮（GB/T 4459.2 规定画法）.
    标准画法：
    - 齿顶圆: 粗实线
    - 分度圆: 细点画线
    - 齿根圆: 细实线（在剖视图中为粗实线）
    - 齿形: 仅在局部区域画，其余用示意轮廓
    cx, cy, outer_radius(齿顶圆半径), root_radius(齿根圆半径),
    pitch_radius(分度圆半径), hub_radius(轮毂半径), bore_radius(轴孔半径),
    num_teeth(齿数)
    """
    cx        = entity.get("cx", 0)
    cy        = entity.get("cy", 0)
    outer_r   = entity.get("outer_radius", 50)
    root_r    = entity.get("root_radius",  outer_r * 0.82)
    pitch_r   = entity.get("pitch_radius", (outer_r + root_r) / 2)
    hub_r     = entity.get("hub_radius",   outer_r * 0.25)
    bore_r    = entity.get("bore_radius",  outer_r * 0.12)
    num_teeth = entity.get("num_teeth",    24)
    layer     = entity.get("layer", "OUTLINE")

    # 1. 齿顶圆（粗实线）
    msp.add_circle((cx, cy), outer_r,
                   dxfattribs={"layer": layer, "lineweight": LW_THICK})
    # 2. 齿根圆（细实线）
    msp.add_circle((cx, cy), root_r,
                   dxfattribs={"layer": layer, "lineweight": LW_THIN})
    # 3. 分度圆（细点画线）
    msp.add_circle((cx, cy), pitch_r,
                   dxfattribs={"layer": "CENTER", "lineweight": LW_THIN})
    # 4. 轮毂
    if hub_r > 0:
        msp.add_circle((cx, cy), hub_r,
                       dxfattribs={"layer": layer, "lineweight": LW_THICK})
    # 5. 轴孔
    if bore_r > 0:
        msp.add_circle((cx, cy), bore_r,
                       dxfattribs={"layer": layer, "lineweight": LW_THICK})
    # 6. 辐板孔（3个均布减重孔）
    if entity.get("draw_web_holes", True) and hub_r > 0:
        spoke_r = (hub_r + root_r) / 2
        hole_r  = max((root_r - hub_r) / 4, 3)
        for i in range(3):
            a = 2 * math.pi * i / 3
            hx = cx + spoke_r * math.cos(a)
            hy = cy + spoke_r * math.sin(a)
            msp.add_circle((hx, hy), hole_r,
                           dxfattribs={"layer": layer, "lineweight": LW_THIN})
    # 7. 中心线
    ext = outer_r + 8
    cl  = {"layer": "CENTER", "lineweight": LW_THIN}
    msp.add_line((cx - ext, cy), (cx + ext, cy), dxfattribs=cl)
    msp.add_line((cx, cy - ext), (cx, cy + ext), dxfattribs=cl)


def draw_screw_thread(msp, entity: dict):
    """
    螺纹画法（GB/T 4459.1）.
    外螺纹: 大径=粗实线, 小径=细实线 (0.85×大径)
    cx, cy: 轴线起点; radius: 大径(半径); length: 螺纹长度
    type: 'external'(外螺纹) / 'internal'(内螺纹)
    """
    cx     = entity.get("cx", 0)
    cy     = entity.get("cy", 0)
    radius = entity.get("radius", 10)
    length = entity.get("length", 40)
    ttype  = entity.get("type", "external")
    layer  = entity.get("layer", "OUTLINE")

    minor_r = radius * 0.85   # 小径 = 0.85×大径（近似）

    if ttype == "external":
        # 大径线（粗实线）
        msp.add_line((cx, cy + radius),  (cx + length, cy + radius),
                     dxfattribs={"layer": layer, "lineweight": LW_THICK})
        msp.add_line((cx, cy - radius),  (cx + length, cy - radius),
                     dxfattribs={"layer": layer, "lineweight": LW_THICK})
        # 小径线（细实线）
        msp.add_line((cx, cy + minor_r), (cx + length, cy + minor_r),
                     dxfattribs={"layer": layer, "lineweight": LW_THIN})
        msp.add_line((cx, cy - minor_r), (cx + length, cy - minor_r),
                     dxfattribs={"layer": layer, "lineweight": LW_THIN})
        # 端面（粗实线）
        msp.add_arc((cx, cy), radius, 0, 360,
                    dxfattribs={"layer": layer, "lineweight": LW_THICK})
        msp.add_arc((cx, cy), minor_r, 30, 330,
                    dxfattribs={"layer": layer, "lineweight": LW_THIN})
        # 螺纹终止线
        msp.add_line((cx + length, cy - radius), (cx + length, cy + radius),
                     dxfattribs={"layer": layer, "lineweight": LW_THICK})
    else:
        # 内螺纹（剖面）
        msp.add_line((cx, cy + minor_r),  (cx + length, cy + minor_r),
                     dxfattribs={"layer": layer, "lineweight": LW_THICK})
        msp.add_line((cx, cy - minor_r),  (cx + length, cy - minor_r),
                     dxfattribs={"layer": layer, "lineweight": LW_THICK})
        msp.add_line((cx, cy + radius),   (cx + length, cy + radius),
                     dxfattribs={"layer": layer, "lineweight": LW_THIN})
        msp.add_line((cx, cy - radius),   (cx + length, cy - radius),
                     dxfattribs={"layer": layer, "lineweight": LW_THIN})
        msp.add_arc((cx, cy), minor_r, 0, 360,
                    dxfattribs={"layer": layer, "lineweight": LW_THICK})
        msp.add_arc((cx, cy), radius, 30, 330,
                    dxfattribs={"layer": layer, "lineweight": LW_THIN})

    # 轴中心线
    cl = {"layer": "CENTER", "lineweight": LW_THIN}
    msp.add_line((cx - 5, cy), (cx + length + 5, cy), dxfattribs=cl)


def draw_o_ring(msp, entity: dict):
    """O形圈（GB/T 3452.1 画法）."""
    cx   = entity.get("cx", 0)
    cy   = entity.get("cy", 0)
    od   = entity.get("outer_diameter", 60)
    cord = entity.get("cord_diameter", 5)
    layer = entity.get("layer", "OUTLINE")
    mid_r = (od - cord) / 2
    msp.add_circle((cx, cy), mid_r + cord / 2,
                   dxfattribs={"layer": layer, "lineweight": LW_THICK})
    msp.add_circle((cx, cy), mid_r - cord / 2,
                   dxfattribs={"layer": layer, "lineweight": LW_THIN})
    cl = {"layer": "CENTER", "lineweight": LW_THIN}
    msp.add_line((cx - (od/2 + 5), cy), (cx + (od/2 + 5), cy), dxfattribs=cl)
    msp.add_line((cx, cy - (od/2 + 5)), (cx, cy + (od/2 + 5)), dxfattribs=cl)


def draw_fillet(msp, entity: dict):
    """圆角（倒角弧）."""
    ox    = entity.get("origin", [0, 0])[0]
    oy    = entity.get("origin", [0, 0])[1]
    w     = entity.get("width", 30)
    h     = entity.get("height", 30)
    r     = entity.get("radius", 5)
    layer = entity.get("layer", "OUTLINE")
    attr  = {"layer": layer, "lineweight": LW_THICK}
    msp.add_line((ox, oy + r), (ox, oy + h), dxfattribs=attr)
    msp.add_line((ox + r, oy), (ox + w, oy), dxfattribs=attr)
    msp.add_arc((ox + r, oy + r), r, 180, 270, dxfattribs=attr)


# ═══════════════════════════════════════════════════════
#  v7.0 新增: 基准符号、视图标注、零件序号
# ═══════════════════════════════════════════════════════

def draw_datum_mark(msp, entity: dict):
    """
    基准符号（GB/T 1182）.
    由粗实线方框 + 大写字母 + 细实线连线 + 实心三角形组成。
    x, y: 三角形尖端位置（接触基准要素的点）
    letter: 基准字母（大写，如 A/B/C）
    orientation: 'up'(三角朝上)/'down'/'left'/'right'
    leader_length: 从方框到三角尖端的连线长度
    triangle_size: 等边三角形边长
    box_size: 方框边长
    """
    x       = entity.get("x", 0)
    y       = entity.get("y", 0)
    letter  = entity.get("letter", "A")
    ori     = entity.get("orientation", "up")
    ll      = entity.get("leader_length", 10)
    tri_s   = entity.get("triangle_size", 5)
    box_s   = entity.get("box_size", 7)
    layer   = entity.get("layer", "TOLERANCE")

    # 方向映射：从三角尖端到方框的方向
    dir_map = {
        "up":    (0, 1),    # 三角尖端在下，方框在上
        "down":  (0, -1),
        "right": (-1, 0),
        "left":  (1, 0),
    }
    dx, dy = dir_map.get(ori, (0, 1))

    # 三角尖端 = (x, y)
    # 三角底边中点 = 尖端 + tri_s * 高度方向
    tri_h = tri_s * math.sqrt(3) / 2  # 等边三角形高度
    base_cx = x + dx * tri_h
    base_cy = y + dy * tri_h

    # 三角形两条边（粗实线）
    if ori in ("up", "down"):
        perp_x, perp_y = 1, 0
    else:
        perp_x, perp_y = 0, 1

    tri_attr = {"layer": layer, "lineweight": LW_THICK}
    # 左边
    msp.add_line((x, y), (base_cx - perp_x * tri_s/2, base_cy - perp_y * tri_s/2), dxfattribs=tri_attr)
    # 右边
    msp.add_line((x, y), (base_cx + perp_x * tri_s/2, base_cy + perp_y * tri_s/2), dxfattribs=tri_attr)
    # 底边（粗实线）
    msp.add_line(
        (base_cx - perp_x * tri_s/2, base_cy - perp_y * tri_s/2),
        (base_cx + perp_x * tri_s/2, base_cy + perp_y * tri_s/2),
        dxfattribs=tri_attr
    )

    # 连线（从三角底边中点到方框，细实线）
    wire_end_x = base_cx + dx * ll
    wire_end_y = base_cy + dy * ll
    wire_attr = {"layer": layer, "lineweight": LW_THIN}
    msp.add_line((base_cx, base_cy), (wire_end_x, wire_end_y), dxfattribs=wire_attr)

    # 方框（粗实线）
    if ori in ("up", "down"):
        bx1 = wire_end_x - box_s / 2
        by1 = wire_end_y - dy * 0  # bottom of box
        bx2 = wire_end_x + box_s / 2
        by2 = wire_end_y + box_s
        if ori == "down":
            by1 = wire_end_y - box_s
            by2 = wire_end_y
    else:
        bx1 = wire_end_x
        by1 = wire_end_y - box_s / 2
        bx2 = wire_end_x + box_s
        by2 = wire_end_y + box_s / 2
        if ori == "left":
            bx1 = wire_end_x - box_s
            bx2 = wire_end_x

    box_attr = {"layer": layer, "lineweight": LW_THICK}
    msp.add_lwpolyline(
        [(bx1, by1), (bx2, by1), (bx2, by2), (bx1, by2)],
        close=True, dxfattribs=box_attr
    )

    # 方框内字母
    if ori == "up":
        txt_x = bx1 + (bx2 - bx1) / 2 - 2
        txt_y = by1 + 1
    elif ori == "down":
        txt_x = bx1 + (bx2 - bx1) / 2 - 2
        txt_y = by1 + 1
    elif ori == "right":
        txt_x = bx1 + 1
        txt_y = by1 + (by2 - by1) / 2 - 1
    else:  # left
        txt_x = bx1 + 1
        txt_y = by1 + (by2 - by1) / 2 - 1

    msp.add_text(letter,
                 dxfattribs={"layer": layer, "height": 5}).set_placement(
        (txt_x, txt_y), align=TextEntityAlignment.LEFT
    )


def draw_view_label(msp, entity: dict):
    """
    视图名称标注（放在视图上方居中）.
    text: 如 "主视图", "A-A", "B向", "I" (放大图)
    x, y: 标注位置（通常在视图顶部中间偏上）
    """
    text   = entity.get("text", "")
    x      = entity.get("x", 0)
    y      = entity.get("y", 0)
    height = entity.get("height", TEXT_HEIGHT_TITLE)
    layer  = entity.get("layer", "TEXT")

    if text:
        msp.add_text(text,
                     dxfattribs={"layer": layer, "height": height}).set_placement(
            (x, y), align=TextEntityAlignment.MIDDLE_CENTER
        )


def draw_part_number(msp, entity: dict):
    """
    零件序号标注（装配图专用）.
    引线从 target（箭头端）到 label_pos（序号圆圈中心），
    序号圆圈用粗实线绘制，直径由 circle_radius 决定。
    """
    number     = entity.get("number", 1)
    target     = tuple(entity.get("target", [0, 0]))
    label_pos  = tuple(entity.get("label_pos", [20, 30]))
    cr         = entity.get("circle_radius", 4)
    layer      = entity.get("layer", "TEXT")

    # 引线（箭头端 → 序号圆圈边沿）
    attr = {"layer": layer, "lineweight": LW_THIN}
    msp.add_line(target, label_pos, dxfattribs=attr)

    # 箭头小圆点（target 端）
    msp.add_circle(target, 1.0, dxfattribs={"layer": layer, "color": 7})

    # 序号圆圈（粗实线）
    msp.add_circle(label_pos, cr, dxfattribs={"layer": layer, "lineweight": LW_THICK})

    # 序号数字（居中）
    num_text = str(number)
    # 计算偏移使数字大致居中
    offset = len(num_text) * 1.2
    msp.add_text(num_text,
                 dxfattribs={"layer": layer, "height": TEXT_HEIGHT_BODY}).set_placement(
        (label_pos[0] - offset, label_pos[1] - TEXT_HEIGHT_BODY/3),
        align=TextEntityAlignment.LEFT
    )


# ═══════════════════════════════════════════════════════
#  v8.0 新增: 投影方式符号（ISO 128-1）
# ═══════════════════════════════════════════════════════

def draw_projection_symbol(msp, entity: dict):
    """
    投影方式符号（ISO 128-1 / v8.0 新增）.
    绘制截锥体图形标识第一角或第三角投影方式。
    第一角：上方小圆（俯视图在下），右方全圆（左视图在右）
    第三角：下方小圆（俯视图在上），左方全圆（左视图在左）
    x, y: 符号中心位置
    projection: "first" 或 "third"
    size: 符号整体尺寸，默认 15mm
    """
    x         = entity.get("x", 0)
    y         = entity.get("y", 0)
    proj      = entity.get("projection", "first")
    size      = entity.get("size", 15)
    layer     = entity.get("layer", "BORDER")

    thin_attr = {"layer": layer, "lineweight": LW_THIN}
    thick_attr = {"layer": layer, "lineweight": LW_THICK}

    if proj == "third":
        # 第三角投影符号
        # 上方大圆（主视图/俯视图位置）
        msp.add_circle((x, y + size * 0.28), size * 0.18, dxfattribs=thick_attr)
        # 下方小圆（仰视图位置）
        msp.add_circle((x, y - size * 0.28), size * 0.10, dxfattribs=thin_attr)
        # 左方全圆（左视图位置）
        msp.add_circle((x - size * 0.32, y), size * 0.14, dxfattribs=thick_attr)
        # 截锥体侧视轮廓（梯形）
        msp.add_line(
            (x - size * 0.22, y + size * 0.12),
            (x - size * 0.42, y - size * 0.12),
            dxfattribs=thick_attr
        )
        msp.add_line(
            (x + size * 0.22, y + size * 0.12),
            (x + size * 0.42, y - size * 0.12),
            dxfattribs=thick_attr
        )
        # 中心线
        cl = {"layer": "CENTER", "lineweight": LW_HAIR}
        msp.add_line((x - size * 0.5, y), (x + size * 0.5, y), dxfattribs=cl)
        msp.add_line((x, y - size * 0.5), (x, y + size * 0.5), dxfattribs=cl)
        # 标注 "3rd"
        msp.add_text("3rd", dxfattribs={"layer": "TEXT", "height": 2.5}).set_placement(
            (x + size * 0.45, y - size * 0.05), align=TextEntityAlignment.LEFT
        )
    else:
        # 第一角投影符号
        # 上方小圆（仰视图位置）
        msp.add_circle((x, y + size * 0.28), size * 0.10, dxfattribs=thin_attr)
        # 下方大圆（俯视图位置）
        msp.add_circle((x, y - size * 0.28), size * 0.18, dxfattribs=thick_attr)
        # 右方全圆（左视图位置）
        msp.add_circle((x + size * 0.32, y), size * 0.14, dxfattribs=thick_attr)
        # 截锥体侧视轮廓（梯形）
        msp.add_line(
            (x - size * 0.42, y + size * 0.12),
            (x - size * 0.22, y - size * 0.12),
            dxfattribs=thick_attr
        )
        msp.add_line(
            (x + size * 0.42, y + size * 0.12),
            (x + size * 0.22, y - size * 0.12),
            dxfattribs=thick_attr
        )
        # 中心线
        cl = {"layer": "CENTER", "lineweight": LW_HAIR}
        msp.add_line((x - size * 0.5, y), (x + size * 0.5, y), dxfattribs=cl)
        msp.add_line((x, y - size * 0.5), (x, y + size * 0.5), dxfattribs=cl)
        # 标注 "1st"
        msp.add_text("1st", dxfattribs={"layer": "TEXT", "height": 2.5}).set_placement(
            (x + size * 0.45, y - size * 0.05), align=TextEntityAlignment.LEFT
        )


# ═══════════════════════════════════════════════════════
#  v9.0 新增: ISO 8015 GPS 基准链闭环标注
# ═══════════════════════════════════════════════════════

def draw_datum_chain(msp, doc, entity: dict):
    """
    基准链闭环标注（ISO 8015 / ISO 5458 / ASME Y14.5）.
    从基准面出发，依次标注到各加工面，形成封闭尺寸链。

    参数:
      dimensions: list of dicts, each:
        {
          "p1": [x1, y1], "p2": [x2, y2],   # 尺寸起止点
          "value": "50",                       # 标注值（文字覆盖）
          "datum_ref": "A",                    # 基准参考（可选）
          "tolerance": "+0.05/-0.00",          # 公差（可选）
          "dimline_offset": 10,                # 偏移量
          "angle": 0                           # 0=水平, 90=垂直
        }
      chain_label: 基准链标识文字（如 "DATUM CHAIN A"）
      layer: 图层（默认 "DIM"）
      closed: 是否验证闭环（默认 True）
    """
    dimensions = entity.get("dimensions", [])
    chain_label = entity.get("chain_label", "DATUM CHAIN")
    layer = entity.get("layer", "DIM")
    closed = entity.get("closed", True)

    for i, dim in enumerate(dimensions):
        p1 = tuple(dim.get("p1", (0, 0)))
        p2 = tuple(dim.get("p2", (10, 0)))
        base = dim.get("dimline_offset", 10)
        angle = dim.get("angle", 0)
        value_override = dim.get("value", None)
        datum_ref = dim.get("datum_ref", "")
        tolerance = dim.get("tolerance", "")

        # 计算基准点
        if angle == 0:
            base_point = ((p1[0] + p2[0]) / 2, max(p1[1], p2[1]) + base)
        elif angle == 90:
            base_point = (max(p1[0], p2[0]) + base, (p1[1] + p2[1]) / 2)
        else:
            base_point = ((p1[0] + p2[0]) / 2, max(p1[1], p2[1]) + base)

        try:
            dim_obj = msp.add_linear_dim(
                base=base_point, p1=p1, p2=p2, angle=angle,
                dimstyle="EZDXF", dxfattribs={"layer": layer}
            )
            dim_obj.render()

            # 覆盖标注文字（加入公差）
            if value_override or tolerance:
                from ezdxf.entities import DimStyleOverride
                override_text = value_override if value_override else ""
                if tolerance:
                    override_text += f" {tolerance}"
                if datum_ref:
                    override_text = f"[{datum_ref}] {override_text}"
                try:
                    dim_obj.dxf.text = override_text
                except Exception:
                    pass

            # 基准参考标注线（从基准符号到尺寸线）
            if datum_ref and i == 0:
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                try:
                    msp.add_text(f"← {datum_ref}",
                                 dxfattribs={"layer": "DATUM", "height": TEXT_HEIGHT_SMALL}).set_placement(
                        (mid_x - 5, base_point[1] + 2), align=TextEntityAlignment.LEFT)
                except Exception:
                    pass

        except Exception as e:
            print(f"[WARN] Datum chain dim skipped: {e}", file=sys.stderr)

    # 基准链标识文字
    if chain_label and dimensions:
        first = dimensions[0]
        p1 = tuple(first.get("p1", (0, 0)))
        base = first.get("dimline_offset", 10)
        try:
            msp.add_text(chain_label,
                         dxfattribs={"layer": "TEXT", "height": TEXT_HEIGHT_SMALL}).set_placement(
                (p1[0] - 2, max(p1[1], (p1[1] + tuple(first.get("p2", (10, 0)))[1]) / 2) + base + 4),
                align=TextEntityAlignment.LEFT)
        except Exception:
            pass

    # 闭环验证提示
    if closed and len(dimensions) > 1:
        last_dim = dimensions[-1]
        first_dim = dimensions[0]
        last_p2 = tuple(last_dim.get("p2", (0, 0)))
        first_p1 = tuple(first_dim.get("p1", (0, 0)))
        # 检查链是否闭合（最后一个点的坐标是否接近第一个点）
        gap = math.hypot(last_p2[0] - first_p1[0], last_p2[1] - first_p1[1])
        if gap > 0.5:  # 允许 0.5mm 误差
            print(f"[WARN] Datum chain is NOT closed (gap={gap:.2f}mm). "
                  f"Consider adding closing dimension.", file=sys.stderr)
        else:
            print(f"[OK] Datum chain closed (gap={gap:.2f}mm)", file=sys.stderr)


def draw_general_tolerance_block(msp, entity: dict):
    """
    ISO 2768 通用公差等级标注块（v9.0 新增）.
    在图纸标题栏附近或技术要求区域放置通用公差等级说明。

    参数:
      x, y: 标注位置
      class: ISO 2768 等级（如 "mK", "fK", "H", "m", "c", "v"）
        - m: 中等精度 (medium)
        - f: 精密级 (fine)
        - c: 粗糙级 (coarse)
        - v: 很粗糙级 (very coarse)
        - K: 包含形位公差
      unit_system: "metric"(mm) 或 "imperial"(inch)
    """
    x = entity.get("x", 0)
    y = entity.get("y", 0)
    cls = entity.get("class", "mK")
    unit_system = entity.get("unit_system", "metric")
    layer = entity.get("layer", "TEXT")
    h = entity.get("height", TEXT_HEIGHT_BODY)
    title_h = entity.get("title_height", TEXT_HEIGHT_TITLE)
    box_w = entity.get("box_width", 65)
    box_h = entity.get("box_height", 35)

    attr = {"layer": layer, "lineweight": LW_THIN}
    box_attr = {"layer": layer, "lineweight": LW_THICK}

    # ISO 2768 公差表（线性尺寸，mm）
    TOLERANCE_TABLE = {
        "f": [(0.5, 3, 0.05), (3, 6, 0.05), (6, 30, 0.1), (30, 120, 0.15),
              (120, 400, 0.2), (400, 1000, 0.3), (1000, 2000, 0.5), (2000, 4000, 0.8)],
        "m": [(0.5, 3, 0.1), (3, 6, 0.1), (6, 30, 0.2), (30, 120, 0.3),
              (120, 400, 0.5), (400, 1000, 0.8), (1000, 2000, 1.2), (2000, 4000, 2.0)],
        "c": [(0.5, 3, 0.2), (3, 6, 0.3), (6, 30, 0.5), (30, 120, 0.8),
              (120, 400, 1.2), (400, 1000, 2.0), (1000, 2000, 3.0), (2000, 4000, 4.0)],
        "v": [(0.5, 3, 0.5), (3, 6, 0.5), (6, 30, 1.0), (30, 120, 1.5),
              (120, 400, 2.5), (400, 1000, 4.0), (1000, 2000, 6.0), (2000, 4000, 8.0)],
    }

    # 绘制外框
    msp.add_lwpolyline(
        [(x, y), (x + box_w, y), (x + box_w, y + box_h), (x, y + box_h)],
        close=True, dxfattribs=box_attr
    )

    # 标题行
    msp.add_line((x, y + box_h - 8), (x + box_w, y + box_h - 8), dxfattribs=box_attr)
    msp.add_text("ISO 2768",
                 dxfattribs={"layer": layer, "height": title_h}).set_placement(
        (x + 2, y + box_h - 6), align=TextEntityAlignment.LEFT)

    # 等级标识
    precision_char = cls[0] if cls else "m"
    has_geom = "K" in cls

    msp.add_text(f"Class: {cls}",
                 dxfattribs={"layer": layer, "height": h}).set_placement(
        (x + 2, y + box_h - 12), align=TextEntityAlignment.LEFT)

    # 单位
    unit_str = "mm" if unit_system == "metric" else "inch"
    msp.add_text(f"Unit: {unit_str}",
                 dxfattribs={"layer": layer, "height": h}).set_placement(
        (x + 2, y + box_h - 16), align=TextEntityAlignment.LEFT)

    # 精度等级说明
    precision_desc = {
        "f": "Fine",
        "m": "Medium",
        "c": "Coarse",
        "v": "Very coarse",
    }
    desc = precision_desc.get(precision_char, "Medium")
    msp.add_text(f"Precision: {desc}",
                 dxfattribs={"layer": layer, "height": TEXT_HEIGHT_SMALL}).set_placement(
        (x + 2, y + box_h - 20), align=TextEntityAlignment.LEFT)

    # 形位公差说明
    if has_geom:
        msp.add_text("Includes geometrical",
                     dxfattribs={"layer": layer, "height": TEXT_HEIGHT_SMALL}).set_placement(
            (x + 2, y + box_h - 24), align=TextEntityAlignment.LEFT)
        msp.add_text("tolerances (K)",
                     dxfattribs={"layer": layer, "height": TEXT_HEIGHT_SMALL}).set_placement(
            (x + 2, y + box_h - 28), align=TextEntityAlignment.LEFT)


# ═══════════════════════════════════════════════════════
#  建筑图元（GB/T 50001 规范）
# ═══════════════════════════════════════════════════════

def draw_wall(msp, entity: dict):
    """墙体（双线矩形 + 填充可选）."""
    x     = entity.get("x", 0)
    y     = entity.get("y", 0)
    w     = entity.get("width", 5000)
    h     = entity.get("height", 240)    # 墙厚
    layer = entity.get("layer", "WALL")
    attr  = {"layer": layer, "lineweight": LW_THICK}
    msp.add_lwpolyline(
        [(x, y), (x+w, y), (x+w, y+h), (x, y+h)],
        close=True, dxfattribs=attr
    )
    # 可选填充（砖墙图例）
    if entity.get("fill", False):
        hatch = msp.add_hatch(dxfattribs={"layer": "HATCH"})
        hatch.set_pattern_fill("ANSI31", scale=0.5)
        hatch.paths.add_polyline_path(
            [(x, y), (x+w, y), (x+w, y+h), (x, y+h)], is_closed=True)


def draw_door_arc(msp, entity: dict):
    """
    门扇图例（平开门, 90°弧线）.
    x, y: 铰链端; width: 门宽; opens_left: 朝哪个方向开启
    """
    ox    = entity.get("x", 0)
    oy    = entity.get("y", 0)
    width = entity.get("width", 900)
    opens_left = entity.get("opens_left", False)
    layer = entity.get("layer", "DOOR")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    # 门扇线
    msp.add_line((ox, oy), (ox + (width if not opens_left else 0),
                             oy + (0 if not opens_left else width)), dxfattribs=attr)
    # 弧线
    if opens_left:
        msp.add_arc((ox, oy), width, 0, 90, dxfattribs=attr)
    else:
        msp.add_arc((ox, oy), width, 0, 90, dxfattribs=attr)


def draw_window(msp, entity: dict):
    """窗户图例（三线表示）."""
    cx    = entity.get("x", 0)
    cy    = entity.get("y", 0)
    width = entity.get("width", 1500)
    h     = entity.get("height", 240)
    layer = entity.get("layer", "WINDOW")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    x1, y1 = cx - width/2, cy - h/2
    x2, y2 = cx + width/2, cy + h/2
    # 外框 + 中间线（三线）
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs=attr)
    msp.add_line((x1, (y1+y2)/2), (x2, (y1+y2)/2), dxfattribs={"layer": layer, "lineweight": LW_HAIR})


def draw_stairs(msp, entity: dict):
    """楼梯踏步图例."""
    ox    = entity.get("x", 0)
    oy    = entity.get("y", 0)
    width = entity.get("width", 2400)
    total_h = entity.get("height", 1500)
    num   = entity.get("steps", 10)
    layer = entity.get("layer", "WALL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    rise  = total_h / num
    tread = width / num
    for i in range(num):
        x0 = ox + i * tread
        y0 = oy + i * rise
        msp.add_line((x0, y0 + rise), (x0 + tread, y0 + rise), dxfattribs=attr)
        msp.add_line((x0 + tread, y0), (x0 + tread, y0 + rise), dxfattribs=attr)
    # 方向箭头
    msp.add_line((ox, oy), (ox + width, oy + total_h),
                 dxfattribs={"layer": layer, "lineweight": LW_HAIR})


# ═══════════════════════════════════════════════════════
#  电气符号（GB/T 4728 / IEC 60617）
# ═══════════════════════════════════════════════════════

def draw_symbol_resistor(msp, entity: dict):
    """IEC 矩形电阻符号（GB/T 4728）."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    sz = entity.get("length", 50)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    # 引线
    msp.add_line((ox, oy), (ox + sz*0.25, oy), dxfattribs=attr)
    msp.add_line((ox + sz*0.75, oy), (ox + sz, oy), dxfattribs=attr)
    # 矩形体（高 = sz*0.15）
    bx = ox + sz*0.25; bw = sz*0.5; bh = sz*0.15
    msp.add_lwpolyline(
        [(bx, oy-bh/2), (bx+bw, oy-bh/2), (bx+bw, oy+bh/2), (bx, oy+bh/2)],
        close=True, dxfattribs=attr)


def draw_symbol_capacitor(msp, entity: dict):
    """电容符号（两平行板）."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    sz = entity.get("length", 50)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    plate_h = sz * 0.12
    gap     = sz * 0.06
    cx = ox + sz / 2
    msp.add_line((ox, oy), (cx - gap/2, oy), dxfattribs=attr)
    msp.add_line((cx - gap/2, oy - plate_h), (cx - gap/2, oy + plate_h), dxfattribs=attr)
    msp.add_line((cx + gap/2, oy - plate_h), (cx + gap/2, oy + plate_h), dxfattribs=attr)
    msp.add_line((cx + gap/2, oy), (ox + sz, oy), dxfattribs=attr)


def draw_symbol_inductor(msp, entity: dict):
    """电感符号（IEC 半圆弧）."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    sz = entity.get("length", 50)
    n  = entity.get("coils", 4)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    coil_w = sz * 0.5 / n
    coil_r = coil_w / 2
    start_x = ox + sz * 0.25
    msp.add_line((ox, oy), (start_x, oy), dxfattribs=attr)
    for i in range(n):
        arc_cx = start_x + coil_w * i + coil_r
        msp.add_arc((arc_cx, oy), coil_r, 0, 180, dxfattribs=attr)
    msp.add_line((start_x + n * coil_w, oy), (ox + sz, oy), dxfattribs=attr)


def draw_symbol_diode(msp, entity: dict):
    """二极管符号（三角+竖线）."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    sz = entity.get("length", 50)
    h  = sz * 0.15
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    cx = ox + sz * 0.5
    msp.add_line((ox, oy), (cx - h, oy), dxfattribs=attr)
    # 三角形（朝右导通）
    msp.add_lwpolyline(
        [(cx - h, oy - h), (cx - h, oy + h), (cx + h, oy)],
        close=True, dxfattribs=attr)
    # 截止线
    msp.add_line((cx + h, oy - h), (cx + h, oy + h), dxfattribs=attr)
    msp.add_line((cx + h, oy), (ox + sz, oy), dxfattribs=attr)


def draw_symbol_switch_no(msp, entity: dict):
    """常开开关（NO）符号."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    sz = entity.get("length", 50)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    gap = sz * 0.4
    msp.add_line((ox, oy), (ox + sz*0.3, oy), dxfattribs=attr)
    # 触点小圆
    msp.add_circle((ox + sz*0.3, oy), sz*0.03, dxfattribs=attr)
    msp.add_circle((ox + sz*0.7, oy), sz*0.03, dxfattribs=attr)
    # 可动臂（斜线）
    msp.add_line((ox + sz*0.3, oy), (ox + sz*0.65, oy + sz*0.18), dxfattribs=attr)
    msp.add_line((ox + sz*0.7, oy), (ox + sz, oy), dxfattribs=attr)


def draw_gnd(msp, entity: dict):
    """接地符号（三条渐缩横线）."""
    ox  = entity.get("x", 0); oy = entity.get("y", 0)
    sz  = entity.get("size", 20)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    msp.add_line((ox, oy), (ox, oy + sz*0.4), dxfattribs=attr)
    for i, frac in enumerate([0.5, 0.35, 0.2]):
        bar_w = sz * frac
        yoff  = oy + sz * (0.4 + i * 0.15)
        msp.add_line((ox - bar_w, yoff), (ox + bar_w, yoff), dxfattribs=attr)


def draw_terminal(msp, entity: dict):
    """接线端子（小圆 + 十字线）."""
    cx = entity.get("x", 0); cy = entity.get("y", 0)
    r  = entity.get("radius", 4)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    msp.add_circle((cx, cy), r, dxfattribs=attr)
    msp.add_line((cx-r, cy), (cx+r, cy), dxfattribs=attr)
    msp.add_line((cx, cy-r), (cx, cy+r), dxfattribs=attr)


def draw_node_dot(msp, entity: dict):
    """导线接点（实心小圆）."""
    if "x" in entity:
        cx, cy = entity["x"], entity.get("y", 0)
    else:
        cx, cy = entity.get("center", [0, 0])[:2]
    r     = entity.get("radius", 2.0)
    layer = entity.get("layer", "SYMBOL")
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer, "color": 7})


def draw_transformer(msp, entity: dict):
    """变压器符号（两个耦合电感）."""
    ox    = entity.get("x", 0); oy = entity.get("y", 0)
    sz    = entity.get("length", 40)
    turns = entity.get("coils", 4)
    core  = entity.get("core", True)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    coil_r = sz / (4 * turns)
    for side_off, cx_add in [(0, 0), (sz * 0.6, sz * 0.6)]:
        coil_x = ox + sz * 0.1 + side_off
        for i in range(turns):
            arc_cx = coil_x + (2 * i + 1) * coil_r
            msp.add_arc((arc_cx, oy), coil_r, 0, 180, dxfattribs=attr)
    if core:
        cx_line = ox + sz * 0.35
        msp.add_line((cx_line, oy - sz * 0.5), (cx_line, oy + sz * 0.5),
                     dxfattribs={"layer": layer, "lineweight": LW_THIN})
        msp.add_line((cx_line + 3, oy - sz * 0.5), (cx_line + 3, oy + sz * 0.5),
                     dxfattribs={"layer": layer, "lineweight": LW_THIN})


def draw_transistor(msp, entity: dict):
    """NPN 晶体管符号."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    sz = entity.get("length", 50)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    # 基极竖线
    msp.add_line((ox, oy - sz*0.4), (ox, oy + sz*0.4), dxfattribs=attr)
    # 集电极（斜上）和发射极（斜下）
    msp.add_line((ox, oy + sz*0.15), (ox - sz*0.5, oy + sz*0.4), dxfattribs=attr)  # 集电极
    msp.add_line((ox, oy - sz*0.15), (ox - sz*0.5, oy - sz*0.4), dxfattribs=attr)  # 发射极
    # NPN 箭头（发射极方向外）
    arx = ox - sz*0.35; ary = oy - sz*0.28
    dx2 = -sz*0.15; dy2 = -sz*0.12
    l2 = math.hypot(dx2, dy2)
    msp.add_line((arx - dx2*0.4/l2*3, ary - dy2*0.4/l2*3),
                 (arx, ary), dxfattribs=attr)
    # 引线
    msp.add_line((ox, oy - sz*0.4), (ox, oy - sz*0.7), dxfattribs=attr)


def draw_ic_chip(msp, entity: dict):
    """IC 芯片（矩形 + 引脚）."""
    ox = entity.get("x", 0); oy = entity.get("y", 0)
    w  = entity.get("width", 60); h = entity.get("height", 40)
    pins_l = entity.get("pins_left", 4)
    pins_r = entity.get("pins_right", 4)
    label  = entity.get("label", "")
    layer  = entity.get("layer", "SYMBOL")
    attr   = {"layer": layer, "lineweight": LW_THIN}
    msp.add_lwpolyline([(ox,oy),(ox+w,oy),(ox+w,oy+h),(ox,oy+h)],
                       close=True, dxfattribs=attr)
    for i in range(pins_l):
        py = oy + h * (i+1) / (pins_l+1)
        msp.add_line((ox, py), (ox-10, py), dxfattribs=attr)
        msp.add_text(str(i+1),
                     dxfattribs={"layer": layer, "height": 2}).set_placement(
            (ox+1, py+0.5), align=TextEntityAlignment.LEFT)
    for i in range(pins_r):
        py = oy + h * (pins_r - i) / (pins_r+1)  # 右侧引脚逆序
        msp.add_line((ox+w, py), (ox+w+10, py), dxfattribs=attr)
    if label:
        msp.add_text(label,
                     dxfattribs={"layer": layer, "height": TEXT_HEIGHT_BODY}).set_placement(
            (ox+2, oy + h/2 - 2), align=TextEntityAlignment.LEFT)


def draw_connector(msp, entity: dict):
    """连接器/插头符号."""
    cx = entity.get("cx", 0); cy = entity.get("cy", 0)
    w  = entity.get("width", 20); h = entity.get("height", 40)
    pins = entity.get("pin_count", 4)
    layer = entity.get("layer", "SYMBOL")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    x1, y1 = cx - w/2, cy - h/2
    x2, y2 = cx + w/2, cy + h/2
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs=attr)
    for i in range(pins):
        py = y1 + h * (i+1) / (pins+1)
        msp.add_circle((x1 + w/2, py), 1.5, dxfattribs=attr)
        msp.add_line((x1, py), (x1 - 8, py), dxfattribs=attr)


# ═══════════════════════════════════════════════════════
#  P&ID / 管道仪表
# ═══════════════════════════════════════════════════════

def draw_pipe(msp, entity: dict):
    """管道线段（粗实线）."""
    start = tuple(entity["start"])
    end   = tuple(entity["end"])
    layer = entity.get("layer", "PIPE")
    msp.add_line(start, end, dxfattribs={"layer": layer, "lineweight": LW_THICK})


def draw_pipe_elbow(msp, entity: dict):
    """管道弯头（90°弧）."""
    cx = entity.get("cx", 0); cy = entity.get("cy", 0)
    r  = entity.get("radius", 20)
    cw = entity.get("clockwise", False)
    layer = entity.get("layer", "PIPE")
    sa = 270 if cw else 0
    ea = 360 if cw else 90
    msp.add_arc((cx, cy), r, sa, ea,
                dxfattribs={"layer": layer, "lineweight": LW_THICK})


def draw_valve(msp, entity: dict):
    """截止阀符号（P&ID 矩形+斜线）."""
    cx = entity.get("cx", 0); cy = entity.get("cy", 0)
    sz = entity.get("size", 20); angle = entity.get("angle", 0)
    layer = entity.get("layer", "PIPE")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    rad   = math.radians(angle)
    ca, sa2 = math.cos(rad), math.sin(rad)

    def rot(px, py): return (cx + px*ca - py*sa2, cy + px*sa2 + py*ca)

    # 蝶形阀轮廓（两个三角形）
    msp.add_lwpolyline([rot(-sz, 0), rot(0, sz/2), rot(sz, 0)], close=False, dxfattribs=attr)
    msp.add_lwpolyline([rot(-sz, 0), rot(0, -sz/2), rot(sz, 0)], close=False, dxfattribs=attr)
    # 阀杆
    sx1, sy1 = rot(0, sz/2); sx2, sy2 = rot(0, sz)
    msp.add_line((sx1, sy1), (sx2, sy2), dxfattribs=attr)
    msp.add_circle(rot(0, sz), sz*0.25, dxfattribs=attr)


def draw_pump(msp, entity: dict):
    """离心泵符号（圆形机壳）."""
    cx = entity.get("cx", 0); cy = entity.get("cy", 0)
    sz = entity.get("size", 25)
    layer = entity.get("layer", "PIPE")
    attr  = {"layer": layer, "lineweight": LW_THICK}
    msp.add_circle((cx, cy), sz, dxfattribs=attr)
    msp.add_line((cx-sz*0.5, cy), (cx+sz*0.5, cy), dxfattribs={"layer": layer, "lineweight": LW_THIN})
    msp.add_line((cx, cy-sz*0.5), (cx, cy+sz*0.5), dxfattribs={"layer": layer, "lineweight": LW_THIN})
    msp.add_circle((cx, cy), sz*0.2, dxfattribs={"layer": layer, "lineweight": LW_THIN})
    msp.add_line((cx-sz-15, cy), (cx-sz, cy), dxfattribs={"layer": layer, "lineweight": LW_THIN})
    msp.add_line((cx+sz, cy), (cx+sz+15, cy), dxfattribs={"layer": layer, "lineweight": LW_THIN})


def draw_tank(msp, entity: dict):
    """储罐（竖式, 带弧形封头）."""
    cx = entity.get("cx", 0); cy = entity.get("cy", 0)
    w  = entity.get("width", 60); h = entity.get("height", 120)
    parts = entity.get("partitions", 1)
    layer = entity.get("layer", "PIPE")
    attr  = {"layer": layer, "lineweight": LW_THIN}
    x1, y1 = cx - w/2, cy - h/2
    x2, y2 = cx + w/2, cy + h/2
    msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True, dxfattribs=attr)
    # 顶部封头弧
    msp.add_arc((cx, y2), w/2, 0, 180,
                dxfattribs={"layer": layer, "lineweight": LW_THIN})
    for i in range(1, parts):
        py = y1 + h * i / parts
        msp.add_line((x1, py), (x2, py), dxfattribs=attr)


# ═══════════════════════════════════════════════════════
#  表格与信息框
# ═══════════════════════════════════════════════════════

def draw_bom_table(msp, entity: dict):
    """明细表（BOM, ISO 7573 / GB/T 10609.2）.
    v11.0: 默认标准修正为 GB（与全局默认值一致）.
    当 standard="ISO" 时使用 ISO 7573 英文字段。
    """
    x       = entity.get("x", 0); y = entity.get("y", 0)
    standard = entity.get("standard", "GB")  # v11.0: ★ 默认 GB（与 v10 全局默认一致）

    # v9.0: ISO 7573 标准字段
    if standard == "ISO":
        headers = entity.get("headers",
            ["Item", "Part No.", "Description", "Qty", "Material", "Mass (kg)", "Notes"])
        col_w   = entity.get("col_widths", [12, 35, 50, 12, 30, 18, 25])
    else:
        headers = entity.get("headers", ["序号", "代号", "名称", "数量", "材料", "备注"])
        col_w   = entity.get("col_widths", [15, 40, 55, 15, 35, 30])

    rows    = entity.get("rows", [])
    row_h   = entity.get("row_height", 8)
    layer   = entity.get("layer", "BORDER")
    t_layer = entity.get("text_layer", "TEXT")
    attr    = {"layer": layer, "lineweight": LW_THIN}

    def cell_rect(cx2, cy2, cw, ch):
        msp.add_lwpolyline(
            [(cx2, cy2), (cx2+cw, cy2), (cx2+cw, cy2+ch), (cx2, cy2+ch)],
            close=True, dxfattribs=attr)

    total_w = sum(col_w)
    n_cols  = len(headers)

    # 表头（从底部往上，明细表按行号从下往上排列）
    for c in range(n_cols):
        cx2 = x + sum(col_w[:c])
        cell_rect(cx2, y, col_w[c], row_h)
        msp.add_text(headers[c],
                     dxfattribs={"layer": t_layer, "height": TEXT_HEIGHT_BODY}).set_placement(
            (cx2 + 2, y + 2), align=TextEntityAlignment.LEFT)

    for r, row in enumerate(rows):
        row_y = y + row_h * (r + 1)
        for c, cell in enumerate(row[:n_cols]):
            cx3 = x + sum(col_w[:c])
            cell_rect(cx3, row_y, col_w[c], row_h)
            msp.add_text(str(cell),
                         dxfattribs={"layer": t_layer, "height": TEXT_HEIGHT_BODY}).set_placement(
                (cx3 + 2, row_y + 2), align=TextEntityAlignment.LEFT)

    # 外边框（粗实线）
    msp.add_lwpolyline(
        [(x, y), (x+total_w, y), (x+total_w, y+row_h*(len(rows)+1)),
         (x, y+row_h*(len(rows)+1))],
        close=True,
        dxfattribs={"layer": layer, "lineweight": LW_THICK})


def draw_revision_table(msp, entity: dict):
    """更改区/修订栏（GB/T 10609.1）."""
    x    = entity.get("x", 0); y = entity.get("y", 0)
    revs = entity.get("revisions", [{"rev": "A", "date": "2026-01-01", "desc": "初版"}])
    col_w = [15, 35, 50, 20, 30]
    headers = ["版次", "更改文件号", "更改内容", "日期", "更改人"]
    row_h  = 8
    layer  = entity.get("layer", "BORDER")
    t_l    = entity.get("text_layer", "TEXT")
    attr   = {"layer": layer, "lineweight": LW_THIN}

    total_w = sum(col_w)

    # 标题行
    for c, (cw, hdr) in enumerate(zip(col_w, headers)):
        cx2 = x + sum(col_w[:c])
        msp.add_lwpolyline(
            [(cx2, y), (cx2+cw, y), (cx2+cw, y+row_h), (cx2, y+row_h)],
            close=True, dxfattribs=attr)
        msp.add_text(hdr, dxfattribs={"layer": t_l, "height": TEXT_HEIGHT_SMALL}).set_placement(
            (cx2+2, y+2), align=TextEntityAlignment.LEFT)

    for i, rev in enumerate(revs):
        ry = y + row_h * (i + 1)
        data = [rev.get("rev",""), rev.get("change_no",""), rev.get("desc",""),
                rev.get("date",""), rev.get("author","")]
        for c, (cw, val) in enumerate(zip(col_w, data)):
            cx4 = x + sum(col_w[:c])
            msp.add_lwpolyline(
                [(cx4, ry), (cx4+cw, ry), (cx4+cw, ry+row_h), (cx4, ry+row_h)],
                close=True, dxfattribs=attr)
            msp.add_text(str(val), dxfattribs={"layer": t_l, "height": TEXT_HEIGHT_SMALL}).set_placement(
                (cx4+2, ry+2), align=TextEntityAlignment.LEFT)


# ═══════════════════════════════════════════════════════
#  块（Block）管理
# ═══════════════════════════════════════════════════════

def draw_block_def(msp, doc, entity: dict):
    """定义可重用块."""
    name = entity["name"]
    if name in doc.blocks:
        return
    block = doc.blocks.new(name=name)
    sub_disp = {k: v for k, v in DISPATCHER.items()
                if k not in {"dim_linear","dim_aligned","dim_radius",
                              "dim_diameter","dim_angular","title_block",
                              "block_def","insert_block","grid"}}
    for sub in entity.get("entities", []):
        stype = sub.get("type", "").lower()
        if stype in sub_disp:
            try:
                sub_disp[stype](block, sub)
            except Exception:
                pass


def draw_insert_block(msp, entity: dict):
    """插入已定义的块."""
    name  = entity["block_name"]
    ox    = entity.get("x", 0); oy = entity.get("y", 0)
    scale = entity.get("scale", 1.0)
    rot   = entity.get("rotation", 0)
    layer = entity.get("layer", "0")
    msp.add_blockref(name, (ox, oy), dxfattribs={
        "xscale": scale, "yscale": scale, "zscale": scale,
        "rotation": rot, "layer": layer})


# ═══════════════════════════════════════════════════════
#  v5.0 插件加载（Evolution Engine 兼容）
# ═══════════════════════════════════════════════════════

def load_plugins(dispatcher: dict):
    """
    从 plugins/ 目录热加载已演化的绘图函数。
    每个插件 .py 文件须定义 register(dispatcher) 函数。
    """
    plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
    if not plugins_dir.exists():
        return 0
    loaded = 0
    for plugin_file in sorted(plugins_dir.glob("*.py")):
        if plugin_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"cad_plugin_{plugin_file.stem}", str(plugin_file))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    mod.register(dispatcher)
                    loaded += 1
        except Exception as e:
            print(f"[PLUGIN] Failed to load {plugin_file.name}: {e}", file=sys.stderr)
    return loaded


# ─────────────────────────────────────────────
# 图层初始化
# ─────────────────────────────────────────────

def setup_layers(doc, user_layers: list):
    """
    初始化图层。先加载 GB 标准图层，再覆盖用户自定义图层。
    """
    # 确保所有标准线型可用
    for ltype in ["CENTER", "DASHED", "PHANTOM", "HIDDEN", "DOT"]:
        try:
            if ltype not in doc.linetypes:
                doc.linetypes.add(ltype)
        except Exception:
            pass  # 某些 ezdxf 版本不支持动态添加线型

    # 加载国标图层
    for ldef in GB_LAYER_DEFS:
        name  = ldef["name"]
        color = ldef.get("color", 7)
        ltype = ldef.get("linetype", "Continuous")
        lw    = ldef.get("lineweight", LW_THIN)
        if name not in doc.layers:
            try:
                layer = doc.layers.add(name, color=color, linetype=ltype)
                layer.lineweight = lw
            except Exception:
                try:
                    doc.layers.add(name, color=color)
                except Exception:
                    pass

    # 用户自定义图层（覆盖）
    for ldef in (user_layers or []):
        name  = ldef["name"]
        color = ldef.get("color", 7)
        ltype = ldef.get("linetype", "Continuous")
        if name not in doc.layers:
            try:
                doc.layers.add(name, color=color, linetype=ltype)
            except Exception:
                pass


# ─────────────────────────────────────────────
# 分发表（DISPATCHER）
# ─────────────────────────────────────────────

DISPATCHER = {
    # 基础图元
    "line":               draw_line,
    "circle":             draw_circle,
    "arc":                draw_arc,
    "rectangle":          draw_rectangle,
    "polyline":           draw_polyline,
    "text":               draw_text,
    "hatch":              draw_hatch,
    "spline":             draw_spline,
    "ellipse":            draw_ellipse,
    # 几何图形
    "polygon":            draw_polygon,
    "polygon_hole":       draw_polygon_hole,
    "bolt_circle":        draw_bolt_circle,
    "counterbore":        draw_counterbore,
    "countersink":        draw_countersink,
    "chamber":            draw_chamber,
    "keyway":             draw_keyway,
    "center_mark":        draw_center_mark,
    # 注释与标注
    "leader":             draw_leader,
    "mtext":              draw_mtext,
    # 尺寸标注
    "dim_linear":         draw_dimension_linear,
    "dim_aligned":        draw_dimension_aligned,
    "dim_radius":         draw_dimension_radius,
    "dim_diameter":       draw_dimension_diameter,
    "dim_angular":        draw_dimension_angular,
    # 国标新增符号
    "surface_roughness":  draw_surface_roughness,
    "tolerance_frame":    draw_tolerance_frame,
    "weld_symbol":        draw_weld_symbol,
    "break_line":         draw_break_line,
    "section_line":       draw_section_line,
    "center_hole":        draw_center_hole,
    # v7.0 新增
    "datum_mark":         draw_datum_mark,
    "view_label":         draw_view_label,
    "part_number":        draw_part_number,
    # v8.0 新增
    "projection_symbol":  draw_projection_symbol,
    # v9.0 新增: ISO 8015 GPS 基准体系
    "datum_chain":            draw_datum_chain,
    "general_tolerance_block": draw_general_tolerance_block,
    # 图框与标题栏
    "border":             draw_border,
    "grid":               draw_grid,
    # 机械零件
    "spring":             draw_spring,
    "gear":               draw_gear,
    "screw_thread":       draw_screw_thread,
    "o_ring":             draw_o_ring,
    "fillet":             draw_fillet,
    # 建筑
    "wall":               draw_wall,
    "door_arc":           draw_door_arc,
    "window":             draw_window,
    "stairs":             draw_stairs,
    # 电气符号
    "wire":               draw_wire,
    "bus_line":           draw_bus_line,
    "resistor":           draw_symbol_resistor,
    "capacitor":          draw_symbol_capacitor,
    "inductor":           draw_symbol_inductor,
    "diode":              draw_symbol_diode,
    "switch_no":          draw_symbol_switch_no,
    "gnd":                draw_gnd,
    "terminal":           draw_terminal,
    "node_dot":           draw_node_dot,
    "transformer":        draw_transformer,
    "transistor":         draw_transistor,
    "ic_chip":            draw_ic_chip,
    "connector":          draw_connector,
    # P&ID
    "pipe":               draw_pipe,
    "pipe_elbow":         draw_pipe_elbow,
    "valve":              draw_valve,
    "pump":               draw_pump,
    "tank":               draw_tank,
    # 表格
    "bom":                draw_bom_table,
    "revision_table":     draw_revision_table,
    # 块操作
    "block_def":          draw_block_def,
    "insert_block":       draw_insert_block,
}

# v5.0 插件加载
_PLUGIN_COUNT = load_plugins(DISPATCHER)
if _PLUGIN_COUNT > 0:
    print(f"[PLUGIN] Loaded {_PLUGIN_COUNT} evolved capability plugins", file=sys.stderr)

# 需要 (msp, doc, entity) 的图元类型
_DIM_ENTITIES   = {"dim_linear", "dim_aligned", "dim_radius",
                    "dim_diameter", "dim_angular", "datum_chain"}  # v9.0: +datum_chain
_TITLE_ENTITIES = {"title_block"}
_BLOCK_DEF      = {"block_def"}


# ─────────────────────────────────────────────
# 主生成函数
# ─────────────────────────────────────────────

def generate_dxf(spec: dict, output_path: str):
    version = spec.get("dxf_version", "R2010")
    standard = spec.get("standard", "GB")          # v10.0: 默认 GB（国内生产图纸）
    projection = spec.get("projection", "first")    # v10.0: ★ 默认第一角投影（ISO 128-1 / GB/T 17451）
    unit_system = spec.get("unit_system", "metric") # v9.0: metric 或 imperial
    gps_standard = spec.get("gps_standard", "ISO 8015")  # v9.0: GPS 基准标准

    doc     = ezdxf.new(version)
    msp     = doc.modelspace()

    # 设置单位（v9.0: 支持英制）
    try:
        if unit_system == "imperial":
            doc.units = units.Inches
        else:
            doc.units = units.MM
    except Exception:
        pass

    # 初始化图层
    setup_layers(doc, spec.get("layers", []))

    # 定义标准 dimstyle（ISO 箭头 / ANSI 箭头）
    try:
        dimstyle_name = "ISO_DIM" if standard == "ISO" else "GB_DIM"
        if dimstyle_name not in doc.dimstyles:
            ds = doc.dimstyles.new(dimstyle_name)
            ds.dxf.dimasz  = 3.5   # 箭头大小
            ds.dxf.dimtxt  = 3.5   # 尺寸文字高度
            ds.dxf.dimgap  = 1.0   # 文字与尺寸线间距
            ds.dxf.dimexo  = 2.0   # 尺寸界线起始偏移
            ds.dxf.dimexe  = 2.0   # 尺寸界线超出量
            if unit_system == "imperial":
                ds.dxf.dimlfac = 1.0 / MM_PER_INCH  # 显示值转换系数
    except Exception:
        pass

    # 第一遍: 块定义
    for entity in spec.get("entities", []):
        etype = entity.get("type", "").lower()
        if etype in _BLOCK_DEF:
            try:
                DISPATCHER[etype](msp, doc, entity)
            except Exception as e:
                print(f"[WARN] Skipping {etype}: {e}", file=sys.stderr)

    # 第二遍: 所有图元
    for entity in spec.get("entities", []):
        etype = entity.get("type", "").lower()
        if etype in _DIM_ENTITIES:
            try:
                DISPATCHER[etype](msp, doc, entity)
            except Exception as e:
                print(f"[WARN] Skipping {etype}: {e}", file=sys.stderr)
        elif etype in _TITLE_ENTITIES:
            try:
                # v8.0: 传递顶层 standard/projection 到 title_block
                if "standard" not in entity:
                    entity["standard"] = standard
                if "projection" not in entity:
                    entity["projection"] = projection
                draw_title_block(msp, doc, entity)
            except Exception as e:
                print(f"[WARN] Skipping title_block: {e}", file=sys.stderr)
        elif etype in _BLOCK_DEF:
            pass   # 已处理
        elif etype in DISPATCHER:
            try:
                DISPATCHER[etype](msp, entity)
            except Exception as e:
                print(f"[WARN] Skipping {etype}: {e}", file=sys.stderr)
        else:
            print(f"[WARN] Unknown entity type: {etype}", file=sys.stderr)

    doc.saveas(output_path)
    std_label = "ISO 8015 GPS" if standard == "ISO" else "GB/T"
    proj_label = "3rd Angle" if projection == "third" else "1st Angle"
    unit_label = "Imperial (inch)" if unit_system == "imperial" else "Metric (mm)"
    print(f"[OK] DXF saved: {output_path} (Standard: {std_label}, Projection: {proj_label}, Unit: {unit_label})")


def main():
    parser = argparse.ArgumentParser(
        description="Generate DXF from JSON spec (ISO 8015 GPS / ASME Y14.5 compliant) v7.0")
    parser.add_argument("spec",   help="Path to drawing spec JSON file")
    parser.add_argument("--output", "-o", default="output.dxf",
                        help="Output DXF file path")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"[ERROR] Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    generate_dxf(spec, args.output)


if __name__ == "__main__":
    main()
