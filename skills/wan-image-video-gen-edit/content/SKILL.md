---
name: wan-image-video-gen-edit
description: "阿里通义万相Wan系列模型，支持文生图/图生图/图生视频/参考源视频生成。"
---

# Wan Models

阿里Alibaba发布的Wan系列模型，通过ModelStudio(Bailian) API调用。

## 五大能力

| 能力 | 说明 |
|------|------|
| text2image | 文本生成图片 |
| image-edit | 图片编辑 |
| text2video | 文本生成视频（最长15秒） |
| image2video | 图片转视频（首帧图片） |
| reference2video | 参考图/视频生成视频（角色一致性） |

## 核心用法

text2image:
```bash
python3 scripts/wan-magic.py text2image --prompt "描述" --size 1280*1280
```

image-edit:
```bash
python3 scripts/wan-magic.py image-edit --prompt "编辑指令" --images '图1url' '图2url'
```

text2video:
```bash
python3 scripts/wan-magic.py text2video-gen --prompt "视频描述" --duration 10
```

image2video（以图为首帧）:
```bash
python3 scripts/wan-magic.py image2video-gen --prompt "视频描述" --image "图url"
```

reference2video（角色一致性）:
```bash
python3 scripts/wan-magic.py reference2video-gen --prompt "character1在海边漫步" --reference-files "角色url"
```
