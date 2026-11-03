# 完整战斗场景制作示例

## 场景概述

| 项目 | 内容 |
|------|------|
| 场景编号 | Battle_Scene_03 |
| 时长 | 15秒（450帧@30fps） |
| 情绪曲线 | 5 → 10（压抑→爆发→胜利） |
| 核心事件 | 主角觉醒新形态，释放终极技能击败Boss |

---

## 分镜脚本

### SHOT 01：蓄力时刻（00:00 - 00:03）

**基础信息**
| 参数 | 数值 |
|------|------|
| 景别 | 全景 → 中景（推） |
| 时长 | 3秒（90帧） |
| 运镜 | 缓慢推进 |

**画面内容**
```
主角单膝跪地，双手按在地面。
胸口发出微弱蓝光，能量开始聚集。
周围地面出现裂痕，碎石开始漂浮。
Boss得意地站在远处。
```

**角色动态**
| 角色 | 动态描述 |
|------|---------|
| 主角 | 膝盖下沉、重心降低、手掌按压地面 |
| 呼吸 | 越来越急促（每0.5秒→每0.3秒） |
| 能量 | 从胸口微弱光芒→扩散至全身 |
| Boss | 叉腰站立、嘲讽表情、脚步悠闲 |

**场景灵动**
```
• 地面裂痕缓慢扩大（0.5像素/帧）
• 碎石从地面升起（速度逐渐加快）
• 远处尘埃被气流扰动
• 背景建筑玻璃开始震颤
```

**AI生图提示词**
```
Anime warrior kneeling on cracked ground, hands pressed to earth, glowing blue energy emanating from chest, aura swirling around body, debris and rocks floating upward defying gravity, ground fractures spreading with light emanating from cracks, determined expression with eyes glowing blue, wind sweeping hair backward, dark ruins background with destroyed buildings, volumetric lighting with blue energy particles, dramatic chiaroscuro lighting, cinematic composition, 8K ultra-detailed, studio-quality illustration, intense emotional atmosphere, muscle tension visible through torn clothing, blue-white energy tendrils reaching toward sky
```

**AI生视频提示词**
```
Gradual energy buildup animation, blue light pulsing from chest increasing in intensity, hair swaying in energy wind, small debris particles rising slowly then accelerating, ground cracks spreading outward with light, character breathing heavily with visible strain, distant buildings trembling, dust particles disturbed by energy field, 3-second loop showing energy accumulation, subtle camera push-in, particle density increasing over time, dramatic lighting fluctuation, low-angle view emphasizing power buildup
```

**音效设计**
| 音效类型 | 描述 | 时序 |
|---------|------|------|
| 能量聚集 | 低频嗡鸣声（200Hz→800Hz渐变） | 持续+渐强 |
| 地面震动 | 闷雷般的轰隆声 | 持续 |
| 呼吸声 | 急促、用力 | 同步画面 |
| Boss | 轻蔑笑声（渐弱） | 持续 |

**运镜参数**
| 参数 | 起始值 | 结束值 |
|------|--------|--------|
| 景别 | 全景 | 中景 |
| 推进程度 | 0% | 70% |
| 光圈 | f/8 | f/4 |
| 背景虚化 | 无 | 轻微 |

**特效设计**
| 特效类型 | 参数 |
|---------|------|
| 能量粒子 | 密度20→100/帧，螺旋上升，#00BFFF→#FFFFFF |
| 地面裂痕 | 宽度2px→5px，#00BFFF，闪烁10Hz |
| 飘浮碎片 | 数量5→20个，大小5-30px，慢速旋转上升 |

---

### SHOT 02：觉醒爆发（00:03 - 00:05）

**基础信息**
| 参数 | 数值 |
|------|------|
| 景别 | 中景（全身） |
| 时长 | 2秒（60帧） |
| 运镜 | 快速推进 + 轻微环绕 |

**画面内容**
```
主角猛然站起，全身爆发出耀眼光芒。
金色与蓝色的能量交织成光环。
衣袍在能量冲击下碎裂，露出强化形态。
光芒冲天而起，照亮整个废墟。
```

**角色动态**
| 动作 | 帧数范围 | 描述 |
|------|---------|------|
| 站起 | 帧0-15 | 从跪姿→弓步站起 |
| 能量爆发 | 帧0-30 | 光环从身体向外扩散（3层） |
| 表情 | 帧15-25 | 紧闭双眼→猛然睁开（眼中金光） |
| 手部 | 帧10-30 | 双手张开→向上举起 |
| 衣袍 | 帧5-25 | 被能量撕裂（碎片向外飞扬） |

