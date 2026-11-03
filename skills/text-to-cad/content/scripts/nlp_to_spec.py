#!/usr/bin/env python3
"""
nlp_to_spec.py v3.0 — Intelligent NLP → Drawing Spec JSON
===========================================================

v3.0 MAJOR UPGRADE: True LLM Semantic Understanding Mode
  - Dual-mode architecture: Regex (fast path) + LLM Delegation (smart path)
  - Evolution-aware: dynamically loads new entity types from capability registry
  - Semantic keyword graph instead of flat keyword matching
  - Intent classification with confidence scoring
  - Auto-fallback: if regex fails, delegates to WorkBuddy LLM Agent

Architecture (v3.0):
  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
  │ User Input  │ →  │ Intent Analyzer  │ →  │ Route Selector  │
  └─────────────┘    └──────────────────┘    └──────┬──────────┘
                           │                        │
                    ┌──────┴──────┐         ┌──────┴──────┐
                    │  Fast Path  │         │  Smart Path │
                    │  (Regex)    │         │  (LLM Call) │
                    └─────────────┘         └─────────────┘
                           │                        │
                    ┌──────┴────────────────────────┘
                    ↓
              JSON Spec → cad_generator.py → DXF

The KEY difference from v2.0:
  v2.0: "法兰" → regex match → hardcoded build_flange()
  v3.0: "画一个带6个螺栓孔的法兰盘" → LLM understands context →
         can handle novel combinations, ambiguous specs, and
         even delegate to evolution engine for unknown entity types

Usage:
  python nlp_to_spec.py "法兰盘 外径100 内径40 6个螺栓孔" -o spec.json
  python nlp_to_spec.py --mode smart "设计一个轴承座"
  python nlp_to_spec.py --demo
  python nlp_to_spec.py --check-capabilities
"""

import re
import json
import argparse
import sys
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────
#  Import evolution engine (if available)
# ─────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGINS_DIR = SCRIPT_DIR.parent / "plugins"

try:
    sys.path.insert(0, str(SCRIPT_DIR))
    from evolution_engine import (
        load_registry, get_known_types, can_draw,
        analyze_gap, generate_prompt_for_llm
    )
    HAS_EVOLUTION = True
except ImportError:
    HAS_EVOLUTION = False


# ─────────────────────────────────────────────
#  v2.0 Legacy: Helpers (kept for fast path)
# ─────────────────────────────────────────────

def nums(text: str):
    return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", text)]

def first_num(text: str) -> Optional[float]:
    m = re.search(r"[-+]?\d*\.?\d+", text)
    return float(m.group()) if m else None

def has_any(text: str, kws: list) -> bool:
    t = text.lower()
    return any(k.lower() in t for k in kws)

def has_all(text: str, kws: list) -> bool:
    t = text.lower()
    return all(k.lower() in t for k in kws)


# ─────────────────────────────────────────────
#  v3.0 NEW: Semantic Intent Analysis
# ─────────────────────────────────────────────

