---
name: fashion-showcase
description: 服装展示视频生成工具（微信版）。支持逐张接收图片，自动识别类型（参考图/服装图），汇总后自动进入生成流程。
工作目录：/workspace/skills/fashion-showcase/
---

# fashion-showcase 服装展示视频生成（微信适配版）

## 核心逻辑改变

**微信无法同时发送两张图**，因此 skill 改为：
- 每收到一张图 → **立即识别类型** → **提取对应提示词** → **存储到 state**
- 收到**两张图并都处理完毕** → **自动触发试穿图生成**（不再等用户操作）

---

## 工具清单

- `images_understand` — 分析图片类型并提取提示词
- `image_synthesize` — 生成试穿图和变体图
- `batch_image_to_video` — 将变体图批量转为视频
- `upload_to_cdn` — 发送图片/视频前必须先调用此工具获取 CDN 公开 URL
- `message` — 发送图片和视频（使用 `media` 字段）
- `exec` / `write` / `read` — 状态文件读写

---

## 工作目录

```
/workspace/skills/fashion-showcase/
```

目录文件：
- `state.json` — 工作流状态
- `ref.png` — 参考图副本（如有）
- `clothing.png` — 服装图副本（如有）
- `ref_prompt.txt` — 参考图提示词（自动生成）
- `clothing_desc.txt` — 服装描述（自动生成）
- `tryon_1.png` ~ `tryon_4.png` — 4张试穿图
- `variation_1.png` ~ `variation_8.png` — 变体图
- `video_1.mp4` ~ `video_8.mp4` — 生成的视频
- `final.mp4` — 最终输出视频

---

## 状态管理

通过 `state.json` 的 `stage` 字段管理：

| stage | 含义 | 触发条件 |
|-------|------|---------|
| `idle` | 等待中 | 初始状态 |
| `ref_received` | 参考图已处理，等待服装图 | 参考图处理完毕 |
| `clothing_received` | 服装图已处理，等待参考图 | 服装图处理完毕 |
| `both_ready` | 两张图都就绪，生成试穿图中 | 自动触发 |
| `tryon` | 等待选择试穿图 | 4张试穿图生成完毕 |
| `variation` | 等待确认变体图 | 变体图生成完毕 |
| `done` | 流程结束 | 视频发送完毕 |

---

## 微信图片接收流程（核心）

### 收到任意一张图片时，立即执行以下逻辑：

**第一步：判断图片类型**

用 `images_understand` 分析图片：
```
Prompt: "Is this image primarily showing: (1) a human model with visible pose/body (reference image), or (2) a clothing/garment product shot (clothing image)? Briefly describe what's in the image."
```

**根据识别结果分流：**

#### 情况A：识别为参考图（Reference Image）

1. **保存图片**
   ```
   cp <图片路径> /workspace/skills/fashion-showcase/ref.png
   ```

2. **提取参考图提示词**

   用以下 prompt 提取风格元素（仅提取这些维度，不提取模特姿势/表情/脸）：
   ```
   Please analyze this reference image and extract ONLY the following elements (do NOT describe the model's specific pose, facial expression, or identity):

   1. Scene and environment (what kind of place: indoor/outdoor, concrete/wood/brick, props present, wall color/texture, etc.)
   2. Lighting style (hard/soft/warm/cool, natural/direct flash, direction, contrast level, color temperature)
   3. Overall mood and aesthetic (underground/lo-fi/street/editorial/commercial, mood: gritty/cool/relaxed/etc.)
   4. Subject gender (male/female, approximate age if identifiable from style)

   Output in this exact format:
   - Scene: <scene description>
   - Lighting: <lighting description>
   - Mood: <mood and aesthetic>
   - Gender: <male/female>
   ```

3. **保存提示词到文件**
   ```
   echo "<提取的提示词>" > /workspace/skills/fashion-showcase/ref_prompt.txt
   ```

4. **更新 state.json**
   ```json
   {
     "stage": "ref_received",
     "ref_prompt": "<提取的提示词>",
     "ref_analyzed": true,
     "clothing_analyzed": false
   }
   ```

