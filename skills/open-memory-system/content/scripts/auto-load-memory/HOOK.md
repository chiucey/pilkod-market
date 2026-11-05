---
name: auto-load-memory
description: "会话启动时自动加载核心记忆"
metadata:
  {
    "openclaw": {
      "emoji": "💾",
      "events": ["session:start", "agent:bootstrap"],
      "requires": {}
    }
  }
---

# Auto Load Memory Hook

会话开始时自动加载记忆文件到上下文。

## 功能
1. 读取 MEMORY.md 长期记忆
2. 读取今日 short-term 日志
3. 读取 preferences 摘要
