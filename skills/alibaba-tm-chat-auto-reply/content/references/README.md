---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 78fadf7e9110df242817da429cfc514d
    PropagateID: 78fadf7e9110df242817da429cfc514d
    ReservedCode1: 304502206298cef531cbe021500145b47fa34902e1689cf8f016631b2fe3128a45af2d93022100a526321fdfb6f14153cdd5d4eb708b6e37e914a5b13763d1e0d3688e254c456b
    ReservedCode2: 3046022100c22c15b56848eca9dcc7dd82dd6bdb31961548da657454e4f1b468cfe328e5250221009ca74cb946c8718fffd223db330e47b3ef7aa94ea111968b0042a21b799a240e
---

# 阿里国际站TM聊天自动回复系统

## 概述

本系统为阿里巴巴国际站TradeManager(TM)提供智能自动回复功能，帮助外贸卖家实现7x24小时客户服务。

## 功能特性

- **消息监控**: 实时监控TM聊天窗口，自动读取新消息
- **智能意图识别**: 基于关键词匹配识别买家意图（询价/样品/MOQ等）
- **模板回复**: 内置常用回复模板，支持自定义配置
- **AI增强**: 可选AI接口进行回复优化
- **审核模式**: 支持人工审核后再发送，确保回复质量
- **多语言支持**: 支持中/英/西/法/德等多种语言

## 系统要求

- Windows 7/8/10/11
- Python 3.8+
- TradeManager 已安装并登录

## 快速开始

### 1. 安装依赖

```bash
cd alibaba-tm-chat-auto-reply
python scripts/setup.py
```

### 2. 配置系统

编辑 `config/config.json` 配置文件:

```json
{
  "tm_path": "C:\\Program Files\\TradeManager",
  "monitor_interval": 5,
  "auto_reply": true,
  "review_mode": true,
  "language": "en"
}
```

### 3. 启动系统

- **监控模式**（仅监控，不回复）:
  ```bash
  python scripts/tm_monitor.py --mode monitor
  ```
  或双击 `start_monitor.bat`

- **自动回复模式**:
  ```bash
  python scripts/tm_monitor.py --mode auto
  ```
  或双击 `start_auto_reply.bat`

## 回复模板

系统会根据买家消息的关键词自动匹配回复模板:

| 关键词 | 触发回复 |
|--------|----------|
| price, 价格 | 报价相关回复 |
| moq, 最小起订量 | MOQ说明 |
| sample, 样品 | 样品政策 |
| shipping, 物流 | 发货信息 |
| catalog, 目录 | 产品目录 |
| payment, 付款 | 支付条款 |

## 高级配置

### 启用AI增强

1. 获取AI API密钥
2. 修改配置:
```json
{
  "ai_enhance": {
    "enabled": true,
    "api_key": "your-api-key",
    "model": "minimax"
  }
}
```

### 自定义关键词和模板

编辑 `config/config.json`:

```json
{
  "keywords": {
    "your_intent": ["keyword1", "keyword2"]
  },
  "reply_templates": {
    "your_intent": "Your custom reply template {variable}"
  }
}
```

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        主控制器                              │
│                    TMAutoReply                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ TMChatMonitor │  │ TMReplyEngine │  │ 消息队列      │
│   消息监控     │  │   回复生成     │  │              │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │
        ▼                  ▼
┌───────────────┐  ┌───────────────┐
│ SQLite数据库  │  │ 关键词匹配     │
│ 聊天记录读取   │  │ AI增强        │
└───────────────┘  └───────────────┘
```

## 注意事项

1. **账号安全**: 避免过于频繁的自动回复，可能触发平台风控
2. **业务差异**: B2B场景复杂，AI回复建议开启审核模式
3. **数据隐私**: 所有聊天数据仅在本地处理，不会上传到云端

## 故障排除

### 问题: 提示"未检测到TM安装"
**解决**: 检查 `config.json` 中的 `tm_path` 配置，确保路径正确

### 问题: 无法读取聊天记录
**解决**: 确保TM已登录，且有聊天记录存在

### 问题: 回复未发送
**解决**:
- 检查审核模式是否开启
- 检查窗口焦点是否正确

## 更新日志

### v1.0.0 (2026-03-27)
- 初始版本发布
- 支持消息监控
- 支持关键词回复
- 支持审核模式
