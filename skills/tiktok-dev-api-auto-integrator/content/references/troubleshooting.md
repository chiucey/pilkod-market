# 故障排除指南

## 常见问题

### 1. 授权失败

#### 问题：授权码无效

**症状**：
```
Error: invalid_grant - The provided authorization grant is invalid
```

**解决方案**：
- 授权码只能使用一次
- 授权码有效期为 10 分钟
- 确保 redirect_uri 与注册时一致

#### 问题：redirect_uri 不匹配

**症状**：
```
Error: redirect_uri_mismatch
```

**解决方案**：
- 检查开发者后台配置的回调地址
- 确保完全匹配（包括协议和路径）

### 2. Token 相关问题

#### 问题：Token 已过期

**症状**：
```
Error: unauthorized - Access token expired
```

**解决方案**：
```python
if token.is_expired():
    integrator.oauth.refresh_access_token()
```

#### 问题：Token 刷新失败

**症状**：
```
Error: invalid_grant - Refresh token is invalid
```

**解决方案**：
- 刷新令牌有效期为 30 天
- 需要用户重新授权

### 3. API 调用问题

#### 问题：权限不足

**症状**：
```
Error: forbidden - Insufficient permissions
```

**解决方案**：
- 检查申请的权限范围
- 在开发者后台重新配置权限
- 确保已包含所需的所有 scope

#### 问题：限流

**症状**：
```
Error: rate_limit - Too many requests
```

**解决方案**：
```python
# 实现指数退避重试
def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except APIError as e:
            if e.code == "rate_limit":
                time.sleep(2 ** i)  # 1, 2, 4 秒
            else:
                raise
```

### 4. 文件上传问题

#### 问题：文件格式无效

**症状**：
```
UploadError: 不支持的文件格式: .exe
```

**解决方案**：
- 游戏包必须是 .zip 格式
- HTML5 游戏打包成单个 ZIP
- 包含 index.html 入口文件

#### 问题：文件太大

**症状**：
```
UploadError: 文件太大: 600MB，最大 500MB
```

**解决方案**：
- 压缩资源文件
- 移除不必要的文件
- 使用 CDN 托管静态资源

#### 问题：上传中断

**症状**：
上传进度停在 50% 不动

**解决方案**：
- 使用断点续传功能
- 检查网络连接
- 增加超时时间

### 5. 审核相关问题

#### 问题：审核被拒

**常见驳回原因**：

| 原因 | 说明 | 解决方案 |
|------|------|----------|
| 图标不合格 | 图标模糊或违规 | 使用 512x512 PNG 图标 |
| 截图缺失 | 缺少应用截图 | 上传 5-10 张截图 |
| 描述不符 | 描述与实际功能不符 | 准确描述应用功能 |
| 崩溃/闪退 | 应用无法正常运行 | 测试修复后重新提交 |
| 权限滥用 | 申请不必要的权限 | 只申请必要权限 |

#### 问题：审核时间过长

**症状**：
审核状态一直是 "in_review"

**解决方案**：
- 首次审核通常需要 24-48 小时
- 复审通常需要 12-24 小时
- 检查是否有遗漏的材料
- 联系 TikTok 开发者支持

### 6. 网络问题

#### 问题：SSL 证书错误

**症状**：
```
SSLError: Certificate verify failed
```

**解决方案**：
- 更新系统根证书
- 使用 requests 的 verify 参数：
  ```python
  requests.get(url, verify='/path/to/cert.pem')
  ```

#### 问题：代理问题

**症状**：
无法连接到 TikTok API

**解决方案**：
```python
proxies = {
    "http": "http://proxy:8080",
    "https": "http://proxy:8080"
}
requests.get(url, proxies=proxies)
```

## 日志调试

### 启用调试日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### 常见日志级别

| 级别 | 说明 |
|------|------|
| DEBUG | 详细信息（请求/响应） |
| INFO | 一般信息 |
| WARNING | 警告 |
| ERROR | 错误 |

## 获取帮助

如果问题仍未解决：

1. 查看 [TikTok 开发者文档](https://developers.tiktok.com/)
2. 检查 [API 状态页](https://status.tiktok.com/)
3. 联系 TikTok 开发者支持
