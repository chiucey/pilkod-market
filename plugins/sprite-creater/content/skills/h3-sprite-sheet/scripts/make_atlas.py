#!/usr/bin/env python3
"""H3 sprite pipeline: video clips -> keyed frames -> sampled poses -> atlas.

    python3 make_atlas.py --out DIR idle=idle.mp4 punch=punch.mp4 \
        --loop idle --oneshot punch --frames-per-move 12 \
        --background-mode transparent --cell-size 256 \
        --asset-kind character --pivot bottom-center --facing right

Outputs: frames/*.png, atlas.png, atlas.json, manifest.json, preview.html
(playable state-machine player), report.json (per-move QC metrics — read it
before trusting the result), <move>.gif previews.

Arc-length sampling, seamless-loop search, metrics report and clamp-style
despill adapted from gary149/h3-game-sprites (MIT, (c) 2026 Victor Mustar).
Key color is auto-estimated per frame from border pixels (tolerates H3
background drift and works with any flat key color).
"""

import argparse
import base64
import io
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def extract_frames(clip: Path, tmp: Path) -> list:
    out = tmp / clip.stem
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i",
                    str(clip), str(out / "f_%05d.png")], check=True)
    frames = sorted(out.glob("f_*.png"))
    if not frames:
        raise SystemExit(f"no frames extracted from {clip}")
    return frames


def key_frame(img: Image.Image, near=60.0, far=120.0):
    """Soft chroma key against border-estimated key color. Returns RGBA + purity."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    band = max(2, min(a.shape[0], a.shape[1]) // 50)
    edges = np.concatenate([a[:band].reshape(-1, 3), a[-band:].reshape(-1, 3),
                            a[:, :band].reshape(-1, 3), a[:, -band:].reshape(-1, 3)])
    key = np.median(edges, axis=0)
    d = np.sqrt(((a - key) ** 2).sum(-1))
    alpha = (np.clip((d - near) / (far - near), 0, 1) * 255)
    # despill: clamp key-dominant channels against the off channel in soft
    # edges only — clamping (not blending) avoids tinting the character
    dom = [i for i in range(3) if key[i] > key.min() + 60]
    if 0 < len(dom) < 3:
        soft = (alpha > 0) & (alpha < 255)
        off = a[..., [i for i in range(3) if i not in dom]].max(-1)
        cap = off * 1.18 + 30
        for i in dom:
            a[..., i] = np.where(soft, np.minimum(a[..., i], cap), a[..., i])
    purity = float(((d <= near) | (d >= far)).mean())
    rgba = np.dstack([a.clip(0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(rgba), purity, key


def erode_alpha(img: Image.Image, px: int) -> Image.Image:
    a = img.getchannel("A")
    for _ in range(px):
        a = a.filter(ImageFilter.MinFilter(3))
    img.putalpha(a)
    return img


def frame_stats(img: Image.Image):
    """baseline (feet row), ankle-centroid x (bottom 22% — a tail/arm swing
    moves the bbox center but not the ankles), height. None if empty."""
    al = np.asarray(img)[..., 3] > 0
    ys, xs = np.nonzero(al)
    if len(xs) == 0:
        return None
    thresh = ys.max() - int((ys.max() - ys.min()) * 0.22)
    leg = ys >= thresh
    return {"baseline": int(ys.max()), "top": int(ys.min()),
            "cx": float(xs[leg].mean() if leg.any() else xs.mean()),
            "height": int(ys.max() - ys.min())}


def parse_cell_size(value: str):
    """Parse 256 or 256x320 into a bounded engine cell size."""
    text = value.lower().strip()
    parts = text.split("x")
    if len(parts) == 1 and parts[0].isdigit():
        width = height = int(parts[0])
    elif len(parts) == 2 and all(p.isdigit() for p in parts):
        width, height = map(int, parts)
    else:
        raise argparse.ArgumentTypeError("cell size must be N or WIDTHxHEIGHT")
    if not (16 <= width <= 2048 and 16 <= height <= 2048):
        raise argparse.ArgumentTypeError("cell dimensions must be between 16 and 2048 px")
    return width, height


def validate_action_name(name: str):
    """Portable IDs keep frame paths and engine imports predictable."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
        return (f"invalid action id {name!r}: use an ASCII slug beginning with "
                "a letter (for example idle, walk_right, attack-1)")
    return None


def bleed_transparent_rgb(img: Image.Image, px: int):
    """Dilate visible RGB into transparent edge pixels without changing alpha.

    Chroma-key RGB left under alpha=0 leaks green/magenta when an engine filters
    the atlas. A small RGB-only extrusion gives the sampler a matching edge
    colour while preserving straight alpha.
    """
    rgba = np.asarray(img.convert("RGBA")).copy()
    original_alpha = rgba[..., 3].copy()
    known = original_alpha > 0
    rgb = rgba[..., :3].astype(np.float32)
    rgb[~known] = 0
    for _ in range(max(0, px)):
        sums = np.zeros_like(rgb)
        counts = np.zeros(known.shape, dtype=np.float32)
        for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                       (0, 1), (1, -1), (1, 0), (1, 1)):
            src_y = slice(max(0, -dy), known.shape[0] - max(0, dy))
            src_x = slice(max(0, -dx), known.shape[1] - max(0, dx))
            dst_y = slice(max(0, dy), known.shape[0] - max(0, -dy))
            dst_x = slice(max(0, dx), known.shape[1] - max(0, -dx))
            mask = known[src_y, src_x]
            sums[dst_y, dst_x] += rgb[src_y, src_x] * mask[..., None]
            counts[dst_y, dst_x] += mask
        frontier = (~known) & (counts > 0)
        if not frontier.any():
            break
        rgb[frontier] = sums[frontier] / counts[frontier][:, None]
        known |= frontier
    rgb[~known] = 0
    rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    rgba[..., 3] = original_alpha
    return Image.fromarray(rgba)


