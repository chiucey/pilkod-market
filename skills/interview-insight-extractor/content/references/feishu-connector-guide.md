---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 98d14344f5814207e0f868d1fdfca93e
    PropagateID: 98d14344f5814207e0f868d1fdfca93e
    ReservedCode1: 3045022100e24508a82e14d0d80b1bb652d8e9962ea8bb6541e2f967fbb16d1d361f4f947902207f10ffdfd0c3a8734b8511ab330161672a451097367f3526da04e5ec94f241ee
    ReservedCode2: 3046022100fb7c3ed95926a2c6b6899455455ed5289fb1d05852f9b29dbc8e98e27237ad5a022100d6c807cd76325624d658b0886b9cb07c1df7f27ec62d1cab45a7f8e4f033cfb8
---

# 飞书连接器配置指南

## 连接器设置

### 必需权限
- 文档读取权限（读取源文档）
- 文档创建权限（输出洞察报告）
- 文件夹管理权限（创建输出目录）

### API 端点
```
读取文档：GET /drive/v1/files/{file_token}/content
创建文档：POST /docx/v1/documents
写入内容：POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
```

### Configuration Example
```json
{
  "connector": "feishu",
  "input_folder": "/user-interviews/raw-records",
  "output_folder": "/user-interviews/insight-output",
  "knowledge_base_folders": [
    "/project-background",
    "/product-strategy",
    "/historical-research"
  ]
}
```

## 文档格式要求

### 输入文档（逐字稿）
- 格式：飞书文档 Markdown 格式
- 命名规范：`[受访者编号]_逐字稿_YYYYMMDD.md`
- 内容要求：
  - 包含访谈时间、时长
  - 包含受访者基本信息
  - 按时间顺序记录

### 输入文档（研究员纪要）
- 格式：飞书文档
- 命名规范：`[受访者编号]_纪要_YYYYMMDD.md`
- 内容要求：
  - 结构化的访谈摘要
  - 关键话题分类
  - 初步洞察备注

### 输出文档命名
- 单份洞察：`洞察报告-[受访者编号].md`
- 合并洞察：`综合洞察报告-YYYYMMDD.md`