**场景灵动**
```
• 周围碎片全部被推离
• 地面再次剧烈震动
• Boss被冲击波推后几步
• 远处建筑开始坍塌
• 云层被光芒穿透
```

**AI生图提示词**
```
Epic anime warrior ascending with god-tier power, golden and blue energy swirling around body in double helix pattern, arms raised triumphantly to sky, torn clothing flying outward as new battle form revealed, muscular definition glowing with energy lines, intense light explosion emanating from character center, destroyed city ruins illuminated by divine radiance, dramatic silhouette backlit by overwhelming light source, shattered glass and debris frozen in air, energy tendrils connecting earth and sky, ultra-detailed muscular anime anatomy, perfect dynamic pose with cape-like energy trails, volumetric god rays piercing through clouds, cinematic color grading with warm gold and cool blue contrast, IMAX-quality composition, emotional intensity maximum
```

**AI生视频提示词**
```
Dramatic transformation sequence in 2 seconds, burst of light expanding from character, torn fabric pieces flying outward in all directions, energy rings pulsing outward in succession (3 rings, 200ms apart), hair blown upward with energy wind, particles suddenly frozen then released outward, camera shake effect (subtle), intensity building from 0 to 100%, slow-motion final moment, golden light flares at edges, debris suspended in mid-air by energy field, triumphant music swell, climactic moment capture
```

**音效设计**
| 音效 | 描述 |
|------|------|
| 觉醒音效 | 低频爆发 + 高频尖啸 |
| 能量冲击 | 轰鸣声从内部向外扩散 |
| 衣袍撕裂 | 布料撕裂声 |
| 背景音 | 远处爆炸声（建筑坍塌） |
| 配乐 | 主题曲高潮段落进入 |

**特效设计**
| 特效 | 参数 |
|------|------|
| 能量光环 | 内环：金色#FFD700半径0→150px / 中环：白色#FFFFFF半径0→200px / 外环：蓝色#00BFFF半径0→250px |
| 冲天光柱 | 宽度50px→200px，白金色渐变，瞬间延伸至画面外 |
| 粒子爆发 | 类型：能量球+光点，数量500+，轨迹：螺旋向外 |

---

### SHOT 03：终极一击（00:05 - 00:08）

**基础信息**
| 参数 | 数值 |
|------|------|
| 景别 | 特写 → 全景（爆炸） |
| 时长 | 3秒（90帧） |
| 运镜 | POV主观视角 → 客观全景 |

**画面内容**
```
主角双手推出，能量化作巨龙/巨拳/光束冲向Boss。
Boss惊恐地举起防御。
冲击波接触到Boss的瞬间，爆炸发生。
整个战场被白光吞没。
```

**角色动态**
| 角色 | 动作 |
|------|------|
| 主角 | 双手向前推出（掌心朝前） |
| 能量波 | 巨大能量形态从掌心涌出 |
| Boss | 双臂交叉防御，表情从嘲讽→惊恐 |
| 能量接触 | 冲击波包裹Boss |

**场景灵动**
```
• 能量波经过处，一切化为灰烬
• 冲击波引发连锁爆炸
• 碎片被卷入能量漩涡
• 地面被犁出一道沟壑
```

**AI生图提示词**
```
Anime warrior unleashing devastating ultimate attack, massive dragon made of blue-gold energy erupting from outstretched hands, dragon head charging forward with open jaws, terrified enemy desperately raising arms in defensive barrier, moment of impact with enemy, explosion of light and energy at point of contact, ground carved into deep trench by attack trajectory, chain reactions of smaller explosions, debris caught in swirling energy vortex, cinematic slow-motion impact moment, dragon scale texture on energy construct, perfect dynamic composition showing scale difference, destroyed battlefield illuminated by attack light, god-tier visual effects, 8K resolution, Unreal Engine quality, movie still composition
```

**AI生视频提示词**
```
Charging energy dragon animation, mouth opening wide as it launches forward, energy waves rippling through dragon body, dragon scales shimmering with light patterns, impact sequence with enemy barrier, barrier cracking under pressure, light explosion consuming entire frame, 3-second attack progression from hands to target, camera shake at moment of impact, particle debris swirling in energy vortex, ground destruction following attack path, slow-motion final impact frame, white flash covering screen at climax
```

