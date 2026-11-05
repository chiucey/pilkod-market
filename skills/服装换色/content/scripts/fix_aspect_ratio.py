#!/usr/bin/env python3
"""
fix_aspect_ratio.py - Crop + resize generated image to exactly match original image dimensions.

Usage:
    python3 fix_aspect_ratio.py <original_path> <generated_path>

Steps:
  1. Center-crop generated image to match original aspect ratio
  2. Resize to exactly match original pixel dimensions (LANCZOS)

Output is saved in-place to generated_path.
"""

import sys
from PIL import Image

def fix_aspect_ratio(original_path, generated_path):
    orig = Image.open(original_path)
    gen = Image.open(generated_path)

    orig_w, orig_h = orig.size
    gen_w, gen_h = gen.size
    orig_ratio = orig_w / orig_h
    gen_ratio = gen_w / gen_h

    print(f"原图尺寸: {orig_w}x{orig_h} (比例 {orig_ratio:.3f})")
    print(f"生成图尺寸: {gen_w}x{gen_h} (比例 {gen_ratio:.3f})")

    # Step 1: Center-crop to match aspect ratio
    if abs(orig_ratio - gen_ratio) > 0.02:
        if gen_ratio > orig_ratio:
            # Too wide → crop width
            new_w = int(gen_h * orig_ratio)
            left = (gen_w - new_w) // 2
            gen = gen.crop((left, 0, left + new_w, gen_h))
            print(f"Step1 裁剪宽度: {gen_w} → {new_w} (居中裁剪)")
        else:
            # Too tall → crop height
            new_h = int(gen_w / orig_ratio)
            top = (gen_h - new_h) // 2
            gen = gen.crop((0, top, gen_w, top + new_h))
            print(f"Step1 裁剪高度: {gen_h} → {new_h} (居中裁剪)")
    else:
        print("Step1 比例一致，无需裁剪")

    # Step 2: Resize to exactly match original pixel dimensions
    if gen.size != (orig_w, orig_h):
        gen = gen.resize((orig_w, orig_h), Image.LANCZOS)
        print(f"Step2 缩放至原图精确尺寸: {orig_w}x{orig_h}")
    else:
        print("Step2 尺寸已一致，无需缩放")

    gen.save(generated_path)
    print(f"✅ 已保存: {generated_path} → {gen.size[0]}x{gen.size[1]} (与原图完全一致)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: fix_aspect_ratio.py <original_path> <generated_path>")
        sys.exit(1)
    fix_aspect_ratio(sys.argv[1], sys.argv[2])
