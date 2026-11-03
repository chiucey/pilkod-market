# Video Reader

直接用 `videos_understand` 工具分析本地视频文件：

```javascript
videos_understand({
  videos_info: [{
    file: "/workspace/video.mp4",
    prompt: "详细描述视频中的所有界面内容、文字、数据"
  }]
})
```

支持 `.mp4`、`.mov`、`.avi`、`.mkv`。

GIF 文件用 PIL 提取帧：
```python
from PIL import Image
with Image.open('/workspace/video.gif') as gif:
    for i in range(min(gif.n_frames, 20)):
        gif.seek(i); f = gif.copy()
        if f.mode == 'P': f = f.convert('RGB')
        f.save(f'/workspace/frame_{i:03d}.jpg')
```
