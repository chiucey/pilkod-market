---
name: qianlima-tender-search
description: Query the Qianlima tender platform for bid announcements, winning bids, and tender forecasts. Use this skill when users ask about tender, bidding, or government procurement searches, especially with keywords (like "software development", "IT services", "smart city"), regions (like "Chongqing", "Beijing", "National"), amounts (like "over 1M", "under 500K"), or time filters (like "last 3 days", "last 7 days"). Trigger words: /招标查询, /招标中标, /tender, /招标.
---

# 千里马招标查询 Skill

本 Skill 调用千里马招标平台 API，查询招标公告、中标结果、招标预告等信息，并生成结构化的 Markdown 报告。

## 功能特性

- 支持关键词、地区、金额、时间等多维度筛选
- 自动分类统计：招标公告、中标结果、变更信息
- 智能金额格式化（自动转换万元）
- 支持附件下载功能
- 会话缓存（5分钟有效期）

## 使用方式

### 基础查询

当用户输入类似以下内容时，执行招标查询：

```
/招标查询 软件开发 重庆
/招标查询 智慧城市 100万以上 近一个月
/招标中标 IT服务 北京 50万-200万
/招标查询 政府采购 全国 200万以下 近3天
/招标 智慧城市
```

**执行命令：**
```bash
node scripts/search.js <搜索条件>
```

例如：`node scripts/search.js 软件开发 重庆`

### 带附件下载的查询

当用户明确要求下载附件（如"下载附件"）时，添加 `--download` 参数：

```bash
node scripts/search.js 软件开发 重庆 --download
```

附件将保存到 `downloads/YYYY-MM-DD/` 目录下。

## 搜索条件语法

| 条件 | 示例 | 说明 |
|------|------|------|
| 关键词 | 软件开发 | 搜索关键词，多个用空格分隔 |
| 地区 | 北京、上海、全国、重庆 | 招标项目所在地区 |
| 金额 | 100万以上、50万以下、10-100万 | 金额区间筛选 |
| 时间 | 近3天、近7天、近一个月、近三月 | 发布时间范围 |

### 时间参数映射

| 用户输入 | API timeType |
|----------|-------------|
| 近3天 / 三天 | 1 |
| 近7天 / 七天 / 一周 | 2 |
| 近一个月 / 一个月 / 近30天 | 3 |
| 近三个月 / 三个月 | 4 |
| 近半年 / 半年 | 5 |
| 近一年 / 一年 | 6 |

### 地区参数映射

| 地区 | newAreas |
|------|----------|
| 北京 | 0 |
| 天津 | 1 |
| 河北 | 2 |
| 山西 | 3 |
| 内蒙古 | 4 |
| 辽宁 | 5 |
| 吉林 | 6 |
| 黑龙江 | 7 |
| 上海 | 8 |
| 江苏 | 9 |
| 浙江 | 10 |
| 安徽 | 11 |
| 福建 | 12 |
| 江西 | 13 |
| 山东 | 14 |
| 河南 | 15 |
| 湖北 | 16 |
| 湖南 | 17 |
| 广东 | 18 |
| 广西 | 19 |
| 海南 | 20 |
| 重庆 | 31 |
| 四川 | 21 |
| 贵州 | 22 |
| 云南 | 23 |
| 西藏 | 24 |
| 陕西 | 25 |
| 甘肃 | 26 |
| 青海 | 27 |
| 宁夏 | 28 |
| 新疆 | 29 |
| 全国 | (空) |

## 输出格式

执行后会生成 Markdown 格式的智能摘要报告，包含：

1. **统计摘要** - 招标/中标数量、平均金额、热门地区
2. **中标候选人/结果表** - 项目名称、中标单位、金额、地区、日期
3. **招标公告/预告表** - 项目名称、采购单位、金额、地区、日期
4. **变更/澄清信息表**（如有）

每条结果包含可点击的项目链接。

## 环境要求

- Node.js
- 项目根目录需有 `.env` 文件，包含：
  ```
  QIANLIMA_ACCOUNT=你的账号
  QIANLIMA_PASSWD=你的密码
  ```

## 脚本结构

```
scripts/
├── search.js      # 搜索主逻辑（含登录、认证）
├── formatter.js    # 查询解析和结果格式化
├── downloader.js  # 附件下载模块
├── auth.js        # 认证模块
├── config.js      # 会话配置
└── session.json   # 会话缓存（自动生成）
```

## 注意事项

1. 登录凭证会在首次执行时自动缓存到 `session.json`，有效期 5 分钟
2. 金额单位统一转换为"元"进行计算
3. 默认显示前 10 条结果，完整结果需访问千里马平台
4. 下载附件功能需要有效的登录会话
