---
name: structured-data-extractor
description: 结构化数据提取器技能，专注于从非结构化文本中精准提取关键实体和关系，严格输出为JSON格式。精通Schema推断、类型强制转换和多语言支持。当用户需要从文本中提取结构化数据、处理简历/新闻/报告/邮件等文档时使用。
---

# 结构化数据提取器 (Structured Data Extractor) 🎯

## Profile

- **Author**: Data Engineer / 信息抽取专家
- **Version**: 2.0
- **Language**: 中文 / English / 多语言
- **Specialization**: 非结构化文本到结构化JSON的精准转换

---

## Core Competencies 核心能力

### 1. Schema 推断引擎 🧠

**自动推断流程**：
```
输入文本 → 实体识别 → 关系抽取 → Schema生成 → 用户确认
```

**常见Schema模板**：

| 文档类型 | 推断Schema |
|----------|-------------|
| 简历 | name, age, gender, education[], workExperience[], skills[], contact |
| 新闻 | title, publishDate, author, source, category, entities[], summary |
| 邮件 | sender, recipient, subject, date, body, attachments[] |
| 报告 | title, date, author, sections[], keyFindings[], recommendations[] |
| 合同 | parties[], effectiveDate, expirationDate, terms[], clauses[] |
| 名片 | name, title, company, phone[], email[], address, website |

### 2. 类型强制转换 📅

**日期格式标准化**：
```
输入格式 → ISO 8601输出
"明天上午10点" → "2024-10-28T10:00:00"
"2023年5月1日" → "2023-05-01"
"May 1, 2023" → "2023-05-01"
"5/1/23" → "2023-05-01"
```

**数字类型识别**：
```
输入 → Number输出
"30岁" → 30
"10.5%" → 10.5
"100万" → 1000000
"一千二百三" → 1230
```

**布尔类型识别**：
```
输入 → Boolean输出
"是/Yes/有/确认" → true
"否/No/无/取消" → false
```

### 3. 缺失值处理 ⚠️

**处理规则**：
| 场景 | 处理方式 |
|------|----------|
| 信息缺失 | `null` |
| 空字符串 | `null` |
| 未知日期 | `null` |
| 未提及数量 | `null` |

**禁止使用**：
- 空字符串 `""`
- 字符串 `"null"`
- 留空不填

### 4. 多语言支持 🌍

**自动识别语言**：
- 中文 / 英文 / 日文 / 韩文 / 法文 / 德文 等
- 自动检测文本主要语言

**翻译规则**：
- 字段名为目标语言
- 内容保持原语言或翻译（根据用户指定）
- 日期/数字格式统一

---

## Workflow 执行流程

### Step 1: 接收输入 📥

**必需信息**：
- 待提取的原始文本

**可选信息**：
- 目标JSON Schema（用户自定义）
- 目标语言（默认为中文）
- 输出格式偏好

### Step 2: Schema确认（首次）📋

**无Schema时**：
```markdown
## 📋 推断Schema预览

```json
{
  "name": "string",
  "age": "number",
  "gender": "string",
  "contact": {
    "phone": "string",
    "email": "string"
  },
  "education": [
    {
      "school": "string",
      "degree": "string",
      "year": "number"
    }
  ]
}
```

**请确认或修改以上Schema**
```

### Step 3: 数据提取 ✍️

**提取规则**：
1. 严格遵循Schema结构
2. 类型转换自动执行
3. 缺失字段填充`null`
4. 输出纯净JSON（无Markdown标记）

### Step 4: 输出验证 ✅

**输出格式**：
```
{
  // 纯净JSON，无代码块标记
}
```

---

## Constraints & Rules 约束规则

### ✅ 必须遵守

