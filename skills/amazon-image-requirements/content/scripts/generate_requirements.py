# -*- coding: utf-8 -*-
"""
亚马逊图片设计需求文档生成器
基于 FMS 品牌 5 款产品（FCX10LC80、11023 Ford、11853 塞拉、11871 福特烈马、12451 Tacoma）模板
为 RC 攀爬车新品生成标准化的 Excel 设计需求文档

使用方法：
    from generate_requirements import generate_amazon_image_requirements
    generate_amazon_image_requirements(product_info)
"""

import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


# ========== 字体定义 ==========
TITLE_FONT = Font(name="微软雅黑", size=14, bold=True, color="000000")
HEADER_FONT = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
NORMAL_FONT = Font(name="微软雅黑", size=10, color="000000")
INPUT_FONT = Font(name="微软雅黑", size=10, color="0000FF")
NOTE_FONT = Font(name="微软雅黑", size=9, color="666666", italic=True)

# ========== 填充定义（颜色标识）==========
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
TITLE_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
MAIN_IMAGE_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")  # 主图-黄色
SUB_IMAGE_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")   # 副图-绿色
A_PLUS_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")      # A+-橙色

# ========== 边框定义 ==========
THIN = Side(border_style="thin", color="000000")
BORDER = Border(top=THIN, left=THIN, right=THIN, bottom=THIN)

# ========== 对齐定义 ==========
CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=True)


def _get_main_image_block(colors):
    """生成主图部分（每 SKU 一张）"""
    rows = []
    for idx, color in enumerate(colors):
        seq = "1" if idx == 0 else f"1.{idx}"
        rows.append({
            "seq": seq,
            "size": "1600*1600",
            "position": f"{color}主图",
            "expression": "车型展示\n+遥控\n+包装彩盒",
            "assets": "素材编号待定",
            "reference": None,
            "copy": None,
            "note": "\n车身精修，车壳精致有光影，亮度提亮\n白底\n整车+彩盒包装+遥控器展示\n白底，底部带镜面效果，彩盒放底部"
        })
    return rows


def _get_sub_image_block(product_info):
    """生成 7 张副图"""
    full_name = product_info["full_name"]
    scale = product_info["scale"]
    motor_type = product_info["motor_type"]
    license = product_info["license"]
    dimensions = product_info["dimensions"]
    wheelbase = product_info["wheelbase"]
    ground_clearance = product_info["ground_clearance"]
    battery_motor = product_info["battery_motor"]
    features = product_info["features"]

    # 默认图标
    motor_icon = "Brushed" if motor_type == "有刷" else "Brushless"

    rows = []

    # 副图 1：官方授权 + 核心介绍
    rows.append({
        "seq": 2,
        "size": "1600*1600",
        "position": "副图",
        "expression": f"{license}官方授权仿真车壳\n{features[-1] if len(features) > 3 else features[0]}",
        "assets": "选取合适场景图",
        "reference": None,
        "copy": f"{full_name} RC Crawler\nOfficially Licensed by {license}\n加小图标：FMS / 2.4GHz / {scale} / {motor_icon}",
        "note": "场景图+文案\n突出产品独特卖点"
    })

    # 副图 2-4：核心卖点（取前 3 个）
    feature_mapping = [
        {
            "cn_pattern": lambda f: f,
            "en_pattern": lambda f: f,  # 用户应提供英文版
            "note": "突出核心卖点"
        }
    ]

    for i, feature in enumerate(features[:3], 3):
        rows.append({
            "seq": i,
            "size": "1600*1600",
            "position": "副图",
            "expression": feature,
            "assets": "选取细节图+场景图",
            "reference": None,
            "copy": feature,  # 简化：使用中文作为占位，用户可改为专业英文
            "note": f"细节图+场景图+文案\n突出卖点{i-2}"
        })

    # 副图 5：尺寸标注
    rows.append({
        "seq": 6,
        "size": "1600*1600",
        "position": "副图",
        "expression": "尺寸标注\n电池仓尺寸",
        "assets": "素材编号待定",
        "reference": None,
        "copy": f"车 : {dimensions}\n\n轴距 Wheel Base : {wheelbase}\n\n离地间隙 Ground Clearance: {ground_clearance}",
        "note": "尺寸标注清晰，多角度展示"
    })

    # 副图 6：动力系统
    rows.append({
        "seq": 7,
        "size": "1600*1600",
        "position": "副图",
        "expression": f"强劲{battery_motor}动力系统\n稳定可靠，性能优越",
        "assets": "选取电机+电池细节图",
        "reference": None,
        "copy": f"{battery_motor} Power System\nStable, Reliable, High Performance\n\n加图标：{battery_motor} / RTR",
        "note": "电机+电池仓细节展示+文案"
    })

    # 副图 7：底盘/悬挂
    rows.append({
        "seq": 8,
        "size": "1600*1600",
        "position": "副图",
        "expression": "四轮独立悬挂系统\n全时四驱传动系统",
        "assets": "选取底盘照片+细节标注",
        "reference": None,
        "copy": "Four-Wheel Independent Suspension\nFull-Time 4WD Drivetrain",
        "note": "箭头指示加文案\n突出悬挂和四驱设计"
    })

    return rows


