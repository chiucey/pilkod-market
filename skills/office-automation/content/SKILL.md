---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f3f9a90980150c916c011141d782fbcb
    PropagateID: f3f9a90980150c916c011141d782fbcb
    ReservedCode1: 3045022073c859f70be28415bd7f302b9d666c2e4e3342fed0ff5762c6d87b01894e2a1c022100aceee54ba8e7158f99ae55178b4684a7c47b2878a57bb004d1dd53efcca15cb4
    ReservedCode2: 304502204774dd3edec872d880b034787a4d070803bd93221a697cbfca92f8e0f6c2f6ff022100a3590f037c59a0ea7638a9799693ff76093f2ec9791bf8fc44dbed72ad24ee01
---

---
name: office-automation
description: "金鸡湖英迪格酒店人事办公自动化。自动生成Offer Letter和On Board Notice（输入姓名、职位、年假等字段即出PDF）、批量生成多个文档、自动更新Vacancy List编制表、多Excel人事数据联动同步（改一处自动更新所有关联表格）、Git版本控制与30天回滚、数据校验与变更日志。触发词：生成Offer、入职通知、人事同步、版本回滚、年假修改、薪资数据、Vacancy List、批量生成。使用场景：(1) 需要快速生成Offer或入职通知PDF (2) 修改员工信息后需要同步更新多个Excel (3) 查看或回滚人事数据历史版本 (4) 校验人事数据格式合法性 (5) 新员工入职自动更新编制表 (6) 批量生成多个Offer。"
---

# Office Automation — 金鸡湖英迪格酒店人事办公自动化

通过微信或WorkBuddy对话，完成Offer+入职通知生成、数据同步、版本管理。

**核心流程：生成Offer时自动同时生成On Board Notice，日期一致，一起出。**

## 数据根目录

```
C:\Users\AustinXU\Desktop\金鸡湖英迪格人事文件\
├── 01_Offer与入职\       ← 模板与输出
├── 02_招聘\              ← Vacancy List等
├── 03_薪资与数据\        ← 薪资分析、刷卡记录
├── 04_员工活动\
├── 05_简历\
├── 06_酒店介绍\
└── 07_制度与通知\
```

## 核心脚本

唯一入口：`scripts/office.py`

```bash
# 生成 Offer Letter + On Board Notice PDF（两份一起出）
python scripts/office.py offer --name "张三" --position "前台接待" --department "前厅部" --level "6级" --supervisor "前厅部经理" --start-date "2026-05-01" --salary 5000 --annual-leave 10 --deadline "2026-04-25"

# 生成 On Board Notice PDF
python scripts/office.py onboard --name "张三" --start-date "2026-05-01"

# 批量生成多个 Offer
python scripts/office.py batch --file "批量配置.xlsx" --type both

# 新员工入职自动更新 Vacancy List
python scripts/office.py vacancy --action add --name "徐佳琪" --department "人力资源部" --position "人力资源文员"

# 员工离职标记删除
python scripts/office.py vacancy --action remove --name "张三"

# 员工调岗更新编制
python scripts/office.py vacancy --action transfer --name "李四" --new-department "餐饮部" --new-position "厨师长"

# 同步人事数据（修改员工信息后联动更新所有关联Excel）
python scripts/office.py sync --field "annual_leave" --name "张三" --value 15

# 查看版本历史
python scripts/office.py version list

# 回滚到指定日期
python scripts/office.py version rollback --date "2026-04-10"

# 数据校验
python scripts/office.py validate
```

## 功能详解

### 1. Offer Letter 生成

读取 `01_Offer与入职/Offer letter-最新.docx` 模板，替换以下变量后导出PDF：

| 模板变量 | 说明 | 来源 |
|----------|------|------|
| `{{name}}` | 员工姓名 | 用户输入 |
| `{{department}}` | 部门 | 用户输入 |
| `{{position}}` | 职位 | 用户输入 |
| `{{supervisor}}` | 直接上司 | 用户输入 |
| `{{level}}` | 级别（如6级） | 用户输入 |
| `{{start_date}}` | 生效日期 | 用户输入 |
| `{{probation}}` | 试用期 | 默认"三个月" |
| `{{salary}}` | 月工资（税前） | 用户输入 |
| `{{salary_cn}}` | 工资大写 | 自动转换 |
| `{{annual_leave}}` | 年假天数 | 用户输入 |
| `{{deadline}}` | 签字截止日期 | 用户输入 |