**音效设计**
| 音效 | 描述 |
|------|------|
| 攻击释放 | 能量呼啸声（由远及近） |
| 巨龙咆哮 | 低音咆哮 + 电子音修饰 |
| 冲击声 | 巨大爆炸 + 低频轰鸣 |
| 防御崩溃 | 玻璃碎裂声 + 尖叫 |
| 配乐 | 最高潮段落，所有乐器齐鸣 |

**特效设计**
| 特效 | 参数 |
|------|------|
| 能量巨龙 | 长度：画面60%高度，细节：鳞片纹理、能量流动，眼睛：金色发光核心 |
| 冲击爆炸 | 核心：白色高亮(100%曝光)，火焰：橙红色向外扩散，烟尘：深灰色快速膨胀 |

---

### SHOT 04：尘埃落定（00:08 - 00:12）

**基础信息**
| 参数 | 数值 |
|------|------|
| 景别 | 全景 |
| 时长 | 4秒（120帧） |
| 运镜 | 环绕 → 后拉 |

**画面内容**
```
尘埃和烟雾缓缓散去。
Boss倒在地上，失去战斗力。
主角站在原地，气息平稳，但脸上有疲惫。
战斗结束，废墟恢复了寂静。
```

**角色动态**
| 角色 | 动作 |
|------|------|
| 主角 | 双手放下、重心微沉、微微喘息 |
| Boss | 倒地、失去意识、能量消失 |
| 主角表情 | 从坚定→微微放松→若有所思 |

**场景灵动**
```
• 烟尘缓慢下沉
• 碎片继续下落
• 远处火焰继续燃烧
• 微风吹过，带起一缕尘埃
```

**AI生图提示词**
```
Post-battle scene, victorious anime warrior standing amidst settling dust and smoke, former enemy collapsed on scorched ground defeated, exhausted but standing tall, subtle ash particles floating in air catching dim light, destroyed battlefield with craters and debris, distant fires still burning, dramatic contrast between character's inner peace and external devastation, thoughtful expression with slight weariness, calm wind sweeping hair, volumetric dust particles, cinematic muted color grading, emotional aftermath atmosphere, 8K detailed background, melancholic victory mood, perfect composition with destroyed beauty
```

**AI生视频提示词**
```
Slow-motion dust settling animation, smoke dissipating slowly revealing aftermath, ash particles floating downward at varying speeds, character's breathing returning to normal rhythm, distant small fires flickering, wind blowing dust across frame, 4-second contemplative sequence, subtle camera orbit, lighting shifting from harsh to soft as smoke clears, enemy lying motionless, atmosphere of exhaustion and relief, peaceful yet somber mood
```

**音效设计**
| 音效 | 描述 |
|------|------|
| 环境音 | 火焰噼啪、微风 |
| 呼吸声 | 恢复平稳 |
| 动作音 | 脚步轻微、衣物摩擦 |
| 配乐 | 高潮退场，转入柔和旋律 |

---

### SHOT 05：悬念结尾（00:12 - 00:15）

**基础信息**
| 参数 | 数值 |
|------|------|
| 景别 | 主角特写 → 大远景 |
| 时长 | 3秒（90帧） |
| 运镜 | 特写推进 → 快速后拉 |

**画面内容**
```
主角转身，看向远方。
远方天空中，新的敌人/危机正在逼近。
主角表情再次变得严肃。
画面淡出。
```

**角色动态**
| 动作 | 描述 |
|------|------|
| 转身 | 流畅的180度转身 |
| 视线 | 远望→凝视 |
| 表情 | 放松→警觉 |
| 手部 | 自然下垂→微微握拳 |

**场景灵动**
```
• 天空中的威胁云团/舰队
• 气流变化暗示新危机
• 背景角色开始骚动
```

**AI生图提示词**
```
Anime warrior turning to face new threat on horizon, determined warrior silhouette against ominous sky, distant approaching danger visible as dark mass or fleet, dramatic sky with swirling clouds suggesting incoming storm, cinematic panoramic composition, tension building in final frame, atmospheric perspective creating depth, color palette shifting from warm to cold (ominous), subtle fear in determined eyes, shoulders tensing as new threat approaches, epic cliffhanger ending composition, perfect framing for sequel setup, IMAX cinematic quality, ultra-detailed sky textures with dramatic lighting
```

