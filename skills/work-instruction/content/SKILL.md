---
name: work-instruction
description: 生成标准格式的作业指导书Word文档，符合公文编写规范，包含固定章节结构和编制审批流程。当用户要求生成作业指导书、编写工作流程文档、制作标准操作规范时使用。
---

# 作业指导书生成技能 v0.0.1

## 功能说明

本技能用于生成符合国家标准格式的作业指导书Word文档，采用公文排版规范，包含完整的章节结构和编制审批流程。

## 文档标准格式

### 固定章节结构

1. **目的** - 说明制定本指导书的目的
2. **适用范围** - 明确适用对象和范围
3. **术语定义** - 关键术语解释
4. **职责分工** - 各方职责说明
5. **作业流程** - 具体操作步骤
6. **所需材料/设备** - 必要资源清单
7. **操作要点/注意事项** - 关键提醒
8. **相关文件** - 引用文件列表
9. **记录表格** - 涉及的记录表单
10. **编制审批** - 签字栏

### 公文格式规范

- 字体：标题用方正小标宋简体/黑体，正文用仿宋
- 字号：标题二号，正文三号
- 行距：固定值28磅
- 页边距：上3.7cm、下3.5cm、左2.8cm、右2.6cm
- 页眉：含文件标题，下加红色分隔线
- 页脚：居中页码（— 1 —格式）

## 使用方法

### 第一步：准备配置文件

根据模板创建配置文件，可直接复制示例：

```yaml
file_info:
  code: "WI-XXX-001"     # 文件编号（必填）
  version: "A/0"         # 版本号（可选，默认A/0）
  date: "2026年3月"      # 生效日期（必填）

title: "请填写作业指导书标题"

sections:
  # 目的（必填）
  purpose: |
    请填写编写本作业指导书的目的。

  # 适用范围（必填）
  scope: |
    请填写本指导书适用的对象和范围。

  # 术语定义（可选）
  definitions:
    - term: "术语1"
      description: "术语解释"

  # 职责分工（可选）
  responsibilities:
    - party: "责任方A"
      duties:
        - "职责1"
        - "职责2"

  # 作业流程（可选）
  processes:
    - name: "流程名称"
      steps:
        - "步骤1"
        - "步骤2"

  # 所需材料/设备（可选）
  materials:
    - name: "材料名称"
      provider: "提供方"
      note: "备注"

  # 注意事项（可选）
  notes:
    - title: "注意事项"
      content: "具体内容"

  # 相关文件（可选）
  references:
    - "相关文件1"

  # 记录表格（可选）
  records:
    - "记录表格1"
```

### 第二步：填写配置

根据实际需求修改配置中的内容：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_info.code` | string | 是 | 文件编号，如 WI-CW-001 |
| `file_info.version` | string | 否 | 版本号，默认 A/0 |
| `file_info.date` | string | 是 | 生效日期 |
| `title` | string | 是 | 文档标题 |
| `sections.purpose` | string | 是 | 目的 |
| `sections.scope` | string | 是 | 适用范围 |
| `sections.definitions` | array | 否 | 术语定义列表 |
| `sections.responsibilities` | array | 否 | 职责分工列表 |
| `sections.processes` | array | 否 | 作业流程列表 |
| `sections.materials` | array | 否 | 所需材料清单 |
| `sections.notes` | array | 否 | 注意事项列表 |
| `sections.references` | array | 否 | 相关文件列表 |
| `sections.records` | array | 否 | 记录表格列表 |

### 第三步：生成文档

配置完成后，技能将自动根据配置文件生成符合标准的Word文档。

## 文件结构

```
work-instruction/
├── SKILL.md              # 本说明文件
├── template.yaml          # 配置模板
└── Example/
    └── sample.yaml        # 示例配置
```
