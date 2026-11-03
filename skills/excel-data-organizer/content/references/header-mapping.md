---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100b0475fcbea9c43bbeb7ab80b8331d5a3540868911aa5469385e682e617a88b5102204befbaa66e9165ffe1c4c04fd330377c30b3cfc7c465457d497a33d7ccdb4e77
    ReservedCode2: 3045022100e9753ed6467b8ce26c3682ff709085403076bcb42fe6d829b5d711496797fca702207d92fa7889811b60781fe3c046362058d69eeacdb45dc4dbd0984fd4f999bc7e
---

# 表头映射参考表

## 常用字段同义词映射

### 个人信息类

| 标准名称 | 同义词变体 |
|---------|----------|
| 姓名 | name, 名称, 客户名, 员工姓名, 用户名, 客户名称 |
| 工号 | ID, id, 编号, 员工号, 编号, employee_id, employeeId |
| 手机 | phone, tel, 电话, 联系电话, 手机号, mobile, 手机号码 |
| 邮箱 | email, 电子邮件, 邮箱地址, mail |
| 地址 | address, 住址, 家庭地址, 收货地址 |

### 组织架构类

| 标准名称 | 同义词变体 |
|---------|----------|
| 部门 | dept, department, 科室, 组别, 事业部 |
| 职位 | position, title, 岗位, 职务, job_title, jobTitle |
| 公司 | company, 企业, 单位, 机构, corporation |

### 时间日期类

| 标准名称 | 同义词变体 |
|---------|----------|
| 入职日期 | hire_date, hiredate, 入职时间, 加入日期, entry_date |
| 创建日期 | create_date, createdate, 创建时间, 生成日期, 注册日期 |
| 更新时间 | update_date, updatedate, 修改时间, 最后更新 |
| 出生日期 | birth_date, birthday, 生日, 出生年月, dob |

### 财务数据类

| 标准名称 | 同义词变体 |
|---------|----------|
| 金额 | amount, 数额, 总额, sum, total |
| 价格 | price, 单价, 售价, cost |
| 数量 | quantity, qty, 数目, count |
| 订单号 | order_id, orderId, 订单编号, 订单号, order_no |

### 状态标识类

| 标准名称 | 同义词变体 |
|---------|----------|
| 状态 | status, 状态, 情况, 状况 |
| 是否 | is_, 是否, flag, 标识 |
| 备注 | remark, note, 备注, 说明, 注释 |

## 表头命名规范

### 推荐格式

1. **简短明确**：2-6 个汉字或英文单词
2. **无特殊字符**：避免 `!@#$%^&*()[]{}`
3. **统一语言**：混排时建议中英分开或统一用英文
4. **无空格或下划线连接**：`员工姓名` 或 `employee_name`

### 不推荐

| 不推荐 | 原因 | 改进建议 |
|-------|------|---------|
| "这个字段的名字" | 过长 | "姓名" |
| "A" | 含义不明 | 根据实际用途命名 |
| "Col1/Col2" | 无意义 | 使用描述性名称 |
| "Sum(Total)" | 包含函数符号 | "总计" |

## 数据格式标准

### 日期格式

| 标准 | 格式 | 示例 |
|-----|------|------|
| ISO | YYYY-MM-DD | 2024-01-15 |
| 中文 | YYYY年MM月DD日 | 2024年01月15日 |
| 短格式 | YY-MM-DD | 24-01-15 |

**推荐**：统一使用 ISO 格式 (YYYY-MM-DD)

### 数字格式

- 金额：保留 2 位小数，如 `1999.99`
- 百分比：`25.5%`
- 手机号：11位数字，不添加分隔符或横线

### 文本格式

- 去除首尾空格
- 全角转半角（根据需要）
- 统一编码为 UTF-8