**AI生视频提示词**
```
Character turning animation, cape/hair following momentum then settling, eyes shifting focus from ground to horizon, distant threat growing larger slowly, wind picking up intensity, atmosphere darkening at edges of frame, 3-second suspense build, camera doll in then pull back dramatically, music building to ominous tone, color grading cooling down, fade to black transition
```

**音效设计**
| 音效 | 描述 |
|------|------|
| 动作音 | 转身时衣物摩擦 |
| 环境音 | 风声加强 |
| 情绪音 | 低沉的不祥音调 |
| 配乐 | 悬疑主题旋律，淡入 |
| 结尾 | 低音重音暗示危机 |

---

## 完整时间轴汇总

| 时间码 | 镜头 | 核心内容 | 时长 | 情绪值 |
|-------|------|---------|------|--------|
| 00:00-00:03 | Shot 01 | 蓄力 | 3s | 5→7 |
| 00:03-00:05 | Shot 02 | 觉醒爆发 | 2s | 8→9 |
| 00:05-00:08 | Shot 03 | 终极一击 | 3s | 10 |
| 00:08-00:12 | Shot 04 | 尘埃落定 | 4s | 7→6 |
| 00:12-00:15 | Shot 05 | 悬念结尾 | 3s | 5→4 |

**总计**：15秒 = 450帧 @30fps

---

## 质量检查确认

- [x] 剧本情感曲线完整（5→10→6）
- [x] 场景分割清晰（5个镜头）
- [x] 每个场景有明确目标（蓄力→觉醒→释放→结果→悬念）
- [x] 角色动机明确（觉醒击败Boss）
- [x] 景别变化丰富（全/中/特写交替）
- [x] 运镜有目的性（推进/环绕/POV）
- [x] 动作连贯（起始→经过→结束）
- [x] 角色微动作丰富（呼吸/表情/姿态）
- [x] 场景灵动元素设计（尘埃/碎片/光线）
- [x] 生图提示词完整（风格+主体+姿态+环境+光线+氛围+技术）
- [x] 生视频提示词完整（动作+时间+特效+摄影）
- [x] 特效参数明确（时序/颜色/数值）
- [x] 音效配乐规划（前置/核心/余韵）
- [x] 时间轴精确到帧
- [x] 情感曲线有起伏
- [x] 有明确的开始和结束
- [x] 留有悬念（新的危机浮现）

---

# Seedream × Seedance 完整战斗场景示例（中文版）

## 场景概述

| 项目 | 内容 |
|------|------|
| 场景名称 | 绝境觉醒 - 主角释放究极之力 |
| 总时长 | 15秒（450帧@30fps） |
| 场景类型 | 战斗觉醒高潮 |
| 情绪曲线 | 压抑(3) → 转机(5) → 爆发(10) → 余韵(6) → 悬念(4) |

**剧情简介**：
主角被Boss逼入绝境，能量耗尽跪倒在地。Boss即将给出致命一击时，主角体内沉睡的力量觉醒。究极能量爆发，形态升华，释放终极技能击败Boss。战后，主角望向远方，新的威胁正在逼近...

---

## 逐秒分镜脚本

### SHOT 01：绝望跪地（00:00-00:01）

| 参数 | 数值 |
|------|------|
| 时间 | 00:00 - 00:01（1秒 = 30帧@30fps） |
| 景别 | 中景 |
| 运镜 | 固定镜头 |

**Seedream 4.5 提示词**：
```
"年轻男性武者单膝跪地重伤状态，
左手撑住地面支撑身体，右手捂住胸口伤口，
黑色战甲破碎露出内部伤痕，
血液从嘴角滴落在地，
眼神疲惫但依然燃烧不屈意志，
远处强大敌人居高临下俯视，
阴暗废墟战场背景，暴风雨前夕压抑氛围，
青色闪电在远处云层酝酿，
电影级构图，低角度仰视英雄，
8K细节，完美解剖结构，悲伤而坚定"
```

**Seedance 2.0 提示词**：
```
"角色跪地喘息，呼吸沉重而缓慢，
左手手指在碎石中微微抓地，
胸口伤口处渗出血液随心跳脉冲，
眼皮沉重但眼神始终盯着前方敌人，
嘴角血滴缓缓滑落，
1秒循环呼吸动画，
微风掠过扬起发丝，
远处敌人影子投射在地面逼近，
压抑沉重的氛围"
```

