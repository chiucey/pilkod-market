---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fff17196573b4bff54591cfd963c63ef
    PropagateID: fff17196573b4bff54591cfd963c63ef
    ReservedCode1: 304502200e2019377a0eedad91b1e7971276befc5740586c8ba0b5d5aeedcd9777aa8500022100e78985ae30b76ff9640000eebf46c3d30280dda5db6f255c63f62b28deb456e6
    ReservedCode2: 304402201290f44cbc3477169f727e04c6c7bf5dc5e339588c9f9be25cc77083789a33a30220076b4477b733255de6671471c2961add5eef30af92e98cdaa66ad023b32dd2a9
description: HyperFrames — AI 视频创作技能。用 HTML 写视频，为 AI Agent 与批量视频工厂而生。 触发词：做视频、生成视频、制作视频、剪辑视频、视频配音、字幕视频、HyperFrames、 HTML视频、短视频批量、产品视频、演示视频、数据图表视频、AI短剧、竖屏视频。 技术栈：HeyGen 开源框架，HTML+CSS+GSAP 创作，FFmpeg 渲染，Node.js >= 22。
name: hyperframes-ai-video
---

# HyperFrames — AI 视频创作技能

> 官网：https://hyperframes.heygen.com | GitHub：heygen-com/hyperframes
> 许可证：Apache 2.0（完全开源，可商用，无渲染费用）

---

## 核心理念

**HTML 是视频源代码。**

- 视频 = HTML 文件 + `data-*` 属性（时间轴）+ GSAP 时间线（动画）+ CSS（外观）
- 框架自动处理片段显隐、媒体播放、时间同步
- 无打包步骤，无需 React，无专有 DSL
- AI Agent 已原生理解 HTML，工作流天然对齐

**设计哲学：** 先建最终静态布局 → 再加入场动画 → 再加出场动画。
禁止边写动画边猜位置。

---

## 环境要求

- **Node.js >= 22**（`node -v` 检查）
- **FFmpeg** 在 PATH 中（`ffmpeg -version` 检查）
- 无需全局安装（`npx hyperframes` 按需下载运行）

---

## 五步工作流

```
描述需求 → 生成 HTML 组合文件 → lint 语法检查 → preview 预览 → render 渲染
```

```bash
# 1. 初始化项目
npx hyperframes init my-video

# 2. 编辑 index.html（核心创作步骤）

# 3. 每次修改后必跑语法检查
npx hyperframes lint

# 4. 浏览器预览（热重载，默认端口 3002）
npx hyperframes preview --port 3002

# 5. 渲染输出 MP4
npx hyperframes render --output final.mp4
```

**模板列表**：`blank` | `warm-grain` | `play-mode` | `swiss-grid` | `vignelli` | `decision-tree` | `kinetic-type` | `product-promo` | `nyt-graph`

---

## HTML 组合语法

### 最小完整骨架

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>My Video</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
</head>
<body>
  <!-- 根组合：必填 data-composition-id / data-width / data-height / data-start="0" -->
  <div
    id="root"
    data-composition-id="my-video"
    data-start="0"
    data-width="1920"
    data-height="1080"
  >
    <!-- 媒体片段写在这里 -->
  </div>

  <script>
    window.__timelines = {};
    window.__registerTimeline = function(id, tl) {
      tl.pause();
      window.__timelines[id] = tl;
    };
    // 你的 GSAP 动画写在这里
    var tl = gsap.timeline();
    // tl.from("#el", { y: 50, opacity: 0, duration: 0.6, ease: "power3.out" }, 0.1);
    // ...
    window.__registerTimeline("main", tl);
  </script>
