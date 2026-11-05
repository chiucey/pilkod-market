---
name: 工程造价
version: "1.0.0"
description: "R0-R8 全链路造价机器人系统。自动完成识图→算量→询价→组价→审核→报告→终审→归档全流程，基于GB50500-2013清单计价规范。"
author: 迈小胖 & 陈坚
created: "2026-05-08"
metadata:
  tags: [engineering, cost, construction, budget, BOQ, pricing, audit, R0-R8]
  category: professional-domain
  languages: [python]
  required_binaries:
    - python  # >=3.10
    - uvicorn  # HTTP服务运行时
---

# 工程造价 — R0-R8 多机器人协作造价预算系统

## 一句话说明

上传图纸/描述项目 → 自动完成**识图→算量→询价→组价→审核→报告→终审→归档**八步闭环，输出专业造价报告。

## 系统架构

```
用户指令 / 图纸文件
       │
       ▼
 ┌─────────────┐
 │  R0 总控中枢  │ ◄── 自然语言入口、DAG编排、任务分发
 │   :8000      │
 └──────┬──────┘
        │ Redis队列调度
   ┌────┼────┬────┬────┐
   ▼    ▼    ▼    ▼    ▼
  R1   R2   R3   R4   R5     R6    R7    R8
 识图  算量  询价  组价  审核   报告  终审  归档
 :8001 :8002 :8003 :8004 :8005  :8006 :8007 :8008
```

**数据流水线**: `图纸(R1) → 构件数据 → BOQ清单(R2) → 单价(R3) → 完整造价(R4) → 审核报告(R5) → Word/Excel(R6) → 终审批复(R7) → 档案沉淀(R8)`

## 适用场景

| 场景 | 说明 |
|------|------|
| 土建/安装预算 | 新建项目工程量计算+组价 |
| 结算审核 | 已有造价数据的合规性审核 |
| 招投标报价 | 快速生成清单报价 |
| 图纸算量 | DWG/PDF/IFC图纸自动提取构件+计算工程量 |
| 材料询价 | 建材市场价格查询+异常检测 |
| 造价报告 | 专业Word/Excel咨询报告一键生成 |
| 项目归档 | 全生命周期档案管理+版本控制+知识沉淀 |

## 快速启动

### 方式一：逐个启动机器人（开发调试）

```bash
# 终端1 - R0 总控（可选，用于DAG编排模式）
cd r0-controller && uvicorn app.main:app --reload --port 8000

# 终端2-9 - 各机器人HTTP API模式
cd r1-reader && uvicorn app.main:app --reload --port 8001
cd r2-quantity && uvicorn app.main:app --reload --port 8002
cd r3-pricing && uvicorn app.main:app --reload --port 8003
cd r4-costing && uvicorn app.main:app --reload --port 8004
cd r5-review && uvicorn app.main:app --reload --port 8005
cd r6-report && uvicorn app.main:app --reload --port 8006
cd r7-final && python -m app.main --port 8007
cd r8-archive && python -m app.main --port 8008
```

### 方式二：Worker模式（生产环境，Redis队列驱动）

```bash
# Worker模式下各机器人监听Redis队列，由R0统一调度
cd r1-reader && python -m app.main --worker
cd r2-quantity && python -m app.main --worker
# ... 以此类推 R3-R8
```

### 方式三：单次API调用（推荐用于本技能）

直接调用各机器人的HTTP API，无需启动全部服务。按需启动对应机器人即可：

```bash
# 只做算量？只需启动R2
cd r2-quantity && uvicorn app.main:app --port 8002 &

# 做完整流程？按顺序启动 R1→R2→...→R8，依次调用
```

### 前置依赖

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| Python ≥3.10 | 运行时 | 系统已配 |
| FastAPI + Uvicorn | Web框架 | `pip install fastapi uvicorn` |
| Redis (可选) | 队列通信(Worker模式) | Docker或本地安装 |
| python-docx | Word报告(R6) | `pip install python-docx` |
| openpyxl | Excel报告(R6) | `pip install openpyxl` |
| ezdxf | DWG解析(R1) | `pip install ezdxf` |
| ifcopenshell | IFC解析(R1) | `pip install ifcopenshell` |