**参考图片**：
- [角色参考] 跪地姿态全身照
- [敌人参考] Boss威压姿态图
- [环境参考] 废墟战场氛围图

**音效**：
| 音效 | 描述 |
|------|------|
| 呼吸声 | 沉重、疲惫、每2秒一次 |
| 环境音 | 远处雷鸣低沉 |
| 心跳声 | BPM 50，衰弱但坚定 |
| 配乐 | 低沉弦乐，悲伤主旋律 |

**特效**：
| 特效 | 参数 |
|------|------|
| 光效 | 微弱的环境光 |
| 粒子 | 少量尘埃飘落 |
| 色调 | 低饱和青色冷调 |

---

### SHOT 02：力量觉醒（00:01-00:02）

| 参数 | 数值 |
|------|------|
| 时间 | 00:01 - 00:02（1秒 = 30帧@30fps） |
| 景别 | 特写 |
| 运镜 | 缓慢推进 |

**Seedream 4.5 提示词**：
```
"主角手按胸口核心处发出微光，
金色光点从心脏位置向外扩散渗透进伤痕，
双眼猛然睁开瞳孔绽放金色光芒，
表情从痛苦转变为坚定觉醒，
皮肤下的能量经脉发光可见如蓝色河流，
长发无风自动向上飘浮，
地面裂纹中渗出金色光能量，
周围尘埃被神秘力量托起悬浮，
神圣觉醒时刻，救世主降临感，
戏剧性聚光照亮主体，橙金色光芒，
最高质量，史诗级神圣感"
```

**Seedance 2.0 提示词**：
```
"胸口核心光芒从微弱变强烈脉冲，
金色光能量沿经脉扩散渗透全身，
双眼睁开瞬间瞳孔爆发金光，
发丝开始无风自动向上飘浮，
地面裂纹渗出金色光芒逐渐扩大，
身体周围尘埃开始悬浮旋转，
能量光粒子如星尘环绕身体，
皮肤下的经脉发出可见蓝光，
2秒觉醒能量积聚动画，
镜头缓慢推进聚焦面部表情变化，
光芒强度从30%到100%渐变"
```

**参考图片**：
- [角色参考] 能量觉醒面部特写
- [能量参考] 能量经脉扩散特效
- [姿态参考] 觉醒姿态参考图

**音效**：
| 音效 | 描述 |
|------|------|
| 觉醒音 | 低频到高频的能量涌动声 |
| 心脏音 | 心跳加速 BPM 50→80 |
| 能量音 | 神圣光能量嗡嗡声 |
| 配乐 | 圣歌吟唱渐入 |

**特效**：
| 特效 | 参数 |
|------|------|
| 能量光效 | 金色核心→全身经脉 |
| 粒子特效 | 星尘光点环绕 |
| 地面特效 | 裂纹发光扩散 |
| 色调 | 冷调→暖金色转变 |

---

### SHOT 03：究极变身（00:02-00:03）

| 参数 | 数值 |
|------|------|
| 时间 | 00:02 - 00:03（1秒 = 30帧@30fps） |
| 景别 | 全身全景 |
| 运镜 | 后拉+环绕 |

**Seedream 4.5 提示词**：
```
"究极形态完全觉醒的主角全身姿态，
金色与蓝色能量交织成完美双螺旋环绕全身，
破损战甲被神圣光芒重塑升级，
背后展开六翼金色能量翅膀，
手中凭空凝聚究极圣剑散发耀眼白光，
全身发光如小型太阳照亮周围废墟，
周围被能量冲击波推开的碎石悬浮，
脚下地面承受不住力量开始崩塌，
神圣与威严并存的完美战神形态，
电影级全身构图，史诗级胜利姿态，
最高质量，大师级作品，神级画质"
```

**Seedance 2.0 提示词**：
```
"能量从体内猛然爆发形成球形光罩，
破损战甲在光芒中重塑升级细节，
六翼金色能量翅膀从背后展开绽放，
能量光粒子如银河般环绕旋转，
手中能量凝聚成型的圣剑发光过程，
脚下地面承受不住力量开始龟裂下陷，
冲击波将周围碎石推开悬浮在空中，
头发被能量场向上吹拂形成飞散姿态，
1秒完整究极变身动画过程，
镜头后拉展示全身神圣形态，
光芒强度达到顶峰后稳定"
```

