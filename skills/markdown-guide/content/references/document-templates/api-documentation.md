# API 文档模板规范

## 文档定位

API 文档用于详细描述接口规范，包括请求方法、参数、响应格式、错误码等。

## 标准结构

```markdown
# API 文档

## 概述

简要描述 API 的用途和设计原则。

## 基础信息

- **Base URL**: `https://api.example.com/v1`
- **认证方式**: Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 获取访问令牌

```http
POST /auth/token
Content-Type: application/json

{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

**响应示例：**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## 接口列表

### 用户管理

#### 创建用户

```http
POST /users
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "张三",
  "email": "zhangsan@example.com",
  "role": "user"
}
```

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 用户名，2-50 字符 |
| email | string | 是 | 邮箱地址 |
| role | string | 否 | 角色，默认 user |

**响应示例：**

```json
{
  "id": "user_123",
  "name": "张三",
  "email": "zhangsan@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### 获取用户列表

```http
GET /users?page=1&limit=20
Authorization: Bearer <token>
```

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| limit | integer | 20 | 每页数量，最大 100 |
| role | string | - | 按角色筛选 |

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | 认证失败 | 检查 Token 是否有效 |
| 403 | 权限不足 | 联系管理员授权 |
| 404 | 资源不存在 | 检查资源 ID |
| 429 | 请求过于频繁 | 稍后重试 |
| 500 | 服务器错误 | 联系技术支持 |

## 数据模型

### User

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 用户唯一标识 |
| name | string | 用户名 |
| email | string | 邮箱地址 |
| role | string | 角色：admin, user, guest |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 速率限制

- 每分钟最多 60 次请求
- 每小时最多 1000 次请求

响应头会返回限制信息：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705312800
```

## 变更日志

### v2.0.0 (2024-01-15)

- 新增批量操作接口
- 优化分页性能
- 废弃旧版搜索接口

## SDK 示例

### JavaScript

```javascript
import { ApiClient } from 'example-sdk';

const client = new ApiClient('your_api_key');
const users = await client.users.list({ page: 1 });
```

### Python

```python
from example_sdk import ApiClient

client = ApiClient('your_api_key')
users = client.users.list(page=1)
```
```

## 必选章节

| 章节 | 说明 |
|------|------|
| 概述 | API 整体说明 |
| 认证 | 认证方式和流程 |
| 接口列表 | 按模块组织的接口说明 |
| 请求参数 | 每个接口的参数说明 |
| 响应示例 | 成功和失败的响应示例 |
| 错误码 | 完整的错误码列表 |

## 推荐章节

| 章节 | 说明 |
|------|------|
| 速率限制 | 频率限制说明 |
| 数据模型 | 公共数据结构定义 |
| 变更日志 | API 版本历史 |
| SDK 示例 | 多语言 SDK 使用示例 |

## 质量检查要点

1. **认证说明**：明确说明认证方式
2. **参数表格**：每个接口都有参数说明表格
3. **响应示例**：提供完整的 JSON 响应示例
4. **错误码**：列出常见错误码及解决方案
5. **HTTP 方法**：明确标注 GET/POST/PUT/DELETE

## 接口说明规范

每个接口应包含以下信息：

1. **HTTP 方法和路径**
2. **请求头**（如认证信息）
3. **请求参数**（Query/Body）
4. **响应示例**
5. **错误场景**

## 示例代码要求

- 提供可直接运行的代码
- 包含错误处理逻辑
- 至少提供 2 种语言示例
