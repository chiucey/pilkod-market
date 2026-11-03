---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9eb424fb1051a2c2f27ffe52ee49edbf
    PropagateID: 9eb424fb1051a2c2f27ffe52ee49edbf
    ReservedCode1: 3045022100dd3c5884fc6633548fdbfa94fe9a703369c21c110ca57b3306a600da609edf8c02201f5764c36535aa099776ef36e70aae824119a71cc7347f16054770eba63a85ca
    ReservedCode2: 30440220103bc1dee188dfe7d6c8bc07b28103214498774f5b53bc8754bf161b75ed84eb022048519bbb8fe8df5a50428568f07812f8de2ecf0e79696f6ecef549a4b5720582
description: |-
    Notion 记账/财务数据分析技能。通过 Notion API 读取支出/收入流水表，自动完成： 1) 全量数据获取（自动翻页，处理 has_more） 2) 关系字段解析（relation ID → 实际名称） 3) 按年/月/类别的财务分析 4) 生成结构化分析报告
    触发场景：分析 Notion 记账数据、生成财务报告、查看收支趋势。 前置条件：用户需提供 Notion Integration Token（secret_xxx 格式）。 数据源：需知道支出/收入流水表的 data_source_id。
name: notion-accounting-analysis
---

# Notion 记账数据分析 Skill

## 核心经验（踩坑总结）

### ✅ 正确的字段识别逻辑

支出流水表通常有**两个**分类字段，优先级如下：

| 字段 | 类型 | 说明 |
|------|------|------|
| `支出类别` / `收入来源` | **relation** | 指向另一张表，存的是ID，**必须**通过 API 查询真实名称 |
| `标签` / `标签字段` | select | 直接存文字，直接可用 |

**错误做法**：只用 `select` 字段，忽略 `relation` 主分类。
**正确做法**：两个字段都要读，`relation` 需要额外一步去查名字。

### ✅ 分页必须遍历完所有页

```javascript
// 正确：循环直到 has_more = false
let cursor = null;
do {
  const body = JSON.stringify(cursor ? { page_size: 100, start_cursor: cursor } : { page_size: 100 });
  // POST /v1/data_sources/{id}/query
  // 拿到 page.has_more + page.next_cursor
  cursor = page.has_more ? page.next_cursor : null;
} while (cursor);
```

### ✅ relation 字段解析步骤

```
relation 字段值：[{"id": "xxx-id-xxx"}]
            ↓
GET /v1/pages/{id}  ← 通过这个 API 获取 relation 对应的记录名称
            ↓
字段优先取：properties['名称'].title[0].plain_text
          或 properties['Name'].title[0].plain_text
          或 properties.title.title[0].plain_text
```

## 执行流程

### 第 1 步：确认数据源

如果用户没有提供 data_source_id，用搜索接口查找：

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "支出", "page_size": 20}' | jq '.results[] | {id, title: (.properties.Name.title[0].plain_text // .title[0].plain_text)}'
```

### 第 2 步：获取全量数据（带分页）

```bash
# 先拿第一页，判断 has_more
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100}' > /tmp/page1.json

# 如果 has_more=true，用 next_cursor 继续拿
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100, "start_cursor": "<cursor>"}' > /tmp/page2.json
```

合并所有页数据后再分析，不要分析完一页就下结论。

### 第 3 步：收集所有 relation ID → 名称

用 Node.js 分析时，先建立 relation ID → 名称映射：

```javascript
const relMap = {};
// 从原始数据中收集所有 relation IDs
const allRelIds = [...new Set(results.flatMap(r =>
  (r.properties['支出类别']?.relation || []).map(rel => rel.id)
))];

// 批量查询每个 ID 对应的页面名称
// GET /v1/pages/{id}
// 建立映射：{ 'id': '类别名称' }
```

### 第 4 步：字段提取规范

```javascript
// 支出表
const fmt = (p) => ({
  date:    p.properties['支出日期']?.date?.start,         // date 类型
  amount:  p.properties['支出金额']?.number || 0,          // number 类型
  cat:     (p.properties['支出类别']?.relation || [])[0]?.id, // relation → 用 ID 查名称
  tag:     p.properties['标签']?.select?.name || null,    // select → 直接用
  note:    (p.properties['备注']?.rich_text || []).map(t => t.plain_text).join('')
});

// 收入表
const fmtInc = (p) => ({
  date:    p.properties['收入日期']?.date?.start,
  amount:  p.properties['收入金额']?.number || 0,
  source:  (p.properties['收入来源']?.relation || [])[0]?.id,
  note:    (p.properties['备注']?.rich_text || []).map(t => t.plain_text).join('')
});
```

### 第 5 步：分析维度

- 按年/月/季度汇总
- 按类别（relation 解析后）汇总
- 按标签（select）交叉分析
- TOP N 大额支出
- 收入 vs 支出对比

## 常见错误处理

| 错误现象 | 原因 | 解决 |
|----------|------|------|
| 类别全是"未分类" | 用了 select 字段，relation 分类全丢了 | 改用 relation ID 查表 |
| 总支出偏低 | 只查了第一页（100条），还有后续页 | 循环翻页合并 |
| relation ID 查不到名称 | ID 对应的记录不属于 integration 的可见范围 | 在 Notion 中给该页面添加 connection |
| 金额对不上 | 同时用了"标签"和"支出类别"，重复计算 | 一个类别只取一个字段，优先 relation |

## 已知 relation ID 参考（来自真实数据）

以下 relation ID 已在实际环境中验证，供参考：

| relation ID | 对应类别名称 |
|------------|------------|
| `2e1bd123-80a0-817c-a724-e5eab4b6a6c7` | 房租 |
| `2e1bd123-80a0-80e8-a87a-cc3f8aaf917e` | 旅游娱乐 |
| `2e1bd123-80a0-8081-9e99-f711c1eba40e` | 房贷 |
| `2e1bd123-80a0-815a-81b6-c5bda98d020e` | 餐饮 |
| `2e1bd123-80a0-8004-aaab-dfc064089761` | 总记账 |
| `2e1bd123-80a0-806f-b571-db88e01d2576` | 医疗 |
| `2e1bd123-80a0-8059-b71c-d7d6f4f1acd8` | 购物 |
| `2e1bd123-80a0-80d4-8666-c51e4aea5c9e` | 所得税 |
| `2e1bd123-80a0-817f-8d07-fa40e110bdc6` | 交通 |
| `2e1bd123-80a0-81dd-8d05-d5984f42738b` | 人情往来 |
| `2e1bd123-80a0-8084-a89d-f5d45b19c689` | 专项 |
| `2e1bd123-80a0-810d-9884-f3a123b24776` | 运动 |
| `2e1bd123-80a0-8054-a573-fdeec9dd88b7` | 公司额外 |
| `2e1bd123-80a0-81de-966a-ebe963021603` | 日用 |
| `336bd123-80a0-8022-8aac-fb6c091a27c2` | 公司额外 |

> 💡 提示：如果发现新的 relation ID 查不到名称，在 Notion 中打开该记录页面 → 右上角 `...` → `Add connections` → 添加你的 Integration 即可。

## 分析报告模板

```markdown
# {年份} 年度财务分析报告

> 数据来源：Notion {数据库名称}
> 分析范围：{年}年{月}月 – {月}月（{n}笔支出，{n}笔收入）

## 一、收支总览
## 二、月度趋势
## 三、类别分析（含 relation 正确名称）
## 四、标签交叉分析（select vs relation）
## 五、TOP 大额支出
## 六、优化建议
```
