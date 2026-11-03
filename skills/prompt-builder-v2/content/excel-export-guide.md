# Excel导出功能指南

## 概览
本指南说明如何使用提示词巧匠的Excel导出功能。

---

## 功能说明

### 支持的导出格式

1. **详细版（detailed）**
   - 包含所有字段：提示词ID、场景、目标导向、效率优先、准确性优先、提示词全文、评分、生成模式、创建时间
   - 包含14个维度拆解：角色设定、目标受众、语言风格、内容结构、输出格式、思维深度、创意水平、专业性、实用性、可操作性、清晰度、完整性、灵活性、适配性
   - 适合：需要完整信息的场景

2. **简洁版（simple）**
   - 只包含关键字段：提示词ID、使用场景、目标导向、评分、生成模式、创建时间
   - 适合：快速浏览和总结

### Excel样式特性

- ✅ 表头加粗、蓝色背景
- ✅ 自动换行、对齐整齐
- ✅ 列宽自适应（支持中文）
- ✅ 边框清晰
- ✅ 行高合理设置

---

## 使用方法

### 方式1：命令行调用

#### 基本用法

```bash
python scripts/export-to-excel.py \
  --input prompts.json \
  --output prompts_export.xlsx \
  --format detailed
```

#### 参数说明

- `--input, -i`（必需）：输入的JSON文件路径
- `--output, -o`（可选）：输出的Excel文件路径，默认为 `prompts_export.xlsx`
- `--format, -f`（可选）：导出格式，`detailed` 详细版或 `simple` 简洁版，默认为 `detailed`

#### 示例

**导出详细版**：
```bash
python scripts/export-to-excel.py -i my_prompts.json -o detailed_export.xlsx -f detailed
```

**导出简洁版**：
```bash
python scripts/export-to-excel.py -i my_prompts.json -o simple_export.xlsx -f simple
```

**使用默认参数**：
```bash
python scripts/export-to-excel.py -i my_prompts.json
```

### 方式2：在智能体中调用

智能体可以根据用户需求自动调用导出脚本：

```python
import subprocess
import json

# 用户提示词数据
prompt_data = {
    "prompt_id": 1,
    "scenario": "文案撰写",
    "goal_orientation": "创造性优先",
    "prompt_content": "你是一位拥有10年经验的资深营销专家...",
    "score": 95,
    "mode": "fast",
    "dimensions": {
        "identity": "资深营销专家",
        "target_audience": "25-35岁年轻白领",
        "style": "轻松活泼",
        "structure": "问题导入 → 核心观点 → 论据支撑 → 行动号召",
        "output_format": "100-200字短文案",
        "thinking_depth": "中等",
        "creativity": "高",
        "professionalism": "高",
        "practicality": "高",
        "operability": "高",
        "clarity": "高",
        "completeness": "高",
        "flexibility": "中",
        "adaptability": "中"
    },
    "is_efficiency_priority": False,
    "is_accuracy_priority": False,
    "created_at": "2024-02-11T14:30:00Z"
}

# 保存为JSON文件
with open('temp_prompts.json', 'w', encoding='utf-8') as f:
    json.dump([prompt_data], f, ensure_ascii=False, indent=2)

# 调用导出脚本
subprocess.run([
    'python', 'scripts/export-to-excel.py',
    '--input', 'temp_prompts.json',
    '--output', 'my_prompts.xlsx',
    '--format', 'detailed'
])

print("✅ Excel文件已生成：my_prompts.xlsx")
```

---

## JSON数据格式

### 单个提示词格式

```json
{
  "prompt_id": 1,
  "scenario": "文案撰写",
  "goal_orientation": "创造性优先",
  "prompt_content": "你是一位拥有10年经验的资深营销专家，擅长为年轻品牌打造富有感染力的营销文案。",
  "score": 95,
  "mode": "fast",
  "dimensions": {
    "identity": "资深营销专家",
    "target_audience": "25-35岁年轻白领",
    "style": "轻松活泼",
    "structure": "问题导入 → 核心观点 → 论据支撑 → 行动号召",
    "output_format": "100-200字短文案",
    "thinking_depth": "中等",
    "creativity": "高",
    "professionalism": "高",
    "practicality": "高",
    "operability": "高",
    "clarity": "高",
    "completeness": "高",
    "flexibility": "中",
    "adaptability": "中"
  },
  "is_efficiency_priority": false,
  "is_accuracy_priority": false,
  "created_at": "2024-02-11T14:30:00Z"
}
```

### 批量提示词格式

```json
[
  {
    "prompt_id": 1,
    "scenario": "文案撰写",
    "goal_orientation": "创造性优先",
    "prompt_content": "...",
    "score": 95,
    "mode": "fast",
    "dimensions": {},
    "is_efficiency_priority": false,
    "is_accuracy_priority": false,
    "created_at": "2024-02-11T14:30:00Z"
  },
  {
    "prompt_id": 2,
    "scenario": "代码编程",
    "goal_orientation": "准确性优先",
    "prompt_content": "...",
    "score": 88,
    "mode": "precision",
    "dimensions": {},
    "is_efficiency_priority": false,
    "is_accuracy_priority": true,
    "created_at": "2024-02-11T15:20:00Z"
  }
]
```

