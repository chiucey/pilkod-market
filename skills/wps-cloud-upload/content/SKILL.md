---
name: wps-cloud-upload
description: 当用户要求上传文档到金山文档、分享到WPS云、保存文件到WPS云端时使用。此技能处理文档上传、文件夹管理和云端分享链接生成。
---

# WPS云文档上传技能

将本地文档上传至金山文档（WPS云文档）平台。

## 使用场景

- 将agent生成的PDF、Word、Excel等文档上传到WPS云端
- 创建云端文件夹结构
- 生成分享链接供他人访问
- 管理云端文档和权限

## 前置准备

### 1. 获取WPS API凭证

使用金山文档API需要以下凭证：
- `WPS_APP_ID`: 应用标识
- `WPS_APP_SECRET`: 应用密钥
- `WPS_ACCESS_TOKEN`: 访问令牌（需OAuth2.0获取）

### 2. 检查本地文件

确认要上传的文件存在且格式支持：
- PDF (.pdf)
- Word文档 (.docx, .doc)
- Excel表格 (.xlsx, .xls)
- PPT演示文稿 (.pptx, .ppt)
- 文本文件 (.txt)

## 核心流程

### 步骤1：身份验证

```python
# 获取Access Token
def get_wps_access_token(app_id, app_secret):
    token_url = "https://open.wps.cn/oauth2/token"
    # 实现OAuth2.0客户端凭证流程
```

### 步骤2：上传文件

```python
# 上传文件到WPS云
def upload_to_wps(file_path, folder_id=None):
    upload_url = "https://open.wps.cn/api/v1/files/upload"
    # multipart/form-data 上传
```

### 步骤3：设置权限和分享

```python
# 设置文档权限并生成分享链接
def share_document(file_id, permission="view"):
    share_url = "https://open.wps.cn/api/v1/files/{file_id}/share"
    # 返回分享链接和提取码
```

## API端点参考

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取Token | POST | /oauth2/token |
| 上传文件 | POST | /api/v1/files/upload |
| 创建文件夹 | POST | /api/v1/files/createFolder |
| 获取文件列表 | GET | /api/v1/files/list |
| 生成分享链接 | POST | /api/v1/files/{file_id}/share |
| 删除文件 | DELETE | /api/v1/files/{file_id} |

## 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 401 | Token过期 | 重新获取access_token |
| 403 | 权限不足 | 检查应用授权范围 |
| 413 | 文件过大 | 压缩或分割文件 |
| 415 | 格式不支持 | 转换文件格式 |

## 完整工作流示例

```
1. 用户请求："将报告.pdf上传到金山文档"
2. 技能执行：
   - 验证文件存在性
   - 获取/刷新WPS访问令牌
   - 上传文件到指定文件夹
   - 设置阅读权限
   - 返回分享链接
3. 输出：分享链接和提取码（如有）
```

## 注意事项

- 单文件大小限制：100MB
- 支持批量上传（需循环处理）
- 云端文件夹ID可通过 `createFolder` 获取
- 分享链接默认有效期：7天
