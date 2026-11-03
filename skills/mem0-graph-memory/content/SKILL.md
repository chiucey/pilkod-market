name: mem0-graph-memory
description: mem0 图向量记忆系统。提供跨会话语义检索和图关系联想，直接读写 mem0 (NVIDIA embedding + Qdrant local)。

## 图记忆架构

```
向量模型: NVIDIA nv-embed-v1 (4096维)
向量存储: Qdrant local (/tmp/mem0_qdrant)
用户ID: kirk
CLI入口: /workspace/run_mem0.py
```

## 核心操作

**搜索记忆**
```bash
PYTHONPATH="/tmp/pypackages:$PYTHONPATH" python3 /workspace/run_mem0.py search "<查询内容>" [user_id]
```

**添加记忆**
```bash
PYTHONPATH="/tmp/pypackages:$PYTHONPATH" python3 /workspace/run_mem0.py add "<记忆内容>" [user_id]
```

**列出所有记忆**
```bash
PYTHONPATH="/tmp/pypackages:$PYTHONPATH" python3 /workspace/run_mem0.py list [user_id]
```

## 使用时机

在每次处理需要"回忆过去"的任务时主动调用：
- 用户问到之前聊过什么、决定过什么
- 跨 session 需要延续之前的上下文
- 需要图关系联想的时候

## 执行确认规则

- ✅ 搜索/读取 → 无需确认，直接执行
- ⚠️ 添加记忆 → 需先确认（告诉用户存什么）
- ⚠️ 删除记忆 → 需先确认
