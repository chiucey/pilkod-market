#!/usr/bin/env python3
"""
测试脚本：创建示例文档并演示格式化
"""

from docx import Document
from docx.shared import Pt
import os

def create_sample_petition():
    """创建示例请示文档"""
    doc = Document()
    
    # 添加标题（未格式化）
    doc.add_paragraph('信息技术中心关于采购办公设备的请示')
    
    # 添加空行
    doc.add_paragraph('')
    
    # 添加收件单位
    doc.add_paragraph('规划采购部：')
    
    # 添加正文
    doc.add_paragraph('    我中心需要采购一批办公设备，包括电脑、打印机等。经过市场调研和比价，拟选择XX公司作为供应商，总金额为50000元。')
    
    doc.add_paragraph('    具体设备清单详见附件。')
    
    # 添加结尾语
    doc.add_paragraph('妥否，请批示。')
    
    # 添加附件
    doc.add_paragraph('附件：设备清单')
    
    # 添加空行
    doc.add_paragraph('')
    doc.add_paragraph('')
    
    # 添加日期
    doc.add_paragraph('2025年11月24日')
    
    # 添加经办人
    doc.add_paragraph('（经办人：张三 联系方式：13800138000）')
    
    # 保存未格式化的文档
    output_file = 'sample_petition_before.docx'
    doc.save(output_file)
    print(f"✓ 已创建示例文档: {output_file}")
    return output_file


def main():
    print("=" * 60)
    print("Word 公文格式化工具 - 测试演示")
    print("=" * 60)
    print()
    
    # 创建示例文档
    print("步骤1: 创建示例请示文档...")
    input_file = create_sample_petition()
    print()
    
    # 提示用户运行格式化
    print("步骤2: 运行以下命令格式化文档:")
    print(f"   python scripts/format_doc.py {input_file} sample_petition_after.docx petition")
    print()
    
    print("步骤3: 对比查看格式化前后的文档")
    print(f"   格式化前: {input_file}")
    print(f"   格式化后: sample_petition_after.docx")
    print()
    
    print("=" * 60)
    print("提示: 你也可以直接把 .docx 文件发给 AI 助手进行格式化")
    print("=" * 60)


if __name__ == '__main__':
    main()
