#!/usr/bin/env python3
"""
行政流程图模板生成工具
快速生成标准化的行政流程图XML文件

使用方法:
    python gen_template.py <模板名称> [输出文件]
"""

import sys
from datetime import datetime

# 模板定义
TEMPLATES = {
    "公文处理": {
        "title": "公文处理流程图",
        "nodes": [
            {"id": "start", "type": "start", "label": "开始", "x": 400, "y": 50},
            {"id": "draft", "type": "process", "label": "拟稿", "x": 400, "y": 150},
            {"id": "dept_review", "type": "process", "label": "部门审核", "x": 400, "y": 250},
            {"id": "office_review", "type": "process", "label": "办公室初审", "x": 400, "y": 350},
            {"id": "sign", "type": "process", "label": "领导签发", "x": 400, "y": 450},
            {"id": "publish", "type": "process", "label": "印发归档", "x": 400, "y": 550},
            {"id": "end", "type": "end", "label": "结束", "x": 400, "y": 650},
        ],
        "connections": [
            ("start", "draft"),
            ("draft", "dept_review"),
            ("dept_review", "office_review"),
            ("office_review", "sign"),
            ("sign", "publish"),
            ("publish", "end"),
        ],
    },
    "会议管理": {
        "title": "会议管理流程图",
        "nodes": [
            {"id": "start", "type": "start", "label": "会议申请", "x": 400, "y": 50},
            {"id": "approval", "type": "process", "label": "领导审批", "x": 400, "y": 150},
            {"id": "prepare", "type": "process", "label": "会前准备", "x": 400, "y": 250},
            {"id": "meeting", "type": "process", "label": "召开会议", "x": 400, "y": 350},
            {"id": "minutes", "type": "process", "label": "编写纪要", "x": 400, "y": 450},
            {"id": "archive", "type": "process", "label": "归档存档", "x": 400, "y": 550},
            {"id": "end", "type": "end", "label": "结束", "x": 400, "y": 650},
        ],
        "connections": [
            ("start", "approval"),
            ("approval", "prepare"),
            ("prepare", "meeting"),
            ("meeting", "minutes"),
            ("minutes", "archive"),
            ("archive", "end"),
        ],
    },
    "绩效考核": {
        "title": "绩效考核流程图",
        "nodes": [
            {"id": "start", "type": "start", "label": "发布考核通知", "x": 400, "y": 50},
            {"id": "self_eval", "type": "process", "label": "个人述职自评", "x": 400, "y": 150},
            {"id": "dept_eval", "type": "process", "label": "部门初评", "x": 400, "y": 250},
            {"id": "demo_eval", "type": "process", "label": "民主测评", "x": 400, "y": 350},
            {"id": "final_eval", "type": "process", "label": "考核小组复审", "x": 400, "y": 450},
            {"id": "result", "type": "process", "label": "结果公示", "x": 400, "y": 550},
            {"id": "end", "type": "end", "label": "结束", "x": 400, "y": 650},
        ],
        "connections": [
            ("start", "self_eval"),
            ("self_eval", "dept_eval"),
            ("dept_eval", "demo_eval"),
            ("demo_eval", "final_eval"),
            ("final_eval", "result"),
            ("result", "end"),
        ],
    },
}


def get_style_by_type(node_type):
    """根据节点类型获取样式"""
    styles = {
        "start": {"shape": "ellipse", "fillColor": "#70AD47", "fontColor": "#FFFFFF"},
        "end": {"shape": "ellipse", "fillColor": "#C00000", "fontColor": "#FFFFFF"},
        "process": {"shape": "rectangle", "fillColor": "#4472C4", "fontColor": "#FFFFFF"},
        "decision": {"shape": "rhombus", "fillColor": "#ED7D31", "fontColor": "#FFFFFF"},
    }
    return styles.get(node_type, styles["process"])


def generate_xml(template_name):
    """生成draw.io XML文件内容"""
    template = TEMPLATES.get(template_name)
    if not template:
        return None

    xml_parts = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append('<mxfile host="app.diagrams.net">')
    xml_parts.append('  <diagram name="{}">'.format(template["title"]))
    xml_parts.append('    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10">')
    xml_parts.append('      <root>')
    xml_parts.append('        <mxCell id="0" />')
    xml_parts.append('        <mxCell id="1" parent="0" />')

    # 生成节点
    for i, node in enumerate(template["nodes"]):
        style_info = get_style_by_type(node["type"])
        style = "shape={shape};whiteSpace=wrap;html=1;fillColor={fillColor};fontColor={fontColor};".format(
            **style_info
        )
        cell_id = i + 10
        xml_parts.append(
            '        <mxCell id="{}" value="{}" style="{}" vertex="1" parent="1">'.format(
                cell_id, node["label"], style
            )
        )
        xml_parts.append(
            '          <mxGeometry x="{}" y="{}" width="120" height="60" as="geometry" />'.format(
                node["x"] - 60, node["y"]
            )
        )
        xml_parts.append("        </mxCell>")

    # 生成连接
    node_map = {n["id"]: i + 10 for i, n in enumerate(template["nodes"])}
    edge_id = 100
    for source, target in template["connections"]:
        xml_parts.append(
            '        <mxCell id="{}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;endArrow=classic;" edge="1" parent="1" source="{}" target="{}">'.format(
                edge_id, node_map[source], node_map[target]
            )
        )
        xml_parts.append('          <mxGeometry relative="1" as="geometry" />')
        xml_parts.append("        </mxCell>")
        edge_id += 1

    xml_parts.append("      </root>")
    xml_parts.append("    </mxGraphModel>")
    xml_parts.append("  </diagram>")
    xml_parts.append("</mxfile>")

    return "\n".join(xml_parts)


def main():
    if len(sys.argv) < 2:
        print("行政流程图模板生成工具 v1.0")
        print("\n使用方法: python gen_template.py <模板名称> [输出文件]")
        print("\n可用模板:")
        for name in TEMPLATES.keys():
            print("  - {}".format(name))
        print("\n示例:")
        print("  python gen_template.py 公文处理 output.drawio")
        sys.exit(1)

    template_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "{}.drawio".format(template_name)

    xml_content = generate_xml(template_name)
    if xml_content:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print("成功生成: {}".format(output_file))
        print("提示: 双击文件在draw.io中打开")
    else:
        print("错误: 未知的模板 '{}'".format(template_name))
        print("可用模板: {}".format(", ".join(TEMPLATES.keys())))


if __name__ == "__main__":
    main()