</body>
</html>
```

### 片段类型

| 类型 | 标签 | 关键属性 |
|------|------|---------|
| 视频 | `<video>` | `data-start`, `data-duration`, `data-track-index`, `src`, `muted`, `playsinline` |
| 图片 | `<img>` | `data-start`, `data-duration`, `data-track-index`, `src` |
| 音频 | `<audio>` | `data-start`, `data-duration`, `data-track-index`, `src`, `data-volume="0.5"` |
| 字幕 | `<div>` | `data-start`, `data-duration`, `data-track-index` |
| 子组合 | `<div>` | `data-composition-id`, `data-composition-src`, `data-start`, `data-duration` |

### 关键属性速查

| 属性 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 片段唯一 ID |
| `data-start` | ✅ | 开始时间（秒，或 `"el-1"` / `"el-1 + 2"` 引用）|
| `data-duration` | ⚠️ | 持续秒数；视频/音频可省略，取媒体实际时长 |
| `data-track-index` | ✅ | 轨道索引；同轨道片段不可重叠 |
| `data-media-start` | 否 | 媒体内部偏移（秒）|
| `data-volume` | 否 | 音量 0~1（仅音频/视频）|

### 宽高比

| 场景 | 尺寸 |
|------|------|
| YouTube / 横版 | `1920×1080` |
| TikTok / Reels / 小红书 / 竖屏 | `1080×1920` |
| 通用横版 | `1280×720` |
| 方形 | `1080×1080` |

---

## GSAP 动画规范

### 时间线注册（必须遵守）

```js
// ✅ 正确：暂停 + 注册
var tl = gsap.timeline();
tl.to("#el", { opacity: 0, duration: 0.5 });
tl.pause();
window.__registerTimeline("main", tl);

// ❌ 错误：未注册，时间线不播放
var tl = gsap.timeline();
tl.to("#el", { opacity: 0 });
// 忘记 pause() 和 registerTimeline
```

### 三段式动画结构

| 阶段 | 时间占比 | 任务 |
|------|---------|------|
| **Build（入场）** | 0~30% | 元素交错入场，从重要到次要，总时长 < 500ms |
| **Breathe（持续）** | 30~70% | 内容完全可见，配 1 个氛围动画（呼吸/漂移/微动）|
| **Resolve（离场）** | 70~100% | 快速离场，出场 < 入场时长 |

```js
var tl = gsap.timeline();
// Build：交错入场
tl.from("#el-title", { y: 50, opacity: 0, duration: 0.5, ease: "power3.out" }, 0.1);
tl.from("#el-sub",   { y: 30, opacity: 0, duration: 0.4, ease: "power3.out" }, 0.25);
tl.from("#el-tag",   { scale: 0.9, opacity: 0, duration: 0.3, ease: "back.out(1.7)" }, 0.35);
// Breathe：氛围动画
gsap.to("#bg-glow", { scale: 1.05, opacity: 0.6, duration: 2.5, yoyo: true, repeat: -1, ease: "sine.inOut" });
// Resolve：离场（快于入场）
tl.to("#el-title", { y: -30, opacity: 0, duration: 0.3, ease: "power2.in" }, 3.5);
tl.to("#el-sub",   { y: -20, opacity: 0, duration: 0.25, ease: "power2.in" }, 3.6);
window.__registerTimeline("main", tl);
```

### Easing 情感对照表

| Easing | 情感 | 适用场景 |
|--------|------|---------|
| `power3.out` | 自信、响应快 | 标题入场 |
| `back.out(1.7)` | 弹力、活泼 | 数字弹出、标签 |
| `elastic.out` | 开心、童趣 | 贴纸、emoji |
| `bounce.out` | 重量感、实体 | 游戏化 |
| `sine.inOut` | 梦幻、流畅 | 过渡 |
| `power2.in` | 离开感、抛离 | 元素退场（必须用 .in）|
| `expo.out` | 冲击力、震撼 | 大标题 |
| `linear` | 机械 | 进度条、计时器 |

**核心规则：入场用 `.out`，离场用 `.in`，位移用 `.inOut`**

### 速度与重量感

| 时长 | 感受 |
|------|------|
| 0.15~0.3s | 高能、急迫 |
| 0.3~0.5s | 专业、大多数内容 |
| 0.5~0.8s | 重量感、奢侈 |
| 0.8~2.0s | 情绪铺垫、大气 |

### 入场方向（禁止统一方向）

- ✅ `y: 50`（从下）| `y: -50`（从上）| `x: -80`（从左）| `x: 80`（从右）
- ✅ `scale: 0.8`（缩小展开）| `opacity: 0`（纯淡入）| `letterSpacing`（字间距）
- ❌ 禁止所有元素都用 `y: 30, opacity: 0` 统一入场

### AI 设计习惯黑名单（需主动规避）

| AI 默认习惯 | 正确做法 |
|------------|---------|
| 渐变色文字 | 纯色 + 阴影或光效层 |
| 卡片左侧竖线装饰 | 用边框、背景块替代 |
| 蓝紫渐变 | 选一个单色 accent |
| 纯 `#000` / `#fff` | 用 accent 色调倾向 |
| 等大卡片网格 | 不规则大小区分主次 |
| 全部居中布局 | 锚定左/右边缘 |
| 万能 `power2.out` | 根据情绪选择 easing |
| 统一 0.4~0.5s | 最快与最慢差 3 倍以上 |

