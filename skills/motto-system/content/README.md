# 座右铭系统 Skill for OpenClaw

## 简介

这是一个完整的 OpenClaw Skill，提供 12 条座右铭，**当用户查询某条座右铭时，除了显示文本，还会自动执行该座右铭对应的实际任务**。

## 安装

1. 将本目录放置在 `~/.openclaw/workspace/skills/motto-system`
2. 进入目录执行 `npm install && npm run build`
3. 重启 OpenClaw Gateway：`openclaw gateway restart`
4. 或在对话中发送 `刷新 skills`

## 使用

| 你说 | 它会做什么 |
|------|------------|
| `座右铭` | 显示今日主题，并自动执行该主题的动作（如检查隐私、拆解任务等） |
| `座右铭第4条` | 显示第4条座右铭，并立即执行任务拆解动作 |
| `设置今日座右铭为第7条` | 手动设置今日主题为复盘优化，并执行复盘动作 |
| `座右铭全部` | 列出所有座右铭（不执行动作） |

## 自定义

- 修改 `index.ts` 中的 `MOTTOS` 对象可以增删座右铭。
- 修改 `KEYWORD_SCORES` 可以调整自动选择的计分规则。
- 每个动作函数都可以根据你的实际环境（如数据库、API）进行增强。

## 故障排除

如果遇到 `memory.get is not a function` 等错误，请确认 OpenClaw 版本 >= 1.0.0，并且 Skill 被正确加载。你可以在 OpenClaw 的日志中查看加载信息。

## 许可

MIT