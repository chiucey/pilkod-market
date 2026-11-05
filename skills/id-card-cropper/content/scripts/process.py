#!/usr/bin/env python3
"""
id-card-cropper 处理脚本：从照片中提取身份证，做透视矫正，输出标准 1.586:1 比例图。

支持两种背景检测策略：
1. 简单背景（桌面/纯色）：用 HSV 亮度阈值 + 连通分量
2. 复杂背景（墙、纹理）：用 GrabCut 前景分离

输出：
- <input>_corrected.png  -- 矫正后的身份证（无白边）
- <input>_with_border.png -- 矫正后 + 5% 白色留白

用法：
  python3 process.py <input_image> [--border 0.05] [--width 1600] [--no-border]

依赖：opencv-python-headless, numpy
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


# 中国居民身份证标准宽高比 85.6mm × 54mm
ID_ASPECT = 85.6 / 54.0  # ≈ 1.5852


def detect_id_simple(img_small: np.ndarray) -> np.ndarray:
    """简单背景检测：桌面/纯色场景。

    用 HSV 亮度阈值找和图像边缘相连的"背景"区域，反向得到身份证 mask。
    适合：身份证几乎填满图像、背景是单一颜色的情况。
    """
    hsv = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
    _, _, V = cv2.split(hsv)

    # 桌面/背景：V > 180（高亮）
    bg_mask = (V > 180).astype(np.uint8) * 255

    kernel = np.ones((5, 5), np.uint8)
    bg_mask = cv2.morphologyEx(bg_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    bg_mask = cv2.morphologyEx(bg_mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # 只保留和图像边缘相连的最大背景区域
    num_labels, labels = cv2.connectedComponents(bg_mask)
    edge_labels = set()
    edge_labels.update(labels[0, :].tolist())
    edge_labels.update(labels[-1, :].tolist())
    edge_labels.update(labels[:, 0].tolist())
    edge_labels.update(labels[:, -1].tolist())

    connected = np.zeros_like(bg_mask)
    for lbl in edge_labels:
        if lbl == 0:
            continue
        connected[labels == lbl] = 255

    id_mask = (connected == 0).astype(np.uint8) * 255
    return id_mask


def detect_id_grabcut(img_small: np.ndarray) -> np.ndarray:
    """复杂背景检测：墙、纹理、磨花场景。

    用 GrabCut 算法分离身份证前景和复杂背景。
    需要大致包含身份证的初始矩形框（这里自动按中心区域估算）。
    """
    h, w = img_small.shape[:2]

    # 自动估算身份证位置：中心 80% × 80% 的区域（尽量包含整个身份证，
    # 即使包含一些背景也比框太小好——太大的框 GrabCut 也能处理）
    margin_x = int(w * 0.1)
    margin_y_top = int(h * 0.1)
    margin_y_bot = int(h * 0.1)
    rect = (margin_x, margin_y_top, w - 2 * margin_x, h - margin_y_top - margin_y_bot)

    mask = np.zeros(img_small.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(img_small, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    id_mask = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    return id_mask


def detect_id_by_edges(img_small: np.ndarray) -> np.ndarray:
    """边缘检测 + 颜色聚类找身份证：适合"身份证几乎填满图、背景是浅色"的场景。

    策略：用 HSV V 阈值找"亮背景"，反向得到身份证 mask。
    适用：桌面是中性灰（V > 180），身份证背景色 V < 175。
    """
    hsv = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
    _, _, V = cv2.split(hsv)

    # 背景：V > 180（高亮的中性灰）
    bg_mask = (V > 180).astype(np.uint8) * 255

    kernel = np.ones((5, 5), np.uint8)
    bg_mask = cv2.morphologyEx(bg_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    bg_mask = cv2.morphologyEx(bg_mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # 只保留和图像边缘相连的最大背景
    num_labels, labels = cv2.connectedComponents(bg_mask)
    edge_labels = set()
    edge_labels.update(labels[0, :].tolist())
    edge_labels.update(labels[-1, :].tolist())
    edge_labels.update(labels[:, 0].tolist())
    edge_labels.update(labels[:, -1].tolist())

    connected = np.zeros_like(bg_mask)
    for lbl in edge_labels:
        if lbl == 0:
            continue
        connected[labels == lbl] = 255

    id_mask = (connected == 0).astype(np.uint8) * 255
    return id_mask


def find_corners(id_mask: np.ndarray) -> np.ndarray:
    """从身份证 mask 中找 4 个角点（TL, TR, BR, BL 顺序）。

    策略：
    1. 找最大轮廓
    2. 凸包 → 多边形近似到 4 顶点（如果能收紧到 4 且形状合理）
    3. 否则用 minAreaRect 兜底（给出 mask 包围的旋转矩形）

    为什么优先 minAreaRect：
    - 多边形近似在 mask 噪声大时会给出错误的"角点"（指向噪声边缘）
    - minAreaRect 给的是 mask 的最小包围矩形，更稳定
    - 即使身份证有透视变形，minAreaRect 也能正确捕捉（它支持旋转矩形）
    """
    contours, _ = cv2.findContours(id_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("No contours found in ID mask")

    largest = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(largest)
    peri = cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, 0.05 * peri, True)

    if len(approx) == 4:
        # 检查 4 顶点是否构成"接近矩形"（边长差异不能太大）
        # 如果 4 顶点形成的"四边形"边长差异 > 5x，fallback 到 minAreaRect
        pts = approx.reshape(4, 2).astype(np.float32)
        dists = []
        for i in range(4):
            d = np.linalg.norm(pts[i] - pts[(i + 1) % 4])
            dists.append(d)
        ratio = max(dists) / min(dists) if min(dists) > 0 else 999
        if ratio < 5:
            corners = pts
        else:
            rect = cv2.minAreaRect(largest)
            corners = cv2.boxPoints(rect).astype(np.float32)
    else:
        rect = cv2.minAreaRect(largest)
        corners = cv2.boxPoints(rect).astype(np.float32)

    # 排序为 TL, TR, BR, BL
    s = corners.sum(axis=1)
    diff = np.diff(corners, axis=1).flatten()
    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = corners[np.argmin(s)]
    ordered[2] = corners[np.argmax(s)]
    ordered[1] = corners[np.argmin(diff)]
    ordered[3] = corners[np.argmax(diff)]
    return ordered


def warp_card(img: np.ndarray, corners: np.ndarray,
              target_w: int = 1600,
              border_ratio: float = 0.0) -> np.ndarray:
    """透视变换矫正身份证到标准比例。

    corners: 4x2 数组，身份证的 4 个角点（TL, TR, BR, BL）
    target_w: 输出身份证宽度（高度按 1.586:1 自动算）
    border_ratio: 留白比例（每边），0 表示无留白
    """
    card_h = int(target_w / ID_ASPECT)

    if border_ratio > 0:
        # 留白模式：身份证放在目标图中央，外面加白边
        margin_w = int(target_w * border_ratio)
        margin_h = int(card_h * border_ratio)
        target_w_final = target_w + 2 * margin_w
        target_h_final = card_h + 2 * margin_h

        card_dst = np.array([
            [margin_w, margin_h],
            [margin_w + target_w - 1, margin_h],
            [margin_w + target_w - 1, margin_h + card_h - 1],
            [margin_w, margin_h + card_h - 1],
        ], dtype=np.float32)

        warped = cv2.warpPerspective(
            img, cv2.getPerspectiveTransform(corners, card_dst),
            (target_w_final, target_h_final)
        )
        return cv2.copyMakeBorder(
            warped[:card_h, :target_w] if False else warped,
            0, 0, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)
        )
    else:
        dst = np.array([
            [0, 0],
            [target_w - 1, 0],
            [target_w - 1, card_h - 1],
            [0, card_h - 1],
        ], dtype=np.float32)

        return cv2.warpPerspective(
            img, cv2.getPerspectiveTransform(corners, dst),
            (target_w, card_h)
        )


def process(input_path: str, output_dir: str | None = None,
            target_w: int = 1600, border_ratio: float = 0.05,
            save_no_border: bool = True, strategy: str = "auto") -> dict:
    """主流程：检测 → 矫正 → 输出。

    strategy 选项：
    - "auto": 自动判断（先 GrabCut，如果 mask 比例 < 0.25 用 V>180 兜底）
    - "grabcut": 强制用 GrabCut
    - "edges": 强制用 V>180 边缘检测（适合浅色背景+身份证占满图）
    - "fullimage": 假设身份证填满图，直接用图像边界

    返回包含输出文件路径的字典。
    """
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {input_path}")

    h, w = img.shape[:2]

    # 缩小到 ~1500 宽做处理（原图处理太慢）
    proc_w = 1500
    scale = proc_w / w
    img_s = cv2.resize(img, (proc_w, int(h * scale)))
    img_area = img_s.shape[0] * img_s.shape[1]

    if strategy == "fullimage":
        # 假设身份证填满图，直接用图像四边向内缩 5px 作为角点
        m = 5
        corners_small = np.array([
            [m, m], [proc_w - m, m], [proc_w - m, img_s.shape[0] - m], [m, img_s.shape[0] - m]
        ], dtype=np.float32)
    elif strategy == "edges":
        id_mask = detect_id_by_edges(img_s)
        corners_small = find_corners(id_mask)
    elif strategy == "grabcut":
        id_mask = detect_id_grabcut(img_s)
        corners_small = find_corners(id_mask)
    else:  # auto
        # 先跑 GrabCut，看最大连通区域占图比例
        id_mask_grabcut = detect_id_grabcut(img_s)
        num, labels = cv2.connectedComponents(id_mask_grabcut)
        grabcut_ratio = 0
        if num > 1:
            sizes = [(labels == i).sum() for i in range(1, num)]
            grabcut_ratio = max(sizes) / img_area if sizes else 0
        print(f'  GrabCut ratio: {grabcut_ratio:.3f}')

        if grabcut_ratio < 0.35:
            # 身份证在图中央（占图 < 35%），GrabCut 应该能用
            id_mask = id_mask_grabcut
        else:
            # 身份证占图较大（> 35%），可能几乎填满图，GrabCut 容易漏掉边缘
            # 用 V>180 边缘检测（minAreaRect 兜底更稳定）
            print('  Falling back to V>180 edge detection')
            id_mask = detect_id_by_edges(img_s)
        corners_small = find_corners(id_mask)

    # 映射回原图
    corners = corners_small / scale

    if output_dir is None:
        output_dir = str(Path(input_path).parent)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    stem = Path(input_path).stem
    results = {}

    if save_no_border:
        out_no_border = str(Path(output_dir) / f"{stem}_corrected.png")
        img_no_border = warp_card(img, corners, target_w=target_w, border_ratio=0)
        cv2.imwrite(out_no_border, img_no_border)
        results["corrected"] = out_no_border

    if border_ratio > 0:
        out_bordered = str(Path(output_dir) / f"{stem}_with_border.png")
        img_bordered = warp_card(img, corners, target_w=target_w, border_ratio=border_ratio)
        cv2.imwrite(out_bordered, img_bordered)
        results["with_border"] = out_bordered

    return results


def main():
    parser = argparse.ArgumentParser(
        description="从照片中提取身份证，透视矫正，输出标准比例图"
    )
    parser.add_argument("input", help="输入图片路径")
    parser.add_argument("--output-dir", "-o", help="输出目录（默认与输入同目录）")
    parser.add_argument("--width", "-w", type=int, default=1600, help="输出身份证宽度（默认 1600）")
    parser.add_argument("--border", "-b", type=float, default=0.05, help="白边比例（每边，默认 0.05 = 5%%）")
    parser.add_argument("--no-border", action="store_true", help="不输出白边版本")
    parser.add_argument(
        "--strategy", "-s",
        choices=["auto", "grabcut", "edges", "fullimage"],
        default="auto",
        help="检测策略：auto(默认) / grabcut / edges(V>180 边缘) / fullimage(身份证填满图)",
    )
    args = parser.parse_args()

    results = process(
        args.input,
        output_dir=args.output_dir,
        target_w=args.width,
        border_ratio=args.border,
        save_no_border=not args.no_border,
        strategy=args.strategy,
    )

    print("处理完成，输出文件：")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
