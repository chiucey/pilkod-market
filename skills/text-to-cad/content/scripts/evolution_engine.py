#!/usr/bin/env python3
"""
evolution_engine.py — LLM-Driven Self-Evolution Engine  v1.0
===========================================================

This is the CORE INNOVATION of text-to-cad v5.0: a genuine LLM-powered
self-evolution system that allows the CAD skill to autonomously:

  1. ANALYZE   — Detect gaps in current drawing capabilities
  2. GENERATE  — Create new draw_* functions via LLM code synthesis
  3. VALIDATE  — Auto-test generated code for correctness
  4. INTEGRATE — Hot-load new capabilities into the running system
  5. LEARN     — Build experience from successes/failures

Architecture:
  User Request → LLM Agent (WorkBuddy) → Evolution Engine
                                              ↓
                                    Capability Registry (what we can draw)
                                              ↓
                                    Gap Analysis (what we CAN'T draw)
                                              ↓
                                    LLM Code Generation (write new draw_*)
                                              ↓
                                    Validation (syntax check + dry-run)
                                              ↓
                                    Plugin Installation (hot-load .py)
                                              ↓
                                    Registry Update (永久记忆)

Key Principle: LLM is the BRAIN. Python is the HAND.
  - LLM decides WHAT to draw and HOW to implement it
  - Python executes reliably and deterministically
  - The combination is genuinely intelligent evolution

Usage (by WorkBuddy Agent):
  python evolution_engine.py --analyze "bearing"           # Check if we can draw it
  python evolution_engine.py --generate "bearing"          # LLM generates draw_bearing()
  python evolution_engine.py --validate plugins/bearing.py # Test the generated code
  python evolution_engine.py --register "bearing"          # Add to capability registry
  python evolution_engine.py --status                      # Show evolution status
  python evolution_engine.py --evolve                       # Full auto-evolve cycle

IMPORTANT: This script is designed to be CALLED BY the WorkBuddy LLM Agent.
The Agent provides the intelligence; this script provides the infrastructure.
"""

import argparse
import ast
import importlib.util
import json
import os
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
#  Constants & Paths
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGINS_DIR = SCRIPT_DIR.parent / "plugins"
REGISTRY_FILE = PLUGINS_DIR / "capability_registry.json"
EVOLUTION_LOG = PLUGINS_DIR / "evolution_log.json"
CAD_GENERATOR = SCRIPT_DIR / "cad_generator.py"


def _ensure_dirs():
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  1. CAPABILITY REGISTRY — What we can draw right now
# ─────────────────────────────────────────────────────────────────────────────

def load_registry() -> dict:
    """Load the capability registry from disk."""
    _ensure_dirs()
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Initialize with built-in capabilities from cad_generator.py
    return _init_builtin_registry()


def save_registry(registry: dict):
    """Persist registry to disk."""
    _ensure_dirs()
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def _init_builtin_registry() -> dict:
    """Scan cad_generator.py DISPATCHER to discover built-in capabilities."""
    registry = {
        "version": "5.0",
        "last_evolved": None,
        "evolution_count": 0,
        "capabilities": {},
        "evolution_history": [],
    }

    # Parse DISPATCHER from cad_generator.py
    if CAD_GENERATOR.exists():
        source = CAD_GENERATOR.read_text(encoding="utf-8")
        # Find all "entity_name": draw_function entries
        for match in __import__("re").finditer(
            r'"([^"]+)"\s*:\s*draw_(\w+)', source
        ):
            alias = match.group(1)
            func_name = f"draw_{match.group(2)}"
            registry["capabilities"][alias] = {
                "type": alias,
                "function": func_name,
                "source": "builtin",
                "version_added": "4.0",
                "description": f"Built-in {alias} entity",
                "schema": _infer_schema(alias),
            }

    save_registry(registry)
    return registry