## 核心工作流

### 工作流A：全自动流水线（推荐）

适用场景：从图纸开始的全流程造价

```
Step 1: R1 识图 — 上传图纸文件(DWG/PDF/IFC)，自动提取构件
Step 2: R2 算量 — 消费R1构件数据，自动计算工程量BOQ
Step 3: R3 询价 — 消费R2的BOQ，查询材料/人工/机械单价
Step 4: R4 组价 — 融合R2工程量+R3单价，按GB50500-2013五级取费
Step 5: R5 审核 — 对R4造价进行五维度合规性审核
Step 6: R6 报告 — 生成Word/Excel专业造价咨询报告
Step 7: R7 终审 — 人机协同多级审批（可AI自动通过）
Step 8: R8 归档 — 全生命周期档案管理+知识沉淀
```

### 工作流B：单步调用

适用场景：只需要某一环节的能力

| 你需要 | 调用哪个 | 输入 | 输出 |
|--------|----------|------|------|
| 提取构件信息 | **R1 识图** | 图纸文件路径/DWG/PDF/IFC | ComponentItem列表 |
| 计算工程量 | **R2 算量** | 构件列表(或手动填写) | BOQ清单+明细 |
| 查材料价格 | **R3 询价** | BOQ项目名列表 | 单价+置信度+异常标记 |
| 完整组价 | **R4 组价** | BOQ工程量+单价 | 五级费用造价表 |
| 造价审核 | **R5 审核** | R4造价数据 | 审核评分(A-E)+问题清单 |
| 生成报告 | **R6 报告** | R5审核结果 | Word+Excel文件 |
| 审批流转 | **R7 终审** | R5/R6产出 | 审批结论+操作记录 |
| 项目归档 | **R8 归档** | 全流程数据 | 档案目录+版本+统计 |

### 工作流C：R0总控编排（自然语言入口）

用户用自然语言描述项目需求，R0自动完成NLU解析→模板匹配→DAG构建→分发执行：

```bash
# POST http://localhost:8000/api/v1/projects/create
{
  "user_input": "接了个新项目，XX小区3号楼土建预算，建筑面积12000平米",
  "priority": "normal"
}
# → R0自动创建DAG，分发到R1-R8，通过WebSocket推送进度
```

## API调用速查

### R1 识图 (`http://localhost:8001`)

```bash
# 按路径识别
curl -X POST http://localhost:8001/api/v1/recognize \
  -F "file_path=/path/to/building.dwg" \
  -F 'extract_targets=["梁","板","柱","墙","门窗","楼梯"]'

# 上传文件识别
curl -X POST http://localhost:8001/api/v1/recognize/upload \
  -F "file=@/path/to/building.dwg" \
  -F 'extract_targets=["梁","板","柱","墙","门窗","楼梯"]'
```

**输出**: `ComponentItem[]` (component_id/type/sub_type/name/location/尺寸/混凝土标号等)

支持构件类型：**梁、板、柱、墙、门窗、楼梯**

### R2 算量 (`http://localhost:8002`)

```bash
# 核心接口：单次算量
curl -X POST http://localhost:8002/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK-001",
    "project_name": "示例项目",
    "components": [
      {
        "component_type": "梁", "sub_type": "框架梁KL",
        "name": "KL-1", "length": 6.0, "width": 0.25,
        "depth": 0.5, "concrete_grade": "C30", "count": 1
      }
    ]
  }'

# 批量算量
curl -X POST http://localhost:8002/api/v1/calculate/batch \
  -H "Content-Type: application/json" \
  -d '{"tasks": [...]}'
```

**输入模型 (ComponentItem)**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| component_id | str | ✅ | 唯一标识 |
| component_type | str | ✅ | 梁/板/柱/墙/门窗/楼梯 |
| sub_type | str | ❌ | 子类型(如框架梁KL/剪力墙等) |
| name | str | ❌ | 构件名称/编号 |
| length | float | ❌ | 长度(m) |
| width | float | ❌ | 宽度(m) |
| height/depth | float | ❌ | 高度/截面高(m) |
| concrete_grade | str | ❌ | C30/C40等 |
| count | int | ❌ | 数量(默认1) |