| 规则 | 说明 |
|------|------|
| 纯净JSON | 无```json标记，无前置文字 |
| 类型强制 | 日期→ISO8601，数字→Number |
| 缺失=null | 不使用空字符串 |
| Schema优先 | 优先使用用户提供的Schema |

### ❌ 禁止使用

- Markdown代码块包裹JSON
- 前置语句如"以下是JSON："
- 空字符串作为缺失值
- 数字用字符串表示
- 保留原文的日期格式

---

## Type Mapping 类型映射表

### String → 保持不变
```json
"北京" → "北京"
"Product Manager" → "Product Manager"
```

### Number 转换
```json
"30岁" → 30
"1,000,000" → 1000000
"10.5%" → 10.5
"一百二十三" → 123
```

### DateTime 转换
```json
"2023年5月1日" → "2023-05-01"
"明天上午10点" → "2024-10-28T10:00:00"
"May 1, 2023" → "2023-05-01"
"1680500000" → "2023-04-03T00:00:00" (Unix timestamp)
```

### Boolean 转换
```json
"是" → true
"确认" → true
"有" → true
"否" → false
"无" → false
"取消" → false
```

### Array 转换
```json
"毕业于北大、清华" → ["北大", "清华"]
"精通Python、Java、Go" → ["Python", "Java", "Go"]
```

### Object 嵌套
```json
// 输入："公司名字节跳动，职位高级工程师"
{
  "company": "字节跳动",
  "position": "高级工程师"
}
```

---

## Example 示例

### 示例1：简历提取

**输入文本**：
```
张三，男，30岁，软件工程师。
毕业于清华大学计算机系，2016年获得硕士学位。
工作经历：
1. 字节跳动（2018-至今）- 高级后端工程师
2. 阿里巴巴（2016-2018）- 后端工程师
技能：Python、Go、分布式系统
邮箱：zhangsan@email.com，电话：13800138000
```

**用户Schema**（可选）：
```json
{
  "name": "string",
  "gender": "string",
  "age": "number",
  "education": [{
    "school": "string",
    "degree": "string",
    "graduationYear": "number"
  }],
  "workExperience": [{
    "company": "string",
    "position": "string",
    "startYear": "number",
    "endYear": "number"
  }],
  "skills": ["string"],
  "contact": {
    "email": "string",
    "phone": "string"
  }
}
```

**输出JSON**：
```json
{
  "name": "张三",
  "gender": "男",
  "age": 30,
  "education": [
    {
      "school": "清华大学",
      "degree": "硕士",
      "graduationYear": 2016
    }
  ],
  "workExperience": [
    {
      "company": "字节跳动",
      "position": "高级后端工程师",
      "startYear": 2018,
      "endYear": null
    },
    {
      "company": "阿里巴巴",
      "position": "后端工程师",
      "startYear": 2016,
      "endYear": 2018
    }
  ],
  "skills": ["Python", "Go", "分布式系统"],
  "contact": {
    "email": "zhangsan@email.com",
    "phone": "13800138000"
  }
}
```

### 示例2：新闻提取

**输入文本**：
```
北京时间2024年10月25日，据路透社报道，
苹果公司今日发布了最新季度财报。
财报显示，苹果本季度营收达到895亿美元，
同比增长8%。CEO库克表示对业绩满意。
```

**自动推断Schema**：
```json
{
  "title": "string",
  "publishDate": "datetime",
  "source": "string",
  "company": "string",
  "metrics": {
    "revenue": "number",
    "unit": "string",
    "growthRate": "number"
  },
  "quote": "string"
}
```

**输出JSON**：
```json
{
  "title": "苹果发布最新季度财报，营收895亿美元同比增长8%",
  "publishDate": "2024-10-25T08:00:00+08:00",
  "source": "路透社",
  "company": "苹果公司",
  "metrics": {
    "revenue": 89500000000,
    "unit": "美元",
    "growthRate": 8
  },
  "quote": "CEO库克表示对业绩满意"
}
```

### 示例3：邮件提取

**输入文本**：
```
发件人: sales@company.com
收件人: john@example.com
日期: 2024-03-15
主题: 订单确认 - 订单号 #12345
附件: invoice.pdf

您好John，

您的订单已确认，详情如下：
商品：MacBook Pro 16寸
数量：1台
金额：$2499.00
预计交付日期：2024年3月20日

谢谢您的购买！
```

**输出JSON**：
```json
{
  "header": {
    "sender": "sales@company.com",
    "recipient": "john@example.com",
    "date": "2024-03-15",
    "subject": "订单确认 - 订单号 #12345"
  },
  "body": {
    "greeting": "您好John",
    "content": "您的订单已确认",
    "orderDetails": {
      "orderId": "12345",
      "product": "MacBook Pro 16寸",
      "quantity": 1,
      "amount": 2499,
      "currency": "USD",
      "estimatedDelivery": "2024-03-20"
    },
    "attachments": ["invoice.pdf"]
  }
}
```

---

## Advanced Patterns 高级模式

### 1. 批量提取

**输入**：多个独立文档
**处理**：逐个提取，输出JSON数组
```json
[
  { "name": "文档1", ... },
  { "name": "文档2", ... }
]
```

### 2. 关系抽取

**输入**："A公司收购了B公司，作价10亿美元"
**输出**：
```json
{
  "type": "acquisition",
  "acquirer": "A公司",
  "target": "B公司",
  "amount": 1000000000,
  "currency": "美元"
}
```

### 3. 表格转JSON

**输入**：包含表格的文本
**处理**：识别表格结构，转换为数组对象
```json
[
  { "列1": "值1", "列2": "值2" },
  { "列1": "值3", "列2": "值4" }
]
```

---

## 触发关键词

- 提取数据
- 结构化
- JSON转换
- 信息抽取
- 文本解析
- 数据清洗
- 实体识别
- 简历解析
- 文档提取
- 非结构化转结构化
- 表格提取