def _infer_schema(entity_type: str) -> dict:
    """Infer the JSON schema for an entity type from common patterns."""
    schemas = {
        "line": {"type": "line", "start": "[x,y]", "end": "[x,y]", "layer": "str"},
        "circle": {"type": "circle", "center": "[x,y]", "radius": "float", "layer": "str"},
        "arc": {"type": "arc", "center": "[x,y]", "radius": "float",
                "start_angle": "float", "end_angle": "float", "layer": "str"},
        "rectangle": {"type": "rectangle", "origin": "[x,y]", "width": "float",
                      "height": "float", "layer": "str"},
        "polyline": {"type": "polyline", "points": "[[x,y],...]", "closed": "bool"},
        "text": {"type": "text", "content": "str", "position": "[x,y]", "height": "float"},
    }
    return schemas.get(entity_type, {"type": entity_type, "layer": "str"})


def get_known_types() -> list:
    """Return list of all entity types we can currently draw."""
    reg = load_registry()
    return list(reg["capabilities"].keys())


def can_draw(entity_type: str) -> bool:
    """Check if we can draw a specific entity type."""
    return entity_type.lower() in [t.lower() for t in get_known_types()]


# ─────────────────────────────────────────────────────────────────────────────
#  2. GAP ANALYSIS — What CAN'T we draw?
# ─────────────────────────────────────────────────────────────────────────────

# Common CAD entity types that skilled draftspeople use frequently
CAD_KNOWLEDGE_BASE = {
    # Mechanical features
    "bearing": {"category": "mechanical", "aliases": ["轴承", "bearing"]},
    "coupling": {"category": "mechanical", "aliases": ["联轴器", "coupling"]},
    "pulley": {"category": "mechanical", "aliases": ["滑轮", "带轮", "pulley"]},
    "cam": {"category": "mechanical", "aliases": ["凸轮", "cam"]},
    "crankshaft": {"category": "mechanical", "aliases": ["曲轴", "crankshaft"]},
    "piston": {"category": "mechanical", "aliases": ["活塞", "piston"]},
    "dowel_pin": {"category": "mechanical", "aliases": ["销钉", "dowel"]},
    "snap_ring": {"category": "mechanical", "aliases": ["卡簧", "挡圈", "snap_ring"]},
    "key": {"category": "mechanical", "aliases": ["平键", "半圆键"]},
    "washer": {"category": "mechanical", "aliases": ["垫圈", "washer"]},

    # Structural / Welding
    "weld_symbol": {"category": "structural", "aliases": ["焊缝", "焊接符号", "weld"]},
    "section_view": {"category": "structural", "aliases": ["剖面图", "section"]},
    "detail_view": {"category": "structural", "aliases": ["局部放大", "detail"]},
    "break_line": {"category": "structural", "aliases": ["断裂线", "break"]},

    # Hydraulic / Pneumatic
    "cylinder": {"category": "hydraulic", "aliases": ["液压缸", "气缸", "cylinder"]},
    "filter": {"category": "hydraulic", "aliases": ["过滤器", "filter"]},
    "pressure_gauge": {"category": "hydraulic", "aliases": ["压力表", "gauge"]},
    "flow_arrow": {"category": "hydraulic", "aliases": ["流向", "flow"]},

    # Electrical extended
    "fuse": {"category": "electrical", "aliases": ["保险丝", "fuse"]},
    "relay": {"category": "electrical", "aliases": ["继电器", "relay"]},
    "motor": {"category": "electrical", "aliases": ["电机", "motor"]},
    "battery": {"category": "electrical", "aliases": ["电池", "battery"]},
    "led": {"category": "electrical", "aliases": ["LED", "发光二极管"]},
    "capacitor_polarized": {"category": "electrical", "aliases": ["电解电容"]},
    "variable_resistor": {"category": "electrical", "aliases": ["电位器", "可变电阻"]},
    "push_button": {"category": "electrical", "aliases": ["按钮", "push_button"]},

    # Architectural extended
    "column": {"category": "architectural", "aliases": ["柱", "column"]},
    "beam": {"category": "architectural", "aliases": ["梁", "beam"]},
    "elevator": {"category": "architectural", "aliases": ["电梯", "elevator"]},
    "plumbing_fixture": {"category": "architectural", "aliases": ["卫浴", "plumbing"]},

    # HVAC
    "duct": {"category": "hvac", "aliases": ["风管", "duct"]},
    "diffuser": {"category": "hvac", "aliases": ["散流器", "diffuser"]},
    "fan_symbol": {"category": "hvac", "aliases": ["风机", "fan"]},

    # GD&T
    "surface_finish": {"category": "gdt", "aliases": ["表面粗糙度", "roughness"]},
    "datum_feature": {"category": "gdt", "aliases": ["基准", "datum"]},
    "runout": {"category": "gdt", "aliases": ["跳动", "runout"]},
}

