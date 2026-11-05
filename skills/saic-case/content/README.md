# 市场监督管理投诉举报案件处理技能（saic-case）

基于《市场监督管理投诉举报处理办法》（国家市场监督管理总局令第121号，2026年4月15日施行）构建的专业技能，辅助处理市场监管投诉举报案件。

## 📌 功能概览

| 功能模块 | 说明 |
|---------|------|
| 🔍 **案件材料审查** | 对照《办法》第10-11条，核查投诉/举报材料是否齐备 |
| 📝 **投诉书/举报书起草** | 根据《办法》规定的形式要件，起草规范化文书 |
| 🗺️ **管辖判断** | 依据第13-14条（投诉）、第29-33条（举报）确定管辖部门 |
| ⏱️ **时限监控** | 跟踪7日受理、60日调解、15日核查等关键节点 |
| ✅ **程序合规检查** | 对照《办法》全文，检查各环节程序是否合法 |
| 🔎 **违法线索研判** | 分析涉嫌违反的市场监督管理法律法规条款 |
| 🎯 **举报策略优化** | 根据第35条重复举报规则，优化举报策略 |
| ⚠️ **恶意索赔识别** | 依据第16条、第42条，识别和应对恶意索赔行为 |

## 📂 目录结构

```
saic-case/
├── SKILL.md                           # 技能主说明文件（含Frontmatter元数据）
├── README.md                          # 本文件
├── LICENSE                            # MIT License
├── metadata.json                      # 包元数据（版本、作者、依赖等）
├── references/
│   ├── legal_provisions.md           # 重点条款逐条解读
│   ├── jurisdiction_rules.md          # 投诉/举报管辖规则详解
│   ├── key_deadlines.md               # 关键时限汇总表
│   └── bad_claims_rules.md            # 恶意索赔认定与规制规则
├── templates/
│   ├── complaint_template.md          # 投诉书参考模板
│   └── report_template.md             # 举报书参考模板
└── scripts/
    └── complaint_analyzer.py           # 核心Python脚本
```

## 🔧 安装方式

### 方式一：手动安装

将整个 `saic-case` 目录复制到 `~/.openclaw/skills/` 目录下：

```bash
cp -r saic-case ~/.openclaw/skills/
```

### 方式二：OpenClaw CLI 安装

```bash
openclaw skills install saic-case
```

## 📖 使用方法

### 在对话中直接调用

当对话涉及以下关键词时，技能自动激活：
> **投诉、举报、市场监管、市场监督投诉、举报材料、投诉举报办理、市场监管投诉举报案件**

### Python脚本调用

```python
import sys
sys.path.append('/path/to/saic-case/scripts')

from complaint_analyzer import (
    review_complaint,           # 投诉材料审查
    generate_complaint_letter, # 生成投诉书
    generate_report_letter,     # 生成举报书
    determine_jurisdiction,     # 管辖判断
    calculate_deadlines,        # 时限计算
    check_procedure_compliance, # 程序合规检查
    analyze_violation,          # 违法线索分析
)
```

### 示例

#### 投诉材料审查

```python
from complaint_analyzer import review_complaint

result = review_complaint({
    "complainant_info": {
        "name": "张三",
        "phone": "13800138000",
        "address": "北京市朝阳区"
    },
    "respondent_info": {
        "name": "某超市",
        "address": "北京市海淀区"
    },
    "claim": "退货退款并赔偿500元",
    "facts": "2026年4月1日在该超市购买牛奶，发现已过期",
    "evidence": ["购物小票", "过期牛奶照片"],
    "consumer_purpose": True   # 是否为生活消费需要
})

print(f"可受理: {result.is_acceptable}")
print(f"缺失材料: {result.missing_materials}")
print(f"风险提示: {result.risk_warnings}")
print(f"建议: {result.suggestions}")
```

#### 管辖判断

```python
from complaint_analyzer import determine_jurisdiction

# 平台内经营者（公示地址无法联系）
result = determine_jurisdiction(
    case_type="complaint",
    respondent_type="platform_seller",
    respondent_address={
        "displayed": "北京市朝阳区",
        "actual_contactable": False
    }
)

print(f"管辖部门: {result.primary_authority}")
print(f"法律依据: {result.legal_basis}")
```

#### 违法线索分析

```python
from complaint_analyzer import analyze_violation

result = analyze_violation(
    facts=["购买牛奶后发现过期", "超市拒绝赔偿"],
    case_context="消费者在超市购买食品后发现过期"
)

print(f"涉嫌违法类型: {result.violation_type}")
print(f"涉嫌违反条款: {result.suspected_articles}")
print(f"建议: {result.report_suggestion}")
```

## 📚 法律依据

本技能基于以下法律法规构建：

| 法规 | 说明 |
|------|------|
| 《市场监督管理投诉举报处理办法》（总局令第121号） | 2026年4月15日施行，核心依据 |
| 《中华人民共和国消费者权益保护法》 | 消费者权益保护基本法 |
| 《中华人民共和国消费者权益保护法实施条例》 | 2024年施行，细化消费者权益保护 |
| 《市场监督管理行政处罚程序规定》 | 举报处理程序的衔接规定 |
| 《治安管理处罚法》第49条 | 恶意索赔涉嫌违法时的法律后果 |
| 《刑法》第266条、第274条 | 诈骗罪、敲诈勒索罪 |

## ⚠️ 注意事项

1. 本技能依据2026年4月15日施行的总局令第121号构建，请确认当地执行版本
2. 投诉须证明"为生活消费需要"（第16条第3项），生产经营目的不受保护
3. 举报须提供"具体线索和事实依据"（第28条），空洞举报不予受理
4. 重复举报同一事实不再处理，但补充新事实可合并处理（第35条）
5. 涉嫌敲诈勒索、夹带掉包造假等行为须移送公安机关（第42条）
6. 调解须双方同意，任何一方拒绝则不能强制调解（第18条）
7. 本技能仅提供辅助法律参考，不构成正式法律意见

## 📄 许可证

MIT License

## 🔖 版本历史

- **v1.0.0** (2026-04-14) — 初始版本，支持投诉举报案件处理全流程