**参考图片**：
- [角色参考] 究极形态全身参考
- [翅膀参考] 能量翅膀参考图
- [武器参考] 圣剑特效参考
- [环境参考] 神圣光芒背景

**音效**：
| 音效 | 描述 |
|------|------|
| 变身音 | 能量爆发轰鸣 |
| 翅膀音 | 神圣翅膀展开声 |
| 环境音 | 空间扭曲震颤 |
| 配乐 | 交响乐高潮爆发 |

**特效**：
| 特效 | 参数 |
|------|------|
| 翅膀特效 | 六翼金色能量翼 |
| 武器特效 | 圣剑光芒 |
| 环境特效 | 地面崩塌、碎片悬浮 |
| 光效 | 神圣球形光罩 |

---

### SHOT 04：能量释放（00:03-00:05）

| 参数 | 数值 |
|------|------|
| 时间 | 00:03 - 00:05（2秒 = 60帧@30fps） |
| 景别 | 中景 → 特写（推） |
| 运镜 | 快速推进 |

**Seedream 4.5 提示词**：
```
"主角双手持剑向前方斩下，
金色剑光形成巨大月牙形态向前切割，
剑光所过之处空间都被撕裂，
能量如洪流从剑刃倾泻而出，
BOSS双手防御被剑光压迫后退，
背景空间产生裂缝碎片飘散，
光线从裂缝中照射进来，
史诗级终极斩击画面，
动态模糊效果表现速度，
最高质量，史诗级冲击力"
```

**Seedance 2.0 提示词**：
```
"双手握剑高举过顶准备斩下，
腿部发力身体旋转积蓄力量，
剑刃能量达到最大亮度，
斩击动作从右向左快速挥出，
剑光月牙向前切割飞行，
能量如洪水般从剑刃涌出，
BOSS被冲击波推得双脚向后滑动，
地面被犁出深沟裂痕，
空间裂缝从剑光边缘产生碎片，
空气被切割发出尖锐呼啸，
2秒完整斩击释放动画，
镜头跟随剑光快速推进"
```

**参考图片**：
- [角色参考] 斩击姿态全身
- [特效参考] 剑光斩击特效
- [BOSS参考] BOSS防御姿态

**音效**：
| 音效 | 描述 |
|------|------|
| 斩击音 | 空间撕裂轰鸣 |
| 能量音 | 洪流倾泻声 |
| 敌人音 | 防御崩溃惨叫 |
| 配乐 | 最高潮段落 |

**特效**：
| 特效 | 参数 |
|------|------|
| 剑光特效 | 巨大金色月牙斩击 |
| 冲击特效 | 能量洪流 |
| 环境特效 | 空间裂缝、地面裂痕 |
| 粒子特效 | 能量碎片飞散 |

---

### SHOT 05：冲击爆炸（00:05-00:08）

| 参数 | 数值 |
|------|------|
| 时间 | 00:05 - 00:08（3秒 = 90帧@30fps） |
| 景别 | 全景 → 特写 |
| 运镜 | 环绕 + 推进 |

**Seedream 4.5 提示词**：
```
"剑光命中BOSS的瞬间产生巨大爆炸，
白色核心向四面八方释放能量波，
橙红色火焰从爆炸中心翻涌，
黑色浓烟形成蘑菇云向上升腾，
BOSS被冲击波推飞出去，
碎片残骸被爆炸卷入旋转飞舞，
巨大能量球在空中悬浮，
地面被冲击出巨大陨石坑，
神圣与毁灭并存的壮观场景，
电影级爆炸场景，完美的破坏美学，
最高质量，史诗级视觉效果"
```

**Seedance 2.0 提示词**：
```
"剑光接触目标的瞬间闪光覆盖画面，
爆炸冲击波从接触点向外扩散，
火焰球体快速膨胀然后缓慢消散，
浓烟向上翻涌形成蘑菇云形态，
碎片残骸被冲击波抛向高空，
BOSS被冲击波击飞轨迹，
能量球在空中悬浮脉动，
地面陨石坑逐渐成型，
尘埃云向四面八方扩散，
3秒完整爆炸过程动画，
镜头环绕爆炸中心旋转拍摄，
最后定格在主角持剑站立的剪影"
```

