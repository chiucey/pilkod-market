#!/usr/bin/env python3
"""
spec_validation.py v1.0 - Drawing Spec JSON Auto-Validator (v11.0 Skill companion)
Validates drawing spec JSON files before DXF generation to ensure compliance
with ISO/GB standards and internal consistency.

Usage:
    python spec_validation.py <spec.json>
    python spec_validation.py <spec.json> --strict  # Exit with error code on warnings
"""

import json
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════
#  内置图元类型注册表（与 cad_generator.py DISPATCHER 同步）
# ═══════════════════════════════════════════════════════

SUPPORTED_ENTITY_TYPES = {
    # 基础
    "line", "circle", "arc", "rectangle", "polyline", "text", "hatch",
    "spline", "ellipse",
    # 几何
    "polygon", "polygon_hole", "bolt_circle", "counterbore", "countersink",
    "chamber", "keyway", "center_mark",
    # 注释
    "leader", "mtext",
    # 尺寸标注
    "dim_linear", "dim_aligned", "dim_radius", "dim_diameter", "dim_angular",
    # 国标符号
    "surface_roughness", "tolerance_frame", "weld_symbol", "break_line",
    "section_line", "center_hole",
    # v7.0+
    "datum_mark", "view_label", "part_number", "projection_symbol",
    # v9.0 GPS
    "datum_chain", "general_tolerance_block",
    # 图框
    "border", "grid",
    # 机械零件
    "spring", "gear", "screw_thread", "o_ring", "fillet",
    # 标题栏/BOM（特殊处理：需要 doc 参数）
    "title_block", "bom", "revision_table",
    # 块
    "block_def", "insert_block",
    # 建筑
    "wall", "door_arc", "window", "stairs",
    # 电气
    "wire", "bus_line", "resistor", "capacitor", "inductor", "diode",
    "switch_no", "gnd", "terminal", "node_dot", "transformer", "transistor",
    "ic_chip", "connector",
    # P&ID
    "pipe", "pipe_elbow", "valve", "pump", "tank",
}

# 标准图层定义
STANDARD_LAYERS = {
    "OUTLINE", "HIDDEN", "CENTER", "DIM", "TEXT", "HATCH",
    "BORDER", "SECTION", "PHANTOM", "DATUM", "SURFACE",
    "TOLERANCE", "WELD",
}

# 每类图元推荐图层
ENTITY_LAYER_MAP = {
    "line": {"OUTLINE", "HIDDEN", "CENTER", "SECTION", "PHANTOM", "WELD"},
    "circle": {"OUTLINE", "HIDDEN", "CENTER", "HATCH", "SURFACE", "DATUM"},
    "arc": {"OUTLINE", "HIDDEN", "CENTER", "SECTION", "PHANTOM"},
    "rectangle": {"OUTLINE", "HIDDEN", "BORDER", "SECTION"},
    "polyline": {"OUTLINE", "HIDDEN", "CENTER", "PHANTOM"},
    "text": {"TEXT", "DIM", "BORDER", "SURFACE", "TOLERANCE"},
    "mtext": {"TEXT"},
    "hatch": {"HATCH"},
    "dim_linear": {"DIM"},
    "dim_aligned": {"DIM"},
    "dim_radius": {"DIM"},
    "dim_diameter": {"DIM"},
    "dim_angular": {"DIM"},
    "surface_roughness": {"SURFACE"},
    "tolerance_frame": {"TOLERANCE"},
    "datum_mark": {"DATUM", "TOLERANCE"},
    "weld_symbol": {"WELD"},
    "break_line": {"OUTLINE"},
    "section_line": {"SECTION"},
    "center_hole": {"OUTLINE"},
    "datum_chain": {"DIM"},
    "general_tolerance_block": {"TEXT", "DIM"},
    "border": {"BORDER"},
    "title_block": {"BORDER"},
    "grid": {"DIM"},
    "spring": {"OUTLINE"},
    "gear": {"OUTLINE"},
    "screw_thread": {"OUTLINE"},
    "o_ring": {"OUTLINE"},
    "fillet": {"OUTLINE"},
    "bolt_circle": {"CENTER"},
    "counterbore": {"OUTLINE"},
    "countersink": {"OUTLINE"},
    "chamber": {"OUTLINE"},
    "keyway": {"OUTLINE"},
    "center_mark": {"CENTER"},
    "leader": {"TEXT"},
    "view_label": {"TEXT"},
    "part_number": {"TEXT"},
    "projection_symbol": {"BORDER"},
    "bom": {"BORDER"},
    "revision_table": {"BORDER"},
}

