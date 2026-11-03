#!/usr/bin/env python3
"""
校准证书信息生成Excel脚本
根据提取的校准证书数据生成标准化的7列Excel汇总表

使用方法:
    python create_excel_from_certs.py
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

def create_calibration_excel(certificates: list, output_path: str):
    """
    创建校准证书汇总Excel文件

    Args:
        certificates: 证书数据列表，每个元素为字典
        output_path: 输出文件路径
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "校准证书信息汇总"

    # 设置表头
    headers = ["证书编号", "器具名称", "型号/规格", "制造单位", "校准日期", "校准依据", "数据测试内容"]
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # 设置列宽
    column_widths = [18, 20, 20, 25, 15, 40, 60]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    # 添加数据
    data_alignment = Alignment(vertical="top", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row, cert in enumerate(certificates, 2):
        for col, key in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=cert.get(key, ""))
            cell.alignment = data_alignment
            cell.border = thin_border

    # 设置行高
    for row in range(2, len(certificates) + 2):
        ws.row_dimensions[row].height = 80

    wb.save(output_path)
    print(f"Excel文件已创建: {output_path}")


if __name__ == "__main__":
    # 示例数据
    sample_certificates = [
        {
            "证书编号": "J26457S00146",
            "器具名称": "电子秤",
            "型号/规格": "TCS-150",
            "制造单位": "中山市衡新电子有限公司",
            "校准日期": "2026年4月1日",
            "校准依据": "JJG 539-2016 数字指示秤检定规程",
            "数据测试内容": "称量校准\n测试点(kg)：1/10/40/100/150\n测试条件：环境温度22°C"
        },
        {
            "证书编号": "J26543S00213",
            "器具名称": "瓶盖扭矩测试仪",
            "型号/规格": "HB-10",
            "制造单位": "东莞市恒宇仪器有限公司",
            "校准日期": "2026年4月2日",
            "校准依据": "JJG 797-2013 扭矩扳子检定仪检定规程",
            "数据测试内容": "扭矩校准\n顺时针方向测试点(Nm)：1.75/2/4/6/8/10\n逆时针方向测试点(Nm)：1.75/2/4/6/8/10\n测试条件：环境温度22.1℃"
        }
    ]

    output = "/workspace/校准证书示例.xlsx"
    create_calibration_excel(sample_certificates, output)
