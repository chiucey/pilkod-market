#!/usr/bin/env python3
"""
Blood Glucose Tracker
血糖监测追踪器 - 用于记录、查询和管理血糖数据
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class GlucoseRecord:
    """血糖记录数据模型"""
    id: str
    date: str
    time: str
    value: float
    type: str  # 'fasting' or 'postprandial'
    note: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def get_status(self) -> str:
        """根据血糖值和类型判断状态"""
        if self.type == 'fasting':
            if self.value < 3.9:
                return "偏低"
            elif self.value <= 6.1:
                return "正常"
            elif self.value <= 7.0:
                return "偏高"
            else:
                return "过高"
        else:  # postprandial
            if self.value < 7.8:
                return "正常"
            elif self.value <= 11.1:
                return "偏高"
            else:
                return "过高"

    def get_type_display(self) -> str:
        """获取类型的中文显示"""
        return "餐前" if self.type == "fasting" else "餐后"


class GlucoseDataStore:
    """血糖数据存储器"""

    def __init__(self, data_file: str = "data/glucose_records.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """确保数据文件存在"""
        if not self.data_file.exists():
            self._save_data({"records": []})

    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"records": []}

    def _save_data(self, data: Dict):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_record(self, record: GlucoseRecord) -> bool:
        """添加新记录"""
        try:
            data = self._load_data()
            data["records"].append(asdict(record))
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error saving record: {e}")
            return False

    def get_records(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        record_type: Optional[str] = None,
        sort_order: str = "desc"
    ) -> List[GlucoseRecord]:
        """获取记录列表"""
        data = self._load_data()
        records = []

        for r in data.get("records", []):
            # 日期过滤
            if start_date and r["date"] < start_date:
                continue
            if end_date and r["date"] > end_date:
                continue

            # 类型过滤
            if record_type and r["type"] != record_type:
                continue

            records.append(GlucoseRecord(**r))

        # 排序
        records.sort(
            key=lambda x: (x.date, x.time),
            reverse=(sort_order == "desc")
        )

        return records

    def get_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """获取统计数据"""
        records = self.get_records(start_date, end_date)

        if not records:
            return {
                "count": 0,
                "average": 0,
                "max": 0,
                "min": 0,
                "fasting_count": 0,
                "postprandial_count": 0,
                "normal_count": 0,
                "high_count": 0,
                "low_count": 0
            }

        values = [r.value for r in records]
        fasting_records = [r for r in records if r.type == "fasting"]
        postprandial_records = [r for r in records if r.type == "postprandial"]

        return {
            "count": len(records),
            "average": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "fasting_count": len(fasting_records),
            "postprandial_count": len(postprandial_records),
            "fasting_normal": len([r for r in fasting_records if r.get_status() == "正常"]),
            "postprandial_normal": len([r for r in postprandial_records if r.get_status() == "正常"]),
            "normal_count": len([r for r in records if r.get_status() == "正常"]),
            "high_count": len([r for r in records if r.get_status() in ["偏高", "过高"]]),
            "low_count": len([r for r in records if r.get_status() == "偏低"]),
            "abnormal_records": [r for r in records if r.get_status() in ["偏高", "过高", "偏低"]]
        }


class GlucoseTracker:
    """血糖追踪器主类"""

    def __init__(self, data_file: str = "data/glucose_records.json"):
        self.store = GlucoseDataStore(data_file)

    def record_glucose(
        self,
        value: float,
        record_type: str = "fasting",
        note: str = "",
        date: Optional[str] = None,
        time: Optional[str] = None
    ) -> Tuple[bool, GlucoseRecord]:
        """记录血糖"""
        # 验证血糖值
        if not 0.1 <= value <= 50.0:
            raise ValueError("血糖值必须在 0.1 - 50.0 mmol/L 之间")

        # 标准化类型
        if record_type in ["餐前", "空腹", "fasting", "before"]:
            record_type = "fasting"
        else:
            record_type = "postprandial"

        # 获取当前日期时间
        now = datetime.now()
        record_date = date or now.strftime("%Y-%m-%d")
        record_time = time or now.strftime("%H:%M")

        # 创建记录
        record = GlucoseRecord(
            id=str(uuid.uuid4()),
            date=record_date,
            time=record_time,
            value=value,
            type=record_type,
            note=note
        )

        # 保存
        success = self.store.add_record(record)

        return success, record

    def view_records(
        self,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        record_type: Optional[str] = None,
        sort_order: str = "desc"
    ) -> List[GlucoseRecord]:
        """查看记录"""
        records = self.store.get_records(
            start_date=start_date,
            end_date=end_date,
            record_type=record_type,
            sort_order=sort_order
        )

        if limit:
            records = records[:limit]

        return records

    def get_report(
        self,
        days: int = 7,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """获取统计报告"""
        if not start_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
            start_date = start_dt.strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        stats = self.store.get_statistics(start_date, end_date)
        stats["start_date"] = start_date
        stats["end_date"] = end_date
        stats["days"] = days

        return stats


def format_record_display(record: GlucoseRecord) -> str:
    """格式化单条记录显示"""
    status_emoji = {
        "正常": "✅",
        "偏低": "⚠️",
        "偏高": "⚠️",
        "过高": "🚨"
    }

    emoji = status_emoji.get(record.get_status(), "")
    status = record.get_status()

    return f"""| {record.date} | {record.time} | {record.value:.1f} | {record.get_type_display()} | {emoji} {status} |"""


def format_records_table(records: List[GlucoseRecord], title: str = "血糖记录") -> str:
    """格式化记录列表为表格"""
    if not records:
        return f"""
