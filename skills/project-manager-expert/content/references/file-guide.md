# 文件解析指南

## 支持的文件格式

### PDF文档

**提取策略：**
- 使用 `extract_pdfs_key_info` 提取关键信息
- 使用 `extract_pdfs_full_content` 提取完整内容
- 识别项目标题、章节、表格、列表

**关键信息提取：**
```
项目名称
├── 项目描述
├── 时间范围
├── 里程碑列表
├── 任务清单
└── 资源分配
```

**最佳实践：**
- 中文PDF优先使用 full_content 模式
- 英文PDF可使用 key_info 快速提取
- 复杂文档建议先全文提取再分析

### Microsoft Project文件

**解析方法：**
- Project文件需要导出为PDF或Excel后再解析
- 建议用户导出为PDF格式
- 包含Gantt图和任务列表的PDF最易解析

**关键数据字段：**
| 字段 | 说明 | 优先级 |
|------|------|--------|
| 任务名称 | 任务标题 | 必须 |
| 开始/结束日期 | 时间安排 | 必须 |
| 任务状态 | 完成度 | 必须 |
| 依赖关系 | 任务链接 | 高 |
| 负责人 | 资源分配 | 中 |
| 完成百分比 | 进度 | 高 |

### Word文档

**适用场景：**
- 项目计划书
- 需求文档
- 会议纪要

**解析策略：**
- 提取标题结构
- 识别表格和列表
- 提取关键日期和里程碑

### Excel表格

**适用场景：**
- 任务清单
- 进度跟踪表
- 资源分配表

**解析策略：**
- 读取表格结构
- 识别列标题
- 提取关键数值

## 文件命名规范

**Recommended Format:**
```
project_type_project_name_version_date
```

**Examples:**
- `event_annual_meeting_v1_20240315.pdf`
- `construction_commercial_center_progress_v2.xlsx`
- `project_plan_rd_department_2024Q1.docx`

## 文件上传注意事项

1. **单文件大小**：建议不超过50MB
2. **文件格式**：优先使用标准格式（PDF、DOCX、XLSX）
3. **编码问题**：中文文件确保UTF-8编码
4. **扫描件**：OCR识别可能需要额外处理
