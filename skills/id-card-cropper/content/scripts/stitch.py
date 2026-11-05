#!/usr/bin/env python3
"""
id-card-cropper 拼接脚本：把身份证人像面 + 国徽面上下拼成一张图。

输出文件名：61-<身份证号>.png（中国身份证号的"61"前缀是常见的命名约定）。

流程：
1. 对每张图做"旋转 90° CCW + GrabCut + 透视变换"（和人像面一致）
2. 矫正后按 1.586:1 标准比例（width 1600, height ~1009）
3. 加白边（按比例加，保持 1.586 比例）
4. 上下 vstack 拼接

用法：
  python3 stitch.py --portrait portrait.jpg --guohui guohui.jpg
  python3 stitch.py --portrait portrait.jpg --guohui guohui.jpg --output custom.png
  python3 stitch.py --portrait portrait.jpg --guohui guohui.jpg --id 532927199612271924

依赖：opencv-python-headless, numpy（沙箱已预装）
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

# 复用 process.py 的角点检测
sys.path.insert(0, str(Path(__file__).parent))
from process import detect_id_grabcut, find_corners  # noqa: E402

ID_ASPECT = 85.6 / 54.0  # 1.586


def crop_and_correct(image_path: str, target_w: int = 1600) -> np.ndarray:
    """加载身份证图 → 旋转 90° CCW → GrabCut 4 角 → 透视变换 → 加比例白边。

    输出尺寸：target_w × (target_w / 1.586)，整体 1.586 比例。
    """
    img_orig = cv2.imread(image_path)
    if img_orig is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    # 横排放置的身份证需要先旋转 90° CCW（让文字朝上）
    img = cv2.rotate(img_orig, cv2.ROTATE_90_COUNTERCLOCKWISE)
    h, w = img.shape[:2]

    # 缩小到 1500 宽做 GrabCut（原图太大太慢）
    proc_w = 1500
    scale = proc_w / w
    img_s = cv2.resize(img, (proc_w, int(h * scale)))

    # GrabCut（大初始框：5%-95%）
    mask = np.zeros(img_s.shape[:2], np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    rect = (int(proc_w * 0.05), int(h * scale * 0.05),
            int(proc_w * 0.9), int(h * scale * 0.9))
    cv2.grabCut(img_s, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
    id_mask = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)

    # 形态学清理
    kernel = np.ones((5, 5), np.uint8)
    id_mask = cv2.morphologyEx(id_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    id_mask = cv2.morphologyEx(id_mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # 4 角点
    corners_small = find_corners(id_mask)
    corners_orig = corners_small / scale

    # 透视变换到标准比例
    target_h = int(target_w / ID_ASPECT)
    src = corners_orig.astype(np.float32)
    dst = np.array([
        [0, 0],
        [target_w - 1, 0],
        [target_w - 1, target_h - 1],
        [0, target_h - 1],
    ], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (target_w, target_h))

    # 加白边（按比例加，保持 1.586 整体比例）
    total_w = target_w + 160  # 左右各 80
    total_h = int(total_w / ID_ASPECT)
    margin_w = (total_w - target_w) // 2
    margin_h = (total_h - target_h) // 2
    bordered = cv2.copyMakeBorder(
        warped, margin_h, margin_h, margin_w, margin_w,
        cv2.BORDER_CONSTANT, value=(255, 255, 255),
    )
    return bordered


def stitch(portrait_path: str, guohui_path: str, output_path: str,
          id_number: str | None = None, target_w: int = 1600) -> str:
    """拼接人像面 + 国徽面，返回输出路径。

    如果提供 id_number，文件名用 `61-<id_number>.png`；否则用 `stitched.png`。
    """
    portrait = crop_and_correct(portrait_path, target_w=target_w)
    guohui = crop_and_correct(guohui_path, target_w=target_w)
    print(f'Portrait: {portrait.shape}')
    print(f'Guohui:   {guohui.shape}')

    # 上下 vstack
    combined = np.vstack([portrait, guohui])
    print(f'Combined: {combined.shape} (ratio h/w = {combined.shape[0]/combined.shape[1]:.3f})')

    cv2.imwrite(output_path, combined)
    print(f'Saved: {output_path}')
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="把身份证人像面 + 国徽面上下拼成一张图"
    )
    parser.add_argument("--portrait", required=True, help="人像面图片路径")
    parser.add_argument("--guohui", required=True, help="国徽面图片路径")
    parser.add_argument("--output", "-o", help="输出路径（默认 61-<id>.png 或 stitched.png）")
    parser.add_argument("--id", help="身份证号（用于命名输出文件：61-<id>.png）")
    parser.add_argument("--width", "-w", type=int, default=1600, help="单张身份证宽度（默认 1600）")
    args = parser.parse_args()

    # 默认输出路径
    if args.output:
        output_path = args.output
    elif args.id:
        output_path = f"61-{args.id}.png"
    else:
        output_path = "stitched.png"

    stitch(args.portrait, args.guohui, output_path,
          id_number=args.id, target_w=args.width)


if __name__ == "__main__":
    main()
