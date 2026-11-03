---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5afaed00bbc8d42ae8073c9338a63e6e
    PropagateID: 5afaed00bbc8d42ae8073c9338a63e6e
    ReservedCode1: 30460221009086e4a2a8141d0890ab197c9ae495ffc8b53ef591967f57f31aa1235563d75e022100c7833dddbac3f933027169b70243fcd96fa830cd512e89b0ba08209a08e05189
    ReservedCode2: 304402202dca545e1f92001a37cc8ae6016d803e742aba1632044d0edeb342bce0977d300220165a5470d9cc77415edb088f380f14c39ea7c28c59fdfc7d8d168201eed0724e
description: 连接伙伴云平台并管理表格数据操作。当用户需要创建、查询、更新伙伴云表格中的记录时使用。触发短语包括："创建客户"、"查询订单"、"更新数据"、"伙伴云"、"huoban cloud"、"连接伙伴云"。
name: connect-to-huoban-cloud
---

# ConnectToHuobanCloud Skill - 伙伴云数据连接器

## 概述

本技能提供与伙伴云 API 的无缝集成，通过对话界面实现自动化数据管理。支持多表格配置、自动字段映射、关联字段处理和全面的数据操作功能。

## 功能特性

- **多表格支持**：在工作区内配置和管理多个表格
- **自动字段映射**：智能关键词到字段ID的映射
- **关联字段处理**：自动解析表格之间的关联字段
- **选项字段映射**：智能将选项值映射为选项ID
- **操作日志记录**：完整的数据操作审计跟踪
- **日期解析**：支持自然语言日期（今天、明天、后天）

## 核心 API 端点

| 操作 | 端点 | 方法 |
|------|------|------|
| 获取表格列表 | `https://api.huoban.com/openapi/v1/table/list` | POST |
| 获取表格配置 | `https://api.huoban.com/openapi/v1/table/{table_id}` | POST |
| 查询数据列表 | `https://api.huoban.com/openapi/v1/item/list` | POST |
| 获取数据详情 | `https://api.huoban.com/openapi/v1/item/{item_id}` | POST |
| 创建数据 | `https://api.huoban.com/openapi/v1/item` | POST |
| 更新数据 | `https://api.huoban.com/openapi/v1/item/{item_id}` | PUT |

## 使用命令

### 配置命令

| 命令 | 说明 |
|------|------|
| `python huoban_cloud.py setup <access_token>` | 配置 API Token，用于身份认证 |
| `python huoban_cloud.py init <space_id>` | 初始化工作区，自动获取所有表格配置信息 |

### 表格管理命令

| 命令 | 说明 |
|------|------|
| `python huoban_cloud.py add <table_id> [table_name]` | 添加单个表格配置（自动获取字段信息并生成字段映射） |
| `python huoban_cloud.py update <table_id>` | 更新表格配置（从 API 获取最新表格配置，自动重新梳理字段映射） |
| `python huoban_cloud.py list` | 列出所有已配置的表格 |
| `python huoban_cloud.py fields <table_id>` | 查看指定表格的字段详情 |

### 数据操作命令

| 命令 | 说明 |
|------|------|
| `python huoban_cloud.py run <table_id> "用户消息"` | 从对话中提取信息并创建数据 |
| `python huoban_cloud.py query <table_id> "查询条件"` | 根据条件查询表格数据 |
| `python huoban_cloud.py modify <table_id> <item_id> "修改内容"` | 更新指定数据的字段值 |

### 高级命令

| 命令 | 说明 |
|------|------|
| `python huoban_cloud.py mapping <table_id> "关键词:字段ID"` | 手动配置字段映射关系 |
| `python huoban_cloud.py log [limit]` | 查看操作日志（默认显示最近10条） |

### 命令使用示例

```bash
# 1. 首次使用：配置 API Token
python huoban_cloud.py setup your_access_token_here

# 2. 获取工作区中的所有表格
python huoban_cloud.py init your_space_id_here

# 3. 查看已配置的表格
python huoban_cloud.py list

# 4. 查看表格字段
python huoban_cloud.py fields 2100000074953145

# 5. 更新表格配置（当伙伴云表格字段有变化时使用）
# 自动从 API 获取最新配置并重新生成字段映射
python huoban_cloud.py update 2100000074953145

# 6. 创建数据
python huoban_cloud.py run 2100000074953145 "客户张三、电话13800138000、客户类型为重点客户"

# 7. 查询数据
python huoban_cloud.py query 2100000074953145 "客户姓名为张三"

# 8. 更新数据
python huoban_cloud.py modify 2100000074953145 2300019181796884 "电话13900139000"

# 9. 手动添加字段映射
python huoban_cloud.py mapping 2100000074953145 "姓名:2200000594696996" "电话:2200000594696997"

# 10. 查看操作日志
python huoban_cloud.py log
```

## 数据操作流程

### 创建数据 (run)
```
1. 加载表格配置
2. 从用户消息中提取信息
3. 使用 field_mapping 将关键词映射到字段ID
4. 处理选项字段（将选项名称转换为选项ID）
5. 解析关联字段（查找关联的 item_id）
6. 调用 API 创建数据
```

### 查询数据 (query)
```
1. 加载表格配置
2. 从消息中解析查询条件
3. 构建筛选条件配置
4. 执行分页查询
5. 返回格式化结果
```

### 更新数据 (modify)
```
1. 加载表格配置
2. 提取修改内容
3. 映射到字段格式
4. 处理特殊字段类型
5. 调用 API 更新数据
```

## 筛选器操作符

