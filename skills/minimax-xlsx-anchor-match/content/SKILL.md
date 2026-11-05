---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 167c4e5142305ffc2ce628ec579c5bf0
    PropagateID: 167c4e5142305ffc2ce628ec579c5bf0
    ReservedCode1: 3045022100f8ae66e92237f245fefdfea2da36abe221d7701c2abceb0524855c82bf17230c022023c1aa3084e0918e875c5ca2f0d19bb895c2523f10efceb7054dc919504deee1
    ReservedCode2: 30460221009c38d9cd77c6eeef26db0a715b28726abe50ca14350d7b766ac62c91fd0bde4c022100843eb47c8ca2fd9199787c980fd97986573003b336def87b4118f7d94475fccb
description: 使用此技能处理主播打卡时间与直播记录的自动匹配场景。当用户需要根据Sheet1中的主播打卡时间数据（包含每日上班打卡和下班打卡时间），去匹配Sheet2中的直播开始时间和直播结束时间，并在Sheet2的主播列中填写对应的主播名称时，应使用此技能。此技能特别适用于直播平台、主播运营团队等需要对直播场次进行主播归属归类的业务场景。
license: MIT
name: minimax-xlsx-anchor-match
---

# minimax-xlsx-anchor-match

主播打卡时间与直播时间匹配技能，专用于将直播记录自动归类到对应主播的业务场景。

## 一、技能触发条件

### 1.1 何时使用此技能

当用户提出以下类型的需求时，应该触发此技能。第一种是明确的匹配需求，例如「根据Sheet1页中的主播打卡时间，去匹配sheet2中的直播开始时间和直播结束时间，并在sheet2中主播列填写」。第二种是相关的业务描述，例如「主播打卡表和直播记录表」「把直播场次对应到主播」「根据打卡记录识别直播是谁的」。第三种是数据归类需求，例如「主播考勤与直播时长关联分析」「直播场次归属统计」。

### 1.2 前置数据要求

使用此技能前，需要确保数据满足基本结构要求。Sheet1应该包含主播打卡时间表，第一列为主播名称，后续每列对应一天的日期，单元格内容为打卡时间记录。Sheet2应该包含直播记录表，至少包含直播开始时间、直播结束时间、主播（待填充）三列。主播名称在两个Sheet中应该保持一致，以便进行准确匹配。

### 1.3 技能限制说明

此技能存在以下适用边界。对于时间匹配场景最为有效，如果用户需要基于其他维度（如商品、频道、GMV）进行主播归类，则需要使用其他方法。如果直播记录数量超过100000条，建议进行分批处理以优化性能。如果存在多主播同时直播的记录，此技能仅支持一对一匹配，不适用于多对多场景。

## 二、数据结构分析

### 2.1 Sheet1打卡数据结构

主播打卡时间表通常采用横向布局，行为主播名称，列为日期。打卡记录格式通常为「状态(时:分),状态(时:分)」，表示上午上班时间和上午下班时间，或者下午的上班和下班时间。状态字段可能包含「正常」「迟到N分钟」「早退N分钟」等变体。部分记录可能包含「休息(-,-)」表示休息日，或者「事假」「病假」等特殊标记。

### 2.2 Sheet2直播数据结构

直播记录表通常包含精确的日期时间信息。直播开始时间和结束时间应为标准datetime格式，能够准确区分不同日期的直播场次。跨天直播（如20:00开始、次日01:00结束）应该在结束时间中明确体现日期变化。主播列初始状态为空，需要通过匹配算法进行填充。

### 2.3 数据质量检查点

在进行匹配之前，应该检查以下数据质量指标。完整性方面，检查是否存在缺失的主播打卡记录或直播时间信息。格式一致性方面，检查日期格式是否统一，时间格式是否标准。异常值方面，检查是否存在不合理的打卡时间或直播时长（如打卡时间缺失、直播时长超过24小时等）。

## 三、匹配算法实现

### 3.1 时间解析模块