**参考图片**：
- [爆炸参考] 蘑菇云爆炸场景
- [BOSS参考] BOSS被击飞姿态
- [环境参考] 陨石坑效果

**音效**：
| 音效 | 描述 |
|------|------|
| 爆炸音 | 巨大轰鸣声 |
| 火焰音 | 爆燃呼啸 |
| 敌人音 | BOSS惨叫回响 |
| 配乐 | 高潮持续 |

**特效**：
| 特效 | 参数 |
|------|------|
| 爆炸特效 | 能量球 + 火焰 + 浓烟 |
| 冲击特效 | 环形冲击波 |
| 环境特效 | 地面陨石坑 |
| 碎片特效 | 残骸飞散 |

---

### SHOT 06：战后余韵（00:08-00:11）

| 参数 | 数值 |
|------|------|
| 时间 | 00:08 - 00:11（3秒 = 90帧@30fps） |
| 景别 | 中景 |
| 运镜 | 缓慢环绕 |

**Seedream 4.5 提示词**：
```
"战斗结束后废墟恢复寂静，
主角单手拄剑支撑身体站立，
究极形态逐渐消退回归常态，
金色翅膀碎片般消散融入虚空，
全身覆盖汗水和尘土但神情坚定，
远处BOSS倒地失去战斗力，
夕阳从云层缝隙照射下来，
尘埃在光线中缓缓飘落，
胜利但疲惫的战士身影，
电影级余韵画面，情感丰富，
8K细节，完美的氛围营造"
```

**Seedance 2.0 提示词**：
```
"金色翅膀如碎片般逐渐消散，
能量形态慢慢从身体褪去，
单手拄剑支撑站立微微喘息，
呼吸从急促慢慢恢复平稳，
额头汗水顺脸颊滑落，
远处尘埃缓慢下落填充空间，
夕阳光芒穿透云层洒落大地，
环境逐渐从战斗混乱恢复平静，
3秒平息过渡动画，
镜头缓慢环绕展示战后景象，
配乐渐弱转为柔和旋律"
```

**参考图片**：
- [角色参考] 战后疲惫姿态
- [翅膀参考] 翅膀消散过程
- [环境参考] 夕阳废墟氛围

**音效**：
| 音效 | 描述 |
|------|------|
| 呼吸声 | 逐渐平稳 |
| 环境音 | 风声、尘埃落定声 |
| 配乐 | 高潮退场，柔和旋律 |
| 胜利音 | 低沉庄严的号角 |

**特效**：
| 特效 | 参数 |
|------|------|
| 翅膀消散 | 金色粒子飘散 |
| 环境光 | 夕阳穿透云层 |
| 粒子特效 | 尘埃下落 |
| 色调 | 暖色调夕阳余晖 |

---

### SHOT 07：新威胁降临（00:11-00:15）

| 参数 | 数值 |
|------|------|
| 时间 | 00:11 - 00:15（4秒 = 120帧@30fps） |
| 景别 | 特写 → 大远景 |
| 运镜 | 特写推进 → 快速后拉 |
| 转场 | 淡出 Fade to Black |

**Seedream 4.5 提示词**：
```
"主角转身望向远方地平线，
远方天空中黑色舰队正在逼近，
巨大阴影笼罩大地带来压迫感，
主角表情从疲惫转为严肃警觉，
手中圣剑再次发出微光响应，
预示着新的更大危机即将来临，
史诗级悬念结尾，完美的续集预告感，
电影级构图，远近对比强烈，
最高质量，史诗级氛围营造"
```

**Seedance 2.0 提示词**：
```
"角色转身动作流畅有力量，
头部转向远方地平线方向，
视线从地面缓慢抬升至天际，
表情从疲惫转为严肃紧绷，
远方黑色舰队逐渐放大逼近，
阴影逐渐覆盖整个画面，
环境中出现不祥预兆变化，
风向改变云层快速聚集，
4秒悬念建立动画，
镜头从面部特写推进，
然后快速后拉展示全景威胁"
```

**参考图片**：
- [角色参考] 转身凝视姿态
- [威胁参考] 黑色舰队场景
- [天空参考] 压迫云层背景

**音效**：
| 音效 | 描述 |
|------|------|
| 动作音 | 转身衣物摩擦声 |
| 环境音 | 风向改变呼啸声 |
| 不祥音 | 低沉不祥旋律 |
| 配乐 | 悬疑主题渐入 |

