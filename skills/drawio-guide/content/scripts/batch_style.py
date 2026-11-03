#!/usr/bin/env python3
"""
draw.io 批量样式应用工具
用于快速将预设样式应用到多个图形

使用方法:
    python batch_style.py <style_name>
    
支持的样式:
    行政蓝 - 政府公文风格
    流程绿 - 流程执行中
    判断橙 - 条件判断节点
    结束红 - 开始/结束节点
    学术蓝 - 学术论文风格
"""

import sys
import xml.etree.ElementTree as ET

# 预设样式库
STYLES = {
    "行政蓝": {
        "fillColor": "#4472C4",
        "fontColor": "#FFFFFF",
        "strokeColor": "#2F5597",
        "fontSize": "12",
        "fontStyle": "1",  # 加粗
    },
    "流程绿": {
        "fillColor": "#70AD47",
        "fontColor": "#FFFFFF",
        "strokeColor": "#538135",
        "fontSize": "12",
    },
    "判断橙": {
        "fillColor": "#ED7D31",
        "fontColor": "#FFFFFF",
        "strokeColor": "#C55A11",
        "fontSize": "12",
    },
    "结束红": {
        "fillColor": "#C00000",
        "fontColor": "#FFFFFF",
        "strokeColor": "#8B0000",
        "fontSize": "12",
        "shape": "ellipse",  # 圆角矩形
    },
    "学术蓝": {
        "fillColor": "#2E75B6",
        "fontColor": "#FFFFFF",
        "strokeColor": "#1F497D",
        "fontSize": "11",
    },
}


def apply_style_to_cell(cell, style):
    """应用样式到指定单元格"""
    # 获取现有样式
    existing_style = cell.get("style", "")

    # 更新样式
    updates = []
    for key, value in style.items():
        if key == "shape":
            updates.append(f"shape={value}")
        elif key == "fillColor":
            updates.append(f"fillColor={value}")
        elif key == "fontColor":
            updates.append(f"fontColor={value}")
        elif key == "strokeColor":
            updates.append(f"strokeColor={value}")
        elif key == "fontSize":
            updates.append(f"fontSize={value}")
        elif key == "fontStyle":
            updates.append(f"fontStyle={value}")

    # 合并样式
    new_style = existing_style
    for update in updates:
        key, value = update.split("=")
        # 检查是否已存在该属性
        parts = new_style.split(";")
        new_parts = []
        found = False
        for part in parts:
            if part.startswith(f"{key}="):
                new_parts.append(update)
                found = True
            elif part:
                new_parts.append(part)
        if not found:
            new_parts.append(update)
        new_style = ";".join(new_parts)

    cell.set("style", new_style)


def process_drawio_file(file_path, style_name):
    """处理draw.io文件并应用样式"""
    if style_name not in STYLES:
        print(f"错误: 未知的样式 '{style_name}'")
        print(f"支持的样式: {', '.join(STYLES.keys())}")
        return False

    try:
        # 解析XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        # 找到所有mxCell元素
        ns = {"mx": "http://draw.io.mxgraph.com"}
        cells = root.findall(".//mxCell")

        # 应用样式
        style = STYLES[style_name]
        for cell in cells:
            if cell.get("vertex") == "1":  # 只处理图形，不处理连接线
                apply_style_to_cell(cell, style)

        # 保存文件
        output_path = file_path.replace(".drawio", f"_{style_name}.drawio")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"成功: {output_path}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("draw.io 批量样式工具 v1.0")
        print("\n使用方法: python batch_style.py <样式名称> [文件路径]")
        print("\n支持的样式:")
        for name, props in STYLES.items():
            print(f"  - {name}: {props['fillColor']}")
        print("\n示例:")
        print("  python batch_style.py 行政蓝 myflow.drawio")
        sys.exit(1)

    style_name = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if file_path:
        process_drawio_file(file_path, style_name)
    else:
        print(f"请指定要处理的文件路径")
        print(f"支持的样式: {', '.join(STYLES.keys())}")


if __name__ == "__main__":
    main()
