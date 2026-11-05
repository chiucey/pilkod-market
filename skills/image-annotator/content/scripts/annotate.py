#!/usr/bin/env python3
"""
annotate.py — 图片注释主脚本
支持两种情况：

情况1（图片 + PDF）：
  Agent 分析 PDF → 提取附图标记说明 → 与图片标记匹配 → 叠加标注

情况2（图片 + 文字）：
  从技术文字提取附图标记 → 与图片标记匹配 → 叠加标注

用法（Agent 内部调用）：
  # 情况2示例
  python3 annotate.py --image /path/to/img.jpg --text "离心管[100]..." --output /path/to/out.jpg

  # 情况1示例
  python3 annotate.py --image /path/to/img.jpg --pdf /path/to/doc.pdf --output /path/to/out.jpg
"""
import sys, os, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from extract_from_text import extract_from_text

OUTPUT_DIR = "/workspace/output"

# 标注样式
LABEL_COLOR = "#1E3A8A"   # 深蓝色
FONT_SIZE = 14             # 字号
OFFSET_X = 15              # 相对数字的X偏移（右侧）
OFFSET_Y = -8              # 相对数字的Y偏移（上方）

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_labels_from_text(text: str) -> dict:
    """从技术文字中提取附图标记对应关系"""
    return extract_from_text(text)

def match_and_overlay(image_path: str, output_path: str,
                      labels: dict, markers: list) -> str:
    """
    将附图标记与图片坐标匹配，并叠加到图片

    markers格式: [{"number": "100", "x": 300, "y": 100, "area": "顶部"}, ...]
    labels格式:  {"100": "离心管", "40": "管盖", ...}

    返回输出路径
    """
    ensure_output_dir()

    # 匹配坐标
    marker_map = {m["number"]: m for m in markers}
    matched = {}
    for num, name in labels.items():
        if num in marker_map:
            m = marker_map[num]
            matched[num] = {
                "name": name,
                "x": m.get("x", 0),
                "y": m.get("y", 0),
            }
        else:
            print(f"[WARN] 标记 {num}({name}) 在图片中未找到，跳过")

    print(f"[INFO] 成功匹配 {len(matched)}/{len(labels)} 个标注")

    if not matched:
        print("[ERROR] 没有可用的标注")
        return output_path

    # 调用 ImageMagick
    success = overlay_with_imagemagick(image_path, output_path, matched)
    if success:
        return output_path

    # 备选：AI 生成方式（通过 Agent 调用 image_synthesize）
    print("[INFO] ImageMagick 方案不可用，请使用 image_synthesize 工具")
    return output_path

def overlay_with_imagemagick(img_path: str, output_path: str,
                               matched: dict) -> bool:
    """
    使用 ImageMagick 叠加文字标注
    matched格式: {"100": {"name": "离心管", "x": 300, "y": 100}, ...}
    """
    import subprocess

    cmd = ["convert", img_path]
    for num, info in matched.items():
        text = f"{info['name']}({num})"
        ax = info["x"] + OFFSET_X
        ay = max(info["y"] + OFFSET_Y, FONT_SIZE)
        cmd += [
            "-fill", LABEL_COLOR,
            "-font", "DejaVu-Sans-Bold",
            "-pointsize", str(FONT_SIZE),
            "-gravity", "NorthWest",
            "-annotate", f"+{ax}+{ay}", text
        ]
    cmd.append(output_path)

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            sz = os.path.getsize(output_path)
            print(f"[OK] 标注完成: {output_path} ({sz//1024}KB)")
            return True
        print(f"[WARN] ImageMagick: {r.stderr[:200]}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def build_ai_synthesize_prompt(matched: dict) -> str:
    """生成 image_synthesize 工具的提示词"""
    label_list = []
    for num, info in sorted(matched.items(), key=lambda x: int(x[0])):
        label_list.append(
            f"- '{info['name']}({num})' 坐标: ({info['x']}, {info['y']})"
        )
    return f"""在这张工程示意图中，在以下精确坐标位置添加文字标注。

标注列表：
{chr(10).join(label_list)}

要求：
- 只添加上述标注，不修改任何原有图案、线条、数字
- 文字格式："部件名称(编号)"，如"10上管体"
- 字体颜色：深蓝色(#1E3A8A)
- 字体大小：与原图数字大小相近
- 无背景框，纯文字标注
- 标注位于数字右上方"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="图片注释 - 工程图纸附图标注")
    parser.add_argument("--image", required=True, help="工程图片路径")
    parser.add_argument("--pdf", help="PDF文件路径（情况1）")
    parser.add_argument("--text", help="技术文字内容（情况2）")
    parser.add_argument("--textfile", help="技术文字文件路径")
    parser.add_argument("--output", required=True, help="输出图片路径")
    parser.add_argument("--labels", help="标签JSON文件（覆盖自动提取）")
    parser.add_argument("--markers", help="标记坐标JSON文件")

    args = parser.parse_args()

    # 1. 提取附图标记名称
    if args.labels:
        with open(args.labels, "r", encoding="utf-8") as f:
            labels = json.load(f)
        print(f"[INFO] 从JSON文件加载 {len(labels)} 个标签")
    elif args.text:
        labels = extract_labels_from_text(args.text)
        print(f"[INFO] 从文字内容提取 {len(labels)} 个标签")
    elif args.textfile:
        with open(args.textfile, "r", encoding="utf-8") as f:
            labels = extract_labels_from_text(f.read())
        print(f"[INFO] 从文字文件提取 {len(labels)} 个标签")
    else:
        print("[ERROR] 必须提供 --text、--textfile、--labels 之一")
        sys.exit(1)

    # 打印标签
    for num, name in sorted(labels.items(), key=lambda x: int(x[0])):
        print(f"  {num} → {name}")

    # 2. 标记坐标（由 Agent 调用 images_understand 后提供）
    markers = []
    if args.markers:
        with open(args.markers, "r", encoding="utf-8") as f:
            markers = json.load(f)
        print(f"[INFO] 加载 {len(markers)} 个标记坐标")

    # 3. 执行标注
    result = match_and_overlay(args.image, args.output, labels, markers)
    print(f"[INFO] 输出: {result}")


if __name__ == "__main__":
    main()
