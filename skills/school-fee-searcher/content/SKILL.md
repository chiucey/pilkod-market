---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: bcdae1696f7582fb0f0e868903a5bd97
    PropagateID: bcdae1696f7582fb0f0e868903a5bd97
    ReservedCode1: 304402207f50b12be50fb334e72deeed8b1b52a1372138bc31cee3843cea032d40dab972022073b0b8492400ba38426b104fb95afe0cafea79c5e457c242b5e8c47c62b50ab6
    ReservedCode2: 30450221009b74a021533abc9c6b93a26dc3aed7f77e1badb635a2b073976cd4df196ecd7702204f06dd83a315760ab29733bca63ab2cb238133240195633fa56903d44141bf80
description: 用于搜索学校官网URL并查找国际学生费用的技能。当用户要求查找学校的国际学生学费、费用信息、收费标准，或需要找到学校的官方网站时使用。
name: school-fee-searcher
---

# 学校国际生费用搜索技能

## 核心能力
1. 搜索学校官网URL
2. 提取国际学生费用信息

## 工作流程

### 步骤1：确定学校名称
- 从用户输入中提取学校名称
- 如果信息不完整，询问用户补充

### 步骤2：搜索学校官网
使用 `batch_web_search` 工具搜索学校官网：

```
查询模板：
- "{学校名称} 官网" / "{学校名称} official website"
- "{学校名称} international students tuition" (英文搜索)
```

### 步骤3：提取费用信息
使用 `extract_content_from_websites` 工具访问学校官网，提取：
- 国际学生学费
- 申请费
- 杂费
- 生活费预算（如有）

### 步骤4：输出结果
以结构化格式返回：
- 学校官方网站URL
- 国际生学费（按学年/学期）
- 其他相关费用
- 费用来源页面链接
- 信息时效性说明

## 示例

**用户输入**："查找哈佛大学的国际学生费用"

**执行流程**：
1. 搜索 "Harvard University official website"
2. 定位国际学生费用页面
3. 提取最新学费数据
4. 返回结构化结果

## 注意事项
- 优先查找英文官方网站获取最准确信息
- 标注信息来源和采集时间
- 如官网无明确数据，说明原因并提供替代查询建议