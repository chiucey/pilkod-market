---
name: finance-video-editor
description: 全自动财经视频剪辑工作流。当用户要求制作财经视频、自动剪辑视频、智能生成B-roll素材、财经视频包装、视频素材合成、或需要将长视频自动转换为精美的财经短视频时使用。
---

# Finance Video Editor

全自动财经视频剪辑工作流技能 - 将原始视频自动转换为专业财经风格短视频。

## 核心功能

| 阶段 | 功能 | 描述 |
|------|------|------|
| **阶段 1** | 多模态理解 | 利用 MiniMax 视觉模型解析原片台词与动作 |
| **阶段 2** | 智能策划 | 根据台词自动生成 B-roll 视觉 Prompt |
| **阶段 3** | 并行素材生成 | 调用 Hailuo 视频生成模型批量创建 AI 素材 |
| **阶段 4** | 云端合成 | 缝合、字幕、专业财经滤镜一站式导出 |

## 工作流程

```mermaid
graph LR
    A[原片视频] --> B[多模态理解]
    B --> C[智能策划]
    C --> D[并行素材生成]
    D --> E[云端合成]
    E --> F[成品视频]

    B -->|转录文本| C
    C -->|B-roll 脚本| D
    D -->|AI 素材| E
```

## 使用场景

1. **财经新闻剪辑** - 将长篇财经报道自动剪辑为短视频
2. **市场分析视频** - 自动插入数据图表、市场走势等素材
3. **投资教育内容** - 为教学视频自动添加案例画面
4. **企业宣传片** - 快速生成带有专业财经风格的宣传素材

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `video_path` | string | ✅ | - | 原始视频文件路径 |
| `video_duration` | int | ❌ | 5 | 每个 B-roll 片段时长(秒) |
| `video_resolution` | string | ❌ | "4k" | 输出分辨率 |
| `max_parallel` | int | ❌ | 3 | 并行生成数量 |
| `enable_subtitle` | bool | ❌ | true | 是否生成字幕 |
| `enable_filter` | bool | ❌ | true | 是否应用财经滤镜 |

## 输出结果

```json
{
    "status": "Success",
    "video_url": "https://...",
    "hot_topics_used": "已同步最新大中华区财经热点",
    "segments_count": 5,
    "processing_time": 125.3
}
```

## 调用示例

### Python SDK

```python
import max_claw_sdk as sdk

result = sdk.finance_video_editor.run(
    video_path="/path/to/raw_video.mp4",
    config={
        "video_duration": 6,
        "video_resolution": "4k",
        "max_parallel": 5
    }
)

print(result["video_url"])
```

### Agent 调用

```python
from agent.skills import finance_video_editor

# 同步执行
result = finance_video_editor.main("/path/to/video.mp4")

# 异步执行
result = await finance_video_editor.main_async("/path/to/video.mp4")
```

## 技术特点

1. **并行处理** - 支持多线程/异步并发生成，大幅提升效率
2. **智能重试** - 自动重试失败任务，保证稳定性
3. **进度追踪** - 支持回调函数，实时显示处理进度
4. **配置灵活** - 支持自定义各项参数

## 依赖项

- `max_claw_sdk` - MiniMax 核心 SDK
- `asyncio` - 异步支持
- `concurrent.futures` - 并行处理

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| API 调用失败 | 自动重试 3 次，指数退避 |
| 视频解析失败 | 返回详细错误信息 |
| 素材生成超时 | 记录失败片段，继续处理其他片段 |
| 合成失败 | 返回部分成果 + 错误详情 |

## 最佳实践

1. **输入视频建议** - 1080P 以上分辨率，时长 1-30 分钟
2. **并行数量** - 根据 API 配额调整，建议 3-5
3. **片段时长** - 财经数据类 3-5 秒，叙事类 5-8 秒
4. **质量优先** - 使用 4K 分辨率获得最佳效果