# 必须存在的顶层字段
REQUIRED_TOP_FIELDS = ["entities"]

# 每种图元必须包含的字段
ENTITY_REQUIRED_FIELDS = {
    "border": ["size"],
    "title_block": ["title", "scale"],
    "datum_mark": ["letter"],
    "datum_chain": ["segments"],
    "projection_symbol": ["projection"],
    "surface_roughness": ["ra"],
    "tolerance_frame": ["tolerances"],
    "weld_symbol": [],
    "break_line": ["start", "end"],
    "section_line": ["p1", "p2"],
    "center_hole": ["type"],
    "bom": ["rows"],
    "general_tolerance_block": [],
    "bolt_circle": ["center", "radius", "count"],
    "counterbore": ["center", "outer_radius"],
    "countersink": ["center", "outer_radius"],
    "keyway": ["origin", "width", "height"],
    "chamber": ["origin", "width", "depth"],
    "spring": ["cx", "cy", "outer_radius", "wire_diameter", "coils", "length"],
    "gear": ["cx", "cy", "outer_radius"],
    "screw_thread": ["cx", "cy", "radius", "length"],
}


class ValidationResult:
    """Validation result container."""

    def __init__(self):
        self.errors = []   # Critical: must fix
        self.warnings = [] # Recommended to fix
        self.info = []     # Informational

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def info_msg(self, msg):
        self.info.append(msg)

    @property
    def ok(self):
        return len(self.errors) == 0