输出路径：`01_Offer与入职/output/姓名_Offer_YYYYMMDD.pdf`

### 2. On Board Notice 生成

读取 `01_Offer与入职/On Board Notice-最新.docx` 模板，替换变量后导出PDF：

| 模板变量 | 说明 |
|----------|------|
| `{{name}}` | 员工姓名 |
| `{{start_date}}` | 入职日期 |
| `{{report_time}}` | 报到时间（默认8:30） |

输出路径：`01_Offer与入职/output/姓名_OnBoard_YYYYMMDD.pdf`

### 3. 人事数据同步

修改一个Excel中的数据后，自动同步到所有关联表格。

**关联规则** 详见 `references/sync_rules.md`

核心关联关系：
- 员工主表（薪资分析 Sheet2）↔ Vacancy List（编制对照）
- 修改年假 → 更新Offer记录、薪资分析
- 新增员工 → 更新Vacancy List编制、薪资分析

### 4. 版本控制

每次数据变更自动Git提交，保留30天历史。

| 命令 | 说明 |
|------|------|
| `version list` | 列出最近30天提交记录 |
| `version rollback --date YYYY-MM-DD` | 回滚到指定日期 |
| `version rollback --hash abc1234` | 回滚到指定commit |
| `version diff --date YYYY-MM-DD` | 查看与指定日期的差异 |

### 5. 数据校验

校验所有Excel数据的合法性：
- 手机号格式（11位数字）
- 邮箱格式
- 日期逻辑（入职日期 ≤ 今天）
- 级别格式（数字 + 级，如 6级）
- 年假范围（0-30天）
- 薪资非负

### 6. 批量生成文档

一次性生成多个 Offer 或入职通知，减少重复操作。

**Excel 批量配置格式：**
| 姓名 | 部门 | 职位 | 直接上司 | 入职日期 | 月薪 | 年假 | 试用期 | 截止日期 |
|------|------|------|----------|----------|------|------|--------|----------|
| 张三 | 前厅部 | 前台接待 | 前厅部经理 | 2026-05-01 | 5000 | 10 | 三个月 | 2026-04-20 |

**命令示例：**
```bash
# 批量生成 Offer
python scripts/office.py batch --file "批量配置.xlsx" --type offer

# 批量生成 Offer + On Board Notice
python scripts/office.py batch --file "批量配置.xlsx" --type both
```

### 7. 自动更新 Vacancy List

新员工入职、离职或调岗时，自动更新 Vacancy List 编制表。

**命令示例：**
```bash
# 新员工入职 → 添加到编制
python scripts/office.py vacancy --action add --name "徐佳琪" --department "人力资源部" --position "人力资源文员"

# 员工离职 → 标记删除
python scripts/office.py vacancy --action remove --name "张三"

# 员工调岗 → 更新部门/职位
python scripts/office.py vacancy --action transfer --name "李四" --new-department "餐饮部" --new-position "厨师长"
```

### 8. 变更日志

每次数据修改自动记录到 `logs/changes_YYYY-MM.json`：
```json
{
  "timestamp": "2026-04-15T19:30:00",
  "operator": "AustinXU",
  "action": "update",
  "target": "annual_leave",
  "employee": "张三",
  "old_value": 10,
  "new_value": 15,
  "affected_files": ["薪资分析20260330.xlsx", "202604 Vacancy List.xls"]
}
```

## 依赖

```bash
pip install python-docx openpyxl xlrd msoffcrypto-tool pandas gitpython reportlab
```

## 模板文件

- `assets/offer_template.docx` — Offer Letter模板（从 `01_Offer与入职/` 复制）
- `assets/onboard_template.docx` — On Board Notice模板（从 `01_Offer与入职/` 复制）