def small_arrays(imgs):
    """Small premultiplied RGBA arrays used by all temporal comparisons.

    Keyed pixels retain their original RGB even when alpha is zero. Comparing
    straight RGBA therefore lets the flat key background dominate the score
    and can make unrelated poses look deceptively similar. Premultiplication
    removes invisible RGB while keeping alpha/edge changes measurable.
    """
    out = []
    for im in imgs:
        a = np.asarray(im.resize((max(1, im.width // 8),
                                  max(1, im.height // 8)))).astype(np.float32)
        alpha = a[..., 3:4] / 255.0
        a[..., :3] *= alpha
        out.append(a.astype(np.int16))
    return out


def frame_distance(a, b):
    return float(np.abs(a - b).mean())


def motion_curve(small):
    return [0.0] + [float(np.abs(small[i] - small[i - 1]).mean())
                    for i in range(1, len(small))]


def pick_arclength(energy, n):
    """Equal steps of cumulative motion — frames land on pose extremes without
    over-sampling holds (uniform looks mushy, minima-picking over-samples idle)."""
    cum = np.cumsum(energy)
    if cum[-1] <= 0:
        picks = sorted(set(np.linspace(0, len(energy) - 1, n)
                           .round().astype(int).tolist()))
        return ensure_exact_count(picks, 0, len(energy), n)
    targets = np.linspace(0, cum[-1], n)
    picks = sorted({int(np.argmin(np.abs(cum - t))) for t in targets}
                   | {0, len(energy) - 1})
    return ensure_exact_count(picks, 0, len(energy), n)


def pick_uniform(total, n):
    return sorted({round(i * (total - 1) / (max(1, n - 1))) for i in range(n)})


def ensure_exact_count(picks, start, end, n):
    """Fill the largest temporal gaps so a requested frame budget stays exact."""
    out = sorted({p for p in picks if start <= p < end})
    candidates = [p for p in range(start, end) if p not in out]
    while len(out) < n and candidates:
        if not out:
            choice = candidates[len(candidates) // 2]
        else:
            choice = max(candidates,
                         key=lambda p: min(abs(p - chosen) for chosen in out))
        out.append(choice)
        out.sort()
        candidates.remove(choice)
    if len(out) > n:
        keep = pick_uniform(len(out), n)
        out = [out[i] for i in keep]
    return out


def pick_motion_spaced(small, start, end, n):
    """Chronological equal-motion sampling inside [start,end).

    Fixed-FPS playback looks jerky when time-uniform picks alternate between a
    held pose and a fast pose change. Equal cumulative visual motion keeps the
    order forward while making adjacent exported frames more even.
    """
    segment = small[start:end]
    if len(segment) <= n:
        return list(range(start, end))
    cumulative = np.cumsum(motion_curve(segment))
    if cumulative[-1] <= 0:
        return ensure_exact_count(pick_uniform(end - start, n), 0,
                                  end - start, n)
    targets = np.linspace(0, cumulative[-1], n, endpoint=False)
    local = [int(np.argmin(np.abs(cumulative - target))) for target in targets]
    local = ensure_exact_count(local, 0, end - start, n)
    return [start + p for p in local]


def micro_event_frames(small, picks, k, grid=6, ratio_gate=6.0):
    """Blink/twitch capture. Global-motion sampling (arclength/uniform) never
    lands on 2-4 frame events confined to a tiny region: their contribution to
    mean motion is ~zero. Signature instead = one block's diff spiking while
    the global mean stays low; add the top-k such frames to the selection."""
    cands = []
    for i in range(1, len(small)):
        d = np.abs(small[i] - small[i - 1]).astype(np.float32)
        if d.ndim == 3:
            d = d.mean(axis=2)
        h, w = d.shape
        bh, bw = max(1, h // grid), max(1, w // grid)
        local = max(float(d[y:y + bh, x:x + bw].mean())
                    for y in range(0, h, bh) for x in range(0, w, bw))
        g = float(d.mean())
        cands.append((local / (g + 1e-6), local, i))
    cands.sort(reverse=True)
    out = []
    for ratio, _local, i in cands:
        if ratio < ratio_gate or len(out) >= k:
            break
        if all(abs(i - p) > 3 for p in list(picks) + out):
            out.append(i)
    return out


def inject_event_frames(picks, events, target_n):
    """Replace nearby interior picks so an explicit frame budget stays exact.

    Endpoints are preserved for one-shot clips. Loop clips never call this:
    inserting an unrelated blink/twitch into a base loop breaks its phase.
    """
    out = sorted(set(picks))
    for event in events:
        if event in out or len(out) < 3:
            continue
        interior = out[1:-1]
        victim = min(interior, key=lambda p: abs(p - event))
        out.remove(victim)
        out.append(event)
        out.sort()
    return out[:target_n]


def pick_loop(small, n, lo=0.03, hi=0.97, min_gap=12, max_gap=None,
              context=2):
    """Find one chronological cycle and sample it in forward time.

    A single-pose comparison is insufficient for gait: opposite gait phases
    can look alike, yet have opposite incoming/outgoing motion. Compare a
    small temporal window around both endpoints so pose *and phase direction*
    must agree. The end frame is a boundary marker and is intentionally not
    emitted, avoiding a duplicated first/last hold.
    """
    total = len(small)
    min_gap = max(min_gap, n)
    max_gap = max_gap or min(total - context * 2 - 1, round(total * 0.75))
    start = max(context, int(total * lo))
    stop = min(total - context, int(total * hi))
    idxs = range(start, stop)
    energy = motion_curve(small)
    cumulative_motion = np.cumsum(energy)
    total_motion = float(cumulative_motion[-1]) if len(cumulative_motion) else 0.0
    candidates = []
    for i in idxs:
        for j in idxs:
            if min_gap <= j - i <= max_gap:
                window = [frame_distance(small[i + off], small[j + off])
                          for off in range(-context, context + 1)]
                score = float(np.mean(window))
                pose_diff = window[context]
                segment_motion = float(cumulative_motion[j] - cumulative_motion[i])
                coverage = segment_motion / max(total_motion, 1e-6)
                candidates.append((score, pose_diff, i, j, coverage,
                                   "internal-repeat"))
    # FL2VA intentionally pins the first and final source frames to the same
    # reference. A slow idle/blink may contain exactly one cycle across the
    # whole clip and no valid short repeat inside it. Always consider the full
    # source boundary; j is the duplicate boundary marker and stays excluded.
    if total - 1 >= min_gap:
        i, j = 0, total - 1
        pose_diff = frame_distance(small[i], small[j])
        segment_motion = float(cumulative_motion[j] - cumulative_motion[i])
        coverage = segment_motion / max(total_motion, 1e-6)
        candidates.append((pose_diff, pose_diff, i, j, coverage,
                           "source-boundary"))
    if not candidates:
        return None, pick_uniform(total, n)
    # H3 clips may contain a slow 2-4 second idle cycle but a much shorter gait
    # cycle. Search the useful clip instead of assuming a 45-frame ceiling.
    # Among endpoint windows close to the global best, choose the shortest gap:
    # this selects the fundamental cycle rather than two or three repetitions.
    # A static hold has a beautiful seam but is not an animation cycle. Require
    # the candidate to cover a meaningful part of the clip's actual motion.
    # This rejects 10-20 frame pauses inside idle videos while still allowing
    # the fundamental cycle when a clip contains several walk repetitions.
    meaningful = [c for c in candidates if c[4] >= 0.08]
    pool = meaningful or candidates
    global_best = min(c[0] for c in pool)
    close = [c for c in pool if c[0] <= global_best * 1.5 + 0.25]
    evaluated = []
    verdict_rank = {"PASS": 0, "WARN": 1, "FAIL": 2}
    for candidate in close:
        score, pose_diff, i, j, coverage, boundary_source = candidate
        candidate_picks = pick_motion_spaced(small, i, j, n)
        quality = playback_quality(small, candidate_picks, True,
                                   expected_n=n)
        evaluated.append((verdict_rank[quality["verdict"]], j - i, score,
                          candidate, candidate_picks))
    _rank, _gap, _score, best, picks = min(evaluated,
                                            key=lambda item: item[:3])
    score, pose_diff, i, j, coverage, boundary_source = best
    return ({"i": i, "j": j, "diff": round(pose_diff, 3),
             "phase_window_diff": round(score, 3),
             "cycle_frames": j - i,
             "motion_coverage": round(coverage, 3),
             "sampling": "motion-spaced",
             "boundary_source": boundary_source}, picks)


def loop_quality(small, picks, loop_info):
    """Measure the seam that the exported player will actually show."""
    if not loop_info or len(picks) < 2:
        return None
    internal = [frame_distance(small[a], small[b])
                for a, b in zip(picks, picks[1:])]
    seam = frame_distance(small[picks[-1]], small[picks[0]])
    median_step = float(np.median(internal)) if internal else 0.0
    ratio = seam / max(median_step, 1e-6)
    outside = [p for p in picks
               if not (loop_info["i"] <= p < loop_info["j"])]
    verdict = "PASS" if not outside and ratio <= 1.75 else "WARN"
    return {
        "verdict": verdict,
        "chronological": picks == sorted(picks),
        "selected_outside_cycle": outside,
        "boundary_diff": loop_info["diff"],
        "selected_seam_diff": round(seam, 3),
        "median_internal_step_diff": round(median_step, 3),
        "seam_ratio": round(ratio, 3),
    }


def playback_quality(small, picks, is_loop, expected_n=None, min_frames=0):
    """Second gate over the exact exported order, not the source clip.

    It catches the common 'hold, teleport, hold, teleport' failure that can
    pass source-video and seam checks. Semantic gait/action correctness remains
    an M3 review responsibility; this gate covers deterministic timing defects.
    """
    budget_issues = []
    if expected_n is not None and len(picks) != expected_n:
        budget_issues.append(f"frame budget mismatch: wanted {expected_n}, got {len(picks)}")
    if len(picks) < min_frames:
        budget_issues.append(f"insufficient frame density: need at least {min_frames}, got {len(picks)}")
    if len(picks) < 2:
        return {"verdict": "FAIL", "issues": budget_issues + ["fewer than 2 frames"],
                "frame_count": len(picks), "expected_frames": expected_n,
                "minimum_frames": min_frames}
    steps = [frame_distance(small[a], small[b])
             for a, b in zip(picks, picks[1:])]
    median = float(np.median(steps))
    mean = float(np.mean(steps))
    cv = float(np.std(steps) / max(mean, 1e-6))
    duplicate_gate = max(0.15, median * 0.30)
    jump_gate = max(0.75, median * 2.0)
    duplicate_steps = [i for i, d in enumerate(steps) if d < duplicate_gate]
    jump_steps = [i for i, d in enumerate(steps) if d > jump_gate]
    seam = frame_distance(small[picks[-1]], small[picks[0]]) if is_loop else None
    seam_ratio = seam / max(median, 1e-6) if seam is not None else None
    issues = list(budget_issues)
    fail = bool(budget_issues)
    if len(picks) != len(set(picks)):
        issues.append("duplicate source frame indices")
        fail = True
    if duplicate_steps:
        issues.append(f"near-freeze transitions at {duplicate_steps}")
    if jump_steps:
        issues.append(f"jump transitions at {jump_steps}")
    if cv > 0.60:
        issues.append(f"uneven transition rhythm (cv={cv:.2f})")
    if is_loop and seam_ratio is not None and seam_ratio > 1.75:
        issues.append(f"loop seam spike (ratio={seam_ratio:.2f})")
        fail = True
    tolerated = max(1, len(steps) // 8)
    if is_loop and (len(duplicate_steps) > tolerated
                    or len(jump_steps) > tolerated or cv > 0.80):
        fail = True
    if not is_loop and (len(duplicate_steps) > len(steps) * 0.4
                        or len(jump_steps) > len(steps) * 0.3 or cv > 1.10):
        fail = True
    verdict = "FAIL" if fail else "WARN" if issues else "PASS"
    return {
        "verdict": verdict,
        "issues": issues,
        "frame_count": len(picks),
        "expected_frames": expected_n,
        "minimum_frames": min_frames,
        "step_diffs": [round(d, 3) for d in steps],
        "median_step_diff": round(median, 3),
        "transition_cv": round(cv, 3),
        "near_freeze_steps": duplicate_steps,
        "jump_steps": jump_steps,
        "seam_diff": round(seam, 3) if seam is not None else None,
        "seam_ratio": round(seam_ratio, 3) if seam_ratio is not None else None,
    }


def spatial_quality(cells, pad):
    """Gate the actual exported cells, after crop/scale/anchor composition."""
    boxes = [cell.getchannel("A").getbbox() for cell in cells]
    empty = [i for i, box in enumerate(boxes) if box is None]
    touching = []
    for i, box in enumerate(boxes):
        if box is None:
            continue
        if (box[0] < pad or box[1] < pad
                or box[2] > cells[i].width - pad
                or box[3] > cells[i].height - pad):
            touching.append(i)
    stats = [s for s in (frame_stats(cell) for cell in cells) if s]
    baseline_drift = (max(s["baseline"] for s in stats)
                      - min(s["baseline"] for s in stats)) if stats else None
    centroid_drift = (max(s["cx"] for s in stats)
                      - min(s["cx"] for s in stats)) if stats else None
    issues = []
    if empty:
        issues.append(f"empty exported cells: {empty}")
    if touching:
        issues.append(f"sprite enters reserved padding at cells: {touching}")
    fail = bool(empty or touching)
    verdict = "FAIL" if fail else "PASS"
    return {
        "verdict": verdict,
        "issues": issues,
        "empty_cells": empty,
        "padding_intrusions": touching,
        "baseline_drift_px": baseline_drift,
        "centroid_drift_px": round(centroid_drift, 1)
        if centroid_drift is not None else None,
    }


def move_is_loop(name, loops, oneshot):
    """When --loop is supplied it is the authoritative loop allow-list."""
    return name in loops if loops else name not in oneshot


def validate_playback_modes(move_names, loops, oneshot):
    """Every move must have exactly one explicit runtime playback type."""
    names = set(move_names)
    overlap = sorted(loops & oneshot)
    unknown = sorted((loops | oneshot) - names)
    missing = sorted(names - (loops | oneshot))
    issues = []
    if overlap:
        issues.append(f"moves listed as both loop and oneshot: {overlap}")
    if unknown:
        issues.append(f"playback lists unknown moves: {unknown}")
    if missing:
        issues.append(f"moves missing playback type: {missing}")
    return issues


def validate_hold_modes(holds, oneshot):
    invalid = sorted(holds - oneshot)
    return ([f"hold actions must also be oneshot: {invalid}"] if invalid else [])


def background_mode_to_no_key(background_mode):
    return background_mode == "keep"


def profile_min_frames(quality_profile):
    return {"game-keyframes": 2, "smooth": 8, "video": 16}[quality_profile]


def pixelate_all(frames, target_h, colors):
    """Shared palette across ALL frames — per-frame quantization flickers."""
    small = [f.resize((max(1, round(f.width * target_h / f.height)), target_h),
                      Image.LANCZOS) for f in frames]
    montage = Image.new("RGB", (sum(i.width for i in small), target_h))
    x = 0
    for i in small:
        montage.paste(i.convert("RGB"), (x, 0))
        x += i.width
    pal = montage.quantize(colors=colors)
    out = []
    for f in small:
        alpha = f.getchannel("A").point(lambda v: 255 if v > 127 else 0)
        q = f.convert("RGB").quantize(palette=pal).convert("RGBA")
        q.putalpha(alpha)
        out.append(q)
    return out


def check_clips(moves, out_dir: Path, ref_path=None,
                background_mode="transparent"):
    """Pre-packing gate: validate raw clips BEFORE any sampling/packing so a
    bad generation is caught while regeneration is still the cheap answer.
    Checks: key drift (bg changed color mid-clip), bg purity, subject
    presence, subject touching frame edge, first-frame match vs 定妆图."""
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="h3check_"))
    ref_small = None
    if ref_path:
        ref_small = np.asarray(Image.open(ref_path).convert("RGB")
                               .resize((64, 64))).astype(np.float32)
    results = {}
    try:
        for name, spec in moves.items():
            clip, _n = spec if isinstance(spec, tuple) else (spec, None)
            paths = extract_frames(clip, tmp)
            keys, purities, edge, missing = [], [], 0, 0
            first_match = None
            for i, p in enumerate(paths):
                img = Image.open(p)
                if i == 0 and ref_small is not None:
                    cur = np.asarray(img.convert("RGB").resize((64, 64))).astype(np.float32)
                    first_match = float(np.abs(cur - ref_small).mean())
                if background_mode == "keep":
                    continue
                keyed, pu, kc = key_frame(img)
                keys.append(kc)
                purities.append(pu)
                al = np.asarray(keyed)[..., 3] > 0
                if al.mean() < 0.005:
                    missing += 1
                    continue
                ys, xs = np.nonzero(al)
                if (ys.min() <= 1 or xs.min() <= 1
                        or ys.max() >= al.shape[0] - 2 or xs.max() >= al.shape[1] - 2):
                    edge += 1
            n = len(paths)
            ref_key = (np.median(np.stack(keys[:max(3, n // 10)]), axis=0)
                       if keys else None)
            drift = ([float(np.linalg.norm(k - ref_key)) for k in keys]
                     if ref_key is not None else [])
            bad = sum(1 for d in drift if d > 90.0)
            onset = next((i for i, d in enumerate(drift) if d > 90.0), None)
            issues = []
            if background_mode == "transparent" and bad > n // 3:
                issues.append(f"FAIL bg-drift: background changed color on {bad}/{n} frames (from #{onset})")
            elif background_mode == "transparent" and bad:
                issues.append(f"WARN bg-drift: {bad}/{n} frames drifted (from #{onset}); clean segment still usable")
            if background_mode == "transparent" and missing > n // 10:
                issues.append(f"FAIL subject-missing: no subject on {missing}/{n} frames")
            if first_match is not None and first_match > 60:
                issues.append(f"FAIL first-frame: differs from reference (diff {first_match:.0f}/255)")
            if background_mode == "transparent" and edge > n // 5:
                issues.append(f"WARN edge: subject touches frame edge on {edge}/{n} frames (may walk out / get cropped)")
            if purities and min(purities) < 0.90:
                issues.append(f"WARN purity: worst bg purity {min(purities):.2f} (<0.90, keying may be rough)")
            verdict = ("REGENERATE" if any(x.startswith("FAIL") for x in issues)
                       else "WARN" if issues else "PASS")
            results[name] = {"verdict": verdict, "issues": issues, "frames": n,
                             "background_mode": background_mode,
                             "key_ref": ([round(v) for v in ref_key.tolist()]
                                         if ref_key is not None else None),
                             "drift_frames": bad, "drift_onset": onset,
                             "missing_frames": missing, "edge_frames": edge,
                             "worst_purity": (round(min(purities), 4)
                                              if purities else None),
                             "first_frame_diff": round(first_match, 1) if first_match is not None else None}
            print(f"[{name}] {verdict}" + ("".join("\n  - " + x for x in issues) or " — all checks clean"),
                  flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    (out_dir / "check.json").write_text(json.dumps(results, indent=2))
    print(f"check.json -> {out_dir/'check.json'}")
    return results


def build(moves, out_dir: Path, frames_per_move, fps_suggest, pad, edge_erode,
          sampling, no_key, align, oneshot, loops, holds, pixelate, colors,
          micro_events=0, quality_profile="smooth",
          background_mode="transparent", cell_size=(256, 256),
          max_texture=4096, extrude=2, pivot_mode="bottom-center",
          asset_kind="character", facing="right"):
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="h3sprite_"))
    selected, selected_source_indices, report = {}, {}, {}
    try:
        for name, spec in moves.items():
            clip, n_move = spec if isinstance(spec, tuple) else (spec, None)
            n_move = n_move or frames_per_move
            paths = extract_frames(clip, tmp)
            print(f"[{name}] {len(paths)} frames extracted", flush=True)
            purities, keys, drift_info = [], [], None
            source_indices = list(range(len(paths)))
            if no_key:
                imgs = [Image.open(p).convert("RGBA") for p in paths]
            else:
                imgs = []
                for p in paths:
                    im, pu, kc = key_frame(Image.open(p))
                    if edge_erode > 0:
                        im = erode_alpha(im, edge_erode)
                    imgs.append(im)
                    purities.append(pu)
                    keys.append(kc)
                # Key-drift gate. Adaptive keying tolerates wobble, but when
                # H3 drifts the background to a NEW color (e.g. magenta ->
                # yellow ~ hair) it would silently key out matching parts of
                # the character. Reference = median key of the first 10%;
                # frames beyond DRIFT_TOL are corrupted — sample around them.
                ref = np.median(np.stack(keys[:max(3, len(keys) // 10)]), axis=0)
                drift = [float(np.linalg.norm(k - ref)) for k in keys]
                DRIFT_TOL = 90.0
                bad = [i for i, dv in enumerate(drift) if dv > DRIFT_TOL]
                if bad:
                    drift_info = {"ref_key": [round(v) for v in ref.tolist()],
                                  "bad_frames": len(bad), "total": len(imgs),
                                  "onset": bad[0],
                                  "regen_recommended": len(bad) > len(imgs) // 3}
                    good = [i for i in range(len(imgs)) if i not in set(bad)]
                    print(f"[{name}] WARNING: background drifted to a different "
                          f"color on {len(bad)}/{len(imgs)} frames (from #{bad[0]}) "
                          f"— sampling clean frames only"
                          + ("; REGENERATION RECOMMENDED"
                             if drift_info["regen_recommended"] else ""), flush=True)
                    imgs = [imgs[i] for i in good]
                    purities = [purities[i] for i in good]
                    source_indices = [source_indices[i] for i in good]
            small = small_arrays(imgs)
            loop_info = None
            is_loop = move_is_loop(name, loops, oneshot)
            if is_loop:
                loop_info, picks = pick_loop(small, n_move)
            elif sampling == "uniform":
                picks = pick_uniform(len(imgs), n_move)
            else:
                picks = pick_arclength(motion_curve(small), n_move)
            picks = picks[:n_move]
            kept_events = []
            if micro_events > 0:
                if is_loop:
                    print(f"[{name}] micro-events skipped: base loops must remain "
                          "inside one chronological cycle; export blink/twitch "
                          "as a separate one-shot move", flush=True)
                else:
                    extra = micro_event_frames(small, picks, micro_events)
                    if extra:
                        picks = inject_event_frames(picks, extra, n_move)
                        kept_events = [p for p in extra if p in picks]
                        print(f"[{name}] micro-events replaced nearby picks: "
                              f"{kept_events}", flush=True)
            frames = [imgs[i] for i in picks]
            if pixelate > 0:
                frames = pixelate_all(frames, pixelate, colors)
            selected[name] = frames
            selected_source_indices[name] = [source_indices[i] for i in picks]
            stats = [s for s in (frame_stats(f) for f in frames) if s]
            loop_qc = loop_quality(small, picks, loop_info)
            playback_qc = playback_quality(
                small, picks, is_loop, expected_n=n_move,
                min_frames=profile_min_frames(quality_profile))
            report[name] = {
                "source_frames": len(paths), "picked": picks,
                "picked_source_frames": selected_source_indices[name],
                "loop": loop_info,
                "playback": "forward-loop" if is_loop else "once",
                "micro_events": kept_events,
                "baseline_drift_px": (max(s["baseline"] for s in stats)
                                      - min(s["baseline"] for s in stats))
                                     if stats else None,
                "centroid_drift_px": (round(max(s["cx"] for s in stats)
                                            - min(s["cx"] for s in stats), 1)
                                      if stats else None),
                "height_var_px": (max(s["height"] for s in stats)
                                  - min(s["height"] for s in stats))
                                 if stats else None,
                "loop_qc": loop_qc,
                "playback_qc": playback_qc,
                "worst_bg_purity": round(min(purities), 4) if purities else None,
                "key_drift": drift_info,
            }
            print(f"[{name}] picked {picks}"
                  + (f" loop seam {loop_info}; seam QC {loop_qc}" if loop_info else "")
                  + f"; playback QC {playback_qc}",
                  flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # fixed alignment uses one union canvas across every action. This keeps
    # scale and screen position stable when switching idle -> walk -> attack;
    # per-action auto-crops subtly re-center the character and cause a jump.
    all_frames = [frame for frames in selected.values() for frame in frames]
    source_sizes = {(frame.width, frame.height) for frame in all_frames}
    if len(source_sizes) > 1 and align == "fixed":
        raise SystemExit("SOURCE_CANVAS_MISMATCH: fixed alignment requires all "
                         "action videos to share one canvas/aspect ratio")
    all_boxes = [box for box in
                 (frame.getchannel("A").getbbox() for frame in all_frames) if box]
    if not all_boxes:
        raise SystemExit("EMPTY_SPRITE: no visible subject remains after background processing")
    global_union = (min(b[0] for b in all_boxes), min(b[1] for b in all_boxes),
                    max(b[2] for b in all_boxes), max(b[3] for b in all_boxes))
    cropped = {}
    for name, frames in selected.items():
        if align == "fixed":
            cropped[name] = [frame.crop(global_union) for frame in frames]
        else:
            cropped[name] = [frame.crop(frame.getchannel("A").getbbox())
                             for frame in frames]

    cw, ch = cell_size
    usable_w, usable_h = cw - pad * 2, ch - pad * 2
    if usable_w <= 0 or usable_h <= 0:
        raise SystemExit("CELL_PADDING_INVALID: padding leaves no drawable area")
    max_crop_w = max(c.width for frames in cropped.values() for c in frames)
    max_crop_h = max(c.height for frames in cropped.values() for c in frames)
    fixed_stats = [s for s in
                   (frame_stats(frame) for frames in cropped.values()
                    for frame in frames) if s]
    if pivot_mode == "center":
        fixed_anchor_x = (global_union[2] - global_union[0] - 1) / 2
        fixed_anchor_y = (global_union[3] - global_union[1] - 1) / 2
        pivot_x, pivot_y = cw // 2, ch // 2
    else:
        fixed_anchor_x = float(np.median([s["cx"] for s in fixed_stats]))
        fixed_anchor_y = max(s["baseline"] for s in fixed_stats)
        pivot_x, pivot_y = cw // 2, ch - pad - 1
    # Reserve two extra pixels for resampling support. Fit around the declared
    # anchor, not around bbox centre: a character's foot anchor is often
    # asymmetric because of a weapon, hair, or tail.
    safe_pad = pad + 2
    scale = min((cw - safe_pad * 2) / max_crop_w,
                (ch - safe_pad * 2) / max_crop_h)
    if align == "fixed":
        constraints = []
        extents = (
            (fixed_anchor_x, pivot_x - safe_pad),
            (max_crop_w - 1 - fixed_anchor_x, cw - 1 - safe_pad - pivot_x),
            (fixed_anchor_y, pivot_y - safe_pad),
            (max_crop_h - 1 - fixed_anchor_y, ch - 1 - safe_pad - pivot_y),
        )
        for source_extent, target_extent in extents:
            if source_extent > 0:
                constraints.append(target_extent / source_extent)
        if constraints:
            scale = min(scale, *constraints)
    if scale <= 0:
        raise SystemExit("CELL_SCALE_INVALID: requested pivot/padding cannot fit "
                         "the sprite; use a larger cell or a different pivot")
    resample = Image.Resampling.NEAREST if pixelate > 0 else Image.Resampling.LANCZOS
    cells_by_move, placement_by_move = {}, {}
    for name, frames in cropped.items():
        cells, placements = [], []
        for crop in frames:
            rw = max(1, round(crop.width * scale))
            rh = max(1, round(crop.height * scale))
            rendered = crop.resize((rw, rh), resample)
            if align == "fixed":
                anchor_x = fixed_anchor_x * scale
                anchor_y = fixed_anchor_y * scale
            elif pivot_mode == "bottom-center":
                st = frame_stats(crop)
                anchor_x = (st["cx"] if st else crop.width / 2) * scale
                anchor_y = (st["baseline"] if st else crop.height - 1) * scale
            else:
                anchor_x = (crop.width - 1) / 2 * scale
                anchor_y = (crop.height - 1) / 2 * scale
            x = round(pivot_x - anchor_x)
            y = round(pivot_y - anchor_y)
            cell = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            cell.alpha_composite(rendered, (x, y))
            if not no_key:
                cell = bleed_transparent_rgb(cell, extrude)
            box = cell.getchannel("A").getbbox()
            cells.append(cell)
            placements.append({"x": x, "y": y, "w": rw, "h": rh,
                               "alpha_bbox": list(box) if box else None})
        cells_by_move[name] = cells
        placement_by_move[name] = placements
        report[name]["spatial_qc"] = spatial_quality(cells, pad)
        report[name]["output_scale"] = round(scale, 6)

    total_frames = sum(len(frames) for frames in cells_by_move.values())
    max_cols = max_texture // cw
    max_rows = max_texture // ch
    if max_cols < 1 or max_rows < 1:
        raise SystemExit(f"ATLAS_CELL_TOO_LARGE: cell {cw}x{ch} exceeds "
                         f"texture limit {max_texture}px")
    preferred_cols = max(len(frames) for frames in cells_by_move.values())
    cols = min(preferred_cols, max_cols)
    rows = math.ceil(total_frames / cols)
    if rows > max_rows:
        capacity = max_cols * max_rows
        raise SystemExit(f"ATLAS_TOO_LARGE: {total_frames} cells exceed one "
                         f"{max_texture}px atlas capacity ({capacity}) at "
                         f"{cw}x{ch}; reduce frames/cell size or split the character")
    atlas = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    duration_ms = round(1000 / max(1, fps_suggest))
    pivot_norm = {"x": round(pivot_x / cw, 6),
                  "y": round(pivot_y / ch, 6),
                  "origin": "top-left"}
    meta = {"meta": {"schema_version": 2, "image": "atlas.png",
                     "cell_w": cw, "cell_h": ch,
                     "fps_suggest": fps_suggest,
                     "duration_ms": duration_ms,
                     "pivot": pivot_norm,
                     "pivot_mode": pivot_mode,
                     "asset_kind": asset_kind, "facing": facing,
                     "color_space": "sRGB", "alpha_mode": "straight",
                     "extrude_px": extrude, "max_texture_px": max_texture},
            "moves": {}}
    frames_root = out_dir / "frames"
    frames_root.mkdir(parents=True, exist_ok=True)
    atlas_index = 0
    for name, frames in cells_by_move.items():
        entries = []
        action_dir = frames_root / name
        action_dir.mkdir(parents=True, exist_ok=True)
        for local_index, cell in enumerate(frames):
            col, row = atlas_index % cols, atlas_index // cols
            x, y = col * cw, row * ch
            atlas.alpha_composite(cell, (x, y))
            frame_file = f"frames/{name}/{name}_{local_index:03d}.png"
            cell.save(out_dir / frame_file)
            box = placement_by_move[name][local_index]["alpha_bbox"]
            entries.append({
                "index": local_index,
                "image": "atlas.png",
                "x": x, "y": y, "w": cw, "h": ch,
                "duration_ms": duration_ms,
                "source_frame": selected_source_indices[name][local_index],
                "frame_file": frame_file,
                "rotated": False, "trimmed": False,
                "source_size": {"w": cw, "h": ch},
                "sprite_source_size": ({"x": box[0], "y": box[1],
                                        "w": box[2] - box[0],
                                        "h": box[3] - box[1]}
                                       if box else None),
                "pivot": pivot_norm,
            })
            atlas_index += 1
        is_loop = move_is_loop(name, loops, oneshot)
        move_qcs = [report[name]["playback_qc"]["verdict"],
                    report[name]["spatial_qc"]["verdict"]]
        move_qc = "FAIL" if "FAIL" in move_qcs else "WARN" if "WARN" in move_qcs else "PASS"
        meta["moves"][name] = {"frames": entries,
                               "loop": is_loop,
                               "playback": "forward" if is_loop else "once",
                               "end_behavior": ("loop" if is_loop else
                                                "hold" if name in holds else
                                                "return-home"),
                               "fps": fps_suggest,
                               "events": [], "qc": move_qc}
        # per-move GIF preview (chat-friendly) uses final engine cells.
        gif = []
        for cell in frames:
            bg = Image.new("RGB", cell.size, (24, 26, 32))
            bg.paste(cell, (0, 0), cell)
            bg.thumbnail((420, 560))
            gif.append(bg)
        if gif:
            gif[0].save(out_dir / f"{name}.gif", save_all=True,
                        append_images=gif[1:], duration=duration_ms, loop=0)

    atlas.save(out_dir / "atlas.png")
    kb = (out_dir / "atlas.png").stat().st_size / 1024
    # user-facing spec card: what sprite/sequence consumers actually check
    meta["meta"]["spec"] = {
        "atlas_px": [atlas.width, atlas.height],
        "cell_px": [cw, ch],
        "grid": [cols, rows],
        "file_kb": round(kb, 1),
        "decoded_mb": round(atlas.width * atlas.height * 4 / 1048576, 1),
        "total_frames": total_frames,
        "fps_suggest": fps_suggest,
        "quality_profile": quality_profile,
        "background_mode": background_mode,
        "transparent": not no_key,
        "color_space": "sRGB",
        "alpha_mode": "straight",
        "pivot": pivot_norm,
        "pivot_mode": pivot_mode,
        "asset_kind": asset_kind,
        "facing": facing,
        "padding_px": pad,
        "extrude_px": extrude,
        "max_texture_px": max_texture,
        "moves": {n: {"frames": len(v["frames"]),
                      "type": "loop" if v["loop"] else "oneshot",
                      "end_behavior": v["end_behavior"]}
                  for n, v in meta["moves"].items()},
    }
    verdicts = [q for r in report.values() for q in
                (r["playback_qc"]["verdict"], r["spatial_qc"]["verdict"])]
    meta["meta"]["qc"] = ("FAIL" if "FAIL" in verdicts else
                           "WARN" if "WARN" in verdicts else "PASS")
    (out_dir / "atlas.json").write_text(json.dumps(meta, indent=2) + "\n")
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    manifest = {
        "schema_version": 1,
        "asset_type": "sprite-sequence",
        "atlas": "atlas.png",
        "metadata": "atlas.json",
        "preview": "preview.html",
        "frames_root": "frames",
        "background_mode": background_mode,
        "color_space": "sRGB",
        "alpha_mode": "straight",
        "cell_size": [cw, ch],
        "pivot": pivot_norm,
        "pivot_mode": pivot_mode,
        "asset_kind": asset_kind,
        "facing": facing,
        "actions": {name: {"frames": len(move["frames"]),
                           "playback": move["playback"],
                           "end_behavior": move["end_behavior"],
                           "fps": move["fps"]}
                    for name, move in meta["moves"].items()},
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_preview(out_dir, atlas, meta)
    mv = " · ".join(f"{n} {v['frames']}帧{'循环' if v['type']=='loop' else '单次'}"
                    for n, v in meta["meta"]["spec"]["moves"].items())
    print("─── 规格 ───")
    print(f"atlas   {atlas.width}x{atlas.height}px · {kb:,.0f}KB 文件 · "
          f"解码后约 {meta['meta']['spec']['decoded_mb']}MB 显存")
    print(f"网格    {cols} 列 x {rows} 行 · 单帧 cell {cw}x{ch}px · "
          f"上限 {max_texture}px")
    print(f"动作    {mv}（共 {total_frames} 帧）")
    print(f"播放    建议 {fps_suggest} FPS · 背景{'透明' if not no_key else '保留'}")
    print(f"锚点    {pivot_mode} ({pivot_x},{pivot_y}) · straight alpha/sRGB · "
          f"padding {pad}px · RGB extrude {extrude}px")
    print(f"二次质检 {meta['meta']['qc']}")
    print(json.dumps(report, indent=1))
    return meta["meta"]["qc"] != "FAIL"


def write_preview(out_dir, atlas, meta):
    buf = io.BytesIO()
    atlas.save(buf, format="PNG")
    tpl = (Path(__file__).parent / "preview_template.html").read_text()
    html = (tpl.replace("__ATLAS_B64__", base64.b64encode(buf.getvalue()).decode())
               .replace("__META_JSON__", json.dumps(meta)))
    (out_dir / "preview.html").write_text(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+", help="move=path.mp4 pairs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames-per-move", type=int, default=8)
    ap.add_argument("--fps-suggest", type=int, default=10)
    ap.add_argument("--quality-profile",
                    choices=["game-keyframes", "smooth", "video"],
                    default="smooth",
                    help="game-keyframes accepts deliberate low-frame style; "
                         "smooth requires >=8 frames; video requires >=16")
    ap.add_argument("--cell-size", required=True, type=parse_cell_size,
                    help="required engine cell: N or WIDTHxHEIGHT, e.g. 256")
    ap.add_argument("--asset-kind", required=True,
                    choices=["character", "object", "vfx", "ui", "scene"],
                    help="controls the declared sequence-asset contract")
    ap.add_argument("--pivot", required=True,
                    choices=["bottom-center", "center"],
                    help="character ground anchor or object/VFX centre anchor")
    ap.add_argument("--facing", required=True,
                    choices=["left", "right", "front", "back", "none"],
                    help="declared visual facing; use none for non-directional assets")
    ap.add_argument("--max-texture-size", type=int, default=4096,
                    help="single-atlas GPU/import limit; default 4096")
    ap.add_argument("--pad", type=int, default=4)
    ap.add_argument("--extrude", type=int, default=2,
                    help="RGB-only edge bleed under transparent alpha")
    ap.add_argument("--edge-erode", type=int, default=1)
    ap.add_argument("--sampling", choices=["arclength", "uniform"], default="arclength",
                    help="arclength=motion-weighted pose extremes; uniform=smooth sequence")
    ap.add_argument("--background-mode", choices=["transparent", "keep"],
                    help="required user choice: transparent=key/remove a flat "
                         "background; keep=preserve the source background")
    ap.add_argument("--align", choices=["fixed", "feet"], default="fixed",
                    help="fixed=union rect per move; feet=per-frame ankle anchor")
    ap.add_argument("--oneshot", default="",
                    help="moves that play once then return to first loop move")
    ap.add_argument("--loop", default="",
                    help="moves to run the seamless-cycle finder on (walk,run,idle)")
    ap.add_argument("--hold", default="",
                    help="oneshot moves that hold their last frame instead of returning home")
    ap.add_argument("--micro-events", type=int, default=0,
                    help="opt-in tiny localized events for one-shot clips; "
                         "replaces nearby picks and keeps the frame budget "
                         "exact. Ignored for loops: export blink/twitch as a "
                         "separate one-shot move")
    ap.add_argument("--pixelate", type=int, default=0,
                    help="pixel-art mode: target frame height px (shared palette)")
    ap.add_argument("--colors", type=int, default=16)
    ap.add_argument("--check-only", action="store_true",
                    help="pre-packing gate: validate raw clips (drift/purity/"
                         "presence/edge/first-frame vs --ref) and exit")
    ap.add_argument("--ref", default=None,
                    help="定妆图 path for first-frame consistency check")
    ap.add_argument("--allow-qc-fail", action="store_true",
                    help="write failed diagnostic artifacts without returning "
                         "a non-zero status; never use for final delivery")
    a = ap.parse_args()
    if not 1 <= a.fps_suggest <= 60:
        sys.exit("FPS_INVALID: --fps-suggest must be between 1 and 60")
    if not 2 <= a.frames_per_move <= 64:
        sys.exit("FRAME_COUNT_INVALID: --frames-per-move must be between 2 and 64")
    if a.pad < 0 or a.extrude < 0 or a.extrude > a.pad:
        sys.exit("PADDING_INVALID: require pad >= extrude >= 0")
    if a.pad * 2 >= min(a.cell_size):
        sys.exit("PADDING_INVALID: padding consumes the requested cell")
    if a.pivot == "center" and a.align == "feet":
        sys.exit("ALIGNMENT_INVALID: feet alignment requires bottom-center pivot")
    if (a.max_texture_size < 512 or a.max_texture_size > 16384
            or a.max_texture_size & (a.max_texture_size - 1)):
        sys.exit("TEXTURE_LIMIT_INVALID: use a power of two from 512 to 16384")
    if not a.background_mode:
        sys.exit("BACKGROUND_MODE_REQUIRED: ask the user to choose transparent or keep")
    moves = {}
    for spec in a.clips:
        if "=" not in spec:
            sys.exit(f"bad clip spec (want move=path.mp4): {spec}")
        k, v = spec.split("=", 1)
        name_issue = validate_action_name(k)
        if name_issue:
            sys.exit("ACTION_ID_INVALID: " + name_issue)
        if k in moves:
            sys.exit(f"ACTION_ID_DUPLICATE: action {k!r} was supplied more than once")
        n_override = None
        if ":" in v:
            head, tail = v.rsplit(":", 1)
            if tail.isdigit():          # name=path.mp4:6  → 6 frames for this move
                v, n_override = head, int(tail)
                if not 2 <= n_override <= 64:
                    sys.exit(f"FRAME_COUNT_INVALID: {k} requests {n_override}; use 2..64")
        moves[k] = (Path(v), n_override)
        if not moves[k][0].exists():
            sys.exit(f"clip not found: {v}")
    if a.check_only:
        check_clips(moves, Path(a.out), a.ref, a.background_mode)
        return
    oneshot = {s.strip() for s in a.oneshot.split(",") if s.strip()}
    loops = {s.strip() for s in a.loop.split(",") if s.strip()}
    holds = {s.strip() for s in a.hold.split(",") if s.strip()}
    mode_issues = (validate_playback_modes(moves, loops, oneshot)
                   + validate_hold_modes(holds, oneshot))
    if mode_issues:
        sys.exit("PLAYBACK_MODE_REQUIRED: " + "; ".join(mode_issues))
    ok = build(moves, Path(a.out), a.frames_per_move, a.fps_suggest, a.pad,
               a.edge_erode, a.sampling,
               background_mode_to_no_key(a.background_mode), a.align,
               oneshot, loops, holds, a.pixelate, a.colors, a.micro_events,
               a.quality_profile, a.background_mode, a.cell_size,
               a.max_texture_size, a.extrude, a.pivot, a.asset_kind, a.facing)
    if not ok and not a.allow_qc_fail:
        sys.exit("OUTPUT_QC_FAIL: inspect report.json/playback_qc; do not deliver")


if __name__ == "__main__":
    main()
