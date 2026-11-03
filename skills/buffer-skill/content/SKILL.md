---
name: buffer-skill
description: Buffer 社交媒体排程平台 MCP API 技能（多账号加密版）。支持多账号、加密存储、自动注册 MCP Server，适用于 Twitter/Facebook/Instagram/YouTube/Threads/Bluesky。
---

# Buffer Skill - 多账号版

## 核心概念

- **Vault（保险库）**：加密存储所有账号 API Key，支持无限账号
- **账号名**：用户自定义，如 `buffer1`、`my_ads`、`zhangsan`
- **自动 MCP 注册**：添加账号时自动在 `/root/.mcporter/mcporter.json` 注册对应 MCP Server
- **Channel ID**：每个平台账号下的具体渠道 ID，需从 Buffer 后台获取

## 环境变量

```bash
export BUFFER_VAULT_KEY='babyluck-encrypt-2026'   # 解密密钥，只需设置一次
```

## 快速开始

```bash
# 添加账号（自动注册 MCP Server）
export BUFFER_VAULT_KEY='babyluck-encrypt-2026'
python3 vault.py add buffer1 'PJAEvErdDANBjKFerDhF81fQPa1-GcK3lneeP1-uJnq'
python3 vault.py add buffer2 'zzgGObNbHJzv_E4AFa3wAnLzHM3fBaXxmM3Cedi5vLV'

# 列出所有账号
python3 vault.py list

# 查看账号下的渠道
python3 vault.py channels buffer1
```

## 账号管理

| 命令 | 说明 |
|------|------|
| `vault.py add <名> <Key>` | 添加账号 + 自动注册 MCP |
| `vault.py list` | 列出所有账号 |
| `vault.py get <名>` | 获取 API Key |
| `vault.py remove <名>` | 删除账号 + 注销 MCP |
| `vault.py channels <名>` | 查看账号下的所有渠道 |
| `vault.py servers` | 列出已注册的 MCP Server |

## 发布命令

```bash
buffer.sh post <账号名> <channel_id> <text> [due_at] [img_url]
```

**示例：**
```bash
# Buffer 1 - Twitter
buffer.sh post buffer1 69fed1bc5c4c051afa282701 "文案内容" "2026-05-20T15:30:00.000Z" "https://cdn.example.com/img.jpg"

# Buffer 2 - YouTube
buffer.sh post buffer2 6a0a7b6d090476fb992fc107 "文案内容" "2026-05-20T15:30:00.000Z" "https://cdn.example.com/img.jpg"
```

## 已配置账号

| 账号 | MCP Server | API Key 长度 | 渠道 |
|------|-----------|-------------|------|
| buffer1 | buf_buffer1 | 43 chars | Twitter / Facebook / Instagram |
| buffer2 | buf_buffer2 | 43 chars | YouTube / Threads / Bluesky |

## 技术说明

- **加密算法**：PBKDF2 + Fernet（对称加密，密钥为环境变量 `BUFFER_VAULT_KEY`）
- **Key 存储**：`/workspace/skills/buffer-skill/scripts/.vault`（加密，需密钥读取）
- **MCP 配置**：`/root/.mcporter/mcporter.json`
- **调用方式**：通过 `mcporter` 调用对应账号的 MCP Server，Header 携带 API Key

## 扩展新账号

```bash
export BUFFER_VAULT_KEY='babyluck-encrypt-2026'

# 添加新账号
python3 vault.py add buffer3 '新APIKey'

# 查看新账号渠道
python3 vault.py channels buffer3

# 直接使用
buffer.sh post buffer3 <新channel_id> "文案"
```

> 注意：添加账号后会通过 Buffer API 自动探测可用渠道并显示。如某渠道未被探测到（账号在 Buffer 后台已连接但 API 未返回），可手动记录 channel ID 并告知 AI 需要发布到该平台。