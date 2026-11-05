#!/usr/bin/env python3
"""
overlay_labels.py — 将附图标记名称叠加到工程图片

使用 ImageMagick convert 命令将文字标注叠加到图片
标注样式：深蓝色(#1E3A8A)文字，无背景框，位于数字标记右上方

用法：
  python3 overlay_labels.py <原图.jpg> <输出.jpg> <标注JSON>
  标注JSON格式：{"100": {"name": "离心管", "x": 361, "y": 111}, ...}

备选方案（无中文字体时）：
  使用 image_synthesize 工具生成标注图
"""
import sys, json, subprocess, os

# 标注样式常量
LABEL_COLOR = "#1E3A8A"   # 深蓝色
FONT_SIZE = 14             # 字号
OFFSET_X = 15             # 文字相对数字的X偏移（右侧）
OFFSET_Y = -8             # 文字相对数字的Y偏移（上方）
IMGW = 1178                # 默认图片宽度
IMGH = 1078                # 默认图片高度

def overlay_with_imagemagick(img_path: str, output_path: str,
                               labels: dict, img_w: int = None,
                               img_h: int = None) -> bool:
    """
    使用 ImageMagick 将文字标注叠加到图片
    labels格式: {"100": {"name": "离心管", "x": 361, "y": 111}, ...}
    """
    w = img_w or IMGW
    h = img_h or IMGH

    # 构建 ImageMagick 命令
    # 使用 -gravity NorthWest -annotate +x+y 实现文字定位
    cmd = ["convert", img_path]

    for num, info in labels.items():
        name = info.get("name", "")
        x = info.get("x", 0)
        y = info.get("y", 0)

        if not name:
            continue

        text = f"{name}({num})"
        # 标注位置：数字右上方
        ax = x + OFFSET_X
        ay = max(y + OFFSET_Y, FONT_SIZE)  # 确保在图片范围内

        cmd += [
            "-fill", LABEL_COLOR,
            "-font", "DejaVu-Sans-Bold",
            "-pointsize", str(FONT_SIZE),
            "-gravity", "NorthWest",
            "-annotate", f"+{ax}+{ay}", text
        ]

    cmd.append(output_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            sz = os.path.getsize(output_path)
            print(f"[OK] 标注完成: {output_path} ({sz//1024}KB)")
            return True
        else:
            print(f"[WARN] ImageMagick 失败: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] 执行异常: {e}")
        return False

def generate_label_description(labels: dict, img_path: str) -> str:
    """
    生成标注描述，供 image_synthesize 工具使用
    返回用于 AI 生成的精确提示词
    """
    label_list = []
    for num, info in sorted(labels.items(), key=lambda x: int(x[0])):
        name = info.get("name", "")
        x = info.get("x", 0)
        y = info.get("y", 0)
        label_list.append(f"- '{name}({num})' → 位置: ({x}, {y})")

    return f"""请在这张工程示意图中，在以下精确坐标位置添加文字标注（深蓝色#1E3A8A，无背景框，字体与原图协调）：

标注列表：
{chr(10).join(label_list)}

要求：
- 只添加上述标注，不修改任何原有图案、线条、数字
- 标注文字内容为"部件名称(编号)"，如"10上管体"
- 字体颜色为深蓝色(#1E3A8A)
- 标注位于对应数字的右上方"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 overlay_labels.py <原图.jpg> <输出.jpg> <标注JSON或文件>")
        sys.exit(1)

    img_in = sys.argv[1]
    img_out = sys.argv[2]

    # 解析标注数据
    if sys.argv[3].endswith(".json"):
        with open(sys.argv[3], "r", encoding="utf-8") as f:
            labels = json.load(f)
    else:
        labels = json.loads(sys.argv[3])

    print(f"加载了 {len(labels)} 个标注")
    success = overlay_with_imagemagick(img_in, img_out, labels)

    if not success:
        print("\n[INFO] ImageMagick 方案失败，请使用 image_synthesize 工具生成标注图")
        prompt = generate_label_description(labels, img_in)
        print("\n=== image_synthesize 提示词 ===")
        print(prompt)
        print("\n=== 用法 ===")
        print(f"input_files: [{img_in}]")
        print(f"prompt: 见上方提示词")
        print(f"output_file: {img_out}")
