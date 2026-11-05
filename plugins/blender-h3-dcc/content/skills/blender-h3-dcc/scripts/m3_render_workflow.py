#!/usr/bin/env python3
"""Deterministic scaffolding for M3-driven Blender white-model rendering."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import h3_timeline_contract as timeline


FILL = "M3_FILL"
STRUCTURE_CHECK_NAMES = (
    "shots_and_cuts",
    "source_instance_conservation",
    "source_instance_screen_space_match",
    "source_instance_visibility_and_occlusion",
    "camera_motion_decomposition",
    "entity_motion_contracts",
    "interaction_and_contact_relations",
    "lighting_spatial_logic",
    "identity_and_temporal_stability",
)
STYLE_CHECK_NAMES = (
    "source_instance_render_completion",
    "style_route_application",
    "cross_domain_style_coherence",
)
CHECK_NAMES = STRUCTURE_CHECK_NAMES + STYLE_CHECK_NAMES
STYLE_BIBLE_FIELDS = (
    "world_and_era",
    "visual_language",
    "palette",
    "material_language",
    "environment_design",
    "prop_design",
    "lighting_and_atmosphere",
)
OFFICIAL_ONLINE_SUBMISSION_CHARACTER_LIMIT = 7000
DEFAULT_PROMPT_CHARACTER_BUDGET = 6500
CONTRACT_SCHEMA_VERSION = 4
APPEARANCE_SCHEMA_VERSION = 6
QA_SCHEMA_VERSION = 5
SHOT_SCALES = {
    "extreme_wide", "wide", "full", "medium_full", "medium", "close", "extreme_close"
}
ENTITY_CLASSES = {
    "living", "articulated", "rigid", "environment", "effect", "other"
}
IMPORTANCE_LEVELS = {"primary", "secondary", "context"}
MOTION_MODES = {
    "locomotion", "rigid_travel", "articulation", "manipulation",
    "deformation", "effect_evolution", "static", "camera_only",
}
VISIBILITY_STATES = {"visible", "partially_occluded", "offscreen"}
CAMERA_MOTION_TYPES = {
    "static", "tracking", "dolly", "orbit", "pan_tilt", "crane",
    "handheld", "compound",
}
CAMERA_SCALAR_TRENDS = {"stable", "increase", "decrease", "variable"}
CAMERA_AZIMUTH_TRENDS = {"stable", "clockwise", "counterclockwise", "variable"}
INSTANCE_REVIEW_STATUSES = {"preserved", "missing", "merged", "split", "replaced"}
MOTION_REVIEW_STATUSES = {
    "preserved", "frozen", "slowed", "wrong_direction", "wrong_phase", "replaced"
}
REFERENCE_SCOPES = {
    "global_world", "entity_set", "environment_only", "materials_only", "lighting_only"
}
SOURCE_VISUAL_POLICY = "spatiotemporal_evidence_only"
SILHOUETTE_POLICY = "stay_within_source_bounds_and_articulation_envelope"
REFERENCE_STRUCTURE_POLICY = "appearance_only_no_pose_framing_motion_layout_or_new_elements"
REFERENCE_EXCLUSION_TOKENS = (
    "pose,body-configuration,camera,framing,motion,timing,layout,count,bbox,"
    "visibility,occlusion,source-unsupported-elements"
)
REFERENCE_RISK_FLAGS = {
    "explicit_pose", "camera_or_framing", "environment_layout",
    "held_or_attached_elements", "large_deforming_or_occluding_elements",
    "source_unsupported_entities", "text_or_branding",
}
FIELD_LIMITS = {
    "style_source": (110, 35),
    "reference_route": (80, 28),
    "style_bible": (82, 28),
    "entity_source": (72, 16),
    "entity_target": (78, 18),
    "entity_finish": (100, 24),
    "entity_style_route": (70, 14),
    "entity_constraint": (108, 30),
    "motion_action": (92, 24),
    "motion_continuity": (112, 28),
    "motion_forbidden": (100, 24),
    "shot_camera": (142, 70),
    "camera_path": (110, 32),
    "camera_composition": (95, 28),
    "camera_forbidden": (90, 24),
    "shot_actions": (155, 80),
    "shot_layout": (142, 70),
    "shot_lighting": (92, 35),
    "anchor_camera": (65, 10),
    "anchor_composition": (70, 10),
    "anchor_layout": (65, 10),
    "tracked_orientation": (38, 7),
    "tracked_motion": (48, 8),
    "tracked_relations": (48, 8),
    "inventory_cues": (52, 14),
    "interaction_relation": (62, 18),
    "interaction_forbidden": (70, 20),
    "sound": (110, 40),
}


class WorkflowError(RuntimeError):
    pass


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: str | Path) -> dict[str, Any]:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise WorkflowError(f"JSON file does not exist: {resolved}")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"invalid JSON: {resolved}") from exc
    if not isinstance(payload, dict):
        raise WorkflowError(f"JSON root must be an object: {resolved}")
    return payload


def load_manifest(path: str | None) -> dict[str, Any] | None:
    return read_json(path) if path else None


def anchor_times(duration: float, fps: float, cut_times: list[float]) -> list[float]:
    last = max(0.0, duration - 1.0 / fps)
    count = min(9, max(5, math.ceil(last / 1.0) + 1))
    values = [last * index / (count - 1) for index in range(count)]
    for cut in cut_times:
        values.extend([max(0.0, cut - 2.0 / fps), min(last, cut + 2.0 / fps)])
    return sorted({round(value, 3) for value in values})


def manifest_shots(manifest: dict[str, Any] | None, duration: float, fps: float) -> list[dict[str, Any]]:
    raw = manifest.get("shots") if manifest else None
    if not isinstance(raw, list) or not raw:
        return [{"shot_id": 1, "start_seconds": 0.0, "end_seconds": duration}]
    shots = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise WorkflowError("manifest shots must be objects")
        shot_fps = float(item.get("fps") or fps)
        start_frame = int(item.get("frame_start"))
        end_frame = int(item.get("frame_end"))
        top_start = int(manifest.get("frame_start") or start_frame)
        start = max(0.0, (start_frame - top_start) / shot_fps)
        end = min(duration, (end_frame - top_start + 1) / shot_fps)
        shots.append({"shot_id": index, "start_seconds": round(start, 6), "end_seconds": round(end, 6)})
    return shots


def manifest_structure(manifest: dict[str, Any] | None) -> dict[str, Any] | None:
    evidence = manifest.get("structure_evidence") if manifest else None
    if not isinstance(evidence, dict) or evidence.get("schema_version") != 1:
        return None
    if not isinstance(evidence.get("objects"), list) or not isinstance(evidence.get("sample_frames"), list):
        return None
    return evidence


def structure_inventory(
    manifest: dict[str, Any] | None, duration: float, fps: float,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    evidence = manifest_structure(manifest)
    if evidence is None:
        placeholder = {
            "source_id": "V001",
            "source_name": FILL,
            "source_type": FILL,
            "root_name": FILL,
            "first_visible_seconds": FILL,
            "last_visible_seconds": FILL,
            "identity_cues": FILL,
            "evidence_origin": "visual_review",
        }
        return [placeholder], {}
    top_start = int(manifest.get("frame_start") or evidence["sample_frames"][0])
    lookup = {}
    inventory = []
    for item in evidence["objects"]:
        if not isinstance(item, dict) or not item.get("ever_projected_visible"):
            continue
        source_id = str(item.get("source_id") or "")
        samples = item.get("samples") if isinstance(item.get("samples"), list) else []
        visible_samples = [sample for sample in samples if isinstance(sample, dict) and sample.get("projected_visible")]
        if not source_id or not visible_samples:
            continue
        first_frame = min(int(sample["frame"]) for sample in visible_samples)
        last_frame = max(int(sample["frame"]) for sample in visible_samples)
        first_seconds = max(0.0, (first_frame - top_start) / fps)
        last_seconds = min(duration, (last_frame - top_start) / fps)
        dimensions = visible_samples[0].get("world_dimensions")
        cues = f"name={item.get('name')}; type={item.get('object_type')}; root={item.get('root_name')}"
        if isinstance(dimensions, list) and len(dimensions) == 3:
            cues += "; dimensions=" + ",".join(f"{float(value):.3f}" for value in dimensions)
        inventory.append({
            "source_id": source_id,
            "source_name": str(item.get("name") or source_id),
            "source_type": str(item.get("object_type") or "other"),
            "root_name": str(item.get("root_name") or item.get("name") or source_id),
            "first_visible_seconds": round(first_seconds, 3),
            "last_visible_seconds": round(last_seconds, 3),
            "identity_cues": cues,
            "evidence_origin": "blender_manifest",
        })
        lookup[source_id] = item
    if not inventory:
        return structure_inventory(None, duration, fps)
    return inventory, lookup


def seed_entities(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    for item in inventory:
        grouped.setdefault(str(item["root_name"]), []).append(str(item["source_id"]))
    entities = []
    for index, (root_name, source_ids) in enumerate(grouped.items(), start=1):
        display_root = root_name if FILL not in root_name else "Unresolved Source Group"
        entities.append({
            "label": f"Entity {index:02d} {display_root}"[:72],
            "entity_class": "other",
            "importance": "primary" if index == 1 else "context",
            "source_instance_ids": source_ids,
            "instance_count": len(source_ids),
            "conservation_rule": "one_to_one_no_merge_split_delete_or_replace",
            "source_role": FILL,
            "structural_constraints": FILL,
            "motion_contract": {
                "mode": FILL,
                "action": FILL,
                "continuity_requirement": FILL,
                "forbidden_substitutions": FILL,
            },
        })
    return entities


def nearest_structure_sample(
    item: dict[str, Any], manifest: dict[str, Any] | None, time_seconds: float,
) -> dict[str, Any] | None:
    samples = item.get("samples") if isinstance(item.get("samples"), list) else []
    if not samples:
        return None
    fps = float((manifest or {}).get("fps") or 24)
    frame_start = int((manifest or {}).get("frame_start") or samples[0].get("frame") or 0)
    target_frame = frame_start + time_seconds * fps
    return min(samples, key=lambda sample: abs(float(sample.get("frame") or 0) - target_frame))


def empty_entity_appearance() -> dict[str, Any]:
    return {
        "semantic_target": FILL,
        "final_materials_and_detail": FILL,
        "style_route": FILL,
        "source_visual_policy": SOURCE_VISUAL_POLICY,
        "silhouette_policy": SILHOUETTE_POLICY,
        "source_unsupported_additions": [],
    }


def preflight(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).expanduser().resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    source = timeline.probe(args.source)
    manifest = load_manifest(args.manifest)
    plan = timeline.make_plan(source, args.min_seconds, args.max_seconds)
    cuts = timeline.cut_candidates(source["path"], args.scene_threshold)
    shots = manifest_shots(manifest, source["duration"], source["fps"])
    inventory, structure_lookup = structure_inventory(manifest, source["duration"], source["fps"])
    entities = seed_entities(inventory)
    source_to_entity = {
        source_id: entity["label"]
        for entity in entities for source_id in entity["source_instance_ids"]
    }
    anchors = anchor_times(source["duration"], source["fps"], cuts)
    anchor_items = []
    for index, value in enumerate(anchors, start=1):
        frame = workdir / "source_anchor_frames" / f"anchor_{index:02d}.jpg"
        frame_time = min(value, source["duration"] - 1.0 / source["fps"])
        extract_frame(source["path"], frame_time, frame)
        tracked_instances = []
        for item in inventory:
            source_id = item["source_id"]
            evidence_item = structure_lookup.get(source_id)
            sample = nearest_structure_sample(evidence_item, manifest, value) if evidence_item else None
            bbox = sample.get("screen_bbox_percent") if isinstance(sample, dict) else None
            projected_visible = bool(isinstance(sample, dict) and sample.get("projected_visible") and isinstance(bbox, dict))
            tracked_instances.append({
                "source_id": source_id,
                "entity_label": source_to_entity[source_id],
                "visibility": "visible" if projected_visible or not evidence_item else "offscreen",
                "center_x_percent": bbox.get("center_x") if projected_visible else (FILL if not evidence_item else None),
                "center_y_percent": bbox.get("center_y") if projected_visible else (FILL if not evidence_item else None),
                "bbox_width_percent": bbox.get("width") if projected_visible else (FILL if not evidence_item else None),
                "bbox_height_percent": bbox.get("height") if projected_visible else (FILL if not evidence_item else None),
                "orientation": FILL,
                "motion_state": FILL,
                "spatial_relations": FILL,
            })
        anchor_items.append({
            "time_seconds": value,
            "source_frame": str(frame),
            "composition": {
                "shot_scale": FILL,
                "frame_balance_and_depth": FILL,
            },
            "camera_relation": FILL,
            "tracked_instances": tracked_instances,
            "key_layout_and_occlusion": FILL,
        })

    preflight_payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "source": source,
        "manifest_path": str(Path(args.manifest).expanduser().resolve()) if args.manifest else None,
        "timeline_plan": plan,
        "source_cut_candidates": cuts,
        "structure_evidence_available": bool(structure_lookup),
        "blender_structure_evidence": manifest_structure(manifest),
        "requires_m3_cut_review": bool(cuts),
        "rule": "Cut candidates are evidence only; M3 decides real shot boundaries after full-video review.",
    }
    contract = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "source": source,
        "watched_full_source": False,
        "shot_count": len(shots),
        "source_inventory": inventory,
        "entities": entities,
        "interaction_contracts": [],
        "shots": [
            {
                **shot,
                "camera_contract": {
                    "motion_type": FILL,
                    "tracked_target_entity": FILL,
                    "world_path": FILL,
                    "target_distance_trend": FILL,
                    "azimuth_trend": FILL,
                    "elevation_trend": FILL,
                    "focal_length_trend": FILL,
                    "screen_composition_rule": FILL,
                    "forbidden_reinterpretations": FILL,
                },
                "actions": FILL,
                "layout_and_occlusion": FILL,
                "lighting_spatial_logic": FILL,
            }
            for shot in shots
        ],
        "anchors": anchor_items,
        "m3_cut_review": {
            "candidate_times": cuts,
            "confirmed_real_cuts": FILL if cuts else [],
            "reasoning": FILL if cuts else "No source cut candidate requires review.",
        },
    }
    appearance = {
        "schema_version": APPEARANCE_SCHEMA_VERSION,
        "watched_references": False,
        "style_source_summary": FILL,
        "reference_routes": [],
        "global_style_bible": {field: FILL for field in STYLE_BIBLE_FIELDS},
        "entity_appearances": {
            entity["label"]: empty_entity_appearance() for entity in entities
        },
        "blockout_rejection": {
            "all_visible_entities_must_be_finished": True,
            "forbidden_final_look": "source construction proxy, default viewport material, incomplete proxy geometry, or any visibly unart-directed placeholder",
            "ambiguous_proxy_fallback": "Choose a plausible finished World Style design inside the exact source bounds; never leave it semantically or materially generic.",
        },
        "sound": "Natural environment and action sounds only; no dialogue or music unless requested.",
    }
    write_json(workdir / "preflight.json", preflight_payload)
    write_json(workdir / "render_contract.json", contract)
    write_json(workdir / "appearance.json", appearance)
    print(json.dumps({
        "preflight": str(workdir / "preflight.json"),
        "contract": str(workdir / "render_contract.json"),
        "appearance": str(workdir / "appearance.json"),
    }, ensure_ascii=False, indent=2))
    return 0


def contains_fill(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or FILL in value
    if isinstance(value, list):
        return any(contains_fill(item) for item in value)
    if isinstance(value, dict):
        return any(contains_fill(item) for item in value.values())
    return False


def normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return str(value)
    return re.sub(r"\s+", " ", value).strip()


def compact_text(value: Any, limit: int) -> str:
    text = normalize_text(value)
    if len(text) <= limit:
        return text
    clauses = [item.strip() for item in re.split(r"(?<=[.!?;。！？；])\s*", text) if item.strip()]
    kept: list[str] = []
    for clause in clauses:
        candidate = " ".join([*kept, clause])
        if len(candidate) <= limit - 1:
            kept.append(clause)
        else:
            break
    if kept:
        result = " ".join(kept).rstrip(" ,;:.。；")
        return result + "…"
    cut = text[: max(1, limit - 1)].rstrip()
    boundary = max(cut.rfind(" "), cut.rfind(","), cut.rfind(";"), cut.rfind("，"), cut.rfind("；"))
    if boundary >= max(12, int(limit * 0.55)):
        cut = cut[:boundary]
    return cut.rstrip(" ,;:.。；") + "…"


def text_character_count(value: Any) -> int:
    if isinstance(value, str):
        return len(normalize_text(value))
    if isinstance(value, list):
        return sum(text_character_count(item) for item in value)
    if isinstance(value, dict):
        return sum(text_character_count(item) for item in value.values())
    return 0


def compress_instance_aliases(aliases: list[str]) -> str:
    """Encode ordered I-number lists as ranges without losing membership."""
    numbers = []
    for alias in aliases:
        match = re.fullmatch(r"I([1-9][0-9]*)", alias)
        if not match:
            return ",".join(aliases)
        numbers.append(int(match.group(1)))
    if not numbers:
        return "none"
    ranges = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        ranges.append(f"I{start}-I{previous}" if start != previous else f"I{start}")
        start = previous = number
    ranges.append(f"I{start}-I{previous}" if start != previous else f"I{start}")
    return ",".join(ranges)


def render_budgeted_prompt(
    contract: dict[str, Any], appearance: dict[str, Any], factor: float
) -> tuple[str, list[dict[str, Any]]]:
    compacted: list[dict[str, Any]] = []

    def field(path: str, value: Any, limit_name: str) -> str:
        maximum, minimum = FIELD_LIMITS[limit_name]
        limit = max(minimum, int(maximum * factor))
        original = normalize_text(value)
        final = compact_text(original, limit)
        if final != original:
            compacted.append({
                "path": path,
                "original_characters": len(original),
                "final_characters": len(final),
                "field_limit": limit,
            })
        return final

    bible = appearance["global_style_bible"]
    aliases = {entity["label"]: f"E{index}" for index, entity in enumerate(contract["entities"], start=1)}
    instance_aliases = {
        item["source_id"]: f"I{index}" for index, item in enumerate(contract["source_inventory"], start=1)
    }
    entity_by_source_id = {
        source_id: entity
        for entity in contract["entities"] for source_id in entity["source_instance_ids"]
    }
    definitions = ["<Video 1>: authority for time, shots, camera, motion, layout, visibility, and occlusion."]
    definitions.append(
        "<World Style>: "
        f"{field('appearance.global_style_bible.world_and_era', bible['world_and_era'], 'style_bible')}; "
        f"{field('appearance.global_style_bible.visual_language', bible['visual_language'], 'style_bible')}."
    )
    definitions.append(
        "[INSTANCE REGISTRY] " + ",".join(
            f"{instance_aliases[item['source_id']]}=<{item['source_id']}>"
            for item in contract["source_inventory"]
        ) + "."
    )
    retention = [
        "<Video 1>: preserve all spatiotemporal structure and light direction."
    ]
    for index, entity in enumerate(contract["entities"]):
        label = entity["label"]
        alias = aliases[label]
        render_map = appearance["entity_appearances"][label]
        motion = entity["motion_contract"]
        instances = compress_instance_aliases([
            instance_aliases[source_id] for source_id in entity["source_instance_ids"]
        ])
        definitions.append(
            f"<{label}>={alias}[{entity['entity_class']}/{entity['importance']}/{motion['mode']}] "
            f"members={instances};n={entity['instance_count']};"
            f"src={field(f'contract.entities[{index}].source_role', entity['source_role'], 'entity_source')}; "
            f"final={field(f'appearance.entity_appearances.{label}.semantic_target', render_map['semantic_target'], 'entity_target')}; "
            f"finish={field(f'appearance.entity_appearances.{label}.final_materials_and_detail', render_map['final_materials_and_detail'], 'entity_finish')}; "
            f"style={field(f'appearance.entity_appearances.{label}.style_route', render_map['style_route'], 'entity_style_route')}."
        )
        retention.append(
            f"{alias}:{instances};1:1;n={entity['instance_count']}."
        )

    route_lines = []
    for route in appearance["reference_routes"]:
        targets = ",".join(aliases[label] for label in route["target_entities"]) or "all"
        safe = ",".join(route["safe_style_attributes"])
        review = route["reference_structure_review"]
        risks = ",".join(review["risk_flags"]) or "none"
        blocked = ",".join(review["blocked_reference_details"]) or "none"
        route_lines.append(
            f"{route['reference_id']} scope={route['scope']} targets={targets} "
            f"safe={safe} risks={risks} block={blocked} "
            f"policy={route['structure_transfer_policy']} exclude={REFERENCE_EXCLUSION_TOKENS}"
        )
    routes = " | ".join(route_lines) if route_lines else "No external reference; use user direction and <World Style>."
    detailed = [
        "[STYLE ROUTING] "
        f"{field('appearance.style_source_summary', appearance['style_source_summary'], 'style_source')} | {routes}",
        "[WORLD] "
        f"palette={field('appearance.global_style_bible.palette', bible['palette'], 'style_bible')} | "
        f"materials={field('appearance.global_style_bible.material_language', bible['material_language'], 'style_bible')} | "
        f"environment={field('appearance.global_style_bible.environment_design', bible['environment_design'], 'style_bible')} | "
        f"props={field('appearance.global_style_bible.prop_design', bible['prop_design'], 'style_bible')} | "
        f"light={field('appearance.global_style_bible.lighting_and_atmosphere', bible['lighting_and_atmosphere'], 'style_bible')}.",
        "[RENDER OBLIGATION] Finish every I#; proxies supply structure only. No raw, default, incomplete, or unart-directed look.",
        f"[SOURCE POLICY] All {','.join(aliases.values())}={SOURCE_VISUAL_POLICY};"
        f"shape={SILHOUETTE_POLICY};new=none.",
        "[ENTITY CONSERVATION] Keep every registered I# 1:1: exact count, bounds, placement, visibility, and occlusion; no merge, split, delete, replace, regroup, or new entity.",
        "[MOTION LOCKS]",
        "[SCREEN-SPACE LOCK] Match tracked I# metrics, orientation, motion, relations, shot scale, source camera/framing, composition, and depth.",
    ]
    static_aliases = []
    for index, entity in enumerate(contract["entities"]):
        motion = entity["motion_contract"]
        if motion["mode"] == "static":
            static_aliases.append(aliases[entity["label"]])
            continue
        detailed.append(
            f"{aliases[entity['label']]}:{motion['mode']} | "
            f"Act={field(f'contract.entities[{index}].motion_contract.action', motion['action'], 'motion_action')} | "
            f"Keep={field(f'contract.entities[{index}].motion_contract.continuity_requirement', motion['continuity_requirement'], 'motion_continuity')} | "
            f"Ban={field(f'contract.entities[{index}].motion_contract.forbidden_substitutions', motion['forbidden_substitutions'], 'motion_forbidden')}."
        )
    if static_aliases:
        detailed.append(
            f"[STATIC LOCK] {','.join(static_aliases)} stay source-fixed at all times; no motion, replacement, or regrouping."
        )
    detailed.append("[INTERACTIONS]")
    if contract["interaction_contracts"]:
        for index, interaction in enumerate(contract["interaction_contracts"]):
            participants = ",".join(instance_aliases[source_id] for source_id in interaction["source_instance_ids"])
            detailed.append(
                f"{interaction['interaction_id']}@{interaction['start_seconds']:.3f}-{interaction['end_seconds']:.3f}s "
                f"{participants}: rel={field(f'contract.interaction_contracts[{index}].relation', interaction['relation'], 'interaction_relation')}; "
                f"ban={field(f'contract.interaction_contracts[{index}].forbidden_change', interaction['forbidden_change'], 'interaction_forbidden')}."
            )
    else:
        detailed.append("No source interaction; do not invent contact, carrying, attachment, support, or manipulation.")
    one_shot = contract["shot_count"] == 1
    for index, shot in enumerate(contract["shots"], start=1):
        prefix = f"[Shot {index}] @{shot['start_seconds']:.3f}-{shot['end_seconds']:.3f}s"
        continuity = "ONE TAKE; no cuts, angle jumps, inserts, or transitions" if one_shot else "only the exact source cut; no added transition"
        camera = shot["camera_contract"]
        target = aliases.get(camera["tracked_target_entity"], "none")
        detailed.append(
            f"{prefix} {continuity} | "
            f"Cam={camera['motion_type']};target={target};"
            f"path={field(f'contract.shots[{index - 1}].camera_contract.world_path', camera['world_path'], 'camera_path')};"
            f"dist={camera['target_distance_trend']};azi={camera['azimuth_trend']};"
            f"elev={camera['elevation_trend']};lens={camera['focal_length_trend']};"
            f"comp={field(f'contract.shots[{index - 1}].camera_contract.screen_composition_rule', camera['screen_composition_rule'], 'camera_composition')};"
            f"ban={field(f'contract.shots[{index - 1}].camera_contract.forbidden_reinterpretations', camera['forbidden_reinterpretations'], 'camera_forbidden')} | "
            f"Act={field(f'contract.shots[{index - 1}].actions', shot['actions'], 'shot_actions')} | "
            f"Layout={field(f'contract.shots[{index - 1}].layout_and_occlusion', shot['layout_and_occlusion'], 'shot_layout')} | "
            f"Light={field(f'contract.shots[{index - 1}].lighting_spatial_logic', shot['lighting_spatial_logic'], 'shot_lighting')}."
        )
    detailed.append(
        "[ANCHORS exact t; V/P=I:x/y/w/h%; O=offscreen ranges; "
        "D=I:state/x/y/w/h/o/m/r]"
    )
    for index, item in enumerate(contract["anchors"]):
        composition = item["composition"]
        anchor_lines = [
            f"@{item['time_seconds']:.3f}s "
            f"F={composition['shot_scale']};"
            f"Comp={field(f'contract.anchors[{index}].composition.frame_balance_and_depth', composition['frame_balance_and_depth'], 'anchor_composition')};"
            f"Cam={field(f'contract.anchors[{index}].camera_relation', item['camera_relation'], 'anchor_camera')};"
            f"Lay={field(f'contract.anchors[{index}].key_layout_and_occlusion', item['key_layout_and_occlusion'], 'anchor_layout')}"
        ]
        static_visible: list[str] = []
        static_partial: list[str] = []
        static_offscreen: list[str] = []
        dynamic_items: list[str] = []
        for tracked_index, tracked in enumerate(item["tracked_instances"]):
            metric_path = f"contract.anchors[{index}].tracked_instances[{tracked_index}]"
            alias = instance_aliases[tracked["source_id"]]
            if tracked["visibility"] == "offscreen":
                geometry = "o"
            else:
                geometry = (
                    f"{float(tracked['center_x_percent']):.0f}/{float(tracked['center_y_percent']):.0f}/"
                    f"{float(tracked['bbox_width_percent']):.0f}/{float(tracked['bbox_height_percent']):.0f}"
                )
            visibility_code = {
                "visible": "v", "partially_occluded": "p", "offscreen": "o"
            }[tracked["visibility"]]
            source_entity = entity_by_source_id[tracked["source_id"]]
            if source_entity["importance"] == "primary" or source_entity["motion_contract"]["mode"] != "static":
                dynamic_items.append(
                    f"{alias}:{visibility_code}/{geometry}/"
                    f"o:{field(metric_path + '.orientation', tracked['orientation'], 'tracked_orientation')}/"
                    f"m:{field(metric_path + '.motion_state', tracked['motion_state'], 'tracked_motion')}/"
                    f"r:{field(metric_path + '.spatial_relations', tracked['spatial_relations'], 'tracked_relations')}"
                )
            elif tracked["visibility"] == "offscreen":
                static_offscreen.append(alias)
            elif tracked["visibility"] == "partially_occluded":
                static_partial.append(f"{alias}:{geometry}")
            else:
                static_visible.append(f"{alias}:{geometry}")
        if static_visible:
            anchor_lines.append("V=" + ",".join(static_visible))
        if static_partial:
            anchor_lines.append("P=" + ",".join(static_partial))
        if static_offscreen:
            anchor_lines.append("O=" + compress_instance_aliases(static_offscreen))
        if dynamic_items:
            anchor_lines.append("D=" + ",".join(dynamic_items))
        detailed.append(" ".join(anchor_lines))
    detailed.append(
        "[NEGATIVE] No new shot, camera, focus, entity, action, contact, text, motion reset, proxy, merge, or disappearance. Appearance only."
    )
    prompt = "\n\n".join([
        "subject_definitions:\n" + "\n".join(definitions),
        "summary:\n[video editing] Restyle <Video 1>; preserve its complete spatiotemporal structure.",
        "retention_analysis:\n" + "\n".join(retention),
        "detailed_description:\n" + "\n".join(detailed),
        "overall_soundscape:\n" + field("appearance.sound", appearance["sound"], "sound"),
        "non_diegetic_music:\nN/A",
    ]) + "\n"
    return prompt, compacted


def prompt_invariant_errors(
    prompt: str, contract: dict[str, Any], appearance: dict[str, Any]
) -> list[str]:
    errors = []
    for section in (
        "subject_definitions:",
        "summary:",
        "retention_analysis:",
        "detailed_description:",
        "overall_soundscape:",
        "non_diegetic_music:",
    ):
        if section not in prompt:
            errors.append(f"missing section {section}")
    for index in range(1, contract["shot_count"] + 1):
        if f"[Shot {index}]" not in prompt:
            errors.append(f"missing Shot {index}")
    for entity in contract["entities"]:
        if f"<{entity['label']}>" not in prompt:
            errors.append(f"missing entity {entity['label']}")
        if SILHOUETTE_POLICY not in prompt:
            errors.append("missing entity silhouette policy")
    for item in contract["source_inventory"]:
        if f"<{item['source_id']}>" not in prompt:
            errors.append(f"missing source instance {item['source_id']}")
    for anchor in contract["anchors"]:
        marker = f"@{anchor['time_seconds']:.3f}s"
        if marker not in prompt:
            errors.append(f"missing anchor {marker}")
    for marker in (
        "[STYLE ROUTING]", "[WORLD]", "[RENDER OBLIGATION]", "[ENTITY CONSERVATION]",
        "[MOTION LOCKS]", "[INTERACTIONS]", "[SCREEN-SPACE LOCK]", "[ANCHORS", "[NEGATIVE]",
    ):
        if marker not in prompt:
            errors.append(f"missing protected marker {marker}")
    if any(entity["motion_contract"]["mode"] == "static" for entity in contract["entities"]):
        if "[STATIC LOCK]" not in prompt:
            errors.append("missing static entity lock")
    if f"exclude={REFERENCE_EXCLUSION_TOKENS}" not in prompt and appearance["reference_routes"]:
        errors.append("missing complete reference structure exclusion set")
    for route in appearance["reference_routes"]:
        protected = [
            route["reference_id"], route["structure_transfer_policy"],
            *route["safe_style_attributes"],
            *route["reference_structure_review"]["blocked_reference_details"],
        ]
        for value in protected:
            if value not in prompt:
                errors.append(f"missing protected reference route content: {value}")
    return errors


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        errors.append(
            f"contract schema_version must be {CONTRACT_SCHEMA_VERSION}; rerun preflight with this plugin version"
        )
    if contract.get("watched_full_source") is not True:
        errors.append("watched_full_source must be true")
    duration = float(contract.get("source", {}).get("duration") or 0)
    inventory = contract.get("source_inventory")
    inventory_ids: list[str] = []
    if not isinstance(inventory, list) or not inventory:
        errors.append("source_inventory must be a non-empty list")
        inventory = []
    else:
        required_inventory_fields = {
            "source_id", "source_name", "source_type", "root_name",
            "first_visible_seconds", "last_visible_seconds", "identity_cues",
            "evidence_origin",
        }
        for index, item in enumerate(inventory, start=1):
            if not isinstance(item, dict) or set(item) != required_inventory_fields:
                errors.append(f"source_inventory {index}: must contain the exact required fields")
                continue
            source_id = item.get("source_id")
            if not isinstance(source_id, str) or not source_id.strip() or FILL in source_id:
                errors.append(f"source_inventory {index}: invalid source_id")
            else:
                inventory_ids.append(source_id)
            for field in ("source_name", "source_type", "root_name", "identity_cues"):
                if contains_fill(item.get(field)):
                    errors.append(f"source_inventory {index}: {field} is incomplete")
            if item.get("evidence_origin") not in {"blender_manifest", "visual_review"}:
                errors.append(f"source_inventory {index}: invalid evidence_origin")
            first = item.get("first_visible_seconds")
            last = item.get("last_visible_seconds")
            if not isinstance(first, (int, float)) or isinstance(first, bool):
                errors.append(f"source_inventory {index}: first_visible_seconds must be numeric")
            if not isinstance(last, (int, float)) or isinstance(last, bool):
                errors.append(f"source_inventory {index}: last_visible_seconds must be numeric")
            if isinstance(first, (int, float)) and isinstance(last, (int, float)):
                if float(first) < 0 or float(last) < float(first) or float(last) > duration + 0.05:
                    errors.append(f"source_inventory {index}: invalid visibility interval")
        if len(inventory_ids) != len(set(inventory_ids)):
            errors.append("source_inventory source_ids must be unique")

    shots = contract.get("shots")
    if not isinstance(shots, list) or not shots:
        errors.append("shots must be a non-empty list")
        shots = []
    if contract.get("shot_count") != len(shots):
        errors.append("shot_count must equal len(shots)")
    previous_end = 0.0
    for index, shot in enumerate(shots, start=1):
        if shot.get("shot_id") != index:
            errors.append(f"shot {index}: shot_id must be {index}")
        start = float(shot.get("start_seconds") or 0)
        end = float(shot.get("end_seconds") or 0)
        if abs(start - previous_end) > 0.05:
            errors.append(f"shot {index}: timeline is not contiguous")
        if end <= start or end > duration + 0.05:
            errors.append(f"shot {index}: invalid time range")
        previous_end = end
        for field in ("actions", "layout_and_occlusion", "lighting_spatial_logic"):
            if contains_fill(shot.get(field)):
                errors.append(f"shot {index}: {field} is incomplete")
        camera = shot.get("camera_contract")
        required_camera_fields = {
            "motion_type", "tracked_target_entity", "world_path",
            "target_distance_trend", "azimuth_trend", "elevation_trend",
            "focal_length_trend", "screen_composition_rule",
            "forbidden_reinterpretations",
        }
        if not isinstance(camera, dict) or set(camera) != required_camera_fields:
            errors.append(f"shot {index}: camera_contract must contain the exact required fields")
        elif contains_fill(camera):
            errors.append(f"shot {index}: camera_contract is incomplete")
        else:
            if camera.get("motion_type") not in CAMERA_MOTION_TYPES:
                errors.append(f"shot {index}: invalid camera motion_type")
            for field in ("target_distance_trend", "elevation_trend", "focal_length_trend"):
                if camera.get(field) not in CAMERA_SCALAR_TRENDS:
                    errors.append(f"shot {index}: invalid scalar camera trend {field}")
            if camera.get("azimuth_trend") not in CAMERA_AZIMUTH_TRENDS:
                errors.append(f"shot {index}: invalid azimuth camera trend")
    if shots and abs(previous_end - duration) > 0.05:
        errors.append("shots must cover the complete source duration")
    entities = contract.get("entities")
    if not isinstance(entities, list) or not entities:
        errors.append("entities must be a non-empty list")
        labels = []
    else:
        labels = []
        assigned_source_ids = []
        source_to_label = {}
        for entity in entities:
            label = entity.get("label") if isinstance(entity, dict) else None
            if not isinstance(label, str) or not label.strip():
                errors.append("every entity needs a label")
                continue
            labels.append(label)
            if entity.get("entity_class") not in ENTITY_CLASSES:
                errors.append(f"entity {label}: invalid entity_class")
            if entity.get("importance") not in IMPORTANCE_LEVELS:
                errors.append(f"entity {label}: invalid importance")
            source_ids = entity.get("source_instance_ids")
            if not isinstance(source_ids, list) or not source_ids:
                errors.append(f"entity {label}: source_instance_ids must be non-empty")
                source_ids = []
            elif len(source_ids) != len(set(source_ids)):
                errors.append(f"entity {label}: source_instance_ids must be unique")
            elif any(source_id not in inventory_ids for source_id in source_ids):
                errors.append(f"entity {label}: source_instance_ids must match source_inventory")
            if entity.get("instance_count") != len(source_ids):
                errors.append(f"entity {label}: instance_count must equal source_instance_ids length")
            if entity.get("conservation_rule") != "one_to_one_no_merge_split_delete_or_replace":
                errors.append(f"entity {label}: conservation_rule must remain one_to_one_no_merge_split_delete_or_replace")
            assigned_source_ids.extend(source_ids)
            for source_id in source_ids:
                source_to_label[source_id] = label
            if contains_fill(entity.get("source_role")) or contains_fill(entity.get("structural_constraints")):
                errors.append(f"entity {label}: description is incomplete")
            motion = entity.get("motion_contract")
            required_motion_fields = {
                "mode", "action", "continuity_requirement", "forbidden_substitutions"
            }
            if not isinstance(motion, dict) or set(motion) != required_motion_fields:
                errors.append(f"entity {label}: motion_contract must contain the exact required fields")
            elif contains_fill(motion):
                errors.append(f"entity {label}: motion_contract is incomplete")
            elif motion.get("mode") not in MOTION_MODES:
                errors.append(f"entity {label}: invalid motion mode")
        if len(labels) != len(set(labels)):
            errors.append("entity labels must be unique")
        if len(assigned_source_ids) != len(set(assigned_source_ids)):
            errors.append("each source instance may belong to only one entity")
        if set(assigned_source_ids) != set(inventory_ids):
            errors.append("entities must assign every source_inventory item exactly once")
        if not any(entity.get("importance") == "primary" for entity in entities if isinstance(entity, dict)):
            errors.append("at least one entity must have primary importance")
    if not isinstance(entities, list) or not entities:
        source_to_label = {}
    for index, shot in enumerate(shots, start=1):
        camera = shot.get("camera_contract")
        if isinstance(camera, dict):
            target = camera.get("tracked_target_entity")
            if target != "none" and target not in labels:
                errors.append(f"shot {index}: tracked_target_entity must be none or a contract entity label")

    interactions = contract.get("interaction_contracts")
    if not isinstance(interactions, list):
        errors.append("interaction_contracts must be a list")
    else:
        interaction_ids = []
        required_interaction_fields = {
            "interaction_id", "source_instance_ids", "start_seconds", "end_seconds",
            "relation", "forbidden_change",
        }
        for index, interaction in enumerate(interactions, start=1):
            if not isinstance(interaction, dict) or set(interaction) != required_interaction_fields:
                errors.append(f"interaction {index}: must contain the exact required fields")
                continue
            if contains_fill(interaction):
                errors.append(f"interaction {index}: is incomplete")
                continue
            interaction_ids.append(interaction.get("interaction_id"))
            source_ids = interaction.get("source_instance_ids")
            if not isinstance(source_ids, list) or not source_ids or any(source_id not in inventory_ids for source_id in source_ids):
                errors.append(f"interaction {index}: source_instance_ids must match source_inventory")
            start = interaction.get("start_seconds")
            end = interaction.get("end_seconds")
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or float(start) < 0 or float(end) < float(start) or float(end) > duration + 0.05:
                errors.append(f"interaction {index}: invalid time range")
        if len(interaction_ids) != len(set(interaction_ids)):
            errors.append("interaction_ids must be unique")
    anchors = contract.get("anchors")
    if not isinstance(anchors, list) or len(anchors) < 2:
        errors.append("at least two anchors are required")
    else:
        previous_anchor_time = -1.0
        for index, anchor in enumerate(anchors, start=1):
            if not isinstance(anchor, dict):
                errors.append(f"anchor {index}: must be an object")
                continue
            for field in ("time_seconds", "camera_relation", "key_layout_and_occlusion"):
                if contains_fill(anchor.get(field)):
                    errors.append(f"anchor {index}: {field} is incomplete")
            time_value = anchor.get("time_seconds")
            if not isinstance(time_value, (int, float)) or isinstance(time_value, bool):
                errors.append(f"anchor {index}: time_seconds must be numeric")
            else:
                current_time = float(time_value)
                if current_time <= previous_anchor_time or current_time < 0 or current_time > duration + 0.05:
                    errors.append(f"anchor {index}: time_seconds must be increasing and inside the source duration")
                previous_anchor_time = current_time
            composition = anchor.get("composition")
            if not isinstance(composition, dict) or set(composition) != {"shot_scale", "frame_balance_and_depth"}:
                errors.append(f"anchor {index}: composition must contain the exact required fields")
            elif contains_fill(composition):
                errors.append(f"anchor {index}: composition is incomplete")
            elif composition.get("shot_scale") not in SHOT_SCALES:
                errors.append(f"anchor {index}: invalid shot_scale")
            tracked_instances = anchor.get("tracked_instances")
            if not isinstance(tracked_instances, list) or not tracked_instances:
                errors.append(f"anchor {index}: tracked_instances must be a non-empty list")
                continue
            tracked_source_ids = []
            for tracked_index, tracked in enumerate(tracked_instances, start=1):
                prefix = f"anchor {index} tracked instance {tracked_index}"
                required_tracking_fields = {
                    "source_id", "entity_label", "visibility", "center_x_percent", "center_y_percent",
                    "bbox_width_percent", "bbox_height_percent", "orientation",
                    "motion_state", "spatial_relations",
                }
                if not isinstance(tracked, dict) or set(tracked) != required_tracking_fields:
                    errors.append(f"{prefix}: must contain the exact required fields")
                    continue
                source_id = tracked.get("source_id")
                entity_label = tracked.get("entity_label")
                if source_id not in inventory_ids:
                    errors.append(f"{prefix}: source_id must match source_inventory")
                else:
                    tracked_source_ids.append(source_id)
                if entity_label != source_to_label.get(source_id):
                    errors.append(f"{prefix}: entity_label must match source instance assignment")
                visibility = tracked.get("visibility")
                if visibility not in VISIBILITY_STATES:
                    errors.append(f"{prefix}: invalid visibility")
                for key in ("orientation", "motion_state", "spatial_relations"):
                    if contains_fill(tracked.get(key)):
                        errors.append(f"{prefix}: {key} is incomplete")
                metric_keys = (
                    "center_x_percent", "center_y_percent", "bbox_width_percent", "bbox_height_percent"
                )
                if visibility == "offscreen":
                    if any(tracked.get(key) is not None for key in metric_keys):
                        errors.append(f"{prefix}: offscreen metrics must be null")
                else:
                    for key in metric_keys:
                        value = tracked.get(key)
                        if not isinstance(value, (int, float)) or isinstance(value, bool):
                            errors.append(f"{prefix}: {key} must be numeric when visible")
                        elif not 0 <= float(value) <= 100:
                            errors.append(f"{prefix}: {key} must be between 0 and 100")
                    for key in ("bbox_width_percent", "bbox_height_percent"):
                        value = tracked.get(key)
                        if isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) <= 0:
                            errors.append(f"{prefix}: {key} must be greater than 0 when visible")
            if len(tracked_source_ids) != len(set(tracked_source_ids)):
                errors.append(f"anchor {index}: tracked source_ids must be unique")
            if set(tracked_source_ids) != set(inventory_ids):
                errors.append(f"anchor {index}: track every source_inventory instance exactly once")
    cut_review = contract.get("m3_cut_review")
    if not isinstance(cut_review, dict) or contains_fill(cut_review):
        errors.append("m3_cut_review is incomplete")
    return errors


def check_contract(args: argparse.Namespace) -> int:
    errors = validate_contract(read_json(args.contract))
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


def validate_appearance(appearance: dict[str, Any], entity_labels: list[str]) -> list[str]:
    errors = []
    if appearance.get("schema_version") != APPEARANCE_SCHEMA_VERSION:
        errors.append(
            f"appearance schema_version must be {APPEARANCE_SCHEMA_VERSION}; rerun preflight with this plugin version"
        )
    if appearance.get("watched_references") is not True:
        errors.append("watched_references must be true")
    if contains_fill(appearance.get("style_source_summary")):
        errors.append("style_source_summary is incomplete")
    routes = appearance.get("reference_routes")
    if not isinstance(routes, list):
        errors.append("reference_routes must be a list")
    else:
        route_ids = []
        for index, route in enumerate(routes, start=1):
            required_route_fields = {
                "reference_id", "scope", "target_entities", "safe_style_attributes",
                "reference_structure_review", "structure_transfer_policy",
            }
            if not isinstance(route, dict) or set(route) != required_route_fields:
                errors.append(f"reference route {index}: must contain the exact required fields")
                continue
            if contains_fill(route):
                errors.append(f"reference route {index}: is incomplete")
                continue
            route_id = route.get("reference_id")
            route_ids.append(route_id)
            if route.get("scope") not in REFERENCE_SCOPES:
                errors.append(f"reference route {index}: invalid scope")
            targets = route.get("target_entities")
            if not isinstance(targets, list) or any(label not in entity_labels for label in targets):
                errors.append(f"reference route {index}: target_entities must contain only contract entity labels")
            elif len(targets) != len(set(targets)):
                errors.append(f"reference route {index}: target_entities must be unique")
            elif route.get("scope") in {"entity_set", "environment_only"} and not targets:
                errors.append(f"reference route {index}: selected scope requires target_entities")
            safe = route.get("safe_style_attributes")
            if (
                not isinstance(safe, list) or not 1 <= len(safe) <= 6
                or any(not isinstance(item, str) or contains_fill(item) or len(item) > 48 for item in safe)
                or len(",".join(safe)) > 220
            ):
                errors.append(
                    f"reference route {index}: safe_style_attributes needs 1-6 short style-only strings"
                )
            review = route.get("reference_structure_review")
            required_review_fields = {"risk_flags", "blocked_reference_details", "mitigation_applied"}
            if not isinstance(review, dict) or set(review) != required_review_fields:
                errors.append(f"reference route {index}: invalid reference_structure_review")
            else:
                flags = review.get("risk_flags")
                blocked = review.get("blocked_reference_details")
                if (
                    not isinstance(flags, list) or len(flags) != len(set(flags))
                    or any(flag not in REFERENCE_RISK_FLAGS for flag in flags)
                ):
                    errors.append(f"reference route {index}: invalid or duplicate risk_flags")
                if (
                    not isinstance(blocked, list)
                    or any(not isinstance(item, str) or contains_fill(item) or len(item) > 72 for item in blocked)
                    or len(",".join(blocked)) > 300
                ):
                    errors.append(f"reference route {index}: invalid blocked_reference_details")
                elif flags and not blocked:
                    errors.append(f"reference route {index}: risk flags require blocked details")
                if review.get("mitigation_applied") is not True:
                    errors.append(f"reference route {index}: mitigation_applied must be true")
            if route.get("structure_transfer_policy") != REFERENCE_STRUCTURE_POLICY:
                errors.append(
                    f"reference route {index}: structure_transfer_policy must remain {REFERENCE_STRUCTURE_POLICY}"
                )
        if len(route_ids) != len(set(route_ids)):
            errors.append("reference route ids must be unique")
    bible = appearance.get("global_style_bible")
    if not isinstance(bible, dict) or set(bible) != set(STYLE_BIBLE_FIELDS):
        errors.append("global_style_bible must contain the exact required fields")
    elif contains_fill(bible):
        errors.append("all global_style_bible fields must be filled")
    if contains_fill(appearance.get("sound")):
        errors.append("appearance.sound is incomplete")
    mapping = appearance.get("entity_appearances")
    if not isinstance(mapping, dict):
        errors.append("entity_appearances must be an object")
    else:
        if set(mapping) != set(entity_labels):
            errors.append("entity_appearances keys must exactly match contract entity labels")
        required_render_fields = {
            "semantic_target", "final_materials_and_detail", "style_route", "source_visual_policy",
            "silhouette_policy", "source_unsupported_additions",
        }
        for label in entity_labels:
            render_map = mapping.get(label)
            if not isinstance(render_map, dict) or set(render_map) != required_render_fields:
                errors.append(f"entity appearance {label}: must contain the exact required fields")
                continue
            if contains_fill(render_map):
                errors.append(f"entity appearance {label}: is incomplete")
            if render_map.get("source_visual_policy") != SOURCE_VISUAL_POLICY:
                errors.append(f"entity appearance {label}: source_visual_policy must remain {SOURCE_VISUAL_POLICY}")
            if render_map.get("silhouette_policy") != SILHOUETTE_POLICY:
                errors.append(f"entity appearance {label}: silhouette_policy must remain {SILHOUETTE_POLICY}")
            if render_map.get("source_unsupported_additions") != []:
                errors.append(f"entity appearance {label}: source_unsupported_additions must remain empty")
    blockout = appearance.get("blockout_rejection")
    required_blockout_fields = {
        "all_visible_entities_must_be_finished", "forbidden_final_look", "ambiguous_proxy_fallback"
    }
    if not isinstance(blockout, dict) or set(blockout) != required_blockout_fields:
        errors.append("blockout_rejection must contain the exact required fields")
    else:
        if blockout.get("all_visible_entities_must_be_finished") is not True:
            errors.append("blockout_rejection.all_visible_entities_must_be_finished must be true")
        if contains_fill(blockout.get("forbidden_final_look")) or contains_fill(blockout.get("ambiguous_proxy_fallback")):
            errors.append("blockout_rejection text fields must be filled")
    return errors


def build_prompt(args: argparse.Namespace) -> int:
    contract = read_json(args.contract)
    appearance = read_json(args.appearance)
    errors = validate_contract(contract)
    labels = [entity["label"] for entity in contract.get("entities", []) if isinstance(entity, dict) and entity.get("label")]
    errors.extend(validate_appearance(appearance, labels))
    if errors:
        raise WorkflowError("; ".join(errors))

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report).expanduser().resolve() if args.report else output.with_name(output.stem + "_budget.json")
    if args.max_characters > OFFICIAL_ONLINE_SUBMISSION_CHARACTER_LIMIT or args.max_characters < 2000:
        raise WorkflowError(
            f"max-characters must be between 2000 and {OFFICIAL_ONLINE_SUBMISSION_CHARACTER_LIMIT}"
        )
    attempts = (1.0, 0.85, 0.70, 0.55, 0.40, 0.30, 0.25, 0.20)
    prompt = ""
    compacted: list[dict[str, Any]] = []
    used_factor = attempts[-1]
    for factor in attempts:
        candidate, candidate_compacted = render_budgeted_prompt(contract, appearance, factor)
        prompt = candidate
        compacted = candidate_compacted
        used_factor = factor
        if len(candidate) <= args.max_characters:
            break
    invariant_errors = prompt_invariant_errors(prompt, contract, appearance)
    within_budget = (
        len(prompt) <= args.max_characters
        and len(prompt) <= OFFICIAL_ONLINE_SUBMISSION_CHARACTER_LIMIT
    )
    ready_to_submit = within_budget and not invariant_errors
    report = {
        "schema_version": 6,
        "official_online_submission_character_limit": OFFICIAL_ONLINE_SUBMISSION_CHARACTER_LIMIT,
        "target_character_budget": args.max_characters,
        "prompt_characters": len(prompt),
        "within_budget": within_budget,
        "protected_content_valid": not invariant_errors,
        "ready_to_submit": ready_to_submit,
        "invariant_errors": invariant_errors,
        "compression_factor": used_factor,
        "source_text_characters": text_character_count(contract) + text_character_count(appearance),
        "compacted_field_count": len(compacted),
        "compacted_fields": compacted,
        "protected_content": [
            "all shot labels and continuity rules",
            "all source instance ids, entity assignments, exact counts, and one-to-one conservation rules",
            "all entity labels, semantic targets, finish maps, and retention entries",
            "all temporal anchors with per-instance visibility and screen-space metrics, plus primary/dynamic orientation and motion",
            "all dynamic per-entity motion contracts plus a complete static-entity lock",
            "camera motion decomposition and interaction/contact contracts",
            "reference routing, blockout rejection, and global-style sections",
            "complete per-reference safe attributes, risk blocks, and structure exclusions",
        ],
    }
    write_json(report_path, report)
    if not ready_to_submit:
        raise WorkflowError(
            f"prompt is not safe to submit; see {report_path} for budget or protected-content errors"
        )
    output.write_text(prompt, encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "budget_report": str(report_path),
        "shot_count": contract["shot_count"],
        "characters": len(prompt),
        "target_character_budget": args.max_characters,
        "within_budget": within_budget,
        "protected_content_valid": not invariant_errors,
        "ready_to_submit": ready_to_submit,
        "compacted_field_count": len(compacted),
    }, ensure_ascii=False, indent=2))
    return 0


def extract_frame(video: str, time_seconds: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        timeline.ffmpeg_executable(), "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{time_seconds:.6f}", "-i", video, "-frames:v", "1", str(output),
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip().splitlines()
        raise WorkflowError(detail[-1] if detail else "failed to extract QA frame") from exc


def compose_frame_pair(source_frame: Path, result_frame: Path, output: Path) -> None:
    command = [
        timeline.ffmpeg_executable(), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source_frame), "-i", str(result_frame),
        "-filter_complex", "[0:v][1:v]hstack=inputs=2", "-frames:v", "1", str(output),
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip().splitlines()
        raise WorkflowError(detail[-1] if detail else "failed to compose QA comparison frame") from exc


def dense_motion_times(duration: float, fps: float) -> list[float]:
    """Return 9-21 evenly spaced times, dense enough to expose frozen articulation."""
    last = max(0.0, duration - 1.0 / fps)
    count = max(9, min(21, int(math.floor(duration / 0.5)) + 1))
    if count == 1 or last == 0:
        return [0.0]
    return [round(last * index / (count - 1), 6) for index in range(count)]


def prepare_qa(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).expanduser().resolve()
    frames_dir = workdir / "qa_frames"
    source = timeline.probe(args.source)
    result = timeline.probe(args.result)
    contract = read_json(args.contract)
    appearance = read_json(args.appearance)
    contract_errors = validate_contract(contract)
    labels = [entity["label"] for entity in contract.get("entities", []) if isinstance(entity, dict) and entity.get("label")]
    contract_errors.extend(validate_appearance(appearance, labels))
    if contract_errors:
        raise WorkflowError("; ".join(contract_errors))
    tolerance = args.cut_tolerance_frames / result["fps"]
    source_cuts = timeline.cut_candidates(source["path"], args.scene_threshold)
    result_cuts = timeline.cut_candidates(result["path"], args.scene_threshold)
    extra_cuts = timeline.unmatched_cuts(source_cuts, result_cuts, tolerance)
    duration_error = abs(result["duration"] - source["duration"])
    aspect_error = abs(result["aspect_ratio"] - source["aspect_ratio"])
    deterministic = {
        "duration_pass": duration_error <= 1.0 / result["fps"] + 1e-6,
        "duration_error_seconds": duration_error,
        "aspect_ratio_pass": aspect_error <= args.aspect_tolerance,
        "aspect_ratio_error": aspect_error,
        "source_cut_candidates": source_cuts,
        "result_cut_candidates": result_cuts,
        "result_only_cut_candidates": extra_cuts,
        "cut_preflight_pass": not extra_cuts,
    }
    deterministic["hard_preflight_pass"] = all([
        deterministic["duration_pass"], deterministic["aspect_ratio_pass"], deterministic["cut_preflight_pass"]
    ])
    frame_pairs = []
    for index, anchor in enumerate(contract["anchors"], start=1):
        time_seconds = min(float(anchor["time_seconds"]), source["duration"] - 1.0 / source["fps"])
        source_frame = frames_dir / f"anchor_{index:02d}_source.jpg"
        result_frame = frames_dir / f"anchor_{index:02d}_result.jpg"
        comparison_frame = frames_dir / f"anchor_{index:02d}_comparison.jpg"
        extract_frame(source["path"], time_seconds, source_frame)
        extract_frame(result["path"], time_seconds, result_frame)
        compose_frame_pair(source_frame, result_frame, comparison_frame)
        frame_pairs.append({
            "time_seconds": time_seconds,
            "expected": {
                "composition": anchor["composition"],
                "camera_relation": anchor["camera_relation"],
                "tracked_instances": anchor["tracked_instances"],
                "key_layout_and_occlusion": anchor["key_layout_and_occlusion"],
            },
            "source_frame": str(source_frame),
            "result_frame": str(result_frame),
            "comparison_frame": str(comparison_frame),
        })
    motion_frames_dir = workdir / "qa_motion_frames"
    motion_frame_pairs = []
    for index, time_seconds in enumerate(dense_motion_times(source["duration"], source["fps"]), start=1):
        source_frame = motion_frames_dir / f"motion_{index:02d}_source.jpg"
        result_frame = motion_frames_dir / f"motion_{index:02d}_result.jpg"
        comparison_frame = motion_frames_dir / f"motion_{index:02d}_comparison.jpg"
        extract_frame(source["path"], time_seconds, source_frame)
        extract_frame(result["path"], time_seconds, result_frame)
        compose_frame_pair(source_frame, result_frame, comparison_frame)
        motion_frame_pairs.append({
            "time_seconds": time_seconds,
            "source_frame": str(source_frame),
            "result_frame": str(result_frame),
            "comparison_frame": str(comparison_frame),
        })
    primary_labels = {
        entity["label"] for entity in contract["entities"] if entity["importance"] == "primary"
    }
    primary_screen_space_reviews = []
    for anchor in contract["anchors"]:
        for tracked in anchor["tracked_instances"]:
            if tracked["entity_label"] not in primary_labels:
                continue
            primary_screen_space_reviews.append({
                "time_seconds": anchor["time_seconds"],
                "source_id": tracked["source_id"],
                "expected": {
                    "visibility": tracked["visibility"],
                    "center_x_percent": tracked["center_x_percent"],
                    "center_y_percent": tracked["center_y_percent"],
                    "bbox_width_percent": tracked["bbox_width_percent"],
                    "bbox_height_percent": tracked["bbox_height_percent"],
                },
                "observed": {
                    "visibility": FILL,
                    "center_x_percent": FILL,
                    "center_y_percent": FILL,
                    "bbox_width_percent": FILL,
                    "bbox_height_percent": FILL,
                },
                "evidence": FILL,
            })
    dynamic_entities = [
        entity for entity in contract["entities"]
        if entity["motion_contract"]["mode"] not in {"static", "camera_only"}
    ]
    qa = {
        "schema_version": QA_SCHEMA_VERSION,
        "source": source,
        "result": result,
        "deterministic_preflight": deterministic,
        "frame_pairs": frame_pairs,
        "motion_frame_pairs": motion_frame_pairs,
        "source_inventory": contract["source_inventory"],
        "style_target": appearance,
        "entity_motion_targets": {
            entity["label"]: entity["motion_contract"] for entity in contract["entities"]
        },
        "camera_contract_targets": {
            str(shot["shot_id"]): shot["camera_contract"] for shot in contract["shots"]
        },
        "interaction_targets": contract["interaction_contracts"],
        "acceptance_thresholds": {
            "source_instance_center_delta_percentage_points_max": 8,
            "source_instance_bbox_delta_percentage_points_max": 10,
            "visibility_must_match": True,
            "orientation_must_match": True,
            "spatial_relations_must_match": True,
            "source_instance_count_must_match_exactly": True,
            "merge_split_delete_replace_allowed": False,
            "unlisted_entities_allowed": False,
            "unfinished_blockout_entities_allowed": False,
        },
        "watched_full_result": False,
        "reviewed_style_target": False,
        "reviewed_all_comparison_frames": False,
        "reviewed_all_motion_frames": False,
        "reviewed_every_source_instance": False,
        "source_instance_reviews": {
            item["source_id"]: {"status": FILL, "evidence": FILL}
            for item in contract["source_inventory"]
        },
        "entity_motion_reviews": {
            entity["label"]: {
                "status": FILL,
                "root_translation_matches": None,
                "articulation_phase_matches": None,
                "contact_timing_matches": None,
                "evidence": FILL,
            }
            for entity in dynamic_entities
        },
        "primary_screen_space_reviews": primary_screen_space_reviews,
        "checks": {name: {"pass": None, "evidence": FILL} for name in CHECK_NAMES},
        "verdict": FILL,
        "summary": FILL,
    }
    output = workdir / "qa_review.json"
    write_json(output, qa)
    print(json.dumps({
        "qa": str(output), "frames": str(frames_dir),
        "motion_frames": str(motion_frames_dir),
        "deterministic_preflight": deterministic,
    }, ensure_ascii=False, indent=2))
    return 0


def finalize_qa(args: argparse.Namespace) -> int:
    qa = read_json(args.qa)
    errors = []
    if qa.get("schema_version") != QA_SCHEMA_VERSION:
        errors.append(f"QA schema_version must be {QA_SCHEMA_VERSION}; rerun prepare-qa with this plugin version")
    if qa.get("watched_full_result") is not True:
        errors.append("watched_full_result must be true")
    if qa.get("reviewed_style_target") is not True:
        errors.append("reviewed_style_target must be true")
    if qa.get("reviewed_all_comparison_frames") is not True:
        errors.append("reviewed_all_comparison_frames must be true")
    if qa.get("reviewed_all_motion_frames") is not True:
        errors.append("reviewed_all_motion_frames must be true")
    if qa.get("reviewed_every_source_instance") is not True:
        errors.append("reviewed_every_source_instance must be true")
    checks = qa.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(CHECK_NAMES):
        errors.append("QA checks must contain the exact required check names")
        checks = {}
    failed_checks = []
    for name in CHECK_NAMES:
        value = checks.get(name)
        if not isinstance(value, dict) or not isinstance(value.get("pass"), bool):
            errors.append(f"check {name}: pass must be boolean")
            continue
        if contains_fill(value.get("evidence")):
            errors.append(f"check {name}: evidence is incomplete")
        if value["pass"] is False:
            failed_checks.append(name)
    inventory = qa.get("source_inventory")
    inventory_ids = [
        item.get("source_id") for item in inventory
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    ] if isinstance(inventory, list) else []
    reviews = qa.get("source_instance_reviews")
    failed_instances = []
    if not inventory_ids:
        errors.append("source_inventory must be present in QA")
    if not isinstance(reviews, dict) or set(reviews) != set(inventory_ids):
        errors.append("source_instance_reviews must exactly match source_inventory ids")
    else:
        for source_id in inventory_ids:
            review = reviews[source_id]
            if not isinstance(review, dict) or set(review) != {"status", "evidence"}:
                errors.append(f"source instance review {source_id}: must contain status and evidence")
                continue
            status = review.get("status")
            if status not in INSTANCE_REVIEW_STATUSES:
                errors.append(f"source instance review {source_id}: invalid status")
            if contains_fill(review.get("evidence")):
                errors.append(f"source instance review {source_id}: evidence is incomplete")
            if status in INSTANCE_REVIEW_STATUSES - {"preserved"}:
                failed_instances.append(source_id)
    if failed_instances and "source_instance_conservation" not in failed_checks:
        failed_checks.append("source_instance_conservation")
    motion_targets = qa.get("entity_motion_targets")
    dynamic_labels = {
        label for label, target in motion_targets.items()
        if isinstance(target, dict) and target.get("mode") not in {"static", "camera_only"}
    } if isinstance(motion_targets, dict) else set()
    motion_reviews = qa.get("entity_motion_reviews")
    failed_motion_entities = []
    if not isinstance(motion_reviews, dict) or set(motion_reviews) != dynamic_labels:
        errors.append("entity_motion_reviews must exactly match all dynamic entities")
    else:
        required_motion_fields = {
            "status", "root_translation_matches", "articulation_phase_matches",
            "contact_timing_matches", "evidence",
        }
        for label in sorted(dynamic_labels):
            review = motion_reviews[label]
            if not isinstance(review, dict) or set(review) != required_motion_fields:
                errors.append(f"entity motion review {label}: must contain the exact required fields")
                continue
            status = review.get("status")
            if status not in MOTION_REVIEW_STATUSES:
                errors.append(f"entity motion review {label}: invalid status")
            for key in (
                "root_translation_matches", "articulation_phase_matches", "contact_timing_matches"
            ):
                if not isinstance(review.get(key), bool):
                    errors.append(f"entity motion review {label}: {key} must be boolean")
            if contains_fill(review.get("evidence")):
                errors.append(f"entity motion review {label}: evidence is incomplete")
            if status != "preserved" or any(review.get(key) is not True for key in (
                "root_translation_matches", "articulation_phase_matches", "contact_timing_matches"
            )):
                failed_motion_entities.append(label)
    if failed_motion_entities and "entity_motion_contracts" not in failed_checks:
        failed_checks.append("entity_motion_contracts")
    screen_reviews = qa.get("primary_screen_space_reviews")
    screen_mismatches = []
    required_screen_fields = {"time_seconds", "source_id", "expected", "observed", "evidence"}
    metric_fields = (
        "center_x_percent", "center_y_percent", "bbox_width_percent", "bbox_height_percent"
    )
    if not isinstance(screen_reviews, list) or not screen_reviews:
        errors.append("primary_screen_space_reviews must be a non-empty list")
    else:
        thresholds = qa.get("acceptance_thresholds", {})
        center_limit = float(thresholds.get("source_instance_center_delta_percentage_points_max", 8))
        bbox_limit = float(thresholds.get("source_instance_bbox_delta_percentage_points_max", 10))
        for index, review in enumerate(screen_reviews, start=1):
            if not isinstance(review, dict) or set(review) != required_screen_fields:
                errors.append(f"primary screen-space review {index}: must contain the exact required fields")
                continue
            expected = review.get("expected")
            observed = review.get("observed")
            required_measurement_fields = {"visibility", *metric_fields}
            if (
                not isinstance(expected, dict) or set(expected) != required_measurement_fields
                or not isinstance(observed, dict) or set(observed) != required_measurement_fields
            ):
                errors.append(f"primary screen-space review {index}: invalid measurement fields")
                continue
            if contains_fill(review.get("evidence")):
                errors.append(f"primary screen-space review {index}: evidence is incomplete")
            expected_visibility = expected.get("visibility")
            observed_visibility = observed.get("visibility")
            mismatch_reasons = []
            if observed_visibility not in VISIBILITY_STATES:
                errors.append(f"primary screen-space review {index}: invalid observed visibility")
                continue
            if observed_visibility != expected_visibility:
                mismatch_reasons.append(
                    f"visibility {observed_visibility} != {expected_visibility}"
                )
            if observed_visibility == "offscreen":
                if any(observed.get(key) is not None for key in metric_fields):
                    errors.append(f"primary screen-space review {index}: offscreen observed metrics must be null")
            else:
                for key in metric_fields:
                    value = observed.get(key)
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        errors.append(f"primary screen-space review {index}: observed {key} must be numeric")
                        continue
                    if expected_visibility == "offscreen":
                        continue
                    expected_value = expected.get(key)
                    if not isinstance(expected_value, (int, float)) or isinstance(expected_value, bool):
                        errors.append(f"primary screen-space review {index}: expected {key} must be numeric")
                        continue
                    delta = abs(float(value) - float(expected_value))
                    limit = center_limit if key.startswith("center_") else bbox_limit
                    if delta > limit:
                        mismatch_reasons.append(f"{key} delta {delta:.2f} > {limit:.2f}")
            if mismatch_reasons:
                screen_mismatches.append({
                    "time_seconds": review.get("time_seconds"),
                    "source_id": review.get("source_id"),
                    "reasons": mismatch_reasons,
                })
    if screen_mismatches and "source_instance_screen_space_match" not in failed_checks:
        failed_checks.append("source_instance_screen_space_match")
    if contains_fill(qa.get("summary")):
        errors.append("summary is incomplete")
    deterministic_pass = qa.get("deterministic_preflight", {}).get("hard_preflight_pass") is True
    failed_structure = [name for name in failed_checks if name in STRUCTURE_CHECK_NAMES]
    failed_style = [name for name in failed_checks if name in STYLE_CHECK_NAMES]
    if errors:
        expected = "review_incomplete"
    elif not deterministic_pass or failed_structure:
        expected = "structure_failed"
    elif failed_style:
        expected = "style_failed"
    else:
        expected = "pass"
    if not errors and qa.get("verdict") != expected:
        errors.append(f"verdict must be {expected}")
    report = {
        "valid_review": not errors,
        "verdict": expected,
        "deterministic_pass": deterministic_pass,
        "failed_checks": failed_checks,
        "failed_structure_checks": failed_structure,
        "failed_style_checks": failed_style,
        "failed_source_instances": failed_instances,
        "failed_motion_entities": failed_motion_entities,
        "screen_space_mismatches": screen_mismatches,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        return 2
    return 0 if expected == "pass" else 3


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    command = commands.add_parser("preflight")
    command.add_argument("--source", required=True)
    command.add_argument("--manifest")
    command.add_argument("--workdir", required=True)
    command.add_argument("--min-seconds", type=float, default=4.0)
    command.add_argument("--max-seconds", type=float, default=15.0)
    command.add_argument("--scene-threshold", type=float, default=0.35)
    command.set_defaults(func=preflight)

    command = commands.add_parser("check-contract")
    command.add_argument("--contract", required=True)
    command.set_defaults(func=check_contract)

    command = commands.add_parser("build-prompt")
    command.add_argument("--contract", required=True)
    command.add_argument("--appearance", required=True)
    command.add_argument("--output", required=True)
    command.add_argument("--report")
    command.add_argument("--max-characters", type=int, default=DEFAULT_PROMPT_CHARACTER_BUDGET)
    command.set_defaults(func=build_prompt)

    command = commands.add_parser("prepare-qa")
    command.add_argument("--source", required=True)
    command.add_argument("--result", required=True)
    command.add_argument("--contract", required=True)
    command.add_argument("--appearance", required=True)
    command.add_argument("--workdir", required=True)
    command.add_argument("--scene-threshold", type=float, default=0.35)
    command.add_argument("--cut-tolerance-frames", type=int, default=2)
    command.add_argument("--aspect-tolerance", type=float, default=0.001)
    command.set_defaults(func=prepare_qa)

    command = commands.add_parser("finalize-qa")
    command.add_argument("--qa", required=True)
    command.set_defaults(func=finalize_qa)
    return root


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (WorkflowError, timeline.ContractError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