时间解析是将原始打卡字符串转换为可计算时间值的关键步骤。解析函数需要处理多种模式，包括标准格式「正常(07:52)」、迟到格式「迟到1分钟(08:01)」、休息格式「休息(-,-)」等。解析结果应该统一转换为时:分格式，便于后续的时间计算。如果遇到无法识别的格式，函数应该返回None而不是抛出异常。

### 3.2 排班表构建

将解析后的打卡数据组织成便于查询的数据结构。推荐使用嵌套字典结构，外层键为主播名称，内层键为日期，值为(上班时间,下班时间)元组。对于跨天班次（如19:00-01:00），下班时间应该保留原始值，在匹配算法中统一处理日期跨越逻辑。

### 3.3 匹配评分机制

采用多级评分机制评估匹配质量。第一级为精确匹配（3分），当直播时间完全落在打卡时间段内时给予最高分。第二级为容差匹配（2分），当直播时间与打卡时间存在合理偏差时给予次高分。容差范围建议设置为30分钟。第三级为边界匹配（1分），当只有直播开始或结束时间与打卡时间接近时给予基础分。最终选择得分最高的主播作为匹配结果。

### 3.4 跨天特殊处理

跨天情况需要在多个环节进行特殊处理。首先是打卡跨天识别，当下班时间的小时数小于上班时间时，说明存在跨天情况，此时需要在计算时将下班时间加上24小时。其次是直播跨天识别，当直播结束时间早于开始时间时，说明该直播跨越了午夜。第三是日期回溯，对于凌晨时段（建议00:00-06:00）的直播记录，在匹配时应该同时检查当天和前一天的打卡表，因为这类直播很可能属于前一天的班次。

## 四、代码实现模板

### 4.1 依赖导入

```python
import pandas as pd
import re
from datetime import datetime, timedelta
from openpyxl import load_workbook
```

### 4.2 打卡时间解析

```python
def parse_check_in_time(cell_value):
    """解析打卡时间字符串，返回(上班时间,下班时间)"""
    if pd.isna(cell_value) or '休息' in str(cell_value):
        return None

    pattern = r'(\d{2}):(\d{2})'
    matches = re.findall(pattern, str(cell_value))

    if len(matches) >= 2:
        start = f"{matches[0][0]}:{matches[0][1]}"
        end = f"{matches[1][0]}:{matches[1][1]}"
        return (start, end)
    return None
```

### 4.3 匹配核心函数

```python
def match_anchor_improved(live_start, live_end, anchor_schedule):
    """根据直播时间匹配主播"""
    if not isinstance(live_start, datetime) or not isinstance(live_end, datetime):
        return None

    live_date = live_start.date()
    start_time = live_start.hour * 60 + live_start.minute
    end_time = live_end.hour * 60 + live_end.minute

    # 处理直播跨天
    is_cross_day = end_time < start_time
    if is_cross_day:
        end_time += 24 * 60

    best_match = None
    best_score = 0

    # 检查当前日期和前一天（处理凌晨直播）
    dates_to_check = [live_date]
    if is_cross_day or live_start.hour < 6:
        dates_to_check.append(live_date - timedelta(days=1))

    for anchor_name, schedule in anchor_schedule.items():
        for check_date in dates_to_check:
            if check_date not in schedule or schedule[check_date] is None:
                continue

            start, end = schedule[check_date]
            start_minutes = int(start.split(':')[0]) * 60 + int(start.split(':')[1])
            end_minutes = int(end.split(':')[0]) * 60 + int(end.split(':')[1])

            # 处理打卡跨天
            if end_minutes <= start_minutes:
                end_minutes += 24 * 60

            tolerance = 30  # 30分钟容差
            score = 0

            if start_minutes - tolerance <= start_time <= end_minutes + tolerance:
                if start_time <= end_time <= end_minutes + tolerance:
                    score = 3

            if abs(start_time - start_minutes) <= tolerance:
                score = max(score, 2)

            if abs(end_time - end_minutes) <= tolerance:
                score = max(score, 2)

            if score > best_score:
                best_score = score
                best_match = anchor_name

    return best_match
```

### 4.4 主处理流程

