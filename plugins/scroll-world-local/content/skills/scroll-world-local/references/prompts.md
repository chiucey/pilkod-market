# prompts.md — 视频分析、静图与视频段配方

## 0. 已有视频的章节判断

先读取元数据、联系表和 scene-detect 候选帧，再根据语义划分章节。不要把像素变化直接当成最终章节。

每个章节回答五个问题：

1. 画面主体和动作是什么？
2. 用户在这一章应该理解什么？
3. 哪一帧最值得停留？
4. 进入和离开的视觉依据是什么？
5. 文案应覆盖运动画面，还是放在停稳后的阅读窗口？

输出字段：`source_range / scroll_range / focal_point / motion / overlay / transition / preload`。

## A. 场景静图(image_synthesize)

结构:`<style preamble>` + `SCENE: <画面>` + `<构图指令>`

### style preamble(逐字复用到每张图)
锁风格统一的关键。包含四要素:**媒介/材质 + 光照 + 景深 + 严格调色板**。范例:
```
Clay diorama miniature world, tilt-shift macro photography, handcrafted polymer clay and
felt materials with visible fingerprint texture, warm soft studio lighting, shallow depth
of field. COLOR PALETTE STRICTLY: <hex1>, <hex2> background, <hex3>, <hex4>, <hex5> accents.
```
换风格就换这段(实拍 → "cinematic photography, 35mm, natural light";等距插画 →
"isometric 3D render, soft global illumination, matte clay shading" 等),其余结构不变。

### SCENE + 构图
- 每场景写清楚**主体 + 环境 + 关键道具**。
- 构图统一收尾:`Centered composition, negative space around edges, cinematic.`
- hero/入口场景可给等距全景;finale 给产品 macro 特写 + `space for a call-to-action`。
- 若场景有品牌名/招牌,明确写出文字内容(其余不要文字):`a chalkboard sign reading 'BRAND'.
  No text overlays except the sign.`

### 静图检查
逐张 `read` 看图,确认**主体正确**。不要靠像素直方图/饱和度猜内容——直接看。

---

## B. 视频段(gen_videos,架构 A 帧锁)

结构:`<运动前缀>` + `<从当前场景 → 下一场景的推进描述>` + `<稳定性后缀>` + `<调色板>`

### 运动前缀(固定)
```
Continuous forward camera flight, <风格关键词>, warm cinematic lighting, no cuts.
```

### 稳定性后缀(固定,防抖防跳)
```
Steady dolly-forward motion, seamless continuous push-in, no camera shake.
```

### 中段推进描述(每段变)
镜头**只向前**。合法运动 = 推进 / 俯冲 / 掠过 / 穿门 / 钻进物体 / 拉出 / 减速落定。
用"起点→终点"句式,让画面从上段末帧自然演化到下个场景入口:
- 推进:`gliding low over <A>, pushing forward toward <B>`
- 穿门:`glides forward through the glowing doorway, into the interior, toward <B>`
- 钻进再拉出:`dives into the glowing <object>` → 下段 `pulls forward out of the <object>, emerging toward <B>`
- finale 落定:`pushes ahead and settles into an intimate extreme close macro of <product>,
  slows to a gentle rest framing it centered as the final shot.`

### 关键纪律
- 首段用第一张静图当 first_frame;之后每段 first_frame = 上段真实末帧(ffmpeg 抽)。
- `reference_type:"first_frame"`、`duration:6`(可试 10)、`resolution:"1080P"`。
- 每段生成后抽末帧 `read` 看:①首帧≈上段末帧 ②末帧推进到了下场景入口。
- 末帧构图会成为下段起点,所以 prompt 里让镜头**停在一个能自然接下一场景的位置**。
- 首帧锁定只保证像素接缝，不保证末帧到达目标场景。把下一章关键帧作为验收参考；若偏离，重生当前段，不把漂移继续传下去。

### 过渡设计小抄
戏剧性的"钻进→拉出"过渡(如钻进发光烘焙滚筒内部特写,下段再从内部拉出到门店)非常出效果——
它天然制造了一个视觉高潮点,又保持镜头只向前。善用场景里可"钻进"的发光物体(炉膛/窗/门/杯口)。

---

## C. 章节式生成

当故事需要明显不同的场景、排版页或产品 UI 时，各章可以独立生成，不强求伪装成一镜到底。

每章 prompt 使用：

```text
STYLE BIBLE: <共同的材质、调色板、光线、镜头>
CHAPTER: <本章主体、环境和动作>
ENTRY: <如何承接上一章>
HERO FRAME: <本章核心画面和留白>
EXIT: <遮挡、门、窗口、主体特写或色块，供下一章切换>
LOCK: preserve <品牌主体、产品外形、文字、色彩和光线>
```

优先使用与内容有关的转场：布料遮挡、门窗穿越、产品特写、匹配运动、静帧或纯色 DOM 排版。转场数量保持克制，让用户有阅读和理解的停顿。
