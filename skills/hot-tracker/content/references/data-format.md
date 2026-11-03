# 数据格式规范 v2.0

## 目录
- [概述](#概述)
- [新增平台数据格式](#新增平台数据格式)
- [时效性相关字段](#时效性相关字段)
- [合规相关字段](#合规相关字段)
- [验证规则](#验证规则)

## 概述

本文档定义了增强版热榜数据分析脚本所需的输入数据格式。新增支持：微博、知乎、B站、快手等平台，以及时效性和合规相关字段。

## 微信公众号数据格式

### 文件示例：wx_data.json

```json
[
  {
    "title": "文章标题",
    "url": "https://mp.weixin.qq.com/s/xxx",
    "account": "公众号名称",
    "account_id": "account_001",
    "followers": 100000,
    "reads": 100000,
    "like": 5000,
    "watch": 2000,
    "share": 1000,
    "comment_count": 500,
    "is_original": true,
    "is_repost": false,
    "source_attributed": true,
    "has_ad": false,
    "ad_marked": true,
    "is_aigc": false,
    "aigc_marked": true,
    "publish_time": "2025-01-15T10:30:00Z",
    "event_id": "evt_001",
    "topic_type": "tech",
    "novelty": 0.8,
    "diversity": 0.7,
    "delta_1h": 500,
    "delta_3h": 1500,
    "delta_6h": 3000,
    "delta_24h_rank": 0.05,
    "lift_ratio": 6.5,
    "baseline_heat": 1000
  }
]
```

## 小红书数据格式

### 文件示例：xhs_data.json

```json
[
  {
    "title": "笔记标题",
    "url": "https://www.xiaohongshu.com/explore/xxx",
    "author": "用户昵称",
    "author_id": "user_001",
    "followers": 5000,
    "like": 10000,
    "save": 3000,
    "comment": 500,
    "share": 200,
    "publish_time": "2025-01-15T11:00:00Z",
    "event_id": "evt_001",
    "topic_type": "entertainment",
    "novelty": 0.75,
    "diversity": 0.65,
    "delta_1h": 1000,
    "delta_3h": 3000,
    "delta_6h": 6000,
    "delta_24h_rank": 0.03,
    "lift_ratio": 8.2
  }
]
```

## 抖音数据格式

### 文件示例：dy_data.json

```json
[
  {
    "title": "视频标题",
    "url": "https://www.douyin.com/video/xxx",
    "author": "创作者昵称",
    "author_id": "creator_001",
    "followers": 20000,
    "view": 1000000,
    "like": 50000,
    "comment": 2000,
    "fav": 5000,
    "share": 1000,
    "publish_time": "2025-01-15T12:00:00Z",
    "event_id": "evt_001",
    "topic_type": "entertainment",
    "novelty": 0.85,
    "diversity": 0.7,
    "delta_1h": 5000,
    "delta_3h": 15000,
    "delta_6h": 30000,
    "delta_24h_rank": 0.02,
    "lift_ratio": 7.5
  }
]
```

## 新增平台数据格式

### 微博数据格式

```json
[
  {
    "title": "微博内容标题",
    "url": "https://weibo.com/xxx",
    "author": "博主昵称",
    "author_id": "weibo_001",
    "followers": 50000,
    "like": 10000,
    "comment": 2000,
    "forward": 5000,
    "share": 1000,
    "read": 500000,
    "is_original": true,
    "is_repost": false,
    "source_attributed": true,
    "publish_time": "2025-01-15T11:30:00Z",
    "event_id": "evt_001",
    "topic_type": "breaking",
    "novelty": 0.9,
    "diversity": 0.8,
    "delta_1h": 2000,
    "delta_3h": 6000,
    "delta_6h": 12000,
    "rank": 5
  }
]
```

### 知乎数据格式

```json
[
  {
    "title": "知乎问题/回答标题",
    "url": "https://www.zhihu.com/question/xxx",
    "author": "用户昵称",
    "author_id": "zhihu_001",
    "followers": 10000,
    "vote": 5000,
    "comment": 1000,
    "view": 100000,
    "share": 500,
    "is_original": true,
    "publish_time": "2025-01-15T10:00:00Z",
    "event_id": "evt_001",
    "topic_type": "tech",
    "novelty": 0.7,
    "diversity": 0.75,
    "delta_1h": 500,
    "delta_3h": 1500,
    "delta_6h": 3000,
    "rank": 10
  }
]
```

### B站数据格式

```json
[
  {
    "title": "视频标题",
    "url": "https://www.bilibili.com/video/xxx",
    "author": "UP主昵称",
    "author_id": "bilibili_001",
    "followers": 50000,
    "view": 1000000,
    "like": 50000,
    "coin": 10000,
    "favorite": 20000,
    "share": 5000,
    "comment": 2000,
    "publish_time": "2025-01-15T11:00:00Z",
    "event_id": "evt_001",
    "topic_type": "entertainment",
    "novelty": 0.8,
    "diversity": 0.7,
    "delta_1h": 10000,
    "delta_3h": 30000,
    "delta_6h": 60000,
    "rank": 3
  }
]
```

### 快手数据格式

```json
[
  {
    "title": "视频标题",
    "url": "https://www.kuaishou.com/short-video/xxx",
    "author": "主播昵称",
    "author_id": "kuaishou_001",
    "followers": 100000,
    "view": 500000,
    "like": 30000,
    "comment": 1000,
    "share": 500,
    "publish_time": "2025-01-15T10:30:00Z",
    "event_id": "evt_001",
    "topic_type": "general",
    "novelty": 0.6,
    "diversity": 0.55,
    "delta_1h": 3000,
    "delta_3h": 8000,
    "delta_6h": 15000,
    "rank": 15
  }
]
```

## 时效性相关字段

### 必需字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| publish_time | string | ✓ | 发布时间（ISO 8601格式） |
| delta_1h | int | ✗ | 近1小时增量（互动数） |
| delta_3h | int | ✗ | 近3小时增量 |
| delta_6h | int | ✗ | 近6小时增量 |
| topic_type | string | ✗ | 话题类型（breaking/news/entertainment/tech/general） |
| baseline_heat | float | ✗ | 基础热度值（用于计算爆发速度） |

### 时效性评分字段说明

| 字段名 | 计算方式 | 说明 |
|--------|----------|------|
| T_realtime | max(0, 1 - hours/24) | 发布时间得分 |
| T_velocity | 基于增量计算 | 爆发速度得分 |
| T_decay | remaining_life/typical | 生命周期得分 |
| T | 加权综合 | 综合时效性评分 |

### topic_type 与生命周期

| 类型 | 典型生命周期 | 适用场景 |
|------|-------------|----------|
| breaking | 6小时 | 突发事件、重大新闻 |
| news | 12小时 | 时事新闻、政策解读 |
| entertainment | 24小时 | 娱乐八卦、明星动态 |
| tech | 48小时 | 科技新品、技术突破 |
| general | 24小时 | 一般话题 |

## 合规相关字段

### 原创与转载

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| is_original | boolean | ✓ | 是否原创 |
| is_repost | boolean | ✗ | 是否转载 |
| source_attributed | boolean | ✗ | 是否标注来源 |

### 商业合作

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| has_ad | boolean | ✗ | 是否含商业推广 |
| is_ad | boolean | ✗ | 是否为广告内容 |
| ad_marked | boolean | ✗ | 是否标注广告 |

### AIGC 相关

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| is_aigc | boolean | ✗ | 是否为AI生成内容 |
| aigc_marked | boolean | ✗ | 是否标注AIGC |

## 全平台统一必填字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | ✓ | 标题 |
| url | string | ✓ | 链接地址 |
| author | string | ✓ | 作者/账号名 |
| author_id | string | ✓ | 作者/账号ID |
| followers | int | ✓ | 粉丝数 |
| publish_time | string | ✓ | 发布时间 |

## 验证规则

### 格式验证

1. **JSON 格式**：文件必须是合法的 JSON 格式
2. **根节点类型**：支持字典（按平台分组）或数组（单平台）
3. **编码格式**：UTF-8

### 数据完整性验证

1. **必填字段**：所有标记为必填的字段必须存在且非空
2. **数值范围**：
   - 数值类型字段必须 ≥ 0
   - novelty、diversity 必须在 [0, 1] 范围内
   - delta_*h 必须 ≥ 0
3. **时间格式**：publish_time 必须符合 ISO 8601 标准

### 合规性验证

1. **原创内容**：is_original=true 时，is_repost 应为 false
2. **转载内容**：is_repost=true 时，source_attributed 应为 true
3. **商业广告**：has_ad=true 或 is_ad=true 时，ad_marked 应为 true
4. **AIGC 内容**：is_aigc=true 时，aigc_marked 应为 true
