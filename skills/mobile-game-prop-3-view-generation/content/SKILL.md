---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c97d697bcd4b8c6f32a93b9874fbbbcd
    PropagateID: c97d697bcd4b8c6f32a93b9874fbbbcd
    ReservedCode1: 3046022100b57fd53c49fe578ddce5ce4296a1599d70d3fdcb645d64bddf422f7cb6f82c0b022100f7c0f7af4d6481d607d3fb50e72460f07aea0fe7a962dbbc788bf56f1e91dca9
    ReservedCode2: 3044022033b3e881248ca7d4cceeac5efab4d6cccac8c9254d5464ef88d7c713b748223b0220522ca25ba3711314dde4afa9be8628680e83d763a30301253a3aaf71db177d32
description: 生成手游风格低面道具三视角展示图，适用于手机游戏道具概念设计与建模参考。当用户要求生成游戏道具三视图、设计手游装备或武器展示图时使用。
name: mobile-game-prop-3-view-generation
---

## 任务说明

生成手游风格低面道具三视角展示图，适用于手机游戏道具概念设计与建模参考。

## 执行步骤

1. 理解用户描述的道具类型（武器、防具、装备等），若描述模糊则询问具体造型方向。
2. 若用户提供参考图，将其作为内容参考；若无，根据道具类型自行设计造型，遵循以下规范：
   - 造型饱满厚实，不能显得单薄
   - 现代/军事/战术风格优先
   - 功能配件要有（弹夹、把手、配件等），但不堆砌
3. 使用 image_synthesize 生成图像，参数规范如下：
   - edit_mode: style-transfer
   - aspect_ratio: 21:9
   - image_size: 2K
   - 风格参考图（style source）固定使用：https://ribbi.ai/api/v1/files/aba5de23960b400f.png
4. Prompt 构建规范：
   - 布局：三视角横向排列（左前45° + 中间正侧视 + 右后45°）
   - 背景：纯白色
   - 主色：军绿色 + 深灰色
   - 点缀色：橙色（用于弹鼓边缘、扳机、警示条、散热环等细节）
   - 建模规范：quad-face low poly only，圆柱/弧面区域给平滑着色过渡，平整面保持硬边，坚决不出三角面和杂乱法线
   - 比例：造型饱满厚实，手机端道具风格
5. 生成后展示图像，询问用户是否需要调整造型、配色、配件或视角。

## Prompt 模板

"Strictly adhere to the provided style reference image shading rules: cylindrical and curved surfaces use smooth shading with clean transitions (NO triangle face artifacts), flat panels use hard-edge flat shading. All geometry must look like clean quad-face low poly modeling only. Create a [道具描述]: [造型特征]. Thick and voluminous proportions. Three-angle horizontal layout: left front 45 degree, center pure side view, right back 45 degree. Military olive green and dark grey as dominant colors, vivid orange accent on [适合点缀的部位]. Pure white background, 21:9 composition. Mobile game prop asset style."

## 默认值

- 无参考图时默认军事/战术风格
- 默认比例 21:9
- 默认尺寸 2K
- 默认配色：军绿+深灰+橙色点缀
