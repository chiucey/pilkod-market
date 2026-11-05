# remotion-video — React 视频生成专家

> 用 React 代码程序化生成高质量视频

## 与 jianyin-jianji 的区别

| | jianyin-jianji | remotion-video |
|---|---|---|
| 方式 | FFmpeg 模板化 | React 代码程序化 |
| 适合 | 快速剪辑、已有素材 | 动态数据、复杂特效 |
| 定制性 | 中 | 高 |
| 学习成本 | 低 | 中 |

## 功能
- 动态数据图表动画（柱状/折线/饼图）
- React 组件化视频结构
- FFmpeg Lambda 云端批量渲染
- AI 配音 + 字幕同步
- 打字机/缩放/渐变文字特效

## 快速开始
```
npx create-video@latest my-video
# 复制 examples/video.tsx 到 src/
npx remotion preview
npx remotion render DataReport output.mp4
```

## MIT License