def _get_a_plus_block(product_info):
    """生成 A+ 套图部分"""
    full_name = product_info["full_name"]
    scale = product_info["scale"]
    motor_type = product_info["motor_type"]
    license = product_info["license"]
    dimensions = product_info["dimensions"]
    wheelbase = product_info["wheelbase"]
    ground_clearance = product_info["ground_clearance"]
    features = product_info["features"]
    motor_icon = "Brushed" if motor_type == "有刷" else "Brushless"

    rows = []

    # A+ 产品长图
    rows.append({
        "seq": 9,
        "size": "两个尺寸共两张\n1464*2400\n1200*3600",
        "position": "A+ 产品长图",
        "expression": "1.展示户外场景+Banner+图标\n\n2.展示核心卖点1细节\n\n3.展示核心卖点2细节\n\n4.展示核心卖点3细节\n\n5.展示动力系统细节\n\n6.导航栏：图片滑动效果（三张图）\n\n6.1核心卖点1\n6.2核心卖点2\n6.3核心卖点3\n\n7.配件清单：类似参考图，摆放包装内实物，同时标注车子尺寸",
        "assets": "选取合适场景图",
        "reference": None,
        "copy": f"{full_name} RC Crawler\nOfficially Licensed by {license}\n\n图标表达：FMS / {license} / 2.4GHz / {scale} / {motor_icon}",
        "note": "整体长图布局\n体现产品核心卖点",
        "is_a_plus": True
    })

    # A+ 长图各模块细化（不带 seq）
    for i, feature in enumerate(features[:4]):
        rows.append({
            "seq": None,
            "size": None,
            "position": None,
            "expression": feature,
            "assets": "选取细节图+场景图",
            "reference": None,
            "copy": feature,
            "note": None,
            "is_a_plus": True
        })

    # 配件清单
    rows.append({
        "seq": None,
        "size": None,
        "position": None,
        "expression": None,
        "assets": None,
        "reference": None,
        "copy": f"Packing List:\n\nL*W*H:  {dimensions}\nWheelbase: {wheelbase}\nGround Clearance: {ground_clearance}",
        "note": None,
        "is_a_plus": True
    })

    # A+ Banner
    rows.append({
        "seq": 10,
        "size": "三个尺寸共三张\n1464*600\n1200*900\n970*600",
        "position": "A+ banner",
        "expression": "Banner：户外场景+产品图+图标",
        "assets": "选取合适场景图",
        "reference": None,
        "copy": f"{full_name} RC Crawler\nOfficially Licensed by {license}\n\n加图标：FMS / {license}官方授权 / 2.4GHz / {scale} / {motor_icon}",
        "note": None,
        "is_a_plus": True
    })

    # A+ 导航栏（3 张）
    nav_themes = ["核心卖点1", "核心卖点2", "核心卖点3"]
    for i, theme in enumerate(nav_themes, 11):
        if i - 11 < len(features):
            rows.append({
                "seq": i,
                "size": "三个尺寸共三张\n1464*600\n1200*900\n970*600",
                "position": "A+ 导航栏",
                "expression": features[i - 11],
                "assets": "选取细节图+场景图",
                "reference": None,
                "copy": features[i - 11],
                "note": None,
                "is_a_plus": True
            })

    # 配件清单（独立模块）
    rows.append({
        "seq": 14,
        "size": "三个尺寸共三张\n1464*600\n1200*900\n970*600",
        "position": "配件清单",
        "expression": "类似参考图，摆放包装内实物，同时标注车子尺寸",
        "assets": "包装内配件素材",
        "reference": None,
        "copy": f"Packing List:\n\nL*W*H:  {dimensions}\nWheelbase: {wheelbase}\nGround Clearance: {ground_clearance}",
        "note": None,
        "is_a_plus": True
    })

    # 场景图
    rows.append({
        "seq": 15,
        "size": "三个尺寸共三张\n1464*600\n1200*900\n970*600",
        "position": "场景图",
        "expression": "展示产品使用场景\n突出性能与体验",
        "assets": "选取合适场景图",
        "reference": None,
        "copy": f"Experience Ultimate {scale} Crawling Thrills\nPremium RC Experience",
        "note": None,
        "is_a_plus": True
    })

    # 细节图（4-5 张）
    detail_themes = features[:4] if len(features) >= 4 else features + ["产品细节"] * (4 - len(features))
    for i, theme in enumerate(detail_themes, 16):
        rows.append({
            "seq": i,
            "size": "2600*1400",
            "position": "细节图",
            "expression": theme,
            "assets": "素材编号待定",
            "reference": None,
            "copy": theme,
            "note": None,
            "is_a_plus": True
        })

    return rows


