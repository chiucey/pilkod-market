# 产线 A｜静态图去 AI 味

## 三招

| 招式 | 目的 | 策略 | 核心 |
|---|---|---|---|
| 1 不完美提示词 | 追求真实感和生活气息 | 反完美化：有意加入现实世界的缺陷和瑕疵，打破 AI 的理想化生成模式 | 聚焦结果的真实性 |
| 2 更详细的提示词 | 追求可控性和精准性 | 具体化：大量视觉细节（光线、材质、情绪）精确引导画面 | 聚焦过程的精准控制 |
| 3 增加随机词 | 追求灵感和意外惊喜 | 启发式：随机组合不相关的词，激发模型未知的连接和表现力 | 聚焦探索和创造性 |

**用法**：三招叠加，不是三选一。招 1 打底（去 AI 味主力），招 2 补精度，招 3 收尾。

---

## 招 1｜不完美清单

让画面像"真实世界"中随手拍下的一张照片，而不是精心雕琢的艺术品。

### ⚠️ 实战有效性分级（实测结论，必读）

清单里的项**不是都同样有效**。实测三张街拍（2400×1792 高分辨率）后的结论：

| 有效性 | 类别 | 举例 | 实测表现 |
|---|---|---|---|
| ✅ **几乎必中** | **物理瑕疵** | 法令纹、抬头纹、老年斑、油光、晒斑、毛孔、衣服起皱、毛球、扣子错位、指甲缝的泥、卫衣污渍、松弛下垂 | 全部如实生成，且是加分项 |
| ⚠️ **时灵时不灵** | **物理化的成像缺陷** | 焦点不实（"没有对焦就按下了"）、画面切边（"肩膀被画框切掉一半"） | 写得越具体越有效，抽象写法无效 |
| ❌ **高分辨率下基本失效** | **抽象成像缺陷** | 噪点、颗粒感、模糊、欠曝、手持倾斜、低画质 | 分辨率一高就被模型的"干净"默认抹平 |

**结论：去 AI 味的主力是物理瑕疵，不是成像缺陷。**

选 3–5 项时，**至少 3 项来自"物理瑕疵"那一栏**。堆"颗粒感明显"这类词是浪费预算，不写物理细节才是真正的失职。

### 高分辨率反噬

分辨率越高，模型越倾向输出"干净"的图——物理瑕疵也会被连带抹平。实测中同一套物理细节提示词在 2K 下已经偏干净。

追求真实感时**主动降一档分辨率**，比多写三行提示词有用。

### 不完美的皮肤
毛孔 (pores)、凹凸感 (uneven texture)、黑眼圈 (dark circles)、痘痘 (acne)、雀斑 (freckles)、痣 (moles)、疤痕 (scars)、血丝 (visible veins/redness)、皱纹 (wrinkles)、法令纹 (nasolabial folds)、眼袋 (eye bags)、油光 (oily sheen)、干燥/起皮 (dry/flaky skin)

### 不完美的机位
手机拍的 (taken with a phone)、老旧相机 (taken with an old camera)、随手拍 (casual shot)、抓拍 (candid shot)、角度不佳中焦 (off-center composition)、距离太近/太远 (too close/too far)、低角度拍摄 (shot from a low angle)、高角度拍摄 (shot from a high angle)

### 不完美的照片
噪点 (noise)、颗粒感 (grain)、过度曝光 (overexposed)、模糊 (blurry)、没有构图 (no composition)、背景杂乱 (messy background)、欠曝/阴影太重 (underexposed/heavy shadows)、散光/光斑 (lens flare/light spots)、色彩失真 (color distortion)、饱和度过高/过低 (high/low saturation)、白平衡不准 (incorrect white balance)、焦点不实 (soft focus/out of focus)、镜头畸变 (lens distortion)

### 不完美的情绪与表情
略显疲惫 (tired)、正在思考 (pensive)、困惑 (confused)、紧张 (nervous)、尴尬的微笑 (awkward smile)、惊讶 (surprised)、正在说话 (in the middle of a sentence)、正在大笑以致眼睛眯成一条缝 (laughing with squinting eyes)

### 不完美的妆容
妆花了 (smudged makeup)、口红溢出 (lipstick outside the lines)、头发凌乱 (messy hair)、几根发丝垂下来 (stray strands of hair)、头发打结 (tangled hair)、头发被风吹乱 (wind-blown hair)、额前刘海黏在一起 (forehead bangs stuck together)

### 不完美的服饰
衣服起皱 (wrinkled clothes)、领口有点歪 (slightly askew collar)、衣服上有个小污点 (a small stain on the clothing)、肩带滑落 (a slipped strap)、佩戴的眼镜反光 (reflection on glasses)

