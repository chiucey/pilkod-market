# 医学插画风格指南

## 推荐风格优先级

| 优先级 | 风格名 | 适用场景 | 关键 Prompt 词 |
|--------|--------|---------|--------------|
| ⭐ 首选 | **Flat Medical** | 几乎所有科普场景 | `flat medical illustration, clean white background` |
| ⭐ 次选 | **Medical Infographic** | 数据/统计类 | `medical infographic, minimalist style` |
| 备选 | **Cartoon Friendly** | 面向儿童/大众 | `medical cartoon, friendly colorful` |
| 备选 | **Anatomical Diagram** | 解剖/机制类 | `anatomical diagram, clean line art` |

---

## 各系统医学 Prompt 模板

### 🧠 神经系统

```
Flat medical illustration, clean white background,
nervous system cross-section showing brain and neural pathways,
anatomical precision, soft pastel colors,
highlighted nerve signal pathways with subtle glow,
no text, educational science style
```

**适用场景**：神经传递、脑区功能、阿尔茨海默病、帕金森病

---

### ❤️ 心血管系统

```
Flat medical illustration, clean white background,
anatomically accurate heart cross-section with labeled chambers,
soft red and blue color coding for oxygenated/deoxygenated blood,
medical diagram style, modern healthcare design,
no text, educational clarity
```

**适用场景**：心肌梗死、高血压、心律失常、先天性心脏病

---

### 🫁 呼吸系统

```
Flat medical illustration, clean white background,
detailed lung anatomy with bronchi and alveoli structure,
soft blue and pink color scheme, modern healthcare style,
alveoli close-up with gas exchange diagram overlay,
no text, anatomical precision
```

**适用场景**：哮喘、COPD、肺炎、肺栓塞

---

### 🧬 代谢/内分泌系统

```
Flat medical illustration, clean white background,
endocrine system overview showing gland locations,
hormone molecule icons with directional arrows,
soft pastel palette, modern infographic style,
no text, scientific clarity
```

**适用场景**：糖尿病、甲状腺疾病、骨质疏松

---

### 🦴 肌肉骨骼系统

```
Flat medical illustration, clean white background,
joint cross-section showing cartilage and surrounding structures,
muscle fiber arrangement diagram,
soft warm color palette, anatomical diagram style,
no text, educational clarity
```

**适用场景**：骨关节炎、骨质疏松、椎间盘突出

---

### 🧫 免疫系统

```
Flat medical illustration, clean white background,
immune cell landscape with macrophages and lymphocytes,
antibody-y shaped molecules, virus/bacteria antigens,
soft colorful immune cells, educational science style,
no text, clean modern healthcare design
```

**适用场景**：自身免疫病、疫苗原理、过敏、COVID-19

---

### 🧪 肿瘤/细胞

```
Flat medical illustration, clean white background,
cancer cell vs normal cell comparison diagram,
cell division phases shown clearly,
color-coded: red for cancer cells, green for immune cells,
modern healthcare infographic style, no text
```

**适用场景**：癌症机制、靶向治疗、免疫治疗

---

## 负面提示词（避免）

以下词语会降低图像质量，**禁止使用**：

| ❌ 避免 | ✅ 替换为 |
|--------|-----------|
| `realistic anatomy` | `flat illustration, anatomical diagram` |
| `photorealistic` | `clean white background, infographic` |
| `comic style` | `medical cartoon, friendly colorful` |
| `blood and gore` | `clean symbolic representation` |
| `surgery photo` | `surgical procedure illustration` |
| `medical horror` | `hopeful treatment illustration` |

---

## 图像比例与分辨率

| 用途 | 比例 | 分辨率 | 备注 |
|------|------|--------|------|
| AI视频片段源图 | **16:9** | 1K（1024×576）足够 | 避免2K浪费token |
| 封面/缩略图 | 1:1 或 16:9 | 1K | 可单独生成2K版 |
| 信息图全尺寸 | 16:9 | 2K | 用于分步骤解说 |

---

## 动画指令参考

### 视频生成 Prompt 指南

**✅ 推荐动作**（AI视频稳定）：
- `smooth zoom in` — 推进效果，聚焦重点
- `gentle fade in / fade out` — 场景过渡
- `slow pan left to right` — 水平扫视
- `subtle breathing effect` — 呼吸感
- `highlight pulse effect` — 高亮闪烁

**⚠️ 谨慎使用**（可能失真）：
- `camera rotation` — 旋转镜头
- `morphing` — 变形效果
- `complex particle effects` — 复杂粒子

**❌ 避免**（AI视频限制）：
- `realistic face animation` — 真人面部动画
- `hand animation` — 手部动画
- `full body movement` — 全身运动

---

## 色彩方案参考

| 主题类型 | 推荐配色 |
|---------|---------|
| 心血管/血液 | `#E74C3C`红 + `#3498DB`蓝 + 白色背景 |
| 神经/大脑 | `#9B59B6`紫 + `#F39C12`橙 + 白色背景 |
| 代谢/内分泌 | `#27AE60`绿 + `#E67E22`橙 + 白色背景 |
| 免疫/感染 | `#3498DB`蓝 + `#1ABC9C`青 + 白色背景 |
| 肿瘤/癌症 | `#E74C3C`红 + `#95A5A6`灰 + 白色背景 |
| 骨骼/关节 | `#ECF0F1`浅灰 + `#E67E22`橙 + 白色背景 |

---

## 受众语气对应

| 受众 | 画面复杂度 | 术语密度 | 语调 |
|------|-----------|---------|------|
| 大众（默认） | 简单直观 | 无专业术语 | 温暖、鼓励 |
| 医学生 | 中等解剖细节 | 允许专业术语 | 严谨清晰 |
| 患者 | 温和图示 | 简单解释 | 同理、给予希望 |