def validate_spec(spec: dict, result: ValidationResult):
    """Main validation entry point."""

    # ── 1. 顶层字段检查 ──
    result.info_msg("━━ 1. 顶层字段检查 ━━")

    for field in REQUIRED_TOP_FIELDS:
        if field not in spec:
            result.error(f"缺少必填顶层字段: '{field}'")

    # 标准体系默认值检查
    standard = spec.get("standard", "GB")
    projection = spec.get("projection", "first")
    unit_system = spec.get("unit_system", "metric")
    gps_standard = spec.get("gps_standard", "ISO 8015")

    result.info_msg(f"  standard      = {standard}")
    result.info_msg(f"  projection    = {projection}")
    result.info_msg(f"  unit_system   = {unit_system}")
    result.info_msg(f"  gps_standard  = {gps_standard}")

    if standard not in ("GB", "ISO"):
        result.error(f"standard 值无效: '{standard}'（应为 'GB' 或 'ISO'）")

    if projection not in ("first", "third"):
        result.error(f"projection 值无效: '{projection}'（应为 'first' 或 'third'）")

    if unit_system not in ("metric", "imperial"):
        result.error(f"unit_system 值无效: '{unit_system}'（应为 'metric' 或 'imperial'）")

    # 默认值一致性提示
    if standard == "GB" and projection == "first":
        result.info_msg("  ✓ 默认值一致（GB + 第一角投影）")
    elif standard == "ISO" and projection == "third":
        result.info_msg("  ✓ ISO + 第三角投影（外贸模式）")
    elif standard == "GB" and projection == "third":
        result.warn("  ⚠ GB 标准 + 第三角投影（混合模式，请确认用户意图）")
    elif standard == "ISO" and projection == "first":
        result.info_msg("  ✓ ISO + 第一角投影（欧洲模式）")

    # ── 2. 基准体系检查 ──
    result.info_msg("")
    result.info_msg("━━ 2. 基准体系检查 ━━")

    datum_system = spec.get("datum_system")
    if datum_system:
        primary = datum_system.get("primary", {})
        secondary = datum_system.get("secondary", {})
        tertiary = datum_system.get("tertiary", {})

        result.info_msg(f"  主基准: {primary.get('letter', '?')} ({primary.get('type', '?')})")
        result.info_msg(f"  副基准: {secondary.get('letter', '?')} ({secondary.get('type', '?')})")
        result.info_msg(f"  第三基准: {tertiary.get('letter', '?')} ({tertiary.get('type', '?')})")

        if not primary.get("letter"):
            result.error("datum_system 缺少 primary.letter")
        if not primary.get("type"):
            result.warn("datum_system 缺少 primary.type")

        # 收集定义的基准字母
        defined_datums = set()
        for level in ["primary", "secondary", "tertiary"]:
            letter = datum_system.get(level, {}).get("letter")
            if letter:
                defined_datums.add(letter)
    else:
        result.warn("缺少 datum_system（基准体系定义）")

    # ── 3. 图元检查 ──
    result.info_msg("")
    result.info_msg("━━ 3. 图元类型与字段检查 ━━")

    entities = spec.get("entities", [])
    if not entities:
        result.error("entities 为空数组（至少需要 border + title_block）")

    entity_types = set()
    has_border = False
    has_title_block = False
    has_projection_symbol = False
    has_datum_mark = False
    has_tech_req = False
    datum_marks_found = set()
    datum_chain_count = 0
    dim_count = 0

    for i, entity in enumerate(entities):
        etype = entity.get("type", "").lower().strip()
        if not etype:
            result.error(f"entities[{i}]: 缺少 type 字段")
            continue

        entity_types.add(etype)

        # 检查是否为支持的图元类型
        if etype not in SUPPORTED_ENTITY_TYPES:
            result.warn(f"entities[{i}]: 未知图元类型 '{etype}'（可能需要触发演化模式）")
            continue

        # 检查图元必须字段
        required = ENTITY_REQUIRED_FIELDS.get(etype, [])
        for field in required:
            if field not in entity:
                result.error(f"entities[{i}] ({etype}): 缺少必填字段 '{field}'")

        # 检查图层
        layer = entity.get("layer", "")
        if layer and layer not in STANDARD_LAYERS:
            result.warn(f"entities[{i}] ({etype}): 使用非标准图层 '{layer}'")

        if layer and etype in ENTITY_LAYER_MAP:
            if layer not in ENTITY_LAYER_MAP[etype]:
                result.warn(
                    f"entities[{i}] ({etype}): 图层 '{layer}' 不在推荐图层 "
                    f"{ENTITY_LAYER_MAP[etype]} 中"
                )

        # 统计关键图元
        if etype == "border":
            has_border = True
        elif etype == "title_block":
            has_title_block = True
        elif etype == "projection_symbol":
            has_projection_symbol = True
        elif etype == "datum_mark":
            has_datum_mark = True
            letter = entity.get("letter", "")
            if letter:
                datum_marks_found.add(letter)
        elif etype == "datum_chain":
            datum_chain_count += 1
        elif etype in ("dim_linear", "dim_aligned", "dim_radius", "dim_diameter", "dim_angular"):
            dim_count += 1
        elif etype == "mtext":
            content = entity.get("content", "")
            if "技术要求" in content or "TECHNICAL REQUIREMENTS" in content.upper():
                has_tech_req = True

    result.info_msg(f"  图元总数: {len(entities)}")
    result.info_msg(f"  图元类型数: {len(entity_types)}")

    # ── 4. 必须图元检查 ──
    result.info_msg("")
    result.info_msg("━━ 4. 必须图元完整性检查 ━━")

    if not has_border:
        result.error("缺少 border（图框）— 每张图纸必须有标准图框")
    else:
        result.info_msg("  ✓ border（图框）")

    if not has_title_block:
        result.error("缺少 title_block（标题栏）— 每张图纸必须有标题栏")
    else:
        result.info_msg("  ✓ title_block（标题栏）")

    if not has_projection_symbol:
        result.warn("缺少 projection_symbol（投影符号）— 建议添加")
    else:
        result.info_msg("  ✓ projection_symbol（投影符号）")

    if not has_datum_mark and datum_system:
        result.warn("缺少 datum_mark（基准符号）— 有 datum_system 但未画基准符号")
    elif has_datum_mark:
        result.info_msg(f"  ✓ datum_mark（基准符号）: {datum_marks_found or '?'}")

    if not has_tech_req:
        result.warn("缺少技术要求（mtext 含 '技术要求'）— 建议添加")
    else:
        result.info_msg("  ✓ 技术要求")

    # ── 5. 基准链闭环检查 ──
    result.info_msg("")
    result.info_msg("━━ 5. 基准链标注检查 ━━")

    if datum_chain_count > 0:
        result.info_msg(f"  ✓ 基准链标注: {datum_chain_count} 组")
    elif dim_count > 0:
        result.warn(f"  ⚠ 有 {dim_count} 个尺寸标注但无 datum_chain（基准链闭环标注）")
    else:
        result.warn("  ⚠ 无任何尺寸标注")

    # 基准符号与基准体系对应检查
    if datum_system and datum_marks_found:
        defined_set = defined_datums
        marks_set = datum_marks_found
        if not defined_set.issubset(marks_set):
            missing = defined_set - marks_set
            result.warn(
                f"  ⚠ datum_system 定义了基准 {missing} 但无对应 datum_mark 图元"
            )
        if not marks_set.issubset(defined_set):
            extra = marks_set - defined_set
            result.warn(
                f"  ⚠ datum_mark 中有 {extra} 未在 datum_system 中定义"
            )

    # ── 6. 视图数量检查 ──
    result.info_msg("")
    result.info_msg("━━ 6. 视图数量检查 ━━")

    view_labels = [e for e in entities if e.get("type", "").lower() == "view_label"]
    if len(view_labels) < 2 and len(entities) > 5:
        # 有较多图元但少于2个视图标签
        result.warn(f"  ⚠ 仅有 {len(view_labels)} 个 view_label，建议至少2个视图")

    # ── 7. BOM 一致性检查 ──
    result.info_msg("")
    result.info_msg("━━ 7. BOM 一致性检查 ━━")

    bom_entities = [e for e in entities if e.get("type", "").lower() == "bom"]
    if bom_entities:
        bom = bom_entities[0]
        bom_standard = bom.get("standard", "GB")
        if bom_standard != standard:
            result.warn(
                f"  ⚠ BOM 标准 ('{bom_standard}') 与图纸标准 ('{standard}') 不一致"
            )
        rows = bom.get("rows", [])
        result.info_msg(f"  ✓ BOM 表: {len(rows)} 行记录")
    else:
        # 检查是否为装配图（通过 part_number 等图元判断）
        has_parts = any(e.get("type", "").lower() == "part_number" for e in entities)
        if has_parts:
            result.warn("  ⚠ 有 part_number 图元但缺少 BOM 表")

    # ── 8. 标题栏详细检查 ──
    result.info_msg("")
    result.info_msg("━━ 8. 标题栏详细检查 ━━")

    for e in entities:
        if e.get("type", "").lower() == "title_block":
            tb_standard = e.get("standard", spec.get("standard", "GB"))
            tb_projection = e.get("projection", spec.get("projection", "first"))
            if tb_standard != standard:
                result.error(
                    f"  ✗ title_block standard ('{tb_standard}') "
                    f"≠ 顶层 standard ('{standard}')"
                )
            if tb_projection != projection:
                result.error(
                    f"  ✗ title_block projection ('{tb_projection}') "
                    f"≠ 顶层 projection ('{projection}')"
                )
            if not e.get("title"):
                result.error("  ✗ title_block 缺少 title 字段")
            if not e.get("scale"):
                result.error("  ✗ title_block 缺少 scale 字段")
            if not e.get("material"):
                result.warn("  ⚠ title_block 缺少 material 字段")
            if not e.get("drawing_no"):
                result.warn("  ⚠ title_block 缺少 drawing_no 字段")
            break

    # ── 9. DXF 版本检查 ──
    result.info_msg("")
    result.info_msg("━━ 9. DXF 版本检查 ━━")

    dxf_version = spec.get("dxf_version", "R2010")
    if dxf_version not in ("R12", "R14", "R2000", "R2004", "R2007", "R2010", "R2013", "R2018"):
        result.warn(f"  ⚠ dxf_version '{dxf_version}' 可能不被 ezdxf 支持")
    else:
        result.info_msg(f"  ✓ DXF 版本: {dxf_version}")


