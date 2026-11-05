---
name: douyin-account-manager
description: 抖音账号管理与数据同步技能。当用户要求采集抖音主页数据、同步飞书仪表盘、设置抖音账号监控、获取抖音账号动态、飞书机器人提醒、管理多平台账号时使用。触发短语：抖音账号管理、采集抖音数据、同步飞书、账号动态监控、抖音数据仪表盘、飞书机器人通知。
---

# 抖音账号管理

实时采集抖音账号数据，同步更新至飞书仪表盘，通过飞书机器人推送账号动态提醒。

## 核心功能

1. **抖音数据采集**
   - 采集指定抖音账号的主页数据（粉丝数、获赞数、关注数、作品列表）
   - 增量更新已采集数据的变化
   - 支持多账号批量管理

2. **飞书仪表盘同步**
   - 实时更新飞书多维表格数据
   - 生成账号数据可视化图表
   - 支持自定义数据指标配置

3. **飞书机器人通知**
   - 账号数据异常变化预警
   - 新作品发布即时通知
   - 定时数据汇总报告

## 工作流程

### 步骤1：配置账号信息

用户提供以下信息：
- 抖音账号主页URL或账号ID
- 飞书 Webhook 地址（用于机器人通知）
- 飞书多维表格 App Token 和 Table ID（用于数据同步）

### 步骤2：执行数据采集

使用抖音数据采集脚本：
```bash
python scripts/douyin_scraper.py --accounts <账号列表> --output ./data/accounts.json
```

采集内容包括：
- 账号基本信息（昵称、头像、签名）
- 粉丝/关注/获赞数据
- 最近作品列表及互动数据

### 步骤3：同步飞书仪表盘

数据采集完成后，同步至飞书：
```bash
python scripts/feishu_sync.py --data ./data/accounts.json --app_token <飞书AppToken>
```

### 步骤4：发送机器人通知

数据写入完成后，推送通知：
```bash
python scripts/feishu_bot.py --webhook <飞书Webhook> --message "抖音账号数据更新完成"
```

## 配置示例

```yaml
# config/accounts.yaml
accounts:
  - douyin_id: "1234567890"
    name: "官方账号"
    monitor_enabled: true
    alert_threshold:
      follower_change: 100  # 粉丝变化超过100时告警
      new_videos: 1          # 新视频数量

feishu:
  webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
  app_token: "xxx"
  table_id: "tblxxx"
```

## 输出产物

- `data/accounts.json` - 采集的账号原始数据
- `data/dashboard_sync.json` - 飞书同步记录
- `data/notifications.json` - 通知发送记录