def _set_cell(ws, row, col, value, fill=None, font=None, alignment=None):
    """统一设置单元格样式"""
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = font or NORMAL_FONT
    cell.alignment = alignment or LEFT_ALIGN
    cell.border = BORDER
    if fill:
        cell.fill = fill
    return cell


def _get_row_fill(position):
    """根据位置确定填充色"""
    if not position:
        return None
    position_str = str(position)
    if "A+" in position_str or "banner" in position_str.lower() or "导航栏" in position_str or "细节图" in position_str or "配件清单" in position_str or "场景图" in position_str:
        return A_PLUS_FILL
    elif "主图" in position_str:
        return MAIN_IMAGE_FILL
    else:
        return SUB_IMAGE_FILL


def generate_amazon_image_requirements(product_info):
    """
    生成亚马逊图片设计需求 Excel 文档

    参数:
        product_info (dict): 包含以下键值
            - model: 型号（如 "118L01"）
            - product_name: 产品名（如 "Ford F-100"）
            - full_name: 完整产品名（如 "FMS 1:18 FCXII 118L01 Ford F-100"）
            - scale: 比例（如 "1/18"）
            - motor_type: 电机类型（"有刷" / "无刷"）
            - vehicle_model: 车型（如 "福特F100"）
            - license: 官方授权（如 "Ford"）
            - colors: 颜色列表（如 ["黑白", "蒂芙尼蓝", "红白"]）
            - features: 卖点列表（5-7个卖点）
            - dimensions: 尺寸（如 "330*145*147mm"）
            - wheelbase: 轴距（如 "199mm"）
            - ground_clearance: 离地间隙（如 "31mm"）
            - battery_motor: 电池/电机（如 "180有刷"）
            - has_source_assets: bool, 是否有原始素材
            - need_scene_images: bool, 是否需要场景图
            - need_shooting: bool, 是否需要拍摄
            - output_dir: 输出目录

    返回:
        str: 生成的 Excel 文件绝对路径
    """
    # ========== 验证必要参数 ==========
    required_keys = ["model", "product_name", "full_name", "scale", "motor_type",
                     "vehicle_model", "license", "colors", "features",
                     "dimensions", "wheelbase", "ground_clearance", "battery_motor"]
    for key in required_keys:
        if key not in product_info:
            raise ValueError(f"❌ 缺少必要参数: {key}")

    # ========== 创建工作簿 ==========
    wb = openpyxl.Workbook()
    ws = wb.active

    # Sheet 名称：型号 + 产品名
    sheet_name = f"{product_info['model']} {product_info['product_name']}"
    # 限制 sheet 名长度（Excel 最大 31 字符）
    if len(sheet_name) > 31:
        sheet_name = sheet_name[:31]
    ws.title = sheet_name

    # ========== 第 1 行：标题 ==========
    ws.merge_cells("A1:H1")
    title_cell = ws["A1"]
    title_cell.value = "设计需求表格表"
    title_cell.font = TITLE_FONT
    title_cell.fill = TITLE_FILL
    title_cell.alignment = CENTER_ALIGN
    title_cell.border = BORDER

    # ========== 第 2 行：风格说明 + 设计师信息 ==========
    ws.merge_cells("A2:F2")
    ws["A2"] = "整体色调风格字体需要统一，谢谢"
    ws["A2"].font = NORMAL_FONT
    ws["A2"].alignment = LEFT_ALIGN
    ws["A2"].border = BORDER

    ws.merge_cells("G2:H2")
    ws["G2"] = "本次设计师信息：\n平面：\n视频："
    ws["G2"].font = INPUT_FONT
    ws["G2"].alignment = LEFT_ALIGN
    ws["G2"].border = BORDER

    # ========== 第 3 行：表头 ==========
    headers = ["顺序", "图片尺寸（宽 x 高 ) px", "图片使用位置（主图，副图，A+）",
               "想通过设计表达出来什么", "公司是否有满足的素材", "参考图", "文案", "备注"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_ALIGN
        cell.border = BORDER

    # ========== 数据行 ==========
    all_rows = []
    all_rows.extend(_get_main_image_block(product_info["colors"]))
    all_rows.extend(_get_sub_image_block(product_info))
    all_rows.extend(_get_a_plus_block(product_info))

    for row_data in all_rows:
        seq = row_data["seq"]
        size = row_data["size"]
        position = row_data["position"]
        expression = row_data["expression"]
        assets = row_data["assets"]
        reference = row_data["reference"]
        copy = row_data["copy"]
        note = row_data["note"]

        ws.append([seq, size, position, expression, assets, reference, copy, note])

        # 获取刚添加的行号
        current_row = ws.max_row
        fill = _get_row_fill(position)

        # 应用样式
        for col_idx in range(1, 9):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = NORMAL_FONT
            cell.alignment = LEFT_ALIGN
            cell.border = BORDER
            if fill:
                cell.fill = fill

    # ========== 设置列宽 ==========
    column_widths = {
        "A": 8,    # 顺序
        "B": 20,   # 图片尺寸
        "C": 18,   # 图片使用位置
        "D": 50,   # 想通过设计表达出来什么
        "E": 25,   # 公司是否有满足的素材
        "F": 15,   # 参考图
        "G": 60,   # 文案
        "H": 50,   # 备注
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # ========== 设置行高 ==========
    for row_idx in range(4, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 80
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 40

    # ========== 冻结首行 ==========
    ws.freeze_panes = "A4"

    # ========== 保存文件 ==========
    output_dir = product_info.get("output_dir", os.getcwd())
    os.makedirs(output_dir, exist_ok=True)

    # 文件名：型号_产品名_设计需求表格.xlsx
    safe_product_name = product_info["product_name"].replace("/", "_").replace("\\", "_")
    filename = f"{product_info['model']}_{safe_product_name}_设计需求表格.xlsx"
    output_path = os.path.join(output_dir, filename)

    wb.save(output_path)

    print(f"✅ 文件已生成: {output_path}")
    print(f"📊 共生成 {ws.max_row - 3} 行需求")
    print(f"📐 包含主图{len(product_info['colors'])}张 + 副图7张 + A+套图 + 配件清单 + 细节图")

    return output_path


# ========== 独立使用示例 ==========
if __name__ == "__main__":
    # 示例：FMS 1:18 FCXII 118L01 Ford F-100
    example_info = {
        "model": "118L01",
        "product_name": "Ford F-100",
        "full_name": "FMS 1:18 FCXII 118L01 Ford F-100",
        "scale": "1/18",
        "motor_type": "有刷",
        "vehicle_model": "福特F100",
        "license": "Ford",
        "colors": ["黑白", "蒂芙尼蓝", "红白"],
        "features": [
            "全新FCX18二代低重心(LCG)底盘，更强的攀爬性能与姿态表现（不易翻车）",
            "多品牌授权，福特官方授权仿真车壳，BFGOODRICH授权KO3轮胎",
            "磁吸快拆结构，同款不同涂装的车壳1秒快速更换",
            "全球首推1/18福特F-100攀爬车"
        ],
        "dimensions": "330*145*147mm",
        "wheelbase": "199mm",
        "ground_clearance": "31mm",
        "battery_motor": "180有刷",
        "has_source_assets": True,
        "need_scene_images": True,
        "need_shooting": False,
        "output_dir": r"D:\minimax-亚马逊"
    }

    output_path = generate_amazon_image_requirements(example_info)
    print(f"\n📁 输出文件: {output_path}")