class IntentAnalyzer:
    """
    Semantic intent analyzer that goes beyond flat keyword matching.
    Uses a hierarchical keyword graph with category-aware scoring.
    """

    # Hierarchical semantic graph
    SEMANTIC_GRAPH = {
        "mechanical_part": {
            "keywords": {
                "rotational": ["轴", "shaft", "齿轮", "gear", "轴承", "bearing",
                               "联轴器", "coupling", "带轮", "滑轮", "pulley",
                               "凸轮", "cam", "曲轴", "crankshaft", "飞轮"],
                "fastening": ["法兰", "flange", "螺栓", "bolt", "螺母", "nut",
                              "垫圈", "washer", "销", "pin", "键", "key",
                              "弹簧", "spring", "卡簧", "挡圈"],
                "housing": ["底座", "base", "支架", "bracket", "箱体", "housing",
                            "壳体", "cover", "端盖", "轴承座"],
                "sealing": ["密封", "seal", "O型圈", "o_ring", "垫片", "gasket",
                            "油封"],
                "fluid_power": ["液压缸", "气缸", "cylinder", "阀", "valve",
                                "泵", "pump", "过滤器", "filter"],
            },
            "default_layer": "OUTLINE",
        },
        "electrical": {
            "keywords": {
                "passive": ["电阻", "resistor", "电容", "capacitor", "电感",
                            "inductor", "变压器", "transformer"],
                "active": ["二极管", "diode", "晶体管", "transistor", "LED",
                           "三极管", "场效应管", "IC", "芯片", "运放"],
                "switching": ["开关", "switch", "继电器", "relay", "保险丝",
                              "fuse", "接触器", "contactor", "按钮"],
                "power": ["电机", "motor", "电池", "battery", "发电机",
                          "generator"],
                "connection": ["导线", "wire", "总线", "bus", "端子",
                               "terminal", "连接器", "connector"],
            },
            "default_layer": "SYMBOL",
        },
        "architectural": {
            "keywords": {
                "structure": ["墙", "wall", "柱", "column", "梁", "beam",
                              "楼板", "地板", "基础", "foundation"],
                "opening": ["门", "door", "窗", "window", "洞口"],
                "vertical": ["楼梯", "stairs", "电梯", "elevator", "坡道"],
                "services": ["管道", "pipe", "风管", "duct", "卫浴", "plumbing"],
            },
            "default_layer": "WALL",
        },
        "piping": {
            "keywords": {
                "pipe_elements": ["管", "pipe", "弯头", "elbow", "三通", "tee",
                                  "法兰", "flange", "管件", "fitting"],
                "vessels": ["罐", "tank", "容器", "vessel", "塔", "tower"],
                "instruments": ["压力表", "gauge", "流量计", "温度计", "液位计"],
            },
            "default_layer": "PIPE",
        },
    }

    def analyze(self, text: str) -> dict:
        """
        Analyze user intent with confidence scoring.

        Returns:
            {
                "primary_intent": str,
                "secondary_intents": [str, ...],
                "confidence": float (0-1),
                "category": str,
                "detected_entities": [str, ...],
                "dimensions": dict,
                "is_complex": bool,
                "needs_llm": bool,
            }
        """
        t = text.lower()
        scores = {}
        detected_entities = []

        for category, cat_data in self.SEMANTIC_GRAPH.items():
            cat_score = 0
            for subcat, keywords in cat_data["keywords"].items():
                for kw in keywords:
                    if kw.lower() in t:
                        cat_score += 1
                        detected_entities.append(kw)
            if cat_score > 0:
                scores[category] = cat_score

        total_score = sum(scores.values()) if scores else 0
        confidence = min(total_score / 3.0, 1.0) if total_score > 0 else 0.0

        # Determine complexity
        ns = nums(t)
        is_complex = (
            len(detected_entities) > 2 or  # Multiple entity types
            len(ns) > 5 or                   # Many dimension values
            any(w in t for w in ["且", "并", "同时", "包含", "包括",
                                 "and", "with", "also", "plus"])
        )

        # Check if we need LLM delegation
        needs_llm = (
            confidence < 0.3 or  # Low confidence in regex matching
            is_complex or        # Complex multi-entity request
            self._has_unknown_entity(t, detected_entities) or
            self._has_engineering_jargon(t)  # Technical terms regex can't handle
        )

        # Check evolution engine for new capabilities
        if HAS_EVOLUTION:
            for entity in detected_entities:
                if can_draw(entity) and entity not in [
                    e for cats in self.SEMANTIC_GRAPH.values()
                    for subcats in cats["keywords"].values()
                    for e in subcats
                ]:
                    # Entity is known via evolution but not in static graph
                    pass

        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_intents[0][0] if sorted_intents else "generic"

        return {
            "primary_intent": primary,
            "secondary_intents": [i[0] for i in sorted_intents[1:3]],
            "confidence": round(confidence, 2),
            "category": primary,
            "detected_entities": list(set(detected_entities)),
            "dimensions": self._quick_dims(text),
            "is_complex": is_complex,
            "needs_llm": needs_llm,
        }

    def _has_unknown_entity(self, text: str, detected: list) -> bool:
        """Check if text contains entity references we can't handle."""
        known_flat = set()
        for cat_data in self.SEMANTIC_GRAPH.values():
            for kws in cat_data["keywords"].values():
                known_flat.update(kw.lower() for kw in kws)

        # If evolution engine is available, check dynamic registry too
        if HAS_EVOLUTION:
            known_flat.update(t.lower() for t in get_known_types())

        # Check for CAD-specific terms not in our known set
        cad_terms = [
            "轴承", "联轴器", "凸轮", "活塞", "液压缸", "气缸",
            "焊缝", "表面粗糙度", "基准", "断裂线",
        ]
        for term in cad_terms:
            if term in text and term not in [d.lower() for d in detected]:
                return True
        return False

    def _has_engineering_jargon(self, text: str) -> bool:
        """Detect complex engineering specifications."""
        jargon_patterns = [
            r"公差等级", r"IT\d", r"H7\w", r"Ra[\d.]", r"表面处理",
            r"热处理", r"硬度\s*\d+", r"HRC", r"HB\d",
            r"配合", r"过渡配合", r"间隙配合", r"过盈配合",
            r"形位公差", r"垂直度", r"平行度", r"同轴度",
        ]
        return any(re.search(p, text) for p in jargon_patterns)

    def _quick_dims(self, text: str) -> dict:
        """Quick dimension extraction."""
        d = {}
        ns = nums(text)
        t = text.lower()

        for pat, key in [
            (r"(?:φ|Φ|外径|直径|dia\.?|diameter)\.?\s*(\d+\.?\d*)", "diameter"),
            (r"内径\s*(\d+\.?\d*)", "inner_diameter"),
        ]:
            m = re.search(pat, t)
            if m:
                d[key] = float(m.group(1))

        if "长" in t and "宽" in t and len(ns) >= 2:
            d["length"] = ns[0]
            d["width"] = ns[1]
        elif ns and not d:
            d["size"] = ns[0]

        return d


