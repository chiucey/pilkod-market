# 浏览器爬虫技能使用指南

## 快速开始

### 基本用法

```json
{
  "url": "https://example.com",
  "mode": "full",
  "retry": 1,
  "timeout": 10
}
```

### 模式详解

#### 1. full 模式 - 完整提取
返回页面的完整信息：
- title: 页面标题
- content: 清洗后的正文
- summary: 内容摘要
- links: 所有链接
- images: 所有图片
- status: 请求状态

#### 2. content 模式 - 仅正文
适用于文章、新闻等页面，仅提取标题和正文。

#### 3. links 模式 - 仅链接
返回页面中所有超链接的文本和URL。

#### 4. images 模式 - 仅图片
返回页面中所有图片的URL和alt属性。

## 实际应用示例

### 示例 1：爬取省市县数据
```
url: https://config.net.cn/tools/ProvinceCityCountry.html
mode: content
```

输出可保存为 CSV 格式：
```csv
省,市,县/区
北京市,北京市,东城区
北京市,北京市,西城区
...
```

### 示例 2：下载博客文章
```
url: https://blog.example.com/article-123
mode: full
```

### 示例 3：采集图片资源
```
url: https://gallery.example.com/album
mode: images
```

## 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| URL_INVALID | URL 格式错误 | 检查 URL 拼写 |
| TIMEOUT | 请求超时 | 增加 timeout 值 |
| RETRY_EXCEEDED | 重试次数耗尽 | 检查网络或目标站点 |
| BLOCKED | 被反爬拦截 | 立即停止 |
| PARSE_ERROR | 内容解析失败 | 返回原始错误 |

## 安全使用建议

1. **控制请求频率** - 建议间隔 2-3 秒
2. **设置合理超时** - 根据目标站点响应时间调整
3. **遵守 robots.txt** - 尊重网站爬虫协议
4. **处理异常** - 始终检查 status 字段
5. **数据备份** - 重要数据建议本地备份

## 常见问题

### Q: 遇到 403 错误怎么办？
A: 立即停止，该站点可能有反爬机制，不建议强行绕过。

### Q: 内容提取不完整？
A: 检查页面是否使用 JavaScript 动态渲染，可能需要其他工具辅助。

### Q: 如何导出为文件？
A: 将返回的 JSON 结果保存为 .json 或转换为 CSV/TXT 格式。
