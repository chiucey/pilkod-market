---
name: wechat-news-crawler
description: Mac本地微信公众号追踪与关键词抓取，自动生成简报发送飞书。Use when users ask to crawl WeChat public accounts, monitor news with keywords, set up scheduled Feishu reports, or track bridge/slope monitoring news.
---

# 微信公众号追踪抓取系统

Mac 本地运行的微信公众号新闻抓取系统，支持搜狗微信搜索，通过飞书机器人推送简报。

## 文件位置

```
~/wechat_crawler/
├── wechat_crawler.py   # 主抓取脚本（22:00运行）
├── send_report.py      # 简报脚本（09:00运行）
└── wechat_data/
    └── articles/       # JSON数据存储
```

## 手动运行测试

```bash
python3 ~/wechat_crawler/wechat_crawler.py
```

## 查看定时任务

```bash
crontab -l
```

## 修改追踪公众号

编辑 `TRACKED_GZH` 列表：

```bash
nano ~/wechat_crawler/wechat_crawler.py
```

找到这行，修改公众号名称（用英文逗号分隔，名称用引号）：
```python
TRACKED_GZH = ["公众号1", "公众号2", "公众号3"]
```

## 修改关键词

编辑 `SEARCH_KEYWORDS` 列表：
```python
SEARCH_KEYWORDS = ["关键词1", "关键词2", "关键词3"]
```

## 修改飞书 Webhook

编辑 `FEISHU_WEBHOOK` 变量：
```python
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook"
```

## 常见问题

**Q: 收不到推送？**
- 检查飞书机器人是否正常
- 检查网络连接
- 查看日志：`cat ~/wechat_crawler/crawl.log`

**Q: Mac休眠导致任务不执行？**
- 系统偏好设置 → 电池 → 选项 → 防止自动休眠

**Q: 想立即测试？**
```bash
python3 ~/wechat_crawler/wechat_crawler.py && python3 ~/wechat_crawler/send_report.py
```

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| tracked_gzh | 追踪的微信公众号列表 | 兴哥聊安全监测、结构守护等 |
| keywords | 关键词列表 | 桥梁结构健康监测、边坡监测等 |
| crawl_time | 抓取时间 | 22:00 |
| report_time | 简报发送时间 | 09:00 |
| feishu_webhook | 飞书机器人Webhook地址 | (需填写) |
