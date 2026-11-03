---
name: weibo-daily-scrape
description: 咪咕微博每日内容抓取系统。自动抓取22个咪咕微博账号（熊猫3+综合4+体育15）的当日内容，生成Excel报表，并可推送至微信/飞书。触发场景：用户说"抓取微博"、"微博日报"、"微博内容报告"、"推送微博"、"更新微博Cookie"时激活。也适用于：定期监控咪咕账号内容动态、生成每日内容简报。
---

# 微博每日抓取 Skill

## 快速开始

### 依赖安装
```bash
cd ~/.openclaw/skills/weibo-daily-scrape
npm install
```

### 演示模式（无需Cookie，直接可运行）
```bash
node scripts/run_daily.js
```
输出：样本数据 + Excel文件（可看格式）

### 真实模式（需要微博SUB Cookie）
1. 浏览器登录 weibo.com → F12 → Application → Cookies → 复制 `SUB` 字段值
2. 编辑 `scripts/weibo_cookies.json`，替换 `cookie` 字段，把 `enabled` 改为 `true`
3. 运行：
```bash
node scripts/run_daily.js
```

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `scripts/scrape_weibo.js` | 微博抓取主程序（Node.js） |
| `scripts/excel_generator.js` | Excel生成器（依赖xlsx） |
| `scripts/run_daily.py` | 每日调度器（自动判断模式） |
| `scripts/weibo_cookies.json` | Cookie配置 |
| `references/accounts.md` | 22个账号完整列表 |

---

## 账号列表（22个）

| 类别 | 账号 |
|------|------|
| 熊猫（3） | 开饭了大熊猫、熊猫观察君、咪咕Panda |
| 综合（4） | 咪咕、咪咕音乐、咪咕娱乐、咪咕视频 |
| 体育（15） | 咪咕奥运、咪咕冰雪、咪咕格斗、咪咕篮球、咪咕乒乓球、咪咕斯诺克、咪咕体育、跟我一起看足球、咪咕足球、体育叨叨酱、我们都是足球迷、野生乒乓、CBA最前沿、篮球记事本、UFC终极格斗冠军赛 |

完整UID列表见 `references/accounts.md`

---

## 抓取逻辑

- **真实模式**：按时间窗口（今天08:40→明天08:40）抓取各账号内容，去重只保留每账号第一条
- **演示模式**：输出账号列表和预期格式，不调API
- **Cookie检查**：Cookie过期自动降级到演示模式（见日志判断）

---

## Excel输出字段

| 字段 | 说明 |
|------|------|
| 账号名称 | 微博账号名 |
| 粉丝数 | 抓取时的粉丝数 |
| 微博内容 | 原始文本 |
| 话题 | 提取的#话题# |
| @提及 | 提取的@用户 |
| 视频链接 | https://weibo.com/tv/show/1034:{media_id} 格式 |
| 发布时间 | 格式：YYYY-MM-DD HH:mm |
| 原始URL | 微博详情页链接 |

---

## 定时自动运行

设置cron作业，每天自动抓取并推送：
```
/openclaw cron add \
  --name "咪咕微博每日内容抓取" \
  --schedule "cron:0 40 8 * * *" \
  --sessionTarget isolated \
  --payload '{"kind":"agentTurn","message":"运行 ~/.openclaw/skills/weibo-daily-scrape/scripts/run_daily.py 生成当日微博内容报表"}'
```

---

## Cookie刷新

微博SUB Cookie有效期约1-2周。当日志出现"演示模式"或抓取条数为0时，说明Cookie已过期，需要重新获取。

获取方式：浏览器登录 weibo.com → F12 → Application → Cookies → 复制新的 `SUB` 值 → 更新 `weibo_cookies.json`

---

## 推送到微信/飞书

当前skill运行后将CDN链接以消息形式发送给用户（通过当前对话channel）。如需推送到其他平台，在 run_daily.py 中添加对应平台的API调用。
