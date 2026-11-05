---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100e802262d739a97bdd26dd52f702b1a27795c0080637836f288460860d1eb6196022100ca1302abacdaa79362d74a799f8d6e383216706542bcf0b208749dcee8631b3f
    ReservedCode2: 3046022100e450bef521d8cfc028eab78f0a8bbef806988cb01130f7a205bc93af6f3bed93022100daa82fd28b83913de5a9f76fe3f43c31a2dfe841b5f096923582bc988edbffdc
---

# 支持的文件格式

## 概述

Universal Data Analyst 支持多种数据文件格式，包括结构化和半结构化数据。

## 详细说明

### CSV / TSV

**扩展名**: `.csv`, `.tsv`, `.txt`

**特点**:
- 文本格式，通用性强
- 支持多种编码自动检测
- 支持自定义分隔符

**编码支持**:
- UTF-8 (默认)
- UTF-8 BOM
- GBK / GB2312 / GB18030 (中文)
- Big5 (繁体中文)
- Latin-1 / ISO-8859-1 (西欧)
- ASCII

**分隔符检测**:
- 自动检测: 逗号`,`、制表符`\t`、分号`;`、竖线`|`、空格

**示例**:
```python
# 自动检测编码和分隔符
result = loader.execute({'file_path': 'data.csv'})

# 指定参数
result = loader.execute({'file_path': 'data.csv', 'encoding': 'gbk'})
```

### Excel

**扩展名**: `.xlsx`, `.xls`

**特点**:
- 支持多工作表
- 保留数据类型
- 支持公式

**依赖**: `openpyxl` (推荐), `xlrd` (旧格式兼容)

**示例**:
```python
# 读取第一个工作表
result = loader.execute({'file_path': 'data.xlsx'})

# 指定工作表
result = loader.execute({'file_path': 'data.xlsx', 'sheet_name': 'Sales'})
```

### Parquet

**扩展名**: `.parquet`, `.pq`

**特点**:
- 列式存储，高压缩比
- 适合大数据
- 保留数据类型

**依赖**: `pyarrow`

**示例**:
```python
result = loader.execute({'file_path': 'data.parquet'})
```

### JSON

**扩展名**: `.json`

**特点**:
- 半结构化数据
- 支持嵌套结构
- 自动展平或保留结构

**支持格式**:
- Records: `[{"a": 1}, {"a": 2}]`
- Columns: `{"a": [1, 2], "b": [3, 4]}`
- Split: `{"columns": [...], "index": [...], "data": [...]}`

**示例**:
```python
# 自动检测格式
result = loader.execute({'file_path': 'data.json'})

# 指定格式
result = loader.execute({'file_path': 'data.json', 'json_orient': 'records'})
```

## 编码问题处理

### 常见问题

1. **中文乱码**
   - 尝试 GBK/GB18030 编码
   - 使用文本编辑器查看实际编码

2. **BOM 字符**
   - UTF-8 BOM 会被自动处理
   - 可能影响后续处理

3. **混合编码**
   - 建议统一为 UTF-8
   - 使用 `iconv` 转换

### 最佳实践

```python
# 保存为 UTF-8
df.to_csv('output.csv', encoding='utf-8')

# 读取时指定编码
result = loader.execute({'file_path': 'input.csv', 'encoding': 'utf-8'})
```

## 文件大小限制

- CSV: 无硬性限制，受内存约束
- Excel: 单工作表建议 < 100MB
- Parquet: 建议单文件 < 1GB
- JSON: 建议 < 500MB

## 数据类型保留

| 格式 | 数据类型保留 | 备注 |
|------|-------------|------|
| CSV | 部分保留 | 日期可能被读取为字符串 |
| Excel | 较好 | 依赖引擎 |
| Parquet | 完全保留 | 列式存储 |
| JSON | 较好 | 嵌套结构可能展平 |
