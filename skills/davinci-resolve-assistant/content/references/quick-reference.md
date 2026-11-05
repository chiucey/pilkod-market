# DaVinci Resolve 快速参考卡

## 页面快捷键
| 快捷键 | 页面 |
|--------|------|
| Shift+4 | Media |
| Shift+5 | Cut |
| Shift+6 | Edit |
| Shift+7 | Fusion |
| Shift+8 | Color |
| Shift+9 | Fairlight |
| Shift+10 | Deliver |

## 时间线操作
| 操作 | 快捷键 |
|------|--------|
| 缩放时间线 | +/- 或 Alt+滚轮 |
| 移动播放头 | J/K/L (多次按加速) |
| 标记入点 | I |
| 标记出点 | O |
| 跳转入点 | Shift+I |
| 跳转到出点 | Shift+O |
| 添加标记 | M |
| 到下一个标记 | Shift+M |

## 调色节点系统
```
输入 → 节点1 (基础校准) → 节点2 (风格化) → 节点3 (局部调整) → 输出
```

### 节点类型
- **串行节点 (Serial)**：依次处理
- **并行节点 (Parallel)**：叠加效果
- **层叠节点 (Layer)**：Alpha 混合

## Fusion 常用节点
| 节点 | 用途 |
|------|------|
| MediaIn/MediaOut | 输入输出 |
| Merge | 叠加/合成 |
| Blur | 模糊 |
| ColorCorrect | 色彩校正 |
| Transform | 位置/缩放/旋转 |
| Text+ | 字幕/标题 |

## 音频处理
| 功能 | 位置 |
|------|------|
| 降噪 | Fairlight → Noise Reduction |
| EQ 调整 | Fairlight → EQ |
| 压缩器 | Fairlight → Dynamics |
| 混音 | Fairlight → Mix |

## 项目设置检查清单
- [ ] 时间线分辨率匹配输出
- [ ] 帧率与素材一致
- [ ] 色彩空间正确（Rec.709/DCI-P3/HDR）
- [ ] 启用正确音频采样率
