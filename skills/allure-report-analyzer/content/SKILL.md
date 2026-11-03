---
name: allure-report-analyzer
description: 自动分析 Allure 测试报告执行结果。当用户要求分析测试报告、提取测试执行数据、生成测试趋势报告、诊断测试失败原因或生成测试质量评估时使用。
---

# Allure 测试报告分析器

## 技能概述

本技能用于自动化解析和分析 Allure 测试报告，支持从 JSON/HTML 报告中提取关键测试执行数据，生成统计摘要、失败分析和趋势报告。

## 核心功能

### 1. 数据提取

**支持的数据源：**
- `allure-report/` 目录（JSON 格式）
- 单个 `allure-results/` 目录
- 已解压的 Allure HTML 报告

**提取内容：**
- 测试套件统计（总数、通过、失败、跳过）
- 测试用例详细列表（按状态分组）
- 耗时分析（最慢测试、平均执行时间）
- 标签和分类统计

### 2. 统计分析

```
总测试数: N
通过率: XX%
失败: N (原因分类)
跳过: N
重试: N
```

**状态分类：**
- `passed` - 通过
- `failed` - 失败
- `skipped` - 跳过
- `broken` - 损坏/错误

### 3. 失败分析

**失败原因分类：**
- 断言失败（AssertionError）
- 异常捕获（Exception）
- 超时（Timeout）
- 前置条件失败（Assumption）

**输出格式：**
```json
{
  "total_failures": N,
  "by_type": {
    "assertion": N,
    "exception": N,
    "timeout": N,
    "assumption": N
  },
  "failure_details": [
    {
      "test_name": "xxx",
      "message": "xxx",
      "stack_trace": "..."
    }
  ]
}
```

### 4. 趋势分析

支持多历史报告对比：
- 通过率趋势图
- 测试数量变化
- 失败率趋势
- 执行时间变化

## 使用方式

### 基本命令

```
分析当前目录的 Allure 报告：
allure-analyze

分析指定路径：
allure-analyze --path /path/to/allure-report

生成详细报告：
allure-analyze --verbose

输出 JSON 格式：
allure-analyze --format json

多报告趋势分析：
allure-analyze --compare report1/ report2/ report3/
```

### 集成到 CI/CD

```bash
# 集成到 CI 流程
allure generate ./allure-results -o ./allure-report
allure-analyze --path ./allure-report --output ci-report.json
```

## 技术实现

### 报告结构解析

```
allure-report/
├── data/
│   ├── test-cases.json      # 测试用例详情
│   ├── suites.json           # 测试套件信息
│   ├── categories.json       # 失败分类
│   ├── timeline.json         # 时间线
│   └── history/              # 历史趋势数据
├── plugins/
└── widgets/
```

### 核心解析逻辑

```python
def parse_allure_report(report_path):
    """
    解析 Allure 报告目录
    """
    report_data = {
        'summary': parse_summary(report_path),
        'test_cases': parse_test_cases(report_path),
        'categories': parse_categories(report_path),
        'history': parse_history(report_path)
    }
    return report_data

def parse_test_cases(report_path):
    """
    解析测试用例数据
    - 遍历 data/test-cases.json
    - 按状态分组统计
    - 提取失败详情
    """
    pass

def generate_analysis_report(data):
    """
    生成分析报告
    - 统计摘要
    - 失败分析
    - 趋势图表（可选）
    """
    pass
```

## 输出示例

### 终端输出

```
==============================================
     Allure 测试报告分析结果
==============================================

📊 执行摘要
   总测试数: 150
   通过: 142 (94.67%)
   失败: 5 (3.33%)
   跳过: 3 (2.00%)

⏱️ 执行时间
   总耗时: 12m 34s
   平均: 5.0s/测试
   最慢: login_timeout (45.2s)

❌ 失败测试 (5)
   1. test_user_login [AssertionError]
      预期: 200, 实际: 401
   2. test_api_data_sync [TimeoutError]
      连接超时 30s
   3. test_payment_process [Exception]
      NullPointerException

⚠️ 建议改进
   1. 检查认证 API 稳定性
   2. 增加网络超时重试机制
   3. 修复支付模块空指针问题
```

### JSON 输出

```json
{
  "generated_at": "2026-04-15T20:09:09Z",
  "summary": {
    "total": 150,
    "passed": 142,
    "failed": 5,
    "skipped": 3,
    "pass_rate": 94.67
  },
  "failures": {
    "by_category": {
      "assertion": 2,
      "timeout": 2,
      "exception": 1
    },
    "details": [...]
  },
  "recommendations": [
    "检查认证 API 稳定性",
    "增加网络超时重试机制"
  ]
}
```

## 依赖要求

- Python 3.8+
- 标准库: `json`, `pathlib`, `datetime`
- 可选: `pandas` (趋势分析)

## 扩展功能

### 1. 自定义分类规则

```yaml
categories:
  - name: "网络问题"
    pattern: ".*(timeout|connection|network).*"
  - name: "数据问题"
    pattern: ".*(null|none|missing data).*"
```

### 2. Webhook 通知

支持将分析结果发送到：
- Slack
- 企业微信
- 钉钉
- 邮件

### 3. 趋势可视化

生成趋势图表：
- 通过率折线图
- 失败分布饼图
- 执行时间柱状图

## 最佳实践

1. **定期运行**: 在每次 CI 构建后自动运行分析
2. **历史积累**: 保存历史报告数据用于趋势分析
3. **失败追踪**: 对重复失败的测试建立专项跟踪
4. **性能监控**: 关注执行时间异常增长的测试
5. **分类优化**: 根据项目特点自定义失败分类规则

## 常见问题

**Q: 如何处理大型报告？**
A: 使用流式解析，大文件自动分批处理

**Q: 支持哪些报告格式？**
A: JSON（原生）、HTML（已生成报告）、ZIP（压缩报告）

**Q: 如何自定义分析规则？**
A: 提供 `config.yaml` 配置文件支持自定义

---

**作者**: MiniMax Agent
**版本**: 1.0.0
**更新**: 2026-04-15
