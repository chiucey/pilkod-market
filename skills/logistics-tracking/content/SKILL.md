---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: cce09cbba565b0229a2dca044f921edb
    PropagateID: cce09cbba565b0229a2dca044f921edb
    ReservedCode1: 30450220664470612b11137799821167d118c9338f5d4eead98be9541d348158714305e70221009909b68468a84dae507b295054ab08b069f3a9fc3d1b335884e601e477f6d4de
    ReservedCode2: 304402206f5095342872e7af578d37d80071c51ac8ab4717eb6491d256ffd856f5fc516302200a2f2379ccbf44e82e731eafe42ea0ba36031d07b404d79460fe9e9827e480c1
description: 物流轨迹查询技能。当用户发送快递单号、物流单号、运单号时，自动识别快递公司并查询物流轨迹，将结果整理后发送给用户。支持顺丰、圆通、中通、韵达、申通、极兔、邮政、京东、德邦等主流快递。触发词：查物流、查快递、快递到哪了、物流查询、单号查询。
name: logistics-tracking
---

# 物流轨迹查询

## 工作流程

1. **识别单号**：从用户消息中提取快递单号（去除空格、特殊字符）
2. **自动识别快递公司**：调用 17track API 自动识别快递公司
3. **查询轨迹**：调用 API 获取完整物流信息
4. **格式化输出**：整理成清晰的物流轨迹，发送给用户

## API 配置

使用 [17track](https://user.17track.net/) 免费 API（每天100次免费额度）。

API Key 配置在 `~/.openclaw/env` 中：
```
LOGISTICS_17TRACK_APIKEY=your_api_key_here
```

或在 skill 目录创建 `apikey.txt` 文件存放 key（仅限本机使用）。

**获取 API Key**：访问 https://user.17track.net/ 注册账号，在个人中心获取 API Key（免费版每天100次）。

**后期替换**：只需告诉我新的 API Key，我帮你更新到 `apikey.txt` 文件即可，无需重建 skill。

## 查询脚本

使用 `scripts/track.py` 查询物流：

```bash
python3 /workspace/skills/logistics-tracking/scripts/track.py <单号>
```

输出格式（JSON）：
```json
{
  "code": 200,
  "carrier": "顺丰速运",
  "number": "SF1234567890",
  "status": "运输中",
  "traces": [
    {"time": "2026-04-06 10:00", "location": "上海分拨中心", "message": "快件已发出"},
    {"time": "2026-04-05 15:00", "location": "上海浦东站", "message": "快件已收入"}
  ]
}
```

## 错误处理

- `code: 404` → 单号未找到或超过查询限制
- `code: 403` → API Key 无效
- `code: 500` → 快递公司接口异常
- 网络错误 → 提示用户稍后重试

## 发送给用户的格式

使用 Feishu 消息格式（Markdown 或卡片）：

```
📦 物流查询结果

单号：SF1234567890
快递：顺丰速运
状态：运输中 🟡

━━━━━━━━━━━━━━
📍 04-06 10:00  上海分拨中心
   快件已发出，正在发往目的地
📍 04-05 15:00  上海浦东站
   快件已收入
━━━━━━━━━━━━━━
🔗 官网追踪：https://www.sf-express.com/...
```

## 支持的快递公司（自动识别）

顺丰速运 (SF) / 圆通速递 (YTO) / 中通快递 (ZTO) / 韵达速递 (YD) / 申通快递 (STO) / 极兔速递 (JTSD) / 中国邮政 (EMS) / 京东物流 (JD) / 德邦快递 (DBL) / 菜鸟裹裹 / DHL / FedEx / UPS 等

## 多单号查询

支持一次查询多个单号，用逗号或空格分隔：

```
python3 scripts/track.py SF123456 YTO987654 JD111222
```

## 备用查询（无 API Key 时）

当无 API Key 时，使用公开接口查询：
- 顺丰：https://www.sf-express.com/sf-service-owf-web/service/track/sol/queryByWaybillNos
- 17track 网页查询接口（无需 Key，每天有限制）