---

## 破坏构图

**"没有构图""偏在左边三分之一"这类写法基本无效。** 模型有很强的构图先验，三次实测全部给出了规矩的人像构图。

要真的破坏，必须写成**物理上具体的意外**：

| 无效写法 | 有效写法 |
|---|---|
| 没有构图 | 相机没对焦就随手按下了，主体边缘是虚的 |
| 偏在左边三分之一 | 人物被画框边缘切掉一半肩膀 |
| 构图随意 | 前景有一根电线横穿画面 |
| 随手抓拍 | 快门按早了，人物刚要转头，动作卡在半途 |
| 画面随便 | 画面顶上有半个路人被切掉 |
| 手持轻微晃动 | 相机在走动中按下，地平线歪了 5 度 |

规律：**从"摄影师出了什么错"的角度写，而不是从"画面应该长什么样"的角度写。** 模型对"失误"的响应远强于对"风格"的响应。

---

## ⚠️ 中文文字死穴

**画面里只要出现中文，就会翻车。** 实测中告示牌、招牌上的中文全部是乱码字形，一眼假。

高发位置：招牌、菜单、路牌、书脊、报纸、门牌、广告牌、衣服印花、屏幕 UI、笔记本。

**三种处理方式：**

1. **构图避开** — 让人物占满画面，把文字区域挤出画框（实测的背影版天然避开了所有招牌）
2. **明确规避** — `招牌为空白或无可辨识文字`、`背景文字已虚化不可读`
3. **换无文字载体** — 需要真实街景时用室内、小巷深处、田野、特写

**实在需要文字就后期自己贴。** 提示词解决不了这个问题。

---

## 招 2｜详细化维度表

