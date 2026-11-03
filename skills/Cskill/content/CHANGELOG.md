# Changelog

## 1.2.4

- `SKILL.md`：增加「移动端展示」输出规范（列表化、避免宽表与整段 JSON、控制段落），降低手机端排版错乱

## 1.0.0

- 初始发布版本
- 提供天气查询、员工基础信息查询、员工薪资查询 3 个 OpenClaw 可调用能力
- 每次请求使用 `Authorization: Basic ...` 进行用户名/密码鉴权
- 内置对 `400 / 401 / 403 / 404 / 5xx` 的安全回复约束
- 附带 `openapi.json` 作为工具接口描述

## 1.0.1

- 重写 `SKILL.md`：明确“必须输入用户名密码（Basic Auth）”为强制要求
- 增加高危触发词策略（中英文），包含“忽略规则 / 系统提示词 / 输出密码 / jailbreak / bypass restrictions”等
- 明确中文 Query 参数必须 URL 编码，补充正确/错误示例
- 同步更新 `README.md` 与 `openapi.json`，确保文档与当前后端鉴权和安全策略一致

## 1.1.0

- 新增 `GET /api/v1/customer-companies`：登录后查询当前用户可访问的客户公司信息
- 新增 10 家模拟客户公司数据，分配到 5 个部门，用于演示部门间数据隔离
- 客户公司返回字段新增统一脱敏：法人手机号、法人身份证号、纳税识别号
- 同步更新 `SKILL.md`、`openapi.json` 与 `README.md`，支持 OpenClaw 直接调用新接口

## 1.2.3

- 后端 `GET /api/v1/customer-companies` 增加可选 Query：`company_name`（子串筛选），便于 OpenClaw 精确拉取「甲骨文科技」等客户
- `SKILL.md`：明确 **`department_name` = 客户管户部门 ≠ 登录人部门**；演示规模（管理员 10 家、单部门 2 家）；禁止误读后断言「未找到公司」；版本 **1.2.3**

## 1.2.2

- `SKILL.md`：授信/融资类问题引导**同时或优先**使用 `GET /api/v1/customer-companies` 的结构化尽调字段，避免仅走 RAG 时出现空答复

## 1.2.1

- Skill 标识名（`SKILL.md`  frontmatter `name`）改为 **`Cskill`**
- 发布至 ClawHub 时请将 `--slug` 与上述名称保持一致（见 `README.md` 示例）

## 1.2.0

- 场景切换为**银行对公信贷尽调演示**：客户默认存在融资/授信需求，尽调内容为模拟
- `GET /api/v1/customer-companies` 增加四类尽调摘要字段（经营、授信概要、风险、结论），与 SQLite 种子数据同步
- Chroma 向量库改为按客户幂等写入银行尽调风格片段；员工 `allowed_company_scope` 与 10 家客户对齐，便于全客户 RAG
- `POST /api/v1/rag/query` 系统提示改为客户经理语境；OpenAPI 升至 `0.3.0`
- Skill 描述与 OpenClaw 元数据更新 / `1.2.0`