# ─────────────────────────────────────────────
#  v3.0 NEW: LLM Delegation Mode
# ─────────────────────────────────────────────

def generate_llm_prompt(text: str, intent: dict) -> str:
    """
    Generate a detailed prompt for the WorkBuddy LLM Agent.
    This is the BRIDGE between the Python infrastructure and the LLM brain.

    The Agent receives this prompt and:
    1. Understands the full engineering context
    2. Decides which entity types to use (including evolved ones)
    3. Generates a complete JSON spec with proper parameters
    4. Can trigger evolution for unknown entity types
    """
    known = get_known_types() if HAS_EVOLUTION else ["(evolution engine not available)"]

    prompt = f'''\
=== LLM Delegation: Generate DXF Spec JSON ===

User Request: "{text}"

Intent Analysis:
  Category: {intent["category"]}
  Confidence: {intent["confidence"]}
  Detected Entities: {intent["detected_entities"]}
  Dimensions: {intent["dimensions"]}
  Complex: {intent["is_complex"]}

Available Entity Types:
  {json.dumps(sorted(known), indent=2)}

Reference Schema: see references/dxf_spec_schema.md

Task:
  1. Read the user's request and understand what they want to draw
  2. Check if required entity types exist in the available list
  3. If an entity type is MISSING, trigger evolution:
     - Run: python evolution_engine.py --generate <entity_type>
     - Write the drawing function based on engineering standards
     - Register with: python evolution_engine.py --register <entity_type>
  4. Generate a COMPLETE JSON spec with ALL entities
  5. Include proper layers, dimensions, and annotations
  6. Save the spec and run cad_generator.py to produce the DXF

Output: Write the spec JSON to a file. The spec must be valid for cad_generator.py.
'''
    return prompt


