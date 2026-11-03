# 漫画生成器 - 使用示例

## 示例1：简单故事

**用户输入：** `帮我画一个漫画：小猫迷路了，被好心人带回家`

**AI 处理流程：**

1. 拆分为 4 个分镜（2×2布局）
2. 为每个分镜生成提示词（manga style, black and white）
3. 调用 `image_gen` 生成4张面板图片
4. 使用 `compose_comic.py` 合成漫画页面
5. 输出最终漫画图片

---

## 示例2：多格漫画

**用户输入：** `把这个故事画成6格漫画：勇士战胜恶龙，拯救了公主`

**分镜规划：** 6个面板（3×2布局）

**风格选项：**
- 日系：manga style, epic fantasy
- 欧美：comic book style, bold outlines
- 水彩：watercolor illustration, soft edges

---

## 示例3：指定风格

**用户输入：** `用赛博朋克风格画一个关于AI觉醒的4格漫画`

**风格前缀：** `cyberpunk manga style, neon lights, dark background`

---

## 提示词生成规则

每个面板的提示词 = **风格前缀 + 场景描述 + 角色描述 + 氛围描述**

**示例：**
```
manga style, black and white, screentone,
a warrior standing before a dragon, holding a glowing sword,
epic atmosphere, dramatic lighting, comic panel
```
