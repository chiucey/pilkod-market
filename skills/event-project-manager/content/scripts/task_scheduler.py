#!/usr/bin/env python3
"""
活动任务倒排生成器 - 智企大型线下活动专用版
基于智企大型线下活动SOP
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

# 智企大型线下活动SOP模板
EVENT_TEMPLATES = {
    "智企大型线下活动": {
        "phases": [
            {
                "name": "【立项阶段】活动前2-3个月",
                "start_week": 12,
                "tasks": [
                    {"name": "活动立项-确定活动方案（目的、主题、时间、规模、预算、量化指标）", "days_before": 84, "owner": "项目组", "priority": "高"},
                    {"name": "活动立项-填写立项表，走立项流程", "days_before": 80, "owner": "整体统筹", "priority": "高"},
                ]
            },
            {
                "name": "【筹备阶段-内部&供应商】活动前2个月",
                "start_week": 8,
                "tasks": [
                    {"name": "预定场地（会场、晚宴、茶歇、餐饮住宿方案，签订协议）", "days_before": 56, "owner": "项目组", "priority": "高"},
                    {"name": "议程准备（活动现场流程、圆桌讨论话题与大纲、现场问答设计）", "days_before": 56, "owner": "会务组&嘉宾", "priority": "高"},
                    {"name": "视觉系统-确定会议主视觉，视觉任务拆解", "days_before": 56, "owner": "项目组", "priority": "高"},
                    {"name": "外宣物料（会议资料海报/PPT/推文、嘉宾邀请函、商务合作方案、出行方案、会场服务）", "days_before": 42, "owner": "项目组", "priority": "高"},
                    {"name": "会场物料（会议伴手礼、纸笔基础套件、会议资料印刷品、奖杯奖牌）", "days_before": 14, "owner": "项目组", "priority": "高"},
                    {"name": "公关公司-选定合作公关公司，确定负责会场搭建和执行方案", "days_before": 56, "owner": "项目组", "priority": "高"},
                    {"name": "直播方案-如需同步直播，确定直播流程和准备事项", "days_before": 28, "owner": "项目组", "priority": "中"},
                ]
            },
            {
                "name": "【会议邀请】活动前1-2个月",
                "start_week": 6,
                "tasks": [
                    {"name": "嘉宾邀请-启动嘉宾邀请（含主持人），并确认最后活动议程", "days_before": 56, "owner": "项目组&高层", "priority": "高"},
                    {"name": "参会邀请-确定邀请方案，向目标参会群体正式邀约", "days_before": 42, "owner": "全体成员", "priority": "高"},
                    {"name": "媒体邀请-邀请行业媒体、垂直媒体，确定活动到场媒体", "days_before": 42, "owner": "项目组", "priority": "中"},
                    {"name": "招商邀请-邀请相关企业商务合作（演讲、展位、礼品等）", "days_before": 42, "owner": "项目组", "priority": "中"},
                ]
            },
            {
                "name": "【传播预热】活动前1-2个月",
                "start_week": 6,
                "tasks": [
                    {"name": "整体传播方案-输出整体传播方案", "days_before": 42, "owner": "项目组", "priority": "高"},
                    {"name": "内部预热-海报、推文、视频、EDM等传播内容", "days_before": 28, "owner": "项目组", "priority": "高"},
                    {"name": "外部媒体预热-确定媒体合作方案，前期媒体传播", "days_before": 28, "owner": "项目组&媒体", "priority": "中"},
                    {"name": "社群传播-通过自媒体、短视频、朋友圈、垂直社群、合作协会、合作公众号等进行预热与报名", "days_before": 28, "owner": "全体成员", "priority": "高"},
                ]
            },
            {
                "name": "【会议接待】活动前2周",
                "start_week": 2,
                "tasks": [
                    {"name": "会议速记/翻译/摄影/直播-确定会议速记人员，同传翻译及设备，内外部摄影/直播工作", "days_before": 14, "owner": "内部&第三方", "priority": "高"},
                    {"name": "会场协调-确定场控、会场内部协调人员、会场外展位协调人员，明确分工", "days_before": 14, "owner": "项目组", "priority": "高"},
                    {"name": "演讲嘉宾接待-分配演讲嘉宾前期对接（含合作伙伴）、现场接待与后续相关财务工作", "days_before": 14, "owner": "项目组&高层", "priority": "高"},
                    {"name": "媒体接待-确定媒体统筹，负责会议传播、会议专访工作及后期车马费用结算", "days_before": 14, "owner": "项目组", "priority": "中"},
                ]
            },
            {
                "name": "【执行阶段-会场布置】活动前1天/当天",
                "start_week": 0,
                "tasks": [
                    {"name": "场地搭建-与公关公司、酒店执行搭建工作", "days_before": 1, "owner": "项目组", "priority": "高"},
                    {"name": "会场布置-名卡&伴手礼&会议资料&桌椅布场，展位搭建布置", "days_before": 1, "owner": "项目组", "priority": "高"},
                    {"name": "会场彩排-彩排走流程，检查主视觉、音频设备、开场音乐、视频、演讲PPT及现场道具", "days_before": 1, "owner": "项目组", "priority": "高"},
                ]
            },
            {
                "name": "【执行阶段-嘉宾接待】活动前1天/当天",
                "start_week": 0,
                "tasks": [
                    {"name": "演讲嘉宾接待-场外沟通、熟悉，引导入座；安排休息室、化妆室、餐饮", "days_before": 1, "owner": "项目组&高层", "priority": "高"},
                    {"name": "参会嘉宾接待-签到，会议袋分发（餐饮安排），茶歇引导等", "days_before": 0, "owner": "全体成员", "priority": "高"},
                ]
            },
            {
                "name": "【执行阶段-媒体传播】活动当天",
                "start_week": 0,
                "tasks": [
                    {"name": "媒体传播-媒体接待，专访安排，通稿、嘉宾主题稿件分发", "days_before": 0, "owner": "项目组", "priority": "中"},
                    {"name": "金句/嘉宾稿件-金句速记/海报制作/快讯稿件/视频切片", "days_before": 0, "owner": "项目组", "priority": "高"},
                    {"name": "晚宴安排-晚宴议程，节目、互动，商务交流", "days_before": 0, "owner": "项目组&销售部", "priority": "中"},
                    {"name": "场地收尾-活动后整理场地/收尾", "days_before": 0, "owner": "项目组", "priority": "高"},
                ]
            },
            {
                "name": "【后链路运营】会后1周-1个月",
                "start_week": -1,
                "tasks": [
                    {"name": "文章图片传播-通稿/活动回顾信息图/核心概念解读稿/产品深度解读稿/记者撰稿/专访等", "days_before": -2, "owner": "项目组&媒体", "priority": "高"},
                    {"name": "视频传播-会议回顾/演讲切片", "days_before": -3, "owner": "项目组", "priority": "高"},
                    {"name": "舆情管理-处理负面舆情，引导正向的舆情与评价", "days_before": -7, "owner": "项目组", "priority": "中"},
                    {"name": "线索入库-统计整理各个渠道报名、留资线索，线索入库", "days_before": -7, "owner": "项目组&业务", "priority": "高"},
                    {"name": "清洗转化-SDR线索清洗，成单转化", "days_before": -7, "owner": "销售部", "priority": "高"},
                    {"name": "会后调研-会后需求与满意度调研", "days_before": -7, "owner": "项目组&参会人员", "priority": "中"},
                    {"name": "效果评估-品牌传播量、质量、曝光量、阅读量、线索量、转化率、参会群体质量", "days_before": -30, "owner": "项目组", "priority": "高"},
                    {"name": "财务结算-完善财务记录：尾款结算，发票等等，核对预算", "days_before": -7, "owner": "项目组", "priority": "高"},
                    {"name": "总结复盘-会议总结，复盘", "days_before": -14, "owner": "项目组", "priority": "高"},
                ]
            },
        ]
    },
    "线上直播": {
        "phases": [
            {"name": "【第3周】策划期", "start_week": 3, "tasks": [
                {"name": "确定直播主题与讲师", "days_before": 21, "owner": "PMM", "priority": "高"},
                {"name": "确定直播平台和技术方案", "days_before": 20, "owner": "运营", "priority": "高"},
                {"name": "准备内容诱饵（白皮书/福利）", "days_before": 18, "owner": "产品", "priority": "中"},
                {"name": "启动主视觉设计", "days_before": 18, "owner": "设计", "priority": "高"},
                {"name": "确定官方外宣渠道方案", "days_before": 18, "owner": "PMM", "priority": "中"},
                {"name": "启动数据挖掘邀约", "days_before": 18, "owner": "运营", "priority": "中"},
                {"name": "准备销售定邀话术", "days_before": 18, "owner": "销售", "priority": "中"},
            ]},
            {"name": "【第2周】预热期", "start_week": 2, "tasks": [
                {"name": "发布预热海报（倒计时D-14）", "days_before": 14, "owner": "设计+PMM", "priority": "高"},
                {"name": "启动报名通道", "days_before": 14, "owner": "运营", "priority": "高"},
                {"name": "建立活动快闪群", "days_before": 14, "owner": "运营", "priority": "中"},
                {"name": "发布公众号推文预告", "days_before": 12, "owner": "PMM", "priority": "高"},
                {"name": "启动销售定邀", "days_before": 12, "owner": "销售", "priority": "高"},
                {"name": "准备朋友圈宣传话术", "days_before": 10, "owner": "PMM", "priority": "中"},
                {"name": "制作嘉宾KO海报", "days_before": 10, "owner": "设计", "priority": "中"},
            ]},
            {"name": "【第1周】筹备期", "start_week": 1, "tasks": [
                {"name": "发布倒计时海报（D-7）", "days_before": 7, "owner": "设计", "priority": "高"},
                {"name": "收集并审核嘉宾演讲PPT", "days_before": 7, "owner": "PMM", "priority": "高"},
                {"name": "进行直播技术测试", "days_before": 6, "owner": "技术", "priority": "高"},
                {"name": "准备直播运营脚本", "days_before": 5, "owner": "运营", "priority": "高"},
                {"name": "发布倒计时海报（D-3）", "days_before": 3, "owner": "设计", "priority": "高"},
                {"name": "准备主持词和互动问题", "days_before": 3, "owner": "PMM", "priority": "高"},
                {"name": "制作调研问卷", "days_before": 3, "owner": "运营", "priority": "中"},
                {"name": "配置企微名片弹窗", "days_before": 3, "owner": "运营", "priority": "中"},
                {"name": "准备嘉宾金句海报", "days_before": 3, "owner": "设计", "priority": "中"},
                {"name": "最终彩排", "days_before": 2, "owner": "全员", "priority": "高"},
            ]},
            {"name": "【活动当天】执行", "start_week": 0, "tasks": [
                {"name": "发布倒计时海报（D-1）", "days_before": 1, "owner": "设计", "priority": "高"},
                {"name": "开播前1小时短信通知", "days_before": 1, "owner": "运营", "priority": "高"},
                {"name": "开播前30分钟社群预热", "days_before": 0, "owner": "运营", "priority": "高"},
                {"name": "开播前5分钟企微朋友圈和1V1通知", "days_before": 0, "owner": "运营", "priority": "高"},
                {"name": "直播中互动引导", "days_before": 0, "owner": "主持人", "priority": "高"},
                {"name": "评论区管理", "days_before": 0, "owner": "运营", "priority": "中"},
                {"name": "问卷发放", "days_before": 0, "owner": "运营", "priority": "中"},
            ]},
            {"name": "【活动后】复盘", "start_week": -1, "tasks": [
                {"name": "直播数据统计复盘", "days_before": -1, "owner": "运营", "priority": "高"},
                {"name": "直播回放剪辑和上架", "days_before": -2, "owner": "剪辑", "priority": "高"},
                {"name": "通知观众回放上架", "days_before": -2, "owner": "运营", "priority": "中"},
                {"name": "发布公众号回顾文章", "days_before": -3, "owner": "PMM", "priority": "中"},
                {"name": "SDR线索清洗和分配", "days_before": -5, "owner": "销售", "priority": "高"},
                {"name": "活动复盘会议", "days_before": -7, "owner": "PMM", "priority": "高"},
            ]},
        ]
    },
    "线下沙龙": {
        "phases": [
            {"name": "【第3周】策划", "start_week": 3, "tasks": [
                {"name": "确定主题与场地", "days_before": 21, "owner": "PMM", "priority": "高"},
                {"name": "邀请讲师/嘉宾", "days_before": 20, "owner": "PMM", "priority": "高"},
                {"name": "启动报名", "days_before": 18, "owner": "运营", "priority": "高"},
            ]},
            {"name": "【第2周】筹备", "start_week": 2, "tasks": [
                {"name": "物料设计完成", "days_before": 14, "owner": "设计", "priority": "高"},
                {"name": "物料制作", "days_before": 10, "owner": "采购", "priority": "高"},
                {"name": "餐饮安排", "days_before": 7, "owner": "行政", "priority": "中"},
            ]},
            {"name": "【第1周】执行准备", "start_week": 1, "tasks": [
                {"name": "最终人数确认", "days_before": 5, "owner": "运营", "priority": "高"},
                {"name": "物料到位", "days_before": 3, "owner": "采购", "priority": "高"},
                {"name": "现场布置", "days_before": 1, "owner": "运营", "priority": "高"},
            ]},
        ]
    },
}

def generate_weekly_schedule(event_type: str, event_date: str, event_name: str) -> Dict:
    """生成按周倒排的任务清单（带具体日期）"""
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    today = datetime.now()
    
    template = EVENT_TEMPLATES.get(event_type, EVENT_TEMPLATES["智企大型线下活动"])
    
    schedule = {
        "event_name": event_name,
        "event_type": event_type,
        "event_date": event_date,
        "today": today.strftime("%Y-%m-%d"),
        "weeks": []
    }
    
    for phase in template["phases"]:
        week_tasks = {
            "phase_name": phase["name"],
            "tasks": []
        }
        
        for task in phase["tasks"]:
            deadline = event_dt - timedelta(days=task["days_before"])
            week_tasks["tasks"].append({
                "name": task["name"],
                "deadline": deadline.strftime("%Y-%m-%d"),
                "owner": task["owner"],
                "priority": task["priority"],
                "status": "未开始",
                "days_to_deadline": (deadline - today).days
            })
        
        if week_tasks["tasks"]:
            first_task = week_tasks["tasks"][0]
            last_task = week_tasks["tasks"][-1]
            week_tasks["start_date"] = first_task["deadline"]
            week_tasks["end_date"] = last_task["deadline"]
            schedule["weeks"].append(week_tasks)
    
    return schedule

def generate_preview_schedule(event_type: str, event_date: str, event_name: str) -> str:
    """生成倒排表预览"""
    schedule = generate_weekly_schedule(event_type, event_date, event_name)
    
    output = []
    output.append(f"📅 活动名称：{event_name}")
    output.append(f"📍 活动类型：{event_type}")
    output.append(f"🎯 活动日期：{event_date}")
    output.append(f"📆 当前日期：{schedule['today']}")
    output.append("")
    output.append("=" * 60)
    output.append("📋 任务倒排预览（基于智企大型线下活动SOP）")
    output.append("=" * 60)
    output.append("")
    
    for week in schedule["weeks"]:
        output.append(f"{week['phase_name']}")
        output.append(f"时间范围：{week['start_date']} ~ {week['end_date']}")
        output.append("-" * 40)
        
        for task in week["tasks"]:
            output.append(f"  • {task['name']}")
            output.append(f"    截止日期：{task['deadline']} | 负责人：{task['owner']}")
        
        output.append("")
    
    return "\n".join(output)

def get_daily_report(event_name: str) -> str:
    """生成每日进度报告"""
    data = load_event_data(event_name)
    if not data:
        return f"❌ 未找到活动 '{event_name}'"
    
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    output = []
    output.append(f"📅 {today_str} 活动进度提醒")
    output.append(f"🎯 活动：{data['event_name']}")
    output.append(f"📍 活动日期：{data['event_date']}")
    output.append("")
    
    # 今日任务
    today_tasks = [t for t in data["tasks"] if t["deadline"] == today_str and t["status"] not in ["已完成", "已取消"]]
    if today_tasks:
        output.append("🔔 今日待完成任务：")
        for task in today_tasks:
            output.append(f"  ☐ {task['name']} | 负责人：{task['owner']} | 优先级：{task['priority']}")
        output.append("")
    
    # 逾期任务
    overdue = [t for t in data["tasks"] if t["deadline"] < today_str and t["status"] not in ["已完成", "已取消"]]
    if overdue:
        output.append("⚠️ 已逾期任务（需尽快处理）：")
        for task in overdue:
            output.append(f"  🔴 {task['name']} | 截止：{task['deadline']} | 负责人：{task['owner']}")
        output.append("")
    
    # 即将到期（3天内）
    upcoming = []
    for task in data["tasks"]:
        if task["status"] in ["已完成", "已取消"]:
            continue
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
        days_left = (deadline - today).days
        if 0 < days_left <= 3:
            task["days_left"] = days_left
            upcoming.append(task)
    
    if upcoming:
        output.append("⏰ 即将到期任务（3天内）：")
        for task in upcoming:
            output.append(f"  🟡 {task['name']} | 还剩 {task['days_left']} 天 | 负责人：{task['owner']}")
        output.append("")
    
    # 整体进度
    total = len([t for t in data["tasks"] if t["status"] != "已取消"])
    completed = len([t for t in data["tasks"] if t["status"] == "已完成"])
    progress = (completed / total * 100) if total > 0 else 0
    
    output.append(f"📊 整体进度：{completed}/{total} 任务完成 ({progress:.1f}%)")
    
    return "\n".join(output)

def save_event_data(event_name: str, event_type: str, event_date: str, tasks: List[Dict], enable_daily_reminder: bool = True):
    """保存活动数据到本地"""
    events_dir = os.path.expanduser("~/.openclaw/workspace/events")
    os.makedirs(events_dir, exist_ok=True)
    
    data = {
        "event_name": event_name,
        "event_type": event_type,
        "event_date": event_date,
        "tasks": tasks,
        "enable_daily_reminder": enable_daily_reminder,
        "reminder_time": "12:00",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    filename = f"{event_name.replace(' ', '_')}.json"
    filepath = os.path.join(events_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_event_data(event_name: str) -> Dict:
    """加载活动数据"""
    events_dir = os.path.expanduser("~/.openclaw/workspace/events")
    filename = f"{event_name.replace(' ', '_')}.json"
    filepath = os.path.join(events_dir, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_task_status(event_name: str, task_name: str, status: str):
    """更新任务状态"""
    data = load_event_data(event_name)
    if not data:
        return False
    
    for task in data["tasks"]:
        if task["name"] == task_name:
            task["status"] = status
            break
    
    events_dir = os.path.expanduser("~/.openclaw/workspace/events")
    filename = f"{event_name.replace(' ', '_')}.json"
    filepath = os.path.join(events_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return True

def check_overdue_tasks(tasks: List[Dict]) -> List[Dict]:
    """检查已逾期任务"""
    today = datetime.now().strftime("%Y-%m-%d")
    overdue = [t for t in tasks if t["deadline"] < today and t["status"] not in ["已完成", "已取消"]]
    return overdue

def check_upcoming_tasks(tasks: List[Dict], days: int = 7) -> List[Dict]:
    """检查即将到期的任务"""
    today = datetime.now()
    upcoming = []
    for task in tasks:
        if task["status"] in ["已完成", "已取消"]:
            continue
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
        days_left = (deadline - today).days
        if 0 <= days_left <= days:
            task["days_left"] = days_left
            upcoming.append(task)
    return upcoming

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python task_scheduler.py <command> [args...]")
        print("命令:")
        print("  preview <event_type> <event_date> <event_name>   - 生成倒排表预览")
        print("  generate <event_type> <event_date> <event_name>  - 确认并生成任务倒排表")
        print("  daily <event_name>                               - 生成每日进度报告")
        print("  check <event_name>                               - 检查任务状态")
        print("  update <event_name> <task_name> <status>         - 更新任务状态")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "preview" and len(sys.argv) >= 5:
        event_type = sys.argv[2]
        event_date = sys.argv[3]
        event_name = sys.argv[4]
        
        preview = generate_preview_schedule(event_type, event_date, event_name)
        print(preview)
    
    elif command == "generate" and len(sys.argv) >= 5:
        event_type = sys.argv[2]
        event_date = sys.argv[3]
        event_name = sys.argv[4]
        
        schedule = generate_weekly_schedule(event_type, event_date, event_name)
        
        # 扁平化任务列表
        all_tasks = []
        for week in schedule["weeks"]:
            for task in week["tasks"]:
                all_tasks.append(task)
        
        filepath = save_event_data(event_name, event_type, event_date, all_tasks)
        
        print(f"✅ 已确认并生成活动 '{event_name}' 的任务倒排表")
        print(f"📁 数据保存至: {filepath}")
        print(f"\n📅 每日12:00将自动推送进度提醒")
        print(f"\n任务清单（共 {len(all_tasks)} 项）:")
        print("-" * 80)
        for task in all_tasks:
            print(f"[{task['deadline']}] {task['name']} | {task['owner']} | {task['priority']}")
    
    elif command == "daily" and len(sys.argv) >= 3:
        event_name = sys.argv[2]
        report = get_daily_report(event_name)
        print(report)
    
    elif command == "check" and len(sys.argv) >= 3:
        event_name = sys.argv[2]
        data = load_event_data(event_name)
        
        if not data:
            print(f"❌ 未找到活动 '{event_name}'")
            sys.exit(1)
        
        print(f"📋 活动: {data['event_name']}")
        print(f"📅 活动日期: {data['event_date']}")
        print(f"📊 任务总数: {len(data['tasks'])}")
        
        overdue = check_overdue_tasks(data['tasks'])
        upcoming = check_upcoming_tasks(data['tasks'])
        
        if overdue:
            print(f"\n⚠️ 已逾期任务 ({len(overdue)} 项):")
            for task in overdue:
                print(f"  - {task['name']} (截止: {task['deadline']})")
        
        if upcoming:
            print(f"\n⏰ 即将到期任务 ({len(upcoming)} 项):")
            for task in upcoming:
                print(f"  - {task['name']} (还剩 {task['days_left']} 天)")
        
        if not overdue and not upcoming:
            print("\n✅ 暂无紧急任务")
    
    elif command == "update" and len(sys.argv) >= 5:
        event_name = sys.argv[2]
        task_name = sys.argv[3]
        status = sys.argv[4]
        
        if update_task_status(event_name, task_name, status):
            print(f"✅ 已更新任务 '{task_name}' 状态为 '{status}'")
        else:
            print(f"❌ 更新失败")
    
    else:
        print("参数错误，请检查用法")
