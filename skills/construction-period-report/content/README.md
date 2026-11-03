---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 938cbc71ef8d7d4cba043c8e77114bb5
    PropagateID: 938cbc71ef8d7d4cba043c8e77114bb5
    ReservedCode1: 30450220416fe4cedc952c914fc03d1ae1ea2e4561a5e9fca5cf0c067a58b9866901cab6022100ee2b88de9295819a19a843040aa27a64c82c9b38a33bf2da50930b43e3dbbff3
    ReservedCode2: 3045022100df32c33f342d9f66aa4f084fb5763d279c9d7f1ba16d783a62805015423495010220094e813a31a05afd00f0da5b1a7389292f1b327eb03fbd47e0feff5d8320bfe8
---

# 工期统计通报技能使用指南

## 快速开始

### 1. 环境要求

- Python 3.8+
- pandas
- openpyxl (用于Excel文件处理)

### 2. 安装依赖

```bash
pip install pandas openpyxl
```

### 3. 基本使用

#### 方式一：命令行运行

```python
from duration_calculator import (
    process_high_quality_duration_report,
    process_standard_duration_report,
    parse_date,
    add_days,
    PROJECT_TYPE_STANDARDS
)

# 读取数据
project_df = pd.read_excel("项目报表.xlsx")
aux_df = pd.read_excel("辅助表.xlsx")

# 处理优质工期统计表
enhanced_df, stats_df = process_high_quality_duration_report(
    project_df,
    aux_df,
    business_date="2026-03-03"
)

# 处理标准工期统计表
standard_stats_df = process_standard_duration_report(
    project_df,
    year_range=(2022, 2026)
)
```

#### 方式二：直接调用函数

```python
from duration_calculator import (
    calculate_construction_period_required,
    calculate_construction_phase_required,
    calculate_acceptance_control_required,
    determine_duration_status,
    determine_project_type,
    calculate_standard_duration
)

# 计算优质工程工期要求
construction_required = calculate_construction_period_required("2025-01-15")
# 结果: 2025-10-16 (加274天)

phase_required = calculate_construction_phase_required("2025-03-01")
# 结果: 2025-08-30 (加182天)

acceptance_required = calculate_acceptance_control_required("2025-05-20")
# 结果: 2025-10-19 (加152天)

# 判定工期管控状态
status = determine_duration_status(
    handover_date="2025-08-01",
    completion_date="2025-10-01",
    construction_required=construction_required,
    phase_required=phase_required,
    acceptance_required=acceptance_required
)
# status = 1 (工期符合管控)

# 判定项目类型
project_type = determine_project_type(
    process_template="传输系统-省内干线项目",
    level1_name="传输",
    level2_name="系统"
)
# project_type = "传输系统-省内干线"

# 计算标准工期
duration_result = calculate_standard_duration(
    approval_date="2025-01-01",
    start_date="2025-04-01",
    handover_date="2025-08-01",
    project_type="传输系统-省内干线"
)
```

## 工期计算规则速查

### 优质工期统计表

| 工期类型 | 计算公式 | 天数 |
|---------|---------|------|
| 建设期要求交维时间 | 立项批复完成时间 + 274天 | 274 |
| 施工期要求交维时间 | 开工报告完成时间 + 182天 | 182 |
| 验收控制要求竣工验收时间 | 割接上线交维时间 + 152天 | 152 |

### 工期管控判定

| 标记值 | 含义 | 判定条件 |
|-------|------|---------|
| 1 | 工期符合管控 | 交维时间未超建设期和施工期要求，且竣工时间未超验收控制要求 |
| 2 | 未到管控期 | 相关时间存在空值 |
| 3 | 工期超期 | 不满足上述条件 |

### 标准工期项目类型

| 项目类别 | 建设期(月) | 施工期(月) | 全生命周期(月) | 开工日期(月) |
|---------|-----------|-----------|---------------|-------------|
| 传输系统-省内干线 | 11 | 6 | 20 | 5 |
| 传输线路-省内干线 | 14 | 10 | 26 | 4 |
| 软硬结合项目 | 12 | 9 | 24 | 3 |
| 纯软件-定制开发类 | 12 | 9 | 24 | 3 |
| 土建及大机电类 | 24 | 22 | 36 | 2 |
| 承载网 | 11 | 8 | 23 | 3 |

## 报表字段说明

### 优质工期统计表输出字段

- 项目编码
- 项目名称
- PMS是否关闭过
- 立项批复金额（万）
- 专业
- 工程实施经理-主
- 第一次立项批复完成时间
- 开工报告完成（填报）时间
- 割接上线交维（填报）时间
- 竣工验收时间
- 优质工程建设期要求交维时间
- 优质工程施工期要求交维时间
- 优质工程验收控制要求竣工验收时间
- 是否满足优质工程交维时间

### 标准工期统计分析表输出字段（A-AC列）

- 立项批复时间
- 项目投资（万元）
- 实际完成时间-设计批复
- 实际完成时间-质监申报
- 实际完成时间-开工
- 实际完成时间-交维
- 实际完成时间-竣工验收
- 实际完成时间-竣工备案
- 实际完成时间-竣工决算
- 实际完成时间-项目关闭
- 立项年度
- 项目经理
- 项目类别
- 各阶段工期要求时间

## 注意事项

1. **日期格式**: 支持 `YYYY-MM-DD`、`YYYY/MM/DD`、`YYYYMMDD` 等格式
2. **空值处理**: 原始数据中的0值会被转换为空值
3. **省管项目判断**: 建设单位仅包含一次"河源分公司"则为非省管项目
4. **自动更新**: 配置 `auto_refresh: true` 可实现报表自动刷新
