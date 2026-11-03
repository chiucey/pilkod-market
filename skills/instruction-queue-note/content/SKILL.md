---
name: instruction-queue-note
description: 将用户的大型复杂需求自动拆分为有序可执行的短指令队列，驱动AI自动连续执行全流程。Use when users ask to write long novels, create series content, batch process data, or complete multi-step complex tasks that exceed single AI output limits.
---

# 指令队列便签（Instruction Queue Note）

## 功能概述

智能指令拆分与自动执行引擎。接收用户的复杂长任务需求，自动拆分为可分步执行的标准化指令队列，驱动AI自动按序执行每条指令，自动拼接上下文确保连贯性，最终聚合所有结果输出完整交付物。

**核心能力：突破AI单次输出长度限制，实现"一次输入，完本交付"**

## 工作流程

1. **需求解析** - 接收用户的长周期任务需求
2. **智能拆分** - 自动拆分为符合执行逻辑的有序指令队列
3. **循环执行** - 按顺序自动执行每条指令
4. **上下文传递** - 自动拼接前序结果作为后续上下文
5. **结果聚合** - 执行完成后自动合并所有产出为完整文档

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_prompt | string | 是 | - | 用户的原始完整需求，越详细执行效果越好 |
| task_id | string | 否 | null | 任务ID，用于断点续跑 |
| model_name | string | 否 | doubao-pro-32k | 执行使用的模型名称 |
| base_url | string | 否 | 平台默认 | API地址 |
| max_retry_times | integer | 否 | 3 | 最大重试次数 |
| auto_merge_result | boolean | 否 | true | 是否自动聚合结果 |
| verbose_logging | boolean | 否 | true | 是否输出详细日志 |

## 输出格式

```json
{
  "success": true,
  "task_id": "task_1234567890",
  "user_prompt": "用户原始需求",
  "total_steps": 10,
  "completed_steps": 10,
  "progress_percentage": 100,
  "final_result": "完整聚合结果",
  "result_file": "./task_queue/task_xxx_final_result.md",
  "queue_file": "./task_queue/task_xxx.json"
}
```

## 适用场景

### 内容创作类
- 长篇小说、多章节故事、完整剧本
- 系列课程、培训课件、书籍编写
- 漫画脚本、系列文章批量创作

### 批量处理类
- 多模块项目代码开发
- 批量数据处理与分析
- 系列营销文案生成

### 复杂任务类
- 需要多步骤协作的系统搭建
- 长周期、需要上下文连贯的大型任务
- 任何超过AI单次输出能力的工作

## 使用示例

### 示例1：创作长篇小说
```
输入：写一本10章的校园小说，每章约5000字，主题是成长与梦想
执行：自动拆分为"写大纲 + 10章节写作"共11条指令，自动按序执行
输出：完整10章小说全文 + 执行报告
```

### 示例2：断点续跑
```
输入：task_id="task_1234567890"
执行：从上次中断处继续执行
输出：补充执行结果，更新最终文档
```

## 状态管理

- `pending`: 待执行
- `running`: 执行中
- `completed`: 已完成
- `failed`: 执行失败（可重试）
- `skipped`: 已跳过

## 注意事项

1. 任务状态实时持久化到本地，中断后可恢复
2. 每条指令执行失败会自动重试（最多3次）
3. 上下文超限时自动压缩，保障长任务稳定执行
4. 最终结果自动保存为Markdown文件，方便查阅
