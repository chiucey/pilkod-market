---
name: activity-review
description: 活动复盘合规自查报告生成工具 - 自动审核活动总结Excel并生成专业HTML合规报告
---

# 活动复盘合规审核

自动化的活动复盘合规自查报告生成工具。

## 功能特点

- 自动读取活动总结Excel文件（.xlsx/.xls）
- 支持多Sheet智能解析：活动总结、费用明细、会务费用明细、费用凭证等
- 按照5大板块进行合规审核评分（总分100分）
- 生成专业HTML格式的合规自查报告
- 智能预警提示（P0/P1/P2优先级分类）

## 审核板块及分值

| 板块 | 分值 |
|------|------|
| 活动基本信息及受益产品线 | 5分 |
| 活动规模及商机情况 | 25分 |
| 覆盖客群及触达人数 | 20分 |
| 活动传播 | 25分 |
| 费用明细及凭证 | 25分 |

## 安装依赖

```bash
pip install openpyxl
```

## 使用方法

### 命令行

```bash
python activity_review_skill.py <Excel文件路径> [输出目录]
```

### 示例

```bash
python activity_review_skill.py "活动总结.xlsx" ./output
```

### Python API

```python
from activity_review_skill import main

success, report_path = main("活动总结.xlsx", "./output")
if success:
    print(f"报告已生成: {report_path}")
```

## 输出报告内容

- 综合评分卡（总分、得分率、五大板块进度条）
- 五大板块审核清单（每项带状态标记和优先级）
- 预算执行对比表（预算/实际/差异/差异率）
- 审核结论与补充清单（按优先级列出预警）
- 凭证完整性检查结果
- 活动亮点与不足

## 预警提示

- **P0（红色）**：严重缺失，强烈建议补充
- **P1（橙色）**：重要问题，建议补充
- **P2（黄色）**：一般问题，可选优化

## 版本

v1.0.0