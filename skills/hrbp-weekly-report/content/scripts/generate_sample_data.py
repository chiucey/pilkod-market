#!/usr/bin/env python3
"""
生成示例Excel数据文件，用于演示HRBP周报邮件生成流程
"""

import pandas as pd
from datetime import datetime, timedelta


def create_sample_excel():
    """创建包含示例数据的Excel文件"""

    # 招聘数据
    recruitment_data = pd.DataFrame({
        '日期': ['2024-03-25', '2024-03-26', '2024-03-27', '2024-03-28'],
        '岗位名称': ['Java开发工程师', '产品经理', 'UI设计师', '前端开发'],
        '招聘数量': [2, 1, 1, 1],
        '目标人数': [3, 2, 1, 2],
        '入职日期': ['2024-03-28', '2024-04-01', '2024-04-02', '2024-04-03'],
        '紧急程度': ['紧急', '重要', '一般', '重要']
    })

    # 离职数据
    attrition_data = pd.DataFrame({
        '日期': ['2024-03-27'],
        '员工姓名': ['李四'],
        '部门': ['华东销售'],
        '离职原因': ['个人发展'],
        '具体原因': ['寻求更好的职业发展机会'],
        '职级': ['P5']
    })

    # 培训数据
    training_data = pd.DataFrame({
        '培训日期': ['2024-03-25', '2024-03-26', '2024-03-28'],
        '培训主题': ['新员工入职培训', '团队协作工作坊', '技术分享会'],
        '计划人数': [15, 20, 25],
        '实际人数': [14, 18, 24],
        '时长(小时)': [2, 3, 1.5],
        '满意度': [4.8, 4.5, 4.2],
        '培训形式': ['线下', '线下', '线上']
    })

    # 保存Excel文件
    output_path = '/workspace/temp-skills/hrbp-weekly-report/assets/sample_hr_data.xlsx'

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        recruitment_data.to_excel(writer, sheet_name='招聘数据', index=False)
        attrition_data.to_excel(writer, sheet_name='离职数据', index=False)
        training_data.to_excel(writer, sheet_name='培训数据', index=False)

    print(f"示例数据已生成: {output_path}")
    return output_path


if __name__ == '__main__':
    create_sample_excel()