---

## 设计规范：视觉身份门

> ⚠️ **每次创作前必须完成此步骤，未确认风格前禁止写 HTML。**

### 判断优先级

```
项目有 DESIGN.md？
  → 严格遵循颜色/字体/动效/禁止项

用户指定风格名称（如 "科技感"、"温暖插画"）？
  → 应用预设风格，生成设计决策

无任何指引？
  → 询问 3 个问题：
    1. 整体基调？（震撼电影感 / 清新自然 / 科技未来 / 温暖人文 / 简约商务）
    2. 深色背景还是浅色背景？
    3. 有无品牌色、字体或视觉参考？
```

### 8 种预设风格

| 风格 | 适用场景 |
|------|---------|
| Bold / Energetic | 产品发布、社交媒体、活动公告 |
| Warm / Editorial | 纪录片、人物访谈、品牌故事 |
| Dark / Premium | 科技、金融、奢侈品、电影感 |
| Clean / Corporate | 教程、演示、企业介绍 |
| Nature / Earth | 环保、户外、有机、可持续 |
| Neon / Electric | 游戏、电竞、夜店、科技 |
| Pastel / Soft | 时尚、美妆、生活方式、身心健康 |
| Jewel / Rich | 晚会、奢侈品、高端定制 |

### 色彩系统规则

- 声明一个背景色（bg）+ 一个前景色（fg）+ 一个强调色（accent）
- 中性色向 accent 色相倾斜，不要纯灰 `#888`
- 场景内背景色统一，不频繁切换
- 对比度必须通过 WCAG AA

### 背景层（必须要有）

每个场景至少 2~5 个持续装饰元素，与内容共存：
- 径向光晕（accent 色，低透明度，慢速呼吸动画）
- 幽灵文字（大字主题词，3~8% 透明度，极慢漂移）
- 细线装饰（发丝线，微脉冲）
- 噪点/纹理叠加，几何形状

### 画面构成（视频不是网页）

- 每个场景 **至少 2 个视觉焦点**，引导眼球移动
- 主标题占宽度 **60~80%**，不是网页大小的文字
- **至少 3 层**：背景装饰层 + 前景内容层 + 点缀元素层
- **锚定边缘**，不要漂浮居中
- **分区布局**：左侧数据面板 + 右侧内容，或顶部标签栏 + 下方主区

---

## 字幕与配音流水线

### Step 1 — 列出可用音色

```bash
npx hyperframes tts --list
```

### Step 2 — 生成 TTS 配音

```bash
npx hyperframes tts "视频配音文案内容" \
  --voice af_sarah \
  --output narration.wav
```

### Step 3 — Whisper 转写字幕

```bash
npx hyperframes transcribe narration.wav \
  --model medium \
  --language zh
```

### Step 4 — 嵌入 HTML

