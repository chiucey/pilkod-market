# 微信公众号 API 参考文档

## 官方文档链接

### 基础接口
- **Access Token 获取**: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
- **接口调用频率限制**: https://developers.weixin.qq.com/doc/offiaccount/Operating_Guide/Interface_call_restrictions_description.html

### 草稿箱接口
- **草稿箱官方文档**: https://developers.weixin.qq.com/doc/subscription/guide/product/draft.html
- **新增草稿**: POST `https://api.weixin.qq.com/cgi-bin/draft/add`
- **发布草稿**: POST `https://api.weixin.qq.com/cgi-bin/freepublish/submit`
- **查询发布状态**: GET `https://api.weixin.qq.com/cgi-bin/freepublish/get`

### 素材管理接口
- **上传图片（获取URL）**: POST `https://api.weixin.qq.com/cgi-bin/media/uploadimg`
  - 限制：≤2MB，jpg/png 格式
  - 返回：图片 URL
- **上传缩略图**: POST `https://api.weixin.qq.com/cgi-bin/media/upload`
  - 用于草稿封面图
  - 参数：type=image

## 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | access_token 无效 | 重新获取 access_token |
| 40007 | media_id 不正确 | 检查封面图是否正确上传 |
| 41005 | 缺少 media 数据 | 检查文件是否正确上传 |
| 44001 | 多媒体文件为空 | 检查文件路径是否正确 |
| 44002 | POST 数据为空 | 检查请求体是否正确 |
| 45009 | 接口调用超过限制 | 降低调用频率 |

## 发布流程图

```
用户投喂内容
    ↓
内容解析与排版
    ↓
配图获取与处理
    ↓
上传封面图 → 获取 thumb_media_id
    ↓
创建草稿 → 获取 media_id
    ↓
发布草稿 → 获取 publish_id
    ↓
微信后台审核（草稿箱可见）
    ↓
发布成功
```

## 权限要求

1. **服务号**：完整功能
2. **订阅号**：部分功能，发布需微信审核
3. **必须配置**：IP 白名单（在公众号后台设置）

## Access Token 缓存策略

- 有效期：7200 秒（2小时）
- 建议提前 5 分钟刷新
- 使用 Redis 或文件缓存
- 多实例部署时注意 token 同步
