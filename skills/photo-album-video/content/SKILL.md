---
name: photo-album-video
description: 将多张图片或照片连接成带过渡动画和背景音乐的相册视频。支持多种过渡效果选择，自动生成精美的视频相册。当用户要求制作相册视频、图片转视频、图片拼接、照片视频、音乐相册时使用。
---

# Photo Album Video Generator

## 技能说明

这是一个强大的相册视频生成技能，可以将用户提供的多张图片或照片连接成一段完整的视频，图片之间配有精美的过渡动画效果，并支持添加背景音乐。

## 核心功能

### 1. 图片处理
- 支持多种图片格式：JPG, JPEG, PNG, BMP, WEBP
- 自动处理不同尺寸的图片，统一调整为视频分辨率
- 保持图片比例，使用背景色填充或模糊背景

### 2. 过渡动画效果

提供以下几种过渡样式供用户选择：

| 样式 | 效果描述 |
|------|----------|
| `fade` | 淡入淡出效果，最经典的过渡方式 |
| `slide_left` | 图片从右侧滑入 |
| `slide_right` | 图片从左侧滑入 |
| `slide_up` | 图片从底部向上滑动 |
| `slide_down` | 图片从顶部向下滑动 |
| `zoom_in` | 缩放放大效果 |
| `zoom_out` | 缩放缩小效果 |
| `dissolve` | 溶解效果 |
| `wipe` | 横向擦拭效果 |
| `blur` | 模糊过渡效果 |

### 3. 背景音乐
- 支持多种音频格式：MP3, WAV, AAC, OGG
- 自动循环背景音乐以匹配视频时长
- 可选：音乐音量调节

### 4. 输出设置
- 支持多种视频分辨率：720p, 1080p, 4K
- 支持多种输出格式：MP4, AVI, MOV
- 可自定义每张图片显示时长
- 可自定义过渡动画时长

## 使用方法

```python
from photo_album_video import PhotoAlbumGenerator

# 创建生成器实例
generator = PhotoAlbumGenerator()

# 配置参数
config = {
    'images': ['photo1.jpg', 'photo2.jpg', 'photo3.jpg'],  # 图片路径列表
    'music': 'background.mp3',  # 背景音乐路径（可选）
    'transition': 'fade',  # 过渡效果类型
    'image_duration': 3.0,  # 每张图片显示时长（秒）
    'transition_duration': 1.0,  # 过渡动画时长（秒）
    'output': 'album_video.mp4',  # 输出文件路径
    'resolution': '1080p',  # 输出分辨率
    'fps': 30  # 帧率
}

# 生成视频
generator.create_video(config)
```

## 配置参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `images` | List[str] | 必填 | 图片文件路径列表 |
| `music` | str | None | 背景音乐文件路径 |
| `transition` | str | 'fade' | 过渡效果类型 |
| `image_duration` | float | 3.0 | 每张图片显示时长（秒） |
| `transition_duration` | float | 1.0 | 过渡动画时长（秒） |
| `output` | str | 'output.mp4' | 输出文件路径 |
| `resolution` | str | '1080p' | 输出分辨率 |
| `fps` | int | 30 | 视频帧率 |
| `music_volume` | float | 0.7 | 背景音乐音量（0.0-1.0） |
| `bg_color` | str | 'black' | 背景填充色 |
| `quality` | str | 'high' | 输出质量：low, medium, high |

## 示例代码

### 示例1：基本使用

```python
from photo_album_video import PhotoAlbumGenerator

generator = PhotoAlbumGenerator()
generator.create_video({
    'images': ['img1.jpg', 'img2.jpg', 'img3.jpg'],
    'output': 'my_album.mp4'
})
```

### 示例2：指定过渡效果和背景音乐

```python
from photo_album_video import PhotoAlbumGenerator

generator = PhotoAlbumGenerator()
generator.create_video({
    'images': ['photo1.png', 'photo2.png', 'photo3.png', 'photo4.png'],
    'music': 'music.mp3',
    'transition': 'slide_left',
    'image_duration': 4.0,
    'transition_duration': 1.5,
    'output': 'album.mp4',
    'resolution': '1080p'
})
```

### 示例3：高级配置

```python
from photo_album_video import PhotoAlbumGenerator

generator = PhotoAlbumGenerator()
config = {
    'images': ['1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg'],
    'music': 'background_music.mp3',
    'transition': 'dissolve',
    'image_duration': 5.0,
    'transition_duration': 2.0,
    'output': 'high_quality_album.mp4',
    'resolution': '4k',
    'fps': 60,
    'music_volume': 0.6,
    'quality': 'high'
}
generator.create_video(config)
```

### 示例4：批量生成不同风格

```python
from photo_album_video import PhotoAlbumGenerator

generator = PhotoAlbumGenerator()
images = ['a.jpg', 'b.jpg', 'c.jpg']

transitions = ['fade', 'slide_left', 'zoom_in', 'dissolve']

for t in transitions:
    generator.create_video({
        'images': images,
        'transition': t,
        'output': f'album_{t}.mp4'
    })
```

## 依赖说明

需要安装以下Python包：
- `moviepy` - 视频编辑核心库
- `Pillow` - 图片处理
- `numpy` - 数值计算

安装命令：
```bash
pip install moviepy Pillow numpy
```

## 技术实现说明

### 过渡动画实现原理

每种过渡效果都通过 `moviepy` 的 `CompositeVideoClip` 和 `BitmapScroll` 或自定义函数实现：

1. **Fade（淡入淡出）**：使用 `CrossFadeLou` 和透明度调整
2. **Slide（滑动）**：使用位置动画，从起点移动到终点
3. **Zoom（缩放）**：使用缩放变换实现
4. **Dissolve（溶解）**：多个图层叠加透明度变化
5. **Wipe（擦拭）**：使用掩码(mask)实现横向/纵向擦拭效果
6. **Blur（模糊）**：使用高斯模糊滤镜实现过渡

### 音频处理

- 使用 `CompositeAudioClip` 组合背景音乐
- 自动计算视频时长并循环音乐
- 音量归一化处理

## 注意事项

1. 图片数量建议在2-50张之间
2. 每张图片显示时长建议2-8秒
3. 过渡动画时长建议0.5-2秒
4. 分辨率越高，处理时间越长
5. 确保图片路径正确且文件可读
6. 背景音乐文件大小建议不超过50MB

## 错误处理

技能包含完善的错误处理机制：

```python
try:
    generator.create_video(config)
except ValueError as e:
    print(f"参数错误: {e}")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except Exception as e:
    print(f"生成失败: {e}")
```

## 适用场景

- 旅行相册制作
- 活动照片集锦
- 个人写真集
- 产品展示视频
- 婚礼相册视频
- 企业宣传素材