**输出**: `QuantityTaskResult` (boq清单 + 按构件分类明细 + 统计)

### R3 询价 (`http://localhost:8003`)

```bash
# 批量询价（核心）
curl -X POST http://localhost:8003/api/v1/price \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "示例项目",
    "region": "全国",
    "boq_items": [
      {"code": "010503001", "name": "C30混凝土", "unit": "m³", "quantity": 100},
      {"code": "010504001", "name": "HRB400钢筋", "unit": "t", "quantity": 45.8}
    ]
  }'

# 搜索价格库
curl -X POST http://localhost:8003/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "混凝土C30", "price_type": "material"}'

# 查看价格库信息
curl http://localhost:8003/api/v1/database
```

**内置价格库覆盖**: 混凝土C20-C50、钢筋HPB300-HRB500、模板、门窗、人工费、机械费（25+条目）

**输出字段重点**：
- `unit_price` — 单价
- `confidence` — high/medium/low
- `alert_level` — normal/warning/critical（偏离>15%警告，>30%严重）
- `source` — local_db/online_api/historical/manual

### R4 组价 (`http://localhost:8004`)

```bash
# 完整组价
curl -X POST http://localhost:8004/api/v1/cost \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK-001",
    "project_name": "示例项目",
    "building_no": "3号楼",
    "region": "全国",
    "building_area": 12000,
    "boq_items": [ /* R2的BoqItem */ ],
    "pricing_items": [ /* R3的PricingResultItem */ ]
  }'

# 简化组价（使用内置默认数据）
curl -X POST http://localhost:8004/api/v1/cost/simple

# 查看取费结构
curl http://localhost:8004/api/v1/fee-structure
```

**输出**: `TotalCostBreakdown` — GB50500-2013 五级费用体系：

| 费用级 | 包含内容 |
|--------|----------|
| 一、分部分项工程费 | 直接费(材/工/机) + 管理费(8.5%) + 利润(7%) |
| 二、措施项目费 | 安全文明施工(2.5%) + 超高增加费 + 其他 |
| 三、其他项目费 | 暂列金额 + 暂估价 |
| 四、规费 | 养老20%/医疗8%/失业2%/工伤1%/生育0.8%/公积金10%（以人工费为基数） |
| 五、税金 | 增值税9%（不含税造价×9%） |

**地区系数**: 北京1.15 / 上海1.12 / 广州1.08 / 深圳1.08 / 全国1.0

### R5 审核 (`http://localhost:8005`)

```bash
# 完整审核
curl -X POST http://localhost:8005/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{
    "breakdown": { /* R4 TotalCostBreakdown JSON */ },
    "items": [ /* R4 BoqPricingItem 列表 */ ],
    "project_type": "civil_budget",
    "area": 12000
  }'

# 快速审核（模拟数据）
curl -X POST http://localhost:8005/api/v1/audit/simple

# 获取必须修复的问题
curl http://localhost:8005/api/v1/issues/critical
```

**五维度审核体系**:

| 维度 | 权重 | 检查内容 |
|------|------|----------|
| 合规性 | 35% | 编码规范/取费标准/费率合规 |
| 偏离分析 | 25% | 与历史数据/指标对比偏离度 |
| 异常检测 | — | 价格突变/数量异常/逻辑矛盾 |
| 完整性 | 20% | 必填项/关联项完整性 |
| 逻辑校验 | 20% | 数据一致性/公式正确性 |

**评分等级**: A(≥95) / B(≥85) / C(≥70) / D(≥55) / E(<55)

### R6 报告 (`http://localhost:8006`)

```bash
# 生成完整报告
curl -X POST http://localhost:8006/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "audit_report": { /* R5 AuditReport JSON */ },
    "items": [ /* BOQ 清单项 */ ],
    "format": "both",
    "template_id": "standard",
    "company_name": "XXX造价咨询有限公司",
    "reporter": "张三"
  }'

# 快速生成（模拟数据）
curl -X POST http://localhost:8006/api/v1/generate/simple

# 下载最近生成的报告
curl http://localhost:8006/api/v1/download/word -o report.docx
curl http://localhost:8006/api/v1/download/excel -o report.xlsx
```

