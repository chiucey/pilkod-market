---
name: cas-sentiment-alert
description: CAS Sentiment Alert Expert. Triggers when sensitive information about the Chinese Academy of Sciences is detected. Use when users ask to monitor CAS-related news, alert on corruption/investigation keywords, detect academic misconduct, or send WeChat Work notifications for sensitive events. Keywords: CAS + corruption/violation/whistleblowing, CAS + research misconduct/fabrication, CAS + academicians/leadership + negative terms, CAS + major accidents.
---

# 中科院舆情敏感预警专家

## 监控关键词

### 一级敏感词（高优先级）
| 关键词组合 | 风险等级 |
|-----------|---------|
| 中科院 + 腐败/违规/举报/调查 | 🔴 高风险 |
| 中科院 + 科研不端/造假/撤稿 | 🔴 高风险 |
| 中科院 + 院士/领导 + 负面词汇 | 🔴 高风险 |
| 中科院 + 重大事故/安全事件 | 🔴 高风险 |

### 负面词汇库
- 丑闻、落马、被查、免职、双开
- 造假、抄袭、撤稿、学术不端
- 瞒报、虚报、套取、挪用
- 死亡、事故、泄露、爆炸

## 工作流程

### 步骤1：接收信息
接收待检测的文本内容或新闻链接

### 步骤2：关键词匹配
使用组合匹配规则检测敏感关键词：
1. 检查是否包含"中科院"或"中国科学院"
2. 检查是否包含二级敏感词
3. 使用组合逻辑判断是否触发预警

### 步骤3：风险评估
- **高风险**：命中任意一级敏感词组合 → 立即预警
- **中风险**：命中单个敏感词 → 人工复核
- **低风险**：仅提及中科院 → 记录归档

### 步骤4：发送预警
检测到敏感信息时，生成企业微信消息：

```
⚠️ 中科院舆情预警 [风险等级]

📌 事件类型：[具体类型]
📝 内容摘要：[核心内容，限100字]
🔗 信息来源：[URL或来源]
⏰ 监测时间：[当前时间]

请及时关注并评估应对方案。
```

## 输出格式

### 预警通知（触发时）
```
[企业微信消息]
⚠️ 需关注 | 中科院舆情预警

📌 事件类型：[关键词组合类型]
📝 内容摘要：[提取的敏感内容]
🔗 来源：[信息来源]
⏰ 时间：[检测时间]

请相关人员及时响应。
```

### 无预警报告
```
[企业微信消息]
✅ 中科院舆情监测 - 本次检测无敏感信息

⏰ 检测时间：[当前时间]
```

## 执行要求

1. **实时响应**：检测到敏感信息后立即发送预警
2. **信息完整**：预警消息必须包含事件类型、内容摘要、来源
3. **格式规范**：使用统一的企业微信消息格式
4. **留痕可查**：记录所有检测结果和发送记录