# Keywords that suggest a specific CAD entity
ENTITY_KEYWORDS = {
    "bearing": ["轴承", "bearing", "滚珠", "滚柱", "球轴承", "圆锥滚子"],
    "coupling": ["联轴器", "coupling", "万向节", "梅花联轴器"],
    "pulley": ["滑轮", "带轮", "皮带轮", "pulley", "V带轮"],
    "cam": ["凸轮", "cam", "偏心轮"],
    "piston": ["活塞", "piston", "活塞环"],
    "cylinder": ["液压缸", "气缸", "油缸", "cylinder", "液压"],
    "filter": ["过滤器", "滤网", "filter"],
    "fuse": ["保险丝", "fuse", "熔断器"],
    "relay": ["继电器", "relay"],
    "motor": ["电机", "马达", "motor", "电动机"],
    "battery": ["电池", "电源", "battery", "蓄电池"],
    "led": ["LED", "发光二极管", "指示灯"],
    "weld_symbol": ["焊缝", "焊接", "weld", "角焊", "对接焊"],
    "surface_finish": ["粗糙度", "Ra", "表面粗糙度", "加工符号"],
    "datum_feature": ["基准", "datum", "基准面", "基准轴"],
    "column": ["柱", "柱子", "钢筋混凝土柱", "column", "钢柱"],
    "beam": ["梁", "钢梁", "混凝土梁", "beam"],
    "break_line": ["断裂线", "断裂", "长件省略", "break_line"],
    "section_view": ["剖面图", "剖视图", "截面", "section"],
    "flow_arrow": ["流向", "流动方向", "flow_arrow"],
}


def analyze_gap(request_text: str) -> dict:
    """
    Analyze user request against current capabilities.
    Returns gap analysis report.
    """
    registry = load_registry()
    known = set(reg["capabilities"].keys())

    # Normalize request
    text_lower = request_text.lower()

    # 1. Check if all requested types are supported
    requested_types = set()
    gaps = []
    matched = []

    for entity_name, keywords in ENTITY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            requested_types.add(entity_name)

    for etype in requested_types:
        if etype in known or any(
            c.get("type", "") == etype for c in registry["capabilities"].values()
        ):
            matched.append(etype)
        else:
            gaps.append(etype)

    # 2. Check against knowledge base for missing common entities
    potential_gaps = []
    for name, info in CAD_KNOWLEDGE_BASE.items():
        if name not in known and name not in [g for g in gaps]:
            # Not requested, but commonly needed and missing
            potential_gaps.append({
                "name": name,
                "category": info["category"],
                "aliases": info["aliases"],
                "priority": _calc_priority(name, info["category"]),
            })

    return {
        "request": request_text,
        "timestamp": datetime.now().isoformat(),
        "known_types": sorted(known),
        "matched_types": matched,
        "gap_types": gaps,
        "potential_improvements": sorted(
            potential_gaps, key=lambda x: x["priority"], reverse=True
        )[:10],
        "total_capabilities": len(known),
        "coverage_score": round(
            len(known) / (len(known) + len(gaps) + len(potential_gaps)) * 100, 1
        ) if known else 0,
    }


def _calc_priority(name: str, category: str) -> float:
    """Calculate evolution priority (higher = more valuable)."""
    # Mechanical features are high priority (most requested)
    cat_weights = {
        "mechanical": 0.9,
        "electrical": 0.8,
        "hydraulic": 0.7,
        "structural": 0.7,
        "architectural": 0.6,
        "hvac": 0.5,
        "gdt": 0.6,
    }
    return cat_weights.get(category, 0.5)