```python
# 1. 读取数据
df1 = pd.read_excel(file_path, sheet_name='Sheet1')
df2 = pd.read_excel(file_path, sheet_name='Sheet2')
df2['直播开始时间'] = pd.to_datetime(df2['直播开始时间'])
df2['直播结束时间'] = pd.to_datetime(df2['直播结束时间'])

# 2. 构建排班表
anchor_schedule = {}
for idx, row in df1.iterrows():
    anchor_name = row['主播']
    anchor_schedule[anchor_name] = {}
    for col in df1.columns[1:]:
        date_str = col.split(' ')[0]
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        anchor_schedule[anchor_name][date] = parse_check_in_time(row[col])

# 3. 执行匹配
matched_results = []
for i in range(len(df2)):
    matched = match_anchor_improved(
        df2.iloc[i]['直播开始时间'],
        df2.iloc[i]['直播结束时间'],
        anchor_schedule
    )
    matched_results.append(matched if matched else "未匹配")

# 4. 写入结果
wb = load_workbook(file_path)
ws = wb['Sheet2']
for i, matched in enumerate(matched_results):
    ws.cell(row=i+2, column=3, value=matched)
wb.save(output_path)
```

## 五、结果验证与报告

### 5.1 匹配统计指标

匹配完成后应该输出以下统计信息。总记录数，表示需要匹配的直播场次总数。成功匹配数，表示成功识别出主播的直播场次数量及其占比。各主播分布，表示每个主播分别匹配到的直播场次数量。未匹配记录，表示无法确定主播的直播场次及其具体时间信息。

### 5.2 典型匹配结果

以162条直播记录的测试数据为例，典型的匹配结果分布可能是主播一匹配约50场、主播二匹配约45场、主播三匹配约55场，另有少量记录因数据异常或边界情况无法匹配。总体匹配率通常应该在90%以上，如果匹配率明显偏低，需要检查数据质量或算法参数设置。

### 5.3 未匹配记录分析

未匹配的记录通常具有以下特征。大部分是凌晨00:00-01:00时段的直播，可能是跨天直播的延续部分。少数可能是打卡数据缺失导致。另一部分可能是时间格式异常的特殊记录。对于未匹配记录，建议保留「未匹配」标记，并提供详细的时间信息以便人工核查。

## 六、输出文件规范

### 6.1 文件命名规则

输出文件应该采用清晰的命名规范，建议格式为「原文件名_已匹配.xlsx」。如果需要版本管理，可以在文件名中加入处理日期，例如「主播业绩统计_20260401_已匹配.xlsx」。原始文件应该保持不变，新生成的匹配结果保存为新文件。

### 6.2 数据完整性保证

输出文件应该保持原始数据的完整性。直播开始时间和结束时间列不应该被修改。主播列的新增数据应该与原有数据的格式保持一致。如果需要添加额外的统计信息，建议使用新增列而非覆盖原有数据。

### 6.3 后续处理建议

匹配结果可以用于进一步的分析和应用。主播直播场次统计，可以按主播汇总直播场次数量。工作时长计算，可以结合直播时长和主播打卡时长进行效率分析。数据质量改进，可以基于未匹配记录反推数据问题并进行修正。

## 七、相关文档索引

| 文档 | 说明 |
|------|------|
| [anchor-live-match.md](docs/anchor-live-match.md) | 主播打卡时间与直播时间匹配操作指南，包含详细的操作步骤和最佳实践 |
| [pitfalls-index.md](docs/pitfalls-index.md) | Excel处理常见问题索引，包含数据质量、公式错误等场景的解决方案 |
| [create-edit-guide.md](docs/create-edit-guide.md) | openpyxl创建和编辑Excel的详细指南，包含样式、格式等高级技巧 |

## 八、技术支持与反馈

如果在使用过程中遇到问题，可以检查以下几个方面。首先确认Python环境是否正确安装了pandas和openpyxl库。其次检查Excel文件的Sheet名称是否与代码中引用的一致。第三验证日期时间格式是否符合标准datetime格式。第四确认主播名称在两个Sheet中完全一致。如果问题仍然存在，可以查看相关文档或提供具体的错误信息以便进一步排查。