| 操作符 | 说明 | 适用字段 |
|--------|------|----------|
| eq | 等于 | 文本、数字、选项、日期 |
| neq | 不等于 | 文本、数字、选项、日期 |
| gt/gte | 大于/大于等于 | 数字、日期 |
| lt/lte | 小于/小于等于 | 数字、日期 |
| in | 包含 | 选项、多选、关联 |
| nin | 不包含 | 选项、多选、关联 |
| inc | 模糊匹配 | 文本 |
| em | 为空 | 任何字段 |

## 字段类型支持

| 字段类型 | 创建 | 查询 | 更新 |
|----------|------|------|------|
| input, textarea | ✅ | ✅ | ✅ |
| number | ✅ | ✅ | ✅ |
| numeric, money | ✅ | ✅ | ✅ |
| date, datetime | ✅ | ✅ | ✅ |
| category | ✅ | ✅ | ✅ |
| relation | ✅ | ✅ | ✅ |
| user | - | - | - |
| image, file | - | - | - |

## 配置文件结构 (config.json)

```json
{
  "access_token": "伙伴云开放平台 API Token",
  "current_wecom_user": "当前企业微信用户ID",
  "tables": {
    "table_id": {
      "name": "表格名称",
      "fields": {
        "field_id": "字段名称"
      },
      "full_fields_config": {
        "field_id": {
          "name": "字段名称",
          "field_type": "input|category|relation|...",
          "data_type": "text|category|relation|...",
          "config": {}
        }
      },
      "field_mapping": {
        "关键词": "field_id"
      },
      "relation_configs": {
        "field_id": {
          "table_id": "关联表ID",
          "is_multi": 0
        }
      },
      "category_options": {
        "field_id": [
          {"id": "1", "name": "选项1"},
          {"id": "2", "name": "选项2"}
        ]
      }
    }
  }
}
```

## 使用示例

### 创建客户
```bash
python huoban_cloud.py run 2100000074953145 "客户张三、电话13800138000、客户类型为重点客户"
```

### 查询订单
```bash
python huoban_cloud.py query 2100000074953145 "客户姓名为张三"
python huoban_cloud.py query <table_id> "金额大于1000"
```

### 更新记录
```bash
python huoban_cloud.py modify 2100000074953145 2300019181796884 "电话13900139000"
```

## Python API 调用

```python
from huoban_cloud import run, query, modify, setup, init_workspace

# 配置
setup("your_access_token")

# 初始化工作区
init_workspace("your_space_id")

# 创建数据
result = run("创建客户张三、电话13800138000")

# 查询数据
result = query("客户姓名为张三")

# 更新数据
result = modify("item_id", "电话改为13900139000")
```

## 信息提取模式

本技能自动从用户消息中提取以下信息：

- **电话号码**：11位手机号格式 (1[3-9]\d{9})
- **电子邮箱**：标准邮箱格式
- **日期**：多种格式支持 (2024-03-11、2024年3月11日、今天、明天)
- **时间**：支持上午/下午 (上午10点、下午3点)
- **金额**：带货币单位 (100元、500.50元)
- **年龄**：带年龄单位 (25岁)
- **关键词**：根据 field_mapping 配置进行匹配

## 错误处理

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| INVALID_TOKEN | Access token 过期或无效 | 重新配置 access token |
| TABLE_NOT_FOUND | 表格ID未在配置中 | 使用 `add` 命令添加表格 |
| FIELD_MAPPING_FAILED | 无法将提取的信息映射到字段 | 检查 field_mapping 配置 |
| RELATION_NOT_FOUND | 关联的数据不存在 | 先创建关联的数据 |
| API_RATE_LIMIT | 请求过于频繁 | 等待后重试 |

## 配置文件说明

本技能包含两个配置文件，方便用户查看和检查：

### config.json - 运行时配置

**路径**: `/workspace/temp-skills/connect-to-huoban-cloud/config.json`

**用途**: 存储 API Token 和已获取的表格配置信息

**生成方式**:
- 运行 `python huoban_cloud.py setup <token>` 自动写入 access_token
- 运行 `python huoban_cloud.py init <space_id>` 自动获取所有表格配置
- 运行 `python huoban_cloud.py add <table_id>` 添加单个表格配置

**主要字段**:
- `access_token`: 伙伴云开放平台的 API Token
- `current_wecom_user`: 当前企业微信用户ID（用于自动填充跟进人）
- `tables`: 已配置的表格字典，键为 table_id

### config.example.json - 配置示例

**路径**: `/workspace/temp-skills/connect-to-huoban-cloud/config.example.json`

**用途**: 展示完整配置结构的示例文件

**内容**: 包含一个完整配置的示例，包括：
- 表格的完整字段配置 (full_fields_config)
- 字段映射关系 (field_mapping)
- 选项字段选项列表 (category_options)
- 关联字段配置 (relation_configs)

### process.log - 操作日志

**路径**: `/workspace/temp-skills/connect-to-huoban-cloud/process.log`

**用途**: 记录所有数据操作的审计日志，便于问题排查

**查看方式**: `python huoban_cloud.py log [limit]`

## 文件结构

```
connect-to-huoban-cloud/
├── SKILL.md              # 技能说明文档
├── huoban_cloud.py       # 核心实现代码
├── config.json           # 运行时配置（自动生成）
├── config.example.json   # 配置示例文件
├── _meta.json            # 技能元数据
└── process.log           # 操作日志（自动生成）
```

## 快速开始

1. **配置 API Token**:
   ```bash
   python huoban_cloud.py setup <your_access_token>
   ```

2. **初始化工作区**（获取所有表格配置）:
   ```bash
   python huoban_cloud.py init <your_space_id>
   ```

3. **查看已配置的表格**:
   ```bash
   python huoban_cloud.py list
   ```

4. **查看表格字段详情**:
   ```bash
   python huoban_cloud.py fields <table_id>
   ```

5. **手动编辑配置**: 直接打开 `config.json` 查看和修改配置
