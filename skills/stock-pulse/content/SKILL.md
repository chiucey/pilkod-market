---
name: stock-pulse
description: A股10日涨幅榜 v7 量化扫描技能（v6量价+四力 + 龙头地位三维评分）。当需要查询、分析A股10日涨幅排行榜、筛选强势股票、识别龙头地位、生成操盘建议时激活。触发词：10日涨幅、强势股、龙虎榜、龙头地位、个股诊断、游资模式。
---

# Stock Pulse · 10日涨幅榜量化扫描

## 核心工作流

### 每日监控（定时自动）

定时任务已配置：`*/30 9-15 * * 1-5`（工作日09:00-15:00每30分钟）

```bash
python3 /workspace/skills/stock-pulse/scripts/scan.py
```

输出：TOP15排名 + 买入/观望/风险信号 + 归档JSON

---

## 数据获取

使用 iwencai 直接 API：

```python
import urllib.request, json, urllib.parse

API_KEY = "你的密钥"
API_HOST = "https://openapi.iwencai.com"
params = urllib.parse.urlencode({
    "query": "A股10日涨幅排行榜前30名 股票代码 股票名称 涨跌幅 换手率",
    "page": 1, "per_page": 30, "source": "ths", "cache": 0, "expand_index": "true"
})
url = f"{API_HOST}/v1/query2data?{params}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
with urllib.request.urlopen(req, timeout=15) as resp:
    raw = json.loads(resp.read())
```

**日期校验**：用上证指数确认数据时效
- 查询上证指数最新价，若不等于已知收盘价（2026-04-10=3986.22）则数据已更新

---

## v6 评分模型

字段解析（iwencai返回带日期范围的key）：

```python
chg10_key  = [k for k in s if "涨跌幅" in k and "20260" in k]   # 10日涨幅
turn10_key = [k for k in s if "换手率"   in k and "20260" in k]  # 10日换手
t          = s.get("最新涨跌幅", 0)                               # 今日涨跌幅
code       = s.get("股票代码", "")
name       = s.get("股票简称", "")
```

完整评分逻辑见 `references/v6-model.md`

---

## 操盘信号阈值

| 评分 | 信号 | 操作 |
|------|------|------|
| ≥ 7.5 | 强势8+ | ✅买入 |
| 6.5~7.5 | 偏强7+ | ✅买入（6.5分以上） |
| 5.5~6.5 | 中性5+ | ⚠️观望 |
| 4.0~5.5 | 偏弱4+ | ❌减仓 |
| < 4.0 | 极弱 | 🔴离场 |

**风险标志**：
- 10日涨幅 > 80% + 换手 > 150% → 🔴高位派发
- 10日涨幅 > 80% → ⚠️高位警戒
- 10日换手 > 200% → ⚠️超活跃换手

---

## 买入信号质量分类

| 类型 | 条件 | 优先级 |
|------|------|--------|
| 🥇 金买点 | 低换手(<50%) + 涨停 | 最强 |
| 🥈 银买点 | 中等换手 + 涨停/大涨 | 标准 |
| ⚠️ 谨慎 | 换手>150% 或 10日涨幅>100% | 降低仓位 |

---

## 输出格式

运行后输出：
1. TOP15 完整排名表（Markdown代码块）
2. 买入信号列表（6.5分以上）
3. 风险/离场警示列表
4. JSON 归档至 `daily/YYYY-MM-DD.json`

---

## 快速命令

```bash
# 手动执行一次扫描
python3 /workspace/skills/stock-pulse/scripts/scan.py

# 查看今日数据
cat /workspace/周期女王战法/daily/$(date +%Y-%m-%d).json

# 查看最近3天数据
ls -t /workspace/周期女王战法/daily/ | head -3
```

---

## 数据文件位置

| 类型 | 路径 |
|------|------|
| 每日归档JSON | `/workspace/周期女王战法/daily/YYYY-MM-DD.json` |
| v6模型详情 | `/workspace/skills/stock-pulse/references/v6-model.md` |
| 账户信息 | `/workspace/skills/stock-pulse/references/account-info.md`（可选） |
