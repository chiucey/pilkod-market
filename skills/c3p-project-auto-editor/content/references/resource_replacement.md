# 资源替换指南

## 支持的格式

### 图片格式

| 格式 | 扩展名 | 推荐用途 |
|-----|--------|---------|
| PNG | .png | 透明背景、UI元素 |
| JPEG | .jpg/.jpeg | 照片、背景 |
| WebP | .webp | 高压缩比图片 |
| GIF | .gif | 动画 |

### 音频格式

| 格式 | 扩展名 | 推荐用途 |
|-----|--------|---------|
| OGG | .ogg | 跨平台音频 |
| MP3 | .mp3 | 音乐 |
| WAV | .wav | 音效 |
| AAC | .aac | iOS音频 |

### 字体格式

| 格式 | 扩展名 |
|-----|--------|
| TTF | .ttf |
| OTF | .otf |
| WOFF | .woff |

## 替换规则

### 1. 按名称替换

```python
# 替换指定名称的资源
manager.replace_resource('background.png', '/path/to/new/background.png')
```

### 2. 按类型替换

```python
# 替换所有背景图
bg_resources = manager.find_resource_by_type('background')
for bg in bg_resources:
    manager.replace_resource(bg.original_name, '/path/to/new/background.png')
```

### 3. 批量替换

```python
manager.batch_replace({
    'player.png': '/path/to/player.png',
    'enemy.png': '/path/to/enemy.png',
    'coin.png': '/path/to/coin.png'
})
```

## 图标替换

```python
# 替换应用图标
manager.replace_app_icon('/path/to/icon.png')
```

## 图片优化

```python
# 优化图片尺寸和质量
manager.optimize_image('/path/to/image.png',
                       max_width=1024,
                       max_height=1024,
                       quality=85)
```

## 路径规范

- 媒体资源放在 `media/` 目录
- 图片放在 `media/images/`
- 音频放在 `media/audio/`
- 保持原文件命名规范

## 注意事项

1. **格式兼容性**：尽量保持原格式
2. **尺寸要求**：图标需512x512 PNG
3. **命名规范**：避免特殊字符
4. **备份原文件**：编辑器会自动备份
