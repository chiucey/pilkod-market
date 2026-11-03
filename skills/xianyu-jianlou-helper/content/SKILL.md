---
name: xianyu-jianlou-helper
description: 咸鱼代售每日捡漏助手 v3.0。Use when users ask to find second-hand bargains, monitor Xianyu/Flea market prices, search for cheap used electronics (iPhone, PS5, Switch, Mac mini, graphics cards, etc.), run daily price monitoring reports, or ask about resale profit opportunities. 当用户提到以下内容时激活：执行捡漏任务、今日低价货源、帮我找低价货、捡漏XX、咸鱼代售、闲鱼好价、闲鱼抄底、帮我找XX二手捡漏、便宜XX二手等。
---

# 咸鱼代售每日捡漏助手 v3.0

## 技能概述

监控闲鱼、淘宝、京东、拼多多等8大平台的二手商品价格，每日生成捡漏日报，帮助用户发现低于市场价的优质货源。

## 工作流程

### Phase 1: 读取配置

读取 `config.json` 获取：
- 30大品类、155个子项的关键词和价格阈值
- 8大平台搜索配置
- 代售利润计算公式
- 风险提示规则

### Phase 2: 生成报告框架

执行核心脚本生成 Markdown 报告：

```bash
python scripts/search_today.py
```

脚本会：
1. 读取 `config.json` 中的品类、关键词、平台配置
2. 生成包含全品类搜索直链的报告框架
3. 输出到 `output/report_YYYY-MM-DD.md`

### Phase 3: AI 实时网络搜索填充数据

由于平台反爬限制，无法直接获取实时价格。使用 `batch_web_search` 工具搜索各品类的最新二手价格：

**搜索优先级：**
- **第一梯队（必搜）**：RTX 4060、iPhone 15PM、PS5 Slim、Switch 2、Mac mini M4、AirPods Pro 2 等15项热门商品
- **第二梯队（推荐搜）**：各品类 top 1~2 热门子项
- **第三梯队（按需搜）**：用户指定品类时扩展

**数据源优先级：**
1. nickys.cn（显卡/硬件价格数据站）
2. 什么值得买、知乎数码
3. IT之家、搜狐科技、PConline
4. 同一商品至少2个来源交叉验证

**价格标注要求：**
- 数据来源（站点名 + 日期）
- 与 config.json 阈值的对比

### Phase 4: 标记推荐等级

对比搜索价格与阈值：

| 等级 | 条件 | 标记 |
|------|------|------|
| 🔥 强烈推荐 | 低于 `hot_price`（警戒线） | 红色火焰 |
| ✅ 推荐关注 | 低于 `max_price`（建议入手价） | 绿色勾 |
| 🟡 观望 | 高于 `max_price` 但合理 | 黄色 |
| ❌ 不建议 | 远超 `max_price` | 红色叉 |

### Phase 5: 更新历史记录

1. 将价格数据写入 `output/price_history.json`
2. 检查品类迭代：
   - 新品类/商品成为热点 → 更新 config.json
   - 连续7天无数据 → 降优先级或移除
   - 连续5天价格均高于阈值 → 调整阈值

---

## 价格阈值速查（部分代表商品）

| 品类 | 建议入手价 | 捡漏警戒线 |
|------|-----------|-----------|
| iPhone 15 Pro Max (256G) | ≤¥5,200 | ≤¥4,600 |
| 华为 Mate 60 Pro | ≤¥3,500 | ≤¥3,000 |
| iPad Air 5 M1 | ≤¥2,300 | ≤¥2,000 |
| Switch 2 | ≤¥1,800 | ≤¥1,600 |
| PS5 Slim 光驱版 | ≤¥3,200 | ≤¥2,900 |
| RTX 4060显卡 | ≤¥2,100 | ≤¥1,700 |
| Mac mini M4 | ≤¥3,500 | ≤¥3,000 |
| 索尼 A7M4 | ≤¥11,000 | ≤¥9,500 |
| AirPods Pro 2 | ≤¥1,100 | ≤¥900 |
| 戴森V15 | ≤¥2,000 | ≤¥1,600 |
| 泡泡玛特MEGA | ≤¥3,000 | ≤¥2,000 |

完整155项阈值见 `config.json`。

---

## 全平台搜索覆盖

| 平台 | 类型 | 搜索直链格式 |
|------|------|------------|
| 闲鱼 | 二手 | `https://www.goofish.com/search?q=关键词&sortField=1` |
| 淘宝 | 电商 | `https://s.taobao.com/search?q=关键词` |
| 天猫 | 电商 | `https://list.tmall.com/search_product?q=关键词` |
| 京东 | 电商 | `https://search.jd.com/Search?keyword=关键词` |
| 拼多多 | 电商 | `https://pinduoduo.com/search?q=关键词` |
| 1688 | 批发 | `https://s.1688.com/so/search?q=关键词` |
| 小红书 | 社区 | `https://www.xiaohongshu.com/search_result?keyword=关键词` |
| 抖音 | 短视频 | `https://www.douyin.com/search/关键词` |

**注意**：链接必须使用搜索直链，禁止伪造具体商品链接。

---

## 输出格式

生成结构化捡漏日报：

```markdown
# 📦 咸鱼代售捡漏日报 — YYYY-MM-DD

## 🔥 强烈推荐（低于捡漏警戒线）
| 品类 | 今日参考价 | 警戒线 | 数据来源 | 各平台搜索直链 |

## ✅ 推荐关注（低于建议入手价）
| 品类 | 今日参考价 | 建议入手价 | 数据来源 | 各平台搜索直链 |

## 📊 全品类价格阈值速查（155项）
| 品类 | 建议入手价 | 捡漏警戒线 | 备注 |

## 🔍 全品类搜索直链（8平台）

## 🎯 情绪词搜索组合

## 📊 代售利润速查

## 🔄 品类迭代报告

## 💡 操作建议

## ⚠️ 风险提示
```

---

## 风险提示

- **数据来源声明**：各平台有反爬/登录限制，价格数据来自公开网络汇总，仅作参考
- **假货高风险品类**：AirPods、iPhone、始祖鸟、投影仪、潮玩手办 — 必须查验真伪
- **矿卡风险**：显卡必须查BIOS版本和GPU使用时长
- **异常价格**：低于警戒线50%的商品，需提醒用户甄别风险

---

## 定时任务配置

支持每天早上9:00自动运行：

```toml
name = "每日捡漏日报 v3.0"
rrule = "FREQ=DAILY;BYHOUR=9;BYMINUTE=0"
status = "ACTIVE"
```
