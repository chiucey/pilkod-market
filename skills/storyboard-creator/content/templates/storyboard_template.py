#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分镜表格生成模板
用法：将 ASSETS 和 STORYBOARD_DATA 替换为实际内容，然后运行此脚本。

ASSETS 格式：
    {
        "name": "资产名称-类型",
        "prompt": "完整提示词（人物资产必须含'纯灰色背景，无杂物'）"
    }

STORYBOARD_DATA 格式：
    {
        "seq": 1,                   # 序号（整数）
        "audio": "音频文案（20-40字）",
        "prompt": "视频提示词（七维格式）",
        "speaker": "说话人"
    }
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# ============================================================
# 资产卡数据（替换为实际内容）
# 分三类：角色资产、场景资产、道具资产
# 人物资产提示词中必须包含"纯灰色背景，无杂物"
# ============================================================
ASSETS = [
    # ===== 角色资产（人物必须纯灰色背景） =====
    {
        "name": "示例角色-角色类型",
        "prompt": "男性，30岁，[外貌描述]；[服装描述]；纯灰色背景，无杂物；4K超清，电影质感"
    },
    # ===== 场景资产 =====
    {
        "name": "示例场景-日戏",
        "prompt": "[场景描述]；白天，[光影氛围]；4K超清，电影质感"
    },
    # ===== 道具资产 =====
    {
        "name": "示例道具-道具类型",
        "prompt": "[道具描述]；[材质/体量/细节]；4K超清，微距特写，电影质感"
    },
]

# ============================================================
# 分镜数据（替换为实际内容）
# 每条音频文案控制在 20-40 字（约 3-6 秒）
# ============================================================
STORYBOARD_DATA = [
    {
        "seq": 1,
        "audio": "示例音频文案，控制在20-40字之间，约3-6秒。",
        "prompt": """@示例角色-角色类型
@示例场景-日戏
【构图运镜】中景，固定镜头；
【人物/物件】[画面主体描述]；
【动作/状态】[主体动作描述]；
【位置关系】[位置关系描述]；
【背景环境】[环境描述]；
【光影氛围】[光影描述]；
【时间】白天
(Professional Shot, best quality, highres, masterpiece:1.2, ultra-detailed, [核心意境词])""",
        "speaker": "旁白"
    },
]

# ============================================================
# 分类配置（根据实际资产数量调整 cat_count）
# ============================================================
ASSET_CATEGORIES = [
    ("角色资产", "FF6B35", 1),   # (分类名, 颜色hex, 该分类资产数量)
    ("场景资产", "2E8B57", 1),
    ("道具资产", "4169E1", 1),
]

# ============================================================
# 输出路径（修改为实际输出路径）
# ============================================================
OUTPUT_PATH = "/home/ubuntu/storyboard/分镜表格_输出.xlsx"


# ============================================================
# 以下为生成逻辑，通常无需修改
# ============================================================
def make_border():
    thin = Side(style='thin')
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def make_fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type='solid')


def generate_excel(assets, storyboard_data, asset_categories, output_path):
    wb = openpyxl.Workbook()

    # ---- Sheet 1: 分镜数据 ----
    ws1 = wb.active
    ws1.title = "分镜数据"
    headers1 = ["序号", "音频文案", "视频提示词", "说话人"]
    col_widths1 = [8, 45, 80, 12]

    for col_idx, (header, width) in enumerate(zip(headers1, col_widths1), 1):
        cell = ws1.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = make_fill("2F4F8F")
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = make_border()
        ws1.column_dimensions[get_column_letter(col_idx)].width = width
    ws1.row_dimensions[1].height = 30

    for row_data in storyboard_data:
        row_idx = row_data["seq"] + 1
        row = [row_data["seq"], row_data["audio"], row_data["prompt"], row_data["speaker"]]
        for col_idx, value in enumerate(row, 1):
            cell = ws1.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            cell.border = make_border()
            cell.font = Font(size=10)
            if row_data["seq"] % 2 == 0:
                cell.fill = make_fill("F0F4FF")
        ws1.row_dimensions[row_idx].height = 80

    ws1.freeze_panes = "A2"

    # ---- Sheet 2: 资产卡 ----
    ws2 = wb.create_sheet("资产卡")
    headers2 = ["资产名称", "提示词（Prompt）"]
    col_widths2 = [30, 100]

    for col_idx, (header, width) in enumerate(zip(headers2, col_widths2), 1):
        cell = ws2.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = make_fill("5B4A8F")
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = make_border()
        ws2.column_dimensions[get_column_letter(col_idx)].width = width
    ws2.row_dimensions[1].height = 30

    asset_idx = 0
    row_idx = 2
    for cat_name, cat_color, cat_count in asset_categories:
        # 分类标题行
        cat_cell = ws2.cell(row=row_idx, column=1, value=f"【{cat_name}】")
        cat_cell.font = Font(bold=True, color="FFFFFF", size=11)
        cat_cell.fill = make_fill(cat_color)
        cat_cell.alignment = Alignment(horizontal='center', vertical='center')
        cat_cell.border = make_border()
        ws2.cell(row=row_idx, column=2).fill = make_fill(cat_color)
        ws2.cell(row=row_idx, column=2).border = make_border()
        ws2.row_dimensions[row_idx].height = 25
        row_idx += 1

        for _ in range(cat_count):
            if asset_idx >= len(assets):
                break
            asset = assets[asset_idx]
            name_cell = ws2.cell(row=row_idx, column=1, value=asset["name"])
            name_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            name_cell.border = make_border()
            name_cell.font = Font(size=10, bold=True)

            prompt_cell = ws2.cell(row=row_idx, column=2, value=asset["prompt"])
            prompt_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            prompt_cell.border = make_border()
            prompt_cell.font = Font(size=10)

            if asset_idx % 2 == 0:
                name_cell.fill = make_fill("F5F5FF")
                prompt_cell.fill = make_fill("F5F5FF")

            ws2.row_dimensions[row_idx].height = 60
            row_idx += 1
            asset_idx += 1

    ws2.freeze_panes = "A2"

    wb.save(output_path)
    print(f"✅ 分镜表格已生成：{output_path}")
    print(f"   分镜总条数：{len(storyboard_data)}")
    print(f"   资产卡总数：{len(assets)}")


if __name__ == "__main__":
    generate_excel(ASSETS, STORYBOARD_DATA, ASSET_CATEGORIES, OUTPUT_PATH)
