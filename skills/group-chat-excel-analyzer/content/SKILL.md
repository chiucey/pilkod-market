---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e4d5cfbe282ed9b389d376193e1a3dee
    PropagateID: e4d5cfbe282ed9b389d376193e1a3dee
    ReservedCode1: 30440220190a6179ff3271319569fbbe5aa0bd4772923d61b83e4e7e7ec3a81bf3970dac02203cd674731bf149f89cf0329d5de941815be6993fb7a828767e12a487fd248011
    ReservedCode2: 3046022100d501e1c936fb63b78f7533ea102d4110417fccbba1656940cf6ce8b4cf8cf802022100f94402e8d49e4e8a18110d522b3345db7a4dd3a94977ce09af30efbd1ee70f80
description: Deep analysis skill for WeChat group chat Excel exports. Automatically extracts topics, identifies all shared links, recognizes external figures (tech entrepreneurs, AI researchers, influencers), and generates time-period topic summaries. Use when users upload chat Excel exports and request analysis.
name: group-chat-excel-analyzer
---

# 群聊Excel深度分析 Skill

## 技能触发条件

用户上传微信群聊导出的Excel表格，并要求分析聊天内容、提取话题、识别人物、整理链接。

## 输入数据格式

Excel中至少包含以下字段：
- 发言时间
- 发言用户/昵称
- 发言内容

## 核心分析规则

### 1. 链接完整提取（必须全部列出）

从聊天内容中提取所有URL链接，按时间排序完整输出，格式：
```
序号. 时间 | 发送者
   链接地址
```

### 2. 外部人物识别（非群成员）

识别以下类型的外部人物：
- **AI科技企业家**：奥特曼(Sam Altman)、马斯克、皮查伊、黄仁勋、苏姿丰、马云、马化腾、张一鸣、字节、李开复、陆奇、李彦宏、雷军等
- **AI学者/研究人员**：李飞飞、吴恩达、Hinton、杨立昆、LeCun、Ilya、唐杰等
- **网红/博主**：宝玉、苏林、李一诺、霍氚、少楠、何同学、回形针、巫师财经等

### 3. 按时间段的话题概述

**分析策略**：
1. 按30分钟时段聚合消息
2. 筛选高活跃时段（消息量>=15条或高于平均1.5倍）
3. 对每个高活跃时段提取：
   - 时间范围
   - 消息数量
   - 参与人数
   - 识别的话题标签
   - 代表性发言（去重）

**话题标签类型**：
- Gemini 3.5泄漏
- 奥特曼遇袭事件
- Claude参数泄露
- DeepSeek测试/讨论
- 数学竞赛AI
- 豆包/Kimi产品
- 开源模型
- 产品体验
- 投资理财
- 新闻热点

### 4. 过滤废物信息

以下内容不输出：
- 群成员@提及（只关注外部人物）
- 表情包/图片消息
- 撤回消息标记
- 纯表情符号
- 太短的无效消息

## 输出格式

### 【外链分享完整列表】
总链接数: X

序号. 时间 | 发送者
   链接地址

### 【聊天中提到的外部人物/博主/网红】

【AI科技企业家】
  - 人物名: X次

【AI学者/研究人员】
  - 人物名: X次

### 【每日话题概述】

============================================================
📅 YYYY-MM-DD | 当日消息: X条
============================================================

⏰ 【话题N】HH:MM-HH:MM | 💬X条 | 👥X人
   🏷️ 话题: 标签1, 标签2
   📝 代表发言:
      • 发言内容摘要1
      • 发言内容摘要2

## 注意事项

1. 链接必须100%完整列出，一个不漏
2. 人物识别只关注外部人物，不输出群成员
3. 话题概述要体现群友讨论的核心观点
4. 每天至少提取10个高活跃话题
5. 去除引用格式"[引用 xxx]"和表情标记
6. 发言摘要保留有意义的讨论内容，过滤水话