### 包含在data字段中的格式

```json
{
  "prompts": [
    {
      "prompt_id": 1,
      "scenario": "文案撰写",
      ...
    },
    {
      "prompt_id": 2,
      "scenario": "代码编程",
      ...
    }
  ]
}
```

---

## 字段说明

### 必填字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| prompt_id | int/string | 提示词ID | 1 |
| scenario | string | 使用场景 | "文案撰写" |
| goal_orientation | string | 目标导向 | "创造性优先" |
| prompt_content | string | 提示词全文 | "你是一位..." |
| score | int | 评分（0-100） | 95 |
| mode | string | 生成模式 | "fast" / "precision" |
| created_at | string | 创建时间（ISO格式） | "2024-02-11T14:30:00Z" |

### 可选字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| dimensions | object | 14个维度拆解 | 见下方 |
| is_efficiency_priority | boolean | 是否效率优先 | true / false |
| is_accuracy_priority | boolean | 是否准确性优先 | true / false |

### dimensions维度字段

| 维度名 | 英文key | 说明 | 示例 |
|--------|---------|------|------|
| 角色设定 | identity | 扮演的角色 | "资深营销专家" |
| 目标受众 | target_audience | 目标用户群体 | "25-35岁年轻白领" |
| 语言风格 | style | 语言表达风格 | "轻松活泼" |
| 内容结构 | structure | 内容组织结构 | "问题导入 → 核心观点..." |
| 输出格式 | output_format | 输出内容格式 | "100-200字短文案" |
| 思维深度 | thinking_depth | 思维深度要求 | "中等" |
| 创意水平 | creativity | 创意要求 | "高" |
| 专业性 | professionalism | 专业性要求 | "高" |
| 实用性 | practicality | 实用性要求 | "高" |
| 可操作性 | operability | 可操作性要求 | "高" |
| 清晰度 | clarity | 清晰度要求 | "高" |
| 完整性 | completeness | 完整性要求 | "高" |
| 灵活性 | flexibility | 灵活性要求 | "中" |
| 适配性 | adaptability | 适配性要求 | "中" |

---

## 导出示例

### 详细版导出示例

生成一个Excel文件，包含以下列：

| 提示词ID | 使用场景 | 目标导向 | 效率优先 | 准确性优先 | 提示词全文 | 评分 | 生成模式 | 创建时间 | 角色设定 | 目标受众 | 语言风格 | ... | 适配性 |
|---------|---------|---------|---------|-----------|-----------|------|---------|---------|---------|---------|---------|---|--------|
| 1 | 文案撰写 | 创造性优先 | 否 | 否 | 你是一位... | 95 | fast | 2024-02-11 14:30:00 | 资深营销专家 | 25-35岁年轻白领 | 轻松活泼 | ... | 中 |

### 简洁版导出示例

生成一个Excel文件，只包含以下列：

| 提示词ID | 使用场景 | 目标导向 | 评分 | 生成模式 | 创建时间 |
|---------|---------|---------|------|---------|---------|
| 1 | 文案撰写 | 创造性优先 | 95 | fast | 2024-02-11 14:30:00 |
| 2 | 代码编程 | 准确性优先 | 88 | precision | 2024-02-11 15:20:00 |

---

## 常见问题

### Q1：提示"缺少 openpyxl 依赖库"怎么办？

**A**：执行以下命令安装依赖：
```bash
pip install openpyxl
```

### Q2：JSON文件格式不对怎么办？

**A**：请确保JSON文件符合以下格式之一：
1. 单个提示词对象
2. 提示词数组
3. 包含 `prompts` 字段的对象

### Q3：导出的Excel文件打开乱码怎么办？

**A**：脚本已处理UTF-8编码，如有问题，请确保：
- JSON文件使用UTF-8编码保存
- 使用最新版本的Excel打开（2007及以上）

### Q4：如何批量导出多个JSON文件？

**A**：使用以下脚本批量处理：
```python
import glob
import subprocess

json_files = glob.glob('*.json')
for json_file in json_files:
    output_file = json_file.replace('.json', '.xlsx')
    subprocess.run([
        'python', 'scripts/export-to-excel.py',
        '--input', json_file,
        '--output', output_file
    ])
```

### Q5：如何自定义Excel样式？

**A**：可以修改 `scripts/export-to-excel.py` 中的样式配置：
```python
# 修改表头颜色
self.header_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

# 修改字体
self.header_font = Font(name='宋体', size=12, bold=True, color='000000')
```

---

## 依赖要求

- Python 3.6+
- openpyxl >= 3.0.0

安装依赖：
```bash
pip install openpyxl
```

---

## 技术支持

如有问题，请查看：
1. 检查JSON文件格式是否正确
2. 检查是否安装了 openpyxl 库
3. 检查输入输出路径是否有效
4. 查看脚本输出日志