def print_result(result: ValidationResult, spec_path: str):
    """Print validation results in a formatted way."""

    print(f"\n{'='*60}")
    print(f"  Spec Validation Report")
    print(f"  File: {spec_path}")
    print(f"{'='*60}\n")

    # Info messages
    if result.info:
        for msg in result.info:
            print(f"  {msg}")
        print()

    # Errors
    if result.errors:
        print(f"  ❌ ERRORS ({len(result.errors)}):")
        for msg in result.errors:
            print(f"     [E] {msg}")
        print()

    # Warnings
    if result.warnings:
        print(f"  ⚠️  WARNINGS ({len(result.warnings)}):")
        for msg in result.warnings:
            print(f"     [W] {msg}")
        print()

    # Summary
    print(f"{'─'*60}")
    if result.ok:
        if result.warnings:
            print(f"  Result: ✅ PASS (with {len(result.warnings)} warnings)")
        else:
            print(f"  Result: ✅ PASS (all checks passed)")
    else:
        print(f"  Result: ❌ FAIL ({len(result.errors)} errors, {len(result.warnings)} warnings)")
    print(f"{'='*60}\n")

    return result.ok


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate drawing spec JSON for ISO/GB compliance v1.0")
    parser.add_argument("spec", help="Path to spec JSON file")
    parser.add_argument("--strict", action="store_true",
                        help="Exit with error code on warnings")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"[ERROR] File not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = ValidationResult()
    validate_spec(spec, result)
    passed = print_result(result, str(spec_path))

    if not passed:
        sys.exit(1)
    elif args.strict and result.warnings:
        sys.exit(2)


if __name__ == "__main__":
    main()
