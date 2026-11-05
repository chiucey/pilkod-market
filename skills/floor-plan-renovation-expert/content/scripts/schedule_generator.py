#!/usr/bin/env python3
"""
户型图装修时间进度表生成脚本
功能：根据装修方案生成详细的时间进度表，包含甘特图数据
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class ScheduleTask:
    """进度任务"""
    task_id: str                 # 任务ID
    task_name: str               # 任务名称
    phase: str                   # 阶段
    start_day: int              # 开始天数（相对于开工日期）
    duration: int                # 持续天数
    end_day: int                # 结束天数
    dependencies: List[str]     # 前置任务ID列表
    responsible: str             # 负责人
    notes: str = ""              # 备注


@dataclass
class SchedulePhase:
    """装修阶段"""
    phase_name: str              # 阶段名称
    phase_order: int             # 阶段顺序
    start_day: int              # 开始天数
    end_day: int               # 结束天数
    total_days: int             # 总天数
    tasks: List[ScheduleTask]   # 任务列表


@dataclass
class SchedulePlan:
    """装修进度方案"""
    plan_name: str                          # 方案名称
    plan_type: str                          # 方案类型
    total_area: float                       # 装修面积
    total_days: int                         # 总工期
    start_date: str                        # 开工日期
    phases: List[SchedulePhase] = field(default_factory=list)  # 阶段列表
    tasks: List[ScheduleTask] = field(default_factory=list)     # 所有任务列表

    def get_end_date(self) -> str:
        """计算竣工日期"""
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = start + timedelta(days=self.total_days - 1)
        return end.strftime("%Y-%m-%d")


class ScheduleGenerator:
    """时间进度表生成器"""

    # 阶段工期参考（单位：天）- 经济型/标准型/豪华型
    PHASE_DURATIONS = {
        "design": {"economy": 7, "standard": 10, "luxury": 14},        # 设计阶段
        "demo": {"economy": 3, "standard": 5, "luxury": 7},            # 拆改阶段
        "hydropower": {"economy": 5, "standard": 7, "luxury": 10},   # 水电阶段
        "brickwork": {"economy": 10, "standard": 15, "luxury": 20},   # 泥瓦阶段
        "woodwork": {"economy": 5, "standard": 7, "luxury": 10},      # 木工阶段
        "painting": {"economy": 5, "standard": 7, "luxury": 10},      # 油漆阶段
        "installation": {"economy": 5, "standard": 7, "luxury": 10}, # 安装阶段
        "soft_decor": {"economy": 3, "standard": 5, "luxury": 7},    # 软装阶段
        "cleaning": {"economy": 7, "standard": 10, "luxury": 14}      # 保洁通风
    }

    def __init__(self):
        self.plans: List[SchedulePlan] = []

    def generate_schedule(
        self,
        total_area: float,
        room_count: int = 2,
        bathroom_count: int = 1,
        start_date: str = None,
        include_smart_home: bool = False
    ) -> List[SchedulePlan]:
        """
        生成装修进度计划

        Args:
            total_area: 装修总面积（平方米）
            room_count: 卧室数量
            bathroom_count: 卫生间数量
            start_date: 开工日期（YYYY-MM-DD格式）
            include_smart_home: 是否包含智能家居

        Returns:
            List[SchedulePlan]: 三种进度方案
        """
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")

        plan_types = ["economy", "standard", "luxury"]
        plan_names = ["Economy Practical", "Quality Comfort", "Luxury Premium"]

        for plan_type, plan_name in zip(plan_types, plan_names):
            plan = SchedulePlan(
                plan_name=plan_name,
                plan_type=plan_type,
                total_area=total_area,
                total_days=0,
                start_date=start_date
            )

            # 生成各阶段
            self._generate_design_phase(plan, room_count)
            self._generate_demo_phase(plan)
            self._generate_hydropower_phase(plan, room_count, bathroom_count)
            self._generate_brickwork_phase(plan, bathroom_count)
            self._generate_woodwork_phase(plan, room_count)
            self._generate_painting_phase(plan)
            self._generate_installation_phase(plan, bathroom_count, include_smart_home)
            self._generate_soft_decor_phase(plan, room_count)
            self._generate_cleaning_phase(plan)

            # 计算总工期
            if plan.phases:
                plan.total_days = plan.phases[-1].end_day

            self.plans.append(plan)

        return self.plans

    def _add_phase(self, plan: SchedulePlan, phase_name: str, duration: int, tasks: List[ScheduleTask]) -> int:
        """添加阶段并返回开始天数"""
        if not plan.phases:
            start_day = 1
        else:
            start_day = plan.phases[-1].end_day + 1

        end_day = start_day + duration - 1

        phase = SchedulePhase(
            phase_name=phase_name,
            phase_order=len(plan.phases) + 1,
            start_day=start_day,
            end_day=end_day,
            total_days=duration,
            tasks=tasks
        )
        plan.phases.append(phase)

        # 更新任务的天数
        for task in tasks:
            task.start_day = start_day
            task.end_day = start_day + task.duration - 1
            plan.tasks.append(task)

        return end_day

    def _generate_design_phase(self, plan: SchedulePlan, room_count: int):
        """生成设计阶段"""
        duration = self.PHASE_DURATIONS["design"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_design_01",
                task_name="量房测量",
                phase="design",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="设计师",
                notes="上门测量房屋尺寸"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_design_02",
                task_name="方案设计",
                phase="design",
                start_day=0,
                duration=duration - 2,
                end_day=0,
                dependencies=["design_01"],
                responsible="设计师",
                notes="平面布局、风格定位"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_design_03",
                task_name="施工图设计",
                phase="design",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=["design_02"],
                responsible="设计师",
                notes="水电图、拆改图、立面图"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_design_04",
                task_name="效果图制作",
                phase="design",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=["design_02"],
                responsible="效果图设计师",
                notes="3D效果图制作"
            ),
        ]

        self._add_phase(plan, "设计阶段", duration, tasks)

    def _generate_demo_phase(self, plan: SchedulePlan):
        """生成拆改阶段"""
        duration = self.PHASE_DURATIONS["demo"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_demo_01",
                task_name="主体拆改",
                phase="demo",
                start_day=0,
                duration=duration - 1,
                end_day=0,
                dependencies=[],
                responsible="拆改师傅",
                notes="拆墙、砌墙、铲墙皮"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_demo_02",
                task_name="拆改验收",
                phase="demo",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["demo_01"],
                responsible="监理",
                notes="业主、设计师、监理三方验收"
            ),
        ]

        self._add_phase(plan, "拆改阶段", duration, tasks)

    def _generate_hydropower_phase(self, plan: SchedulePlan, room_count: int, bathroom_count: int):
        """生成水电阶段"""
        duration = self.PHASE_DURATIONS["hydropower"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_hydro_01",
                task_name="水电定位",
                phase="hydropower",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="水电师傅",
                notes="业主到场确认开关插座位置"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_hydro_02",
                task_name="电路改造",
                phase="hydropower",
                start_day=0,
                duration=max(2, duration - 3),
                end_day=0,
                dependencies=["hydro_01"],
                responsible="水电师傅",
                notes="布线、安装底盒"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_hydro_03",
                task_name="水路改造",
                phase="hydropower",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=["hydro_01"],
                responsible="水电师傅",
                notes="水管铺设、热熔连接"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_hydro_04",
                task_name="水电验收",
                phase="hydropower",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["hydro_02", "hydro_03"],
                responsible="监理",
                notes="打压测试、拍照留档"
            ),
        ]

        self._add_phase(plan, "水电阶段", duration, tasks)

    def _generate_brickwork_phase(self, plan: SchedulePlan, bathroom_count: int):
        """生成泥瓦阶段"""
        duration = self.PHASE_DURATIONS["brickwork"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_brick_01",
                task_name="防水工程",
                phase="brickwork",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=[],
                responsible="泥工师傅",
                notes="卫生间、厨房防水涂刷"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_brick_02",
                task_name="闭水试验",
                phase="brickwork",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=["brick_01"],
                responsible="监理",
                notes="48小时闭水测试"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_brick_03",
                task_name="墙地砖铺贴",
                phase="brickwork",
                start_day=0,
                duration=duration - 6,
                end_day=0,
                dependencies=["brick_02"],
                responsible="泥工师傅",
                notes="墙砖、地砖铺贴"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_brick_04",
                task_name="门槛石安装",
                phase="brickwork",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["brick_03"],
                responsible="泥工师傅",
                notes=""
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_brick_05",
                task_name="泥瓦验收",
                phase="brickwork",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["brick_04"],
                responsible="监理",
                notes="空鼓检查、平整度验收"
            ),
        ]

        self._add_phase(plan, "泥瓦阶段", duration, tasks)

    def _generate_woodwork_phase(self, plan: SchedulePlan, room_count: int):
        """生成木工阶段"""
        duration = self.PHASE_DURATIONS["woodwork"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_wood_01",
                task_name="吊顶施工",
                phase="woodwork",
                start_day=0,
                duration=max(3, duration - 5),
                end_day=0,
                dependencies=[],
                responsible="木工师傅",
                notes="客厅、走廊吊顶"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_wood_02",
                task_name="背景墙制作",
                phase="woodwork",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=[],
                responsible="木工师傅",
                notes="电视背景墙、沙发背景墙"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_wood_03",
                task_name="定制柜体安装",
                phase="woodwork",
                start_day=0,
                duration=3,
                end_day=0,
                dependencies=["wood_01"],
                responsible="定制厂家",
                notes="衣柜、鞋柜、橱柜安装"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_wood_04",
                task_name="木工验收",
                phase="woodwork",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["wood_03"],
                responsible="监理",
                notes="结构安全、收口验收"
            ),
        ]

        self._add_phase(plan, "木工阶段", duration, tasks)

    def _generate_painting_phase(self, plan: SchedulePlan):
        """生成油漆阶段"""
        duration = self.PHASE_DURATIONS["painting"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_paint_01",
                task_name="墙面处理",
                phase="painting",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=[],
                responsible="油漆师傅",
                notes="墙面找平、批腻子"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_paint_02",
                task_name="底漆涂刷",
                phase="painting",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["paint_01"],
                responsible="油漆师傅",
                notes="抗碱底漆"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_paint_03",
                task_name="面漆涂刷",
                phase="painting",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=["paint_02"],
                responsible="油漆师傅",
                notes="两遍面漆"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_paint_04",
                task_name="油漆验收",
                phase="painting",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["paint_03"],
                responsible="监理",
                notes="颜色、平整度检查"
            ),
        ]

        self._add_phase(plan, "油漆阶段", duration, tasks)

    def _generate_installation_phase(self, plan: SchedulePlan, bathroom_count: int, include_smart_home: bool):
        """生成安装阶段"""
        duration = self.PHASE_DURATIONS["installation"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_01",
                task_name="地板安装",
                phase="installation",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=[],
                responsible="地板厂家",
                notes="地板铺设"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_02",
                task_name="门安装",
                phase="installation",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["install_01"],
                responsible="门厂家",
                notes="室内门安装"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_03",
                task_name="开关插座安装",
                phase="installation",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="水电师傅",
                notes=""
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_04",
                task_name="灯具安装",
                phase="installation",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["install_03"],
                responsible="水电师傅",
                notes=""
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_05",
                task_name="洁具安装",
                phase="installation",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="卫浴厂家",
                notes="马桶、浴室柜、花洒"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_06",
                task_name="橱柜安装",
                phase="installation",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="橱柜厂家",
                notes="台面、五金安装"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_install_07",
                task_name="家电安装",
                phase="installation",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="家电厂家",
                notes="空调、油烟机等"
            ),
        ]

        if include_smart_home:
            tasks.append(ScheduleTask(
                task_id=f"{plan.plan_type}_install_08",
                task_name="智能家居安装",
                phase="installation",
                start_day=0,
                duration=2,
                end_day=0,
                dependencies=["install_03"],
                responsible="智能家居厂家",
                notes="智能开关、窗帘电机等"
            ))

        self._add_phase(plan, "安装阶段", duration, tasks)

    def _generate_soft_decor_phase(self, plan: SchedulePlan, room_count: int):
        """生成软装阶段"""
        duration = self.PHASE_DURATIONS["soft_decor"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_soft_01",
                task_name="家具进场",
                phase="soft_decor",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="业主",
                notes="床、沙发、餐桌等"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_soft_02",
                task_name="窗帘安装",
                phase="soft_decor",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["soft_01"],
                responsible="窗帘商家",
                notes=""
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_soft_03",
                task_name="装饰品摆放",
                phase="soft_decor",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["soft_02"],
                responsible="业主",
                notes="挂画、绿植、摆件"
            ),
        ]

        self._add_phase(plan, "软装阶段", duration, tasks)

    def _generate_cleaning_phase(self, plan: SchedulePlan):
        """生成保洁通风阶段"""
        duration = self.PHASE_DURATIONS["cleaning"][plan.plan_type]

        tasks = [
            ScheduleTask(
                task_id=f"{plan.plan_type}_clean_01",
                task_name="开荒保洁",
                phase="cleaning",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=[],
                responsible="保洁公司",
                notes="装修垃圾清理、全屋清洁"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_clean_02",
                task_name="通风散味",
                phase="cleaning",
                start_day=0,
                duration=duration - 2,
                end_day=0,
                dependencies=["clean_01"],
                responsible="业主",
                notes="开窗通风、活性炭除甲醛"
            ),
            ScheduleTask(
                task_id=f"{plan.plan_type}_clean_03",
                task_name="竣工验收",
                phase="cleaning",
                start_day=0,
                duration=1,
                end_day=0,
                dependencies=["clean_02"],
                responsible="监理",
                notes="全屋验收、交付业主"
            ),
        ]

        self._add_phase(plan, "保洁通风", duration, tasks)

    def generate_gantt_data(self, plan: SchedulePlan) -> List[Dict]:
        """生成甘特图数据"""
        gantt_items = []
        for phase in plan.phases:
            for task in phase.tasks:
                start_date = datetime.strptime(plan.start_date, "%Y-%m-%d")
                start = start_date + timedelta(days=task.start_day - 1)
                end = start_date + timedelta(days=task.end_day - 1)

                gantt_items.append({
                    "id": task.task_id,
                    "name": task.task_name,
                    "phase": phase.phase_name,
                    "start": start.strftime("%Y-%m-%d"),
                    "end": end.strftime("%Y-%m-%d"),
                    "duration": task.duration,
                    "progress": 100,
                    "responsible": task.responsible,
                    "notes": task.notes
                })
        return gantt_items

    def export_to_json(self, filepath: str):
        """导出为JSON格式"""
        data = []
        for plan in self.plans:
            data.append({
                "plan_name": plan.plan_name,
                "plan_type": plan.plan_type,
                "total_area": plan.total_area,
                "total_days": plan.total_days,
                "start_date": plan.start_date,
                "end_date": plan.get_end_date(),
                "phases": [
                    {
                        "phase_name": phase.phase_name,
                        "start_day": phase.start_day,
                        "end_day": phase.end_day,
                        "total_days": phase.total_days,
                        "tasks": [
                            {
                                "task_id": task.task_id,
                                "task_name": task.task_name,
                                "start_day": task.start_day,
                                "end_day": task.end_day,
                                "duration": task.duration,
                                "responsible": task.responsible,
                                "notes": task.notes
                            }
                            for task in phase.tasks
                        ]
                    }
                    for phase in plan.phases
                ],
                "gantt_data": self.generate_gantt_data(plan)
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_summary(self) -> str:
        """生成进度汇总文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("装修时间进度表")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)

        for plan in self.plans:
            lines.append(f"\n【{plan.plan_name}】")
            lines.append(f"  装修面积：{plan.total_area:.2f} 平方米")
            lines.append(f"  开工日期：{plan.start_date}")
            lines.append(f"  竣工日期：{plan.get_end_date()}")
            lines.append(f"  总工期：{plan.total_days} 天")
            lines.append(f"\n  {'阶段进度':^20} | {'开始'}:{'结束':^8} | {'天数':^4}")
            lines.append(f"  {'-' * 40}")

            for phase in plan.phases:
                start_date = datetime.strptime(plan.start_date, "%Y-%m-%d") + timedelta(days=phase.start_day - 1)
                end_date = datetime.strptime(plan.start_date, "%Y-%m-%d") + timedelta(days=phase.end_day - 1)
                lines.append(
                    f"  {phase.phase_name:<16} | "
                    f"{start_date.strftime('%m/%d')}:{end_date.strftime('%m/%d'):8} | "
                    f"{phase.total_days:>4}天"
                )

        return "\n".join(lines)


def main():
    """主函数 - 示例用法"""
    generator = ScheduleGenerator()

    # 示例：生成100平米两室一厅一卫的进度表
    plans = generator.generate_schedule(
        total_area=100,
        room_count=2,
        bathroom_count=1,
        start_date=datetime.now().strftime("%Y-%m-%d"),
        include_smart_home=False
    )

    # 打印汇总
    print(generator.generate_summary())

    # 导出文件
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    generator.export_to_json(str(output_dir / "schedule_economy_standard_luxury.json"))

    print(f"\n进度表文件已导出到 {output_dir}/")


if __name__ == "__main__":
    main()