📋 暂无血糖记录

💡 提示：
开始记录您的血糖数据，关注健康每一天！
使用指令："记录血糖 [数值]"
"""

    table_header = """| 日期       | 时间  | 血糖值  | 类型 | 状态      |
|------------|-------|---------|------|-----------|
"""
    table_rows = "".join(format_record_display(r) for r in records)

    return f"""
📊 {title}（共 {len(records)} 条）

{table_header}
{table_rows}
"""


def format_statistics_report(stats: Dict) -> str:
    """格式化统计报告"""
    if stats["count"] == 0:
        return """
📈 血糖统计报告

暂无数据记录
"""

    # 获取异常记录
    abnormal = stats.get("abnormal_records", [])
    abnormal_str = ""
    if abnormal:
        abnormal_str = "\n⚠️ 异常提醒：\n"
        for r in abnormal[:3]:  # 只显示前3条
            status_msg = "偏高" if r.get_status() in ["偏高", "过高"] else "偏低"
            abnormal_str += f"• {r.date} {r.time} {r.get_type_display()}血糖{status_msg}（{r.value:.1f} mmol/L）\n"
            if r.note:
                abnormal_str += f"  备注：{r.note}\n"

    return f"""
📈 血糖统计报告（{stats['start_date']} 至 {stats['end_date']}）

📊 基本统计：
• 测量次数：{stats['count']} 次
• 平均值：{stats['average']:.1f} mmol/L
• 最高值：{stats['max']:.1f} mmol/L
• 最低值：{stats['min']:.1f} mmol/L

📋 分类统计：
• 餐前测量：{stats['fasting_count']} 次（正常 {stats.get('fasting_normal', 0)} 次）
• 餐后测量：{stats['postprandial_count']} 次（正常 {stats.get('postprandial_normal', 0)} 次）

📌 状态分布：
• 正常：{stats['normal_count']} 次
• 异常：{stats['high_count'] + stats['low_count']} 次

{abnormal_str}
💡 建议：
{_get_suggestion(stats)}
"""


def _get_suggestion(stats: Dict) -> str:
    """根据统计数据给出建议"""
    if stats["count"] == 0:
        return "开始记录您的血糖数据吧！"

    high_ratio = (stats["high_count"] + stats["low_count"]) / stats["count"]

    if high_ratio > 0.5:
        return "近期异常值较多，建议咨询医生调整方案"
    elif stats["average"] > 7.0:
        return "平均血糖偏高，请注意饮食控制和适量运动"
    elif stats["average"] < 4.0:
        return "平均血糖偏低，请注意是否有低血糖症状"
    else:
        return "血糖控制良好继续保持！规律饮食，适量运动"


def main():
    """演示函数"""
    tracker = GlucoseTracker()

    # 演示记录
    print("=== 演示：记录血糖 ===")

    # 记录几条测试数据
    test_records = [
        (5.6, "fasting", "空腹，早起测量"),
        (7.2, "postprandial", "午餐后2小时"),
        (5.8, "fasting", "空腹，睡眠良好"),
        (8.5, "postprandial", "晚餐后2小时，吃了较多主食"),
        (6.2, "fasting", "空腹，略有疲惫感"),
    ]

    for value, rtype, note in test_records:
        success, record = tracker.record_glucose(value, rtype, note)
        if success:
            print(f"✅ 已记录：{record.value} mmol/L ({record.get_type_display()})")

    print()

    # 演示查看记录
    print("=== 演示：查看记录 ===")
    records = tracker.view_records(limit=5)
    print(format_records_table(records))

    # 演示统计报告
    print("=== 演示：统计报告 ===")
    stats = tracker.get_report(days=30)
    print(format_statistics_report(stats))


if __name__ == "__main__":
    main()