5. **回复用户**
   "✅ 参考图已识别！场景：[简短描述]，性别：[男/女]。等待服装图..."

6. **检查是否同时已有服装图**（state 中 clothing_analyzed == true）
   - 如果是 → 立即进入「两张图都就绪」流程（见 below）

#### 情况B：识别为服装图（Clothing Image）

1. **保存图片**
   ```
   cp <图片路径> /workspace/skills/fashion-showcase/clothing.png
   ```

2. **提取服装描述**

   用以下 prompt：
   ```
   Please analyze this clothing image and describe ONLY the garment itself:
   1. Clothing type (t-shirt/long sleeve/coat/pants/dress/etc.)
   2. Main color and pattern
   3. Style details (neckline/sleeves/fit etc.)
   4. Material/visual texture

   Keep it under 30 words in English, I will use this to generate images of a model wearing this garment.
   ```

3. **保存描述到文件**
   ```
   echo "<服装描述>" > /workspace/skills/fashion-showcase/clothing_desc.txt
   ```

4. **更新 state.json**
   ```json
   {
     "stage": "clothing_received",
     "clothing_desc": "<服装描述>",
     "ref_analyzed": false,
     "clothing_analyzed": true
   }
   ```

5. **回复用户**
   "✅ 服装图已识别！款式：[简短描述]。等待参考图（模特姿势/场景图）..."

6. **检查是否同时已有参考图**（state 中 ref_analyzed == true）
   - 如果是 → 立即进入「两张图都就绪」流程（见 below）

---

## 两张图都就绪后的自动流程

### 状态：stage = "both_ready"（自动触发，无需用户操作）

**读取已保存的提示词：**
- `ref_prompt.txt` → 参考图风格描述（场景 + 光线 + 氛围 + 性别）
- `clothing_desc.txt` → 服装描述（款式 + 颜色 + 面料 + 版型）

**更新 state.json：**
```json
{ "stage": "both_ready" }
```

**自动进入 Step 2（生成试穿图），无需用户额外操作。**

---

## Step 2：生成4张试穿图（核心生成逻辑）

### ⚠️ 关键原则

- **参考图不作为图片输入**，只提取文字风格描述
- **服装图为唯一图片输入**（input_files），确保服装细节忠实于原图
- 场景/光线/氛围全靠文字 prompt 描述
- 模特描述包含：脸型、发色/发型、完整上下身穿搭配（外套+裤子+鞋子）

### 生成方式

`image_synthesize`，仅以服装图为 `input_files`，prompt 包含所有风格和人物描述。

### 4张试穿图 prompt 模板

每张图须包含以下六大要素，按此顺序排列：

```
1. [场景] Gritty underground urban indoor scene: graffiti-covered concrete walls, spray paint on plaster, worn torn fabric sofa
2. [光线] Direct on-camera flash, hard high-contrast shadows, cool color temperature, raw lo-fi aesthetic
3. [氛围] Underground street vibe, raw edgy mood
4. [模特] MODEL [N]: young male, [脸型], [发型发色], [气质描述]. Full outfit: [上装描述]; [裤子描述]; [鞋子描述]
5. [姿势] FRONT VIEW facing camera directly, [具体姿势]
6. [构图硬约束] COMPLETE full body visible from top of head to toes — feet and shoes fully visible at bottom, nothing cut off, full-body shot only. 3:4 portrait aspect ratio. No crop, no close-up
```

### 4张图的人物变量（其余元素完全一致）

| 图号 | 脸型 | 发型/发色 | 上装 | 裤子 | 鞋子 | 姿势 |
|------|------|---------|------|------|------|------|
| 1 | angular sharp bone structure | short buzz cut, dark black | 深蓝黑拼色拉链抓绒, 高领宽松 | slim fit black jeans | black chunky combat boots | standing straight, arms relaxed |
| 2 | soft round youthful | medium-length textured messy, brown highlights | 同上 | relaxed dark wash denim | white classic sneakers | slight weight shift, natural stance |
| 3 | long lean, sharp jawline | short faded on sides, dark | 同上 | straight leg black cargo pants | black leather Chelsea boots | hand in pocket, relaxed cool |
| 4 | boyish round, thick eyebrows | short wavy messy, dark brown | 同上 | ripped skinny black jeans | red high-top sneakers | standing at ease, casual cool |

