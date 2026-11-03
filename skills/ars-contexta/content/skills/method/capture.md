# /capture — 快速捕获模块

## 功能说明
将想法、灵感、临时笔记写入 inbox，不追求完美格式。

## 使用方式
```
/capture [内容]
```

## 执行步骤

### Step 1: 解析捕获内容
- 提取用户提供的原始内容
- 添加时间戳
- 生成文件名： `{YYYY-MM-DD}-{slug}.md`

### Step 2: 创建 inbox 文件
保存位置：`vault/notes/inbox/{filename}.md`

文件格式：
```markdown
---
title: "捕获标题"
created: "YYYY-MM-DD HH:mm:ss"
source: capture
tags: []
---

原始内容...
```

### Step 3: 输出确认
```
📝 /capture 完成
━━━━━━━━━━━━
已写入 inbox：{filename}.md
提示：运行 /reduce 将其转化为原子笔记
```

## 示例

```
用户：/capture 关于Transformer架构的自注意力机制理解
→ 创建 vault/notes/inbox/2026-04-11-transformer自注意力.md
→ 输出捕获确认
```

## 注意事项
- inbox 文件保持原样，不做结构化处理
- 格式不完美没关系，后续 /reduce 会处理
- 建议捕获时添加简短标题