| 维度 | 中文提示词 | English Prompt |
|---|---|---|
| **场景（中国真实场景）** | 苏州湾公园、清河坊街、颐和园十七孔桥、清华大学正门、北京动物园入口、南京夫子庙步行街、上海豫园小吃街、西湖断桥、西安钟楼广场、天津五大道、重庆洪崖洞、丽江古城石桥、长城八达岭段、广州沙面街头 | Suzhou Bay Park, Qinghefang Street, Seventeen-Arch Bridge (Summer Palace), Tsinghua University Gate, Beijing Zoo Entrance, Nanjing Confucius Temple Pedestrian Street, Shanghai City God Temple Snack Street, Broken Bridge (West Lake), Kuanzhai Alley (Chengdu), Bell and Drum Tower Square (Xi'an), Five Great Avenues (Tianjin), Hongyadong (Chongqing), Lijiang Old Town Stone Bridge, Badaling Great Wall, Shamian Street (Guangzhou) |
| **细节描写（核心质感）** | 真实肤质、自然肤色、发丝飞扬、毛发清晰、嘴唇纹理、衣物褶皱、衣物褶皱、肩带压痕、指尖细节、光影层次分明、皮肤微光、表情细微肌肉变化 | Realistic skin texture, natural skin tone, flying hair strands, visible fine hair, lip texture, fabric wrinkles, shoulder strap marks, fingertip detail, layered light and shadow, skin highlights, subtle facial muscle changes |
| **动作** | 看向镜头、看后一侧、闭眼、踮起脚尖、回眸、伸懒腰、低头看手机、举手遮阳、单手插兜、双手插兜、双手抱胸、双臂交叉、双手捋头发、手捏脸、双手比剪刀手、手里拿相机、手里拿扇子、手里拿玩具熊、手捧咖啡、手拿狗绳、手里抱猫咪、自拍 | Looking at camera, looking to the side, eyes closed, tiptoeing, turning back glance, stretching, looking down at phone, shading eyes with hand, resting chin on hand, hands in pockets, arms crossed, squatting, holding cheeks with hands, making V-sign, holding a camera, holding a fan, holding a teddy bear, holding a coffee cup, holding a dog leash, holding a cat, taking a selfie |
| **动作预设库** | 嘟嘴+手捂嘴、踮脚+伸手拿东西、回眸+转头头发、眯眼+浅笑、双手剪刀手+吐舌头、单手拿手机+另一手插兜、伸懒腰+打哈欠、手托脸+发呆 | Pouting lips + covering mouth, tiptoeing + reaching out, turning back + twisting hair, squinting + soft smile, V-sign + sticking tongue out, holding phone in one hand + other hand in pocket, stretching + yawning, resting chin + daydreaming |
| **情绪** | 微笑、轻声笑、大笑、欲言又止、悲伤、眼神充满爱意、害羞、冷漠、俏皮、疲惫、惊讶、沉思、愤怒、温柔、期待、陶醉 | Smiling, soft laugh, laughing, hesitant to speak, sad, eyes full of love, shy, indifferent, playful, tired, surprised, thoughtful, angry, gentle, expectant, immersed |
| **衣服细节·上装** | 黑白条纹衫、白色T恤、格子衬衫、针织毛衣、吊带背心、宽松卫衣、牛仔夹克、皮夹克、西装外套、碎花连衣裙（上身部分） | Striped shirt, white T-shirt, plaid shirt, knitted sweater, tank top, oversized hoodie, denim jacket, leather jacket, blazer, floral dress (upper part) |
| **衣服细节·裤子/裙子** | 牛仔裤、百褶裙、半身长裙、运动裤、阔腿裤、紧身裤、短裤、工装裤、蕾丝裙 | Jeans, pleated skirt, midi skirt, sweatpants, wide-leg pants, leggings, shorts, cargo pants, lace skirt |
| **衣服细节·鞋子** | 运动鞋、帆布鞋、马丁靴、高跟鞋、凉鞋、拖鞋、长靴 | Sneakers, canvas shoes, combat boots, high heels, sandals, slippers, long boots |
| **衣服细节·帽子** | 遮阳帽、棒球帽、渔夫帽、贝雷帽、毛线帽 | Sun hat, baseball cap, bucket hat, beret, beanie |
| **衣服细节·饰品** | 金属无框眼镜、耳钉、项链、手链、发夹、丝巾、戒指 | Rimless metal glasses, earrings, necklace, bracelet, hairpin, scarf, ring |
| **光线运用** | 灰色侧光、伦勃朗光、强烈明暗对比、高反差效果、暗调氛围、黄金时刻光、日落余晖、昏暗街灯、霓虹灯光、月光冷光、窗外自然光、阴天柔光、逆光剪影、聚光灯、环境反光 | Grey side light, Rembrandt lighting, strong light-shadow contrast, high contrast effect, moody tone, golden hour light, sunset glow, dim streetlight, neon light, moonlight, natural window light, cloudy soft light, backlight silhouette, spotlight, reflective ambient light |

---

## 招 3｜随机词库（161 条）

**使用方法**：在原提示的结尾增加

> 以下一些可供参考的随机词汇：`<挑选>`

**铁律：词库是封闭的，只能从下面 161 条里挑，禁止自造。** 词库的价值在于"随机组合出意料之外的连接"，一旦允许自己编词，招 3 就退化成普通写作。词库覆盖不到的表达，说明情况，不要凑词。

按**风格标签**分组最实用——用户说"要写实的"或"要赛博的"，直接从对应组里抓。

### 写实（realistic）

- **表情/眼神**：smiling 微笑 · blinking 眨眼 · gazing 凝视 · posing 摆姿势
- **姿态**：tilting 倾斜
- **修饰**：gracefully 优雅地 · confidently 自信地
- **风格词**：lifelike 栩栩如生 · natural 自然的 · realistic 写实的
- **肤色**：blemished 有瑕疵的 · flushed 脸红的 · freckled 有雀斑的 · porcelain 瓷白的 · radiant 光彩照人的 · smooth 光滑的 · tanned 古铜色的 · taut 绷紧的 · textured 有纹理的 · wrinkled 有皱纹的
- **面部结构**：angular 有棱角的 · defined 清晰轮廓的 · rugged 粗犷的 · symmetrical 对称的
- **年龄**：aged 年老的 · youthful 年轻的
- **情绪**：alert 警觉的 · confident 自信的 · contemplative 沉思的 · expressive 表情丰富的 · focused 专注的 · serene 宁静的 · stern 严肃的
- **姿态类**：poised 镇定的
- **美学**：elegant 优雅的 · subtle 微妙的

### 梦幻（dreamy / fantasy）

- **光影动作**：glowing 发光 · shimmering 闪烁 · sparkling 闪耀
- **姿态动作**：floating 漂浮 · levitating 悬浮
- **修饰**：eerily 怪异地 · softly 柔和地
- **名词/风格**：fairytale 童话
- **风格词**：celestial 天体的 · ethereal 空灵的 · magical 魔幻的 · whimsical 异想天开的
- **氛围**：misty 朦胧的
- **肤色**：glowing 发光的 · translucent 半透明的
- **光影**：haloed 有光环的 · luminous 发光的 · radiant 光彩照人的 · soft-lit 柔光的
- **环境**：misty 朦胧的
- **美学**：haunting 萦绕心头的 · angelic 天使般的 · delicate 精致的 · dreamy 梦幻的 · ethereal 空灵的 · soft 柔和的
- **情绪**：dreamy 梦幻的 · enchanted 被施魔法的 · serene 宁静的
- **色彩**：iridescent 彩虹般的 · pastel 粉彩的

### 赛博（cyber / tech）

- **光影动作**：flickering 闪烁
- **技术动作**：decoding 解码 · glitching 故障中 · rendered 已渲染 · rendering 渲染 · scanning 扫描 · uploading 上传
- **修饰**：robotically 机械地
- **名词**：glitch 故障 · chrome 铬金属 · circuit 电路 · hologram 全息图 · neon 霓虹灯 · datastream 数据流 · firewall 防火墙 · interface 接口 · visor 面罩 · avatar 虚拟形象
- **风格词**：chrome 铬金属的 · pixelated 像素化的 · synthetic 合成的 · cybernetic 赛博风格的 · cyberpunk 赛博朋克的 · glitchy 故障感的 · robotic 机器人般的 · virtual 虚拟的 · neon 霓虹的
- **技术类**：augmented 增强现实的 · biometric 生物识别的 · encrypted 加密的 · holographic 全息的 · modulated 调制的
- **面部特征**：distorted 扭曲的
- **情绪**：corrupted 被腐化的

### 哥特（gothic）

- **表情**：crying 哭泣
- **修饰**：eerily 怪异地
- **风格词**：gothic 哥特风格的 · spectral 幽灵般的
- **氛围**：cryptic 神秘的 · eerie 怪异的 · mysterious 神秘的 · sinister 阴险的
- **肤色**：bloodless 无血色的 · cracked 裂开的 · pale 苍白的
- **光影**：shadowed 阴影笼罩的
- **面部结构**：hollow 空洞的
- **面部特征**：decayed 腐烂的 · gaunt 消瘦的 · hollow 凹陷的 · stitched 缝合的 · torn 撕裂的
- **配饰**：veiled 遮面的
- **情绪**：brooding 忧思的 · cursed 被诅咒的 · haunted 被困扰的 · lifeless 毫无生气的 · melancholic 忧郁的 · possessed 被附身的 · sorrowful 悲伤的
- **美学**：haunting 萦绕心头的

---

## 案例句式（43 个实测案例归纳）

### 句式 1｜简洁"XX 的日常 X 肖像"型
```
中国人的日常生活肖像，采用过度曝光的照片效果，高光区域过曝发白，以日常环境为背景，全身取景，呈现出抓拍摄影的风格。

Daily life portrait of Chinese person, overexposed photo effect, blown-out highlights, everyday environment background, full body shot, candid photography style
```
变体：`半身体像` / `带镜头畸变效果` / `面部带少许雀斑` / `头发略显凌乱` / `焦点略微模糊` / `穿着褪色、起皱且不平整的衣物` / `面部带有细微皱纹等自然衰老痕迹` / `一镜到底` / `画面略带呼吸感`

### 句式 2｜"一张抓拍的 XX 照片"长句型（最完整）
```
一张抓拍的冬日街头照片：一位亚洲人穿着厚重的羽绒服，衣物显得略为宽大臃肿，袖子和衣摆处有不均匀的褶皱。外套颜色普通，搭配随意甚至有些 mismatched（风格混搭），显然未经精心打理。自然的肌肤纹理、略微凌乱的发丝，脸上带着放松的神情。昏暗且不均匀的街道灯光，投射到冬日街坊那些真实而随性的瞬间。

a candid winter street photo of an Asian person wearing a bulky down jacket, the clothing looking slightly oversized and puffy with uneven creases on the sleeves and hem. The jacket color is ordinary with casual mismatched style, not carefully styled. Natural skin texture, slightly messy hair, relaxed expression. Dim and uneven street lighting, raw and realistic documentary style.
```

### 句式 3｜"情绪反差"型
```
一张在客厅里抓拍的照片：一位亚洲人调皮地抿着嘴在玩耍。那种神情带着幽默与逗趣，并非真的动怒。自然的肌肤纹理。带着褶皱的休闲衣着，还有微乱的发丝，在温暖却不均匀的室内光线下，以未经修饰、轻松随意的纪实风格，定格下这一充满生活气息的瞬间。

a candid photo in a living room of an Asian person pursing lips in a playful way, pretending to be angry. The expression looks humorous and teasing rather than truly upset. Natural skin texture, casual wrinkled clothing, slightly messy hair. Warm but uneven indoor lighting, raw, relaxed, and documentary style.
```

### 句式 4｜"偷拍抓拍"型
```
一张抓拍的城市街拍照片：一位亚洲人提着帆布袋，侧身快步走着，姿态放松而自然，眼神没有看向镜头，仿佛正在想别的事情。

a candid street photo of an Asian person with a canvas bag, walking briskly, relaxed posture, eyes not looking at the camera, as if thinking of something else.
```

### 句式 5｜"环境光不完美"型
```
一张抓拍的夜晚市集照片：一对亚洲情侣正沉浸在进食中，嘴角沾着食物，眼神不经意地瞥向侧面，神情自然而随意。背景灯光繁杂无序，画面略带过曝，两人衣物上的褶皱清晰可见，整体呈现出未经修饰、带着不完美感的纪实风格。

a candid night market photo of an Asian couple caught in the middle of eating, with food on the mouth and eyes glancing sideways, natural casual expressions. Background lights cluttered, image slightly overexposed, wrinkled clothing, raw and imperfect documentary style.
```

---

## 负面提示词（人物 / 写实类必给）

正向提示词写得再细，模型默认倾向仍是"棚拍 + 磨皮 + HDR + 完美对称"。负面提示词是把这些默认值显式关掉的唯一手段。

### 通用去 AI 味负面词

```
professional photoshoot, studio lighting, softbox, rim light, golden hour glow,
dramatic shadows, beauty retouching, flawless skin, airbrushed, porcelain skin,
perfect teeth, bokeh, shallow depth of field, f/1.4, cinematic color grading,
teal and orange, HDR, oversaturated, extreme sharpness, razor edge hair strands,
symmetry, centered composition
```

### 画质 / 人体缺陷词

```
watermark, text, logo, extra fingers, deformed hands, distorted face,
low resolution, AI artifact
```

### 塑料感终结词

```
uncanny valley, wax figure, plastic skin, mannequin, 3D render, CGI, anime, illustration
```

### 构图建议

随手拍构图比例用 **4:3 或 3:2**，避开 1:1 和 16:9 的人像中心构图。主体别放正中，偏一点更好。

想躲脸部崩坏时，改用**背影、远景、手部特写**等非正脸主体——AI 最容易崩的是五官。

### ⚠️ 负面词会跟目标风格打架

上面那份通用负面词是按**去 AI 味的随手拍**配的，直接套到影视感画面上会自相矛盾。

| 负面词 | 跟谁打架 | 怎么办 |
|---|---|---|
| `bokeh` / `shallow depth of field` / `f/1.4` | 影视感的浅景深定调 | 删掉，只保留磨皮/棚拍/对称那批 |
| `teal and orange` / `cinematic color grading` | 冷暖对比的电影调色 | 删掉 |
| `golden hour glow` / `dramatic shadows` | 恢弘感封面的大片光影 | 删掉 |
| `centered composition` | 主体宏大（占画面中心） | 删掉 |

**通用做法**：负面词表按目标风格**裁剪后再给**，不要整份照抄。做影视感/恢弘感时，只保留 `studio lighting`、`beauty retouching`、`flawless skin`、`airbrushed`、`porcelain skin`、`symmetry`、`watermark`、`extra fingers`、`deformed hands`、`distorted face`、`uncanny valley`、`plastic skin` 这一批。

**视频类额外必盯**：`distorted face` 和 `deformed hands`——动作模型最容易崩的两项，绝不能删。

---

## 常见误区

| 误区 | 后果 | 正确做法 |
|---|---|---|
| 堆 `8K / best quality / masterpiece` | **加重** AI 味 | 去 AI 味靠具体名词：毛孔、法令纹、掉漆 |
| 写"高质量、精美、震撼人心" | 模型无从下手 | 换成可拍摄的具体描述 |
| 人物配 studio 棚拍/纯色渐变背景 | 塑料感来源 | 一律用 `everyday environment background` |
| 只写"完美、自然" | 触发模型的理想化模式 | 反着写：写褶皱、写不均匀、写未修饰 |
| 视频提示词里写静态缺陷词 | 模型执行成诡异变形 | 视频只用动态/氛围层词，见 SKILL.md §B |
| 把不完美项全押在"噪点/颗粒/模糊"上 | 高分辨率下一条都不生效 | 至少 3 项选物理瑕疵，见上方有效性分级 |
| 追求真实感却拉满分辨率 | 越清晰越假 | 主动降一档，2K 通常偏干净 |
| 写"没有构图""构图随意" | 模型照给标准人像构图 | 写摄影师的具体失误，见"破坏构图" |
| 画面里有中文招牌/路牌/报纸 | 必出乱码字形 | 构图避开 / 明确写不可读 / 后期自己贴 |