**4张图的上装描述统一为：**
> Navy blue and black two-tone zip-up fleece jacket, mock neck collar, long sleeves, side pockets, relaxed fit, white chest logo, soft matte fleece texture

### 统一强制约束（每张 prompt 必须包含）

- `FRONT VIEW facing camera directly` — 正面朝向镜头
- `COMPLETE full body visible from top of head to toes` — 完整全身
- `feet and shoes fully visible at bottom, nothing cut off` — 脚和鞋必须完整
- `full-body shot only` — 明确全身
- `3:4 portrait aspect ratio` — 3:4 竖图比例
- `No crop, no close-up` — 禁止裁切和特写
- `Consistent gritty scene throughout` — 场景全程一致

保存为 `tryon_1.png` ~ `tryon_4.png`，更新 `state.json`：
```json
{
  "stage": "tryon",
  "tryon_images": ["tryon_1.png", "tryon_2.png", "tryon_3.png", "tryon_4.png"]
}
```

**发送4张图给用户，先批量上传CDN，再逐一发送。**

发送完毕后留言：
> "✅ 4张试穿图生成完成！请选择你最喜欢的一张（发 1、2、3 或 4），或说'重新生成'再试。"

---

## Step 3：用户选择 → 生成裂变变体图

用户回复 1/2/3/4 → 以对应试穿图为蓝本，生成8张变体图。

**8张变体图的组合（景别均衡 + 时尚松弛姿势）：**

景别比例：全身×2 · 中景×2 · 近景×2 · 特写×2

```
变体1（中景）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. fashion model pose, standing naturally with hands relaxed at sides, head slightly tilted toward camera, relaxed cool attitude, medium shot (above knee), effortlessly stylish, cool and calm
变体2（近景）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. one hand casually brushing through hair, natural head turn, relaxed pose, close-up shot (waist up), subtly stylish movement, cool and calm
变体3（近景）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. adjusting sleeve cuff casually, composed natural expression, close-up (chest up), relaxed and effortless style, cool and calm
变体4（全身）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. weight shifted to one leg, one hand in pocket, head slightly tilted, casually stylish full body pose, relaxed cool attitude, full body shot, effortlessly stylish
变体5（特写）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. looking down with a soft expression, face and jacket collar in frame, intimate close-up composition, cool calm mood, subtly stylish
变体6（全身）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. caught mid-step while walking, relaxed natural stride, candid editorial moment, full body shot, street style atmosphere, effortlessly stylish
变体7（特写）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. fingers gently touching jacket zipper and pocket detail, garment detail showcase, intimate close-up, relaxed natural pose, cool and calm
变体8（中景）: {场景}, {光线}, {氛围}. MODEL: young male, face similar style but different individual. Full outfit from try-on image. slight natural smile, head tilted, relaxed and approachable pose, medium shot, effortlessly stylish, cool calm energy
```

**统一动作约束（每张prompt必须包含）：**
- `face similar style but different individual` — 新模特，与试穿图不同人
- `fashion model pose` — 时尚模特感
- `effortlessly stylish, cool and calm` — 时尚松弛不刻意
- `relaxed natural pose` — 自然放松
- `subtly stylish movement` — 酷感不过猛
- 不允许出现提衣领和摸面料同时存在

以**用户选中的试穿图**作为 `input_files`，逐一生成8张变体图。
保存为 `variation_1.png` ~ `variation_8.png`。

更新 state.json：`stage: "variation"`

**发送变体图给用户（先批量上传CDN，再逐一发送）。**

---

## Step 4：用户确认 → 生成视频

用户发送"确认"（或任意包含"确认"/"ok"/"好"的消息）→ 将8张变体图全部转为视频。

