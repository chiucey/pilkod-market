---
name: jimeng-seedance-generator
description: 即梦5.0生图和Seedance 2.0生视频技能。当用户要求生成图片、创建图像、使用即梦生图、生成海报、创作插画、生成视频、制作动画、Seedance生视频时使用。
---

# 即梦5.0 + Seedance 2.0 AI内容生成器

本技能支持两种AI内容生成能力：
1. **即梦5.0** - 高质量图片生成
2. **Seedance 2.0** - 专业级视频生成

## 核心工具

### 图片生成 - 即梦5.0

使用 `image_synthesize` 工具生成图片：

```
工具：image_synthesize
参数：
- prompt: 详细的图片描述
- output_file: 输出路径（.png/.jpg）
- aspect_ratio: 画幅比例（1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9）
- resolution: 分辨率（1K, 2K, 4K）
```

### 视频生成 - Seedance 2.0

使用 `gen_videos` 工具生成视频：

```
工具：gen_videos
参数：
- prompt: 详细的视频描述
- output_file: 输出路径（.mp4）
- image_file: 可选，参考图片
- reference_type: first_frame（默认）或 subject
- duration: 视频时长（6秒或10秒）
- resolution: 视频分辨率（768P 或 1080P）
```

## 工作流程

### 流程1：图片生成

1. **收集需求**
   - 获取用户的图片描述
   - 确认画幅比例需求
   - 确认分辨率需求

2. **生成图片**
   - 构建详细的prompt
   - 调用 image_synthesize 工具
   - 保存输出文件

3. **结果交付**
   - 展示生成的图片
   - 提供文件路径

### 流程2：视频生成

1. **收集需求**
   - 获取用户的视频描述
   - 确认是否需要参考图片
   - 确认视频时长和分辨率

2. **生成视频**
   - 构建详细的prompt
   - 调用 gen_videos 工具
   - 保存输出文件

3. **结果交付**
   - 展示生成的视频
   - 提供文件路径

## Prompt优化技巧

### 图片Prompt结构

```
[主体描述] + [场景/环境] + [风格/艺术风格] + [光线/氛围] + [构图/视角] + [画质要求]
```

示例：
```
A majestic mountain landscape at sunset, with golden light cascading over snow-capped peaks,
in the style of National Geographic photography, dramatic clouds, wide-angle perspective,
ultra-detailed, 8K resolution
```

### 视频Prompt结构

```
[主体动作] + [场景变化] + [时间/光线] + [摄影风格] + [运动方式]
```

示例：
```
Aerial view of ocean waves crashing against rocky coastline, golden hour lighting,
cinematic drone shot, slow motion, 4K professional cinematography
```

## 常用画幅比例

| 比例 | 用途 |
|------|------|
| 1:1 | 社交媒体头像、方图 |
| 16:9 | 电影感横图、桌面壁纸 |
| 9:16 | 短视频、故事封面 |
| 4:3 | 经典照片比例 |
| 3:2 | 摄影作品标准比例 |
| 21:9 | 电影级宽银幕 |

## 参数建议

### 图片生成
- **人像/角色**: 3:4 或 4:5
- **风景/场景**: 16:9 或 2:3
- **产品图**: 1:1 或 3:4
- **海报/Banner**: 16:9 或 9:16

### 视频生成
- **短视频内容**: 9:16, 1080P, 10秒
- **社交媒体**: 1:1 或 16:9, 768P, 6秒
- **电影感视频**: 21:9, 1080P, 10秒

## 交互模板

### 图片生成确认

```
请确认您的图片需求：
- 主题：{用户描述}
- 画幅比例：{选择的比例}
- 分辨率：{选择的分辨率}

是否开始生成？
```

### 视频生成确认

```
请确认您的视频需求：
- 场景描述：{用户描述}
- 时长：{6秒/10秒}
- 分辨率：{768P/1080P}
- 参考图片：{有/无}

是否开始生成？
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| Prompt为空 | 请求用户提供详细描述 |
| 文件路径无效 | 建议使用 /workspace/outputs/ 目录 |
| 生成超时 | 重试或降低分辨率 |
| 文件保存失败 | 检查目录权限 |

## 示例对话

**用户**: 生成一张赛博朋克风格的城市夜景图

**助手**:
1. 分析需求：赛博朋克城市夜景，风格明确
2. 构建Prompt：`A futuristic cyberpunk cityscape at night, neon lights reflecting on wet streets, flying vehicles, towering skyscrapers with holographic advertisements, dramatic lighting, cinematic atmosphere, ultra-detailed, 8K`
3. 确认参数：16:9 宽屏适合城市全景，2K分辨率
4. 执行生成并交付结果

---

**技能ID**: 100116
**版本**: 1.0.0
**最后更新**: 2026-03-30
