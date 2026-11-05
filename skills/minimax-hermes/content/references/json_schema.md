# MiniMax Hermes 数据结构规范

本文档定义记忆体系统中使用的数据结构和 JSON Schema。

---

## Session Notes Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Session Notes",
  "type": "object",
  "required": ["created", "task_id", "status"],
  "properties": {
    "created": {
      "type": "string",
      "format": "date-time",
      "description": "会话创建时间"
    },
    "task_id": {
      "type": "string",
      "pattern": "^T-\\d+$",
      "description": "任务唯一标识符"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "in_progress", "completed", "blocked"],
      "description": "当前任务状态"
    },
    "current_focus": {
      "type": "string",
      "description": "当前主要工作内容"
    },
    "progress": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["done", "description"],
        "properties": {
          "done": { "type": "boolean" },
          "description": { "type": "string" }
        }
      }
    },
    "intermediate_results": {
      "type": "array",
      "items": { "type": "string" }
    },
    "active_constraints": {
      "type": "array",
      "items": { "type": "string" }
    },
    "key_variables": {
      "type": "object",
      "additionalProperties": { "type": "string" }
    },
    "blockers": {
      "type": "array",
      "items": { "type": "string" }
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

---

## Pattern Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pattern Entry",
  "type": "object",
  "required": ["title", "pattern", "confidence"],
  "properties": {
    "title": {
      "type": "string",
      "description": "模式标题"
    },
    "pattern": {
      "type": "string",
      "description": "模式内容，支持 Markdown"
    },
    "confidence": {
      "type": "string",
      "enum": ["unconfirmed", "low", "medium", "high", "validated"]
    },
    "verified_count": {
      "type": "integer",
      "minimum": 0
    },
    "category": {
      "type": "string",
      "enum": ["code-review", "debugging", "communication", "deployment", "api-design", "error-handling"]
    },
    "effectiveness": {
      "type": "object",
      "properties": {
        "metric": { "type": "string" },
        "improvement": { "type": "string" }
      }
    },
    "created": {
      "type": "string",
      "format": "date-time"
    },
    "last_verified": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

---

## Lesson Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Lesson Entry",
  "type": "object",
  "required": ["anti_pattern", "confidence"],
  "properties": {
    "anti_pattern": {
      "type": "string",
      "description": "反模式描述"
    },
    "risk_level": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"]
    },
    "correction": {
      "type": "string",
      "description": "正确的做法"
    },
    "confidence": {
      "type": "string",
      "enum": ["unconfirmed", "low", "medium", "high", "validated"]
    },
    "category": {
      "type": "string",
      "enum": ["docker", "api-design", "security", "database", "deployment", "error-handling"]
    },
    "occurrences": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["date", "description"],
        "properties": {
          "date": { "type": "string", "format": "date" },
          "description": { "type": "string" },
          "root_cause": { "type": "string" }
        }
      }
    },
    "created": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

---

## Metrics Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Metrics Entry",
  "type": "object",
  "required": ["review_date"],
  "properties": {
    "review_date": {
      "type": "string",
      "format": "date-time"
    },
    "task_metrics": {
      "type": "object",
      "properties": {
        "success_rate": { "type": "number" },
        "avg_completion_rounds": { "type": "number" },
        "user_corrections_per_session": { "type": "number" }
      }
    },
    "memory_metrics": {
      "type": "object",
      "properties": {
        "hit_rate": { "type": "number" },
        "pattern_application_rate": { "type": "number" },
        "lesson_avoidance_rate": { "type": "number" }
      }
    },
    "improvements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "date": { "type": "string", "format": "date" },
          "description": { "type": "string" }
        }
      }
    },
    "directives": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

---

## Episode Case Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Episode Case",
  "type": "object",
  "required": ["id", "date", "context", "action", "result"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{3}$",
      "description": "格式: YYYY-MM-XXX"
    },
    "date": {
      "type": "string",
      "format": "date-time"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "context": {
      "type": "string",
      "description": "事件发生的背景和上下文"
    },
    "action": {
      "type": "string",
      "description": "当时采取的具体行动"
    },
    "result": {
      "type": "string",
      "enum": ["success", "partial", "failure"]
    },
    "root_cause_analysis": {
      "type": "string",
      "description": "如果失败或部分成功，分析根本原因"
    },
    "pattern_extracted": {
      "type": "string",
      "description": "从这次经验中提取的可复用模式"
    },
    "confidence": {
      "type": "string",
      "enum": ["unconfirmed", "low", "medium", "high", "validated"]
    },
    "verified_count": {
      "type": "integer",
      "minimum": 0
    }
  }
}
```

---

## 用户偏好 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "User Preferences",
  "type": "object",
  "required": ["last_updated"],
  "properties": {
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "code_style": {
      "type": "object",
      "properties": {
        "comments": { "type": "string" },
        "indentation": { "type": "string" },
        "line_length": { "type": "integer" }
      }
    },
    "communication": {
      "type": "object",
      "properties": {
        "response_language": { "type": "string" },
        "detail_level": { "type": "string" },
        "tone": { "type": "string" }
      }
    },
    "task_handling": {
      "type": "object",
      "properties": {
        "task_order_preference": { "type": "string" },
        "confirmation_before_destructive": { "type": "boolean" },
        "progress_report_interval": { "type": "string" }
      }
    }
  }
}
```
