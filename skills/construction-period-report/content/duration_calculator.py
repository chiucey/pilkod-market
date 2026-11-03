"""
工期统计计算模块

基于《优质工期统计表及标准工期统计方法》文档实现工期计算逻辑

数据源：项目明细查询报表（金额单位：元）
- 表头行：第2行（index=1）
- 关键列名：
  - 第一次立项批复完成时间
  - 开工报告完成（填报）时间
  - 割接上线交维（填报）时间
  - 竣工验收完成时间
  - 竣工备案完成时间
  - 决算审计完成时间
  - PMS第一次项目关闭时间
  - 最新立项批复金额

优质工期统计表：
- 建设期要求交维时间：立项批复完成时间 + 274天
- 施工期要求交维时间：开工报告完成时间 + 182天
- 验收控制要求竣工验收时间：割接上线交维时间 + 152天

标准工期统计分析表：
- 按项目类型（月数）计算各阶段要求时间
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json


# ============================================================
# 优质工期统计表 - 常量定义
# ============================================================

# 优质工期天数标准
CONSTRUCTION_PERIOD_DAYS = 274    # 建设期要求交维时间（天）
CONSTRUCTION_PHASE_DAYS = 182      # 施工期要求交维时间（天）
ACCEPTANCE_CONTROL_DAYS = 152      # 验收控制要求竣工验收时间（天）

# 工期管控判定标记
DURATION_STATUS_CONTROLLED = 1     # 工期符合管控
DURATION_STATUS_NOT_YET = 2        # 未到管控期
DURATION_STATUS_OVERDUE = 3        # 工期超期


# ============================================================
# 标准工期统计分析表 - 项目类型标准（月数）
# ============================================================

# 项目类型工期标准
PROJECT_TYPE_STANDARDS = {
    "传输系统-省内干线": {
        "建设期": 11,
        "施工期": 6,
        "全生命周期": 20,
        "开工日期": 5,
        "勘察设计": 5,
        "物资采购": 5,
        "工程实施": 6,
        "工程验收": 4,
        "审计归档": 5
    },
    "传输线路-省内干线": {
        "建设期": 14,
        "施工期": 10,
        "全生命周期": 26,
        "开工日期": 4,
        "勘察设计": 6,
        "物资采购": 6,
        "工程实施": 8,
        "工程验收": 5.5,
        "审计归档": 6.5
    },
    "软硬结合项目": {
        "建设期": 12,
        "施工期": 9,
        "全生命周期": 24,
        "开工日期": 3,
        "勘察设计": 5,
        "物资采购": 5,
        "工程实施": 7,
        "工程验收": 5.5,
        "审计归档": 6.5
    },
    "纯软件-定制开发类": {
        "建设期": 12,
        "施工期": 9,
        "全生命周期": 24,
        "开工日期": 3,
        "勘察设计": 5,
        "物资采购": 5,
        "工程实施": 7,
        "工程验收": 5.5,
        "审计归档": 6.5
    },
    "土建及大机电类": {
        "建设期": 24,
        "施工期": 22,
        "全生命周期": 36,
        "开工日期": 2,
        "勘察设计": 0,
        "物资采购": 0,
        "工程实施": 0,
        "工程验收": 0,
        "审计归档": 0
    },
    "承载网": {
        "建设期": 11,
        "施工期": 8,
        "全生命周期": 23,
        "开工日期": 3,
        "勘察设计": 0,
        "物资采购": 0,
        "工程实施": 0,
        "工程验收": 0,
        "审计归档": 0
    }
}


# ============================================================
# 列名映射 - 与实际数据表对应
# ============================================================

COLUMN_MAPPING = {
    "project_code": "项目编码",
    "project_name": "项目名称",
    "project_year": "项目年份",
    "construction_unit": "建设单位",
    "approval_date": "第一次立项批复完成时间",
    "approval_amount": "最新立项批复金额",
    "start_date": "开工报告完成（填报）时间",
    "handover_date": "割接上线交维（填报）时间",
    "completion_date": "竣工验收完成时间",
    "completion_archive_date": "竣工备案完成时间",
    "final_accounting_date": "决算审计完成时间",
    "pms_close_date": "PMS第一次项目关闭时间",
    "manager_main": "工程实施经理-主",
    "manager_sub": "工程实施经理-辅",
    "process_template": "工程实施流程模板",
    "level1_profession": "一级专业名称",
    "level2_profession": "二级专业名称",
    "level3_profession": "三级专业名称",
    "level4_profession": "四级专业名称",
    "project_set": "项目集名称",
    "design_approval_date": "第一次设计批复完成时间",
    "quality_inspection_date": "质监申报完成（填报）时间"
}


# ============================================================
# 辅助表数据结构
# ============================================================

DEFAULT_AUX_TABLE = """实施经理,专业
张三,传输系统
李四,传输线路
王五,软件工程
赵六,土建工程"""


# ============================================================
# 工期计算函数
# ============================================================

def parse_date(date_value) -> Optional[datetime]:
    """解析日期值，支持多种格式"""
    if pd.isna(date_value) or date_value == 0 or date_value == "0":
        return None

    if isinstance(date_value, datetime):
        return date_value

    if isinstance(date_value, str):
        # 尝试多种日期格式
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%d/%m/%Y",
            "%m/%d/%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_value, fmt)
            except ValueError:
                continue

    return None


def add_days(date_obj: datetime, days: int) -> datetime:
    """日期加天数"""
    return date_obj + timedelta(days=days)


def add_months(date_obj: datetime, months: float) -> datetime:
    """日期加月数（按30天/月计算）"""
    total_days = int(months * 30)
    return date_obj + timedelta(days=total_days)


def add_years(date_obj: datetime, years: int) -> datetime:
    """日期加年数"""
    return datetime(date_obj.year + years, date_obj.month, date_obj.day)


def yuan_to_wan(yuan_value) -> Optional[float]:
    """金额转换：元转万元"""
    if pd.isna(yuan_value) or yuan_value == 0:
        return None
    try:
        return float(yuan_value) / 10000
    except (ValueError, TypeError):
        return None


# ============================================================
# 优质工期统计表计算
# ============================================================

def calculate_construction_period_required(approval_date) -> Optional[datetime]:
    """计算优质工程建设期要求交维时间（立项批复 + 274天）"""
    date = parse_date(approval_date)
    if date is None:
        return None
    return add_days(date, CONSTRUCTION_PERIOD_DAYS)


def calculate_construction_phase_required(start_date) -> Optional[datetime]:
    """计算优质工程施工期要求交维时间（开工报告 + 182天）"""
    date = parse_date(start_date)
    if date is None:
        return None
    return add_days(date, CONSTRUCTION_PHASE_DAYS)


def calculate_acceptance_control_required(handover_date) -> Optional[datetime]:
    """计算优质工程验收控制要求竣工验收时间（割接上线交维 + 152天）"""
    date = parse_date(handover_date)
    if date is None:
        return None
    return add_days(date, ACCEPTANCE_CONTROL_DAYS)


def determine_duration_status(
    handover_date,
    completion_date,
    construction_required,
    phase_required,
    acceptance_required
) -> int:
    """
    判定工期管控状态

    参数:
        handover_date: 割接上线交维（填报）时间
        completion_date: 竣工验收完成时间
        construction_required: 建设期要求交维时间
        phase_required: 施工期要求交维时间
        acceptance_required: 验收控制要求竣工验收时间

    返回:
        1: 工期符合管控
        2: 未到管控期
        3: 工期超期
    """
    # 解析实际时间
    actual_handover = parse_date(handover_date)
    actual_completion = parse_date(completion_date)

    # 解析要求时间
    req_construction = parse_date(construction_required)
    req_phase = parse_date(phase_required)
    req_acceptance = parse_date(acceptance_required)

    # 检查是否有空值（未到管控期）
    if any(v is None for v in [actual_handover, actual_completion,
                                 req_construction, req_phase, req_acceptance]):
        return DURATION_STATUS_NOT_YET

    # 判定是否满足管控条件
    # 条件：交维时间未超建设期和施工期要求，且竣工时间未超验收控制要求
    handover_ok = (actual_handover <= req_construction and
                    actual_handover <= req_phase)
    completion_ok = actual_completion <= req_acceptance

    if handover_ok and completion_ok:
        return DURATION_STATUS_CONTROLLED
    else:
        return DURATION_STATUS_OVERDUE


def is_provincial_project(construction_unit: str) -> Optional[int]:
    """
    判断是否为省管项目

    规则：建设单位名称中仅包含一次"河源分公司"则为空，否则记为1
    说明：
      - "河源分公司"（仅河源）→ 空（非省管）
      - "工程建设部,河源分公司"（含其他单位）→ 1（省管）
      - "省公司,河源分公司,其他"（多次出现）→ 1（省管）
    """
    if pd.isna(construction_unit) or construction_unit == "":
        return 1  # 出错时默认记为1

    # 仅包含一次"河源分公司"且建设单位名称等于"河源分公司"才是非省管
    count = construction_unit.count("河源分公司")
    if count == 1 and construction_unit.strip() == "河源分公司":
        return None  # 非省管项目
    else:
        return 1  # 省管项目


def check_pms_closed(pms_close_date) -> str:
    """判断PMS是否曾关闭"""
    date = parse_date(pms_close_date)
    if date is None:
        return "否"
    else:
        return "是"


# ============================================================
# 标准工期统计分析表计算
# ============================================================

def determine_project_type(
    process_template: str,
    level1_name: str = "",
    level2_name: str = "",
    level3_name: str = "",
    level4_name: str = "",
    project_set: str = ""
) -> Optional[str]:
    """
    判定项目类别

    优先根据工程实施流程模板进行模糊判断，
    若无法判断则结合专业名称进一步判定
    """
    if pd.isna(process_template):
        process_template = ""

    # 模板关键词匹配
    template_keywords = {
        "传输系统-省内干线": ["传输系统", "省内干线", "传输系统干线"],
        "传输线路-省内干线": ["传输线路", "光缆", "线路工程"],
        "软硬结合项目": ["软硬", "软硬件", "系统集成"],
        "纯软件-定制开发类": ["软件开发", "软件定制", "纯软件", "定制开发"],
        "土建及大机电类": ["土建", "机电", "机房建设", "基础设施"],
        "承载网": ["承载网", "数据网", "网络设备"]
    }

    for proj_type, keywords in template_keywords.items():
        for keyword in keywords:
            if keyword in process_template:
                return proj_type

    # 结合专业名称判断
    all_names = f"{level1_name} {level2_name} {level3_name} {level4_name} {project_set}"

    for proj_type, keywords in template_keywords.items():
        for keyword in keywords:
            if keyword in all_names:
                return proj_type

    return None  # 无法判定


def calculate_standard_duration(
    approval_date,
    start_date,
    handover_date,
    project_type: str
) -> Dict[str, Optional[datetime]]:
    """
    计算标准工期各项要求时间

    返回字典包含:
    - 全生命周期要求项目关闭时间
    - 标准建设期要求割接上线时间
    - 标准施工期要求割接上线时间
    - 要求割接上线时间（省公司要求）
    - 标准工期要求开工时间
    - 立项超一年要求开工时间
    - 立项即将超3年要求关闭时间
    """
    result = {
        "全生命周期要求项目关闭时间": None,
        "标准建设期要求割接上线时间": None,
        "标准施工期要求割接上线时间": None,
        "要求割接上线时间_省公司要求": None,
        "标准工期要求开工时间": None,
        "立项超一年要求开工时间": None,
        "立项即将超3年要求关闭时间": None
    }

    # 获取项目类型标准
    standards = PROJECT_TYPE_STANDARDS.get(project_type)
    if standards is None:
        return result

    approval = parse_date(approval_date)
    start = parse_date(start_date)

    if approval is None:
        return result

    # 1. 全生命周期要求项目关闭时间
    result["全生命周期要求项目关闭时间"] = add_months(
        approval, standards["全生命周期"]
    )

    # 2. 标准建设期要求项目割接上线时间
    result["标准建设期要求割接上线时间"] = add_months(
        approval, standards["建设期"]
    )

    # 3. 标准施工期要求项目割接上线时间
    if start is not None:
        result["标准施工期要求割接上线时间"] = add_months(
            start, standards["施工期"]
        )

    # 4. 要求割接上线时间（省公司要求）
    if result["标准建设期要求割接上线时间"] and result["标准施工期要求割接上线时间"]:
        result["要求割接上线时间_省公司要求"] = min(
            result["标准建设期要求割接上线时间"],
            result["标准施工期要求割接上线时间"]
        )
    elif result["标准建设期要求割接上线时间"]:
        result["要求割接上线时间_省公司要求"] = result["标准建设期要求割接上线时间"]

    # 5. 标准工期要求项目开工时间
    result["标准工期要求开工时间"] = add_months(
        approval, standards["开工日期"]
    )

    # 6. 立项超一年要求项目开工时间
    result["立项超一年要求开工时间"] = add_years(approval, 1)

    # 7. 立项即将超3年要求项目关闭时间
    result["立项即将超3年要求关闭时间"] = add_years(approval, 3)

    return result


# ============================================================
# 主处理函数
# ============================================================

def load_project_data(file_path: str, sheet_name: str = "项目明细查询报表") -> pd.DataFrame:
    """
    加载项目数据表

    参数:
        file_path: Excel文件路径
        sheet_name: 工作表名称，默认"项目明细查询报表"

    返回:
        DataFrame，列名已修正
    """
    # 读取数据，表头在第2行（index=1）
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)

    # 清理列名中的空白字符
    df.columns = df.columns.str.strip()

    return df


def process_high_quality_duration_report(
    project_df: pd.DataFrame,
    aux_df: pd.DataFrame,
    business_date: str = "2026-03-03"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    处理优质工期统计表

    参数:
        project_df: 项目报表DataFrame
        aux_df: 辅助表DataFrame（实施经理-专业对应表）
        business_date: 业务数据截至时间

    返回:
        (增补列后的项目报表, 统计表)
    """
    # 复制数据避免修改原始数据
    project_enhanced = project_df.copy()

    # 1. 添加省管项目列
    if "建设单位" in project_enhanced.columns:
        project_enhanced["省管项目"] = project_enhanced["建设单位"].apply(
            is_provincial_project
        )

    # 2. 添加PMS是否曾关闭列
    if "PMS第一次项目关闭时间" in project_enhanced.columns:
        project_enhanced["PMS是否曾关闭"] = project_enhanced[
            "PMS第一次项目关闭时间"
        ].apply(check_pms_closed)

    # 3. 添加/更新工程实施经理-主列（基于辅助表匹配）
    # 4. 添加专业列
    if aux_df is not None and not aux_df.empty:
        aux_dict = dict(zip(aux_df["实施经理"], aux_df["专业"]))

        def match_manager_primary(row):
            """匹配工程实施经理-主"""
            main_mgr = row.get("工程实施经理-主", "")
            sub_mgr = row.get("工程实施经理-辅", "")

            if pd.notna(main_mgr) and main_mgr in aux_dict:
                return main_mgr
            if pd.notna(sub_mgr) and sub_mgr in aux_dict:
                return sub_mgr
            return ""

        def match_profession(row):
            """匹配专业"""
            primary_mgr = row.get("工程实施经理-主_new", row.get("工程实施经理-主", ""))
            if pd.notna(primary_mgr) and primary_mgr in aux_dict:
                return aux_dict[primary_mgr]
            return ""

        if "工程实施经理-主" in project_enhanced.columns:
            project_enhanced["工程实施经理-主_new"] = project_enhanced.apply(
                match_manager_primary, axis=1
            )
            project_enhanced["专业"] = project_enhanced.apply(
                match_profession, axis=1
            )

    # 5. 计算工期要求时间
    project_enhanced["优质工程建设期要求交维时间"] = project_enhanced[
        "第一次立项批复完成时间"
    ].apply(calculate_construction_period_required)

    project_enhanced["优质工程施工期要求交维时间"] = project_enhanced[
        "开工报告完成（填报）时间"
    ].apply(calculate_construction_phase_required)

    project_enhanced["优质工程验收控制要求竣工验收时间"] = project_enhanced[
        "割接上线交维（填报）时间"
    ].apply(calculate_acceptance_control_required)

    # 6. 判定工期管控状态
    def calc_status(row):
        return determine_duration_status(
            row.get("割接上线交维（填报）时间"),
            row.get("竣工验收完成时间"),
            row.get("优质工程建设期要求交维时间"),
            row.get("优质工程施工期要求交维时间"),
            row.get("优质工程验收控制要求竣工验收时间")
        )

    project_enhanced["是否满足优质工程交维时间"] = project_enhanced.apply(
        calc_status, axis=1
    )

    # 7. 生成统计表（筛选条件：省管项目为空 且 PMS未关闭）
    filtered = project_enhanced[
        (project_enhanced["省管项目"].isna()) &
        (project_enhanced["PMS是否曾关闭"] == "否")
    ].copy()

    # 选择统计表字段
    stats_columns = [
        "项目编码", "项目名称", "PMS是否关闭过", "立项批复金额_万_",
        "专业", "工程实施经理-主", "第一次立项批复完成时间",
        "开工报告完成（填报）时间", "割接上线交维（填报）时间", "竣工验收完成时间",
        "优质工程建设期要求交维时间", "优质工程施工期要求交维时间",
        "优质工程验收控制要求竣工验收时间", "是否满足优质工程交维时间"
    ]

    # 获取实际存在的列
    existing_cols = [col for col in stats_columns if col in filtered.columns]
    stats_df = filtered[existing_cols].copy()

    return project_enhanced, stats_df


