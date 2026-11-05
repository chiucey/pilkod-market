---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8b6bfdf8ad878d4d4a06f7789b8a4620
    PropagateID: 8b6bfdf8ad878d4d4a06f7789b8a4620
    ReservedCode1: 3045022100aa43a9cf9a8001e63091a0e4a99f7c3ebaafe7e7feb975d610513169c8d19d36022074bc1bbf2dcd95bf9eea0d2f7dbf1921551bd46591a3d7646859792ad8bdd5d2
    ReservedCode2: 3045022100884528c3d5987a4f80e4df8b2a3008a0aea6eaf1bb58976812ed5bb58628ef7a022056785a48ada73a7864058802b41a8aa59205644b50b45e52e25f26c5102a2d12
description: 国际运输提单格式转换工具。当用户要求"转换提单"、"提单格式转换"、"将提单转为模板"、"处理提单"、"提取提单信息"时使用。支持图片、PDF、Word格式提单的识别与转换。
name: bill-of-lading-converter
---

# 提单格式转换技能

## 概述

本技能用于将各种格式的国际运输提单（Bill of Lading）转换为用户预设的固定模板格式，支持图片、PDF、Word等多种输入格式，自动识别内容并生成标准化PDF输出。

## 核心流程

### 第一阶段：模板管理

#### 1.1 检测预设模板
- 检查 `assets/templates/` 目录是否存在已保存的模板
- 如果存在多个模板，记录模板列表

#### 1.2 模板上传与识别（首次或新增时）
```
当用户上传模板时：
1. 接收用户上传的模板文件（支持PDF、Word、图片格式）
2. 使用对应识别工具提取模板内容：
   - 图片模板 → images_understand 工具
   - PDF模板 → extract_pdfs_full_content 工具
   - Word模板 → 直接读取工具
3. 展示识别的模板结构给用户确认
4. 等待用户确认内容映射准确性
5. 确认后保存模板到 assets/templates/ 目录
6. 更新模板索引文件 templates_index.json
```

#### 1.3 模板选择（多模板场景）
```
当存在多个模板时：
1. 列出所有可用模板及其预览
2. 等待用户选择输出模板
3. 使用用户选择的模板进行转换
```

#### 1.4 模板存储结构
```
assets/templates/
├── templates_index.json     # 模板索引
├── template_001/            # 模板文件夹
│   ├── source_file.pdf       # 原始模板文件
│   ├── structure.json        # 模板结构定义
│   └── field_mapping.json    # 字段映射关系
├── template_002/
│   └── ...
```

### 第二阶段：提单接收与识别

#### 2.1 接收提单文件
```
支持的文件格式：
- 图片格式：JPG、PNG（使用 images_understand 识别）
- PDF格式：PDF文件（使用 extract_pdfs_full_content 识别）
- Word格式：DOC、DOCX（使用文档读取工具）

接收流程：
1. 识别文件类型
2. 调用对应的识别工具
3. 提取提单内容
```

#### 2.2 内容识别与JSON化
```
识别提单中的关键字段：
- 发货人 (Shipper/Exporter)
- 收货人 (Consignee)
- 通知方 (Notify Party)
- 货物描述 (Description of Goods)
- 重量 (Gross Weight)
- 体积 (Volume)
- 装货港 (Port of Loading)
- 卸货港 (Port of Discharge)
- 船名/航次 (Vessel/Voyage)
- 集装箱号 (Container No.)
- 封条号 (Seal No.)
- 开船日期 ( sailing Date)
- 提单号 (B/L No.)

输出：结构化的JSON数据文件
```

### 第三阶段：模板填充与输出

#### 3.1 模板匹配
```
1. 如果只有一个模板，自动使用该模板
2. 如果有多个模板，让用户选择模板
3. 读取模板的 field_mapping.json 获取字段映射关系
```

#### 3.2 数据填充
```
1. 读取用户提单的JSON数据
2. 读取选定模板的结构定义
3. 根据字段映射关系填充模板
4. 生成填充后的文档
```

#### 3.3 输出生成
```
默认输出格式：PDF
输出文件名格式：BL_[原始提单号]_[日期].pdf
保存位置：可由用户指定或默认输出目录
```

## 字段映射定义

```json
{
  "template_fields": {
    "shipper": "发货人/托运人",
    "consignee": "收货人",
    "notify_party": "通知方",
    "vessel": "船名",
    "voyage": "航次",
    "port_of_loading": "装货港",
    "port_of_discharge": "卸货港",
    "container_no": "集装箱号",
    "seal_no": "封条号",
    "description": "货物描述",
    "gross_weight": "毛重",
    "measurement": "体积",
    "sailing_date": "开船日期",
    "bl_no": "提单号",
    "place_of_receipt": "收货地",
    "place_of_delivery": "交货地",
    "freight_prepaid": "运费预付",
    "freight_collect": "运费到付"
  }
}
```

## 识别提示词模板

### 图片/PDF识别提示词
```
请识别这张/这份提单中的以下信息，并以JSON格式输出：
{
  "shipper": "发货人全称和地址",
  "consignee": "收货人全称和地址",
  "notify_party": "通知方全称和地址",
  "vessel": "船名",
  "voyage": "航次号",
  "port_of_loading": "装货港",
  "port_of_discharge": "卸货港",
  "container_no": "集装箱号（如有多个请列出）",
  "seal_no": "封条号",
  "description": "货物描述",
  "gross_weight": "毛重及单位",
  "measurement": "体积及单位",
  "sailing_date": "开船/装船日期",
  "bl_no": "提单号",
  "place_of_receipt": "收货地",
  "place_of_delivery": "交货地",
  "freight_terms": "运费条款"
}
如果某字段在提单中不存在，请标记为 null。
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 未检测到预设模板 | 提示用户上传模板 |
| 识别失败 | 提示用户检查文件清晰度，重试或手动输入 |
| 字段映射不完整 | 列出缺失字段，等待用户补充 |
| 多模板选择无响应 | 使用最近使用的模板或默认模板 |
| 文件格式不支持 | 提示支持的文件格式列表 |

## 使用示例

### 示例1：首次使用，上传模板
```
用户：上传我的提单模板
助手：收到您的模板，请稍候识别...
（识别完成）
助手：已识别模板结构，包含以下字段：
- 发货人区域
- 收货人区域
- 货物描述区域
- 运费条款区域
请确认这些字段映射是否准确？
用户：确认
助手：模板已保存，可以开始转换提单了。
```

### 示例2：转换提单
```
用户：转换这份提单（上传PDF文件）
助手：收到提单文件，开始识别...
（识别完成，JSON化）
助手：已识别提单内容，选择输出模板：
1. 标准海运提单模板
2. 简版提单模板
用户：1
助手：正在生成PDF...
（生成完成）
助手：提单转换完成，文件已保存。
```

## 依赖工具

- `images_understand`：图片内容识别
- `extract_pdfs_full_content`：PDF内容提取
- `html_to_pdf`：PDF生成输出
- `mcp__matrix__bash`：文件操作
