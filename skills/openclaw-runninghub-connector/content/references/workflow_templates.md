# RunningHub 工作流模板库

## 模板索引

1. [文本到图像生成](#1-文本到图像生成)
2. [批量内容处理](#2-批量内容处理)
3. [多模态管道](#3-多模态管道)
4. [条件分支工作流](#4-条件分支工作流)
5. [定时任务工作流](#5-定时任务工作流)
6. [API 集成工作流](#6-api-集成工作流)
7. [聊天机器人](#7-聊天机器人)
8. [数据提取与转换](#8-数据提取与转换)
9. [图像批量处理](#9-图像批量处理)
10. [内容审核管道](#10-内容审核管道)

---

## 1. 文本到图像生成

**描述**：用户输入主题，LLM 优化提示词，DALL-E 生成图像

**触发类型**：手动触发 / Webhook

**流程**：
```
输入 → LLM(优化提示) → 图像生成 → 输出
```

**完整配置**：

```json
{
  "name": "文本到图像生成",
  "description": "输入主题，AI 自动优化提示词并生成图像",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "manual",
        "inputs": [
          {"name": "topic", "type": "string", "label": "主题", "required": true}
        ]
      }
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "提示词优化",
      "config": {
        "model": "gpt-4",
        "system_prompt": "你是一个专业的图像提示词工程师。用户会提供一个主题，你需要生成一个详细、生动的图像描述，包含风格、光线、构图等细节。直接输出优化后的提示词，不要其他解释。",
        "user_prompt": "为主题「{{trigger_1.inputs.topic}}」生成一个高质量的图像提示词",
        "temperature": 0.8
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "image_1",
      "type": "image",
      "name": "图像生成",
      "config": {
        "model": "dall-e-3",
        "size": "1024x1024",
        "quality": "hd",
        "style": "vivid"
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "结果输出",
      "config": {
        "format": "json",
        "fields": [
          {"source": "trigger_1.inputs.topic", "label": "原始主题"},
          {"source": "llm_1.output", "label": "优化提示词"},
          {"source": "image_1.output.image_url", "label": "生成图像"}
        ]
      },
      "inputs": ["image_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "llm_1"},
    {"from": "llm_1", "to": "image_1"},
    {"from": "image_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 创意设计灵感
- 社交媒体配图
- 产品概念可视化

---

## 2. 批量内容处理

**描述**：处理多条输入数据，对每条进行 LLM 处理

**触发类型**：Webhook / 定时

**流程**：
```
输入数组 → Loop → LLM处理 → 收集结果 → Loop End → 输出
```

**完整配置**：

```json
{
  "name": "批量内容处理",
  "description": "批量处理多条文本，每条经过 LLM 分析后输出结果",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "webhook",
        "inputs": [
          {"name": "items", "type": "array", "label": "待处理数据", "required": true}
        ]
      }
    },
    {
      "id": "loop_1",
      "type": "loop",
      "name": "循环处理",
      "config": {
        "items": "{{trigger_1.inputs.items}}"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "内容分析",
      "config": {
        "model": "gpt-4",
        "system_prompt": "分析以下内容，提取关键信息并总结。输出 JSON 格式：{\"summary\": \"摘要\", \"keywords\": [\"关键词1\", \"关键词2\"], \"sentiment\": \"positive/negative/neutral\"}",
        "user_prompt": "{{loop_1.current_item}}"
      },
      "inputs": ["loop_1"]
    },
    {
      "id": "collect_1",
      "type": "collect",
      "name": "结果收集",
      "config": {
        "accumulator": "results"
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "loop_end_1",
      "type": "loop_end",
      "name": "循环结束",
      "config": {},
      "inputs": ["collect_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "批量结果",
      "config": {
        "format": "json"
      },
      "inputs": ["loop_end_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "loop_1"},
    {"from": "loop_1", "to": "llm_1"},
    {"from": "llm_1", "to": "collect_1"},
    {"from": "collect_1", "to": "loop_end_1"},
    {"from": "loop_end_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 批量文章摘要
- 产品评论分析
- 用户反馈批量处理

---

## 3. 多模态管道

**描述**：图像 → LLM 描述 → 语音合成

**触发类型**：手动 / Webhook

**流程**：
```
图像输入 → 图像分析(LLM) → 文本转语音 → 输出音频
```

**完整配置**：

```json
{
  "name": "图像描述转语音",
  "description": "上传图像，AI 分析并生成语音描述",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "manual",
        "inputs": [
          {"name": "image_url", "type": "string", "label": "图像URL", "required": true}
        ]
      }
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "图像分析",
      "config": {
        "model": "gpt-4-vision",
        "system_prompt": "你是一个视觉描述专家。详细描述图像中的内容，包括主体、背景、颜色、风格等。描述应该清晰、生动，适合转换为语音。",
        "user_prompt": "请描述这张图像：{{trigger_1.inputs.image_url}}"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "tts_1",
      "type": "audio",
      "name": "语音合成",
      "config": {
        "model": "tts-1",
        "voice": "alloy",
        "speed": 1.0
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "结果输出",
      "config": {
        "format": "json",
        "fields": [
          {"source": "llm_1.output", "label": "图像描述"},
          {"source": "tts_1.output.audio_url", "label": "语音文件"}
        ]
      },
      "inputs": ["tts_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "llm_1"},
    {"from": "llm_1", "to": "tts_1"},
    {"from": "tts_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 图像解说生成
- 无障碍内容创建
- 视障辅助应用

---

## 4. 条件分支工作流

**描述**：根据输入类型执行不同处理路径

**触发类型**：Webhook

**流程**：
```
输入 → 条件判断 → [文本路径] LLM → 输出1
              → [图像路径] 图像分析 → 输出2
              → [默认路径] 基础处理 → 输出3
```

**完整配置**：

```json
{
  "name": "智能分流处理",
  "description": "根据输入内容类型自动选择处理路径",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "webhook",
        "inputs": [
          {"name": "content", "type": "string", "label": "内容", "required": true},
          {"name": "content_type", "type": "string", "label": "类型", "required": true}
        ]
      }
    },
    {
      "id": "condition_1",
      "type": "condition",
      "name": "条件判断",
      "config": {
        "conditions": [
          {
            "field": "trigger_1.inputs.content_type",
            "operator": "equals",
            "value": "text"
          },
          {
            "field": "trigger_1.inputs.content_type",
            "operator": "equals",
            "value": "image"
          }
        ],
        "default_branch": "default"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "文本处理",
      "config": {
        "model": "gpt-4",
        "system_prompt": "处理文本内容，提取关键信息。",
        "user_prompt": "{{trigger_1.inputs.content}}"
      },
      "inputs": []
    },
    {
      "id": "image_llm_1",
      "type": "llm",
      "name": "图像分析",
      "config": {
        "model": "gpt-4-vision",
        "system_prompt": "分析图像内容并提供详细描述。",
        "user_prompt": "{{trigger_1.inputs.content}}"
      },
      "inputs": []
    },
    {
      "id": "default_1",
      "type": "llm",
      "name": "默认处理",
      "config": {
        "model": "gpt-4",
        "system_prompt": "基础内容处理。",
        "user_prompt": "处理：{{trigger_1.inputs.content}}"
      },
      "inputs": []
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "统一输出",
      "config": {
        "format": "json"
      },
      "inputs": ["llm_1", "image_llm_1", "default_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "condition_1"},
    {"from": "condition_1.text", "to": "llm_1"},
    {"from": "condition_1.image", "to": "image_llm_1"},
    {"from": "condition_1.default", "to": "default_1"},
    {"from": "llm_1", "to": "output_1"},
    {"from": "image_llm_1", "to": "output_1"},
    {"from": "default_1", "to": "output_1"}
  ],
  "branch_mapping": {
    "text": "llm_1",
    "image": "image_llm_1",
    "default": "default_1"
  }
}
```

**使用场景**：
- 智能客服分流
- 多类型内容处理
- 自动化决策系统

---

## 5. 定时任务工作流

**描述**：每日定时执行数据收集和分析

**触发类型**：定时触发 (Cron)

**流程**：
```
定时触发 → 数据收集(API) → 数据分析 → 生成报告 → 发送通知
```

**完整配置**：

```json
{
  "name": "每日数据报告",
  "description": "每天早上9点自动收集数据并生成报告",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "定时触发",
      "config": {
        "trigger_type": "schedule",
        "cron": "0 9 * * *",
        "timezone": "Asia/Shanghai",
        "enabled": true
      }
    },
    {
      "id": "http_1",
      "type": "http",
      "name": "获取数据",
      "config": {
        "method": "GET",
        "url": "https://api.example.com/daily-stats",
        "headers": {
          "Authorization": "Bearer {{env.API_TOKEN}}"
        }
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "数据分析",
      "config": {
        "model": "gpt-4",
        "system_prompt": "你是数据分析专家。分析提供的数据，识别趋势、异常和关键洞察。生成简洁的报告。",
        "user_prompt": "分析以下数据：{{http_1.response.body}}"
      },
      "inputs": ["http_1"]
    },
    {
      "id": "email_1",
      "type": "webhook",
      "name": "发送邮件",
      "config": {
        "action": "send_email",
        "to": "{{env.REPORT_EMAIL}}",
        "subject": "每日数据报告 - {{date}}",
        "body": "{{llm_1.output}}"
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "完成记录",
      "config": {
        "format": "json",
        "fields": [
          {"source": "trigger_1.timestamp", "label": "执行时间"},
          {"source": "http_1.response.status", "label": "数据状态"},
          {"source": "llm_1.output", "label": "分析结果"}
        ]
      },
      "inputs": ["email_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "http_1"},
    {"from": "http_1", "to": "llm_1"},
    {"from": "llm_1", "to": "email_1"},
    {"from": "email_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 日报/周报生成
- 定时数据同步
- 定期健康检查

---

## 6. API 集成工作流

**描述**：外部 API 数据获取 → 处理 → 存储

**触发类型**：Webhook / 定时

**流程**：
```
外部触发 → 获取数据 → 数据转换 → 存储/推送
```

**完整配置**：

```json
{
  "name": "第三方数据同步",
  "description": "从第三方 API 获取数据，处理后存入数据库",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "Webhook触发",
      "config": {
        "trigger_type": "webhook",
        "webhook_secret": "{{env.WEBHOOK_SECRET}}"
      }
    },
    {
      "id": "http_1",
      "type": "http",
      "name": "获取产品信息",
      "config": {
        "method": "GET",
        "url": "https://api.supply.com/products",
        "headers": {
          "X-API-Key": "{{env.SUPPLY_API_KEY}}"
        },
        "params": {
          "updated_since": "{{trigger_1.body.last_sync}}"
        }
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "transform_1",
      "type": "transform",
      "name": "数据转换",
      "config": {
        "mapping": [
          {"from": "id", "to": "external_id"},
          {"from": "name", "to": "product_name"},
          {"from": "price", "to": "sale_price", "transform": "to_cents"},
          {"from": "inventory.count", "to": "stock_quantity"}
        ]
      },
      "inputs": ["http_1"]
    },
    {
      "id": "db_1",
      "type": "database",
      "name": "存储数据",
      "config": {
        "operation": "upsert",
        "table": "products",
        "primary_key": "external_id"
      },
      "inputs": ["transform_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "同步结果",
      "config": {
        "format": "json"
      },
      "inputs": ["db_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "http_1"},
    {"from": "http_1", "to": "transform_1"},
    {"from": "transform_1", "to": "db_1"},
    {"from": "db_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 数据同步
- Webhook 处理
- API 聚合

---

## 7. 聊天机器人

**描述**：对话式 AI 助手，支持上下文记忆

**触发类型**：Webhook

**流程**：
```
用户输入 → 历史消息获取 → LLM对话 → 保存历史 → 返回响应
```

**完整配置**：

```json
{
  "name": "AI 对话助手",
  "description": "具有上下文记忆的对话式 AI 助手",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "对话触发",
      "config": {
        "trigger_type": "webhook",
        "inputs": [
          {"name": "session_id", "type": "string", "label": "会话ID", "required": true},
          {"name": "message", "type": "string", "label": "用户消息", "required": true}
        ]
      }
    },
    {
      "id": "db_1",
      "type": "database",
      "name": "获取历史",
      "config": {
        "operation": "query",
        "table": "chat_history",
        "query": {"session_id": "{{trigger_1.inputs.session_id}}"},
        "limit": 10,
        "order_by": "created_at desc"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "对话生成",
      "config": {
        "model": "gpt-4",
        "system_prompt": "你是一个专业、友好的 AI 助手。保持对话简洁、有帮助。结合历史对话上下文回答当前问题。",
        "messages": "{{db_1.output}}",
        "user_prompt": "{{trigger_1.inputs.message}}"
      },
      "inputs": ["db_1"]
    },
    {
      "id": "save_1",
      "type": "database",
      "name": "保存对话",
      "config": {
        "operation": "insert",
        "table": "chat_history",
        "records": [
          {"session_id": "{{trigger_1.inputs.session_id}}", "role": "user", "content": "{{trigger_1.inputs.message}}"},
          {"session_id": "{{trigger_1.inputs.session_id}}", "role": "assistant", "content": "{{llm_1.output}}"}
        ]
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "响应输出",
      "config": {
        "format": "json",
        "fields": [
          {"source": "llm_1.output", "label": "assistant_message"},
          {"source": "trigger_1.inputs.session_id", "label": "session_id"}
        ]
      },
      "inputs": ["save_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "db_1"},
    {"from": "db_1", "to": "llm_1"},
    {"from": "llm_1", "to": "save_1"},
    {"from": "save_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 客服机器人
- 虚拟助手
- 教育辅导

---

## 8. 数据提取与转换

**描述**：从非结构化文本中提取结构化数据

**触发类型**：Webhook / 文件上传

**流程**：
```
文本输入 → LLM提取 → 数据验证 → JSON输出
```

**完整配置**：

```json
{
  "name": "发票信息提取",
  "description": "从发票文本中提取结构化信息",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "webhook",
        "inputs": [
          {"name": "invoice_text", "type": "string", "label": "发票文本", "required": true}
        ]
      }
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "信息提取",
      "config": {
        "model": "gpt-4",
        "system_prompt": "从发票文本中提取结构化信息。必须返回以下 JSON 格式，不要添加其他内容：\n{\n  \"invoice_number\": \"发票号码\",\n  \"date\": \"日期(YYYY-MM-DD)\",\n  \"vendor\": \"供应商名称\",\n  \"total_amount\": 总金额(数字),\n  \"currency\": \"货币代码\",\n  \"items\": [\n    {\n      \"description\": \"商品描述\",\n      \"quantity\": 数量(数字),\n      \"unit_price\": 单价(数字),\n      \"subtotal\": 小计(数字)\n    }\n  ]\n}",
        "user_prompt": "从以下发票文本提取信息：\n{{trigger_1.inputs.invoice_text}}"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "validate_1",
      "type": "condition",
      "name": "数据验证",
      "config": {
        "conditions": [
          {"field": "llm_1.output.invoice_number", "operator": "exists"},
          {"field": "llm_1.output.total_amount", "operator": "is_number"}
        ]
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "output_success_1",
      "type": "output",
      "name": "成功输出",
      "config": {
        "format": "json",
        "status": "success"
      },
      "inputs": ["validate_1"]
    },
    {
      "id": "output_error_1",
      "type": "output",
      "name": "错误输出",
      "config": {
        "format": "json",
        "status": "error"
      },
      "inputs": []
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "llm_1"},
    {"from": "llm_1", "to": "validate_1"},
    {"from": "validate_1.passed", "to": "output_success_1"},
    {"from": "validate_1.failed", "to": "output_error_1"}
  ]
}
```

**使用场景**：
- 文档信息提取
- 表单自动填充
- 数据迁移

---

## 9. 图像批量处理

**描述**：批量图像风格转换和处理

**触发类型**：手动 / Webhook

**流程**：
```
图像列表 → Loop → 图像处理 → 结果收集 → 批量输出
```

**完整配置**：

```json
{
  "name": "批量图像风格化",
  "description": "批量将图像转换为指定艺术风格",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "webhook",
        "inputs": [
          {"name": "image_urls", "type": "array", "label": "图像URL列表", "required": true},
          {"name": "style", "type": "string", "label": "风格", "required": true}
        ]
      }
    },
    {
      "id": "loop_1",
      "type": "loop",
      "name": "批量循环",
      "config": {
        "items": "{{trigger_1.inputs.image_urls}}"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "llm_1",
      "type": "llm",
      "name": "生成提示词",
      "config": {
        "model": "gpt-4",
        "system_prompt": "根据用户指定的风格，为图像生成一个风格化处理的提示词。直接输出提示词。",
        "user_prompt": "为图像生成风格化为「{{trigger_1.inputs.style}}」的提示词"
      },
      "inputs": ["loop_1"]
    },
    {
      "id": "image_1",
      "type": "image",
      "name": "图像处理",
      "config": {
        "model": "stable-diffusion",
        "prompt": "{{llm_1.output}}",
        "image_url": "{{loop_1.current_item}}",
        "strength": 0.7
      },
      "inputs": ["llm_1"]
    },
    {
      "id": "collect_1",
      "type": "collect",
      "name": "结果收集",
      "config": {
        "accumulator": "stylized_images",
        "item": {
          "original": "{{loop_1.current_item}}",
          "stylized": "{{image_1.output.image_url}}",
          "prompt": "{{llm_1.output}}"
        }
      },
      "inputs": ["image_1"]
    },
    {
      "id": "loop_end_1",
      "type": "loop_end",
      "name": "循环结束",
      "inputs": ["collect_1"]
    },
    {
      "id": "output_1",
      "type": "output",
      "name": "批量输出",
      "config": {
        "format": "json",
        "fields": [
          {"source": "collect_1.results", "label": "stylized_images"}
        ]
      },
      "inputs": ["loop_end_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "loop_1"},
    {"from": "loop_1", "to": "llm_1"},
    {"from": "llm_1", "to": "image_1"},
    {"from": "image_1", "to": "collect_1"},
    {"from": "collect_1", "to": "loop_end_1"},
    {"from": "loop_end_1", "to": "output_1"}
  ]
}
```

**使用场景**：
- 批量图像编辑
- 艺术风格迁移
- 产品图批量处理

---

## 10. 内容审核管道

**描述**：多层次内容审核，检测违规内容

**触发类型**：Webhook

**流程**：
```
内容输入 → 文本审核 → 图像审核(如有) → 综合判断 → 输出结果
```

**完整配置**：

```json
{
  "name": "智能内容审核",
  "description": "多模态内容安全审核系统",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "name": "触发器",
      "config": {
        "trigger_type": "webhook",
        "inputs": [
          {"name": "text", "type": "string", "label": "文本内容"},
          {"name": "image_url", "type": "string", "label": "图像URL"}
        ]
      }
    },
    {
      "id": "llm_moderation_1",
      "type": "llm",
      "name": "文本审核",
      "config": {
        "model": "gpt-4",
        "system_prompt": "你是内容安全审核专家。检测以下内容是否包含：\n1. 色情/低俗内容\n2. 暴力/血腥内容\n3. 政治敏感内容\n4. 虚假信息\n5. 仇恨言论\n\n只返回 JSON 格式：\n{\n  \"safe\": true/false,\n  \"violations\": [\"违规类型\"],\n  \"confidence\": 0.0-1.0\n}",
        "user_prompt": "审核此文本：{{trigger_1.inputs.text}}"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "image_check_1",
      "type": "llm",
      "name": "图像审核",
      "config": {
        "model": "gpt-4-vision",
        "system_prompt": "审核此图像是否包含不适当内容。返回 JSON：\n{\n  \"safe\": true/false,\n  \"violations\": [\"违规类型\"],\n  \"confidence\": 0.0-1.0\n}",
        "user_prompt": "审核此图像：{{trigger_1.inputs.image_url}}"
      },
      "inputs": []
    },
    {
      "id": "condition_1",
      "type": "condition",
      "name": "综合判断",
      "config": {
        "logic": "and",
        "conditions": [
          {"field": "llm_moderation_1.output.safe", "operator": "equals", "value": true},
          {"field": "image_check_1.output.safe", "operator": "equals", "value": true}
        ],
        "default_branch": "flagged"
      },
      "inputs": ["llm_moderation_1", "image_check_1"]
    },
    {
      "id": "output_approved_1",
      "type": "output",
      "name": "通过输出",
      "config": {
        "format": "json",
        "fields": [
          {"source": "trigger_1.inputs", "label": "original_content"},
          {"source": "approved", "label": "status"},
          {"source": "true", "label": "reviewed_at"}
        ]
      },
      "inputs": []
    },
    {
      "id": "output_flagged_1",
      "type": "output",
      "name": "标记输出",
      "config": {
        "format": "json",
        "fields": [
          {"source": "trigger_1.inputs", "label": "original_content"},
          {"source": "flagged", "label": "status"},
          {"source": "llm_moderation_1.output.violations", "label": "text_violations"},
          {"source": "image_check_1.output.violations", "label": "image_violations"}
        ]
      },
      "inputs": []
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "llm_moderation_1"},
    {"from": "trigger_1", "to": "image_check_1"},
    {"from": "llm_moderation_1", "to": "condition_1"},
    {"from": "image_check_1", "to": "condition_1"},
    {"from": "condition_1.passed", "to": "output_approved_1"},
    {"from": "condition_1.flagged", "to": "output_flagged_1"}
  ],
  "branch_mapping": {
    "passed": "output_approved_1",
    "flagged": "output_flagged_1"
  }
}
```

**使用场景**：
- UGC 内容审核
- 评论过滤
- 社交平台安全

---

## 模板使用指南

### 如何使用这些模板

1. **选择模板**：根据需求选择合适的工作流模板
2. **自定义参数**：修改模板中的配置参数
3. **添加认证**：填入必要的 API Key 和凭证
4. **测试运行**：使用测试数据运行工作流
5. **部署上线**：确认无误后启用工作流

### 模板扩展

所有模板都支持以下扩展：
- 添加更多节点
- 修改连接关系
- 调整节点参数
- 添加错误处理分支

### 模板组合

多个模板可以组合使用，构建更复杂的工作流：
- 将输出节点连接到其他工作流的触发器
- 使用子工作流实现复用
- 通过 Webhook 连接不同工作流
