# Channels 频道配置参考

## 支持的频道

| 频道 | 说明 | 文档 |
|------|------|------|
| `feishu` | 飞书 | 见下方 |
| `wecom` | 企业微信 | - |
| `telegram` | Telegram | - |
| `discord` | Discord | - |
| `dingtalk` | 钉钉 | - |

---

## 飞书（Feishu）配置

### 前置要求

- 飞书自建应用（App ID + App Secret）
- 已开启机器人能力
- 已配置事件订阅（长连接模式）

### 完整配置

```json5
{
  "channels": {
    "feishu": {
      "enabled": true,
      "dmPolicy": "pairing",     // pairing | allowlist | open | disabled
      "connectionMode": "websocket",
      "accounts": {
        "main": {
          "appId": "cli_xxxxxxxx",
          "appSecret": "xxxxxxxx"
        }
      }
    }
  }
}
```

### dmPolicy 说明

| 值 | 行为 |
|-----|------|
| `pairing` | 默认。未知用户发消息给配对码，需管理员审批 |
| `allowlist` | 仅 `allowFrom` 列表中的用户可用 |
| `open` | 所有人可自由对话 |
| `disabled` | 禁用私信 |

### 配对授权

```powershell
# 查看待配对请求
openclaw pairing list feishu

# 审批配对码
openclaw pairing approve feishu <CODE>

# 撤销授权
openclaw pairing revoke feishu <OPEN_ID>
```

---

## 企业微信（Wecom）配置

详见 WeCom Connect Skill。

---

## Telegram 配置

```json5
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "your-bot-token",
      "dmPolicy": "allowlist"
    }
  }
}
```

获取 Bot Token：在 Telegram 搜索 @BotFather，创建机器人获得。

---

## 群组配置示例

```json5
{
  "channels": {
    "feishu": {
      "groupPolicy": "open",       // open | allowlist | disabled
      "groups": {
        "oc_xxxxxxxx": {
          "requireMention": true   // 是否必须 @机器人
        }
      }
    }
  }
}
```