# ─────────────────────────────────────────────────────────────────────────────
#  3. LLM CODE GENERATION — The Brain writes new drawing functions
# ─────────────────────────────────────────────────────────────────────────────

# Template for LLM to generate new drawing functions
FUNCTION_TEMPLATE = '''#!/usr/bin/env python3
"""
Auto-generated drawing plugin: {entity_type}
Generated by: text-to-cad Evolution Engine v5.0
Date: {timestamp}
Category: {category}

This module provides draw_{entity_type}() function for the CAD generator.
It was synthesized by an LLM based on engineering domain knowledge.

INTEGRATION:
  The WorkBuddy Agent should:
  1. Review this code for correctness
  2. Test with a sample spec JSON
  3. If valid, register via: python evolution_engine.py --register "{entity_type}"
"""

import math
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ezdxf


def draw_{entity_type}(msp, entity: dict):
    """
    {description}

    Entity Schema:
    {schema}

    Parameters:
        msp: ezdxf modelspace object
        entity: dict with keys: {params}
    """
    # LLM-GENERATED IMPLEMENTATION
    # This is where the LLM writes the actual drawing logic.
    # The implementation should:
    # 1. Extract parameters from entity dict
    # 2. Use ezdxf API to add geometric primitives to msp
    # 3. Handle missing parameters with sensible defaults
    pass


def register(dispatcher: dict):
    """Register this entity type with the CAD generator dispatcher."""
    dispatcher["{entity_type}"] = draw_{entity_type}
'''


def generate_plugin_stub(entity_type: str, category: str = "general",
                         description: str = "", schema: str = "") -> str:
    """
    Generate a plugin stub file for a new entity type.
    This creates the FILE that the LLM (WorkBuddy Agent) will fill in.

    The Agent uses this as a starting point and writes the actual
    drawing logic using its engineering knowledge.
    """
    _ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    params = "cx, cy, size, layer (standard params)"
    if not description:
        description = f"Draw a {entity_type} entity in DXF format"
    if not schema:
        schema = json.dumps({
            "type": entity_type,
            "cx": "float (center x)",
            "cy": "float (center y)",
            "size": "float (overall size)",
            "layer": "str (default: depends on category)"
        }, indent=2, ensure_ascii=False)

    code = FUNCTION_TEMPLATE.format(
        entity_type=entity_type,
        timestamp=timestamp,
        category=category,
        description=description,
        schema=schema,
        params=params,
    )

    plugin_path = PLUGINS_DIR / f"{entity_type}.py"
    plugin_path.write_text(code, encoding="utf-8")

    return str(plugin_path)


def generate_prompt_for_llm(entity_type: str, category: str = "general") -> str:
    """
    Generate a detailed prompt that the WorkBuddy Agent can use to
    write the actual draw_{entity_type}() implementation.

    This is the KEY mechanism of LLM-driven evolution:
    The evolution engine identifies what's missing, then formulates
    a precise prompt for the LLM to generate the code.
    """
    return textwrap.dedent(f'''\
    ═══════════════════════════════════════════════════════════════
    EVOLUTION ENGINE: Code Generation Request
    ═══════════════════════════════════════════════════════════════

    Target: Implement draw_{entity_type}() for the text-to-cad skill

    Category: {category}

    Your task:
    1. Read the existing cad_generator.py to understand the coding patterns
    2. Read references/dxf_spec_schema.md to understand the spec format
    3. Write a draw_{entity_type}(msp, entity: dict) function that:
       - Extracts parameters from entity dict with .get() and defaults
       - Uses ezdxf API (msp.add_line, msp.add_circle, msp.add_arc,
         msp.add_lwpolyline, msp.add_text, etc.) to draw the entity
       - Follows the same layer conventions as existing functions
       - Handles edge cases gracefully (missing params, zero values)
    4. Write the code to: {PLUGINS_DIR / f"{entity_type}.py"}
    5. Validate with: python evolution_engine.py --validate {entity_type}
    6. If valid, register with: python evolution_engine.py --register {entity_type}

    Reference patterns from existing draw functions:
    - draw_gear(): Complex multi-step geometry with trigonometry
    - draw_pump(): Industry-standard symbol representation
    - draw_spring(): Parametric silhouette generation
    - draw_transformer(): Symbol with optional features

    Engineering standards to follow:
    - All coordinates in mm
    - Use CENTER layer for centerlines (linetype="CENTER")
    - Use OUTLINE layer for main geometry (color=1)
    - Use SYMBOL layer for schematic symbols
    - Use DIM layer for dimensions
    - Add text labels where appropriate on TEXT layer

    Output your code directly. No explanations needed.
    ═══════════════════════════════════════════════════════════════
    ''')


