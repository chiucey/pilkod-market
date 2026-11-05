---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c721174a2c891d4581805f3709a9f29f
    PropagateID: c721174a2c891d4581805f3709a9f29f
    ReservedCode1: 3045022100b11b33499a1220aeb4a88d95ad2ca01a343d70119cb33d659e59da047838074002201dc856eb5ccea1e9d297fdcdd22dc8ba1457e5cbfcd16bfb192c1b9fc992abdc
    ReservedCode2: 3046022100ecd0daa0ef790a18ce764d140e334490f6bda9ae62bb31ea041a49e5e7098107022100d7eb927e7b016be6db61650707393301be95ec6467c6f5df6dde0be213728ab5
---

# 保险知识技能使用指南

## 快速开始

### 方式一：命令行使用

```bash
# 安装依赖
pip install requests beautifulsoup4 pyyaml

# 采集公众号文章
python scripts/collect_content.py \
  --accounts "深蓝保" "奶爸保" \
  --limit 5 \
  --interval 30 \
  --output output/wechat_articles.md

# 采集后推送到飞书
python scripts/feishu_pusher.py \
  --webhook "https://open.feishu.cn/open-apis/bot/v2/hook/xxx" \
  --summary \
  --articles-json output/articles.json
```

### 方式二：使用配置文件

```bash
# 编辑配置文件
vim references/config.yaml

# 使用配置文件执行
python scripts/collect_content.py --config references/config.yaml
```

## 常见使用场景

### 场景 1：采集特定公众号

```
用户：帮我采集深蓝保和奶爸保的最新保险文章
```

系统执行：
```bash
python scripts/collect_content.py \
  --accounts "深蓝保" "奶爸保" \
  --keywords "重疾险" "增额终身寿" "年金险"
```

### 场景 2：定时每日推送

使用 cron 设置每日 9 点推送：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务
0 9 * * * cd /path/to/insurance-knowledge && python scripts/collect_content.py --config references/config.yaml && python scripts/feishu_pusher.py --webhook "YOUR_WEBHOOK" --summary
```

### 场景 3：关键词精准过滤

```bash
# 只采集增额终身寿相关内容
python scripts/collect_content.py \
  --accounts "深蓝保" \
  --keywords "增额终身寿" \
  --output output/annuity.md
```

## RSSHub 使用说明

本技能使用 [RSSHub](https://github.com/DIYgod/RSSHub) 公开服务获取微信公众号内容。

### 可用的 RSSHub 实例

- 主站：`https://rsshub.app`
- 备用1：`https://rsshub.rssforever.com`
- 备用2：`https://rsshub.nodepit.cn`

### 手动添加公众号

如果自动抓取失败，可以通过 RSSHub 手动获取：

1. 访问 `https://rsshub.app/wechat/mp/公众号名称`
2. 获取 RSS 源
3. 解析获取文章列表

## 飞书 Webhook 配置

### 步骤 1：创建飞书群机器人

1. 打开飞书群设置
2. 进入"群机器人"功能
3. 添加"自定义机器人"
4. 复制 Webhook 地址

### 步骤 2：配置推送

```bash
python scripts/feishu_pusher.py \
  --webhook "https://open.feishu.cn/open-apis/bot/v2/hook/xxx-xxx-xxx" \
  --summary \
  --articles-json output/articles.json
```

## 保险险种关键词参考

| 险种类别 | 关键词 |
|---------|--------|
| 健康险 | 重疾险, 医疗险, 防癌险 |
| 寿险 | 寿险, 定期寿险, 终身寿险 |
| 年金险 | 年金险, 养老险, 教育金 |
| 储蓄险 | 增额终身寿, 分红险, 万能险 |
| 意外险 | 意外险, 综合意外, 交通意外 |
| 财产险 | 家财险, 车险 |

## 注意事项

1. **频率控制**：建议每次采集间隔 30 秒以上，每日不超过 10 次
2. **高峰时段**：避免在工作日 9-12 点、18-21 点进行大批量采集
3. **内容存储**：仅保存提炼后的观点，不存储原文
4. **合规使用**：仅供个人学习，不用于商业目的
