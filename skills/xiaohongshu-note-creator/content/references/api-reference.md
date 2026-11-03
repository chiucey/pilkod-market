# 小红书发布API参考

## Cookie获取方式

### 方式1：浏览器开发者工具
1. 登录小红书网页版 (https://creator.xiaohongshu.com)
2. 按F12打开开发者工具
3. 切换到Network标签
4. 刷新页面，找到任意请求
5. 复制Request Headers中的Cookie

### 方式2：浏览器扩展
使用EditThisCookie等扩展导出Cookie

## 发布笔记API

### 接口信息
- **方法**: POST
- **URL**: `https://creator.xiaohongshu.com/api/creator/post/released`
- **Headers**:
  ```
  Cookie: {your_cookies}
  Content-Type: application/json
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
  ```

### 请求体结构

```json
{
  "title": "笔记标题",
  "desc": "笔记正文内容",
  "note_id": "可选，更新时使用",
  "at_tag_uids": [],
  "topic_ids": [],
  "post_time": "",
  "image_list": [
    {
      "width": 1125,
      "height": 1500,
      "url": "图片URL",
      "type": "jpeg"
    }
  ]
}
```

### 注意事项

1. **Cookie有效期**：Cookie通常有时效性，过期需重新获取
2. **图片上传**：需先上传图片到小红书服务器获取URL
3. **频率限制**：避免频繁发布，建议间隔至少5分钟
4. **敏感词检测**：发布前建议自检敏感词

## 风险提示

⚠️ 使用Cookie自动发布存在以下风险：
- Cookie泄露可能导致账号安全问题
- 平台策略变化可能导致API失效
- 频繁发布可能触发平台风控

建议优先使用官方开放平台接口进行正规发布。