def process_standard_duration_report(
    project_df: pd.DataFrame,
    year_range: Tuple[int, int] = (2022, 2026)
) -> pd.DataFrame:
    """
    处理标准工期统计分析表

    参数:
        project_df: 项目报表DataFrame
        year_range: 项目年份范围，默认(2022, 2026)

    返回:
        标准工期统计表
    """
    result = project_df.copy()

    # 筛选年份范围内的项目
    if "项目年份" in result.columns:
        result = result[
            (result["项目年份"] >= year_range[0]) &
            (result["项目年份"] <= year_range[1])
        ]

    # 1. 判断省管项目
    if "建设单位" in result.columns:
        result["省管项目"] = result["建设单位"].apply(is_provincial_project)

    # 筛选省管项目
    result = result[result["省管项目"] == 1]

    # 2. 判定项目类别
    def get_project_type(row):
        return determine_project_type(
            row.get("工程实施流程模板", ""),
            row.get("一级专业名称", ""),
            row.get("二级专业名称", ""),
            row.get("三级专业名称", ""),
            row.get("四级专业名称", ""),
            row.get("项目集名称", "")
        )

    result["项目类别"] = result.apply(get_project_type, axis=1)

    # 3. 计算标准工期要求时间
    def calc_all_durations(row):
        return calculate_standard_duration(
            row.get("第一次立项批复完成时间"),
            row.get("开工报告完成（填报）时间"),
            row.get("割接上线交维（填报）时间"),
            row.get("项目类别")
        )

    duration_results = result.apply(calc_all_durations, axis=1)
    duration_df = pd.DataFrame(duration_results.tolist())

    # 合并结果
    for col in duration_df.columns:
        result[col] = duration_df[col].values

    return result


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    # 示例用法
    print("工期统计计算模块")
    print("=" * 50)
    print(f"数据源配置:")
    print(f"  - 工作表名称: 项目明细查询报表")
    print(f"  - 表头行: 第2行")
    print(f"  - 金额单位: 元")
    print()
    print(f"优质工期统计标准:")
    print(f"  - 建设期要求交维时间: {CONSTRUCTION_PERIOD_DAYS}天")
    print(f"  - 施工期要求交维时间: {CONSTRUCTION_PHASE_DAYS}天")
    print(f"  - 验收控制要求竣工验收时间: {ACCEPTANCE_CONTROL_DAYS}天")
    print()
    print(f"项目类型标准数量: {len(PROJECT_TYPE_STANDARDS)}")
    for proj_type in PROJECT_TYPE_STANDARDS:
        print(f"  - {proj_type}")
    print()
    print("使用示例:")
    print("  df = load_project_data('项目数据表.xlsx')")
    print("  enhanced_df, stats_df = process_high_quality_duration_report(df, aux_df)")
    print("  standard_df = process_standard_duration_report(df)")