def smart_parse(text: str) -> dict:
    """
    v3.0 Smart Parse Mode:
    1. Analyze intent with semantic graph
    2. If high confidence + known entities → use fast path (regex)
    3. If low confidence or unknown → delegate to LLM Agent
    4. If evolution possible → trigger auto-evolve
    """
    analyzer = IntentAnalyzer()
    intent = analyzer.analyze(text)

    # Log the analysis
    print(f"[ANALYSIS] Intent: {intent['primary_intent']} "
          f"(confidence: {intent['confidence']:.0%})", file=sys.stderr)
    print(f"[ANALYSIS] Entities: {intent['detected_entities']}", file=sys.stderr)
    print(f"[ANALYSIS] Complex: {intent['is_complex']} | "
          f"Needs LLM: {intent['needs_llm']}", file=sys.stderr)

    if intent["needs_llm"]:
        # Delegate to LLM Agent
        prompt = generate_llm_prompt(text, intent)
        print(f"\n{'='*60}", file=sys.stderr)
        print("DELEGATING TO LLM AGENT", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        print(prompt)

        # Check if evolution is needed
        if HAS_EVOLUTION:
            gap = analyze_gap(text)
            if gap["gap_types"]:
                print(f"\n[EVOLUTION] Missing capabilities detected: "
                      f"{gap['gap_types']}", file=sys.stderr)
                print(f"[EVOLUTION] Run: python evolution_engine.py --evolve "
                      f'"{text}"', file=sys.stderr)

        return {
            "status": "llm_delegation_required",
            "intent": intent,
            "llm_prompt": prompt,
            "message": (
                "This request requires LLM intelligence. "
                "The prompt above should be sent to the WorkBuddy Agent."
            ),
        }
    else:
        # Use fast path (v2.0 legacy regex parser)
        spec = nlp_to_spec_legacy(text)
        spec["intent_analysis"] = intent
        return spec


# ─────────────────────────────────────────────
#  v2.0 Legacy: Dimension & Type Detection
# ─────────────────────────────────────────────

def parse_dimensions(text: str) -> dict:
    t = text.lower()
    d = {}
    for pat, key in [
        (r"(?:φ|Φ|外径|直径|dia\.?|diameter)\.?\s*(\d+\.?\d*)", "diameter"),
        (r"内径\s*(\d+\.?\d*)", "inner_diameter"),
        (r"(\d+\.?\d*)\s*mm?\s*(?:外径|直径|φ)", "diameter"),
        (r"(\d+\.?\d*)\s*mm?\s*内径", "inner_diameter"),
    ]:
        m = re.search(pat, t)
        if m:
            d[key] = float(m.group(1))
            break
    m = re.search(r"(?:r|半径|radius)\.?\s*(\d+\.?\d*)", t)
    if m:
        d["radius"] = float(m.group(1))
    for pat in [r"厚\s*度?\s*(\d+\.?\d*)", r"板\s*厚\s*(\d+\.?\d*)"]:
        m = re.search(pat, t)
        if m:
            d["thickness"] = float(m.group(1))
            break
    ns = nums(t)
    if has_all(t, ["长", "宽", "高"]) or re.search(r"length.*width.*height", t):
        if len(ns) >= 3:
            d["length"], d["width"], d["height"] = ns[0], ns[1], ns[2]
            ns = ns[3:]
    elif has_all(t, ["长", "宽"]) or re.search(r"length.*width", t):
        if len(ns) >= 2:
            d["length"], d["width"] = ns[0], ns[1]
            ns = ns[2:]
    if not d and ns:
        d["length"] = ns[0]
        if len(ns) > 1: d["width"] = ns[1]
        if len(ns) > 2: d["height"] = ns[2]
    return d


def detect_type(text: str) -> str:
    t = text.lower()
    if   has_any(t, ["法兰","flange"]):        return "flange"
    elif has_any(t, ["轴","shaft","棒料"]):     return "shaft"
    elif has_any(t, ["键槽","keyway","键"]):   return "keyway"
    elif has_any(t, ["螺纹","thread","螺孔"]): return "threaded_hole"
    elif has_any(t, ["孔","hole","钻孔"]):      return "hole"
    elif has_any(t, ["垫片","gasket","密封"]): return "gasket"
    elif has_any(t, ["齿轮","gear","齿形"]):    return "gear"
    elif has_any(t, ["建筑","平面图","floor","architect","墙","门","窗","楼梯"]):
                                                 return "architectural"
    elif has_any(t, ["电路","原理图","schematic","电气","电","电图"]):
                                                 return "electrical"
    elif has_any(t, ["槽","slot","凹槽","腔"]): return "slot"
    elif has_any(t, ["底座","base plate","安装板","plate"]): return "base_plate"
    elif has_any(t, ["箱体","housing","外壳","enclosure"]): return "housing"
    elif has_any(t, ["PCB","pcb","印制板"]):    return "pcb"
    elif has_any(t, ["支架","bracket","角","角钢"]): return "bracket"
    # v5.0: Check evolution registry for new types
    elif HAS_EVOLUTION:
        for known_type in get_known_types():
            if known_type in t:
                return known_type
    return "generic"


def detect_hole_count(text: str) -> int:
    t = text.lower()
    for pat in [r"(\d+)\s*孔", r"(\d+)\s*等\s*分", r"(\d+)\s*个\s*孔"]:
        m = re.search(pat, t)
        if m:
            return int(m.group(1))
    return 4


def detect_bolt_hole_dia(text: str, fallback: float) -> float:
    m = re.search(r"(?:φ|Φ|M|m|螺栓孔|孔径)\s*(\d+\.?\d*)", text.lower())
    return float(m.group(1)) if m else fallback


# ─────────────────────────────────────────────
#  Layer helpers (kept from v2.0)
# ─────────────────────────────────────────────

def base_layers(extra: list = None) -> list:
    layers = [
        {"name": "OUTLINE",  "color": 1},
        {"name": "CENTER",   "color": 4, "linetype": "CENTER"},
        {"name": "DIM",      "color": 3},
        {"name": "TEXT",     "color": 2},
        {"name": "HATCH",    "color": 5},
        {"name": "BORDER",   "color": 7},
    ]
    if extra:
        layers.extend(extra)
    return layers


def cross(cx: float, cy: float, size: float = 15) -> list:
    return [
        {"type": "line", "start": [cx - size, cy], "end": [cx + size, cy], "layer": "CENTER"},
        {"type": "line", "start": [cx, cy - size], "end": [cx, cy + size], "layer": "CENTER"},
    ]


def spec_header(description: str = "Generated Drawing") -> dict:
    return {
        "dxf_version": "R2010",
        "description": description,
        "layers": base_layers(),
    }


# ─────────────────────────────────────────────
#  Spec Builders (kept from v2.0)
# ─────────────────────────────────────────────

def build_flange(dims: dict, hole_count: int) -> dict:
    od = dims.get("diameter", 100)
    id_ = dims.get("inner_diameter", od * 0.4)
    pcd = od * 0.75
    cx, cy = 0, 0
    spec = spec_header(f"法兰盘 DN{int(od)}")
    spec["entities"] = [
        {"type": "circle",      "center": [cx, cy], "radius": od / 2, "layer": "OUTLINE"},
        {"type": "circle",      "center": [cx, cy], "radius": id_ / 2, "layer": "OUTLINE"},
        {"type": "bolt_circle", "cx": cx, "cy": cy, "pcd": pcd,
         "holes": hole_count, "hole_diameter": od * 0.04, "layer": "OUTLINE"},
        {"type": "text",        "content": f"法兰 DN{int(od)}",
         "position": [cx - 28, cy - 10], "height": 3, "layer": "TEXT"},
    ] + cross(cx, cy, od * 0.3) + [
        {"type": "dim_diameter", "center": [cx, cy], "radius": od / 2,
         "angle": 0, "layer": "DIM"},
        {"type": "dim_diameter", "center": [cx, cy], "radius": id_ / 2,
         "angle": 0, "layer": "DIM"},
    ]
    return spec


def build_shaft(dims: dict, hole_count: int = 0) -> dict:
    length = dims.get("length", 200)
    dia = dims.get("diameter", 40)
    cx, cy = 0, 0
    spec = spec_header(f"轴 Φ{dia}×{length}")
    spec["entities"] = [
        {"type": "rectangle", "origin": [cx, cy - dia/2], "width": length,
         "height": dia, "layer": "OUTLINE"},
        {"type": "text",      "content": f"轴 Φ{dia}×{length}",
         "position": [length/2 - 30, cy - dia/2 - 10], "height": 3, "layer": "TEXT"},
    ] + cross(length / 2, cy, dia * 0.3) + [
        {"type": "dim_linear",  "p1": [0, -dia/2 - 15], "p2": [length, -dia/2 - 15],
         "dimline_offset": -8, "angle": 0,  "layer": "DIM"},
        {"type": "dim_linear",  "p1": [length, cy - dia/2], "p2": [length, cy + dia/2],
         "dimline_offset": 8, "angle": 90, "layer": "DIM"},
    ]
    return spec


def build_generic(dims: dict, hole_count: int = 0) -> dict:
    L = dims.get("length", 100)
    W = dims.get("width", L)
    cx = L / 2
    spec = spec_header(f"零件 {L}×{W}")
    spec["entities"] = [
        {"type": "rectangle", "origin": [0, -W/2], "width": L, "height": W, "layer": "OUTLINE"},
        {"type": "text",      "content": f"零件 {L}×{W}",
         "position": [L/2 - 30, -W/2 - 10], "height": 3, "layer": "TEXT"},
    ] + cross(cx, 0, max(L, W) * 0.2)
    return spec


# ─────────────────────────────────────────────
#  v3.0: Unified parser with mode selection
# ─────────────────────────────────────────────

def nlp_to_spec_legacy(text: str) -> dict:
    """v2.0 compatible fast path (regex-based)."""
    text = text.strip()
    dims = parse_dimensions(text)
    dtype = detect_type(text)
    hole_cnt = detect_hole_count(text)
    builders = {
        "flange": build_flange,
        "shaft": build_shaft,
        "keyway": lambda d, h: build_generic(d, h),  # simplified
        "hole": lambda d, h: build_generic(d, h),
        "gasket": lambda d, h: build_generic(d, h),
        "base_plate": lambda d, h: build_generic(d, h),
        "bracket": lambda d, h: build_generic(d, h),
        "electrical": lambda d, h: build_generic(d, h),
        "architectural": lambda d, h: build_generic(d, h),
    }
    builder = builders.get(dtype, build_generic)
    spec = builder(dims, hole_cnt)
    spec["metadata"] = {
        "original_text": text,
        "detected_type": dtype,
        "dimensions": dims,
        "hole_count": hole_cnt,
        "generator": "nlp_to_spec.py v3.0 (legacy mode)",
        "mode": "fast",
    }
    return spec


def nlp_to_spec(text: str, mode: str = "auto") -> dict:
    """
    Unified NLP → Spec parser.

    Modes:
      auto   — Use IntentAnalyzer to decide (default)
      fast   — Always use regex (v2.0 compatible)
      smart  — Always delegate to LLM Agent
    """
    if mode == "fast":
        return nlp_to_spec_legacy(text)
    elif mode == "smart":
        return smart_parse(text)
    else:  # auto
        return smart_parse(text)


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="NLP → DXF Spec v3.0 (LLM-Enhanced)")
    parser.add_argument("text", nargs="?", help="Drawing description")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("--mode", choices=["auto", "fast", "smart"], default="auto",
                        help="Parsing mode (auto/fast/smart)")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--check-capabilities", action="store_true",
                        help="Check current drawing capabilities")
    args = parser.parse_args()

    if args.check_capabilities:
        if HAS_EVOLUTION:
            stats = __import__("evolution_engine", fromlist=["get_evolution_stats"]).get_evolution_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print("[WARN] Evolution engine not available. Install text-to-cad v5.0.")
        return

    if args.demo:
        print("=== NLP → DXF Spec v3.0 Demo ===\n")
        demos = [
            "法兰盘 外径100 内径40 6个螺栓孔",
            "画一个带轴承座的轴",
            "设计一个液压系统原理图",
            "轴承座 配合H7/p6 表面粗糙度Ra1.6",
        ]
        for d in demos:
            print(f"输入: {d}")
            analyzer = IntentAnalyzer()
            intent = analyzer.analyze(d)
            print(f"  意图: {intent['primary_intent']} "
                  f"(置信度: {intent['confidence']:.0%})")
            print(f"  实体: {intent['detected_entities']}")
            print(f"  需LLM: {'是' if intent['needs_llm'] else '否'}")
            print()
        return

    if not args.text:
        parser.print_help()
        sys.exit(1)

    result = nlp_to_spec(args.text, mode=args.mode)

    if result.get("status") == "llm_delegation_required":
        # Print the LLM prompt for the agent
        print(result["llm_prompt"])
    else:
        out = args.output or (args.text[:20].replace(" ", "_") + "_spec.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Spec saved: {out}")
        print(f"  Mode: {result['metadata'].get('mode', 'unknown')}")
        print(f"  Type: {result['metadata'].get('detected_type', 'unknown')}")
        print(f"  Entities: {len(result.get('entities', []))}")


if __name__ == "__main__":
    main()