**特效**：
| 特效 | 参数 |
|------|------|
| 威胁特效 | 黑色舰队逼近 |
| 天空特效 | 压迫云层聚集 |
| 光效 | 阴影覆盖 |
| 色调 | 暖色→冷色调转变 |

---

## 完整时间轴汇总

### 15秒战斗觉醒场景 - 帧级时间轴

| 时间码 | 镜头 | 内容 | 景别 | 时长 | 帧数 |
|-------|------|------|------|------|------|
| 00:00 | Shot 01 | 绝望跪地 | 中景 | 1s | 30 |
| 00:01 | Shot 02 | 力量觉醒 | 特写 | 1s | 30 |
| 00:02 | Shot 03 | 究极变身 | 全景 | 1s | 30 |
| 00:03 | Shot 04 | 能量释放 | 中景 | 2s | 60 |
| 00:05 | Shot 05 | 命中爆发 | 全景 | 3s | 90 |
| 00:08 | Shot 06 | 战后余韵 | 中景 | 3s | 90 |
| 00:11 | Shot 07 | 新威胁降临 | 特写→远景 | 4s | 120 |

**总计**：15秒 = 450帧 @30fps

### 制作任务分配

| 阶段 | 任务 | 数量 |
|------|------|------|
| Seedream 4.5 生图 | 关键帧生成 | 7张 |
| Seedance 2.0 生视频 | 镜头生成 | 7段 |
| 后期合成 | 镜头拼接+音效+配乐 | 1项 |

---

## 角色一致性保持技巧

### 问题：同一角色在不同镜头中外观不一致

### 解决方案：全能参考模式设置

**第一步：建立角色参考库**
```
[CR-01] 角色基础形象（正面全身）
[CR-02] 角色侧面轮廓
[CR-03] 角色面部特写
[CR-04] 角色表情参考（平静/愤怒/悲伤）
[CR-05] 角色服装细节
```

**第二步：镜头生成时的参考选择**
| Shot | 参考选择 |
|------|---------|
| Shot 01（跪地） | CR-01 + CR-04（疲惫表情） |
| Shot 02（觉醒） | CR-01 + CR-03（眼睛特写） |
| Shot 03（变身） | CR-01 + 变身特效参考 |
| Shot 04（斩击） | CR-01 + 战斗姿态参考 |
| Shot 05（爆发） | CR-01 + 特效参考 |

**第三步：提示词强调**
添加："保持角色特征一致性，相同的发型瞳色服装"

---

## 复杂动作生成技巧

### 问题：连续动作不流畅，帧与帧之间跳跃

### 解决方案：动作分解参考法

**示例：完整挥拳动作**

**步骤1：生成3张分解参考图**
```
[MA-01] 预备姿势：拳头后拉至肩部
[MA-02] 击发姿势：拳头伸展至极限
[MA-03] 收势姿势：拳头收回腰间
```

**步骤2：Seedance 2.0 全能参考设置**
```
参考图片：[MA-01] + [MA-02] + [角色基础]
提示词："连贯完成从预备到击发到收势的完整挥拳动作，
        动作流畅有力有惯性跟随，
        3秒完成整个挥拳过程"
```

**步骤3：时间节点控制**
| 时间 | 动作 |
|------|------|
| 0-1秒 | 拳头后拉蓄力 |
| 1-2秒 | 拳头快速击出 |
| 2-3秒 | 拳头收回完成动作 |

---

## 质量检查确认（中文版）

- [x] 故事板完整，所有镜头已规划（7个镜头）
- [x] 每镜头有明确的Seedream提示词
- [x] 每镜头有明确的Seedance提示词
- [x] 角色参考图库已准备完整（5个角色参考）
- [x] 环境/风格参考图已准备
- [x] 时长和帧数计算正确（450帧@30fps）
- [x] 情感曲线设计合理（3→5→10→6→4）
- [x] 角色特征一致性（相同的发型瞳色服装）
- [x] 动作流畅无跳跃（动作分解参考法）
- [x] 微动作丰富（呼吸、眨眼、发丝）
- [x] 镜头运动符合设计
- [x] 环境动态有变化
- [x] 特效与动作同步
- [x] 音效与画面同步
- [x] 配乐情绪匹配
- [x] 转场自然合理（淡出 Fade to Black）
- [x] 留有悬念（新威胁降临）