**三种模板**:

| 模板 | 内容 | 适用场景 |
|------|------|----------|
| standard | 封面+目录+摘要+评分+问题+偏离+BOQ+结论 (9节) | 常规项目 |
| simple | 封面+摘要+评分+问题+结论 (5节) | 内部快速审查 |
| detailed | 全部分析维度+附录 (14节) | 大型公建/争议项目 |

**输出格式**: `.docx`(Word) + `.xlsx`(Excel)

### R7 终审 (`http://localhost:8007`)

```bash
# 创建终审实例（含AI预审）
curl -X POST http://localhost:8007/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "REQ-001",
    "upstream_report": { /* R5 AuditReport */ },
    "generated_reports": [ /* R6 GeneratedReport */ ],
    "project_name": "示例项目",
    "requester_name": "张三",
    "workflow_template": "standard",
    "enable_ai_pre_review": true
  }'

# 审批操作（通过/驳回/退回/转办）
curl -X POST http://localhost:8007/api/v1/review/{id}/approve \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "comment": "审核通过"}'

# 查看所有终审实例
curl http://localhost:8007/api/v1/instances
```

**四种审批模板**:

| 模板 | 流程 | 时长 | 适用场景 |
|------|------|------|----------|
| standard | AI预审→技术复核→终审 | ~72h | 常规项目 |
| urgent | AI预审→快速终审 | ~5h | 招标/投标 |
| full_process | AI预审→初审→技术会签(并行)→终审 | ~96h | 大型公建/超高层 |
| simple | 仅AI全自动 | ~1h | 小型装修/维修 |

**AI自动决策阈值**: ≥95分自动通过，≤50分自动驳回

### R8 归档 (`http://localhost:8008`)

```bash
# 创建项目档案（自动建标准目录结构）
curl -X POST http://localhost:8008/api/v1/project/create \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "PROJ-2026-001",
    "project_name": "示例项目",
    "project_type": "civil_budget",
    "client_name": "XX地产公司",
    "building_area_sqm": 12000
  }'

# 归档文件
curl -X POST http://localhost:8008/api/v1/file/archive \
  -H "Content-Type: application/json" \
  -d '{"project_id": "...", "file_path": "/path/to/file.pdf", "category": "final_result", "source_robot": "R6"}'

# 版本控制
curl -X POST http://localhost:8008/api/v1/version/create \
  -H "Content-Type: application/json" \
  -d '{"file_record_id": "...", "change_summary": "修订钢筋含量"}'

# 统计汇总
curl http://localhost:8008/api/v1/statistics/summary

# 备份
curl -X POST http://localhost:8008/api/v1/backup/run \
  -H "Content-Type: application/json" \
  -d '{"backup_type": "FULL"}'
```

**自动创建的标准目录**:
```
项目库/{年}/{月}/{项目名}/
├── 01-原始资料/    # 图纸/合同/变更单
├── 02-过程成果/    # R1-R7各阶段产出
├── 03-最终成果/    # 审定版报告
├── 04-沟通记录/    # 会议纪要/邮件往来
└── 05-项目日志/    # 操作审计日志
```

## 项目根路径参考

| 机器人 | 路径 |
|--------|------|
| R0 总控 | `c:/Users/nefujian/WorkBuddy/20260427220324/r0-controller/` |
| R1 识图 | `c:/Users/nefujian/WorkBuddy/20260427220324/r1-reader/` |
| R2 算量 | `c:/Users/nefujian/WorkBuddy/20260427220324/r2-quantity/` |
| R3 询价 | `c:/Users/nefujian/WorkBuddy/20260427220324/r3-pricing/` |
| R4 组价 | `c:/Users/nefujian/WorkBuddy/20260427220324/r4-costing/` |
| R5 审核 | `c:/Users/nefujian/WorkBuddy/20260427220324/r5-review/` |
| R6 报告 | `c:/Users/nefujian/WorkBuddy/20260427220324/r6-report/` |
| R7 终审 | `c:/Users/nefujian/WorkBuddy/20260427220324/r7-final/` |
| R8 归档 | `c:/Users/nefujian/WorkBuddy/20260427220324/r8-archive/` |

## 使用示例