```html
<!-- 每个字幕片段独立轨道，到时间自动显示/隐藏 -->
<div
  id="caption-1"
  data-start="0"
  data-duration="3.5"
  data-track-index="10"
  style="position:absolute;bottom:120px;width:100%;text-align:center;"
>
  <p style="font-size:48px;color:#fff;font-family:sans-serif;
            text-shadow:0 2px 12px rgba(0,0,0,0.9);">
    欢迎来到本期内容
  </p>
</div>
<div
  id="caption-2"
  data-start="3.5"
  data-duration="4"
  data-track-index="10"
  style="position:absolute;bottom:120px;width:100%;text-align:center;"
>
  <p style="font-size:48px;color:#fff;font-family:sans-serif;
            text-shadow:0 2px 12px rgba(0,0,0,0.9);">
    今天我们深入探索 AI 的前沿
  </p>
</div>
```

---

## 渲染参数

| 参数 | 值 | 默认 | 说明 |
|------|-----|------|------|
| `--fps` | 24/30/60 | 30 | 60fps 渲染时间翻倍 |
| `--quality` | draft/standard/high | standard | draft 快速迭代，high 最终交付 |
| `--format` | mp4/webm | mp4 | WebM 支持透明通道 |
| `--output` | 路径 | `renders/xxx_timestamp.mp4` | 输出文件 |
| `--workers` | 1~8/auto | auto | 并行 Chrome 进程数 |
| `--docker` | flag | off | 字节级一致性渲染 |
| `--strict` | flag | off | lint 错误时中断 |

```bash
# 迭代阶段：快速草稿
npx hyperframes render --quality draft

# 最终交付：高规格
npx hyperframes render --fps 60 --quality high --output final.mp4

# 透明通道（用于合成）
npx hyperframes render --format webm --output with-alpha.webm
```

---

## 常用场景模板

### 片头标题卡（3~5s）

```html
<div
  id="scene-title"
  data-start="0"
  data-duration="5"
  data-track-index="5"
  style="display:flex;align-items:center;justify-content:center;
         background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);"
>
  <h1 style="font-size:120px;color:#fff;font-weight:800;
             text-align:center;letter-spacing:-3px;opacity:0;">
    智能创作<br/>无限可能
  </h1>
</div>
```
```js
var tl = gsap.timeline();
tl.from("h1", { scale: 0.85, opacity: 0, duration: 0.8, ease: "expo.out" }, 0.1);
tl.to("h1",   { scale: 1.05, opacity: 0, duration: 0.6, ease: "power2.in" }, 4);
window.__registerTimeline("main", tl);
```

### 动态柱状图

```html
<div id="chart-scene" data-start="0" data-duration="6" data-track-index="0">
  <div style="display:flex;align-items:flex-end;gap:48px;padding:100px 160px;
             height:100%;box-sizing:border-box;align-self:flex-end;">
    <div id="bar-1" style="flex:1;height:0;background:#4f46e5;border-radius:12px 12px 0 0;"></div>
    <div id="bar-2" style="flex:1;height:0;background:#06b6d4;border-radius:12px 12px 0 0;"></div>
    <div id="bar-3" style="flex:1;height:0;background:#10b981;border-radius:12px 12px 0 0;"></div>
    <div id="bar-4" style="flex:1;height:0;background:#f59e0b;border-radius:12px 12px 0 0;"></div>
  </div>
</div>
```
```js
var tl = gsap.timeline();
tl.to("#bar-1", { height: "320px", duration: 0.7, ease: "power2.out" }, 0.1);
tl.to("#bar-2", { height: "480px", duration: 0.7, ease: "power2.out" }, 0.25);
tl.to("#bar-3", { height: "240px", duration: 0.7, ease: "power2.out" }, 0.4);
tl.to("#bar-4", { height: "400px", duration: 0.7, ease: "power2.out" }, 0.55);
window.__registerTimeline("main", tl);
```

### 竖屏 TikTok / 小红书（1080×1920）

