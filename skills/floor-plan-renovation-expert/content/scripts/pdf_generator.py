#!/usr/bin/env python3
"""
户型图装修方案PDF文档生成脚本
功能：将装修方案整合为完整的PDF文档，包含效果图、预算表、进度表
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from html import escape


@dataclass
class RoomImage:
    """房间效果图"""
    room_name: str        # 房间名称
    image_path: str       # 图片路径
    description: str = "" # 描述


@dataclass
class RenovationPlan:
    """装修方案数据"""
    plan_name: str                    # 方案名称
    plan_type: str                    # 方案类型
    total_area: float                 # 装修面积
    style: str                        # 风格
    concept: str                      # 设计理念

    # 效果图
    overall_images: List[RoomImage] = field(default_factory=list)   # 整体效果图
    room_images: List[RoomImage] = field(default_factory=list)       # 分部分效果图

    # 预算数据
    base_cost: float = 0
    main_material_cost: float = 0
    furniture_cost: float = 0
    appliance_cost: float = 0
    soft_decor_cost: float = 0
    other_cost: float = 0
    total_cost: float = 0
    budget_items: List[Dict] = field(default_factory=list)

    # 进度数据
    phases: List[Dict] = field(default_factory=list)
    total_days: int = 0
    start_date: str = ""
    end_date: str = ""


class PDFGenerator:
    """PDF文档生成器"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.css_styles = self._get_css_styles()

    def _get_css_styles(self) -> str:
        """获取CSS样式"""
        return """
        <style>
            @page {
                size: A4;
                margin: 20mm 15mm;
            }

            * {
                box-sizing: border-box;
            }

            body {
                font-family: "Microsoft YaHei", "SimHei", "PingFang SC", sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }

            /* 封面 */
            .cover {
                text-align: center;
                padding: 80px 40px;
                page-break-after: always;
            }

            .cover h1 {
                font-size: 32pt;
                color: #2c3e50;
                margin-bottom: 20px;
            }

            .cover .subtitle {
                font-size: 16pt;
                color: #666;
                margin-bottom: 60px;
            }

            .cover .info {
                font-size: 12pt;
                color: #999;
                margin-top: 100px;
            }

            /* 目录 */
            .toc {
                page-break-after: always;
            }

            .toc h2 {
                font-size: 20pt;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }

            .toc-item {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px dotted #ddd;
                font-size: 12pt;
            }

            /* 章节标题 */
            .section {
                page-break-before: always;
                padding: 20px 0;
            }

            .section h2 {
                font-size: 18pt;
                color: #2c3e50;
                border-left: 5px solid #3498db;
                padding-left: 15px;
                margin-bottom: 25px;
            }

            .section h3 {
                font-size: 14pt;
                color: #34495e;
                margin: 20px 0 15px 0;
            }

            /* 方案对比 */
            .plan-comparison {
                display: flex;
                justify-content: space-between;
                margin: 20px 0;
            }

            .plan-card {
                flex: 1;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                margin: 0 10px;
                text-align: center;
            }

            .plan-card.economy {
                border-color: #95a5a6;
            }

            .plan-card.standard {
                border-color: #3498db;
                box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
            }

            .plan-card.luxury {
                border-color: #f39c12;
            }

            .plan-card h4 {
                font-size: 14pt;
                margin: 0 0 10px 0;
            }

            .plan-card .price {
                font-size: 20pt;
                color: #e74c3c;
                font-weight: bold;
            }

            /* 效果图 */
            .image-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 20px 0;
            }

            .image-grid.single {
                grid-template-columns: 1fr;
            }

            .image-item {
                border: 1px solid #ddd;
                border-radius: 8px;
                overflow: hidden;
            }

            .image-item img {
                width: 100%;
                height: auto;
                display: block;
            }

            .image-item .caption {
                padding: 10px;
                background: #f8f9fa;
                font-size: 10pt;
                color: #666;
                text-align: center;
            }

            /* 表格 */
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 10pt;
            }

            th {
                background: #3498db;
                color: white;
                padding: 12px 8px;
                text-align: left;
                font-weight: normal;
            }

            td {
                padding: 10px 8px;
                border-bottom: 1px solid #eee;
            }

            tr:nth-child(even) {
                background: #f8f9fa;
            }

            .total-row {
                font-weight: bold;
                background: #ecf0f1 !important;
                color: #2c3e50;
            }

            .total-row td {
                border-top: 2px solid #3498db;
            }

            /* 进度表 */
            .schedule-phase {
                margin: 25px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }

            .schedule-phase h4 {
                margin: 0 0 15px 0;
                color: #2c3e50;
            }

            .gantt-bar {
                display: flex;
                align-items: center;
                margin: 8px 0;
            }

            .gantt-label {
                width: 100px;
                font-size: 10pt;
            }

            .gantt-track {
                flex: 1;
                height: 20px;
                background: #ecf0f1;
                border-radius: 4px;
                position: relative;
                overflow: hidden;
            }

            .gantt-fill {
                position: absolute;
                height: 100%;
                background: linear-gradient(90deg, #3498db, #2980b9);
                border-radius: 4px;
            }

            .gantt-duration {
                width: 80px;
                text-align: right;
                font-size: 10pt;
                color: #666;
            }

            /* 页脚 */
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 9pt;
                color: #999;
                padding: 10px;
                border-top: 1px solid #eee;
            }

            .page-number {
                text-align: right;
                margin-top: 20px;
                font-size: 10pt;
                color: #999;
            }

            /* 提示框 */
            .tip-box {
                background: #e8f6f3;
                border-left: 4px solid #1abc9c;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 4px 4px 0;
            }

            .warning-box {
                background: #fef9e7;
                border-left: 4px solid #f39c12;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 4px 4px 0;
            }
        </style>
        """

    def _load_image_as_base64(self, image_path: str) -> str:
        """将图片转换为base64"""
        if not image_path or not os.path.exists(image_path):
            return ""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _get_image_html(self, image_path: str, alt_text: str, width: str = "100%") -> str:
        """生成图片HTML"""
        if not image_path or not os.path.exists(image_path):
            return f'<div class="image-item"><p style="color:#999;text-align:center;">{escape(alt_text)} (图片待生成)</p></div>'

        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "jpeg" if ext in [".jpg", ".jpeg"] else ext[1:]
        b64_data = self._load_image_as_base64(image_path)
        return f'<img src="data:image/{mime_type};base64,{b64_data}" alt="{escape(alt_text)}" style="width:{width};max-width:{width};" />'

    def generate_cover_page(self, project_name: str, total_area: float, plan_count: int) -> str:
        """生成封面页"""
        return f"""
        <div class="cover">
            <h1>户型装修设计方案</h1>
            <div class="subtitle">
                <p>项目名称：{escape(project_name)}</p>
                <p>装修面积：{total_area:.2f} 平方米</p>
                <p>方案数量：{plan_count} 套</p>
            </div>
            <div class="info">
                <p>编制日期：{datetime.now().strftime('%Y年%m月%d日')}</p>
                <p>专业团队 · 精心设计</p>
            </div>
        </div>
        """

    def generate_toc_page(self) -> str:
        """生成目录页"""
        return """
        <div class="toc">
            <h2>目 录</h2>
            <div class="toc-item">
                <span>一、方案概述</span>
                <span>3</span>
            </div>
            <div class="toc-item">
                <span>二、方案对比</span>
                <span>4</span>
            </div>
            <div class="toc-item">
                <span>三、经济实用型方案</span>
                <span>5</span>
            </div>
            <div class="toc-item">
                <span>四、品质舒适型方案</span>
                <span>8</span>
            </div>
            <div class="toc-item">
                <span>五、高端豪华型方案</span>
                <span>11</span>
            </div>
            <div class="toc-item">
                <span>六、预算费用表</span>
                <span>14</span>
            </div>
            <div class="toc-item">
                <span>七、时间进度表</span>
                <span>18</span>
            </div>
            <div class="toc-item">
                <span>八、装修小贴士</span>
                <span>22</span>
            </div>
        </div>
        """

    def generate_plan_comparison(self, plans: List[RenovationPlan]) -> str:
        """生成方案对比页"""
        cards = []
        for plan in plans:
            cards.append(f"""
            <div class="plan-card {plan.plan_type}">
                <h4>{escape(plan.plan_name)}</h4>
                <p style="color:#666;font-size:10pt;">{escape(plan.style)}</p>
                <p class="price">¥{plan.total_cost:,.0f}</p>
                <p style="font-size:10pt;color:#999;">约 {plan.total_cost / plan.total_area:,.0f}元/平米</p>
                <p style="font-size:10pt;margin-top:15px;">{escape(plan.concept)}</p>
            </div>
            """)

        return f"""
        <div class="section">
            <h2>二、方案对比</h2>
            <p style="margin-bottom:20px;">本方案提供三套不同定位的装修方案，供您根据预算和需求选择：</p>
            <div class="plan-comparison">
                {''.join(cards)}
            </div>
        </div>
        """

    def generate_plan_detail(self, plan: RenovationPlan) -> str:
        """生成单个方案详情页"""
        # 整体效果图
        overall_images_html = ""
        for img in plan.overall_images:
            overall_images_html += f"""
            <div class="image-item">
                {self._get_image_html(img.image_path, img.room_name)}
                <div class="caption">{escape(img.room_name)}</div>
            </div>
            """

        # 分部分效果图
        room_images_html = ""
        for img in plan.room_images:
            room_images_html += f"""
            <div class="image-item">
                {self._get_image_html(img.image_path, img.room_name)}
                <div class="caption">{escape(img.room_name)}</div>
            </div>
            """

        # 预算摘要
        budget_summary = f"""
        <table>
            <tr>
                <th>费用类别</th>
                <th>金额（元）</th>
                <th>占比</th>
            </tr>
            <tr>
                <td>基础装修费</td>
                <td>¥{plan.base_cost:,.2f}</td>
                <td>{plan.base_cost / plan.total_cost * 100:.1f}%</td>
            </tr>
            <tr>
                <td>主材费</td>
                <td>¥{plan.main_material_cost:,.2f}</td>
                <td>{plan.main_material_cost / plan.total_cost * 100:.1f}%</td>
            </tr>
            <tr>
                <td>家具费</td>
                <td>¥{plan.furniture_cost:,.2f}</td>
                <td>{plan.furniture_cost / plan.total_cost * 100:.1f}%</td>
            </tr>
            <tr>
                <td>家电费</td>
                <td>¥{plan.appliance_cost:,.2f}</td>
                <td>{plan.appliance_cost / plan.total_cost * 100:.1f}%</td>
            </tr>
            <tr>
                <td>软装费</td>
                <td>¥{plan.soft_decor_cost:,.2f}</td>
                <td>{plan.soft_decor_cost / plan.total_cost * 100:.1f}%</td>
            </tr>
            <tr>
                <td>其他费用</td>
                <td>¥{plan.other_cost:,.2f}</td>
                <td>{plan.other_cost / plan.total_cost * 100:.1f}%</td>
            </tr>
            <tr class="total-row">
                <td>合计</td>
                <td>¥{plan.total_cost:,.2f}</td>
                <td>100%</td>
            </tr>
        </table>
        """

        # 进度摘要
        schedule_html = ""
        for phase in plan.phases:
            schedule_html += f"""
            <div class="schedule-phase">
                <h4>{escape(phase.get('phase_name', ''))}</h4>
                <p style="font-size:10pt;color:#666;">工期：{phase.get('total_days', 0)}天</p>
            </div>
            """

        return f"""
        <div class="section">
            <h2>{escape(plan.plan_name)}</h2>

            <h3>设计理念</h3>
            <p>{escape(plan.concept)}</p>

            <h3>整体效果图</h3>
            <div class="image-grid single">
                {overall_images_html}
            </div>

            <h3>分部分效果图</h3>
            <div class="image-grid">
                {room_images_html}
            </div>

            <h3>预算摘要</h3>
            {budget_summary}

            <h3>施工进度</h3>
            <p>总工期：{plan.total_days}天 | 开工：{plan.start_date} | 竣工：{plan.end_date}</p>
            {schedule_html}
        </div>
        """

    def generate_budget_table(self, plans: List[RenovationPlan]) -> str:
        """生成预算费用表页"""
        tables_html = ""
        for plan in plans:
            items_html = ""
            for item in plan.budget_items:
                items_html += f"""
                <tr>
                    <td>{escape(item.get('category', ''))}</td>
                    <td>{escape(item.get('item_name', ''))}</td>
                    <td>{item.get('unit', '')}</td>
                    <td>{item.get('quantity', 0)}</td>
                    <td>¥{item.get('unit_price', 0):,.2f}</td>
                    <td>¥{item.get('total_price', 0):,.2f}</td>
                </tr>
                """

            tables_html += f"""
            <h3>{escape(plan.plan_name)} - 费用明细</h3>
            <p style="color:#e74c3c;font-weight:bold;">总价：¥{plan.total_cost:,.2f}</p>
            <table>
                <tr>
                    <th>类别</th>
                    <th>项目</th>
                    <th>单位</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>总价</th>
                </tr>
                {items_html}
            </table>
            """

        return f"""
        <div class="section">
            <h2>六、预算费用表</h2>
            {tables_html}
        </div>
        """

    def generate_schedule_table(self, plans: List[RenovationPlan]) -> str:
        """生成时间进度表页"""
        tables_html = ""
        for plan in plans:
            phases_html = ""
            for phase in plan.phases:
                tasks_html = ""
                for task in phase.get('tasks', []):
                    tasks_html += f"""
                    <tr>
                        <td>{escape(task.get('task_name', ''))}</td>
                        <td>{task.get('duration', 0)}天</td>
                        <td>{escape(task.get('responsible', ''))}</td>
                    </tr>
                    """

                phases_html += f"""
                <div class="schedule-phase">
                    <h4>{escape(phase.get('phase_name', ''))}（第{phase.get('start_day', 0)}-{phase.get('end_day', 0)}天）</h4>
                    <table>
                        <tr>
                            <th>任务</th>
                            <th>工期</th>
                            <th>负责人</th>
                        </tr>
                        {tasks_html}
                    </table>
                </div>
                """

            tables_html += f"""
            <h3>{escape(plan.plan_name)}</h3>
            <p>总工期：{plan.total_days}天 | 开工：{plan.start_date} | 竣工：{plan.end_date}</p>
            {phases_html}
            """

        return f"""
        <div class="section">
            <h2>七、时间进度表</h2>
            {tables_html}
        </div>
        """

    def generate_tips(self) -> str:
        """生成装修小贴士"""
        tips = [
            ("验收标准", "装修完成后，务必对照设计图纸逐一验收，重点检查水电隐蔽工程、防水层、瓷砖空鼓等。"),
            ("环保材料", "选择E0级或以上环保标准的建材，装修后至少通风散味30天再入住。"),
            ("保修期", "签订正规装修合同，明确保修期限（基础工程2年、防水5年），保留好相关票据。"),
            ("增项控制", "施工前确认设计方案，避免中途大幅改动导致增项费用超出预算。"),
            ("拍照留档", "水电改造完成后拍照留档，方便日后维修和改造。"),
        ]

        tips_html = ""
        for title, content in tips:
            tips_html += f"""
            <div class="tip-box">
                <strong>{title}：</strong>{escape(content)}
            </div>
            """

        return f"""
        <div class="section">
            <h2>八、装修小贴士</h2>
            {tips_html}

            <div class="warning-box" style="margin-top:30px;">
                <strong>温馨提示：</strong>本方案仅供参考，实际施工中可能因现场情况、材料供应等因素略有调整。
                建议业主与设计师、施工方保持密切沟通，确保装修效果达到预期。
            </div>
        </div>
        """

    def generate_pdf(
        self,
        project_name: str,
        total_area: float,
        plans: List[RenovationPlan],
        output_filename: str = "renovation_plan.pdf"
    ) -> str:
        """
        生成完整的PDF文档

        Args:
            project_name: 项目名称
            total_area: 装修面积
            plans: 装修方案列表
            output_filename: 输出文件名

        Returns:
            str: 输出文件路径
        """
        # 构建HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>户型装修设计方案 - {escape(project_name)}</title>
            {self.css_styles}
        </head>
        <body>
            {self.generate_cover_page(project_name, total_area, len(plans))}
            {self.generate_toc_page()}
            {self.generate_plan_comparison(plans)}

            # 生成各方案详情
            {''.join(self.generate_plan_detail(plan) for plan in plans)}

            # 预算费用表
            {self.generate_budget_table(plans)}

            # 时间进度表
            {self.generate_schedule_table(plans)}

            # 装修小贴士
            {self.generate_tips()}

            <div class="page-number">
                <p>第 # 页 / 共 # 页</p>
            </div>
        </body>
        </html>
        """

        # 保存HTML文件
        html_path = self.output_dir / "renovation_plan.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(html_path)


def main():
    """主函数 - 示例用法"""
    # 创建示例数据
    plans = [
        RenovationPlan(
            plan_name="经济实用型",
            plan_type="economy",
            total_area=100,
            style="现代简约",
            concept="注重实用性，控制预算，强调收纳功能",
            base_cost=40000,
            main_material_cost=50000,
            furniture_cost=30000,
            appliance_cost=25000,
            soft_decor_cost=8000,
            other_cost=5000,
            total_cost=158000,
            total_days=45,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        ),
        RenovationPlan(
            plan_name="品质舒适型",
            plan_type="standard",
            total_area=100,
            style="现代轻奢",
            concept="注重品质与舒适度，材料升级，空间优化",
            base_cost=70000,
            main_material_cost=80000,
            furniture_cost=50000,
            appliance_cost=35000,
            soft_decor_cost=12000,
            other_cost=8000,
            total_cost=255000,
            total_days=55,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=55)).strftime("%Y-%m-%d")
        ),
        RenovationPlan(
            plan_name="高端豪华型",
            plan_type="luxury",
            total_area=100,
            style="新中式/轻奢",
            concept="高端材料，全屋定制，智能家居，品质生活",
            base_cost=120000,
            main_material_cost=150000,
            furniture_cost=100000,
            appliance_cost=60000,
            soft_decor_cost=25000,
            other_cost=15000,
            total_cost=470000,
            total_days=70,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=70)).strftime("%Y-%m-%d")
        ),
    ]

    # 生成PDF
    generator = PDFGenerator(output_dir="./output")
    html_path = generator.generate_pdf(
        project_name="某小区户型装修设计",
        total_area=100,
        plans=plans
    )

    print(f"PDF文档HTML已生成：{html_path}")
    print("提示：使用浏览器打开HTML文件，选择打印为PDF即可获得PDF文档")


if __name__ == "__main__":
    main()