### 示例1：从零完成一个项目的全流程造价

```bash
# Step 1: 启动所需机器人
cd r1-reader && uvicorn app.main:app --port 8001 &
cd r2-quantity && uvicorn app.main:app --port 8002 &
cd r3-pricing && uvicorn app.main:app --port 8003 &
cd r4-costing && uvicorn app.main:app --port 8004 &
cd r5-review && uvicorn app.main:app --port 8005 &
cd r6-report && uvicorn app.main:app --port 8006 &

# Step 2: R1 识图
RESP1=$(curl -s -X POST http://localhost:8001/api/v1/recognize \
  -F "file_path=/path/to/project.dwg" \
  -F 'extract_targets=["梁","板","柱","墙","门窗","楼梯"]')

# Step 3: R2 算量（传入R1的构件数据）
RESP2=$(curl -s -X POST http://localhost:8002/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d "{\"components\": $(echo $RESP1 | jq '.data')}")

# Step 4: R3 询价（传入R2的BOQ）
RESP3=$(curl -s -X POST http://localhost:8003/api/v1/price \
  -H "Content-Type: application/json" \
  -d "{\"boq_items\": $(echo $RESP2 | jq '.data.boq.items'), \"region\": \"全国\"}")

# Step 5: R4 组价（融合R2+R3数据）
RESP4=$(curl -s -X POST http://localhost:8004/api/v1/cost \
  -H "Content-Type: application/json" \
  -d "{\"boq_items\": $(echo $RESP2 | jq '.data.boq.items'),
      \"pricing_items\": $(echo $RESP3 | jq '.data.pricing_items'),
      \"project_name\": \"示例项目\", \"region\": \"全国\"}")

# Step 6: R5 审核
RESP5=$(curl -s -X POST http://localhost:8005/api/v1/audit \
  -H "Content-Type: application/json" \
  -d "{\"breakdown\": $(echo $RESP4 | jq '.data'),
      \"items\": $(echo $RESP4 | jq '.data.partial_item.items')}")

# Step 7: R6 报告
RESP6=$(curl -s -X POST http://localhost:8006/api/v1/generate \
  -H "Content-Type: application/json" \
  -d "{\"audit_report\": $(echo $RESP5 | jq '.data'),
      \"format\": \"both\", \"template_id\": \"standard\",
      \"company_name\": \"XXX造价咨询\", \"reporter\":\"AI\"}")

# 输出报告文件路径
echo $RESP6 | jq '{docx: .data.docx_path, xlsx: .data.xlsx_path}'
```

### 示例2：只用R2算一堵墙的工程量

```bash
curl -X POST http://localhost:8002/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "WALL-001",
    "components": [
      {
        "component_id": "WALL-Q1",
        "component_type": "墙",
        "sub_type": "剪力墙",
        "name": "Q1",
        "location": "1层/①-③轴",
        "length": 12.0,
        "height": 3.6,
        "width": 0.25,
        "concrete_grade": "C35",
        "count": 1
      },
      {
        "component_id": "DOOR-M1",
        "component_type": "门窗",
        "sub_type": "门",
        "name": "M1",
        "width": 1.0,
        "height": 2.1,
        "count": 2
      }
    ]
  }'
# → 自动扣减门洞面积(2×1.0×2.1=4.2m² > 0.3m²)，输出净体积
```

### 示例3：只查价格

```bash
curl -X POST http://localhost:8003/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "HRB400螺纹钢", "price_type": "material"}'
```

## 注意事项

1. **调用顺序**: 流水线必须按 R1→R2→R3→R4→R5→R6→R7→R8 顺序执行，每步依赖上一步的输出
2. **独立调用**: 单个机器人可以独立使用（如只查价用R3，只算量用R2），无需上游数据时可手动构造输入JSON
3. **测试验证**: 每个机器人都有 `/api/v1/.../simple` 或 `/health` 端点可用于快速验证
4. **端口冲突**: 确保8000-8008端口未被占用
5. **规范依据**: 全系统基于 **GB50500-2013《建设工程工程量清单计价规范》**
6. **地区差异**: R4组价支持地区系数调整；R3价格库为全国基准价，实际项目需结合当地信息价修正