```html
<div
  id="root"
  data-composition-id="vertical-hook"
  data-start="0"
  data-width="1080"
  data-height="1920"
>
  <video id="bg" data-start="0" data-duration="20"
         data-track-index="0" src="bg.mp4" muted playsinline></video>
  <div id="hook" data-start="0" data-duration="3" data-track-index="2"
       style="position:absolute;top:300px;padding:0 60px;box-sizing:border-box;">
    <p style="font-size:80px;color:#fff;font-weight:900;line-height:1.1;
              text-shadow:0 4px 20px rgba(0,0,0,0.5);">
      3秒留住<br/>每一个用户
    </p>
  </div>
  <div id="bullets" data-start="3" data-duration="12" data-track-index="3"
       style="position:absolute;top:700px;padding:0 60px;box-sizing:border-box;">
    <p style="font-size:44px;color:#fff;line-height:2.2;font-weight:500;">
      ✅ 精准定位目标用户<br/>
      ✅ 批量生成效率翻倍<br/>
      ✅ AI 赋能创意生产
    </p>
  </div>
  <div id="cta" data-start="16" data-duration="4" data-track-index="4"
       style="position:absolute;bottom:280px;width:100%;text-align:center;">
    <p style="font-size:60px;color:#ffd700;font-weight:900;">立即开始 →</p>
  </div>
</div>
```

### 画中画（产品演示）

```html
<div id="pip-frame"
     style="position:absolute;top:0;left:0;width:1920px;height:1080px;
            z-index:50;overflow:hidden;">
  <video id="demo-video"
         data-start="0" data-duration="60" data-track-index="0"
         src="demo.mp4" muted playsinline></video>
</div>
```
```js
var tl = gsap.timeline();
// 10s 处缩小并移至右下角
tl.to("#pip-frame", {
  top: 720, left: 1360, width: 500, height: 300,
  borderRadius: 16, duration: 1, ease: "power2.out"
}, 10);
// 30s 处回到全屏
tl.to("#pip-frame", { left: 0, top: 0, width: 1920, height: 1080, duration: 0.6 }, 30);
window.__registerTimeline("main", tl);
```

### 多段幻灯片

```html
<!-- 同轨道片段自动串行播放，无需手动控制时间接续 -->
<div class="slide" data-start="0"  data-duration="8"  data-track-index="3">...内容1...</div>
<div class="slide" data-start="8"  data-duration="7"  data-track-index="3">...内容2...</div>
<div class="slide" data-start="15" data-duration="6"  data-track-index="3">...内容3...</div>
<div class="slide" data-start="21" data-duration="5"  data-track-index="3">...内容4...</div>
```

---

## 50+ 预制组件

```bash
npx hyperframes add flash-through-white   # 闪光转场
npx hyperframes add instagram-follow      # 社交关注引导
npx hyperframes add data-chart            # 动态图表
npx hyperframes add countdown             # 倒计时
# 查看全部：https://hyperframes.heygen.com/catalog/blocks/
```

---

## 错误排查

| 症状 | 检查项 |
|------|--------|
| 预览黑屏 | 根 div 是否有 `data-composition-id`？`data-width/height` 是否填写？|
| GSAP 动画不动 | 时间线是否调用了 `.pause()` + `window.__registerTimeline()`？|
| 片段重叠 | 同 `data-track-index` 的片段时间不能重叠 |
| 渲染卡住 | `ffmpeg -version` 确认 FFmpeg 在 PATH |
| 轨道溢出 | 片段总时长超出根 div 的 `data-duration` |
| 中文字体异常 | 使用 Google Fonts 中文字体（如 Noto Sans SC），`@import` 放 CSS 顶部 |

---

## 不适合的场景

- 复杂多轨非线性剪辑（用剪映 / Premiere）
- 需要逐字精调的手册式字幕（用剪映更高效）
- 实时直播录制
- 需要复杂粒子/烟雾/原生 3D 特效的视频