**视频生成 prompt（场景一致 + 动作幅度小 + 5秒）：**
```
Fashion film, {参考图完整场景描述}, consistent background throughout, no scene change.
Subtle, natural fashion movements only:
- gentle collar adjustment gesture
- slight fabric touch / fabric texture close-up
- slow camera push-in to show garment details and material
- small garment adjustment (zipper, hem, fit)
- subtle standing pose shifts
- elegant and gentle turning motion
5-second clip, smooth camera movement, soft studio lighting, high-end commercial quality.
```

**关键约束（每段视频prompt必须包含）：**
- `consistent scene throughout, no scene transition` — 锁定场景不漂移
- `subtle natural movement, no dramatic actions` — 动作幅度小，禁止过大动作
- `small garment adjustments` — 以服装展示动作为主
- `5-second clip` — 明确5秒时长
- `smooth camera movement` — 镜头平滑

每张图生成 **5秒** 视频，批量处理（8段 × 5秒 = 40秒完整展示）。

---

## Step 5：拼接视频

检查 ffmpeg 是否可用：
```bash
which ffmpeg || ls /workspace/skills/fashion-showcase/ffmpeg
```

**如果 FFmpeg 可用：** 拼接为单个 `final.mp4`
```bash
cd /workspace/skills/fashion-showcase
./ffmpeg -y \
  -f concat -safe 0 -i <(for f in video_*.mp4; do echo "file '$PWD/$f'"; done) \
  -c:v libx264 -preset fast -crf 23 \
  -vf "scale=768:1024:force_original_aspect_ratio=decrease,pad=768:1024:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:a aac -b:a 128k \
  final.mp4
```

**如果 FFmpeg 不可用：** 按顺序发送所有视频文件，每个视频单独发一条消息

---

## Step 6：发送最终视频

CDN 上传 → `message(media=CDN_URL, caption="...")` 发送最终视频。

附说明：`🎉 服装展示视频已完成！共8段，约40秒。`

---

## 状态文件格式（state.json）

```json
{
  "stage": "idle",
  "ref_prompt": "",
  "clothing_desc": "",
  "ref_analyzed": false,
  "clothing_analyzed": false,
  "ref_path": "",
  "clothing_path": "",
  "tryon_images": [],
  "variation_images": [],
  "selected_tryon": ""
}
```

每个新流程开始前，将 `stage` 重置为 `idle`，其他字段清空。

---

## 错误处理

| 错误情况 | 处理方式 |
|---------|---------|
| 图片超过10MB | 提示用户压缩图片后重试 |
| 视频生成部分失败 | 拼接所有成功生成的视频，跳过失败的 |
| FFmpeg 不可用 | 直接发送单个视频文件 |
| 状态文件丢失 | 引导用户重新上传图片 |
| CDN 上传失败 | 重试一次，仍失败则发本地文件路径碰运气 |
| 两次图片类型相同（两张都是参考图或都是服装图） | 提示用户："检测到两张图片都是 [X]，请补充一张 [Y] 图" |

---

## 核心经验总结（已验证）

1. **参考图不作为图片输入**，只提取文字场景/光线/氛围/性别；模特的脸/姿势/表情不进入生成 prompt
2. **服装图为唯一图片输入**（input_files），确保服装忠实于原款
3. **prompt 必须包含完整穿搭**（上装+裤子+鞋子），裤子鞋子越具体，AI 越容易输出完整全身构图
4. **构图硬约束五件套**：`FRONT VIEW` + `COMPLETE full body visible from top of head to toes` + `feet and shoes fully visible at bottom` + `3:4 portrait aspect ratio` + `No crop, no close-up`
5. **4张图变量**：脸型 + 发型发色 + 裤子款式 + 鞋子款式（其他元素完全一致）

---

## 一句话总结新流程

**收到图片 → 识别类型 → 提取对应提示词 → 存状态 → 等第二张 → 两张齐了自动生成试穿图 → 用户选择 → 裂变变体 → 确认 → 生成视频 → 拼接 → 发送完成。**