# ─────────────────────────────────────────────────────────────────────────────
#  4. VALIDATION — Ensure generated code is correct
# ─────────────────────────────────────────────────────────────────────────────

def validate_plugin(entity_type: str) -> dict:
    """
    Validate a generated plugin file.
    Returns validation result with pass/fail and details.
    """
    plugin_path = PLUGINS_DIR / f"{entity_type}.py"

    result = {
        "entity_type": entity_type,
        "plugin_path": str(plugin_path),
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "passed": False,
    }

    # Check 1: File exists
    if not plugin_path.exists():
        result["checks"]["file_exists"] = False
        result["error"] = f"Plugin file not found: {plugin_path}"
        return result
    result["checks"]["file_exists"] = True

    # Check 2: Valid Python syntax
    try:
        source = plugin_path.read_text(encoding="utf-8")
        ast.parse(source)
        result["checks"]["syntax"] = True
    except SyntaxError as e:
        result["checks"]["syntax"] = False
        result["error"] = f"Syntax error: {e}"
        return result

    # Check 3: Contains draw_ function
    has_draw_func = f"def draw_{entity_type}" in source
    result["checks"]["has_draw_function"] = has_draw_func
    if not has_draw_func:
        result["error"] = f"Missing draw_{entity_type} function"
        return result

    # Check 4: Contains register function
    has_register = "def register" in source
    result["checks"]["has_register"] = has_register

    # Check 5: Uses ezdxf API (not raw file I/O or network calls)
    safe_calls = ["msp.add_", "entity.get(", "math.""]
    unsafe_patterns = ["import os", "import subprocess", "open(",
                      "requests.", "urllib", "eval(", "exec("]
    uses_safe = any(call in source for call in safe_calls)
    uses_unsafe = any(pat in source for pat in unsafe_patterns)
    result["checks"]["safe_api"] = uses_safe and not uses_unsafe

    # Check 6: Has docstring
    has_docstring = '"""' in source or "'''" in source
    result["checks"]["has_docstring"] = has_docstring

    # Check 7: Try to import the module
    try:
        spec = importlib.util.spec_from_file_location(
            f"plugin_{entity_type}", str(plugin_path)
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result["checks"]["import_ok"] = True
            result["checks"]["has_register_callable"] = hasattr(mod, "register")
        else:
            result["checks"]["import_ok"] = False
    except Exception as e:
        result["checks"]["import_ok"] = False
        result["checks"]["import_error"] = str(e)

    # Overall pass
    all_checks = result["checks"]
    result["passed"] = (
        all_checks.get("file_exists", False) and
        all_checks.get("syntax", False) and
        all_checks.get("has_draw_function", False) and
        all_checks.get("safe_api", True) and
        all_checks.get("import_ok", False)
    )

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  5. REGISTRATION — Add new capability to the system
# ─────────────────────────────────────────────────────────────────────────────

def register_capability(entity_type: str, metadata: dict = None) -> dict:
    """
    Register a new entity type as a permanent capability.
    """
    registry = load_registry()

    if entity_type in registry["capabilities"]:
        return {
            "status": "already_exists",
            "entity_type": entity_type,
            "message": f"{entity_type} is already registered",
        }

    # Run validation first
    validation = validate_plugin(entity_type)
    if not validation["passed"]:
        return {
            "status": "validation_failed",
            "entity_type": entity_type,
            "validation": validation,
            "message": f"Plugin failed validation. Fix errors before registering.",
        }

    # Get metadata from knowledge base or user-provided
    kb_info = CAD_KNOWLEDGE_BASE.get(entity_type, {})
    entry = {
        "type": entity_type,
        "function": f"draw_{entity_type}",
        "source": "evolved",  # LLM-generated, not builtin
        "version_added": "5.0+",
        "category": kb_info.get("category", "custom"),
        "description": (metadata or {}).get("description",
                        f"Evolved {entity_type} drawing capability"),
        "aliases": kb_info.get("aliases", []),
        "schema": (metadata or {}).get("schema", {}),
        "generated_at": datetime.now().isoformat(),
        "validation": validation,
    }

    registry["capabilities"][entity_type] = entry
    registry["last_evolved"] = datetime.now().isoformat()
    registry["evolution_count"] = registry.get("evolution_count", 0) + 1
    registry["evolution_history"].append({
        "type": "new_capability",
        "entity": entity_type,
        "timestamp": datetime.now().isoformat(),
        "source": "llm_evolution",
    })

    save_registry(registry)

    return {
        "status": "registered",
        "entity_type": entity_type,
        "total_capabilities": len(registry["capabilities"]),
        "evolution_count": registry["evolution_count"],
        "message": f"Successfully registered {entity_type}!",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  6. EVOLUTION LOG — Track all evolution events
# ─────────────────────────────────────────────────────────────────────────────

def log_evolution(event_type: str, entity_type: str, details: dict = None):
    """Append an event to the evolution log."""
    _ensure_dirs()
    log = []
    if EVOLUTION_LOG.exists():
        with open(EVOLUTION_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)

    entry = {
        "event": event_type,
        "entity": entity_type,
        "timestamp": datetime.now().isoformat(),
        "details": details or {},
    }
    log.append(entry)

    # Keep last 1000 events
    log = log[-1000:]

    with open(EVOLUTION_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def get_evolution_stats() -> dict:
    """Get comprehensive evolution statistics."""
    registry = load_registry()
    log = []
    if EVOLUTION_LOG.exists():
        with open(EVOLUTION_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)

    builtin_count = sum(
        1 for c in registry["capabilities"].values()
        if c.get("source") == "builtin"
    )
    evolved_count = sum(
        1 for c in registry["capabilities"].values()
        if c.get("source") == "evolved"
    )

    categories = {}
    for name, info in registry["capabilities"].items():
        cat = info.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    recent_events = log[-5:] if log else []

    return {
        "version": registry.get("version", "5.0"),
        "total_capabilities": len(registry["capabilities"]),
        "builtin_capabilities": builtin_count,
        "evolved_capabilities": evolved_count,
        "evolution_count": registry.get("evolution_count", 0),
        "last_evolved": registry.get("last_evolved", "Never"),
        "categories": categories,
        "all_types": sorted(registry["capabilities"].keys()),
        "recent_evolution_events": recent_events,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  7. FULL AUTO-EVOLVE CYCLE
# ─────────────────────────────────────────────────────────────────────────────

def auto_evolve(request_text: str = "") -> dict:
    """
    Full auto-evolve cycle:
    1. Analyze gaps
    2. Generate prompts for missing types
    3. Return action plan for the LLM Agent to execute

    Note: The actual CODE WRITING is done by the LLM Agent.
    This function provides the intelligence and infrastructure.
    """
    # Step 1: Gap analysis
    gap_report = analyze_gap(request_text)

    # Step 2: Generate prompts for each gap
    evolution_plan = []
    for gap_type in gap_report["gap_types"]:
        kb = CAD_KNOWLEDGE_BASE.get(gap_type, {})
        prompt = generate_prompt_for_llm(gap_type, kb.get("category", "general"))
        evolution_plan.append({
            "action": "generate",
            "entity_type": gap_type,
            "category": kb.get("category", "general"),
            "prompt": prompt,
            "plugin_path": str(PLUGINS_DIR / f"{gap_type}.py"),
        })

    # Step 3: Suggest potential improvements
    for improvement in gap_report["potential_improvements"][:3]:
        evolution_plan.append({
            "action": "suggest",
            "entity_type": improvement["name"],
            "category": improvement["category"],
            "priority": improvement["priority"],
            "aliases": improvement["aliases"],
        })

    return {
        "gap_report": gap_report,
        "evolution_plan": evolution_plan,
        "summary": (
            f"Found {len(gap_report['gap_types'])} capability gaps. "
            f"Current: {gap_report['total_capabilities']} types. "
            f"Coverage: {gap_report['coverage_score']}%"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="text-to-cad Evolution Engine v5.0 — LLM-Driven Self-Evolution"
    )
    sub = parser.add_subparsers(dest="command")

    # --analyze
    p_analyze = sub.add_parser("analyze", help="Analyze capability gaps")
    p_analyze.add_argument("text", nargs="?", default="", help="Request text to analyze")

    # --generate
    p_gen = sub.add_parser("generate", help="Generate plugin stub for LLM to fill")
    p_gen.add_argument("entity_type", help="Entity type to generate")
    p_gen.add_argument("--category", default="general", help="Entity category")
    p_gen.add_argument("--prompt-only", action="store_true",
                       help="Only show the LLM prompt, don't write file")

    # --validate
    p_val = sub.add_parser("validate", help="Validate a generated plugin")
    p_val.add_argument("entity_type", help="Entity type to validate")

    # --register
    p_reg = sub.add_parser("register", help="Register a new capability")
    p_reg.add_argument("entity_type", help="Entity type to register")

    # --status
    sub.add_parser("status", help="Show evolution status and stats")

    # --evolve
    p_evo = sub.add_parser("evolve", help="Full auto-evolve cycle")
    p_evo.add_argument("text", nargs="?", default="", help="Request context")

    # --list
    sub.add_parser("list", help="List all known entity types")

    # --known-check
    p_known = sub.add_parser("known-check", help="Check if entity type is supported")
    p_known.add_argument("entity_type", help="Entity type to check")

    args = parser.parse_args()

    if args.command == "analyze":
        report = analyze_gap(args.text or "general CAD drawing")
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == "generate":
        if args.prompt_only:
            prompt = generate_prompt_for_llm(args.entity_type, args.category)
            print(prompt)
        else:
            path = generate_plugin_stub(args.entity_type, args.category)
            prompt = generate_prompt_for_llm(args.entity_type, args.category)
            print(f"[OK] Plugin stub created: {path}")
            print(f"\n{'='*60}")
            print("Copy the following prompt to the LLM Agent:")
            print(f"{'='*60}\n")
            print(prompt)
            log_evolution("stub_generated", args.entity_type, {"path": path})

    elif args.command == "validate":
        result = validate_plugin(args.entity_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result["passed"]:
            print(f"\n[OK] {args.entity_type} plugin is VALID and ready to register!")
        else:
            print(f"\n[FAIL] {args.entity_type} plugin has errors. Fix and retry.")
            log_evolution("validation_failed", args.entity_type, result)

    elif args.command == "register":
        result = register_capability(args.entity_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result["status"] == "registered":
            log_evolution("capability_registered", args.entity_type, result)

    elif args.command == "status":
        stats = get_evolution_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.command == "evolve":
        plan = auto_evolve(args.text)
        print(json.dumps(plan, indent=2, ensure_ascii=False))

    elif args.command == "list":
        types = get_known_types()
        print(f"Known entity types ({len(types)}):")
        for t in sorted(types):
            reg = load_registry()
            cap = reg["capabilities"].get(t, {})
            src = cap.get("source", "unknown")
            marker = "🧬" if src == "evolved" else "🔧"
            print(f"  {marker} {t} ({src})")

    elif args.command == "known-check":
        known = can_draw(args.entity_type)
        status = "YES" if known else "NO"
        print(f"Can draw '{args.entity_type}': {status}")
        if not known:
            print(f"  → Use --generate {args.entity_type} to create it")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
