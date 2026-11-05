# 微信公众号 API 参考

## 一、基础说明

微信公众号提供了草稿箱功能，开发者可以通过 API 创建和发布草稿。

### 1.1 认证方式
- 使用 Access Token 访问所有 API
- Access Token 需要 AppID 和 AppSecret 获取
- Token 有效期为 2 小时，需要自动刷新

### 1.2 接口基础地址
```
https://api.weixin.qq.com/cgi-bin/
```

## 二、草稿箱 API

### 2.1 新增草稿
**接口地址**：
```
POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN
```

**请求参数**：
```json
{
  "articles": [
    {
      "title": "文章标题",
      "author": "作者",
      "digest": "摘要",
      "content": "文章内容HTML",
      "content_source_url": "原文链接",
      "thumb_media_id": "封面图素材ID",
      "need_open_comment": 1,
      "only_fans_can_comment": 0
    }
  ]
}
```

**响应示例**：
```json
{
  "media_id": "xxxxxxxx"
}
```

### 2.2 获取草稿列表
**接口地址**：
```
GET https://api.weixin.qq.com/cgi-bin/draft/count?access_token=ACCESS_TOKEN
```

**响应**：
```json
{
  "total_count": 1
}
```

### 2.3 删除草稿
**接口地址**：
```
POST https://api.weixin.qq.com/cgi-bin/draft/delete?access_token=ACCESS_TOKEN
```

**请求参数**：
```json
{
  "media_id": "xxxxxxxx"
}
```

## 三、素材管理 API

### 3.1 新增永久素材（封面图）
**接口地址**：
```
POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=image
```

**支持格式**：
- 图片（image）: bmp, png, jpeg, jpg, gif
- 大小：不超过 2MB
- 尺寸：封面图建议 900 x 383

### 3.2 获取素材列表
**接口地址**：
```
POST https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=ACCESS_TOKEN
```

**请求参数**：
```json
{
  "type": "image",
  "offset": 0,
  "count": 20
}
```

## 四、发布相关 API

### 4.1 发布已编辑内容
注意：通过 API 创建的草稿需要通过草稿箱手动发布，或使用发布接口。

### 4.2 提交发布
**接口地址**：
```
POST https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token=ACCESS_TOKEN
```

**请求参数**：
```json
{
  "media_id": "xxxxxxxx"
}
```

## 五、凭证配置

### 5.1 必需凭证
```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret"
}
```

### 5.2 获取 Access Token
```
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
```

**响应**：
```json
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

## 六、工作流集成

### 6.1 完整发布流程

```
1. 获取 Access Token
   ↓
2. 上传封面图获取 thumb_media_id
   ↓
3. 创建草稿（包含完整 HTML 内容）
   ↓
4. 获取草稿 media_id
   ↓
5. 提交发布（可选）
```

### 6.2 注意事项

- 草稿箱最多存储 50 篇草稿
- 发布的文章会进入发表记录
- 通过 API 发布需要公众号已认证
- 封面图必须先上传为永久素材

## 七、错误码参考

| 错误码 | 说明 |
|--------|------|
| 40001 | 获取access_token时AppSecret错误 |
| 40013 | 无效的appid |
| 40125 | 无效的appsecret |
| 41002 | 缺少article参数 |
| 41004 | 缺少secret参数 |
| 44002 | POST数据包为空 |
| 44003 | 文件类型不支持 |
