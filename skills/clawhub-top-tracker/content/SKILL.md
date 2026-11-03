---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d9f157e00e4764662b65df44b00dc945
    PropagateID: d9f157e00e4764662b65df44b00dc945
    ReservedCode1: 304402206813cdf077902b2da1d0fd107ec408c60fe1b01ea3703daa0fc6f1965a2d8ac702207afa6016348ade63a7fbf1dc34f2080751e822c75e3aa610e2042ca7b79b4d1d
    ReservedCode2: 30450220361580bfac21645a5cd0e8b4b97efa807cae3be0d11c8c0273ebbef9b92a444b022100843254a5622326e22260d59988c6997333939f2695b53397f45a0124313c9cd3
description: 监控 ClawHub 榜单动态，挖掘有潜力的 Skill。当需要查询 ClawHub 下载榜排名、分析 Skill 排名变化、发现新上榜或排名跃升的 Skill、以及生成榜单对比报告时使用此 Skill。支持按下载量、发布时间、星级等多维度排序，可自动抓取 Top100 并输出结构化数据。
name: clawhub-top-tracker
---

# ClawHub Top Tracker

监控 ClawHub 榜单动态，挖掘有潜力的 Skill。

## 数据获取

调用 ClawHub 的公开 Convex API 获取榜单数据：

```bash
python3 /workspace/skills/clawhub-top-tracker/scripts/fetch_top_skills.py --num 100 --sort downloads
```

**参数说明：**
- `--num`: 获取数量，默认 25，最大 100
- `--sort`: 排序方式，支持 `downloads`（下载量）、`stars`（星级）、`latest`（最新）
- `--output`: 输出文件路径（JSON格式），默认 `clawhub_top.json`

**输出格式：** JSON 数组，每条记录包含：
```json
{
  "name": "skill-name",
  "author": "author-id",
  "downloads": 12345,
  "stars": 999,
  "description": "简短描述",
  "tags": ["tag1", "tag2"],
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

## 分析任务

当用户要求分析榜单时，执行以下步骤：

1. **获取数据** — 运行 fetch 脚本，拉取最新 Top100
2. **读取结果** — 解析输出的 JSON 文件
3. **多维度分析：**
   - 🏆 **Top20 概览** — 排名、下载量、星级
   - 📈 **排名跃升** — 与历史数据对比，找出排名上升的 Skill
   - 🆕 **新上榜** — 之前不在榜内、最近冒起的 Skill
   - 🏃 **增速黑马** — 下载量增长快、排名跃升明显的
   - 📊 **分类分布** — 哪些类别的 Skill 最受欢迎
4. **生成报告** — 用自然语言输出结构化分析结果

## 增量追踪

若需要对比历史变化：

1. 读取上次的榜单数据（保存在 `--output` 指定路径）
2. 对比新旧两份数据，计算排名差值
3. 标注：新上榜（之前无记录）、排名上升、排名下降、排名不变

## 注意事项

- ClawHub API 使用 `nextCursor` 分页，每页最多 25 条
- `nonSuspiciousOnly=true` 可过滤可疑 Skill（建议始终加上）
- API 响应为 JSON，直接解析使用，无需登录授权
- 两次抓取建议间隔至少 5 分钟，避免频率限制