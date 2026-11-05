---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7cb37a28e842b954ad1c336014828b2b
    PropagateID: 7cb37a28e842b954ad1c336014828b2b
    ReservedCode1: 3045022100ae94d87ceb2928b527ae6981f54191c0e3c98059fa91ef4669b423d8600b557002206fc02c70fb1eb977cb90dde82cbceeedab85682505ce70acb6c2f6743e890e5d
    ReservedCode2: 30440220049fc6948466187bd7dcb283799dcc117c95265dcde79a7ba6f8e43d8e4e90ef022068b913898e82f3c4529a102cd06f9bfda8b328478c0557760a17c88c1bf72cdf
description: 将亚马逊产品图片重新设计为其他平台版本，保留产品主体与文案，换上简约北欧风格背景与场景。适用场景：同一产品多平台图片适配、亚马逊图组复用、独立站/TikTok Shop/Temu 等平台素材准备。触发条件：用户上传产品图片并要求"重新设计"、"换个风格"、"适配其他平台"、每套生成多版本变体。
name: ecommerce-image-adapter
---

# ecommerce-image-adapter

将一套亚马逊产品图片转换为同产品、多风格的北欧简约版本输出。

---

## 核心原则（先理解，再执行）

**已有图像参考时，product 必须与原图完全一致。** image_synthesize 的 input_files 是强参考 —— 产品本身必须从原图来，不允许 AI 自行发挥生成相似产品。

常见错误：只描述产品特征（"deep gray plush sofa bed"）让 AI 自行想象 → 产品会走样。
正确做法：**直接以原图作为 input_files，在 prompt 中强调"only change background, product stays exact"**。

---

## 工作流程

每套图片（通常 6-10 张）→ 生成 3 套北欧风格变体（Set A / Set B / Set C）。

---

## Step 1：分析原图（每张必做）

对套内**每张原图**依次执行 `images_understand`，提取以下信息：

```
产品类型：
产品颜色（色号/色值）：
产品主体形状/轮廓：
图中包含的文字内容（逐字识别，含位置）：
产品角度（正面/侧面/斜拍/俯视）：
光照方向与色温：
面料/材质质感细节：
```

记录以上信息，后续生成时随提示词一并传入。

---

## Step 2：为每张图单独生成，保留产品一致性

**每张原图单独调用 `image_synthesize`**，不要一次性批量生成多张。

### 提示词结构（严格按此填写）

```text
原始图片：[reference image — 产品主体必须以此图为基准，不得自行发挥]

提示词：
"Replace the background with [精确场景描述]. Keep the foreground product 100% identical — same object, same angle, same proportions, same color, same fabric texture, same stitching details, same brand tag, copy-paste the product from the reference image with zero modifications. Maintain the same product placement in frame. Light from [原图光源方向]. ultra-realistic, [分辨率], warm neutral white tone."

要保留的文字内容（逐字保留，不得有任何偏差）：
[逐字抄录原图所有文字]
```

### 场景差异化设计（3套之间必须有明显差异）

| 套别 | 场景关键词 | 光线 | 背景色彩 |
|------|-----------|------|---------|
| Set A | 纯色浅灰亚麻背景 + 绿植 | 柔和侧光，左侧窗户 | 浅灰/米白 |
| Set B | 北欧客厅角落，木质边几 + 抽象画，白墙 | 窗边自然光 | 浅白/原木 |
| Set C | 纺织品家居风，亚麻布 + 羊毛毯，浅木地板 | 散射柔光 | 暖白/燕麦色 |

### 排版差异化（核心改进点）

**原图的排版构图必须被主动打破。** 生成前对比原图构图，按以下规则差异化：

| 原图特点 | Set A 做法 | Set B 做法 | Set C 做法 |
|---------|-----------|-----------|-----------|
| 产品居中 | 移至画面左侧 1/3 处 | 移至画面右侧 1/3 处 | 保留居中但放大特写 |
| 单一产品 | 加入北欧绿植点缀 | 加入家居饰品（蜡烛/画框） | 加入同色系布料/抱枕 |
| 剖面图/特写 | 改为等比例生活场景 | 改为远景展示全貌 | 改为侧面角度 |
| 组合拼图布局 | 改为单产品全屏 | 改为双联场景 | 改为对角线构图 |
| 文字在上方 | 移至左下角 | 移至右下角 | 改为环绕文字排版 |

**每套的构图角度不得与原图相同。** 若原图是 45° 斜侧角，Set A 保持 45°（换背景），Set B 改为正面或正侧，Set C 改为俯视或低角度。

---

## Step 3：质量检查（生成后必做）

每张生成后，用 `images_understand` 对比检查：

1. **产品一致性**：产品形状、颜色、品牌标签是否与原图完全一致
2. **文案准确性**：文字内容、拼写、位置是否与原图逐字一致
3. **排版差异**：构图是否与原图有明显不同

若任何一项不符，**立即重新生成**，不得跳过。

---

## Step 4：输出

- 文件命名：`[产品名]_Set[A/B/C]_[原图编号].jpg`
- 按套别存放于独立文件夹
- 交付时说明每套的构图差异

---

## ⚠️ 关键约束（绝对不得违反）

1. **产品主体零改动**：通过 input_files 强参考实现，prompt 中重申"copy-paste product with zero modifications"
2. **文案逐字保留**：位置偏差仅限于排版差异化允许的范围，内容、大小、颜色必须一致
3. **排版必须差异化**：3 套之间以及与原图之间构图不得雷同
4. **背景原创性**：不得使用原图背景，基于北欧风格重新设计
5. **尺寸匹配**：输出宽高比与原图一致，分辨率不低于 2K
