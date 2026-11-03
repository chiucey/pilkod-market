---
name: agent-reach-tools
description: Agent Reach 工具集，访问各平台内容。当用户要求搜索网页、读取网页内容、获取 YouTube/B站视频信息、搜索 B站、读取 RSS 订阅源、搜索 GitHub、访问微信公众号文章时使用。
---

# Agent Reach 工具集

基于 `agent-reach` 命令行工具，封装已验证可用的渠道访问能力。

## 核心命令

### 全网搜索（免费，无需配置）
```bash
agent-reach search "搜索关键词"
agent-reach search "AI 最新发展"
```

### 读取任意网页
```bash
agent-reach read https://example.com
```

### YouTube 视频和字幕
```bash
agent-reach read "https://youtube.com/watch?v=VIDEO_ID"
```

### B站视频和字幕
```bash
agent-reach search-bilibili "关键词"
agent-reach read "https://bilibili.com/video/BV号"
```

### RSS/Atom 订阅源
```bash
agent-reach read "https://example.com/feed.xml"
```

### 微信公众号文章
```bash
agent-reach search-wx "文章关键词"
agent-reach read "公众号文章URL"
```

## 诊断命令
```bash
agent-reach doctor     # 查看所有渠道状态
agent-reach watch      # 快速健康检查
```

## 注意事项

1. **免费渠道**：全网搜索、网页读取、YouTube、B站、RSS、微信公众号 开箱即用
2. **需要认证的渠道**：Twitter/X、GitHub 等需要额外配置 cookies 或 API key
3. **服务器限制**：V2EX、雪球、Reddit 等可能因 IP 被限制无法访问

## 故障排除

- 搜索失败：检查网络连接，使用 `agent-reach doctor` 诊断
- 视频无法播放：尝试使用 `agent-reach read` 直接读取 URL
- B站搜索失败：自动降级到 B站 API
