# 完整阅读角数据结构与微信读书字段映射

## 目录

1. 数据原则
2. 六个模块的数据来源
3. 规范化 JSON
4. 计算与一致性规则
5. 缺失数据处理

## 1. 数据原则

- 阅读时长接口字段以秒为原始单位，写入 JSON 前转换为小时。
- 先用 `/readdata/detail` 的 `mode=overall` 发现真实有阅读记录的年份。
- 逐年数据分别请求 `mode=annually`，并传入目标年份内的 `baseTime` Unix 时间戳。不要传 `year` 字段。
- overall 总量只用于核对完整账户数据。页面范围与总量都由用户选中的年度数据计算。
- 年度代表书使用年度 `readLongest`，每年最多 8 本。
- 笔记总数使用 `reviewCount + noteCount + bookmarkCount`。
- 可展示划线来自 `/book/bookmarklist` 与 `/review/list/mine`。后者的接口说明位于微信读书 Skill 的 `notes.md`。
- 私密书籍默认排除。
- API Key 只存在于安全环境中，不进入本数据文件。

## 2. 六个模块的数据来源

| 模块 | 主要数据来源 | 输出 |
|---|---|---|
| 年度阅读展览 | 每年 `annually.readLongest`, `readStat` | 用户所选年份的年度卡片与真实书封 |
| 四组趋势 | 每年 `totalReadTime`, `readStat`, `preferCategory` | 本数、时长、分类与主题变化 |
| AI 阅读侧写 | 分类、作者、时长、笔记 | 静态侧写与阅读特征 |
| 跨书主题 | 代表性划线 | 最多五个主题 |
| 作者网络 | 作者、书籍分类 | 作者、分类和边 |
| 时间胶囊 | 代表性划线 | 最多 32 条真实划线 |

## 3. 规范化 JSON

```json
{
  "meta": {
    "title": "我的阅读角",
    "name": "读者昵称",
    "earliestRead": "2021-01-03",
    "latestRead": "2026-07-30",
    "isMock": false
  },
  "categories": [
    {
      "id": "lit",
      "name": "文学",
      "color": "#6b4c8f",
      "share": 28.5,
      "hours": 59.9,
      "count": 22
    }
  ],
  "years": [
    {
      "year": 2026,
      "color": "#6b4c8f",
      "mood": "重新回到故事里",
      "description": "基于这一年真实数据形成的简短观察。",
      "topCategory": "文学",
      "stats": {
        "hours": 35.5,
        "books": 12,
        "days": 60,
        "notes": 66,
        "partial": true
      },
      "books": [
        {
          "title": "真实书名",
          "author": "真实作者",
          "cover": "https://真实封面地址",
          "category": "文学",
          "categoryCode": "LIT",
          "pubYear": 2024,
          "hours": 8.5,
          "rating": 4,
          "summary": "基于真实书籍信息的简短说明"
        }
      ]
    }
  ],
  "profile": {
    "archetype": "跨类型阅读者",
    "label": "READING PROFILE",
    "mbti": "CURIOUS GENERALIST",
    "summary": "基于真实数据形成的静态阅读观察。",
    "traits": [
      {
        "name": "题材跨度",
        "detail": "文学与社会科学占比较高。"
      }
    ]
  },
  "themes": [
    {
      "name": "选择",
      "count": 4,
      "quote": "一条真实划线",
      "book": "真实书名"
    }
  ],
  "notes": [
    {
      "book": "真实书名",
      "bookId": "微信读书 bookId",
      "date": "2025-08-16",
      "text": "一条真实划线",
      "theme": "选择"
    }
  ],
  "network": {
    "authors": [
      {
        "id": "author-1",
        "name": "作者",
        "read": 3
      }
    ],
    "categories": [
      {
        "id": "category-lit",
        "name": "文学",
        "color": "#6b4c8f",
        "share": 28.5
      }
    ],
    "edges": [
      {
        "from": "author-1",
        "to": "category-lit",
        "weight": 3
      }
    ]
  },
  "hero": {
    "title": "你读过的，\n都印在了 memory 里。",
    "sub": "首屏数据说明"
  }
}
```

## 4. 计算与一致性规则

### 阅读时间

```text
hours = round(totalReadTime / 3600, 1)
```

### 年份发现与选择

1. 请求 `mode=overall`。
2. 从 `readTimes` 中读取有正数记录的年度桶，并结合 `yearReport` 核对。
3. 向用户展示发现的年份，让用户选择全部活跃年份、最近六个活跃年份或自定义年份。
4. 每个选中年份分别请求：

```json
{
  "api_name": "/readdata/detail",
  "mode": "annually",
  "baseTime": 1751328000,
  "skill_version": "<已安装版本>"
}
```

`baseTime` 必须落在目标年份内。上面的时间戳仅为格式示例，不能复用于其他年份。

### 年度总量

页面中的范围和总量由构建脚本根据 `years` 自动计算：

```text
meta.range = min(years[].year) + "—" + max(years[].year)
meta.yearCount = count(years[])
meta.totalHours = sum(years[].stats.hours)
meta.totalBooks = sum(years[].stats.books)
meta.totalNotes = sum(years[].stats.notes)
meta.readDays = sum(years[].stats.days)
```

输入 JSON 无需填写这些派生字段。即使存在旧值，构建脚本也会用年度数据覆盖，避免 overall 终身总量与页面选定范围混用。

### 分类比例

优先使用 `preferCategory[].readingTime`：

```text
share = readingTime / 所有可用分类 readingTime 之和 × 100
```

所有分类 `share` 合计应在 99—101 之间。

### 静态阅读侧写

- 侧写在构建前生成一次并写进 JSON。
- 最终 HTML 不包含模型 API，也不读取 API Key。
- 所有引用句必须来自 `notes`。

## 5. 缺失数据处理

- 年度没有 `readLongest`：保留年份统计，年度书架为空。
- 没有足够作者数据：减少作者节点，不补虚构作者。
- 划线少于 32 条：使用实际数量。
- 封面加载失败：使用原模板的 Halftone 文字封面。
- 年份数量没有固定限制：只展示用户最终选择的真实年份，页面中的年份数量、范围、标题、趋势和总量自动变化。
- 只有一个年份时：趋势图显示单点或单柱，不执行除以零的横轴计算。
