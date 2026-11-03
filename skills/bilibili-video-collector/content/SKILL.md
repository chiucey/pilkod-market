---
name: bilibili-video-collector
description: 采集Bilibili指定视频的内容和互动数据。当用户要求采集Bilibili视频信息、分析视频数据、获取弹幕/评论内容、按时间段筛选数据时使用。
---

# Bilibili 视频采集器

采集Bilibili视频的完整内容数据，包括视频信息、弹幕、评论等，支持按时间段筛选。

## 触发条件

用户发送以下类型请求时触发：
- "采集Bilibili视频"
- "获取B站视频数据"
- "抓取B站弹幕/评论"
- "分析B站视频"
- "按时间段筛选弹幕"
- 提供Bilibili视频URL或BV号

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| video_url | string | 是 | Bilibili视频URL或BV号（如 BV1xx411c7mD 或 https://www.bilibili.com/video/BV1xx411c7mD） |
| start_date | string | 否 | 开始日期，格式 YYYY-MM-DD |
| end_date | string | 否 | 结束日期，格式 YYYY-MM-DD |
| collect_type | string | 否 | 采集类型：all/danmaku/comment/info，默认为 all |

## 执行流程

### 步骤1：解析视频标识

1. 提取视频BV号或完整URL
2. 调用 `mcp__matrix__extract_content_from_websites` 获取视频页面信息
3. 解析视频基础信息（标题、作者、发布时间、时长等）

### 步骤2：采集视频信息

使用 extract_content_from_websites 工具访问视频页面：
- 标题、简介
- UP主信息
- 播放量、点赞、投币、收藏数
- 视频发布时间
- 视频标签

### 步骤3：采集弹幕数据（可选）

访问弹幕API或字幕页面获取弹幕内容：
- 弹幕文本内容
- 发送时间戳
- 弹幕发送者信息（简化）

### 步骤4：采集评论数据（可选）

使用工具访问评论区获取评论内容：
- 评论文本
- 评论时间
- 评论者信息
- 回复数、点赞数

### 步骤5：按时间段筛选

如果指定了 start_date 和 end_date：
1. 将弹幕/评论时间转换为日期
2. 筛选出在指定时间范围内的数据
3. 输出筛选结果统计

### 步骤6：数据整理与输出

整理采集的数据为结构化格式：
- JSON格式完整数据
- Markdown格式摘要报告
- 保存到 extract/ 目录

## 输出格式

```json
{
  "video_info": {
    "bv_id": "BV号",
    "title": "视频标题",
    "author": "UP主名称",
    "publish_time": "发布时间",
    "duration": "时长",
    "stats": {
      "view": "播放量",
      "like": "点赞数",
      "coin": "投币数",
      "favorite": "收藏数",
      "danmaku": "弹幕数",
      "comment": "评论数"
    }
  },
  "danmaku": [
    {
      "time": "出现时间",
      "text": "弹幕内容",
      "date": "发送日期"
    }
  ],
  "comment": [
    {
      "content": "评论内容",
      "author": "评论者",
      "date": "评论日期",
      "like": "点赞数"
    }
  ],
  "time_filter": {
    "start_date": "开始日期",
    "end_date": "结束日期",
    "filtered_danmaku_count": 0,
    "filtered_comment_count": 0
  }
}
```

## 错误处理

- 视频不存在或已删除：返回错误提示
- 网络请求失败：重试最多3次
- 无弹幕/评论：返回空数组并说明
- 时间格式错误：提示正确格式

## 使用示例

**示例1：采集完整数据**
```
采集 https://www.bilibili.com/video/BV1xx411c7mD 的全部数据
```

**示例2：按时间段筛选弹幕**
```
采集 BV1xx411c7mD 2024年1月1日至3月31日的弹幕
```

**示例3：仅采集评论**
```
获取这个视频的评论数据：BV1xx411c7mD
```

## 注意事项

- 尊重平台API限制，避免短时间内大量请求
- 弹幕和评论数据受用户隐私设置影响
- 部分老视频可能缺少弹幕数据
- 建议批量采集时添加适当延迟
