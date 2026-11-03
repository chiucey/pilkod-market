#!/usr/bin/env python3
"""
SCENE Quadrant Chart Generator

Generates a prioritized matrix visualization showing the intersection of
industry pain points (X-axis, sorted by revenue impact) and decision-maker
focus areas (Y-axis), with priority scoring to identify the optimal
SCENE narrative anchor point.

Usage:
    python generate_quadrant_chart.py --pain-points "..." --focus-areas "..." --weights "..." --output chart.png

Arguments:
    --pain-points: JSON array of pain point objects [{"name": "...", "category_rank": 1-6}]
    --focus-areas: JSON array of focus area strings ["Sales", "Marketing", ...]
    --weights: JSON object mapping focus area to weight {"Sales": 3.0, ...}
    --output: Output file path (default: scene_quadrant.png)
"""

import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


def parse_args():
    parser = argparse.ArgumentParser(description="Generate SCENE Quadrant Chart")
    parser.add_argument("--pain-points", required=True, help="JSON array of pain points")
    parser.add_argument("--focus-areas", required=True, help="JSON array of focus areas")
    parser.add_argument("--weights", default="{}", help="JSON object of area weights")
    parser.add_argument("--output", default="scene_quadrant.png", help="Output file path")
    parser.add_argument("--title", default="SCENE Quadrant Analysis", help="Chart title")
    return parser.parse_args()


def calculate_scores(pain_points, focus_areas, weights):
    """Calculate priority score for each intersection cell."""
    scores = np.zeros((len(focus_areas), len(pain_points)))
    for i, area in enumerate(focus_areas):
        weight = weights.get(area, 1.0)
        for j, pp in enumerate(pain_points):
            category_rank = pp.get("category_rank", 3)
            scores[i, j] = (7 - category_rank) * weight
    return scores


def get_category_label(rank):
    labels = {
        1: "Direct Revenue Loss",
        2: "Growth Bottleneck",
        3: "Operational Efficiency",
        4: "Customer Experience",
        5: "Compliance & Risk",
        6: "Back-office Efficiency"
    }
    return labels.get(rank, "Other")


def get_priority_label(score):
    if score >= 12:
        return "Critical Focus"
    elif score >= 8:
        return "High Priority"
    elif score >= 4:
        return "Medium Priority"
    else:
        return "Low Priority"


def generate_chart(pain_points, focus_areas, weights, title, output_path):
    scores = calculate_scores(pain_points, focus_areas, weights)
    
    n_focus = len(focus_areas)
    n_pain = len(pain_points)
    
    # Color map: white -> yellow -> orange -> red
    colors = ["#FFFFFF", "#FFE4B5", "#FFB347", "#FF6B35", "#DC143C"]
    cmap = LinearSegmentedColormap.from_list("scene", colors, N=256)
    
    fig, ax = plt.subplots(figsize=(max(12, n_pain * 2.2), max(8, n_focus * 1.2)))
    
    # Normalize scores for color mapping
    vmin, vmax = 0, max(18, scores.max())
    im = ax.imshow(scores, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    
    # Set ticks
    pain_labels = [pp["name"] for pp in pain_points]
    ax.set_xticks(range(n_pain))
    ax.set_yticks(range(n_focus))
    ax.set_xticklabels(pain_labels, rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels(focus_areas, fontsize=10)
    
    # Add score annotations and priority indicators
    for i in range(n_focus):
        for j in range(n_pain):
            score = scores[i, j]
            priority = get_priority_label(score)
            
            # Text color based on cell darkness
            text_color = "white" if score >= 10 else "black"
            
            # Score value
            ax.text(j, i, f"{score:.0f}", ha="center", va="center",
                   fontsize=11, fontweight="bold", color=text_color)
            
            # Priority badge for critical/high cells
            if score >= 12:
                ax.add_patch(plt.Rectangle((j - 0.48, i - 0.48), 0.96, 0.96,
                                           fill=False, edgecolor="#DC143C", linewidth=3))
                ax.text(j, i + 0.25, "★", ha="center", va="center",
                       fontsize=14, color="#DC143C")
            elif score >= 8:
                ax.add_patch(plt.Rectangle((j - 0.48, i - 0.48), 0.96, 0.96,
                                           fill=False, edgecolor="#FF6B35", linewidth=2))
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Priority Score", fontsize=11)
    
    # Title and labels
    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
    ax.set_xlabel("Industry Pain Points (sorted by revenue impact →)", fontsize=11, labelpad=10)
    ax.set_ylabel("Decision-Maker Focus Areas", fontsize=11, labelpad=10)
    
    # Add legend for category ranks
    rank_patches = [
        mpatches.Patch(color="#FFB347", label="1-2: Revenue/Growth Critical"),
        mpatches.Patch(color="#FFE4B5", label="3-4: Operational/Experience"),
        mpatches.Patch(color="#F5F5F5", label="5-6: Compliance/Back-office"),
    ]
    ax.legend(handles=rank_patches, loc="upper left", bbox_to_anchor=(1.15, 1),
             fontsize=9, title="Revenue Impact", title_fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Chart saved to: {output_path}")
    
    # Return analysis results
    max_idx = np.unravel_index(np.argmax(scores), scores.shape)
    primary_anchor = {
        "focus_area": focus_areas[max_idx[0]],
        "pain_point": pain_points[max_idx[1]]["name"],
        "pain_point_rank": pain_points[max_idx[1]]["category_rank"],
        "score": float(scores[max_idx]),
        "position": (int(max_idx[0]), int(max_idx[1]))
    }
    
    critical_cells = []
    high_cells = []
    for i in range(n_focus):
        for j in range(n_pain):
            score = scores[i, j]
            cell = {
                "focus_area": focus_areas[i],
                "pain_point": pain_points[j]["name"],
                "score": float(score)
            }
            if score >= 12:
                critical_cells.append(cell)
            elif score >= 8:
                high_cells.append(cell)
    
    critical_cells.sort(key=lambda x: x["score"], reverse=True)
    high_cells.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "primary_anchor": primary_anchor,
        "critical_cells": critical_cells,
        "high_cells": high_cells,
        "all_scores": scores.tolist()
    }


def main():
    args = parse_args()
    
    pain_points = json.loads(args.pain_points)
    focus_areas = json.loads(args.focus_areas)
    weights = json.loads(args.weights)
    
    # Default all weights to 2.0 if not specified
    for area in focus_areas:
        if area not in weights:
            weights[area] = 2.0
    
    results = generate_chart(pain_points, focus_areas, weights, args.title, args.output)
    
    # Print JSON results for programmatic consumption
    print("\n---RESULTS---")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
