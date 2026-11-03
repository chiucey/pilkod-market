# 题材配置手册 (Genre Configuration Reference)

> **权威声明**: 本文件是类型配置的权威参考。
> 爽点模式定义见 excitement-engineering.md。节奏标准见 pacing-curve-reference.md。

> **来源：** novel-forge · vibe-noveling · AI-Practical-Lab/novel-writer | **版本：** 1.0 | **更新：** 2026-05-19

**题材不同，节奏不同。** 题材配置的本质是为每种类型的故事定义"正确的呼吸节奏"。配置优先级：题材配置 > 通用规则（Anti-AI规则和一致性规则除外，不受题材覆盖）。

每个题材包含四个配置模块：`hook_config`（钩子偏好）、`coolpoint_config`（爽点偏好）、`pacing_config`（节奏偏好）、`special_rules`（题材特殊约束）。

---

## 一、shuangwen（爽文/系统流）

**一句话定位：** 读者来看的就是"爽"——快速压抑、强力兑现、持续递进的快感循环。
**核心爽感来源：** 压抑-爆发的短周期循环，每次爆发都超越上一次。
**节奏红线：** 连续压抑不得超过3章，否则读者弃书。
**典型反模式：** 压抑过长、爽点兑现不足、系统设定过于复杂喧宾夺主。

```yaml
hook_config:
  preferred_types: [渴望钩, 选择钩]
  strength_baseline: strong
  chapter_end_requirement: "每章结尾必须有至少一个strong级别钩子"

coolpoint_config:
  preferred_patterns: [装逼打脸, 扮猪吃虎, 越级反杀, 反派翻车]
  density: high
  small_coolpoint_interval: 3
  combo_interval: 5
  milestone_interval: 15

pacing_config:
  stagnation_threshold: 3
  strand_max: 2
  transition_allowance: 1
  pressure_release_ratio: "压3扬7"

special_rules:
  - "系统面板/金手指在前3章内完成展示，后续只做增量更新"
  - "每个小爽点必须比上一次规模更大或形式更新颖（递进原则）"
  - "系统/金手指规则必须稳定，中后期不得擅自修改核心规则"
  - "配角群像服务于打脸场景：嘲讽者、震惊者、暗中看好者缺一不可"
```

---

## 二、xianxia（修仙/玄幻）

**一句话定位：** 以境界突破为骨架，以世界观扩展为血肉，以道心磨砺为灵魂。
**核心爽感来源：** 积累-突破的质变瞬间，以及突破后对新世界的探索。
**节奏红线：** 境界突破不能无铺垫无代价，否则爽感归零。
**典型反模式：** 突破像喝水、战斗全靠境界碾压无策略、世界观规则自相矛盾。

```yaml
hook_config:
  preferred_types: [危机钩, 渴望钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末钩子强度不低于moderate，关键节点必须strong"

coolpoint_config:
  preferred_patterns: [越级反杀, 装逼打脸, 扮猪吃虎]
  density: moderate
  small_coolpoint_interval: 5
  combo_interval: 10
  milestone_interval: 25

pacing_config:
  stagnation_threshold: 4
  strand_max: 3
  transition_allowance: 3
  pressure_release_ratio: "压5扬5"

special_rules:
  - "境界突破必须有：①铺垫（至少前3章积累暗示）②代价（体力/资源/时间/人情）③仪式感"
  - "每次大境界突破后，须有2-3章展示新能力/新视角/新世界"
  - "功法/法宝设定须建立清晰体系，天劫/瓶颈设定一旦建立后续必须遵守"
  - "师门/势力关系网每次扩展都须交代利害关系"
```

---

## 三、romance（言情/甜宠）

**一句话定位：** 读者要的是"心动"，不是"剧情"——每一次互动都应该是情感的推进。
**核心爽感来源：** 关系位移带来的甜蜜超预期，以及暧昧期的拉扯张力。
**节奏红线：** 主CP（Fire线）连续5章无互动或情感推进即触发警告。
**典型反模式：** 误会持续太久不澄清、配角抢戏超过主角、甜蜜场景平铺直叙。

```yaml
hook_config:
  preferred_types: [情绪钩, 渴望钩]
  strength_baseline: moderate
  chapter_end_requirement: "章末必须有情绪钩或关系悬念"

coolpoint_config:
  preferred_patterns: [甜蜜超预期, 装逼打脸, 反派翻车]
  density: moderate-high
  small_coolpoint_interval: 3
  combo_interval: 8
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 3
  fire_line_tolerance: 5
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压3扬7"

special_rules:
  - "每5章至少一次关系位移（好感度提升、误会化解、亲密升级、承诺递进）"
  - "误会必须有'说清楚'的真正障碍（外部环境/时机/自尊），而非角色变蠢"
  - "甜蜜场景必须写情绪反应，不能只写行为"
  - "配角感情线篇幅控制在主线的20%以内；分离/虐心段落须有终点预告"
```

---

## 四、mystery（悬疑/推理）

**一句话定位：** 真相是饵，逻辑是线——读者为解谜而来，为震撼而留。
**核心爽感来源：** 真相揭露时的"原来如此"，以及推理过程中的逻辑美感。
**节奏红线：** 线索投放和回收必须严格遵守逻辑一致性，任何矛盾都是致命伤。
**典型反模式：** 侦探靠直觉破案、关键线索读者完全看不到、反转靠机械降神。

```yaml
hook_config:
  preferred_types: [悬念钩]
  strength_baseline: strong
  chapter_end_requirement: "每章结尾必须留下至少一个未解答的疑问"

coolpoint_config:
  preferred_patterns: [越级反杀, 反派翻车]
  density: low
  small_coolpoint_interval: 5
  combo_interval: 10
  milestone_interval: 30

pacing_config:
  stagnation_threshold: 5
  strand_max: 4
  transition_allowance: 3
  pressure_release_ratio: "压7扬3"

special_rules:
  - "允许LOGIC_INTEGRITY覆盖其他规则——逻辑一致性是悬疑文的生命线"
  - "线索三层次投放：明线40%（读者可见）、暗线40%（隐藏于叙述中）、推理线20%"
  - "每次反转必须有至少一条先前铺设的伏笔支撑，禁止凭空反转"
  - "叙述者视角规则必须明确：全知不隐瞒、有限可隐瞒但须公平——公平叙述原则"
```

---

## 五、rules-mystery（规则怪谈）

**一句话定位：** 在规则中求生，在违反中死亡——恐惧来自"不知道哪条规则是真的"。
**核心爽感来源：** 发现规则漏洞的智力快感，以及从必死局面中找到生路的绝处逢生。
**节奏红线：** 停滞超过2章无新规则/新信息即读者流失。
**典型反模式：** 规则过于复杂读者跟不上、主角靠运气通关、恐怖感被削弱为普通冒险。

```yaml
hook_config:
  preferred_types: [危机钩, 悬念钩]
  strength_baseline: strong
  chapter_end_requirement: "章末必须有生死悬念或规则疑点"

coolpoint_config:
  preferred_patterns: [越级反杀, 反派翻车]
  density: moderate
  small_coolpoint_interval: 3
  combo_interval: 7
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 2
  strand_max: 3
  transition_allowance: 1
  pressure_release_ratio: "压6扬4"

special_rules:
  - "每次推进真相须绑定明确损失（队友死亡/道具消耗/信息代价/精神损伤）"
  - "规则必须逻辑自洽；允许假规则，但破绽须在揭露前有迹可循"
  - "恐怖氛围不可稀释：每2000字内至少一个'不对劲'的氛围信号"
  - "推理过程必须展示；死亡必须有分量，不能死完就忘"
```

---

## 六、urban-power（都市异能）

**一句话定位：** 在现代都市的日常表象下，隐藏着超凡的力量和更大的世界。
**核心爽感来源：** 超凡力量在日常场景中的展示，以及身份反差带来的双重快感。
**节奏红线：** 缺少三连模式（反馈→反应→反制）的冲突场景视为无效冲突。
**典型反模式：** 异能设定无限膨胀、都市日常完全被异能取代失去反差感。

```yaml
hook_config:
  preferred_types: [危机钩, 选择钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末必须有危机升级或身份悬念"

coolpoint_config:
  preferred_patterns: [装逼打脸, 扮猪吃虎, 越级反杀]
  density: moderate-high
  small_coolpoint_interval: 3
  combo_interval: 8
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 3
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压4扬6"

special_rules:
  - "冲突场景必须包含三连模式：反馈（感知威胁）→反应（分析应对）→反制（主动出击）"
  - "异能体系须建立明确的规则边界和克制关系"
  - "日常场景不可完全消失——都市文的魅力在于'日常中的非日常'"
  - "势力格局必须清晰；社会秩序对异能事件的反应必须有逻辑"
```

---

## 七、zhihu-short（知乎短篇）

**一句话定位：** 在最短篇幅内完成最大反转——每一句话都在为最后的暴击做准备。
**核心爽感来源：** 结尾反转带来的认知颠覆，以及重读时发现伏笔的二次快感。
**节奏红线：** 开头3句不能吸引读者=失败，过渡章容忍度为零。
**典型反模式：** 前半段平庸铺垫后半段才发力、反转靠巧合而非伏笔。

```yaml
hook_config:
  preferred_types: [悬念钩, 情绪钩]
  strength_baseline: maximum
  chapter_end_requirement: "全文即一个钩子系统——每个段落结尾都是钩子"

coolpoint_config:
  preferred_patterns: [反派翻车, 装逼打脸, 甜蜜超预期]
  density: extreme
  small_coolpoint_interval: 1
  combo_interval: 3
  milestone_interval: 5

pacing_config:
  stagnation_threshold: 1
  strand_max: 2
  transition_allowance: 0
  pressure_release_ratio: "压4扬6"
  debt_multiplier: 2.0

special_rules:
  - "开头3句内必须建立核心悬念"
  - "结尾必须有反转——反转力度决定短篇质量上限"
  - "伏笔须自然到第一遍看不出来，第二遍恍然大悟"
  - "字字珠玑：删掉任何一句话不影响理解的，就不该存在"
```

---

## 八、substitute（替身文/虐文）

**一句话定位：** 痛感是这种题材的核心商品——读者就是来被虐的，但虐完必须给糖。
**核心爽感来源：** 极致的痛之后的极致的甜，以及真相揭露时的情绪核爆。
**节奏红线：** 压扬比压7扬3，但糖不能缺席，只是量少而精。
**典型反模式：** 为虐而虐无逻辑、误会能靠一句话解决却拖十章、虐到最后读者麻木。

```yaml
hook_config:
  preferred_types: [情绪钩]
  strength_baseline: strong
  chapter_end_requirement: "章末必须让读者情绪被牵动（心疼/气愤/期待/揪心）"

coolpoint_config:
  preferred_patterns: [甜蜜超预期, 装逼打脸, 反派翻车]
  density: moderate
  small_coolpoint_interval: 5
  combo_interval: 12
  milestone_interval: 25

pacing_config:
  stagnation_threshold: 3
  fire_line_tolerance: 4
  strand_max: 2
  transition_allowance: 2
  pressure_release_ratio: "压7扬3"

special_rules:
  - "每次误会必须有'说清楚'的真正障碍——信息差/自尊/第三方介入/时机，而非角色变蠢"
  - "虐的深度必须递进；给糖必须超预期——痛10分给5分甜=10分满足"
  - "替身/原配/主角三角关系须有合理逻辑，不能脸谱化"
  - "情感转折必须有触发事件；HE须有充足铺垫和转折过程"
```

---

## 九、esports（电竞）

**一句话定位：** 用战术说话，用胜利证明——每一个操作都要有逻辑，每一场胜利都要有代价。
**核心爽感来源：** 以弱胜强的战术博弈，以及团队从磨合到默契的成长弧线。
**节奏红线：** 每章必须有可追踪的胜负目标，纯训练无目标=水字数。
**典型反模式：** 战斗全靠运气/天赋爆发、对手毫无战术只会送。

```yaml
hook_config:
  preferred_types: [渴望钩, 选择钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末必须有比赛悬念或训练成果的验证期待"

coolpoint_config:
  preferred_patterns: [越级反杀, 装逼打脸, 反派翻车]
  density: moderate
  small_coolpoint_interval: 4
  combo_interval: 8
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 3
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压4扬6"

special_rules:
  - "每章需有可追踪的胜负目标（训练赛/排位/正式比赛）"
  - "战术展示须有完整逻辑链条：分析对手→制定策略→训练验证→实战执行"
  - "比赛描写须有具体操作细节和战术逻辑；团队角色分工必须明确"
  - "对手不能是稻草人——强队的强大须有具体表现；胜负必须有因果"
```

---

## 十、livestream（直播文）

**一句话定位：** 观众就是你的评委——每一次直播都是一场实时表演，数据就是掌声。
**核心爽感来源：** 实时反馈循环：表现→弹幕反应→数据变化→升级/解锁。
**节奏红线：** 缺少弹幕反应的直播场景超过500字即失效。
**典型反模式：** 弹幕只是凑字数背景音、主播能力无限膨胀无瓶颈。

```yaml
hook_config:
  preferred_types: [渴望钩, 选择钩]
  strength_baseline: moderate
  chapter_end_requirement: "章末必须有数据悬念或事件预告"

coolpoint_config:
  preferred_patterns: [装逼打脸, 反派翻车, 甜蜜超预期]
  density: high
  small_coolpoint_interval: 2
  combo_interval: 5
  milestone_interval: 15

pacing_config:
  stagnation_threshold: 2
  strand_max: 3
  transition_allowance: 1
  pressure_release_ratio: "压3扬7"

special_rules:
  - "核心节奏闭环：直播行为→弹幕/数据反应→数据变化→决策调整，必须完整"
  - "弹幕每500字至少1条，须有实质内容；须包含铁粉/路人/黑粉/大佬多元声音"
  - "直播平台机制必须明确：算法规则、推荐机制、收益模式、排名规则"
  - "线下场景须服务于线上直播——建立人际/积累素材/引发话题"
```

---

## 十一、cosmic-horror（克苏鲁）

**一句话定位：** 人类无法理解宇宙的真相——越是接近真理，越是走向疯狂。
**核心爽感来源：** 恐惧感的层层递进，以及人类面对不可知存在时的渺小与挣扎。
**节奏红线：** 禁止主角完全理解/征服未知存在，这会摧毁整个题材的核心恐惧。
**典型反模式：** 主角靠常规手段打败旧日支配者、恐怖元素变成打怪升级。

```yaml
hook_config:
  preferred_types: [悬念钩, 危机钩]
  strength_baseline: strong
  chapter_end_requirement: "章末必须有认知层面的不安或未解之谜"

coolpoint_config:
  preferred_patterns: [越级反杀, 反派翻车]
  density: low-moderate
  small_coolpoint_interval: 5
  combo_interval: 10
  milestone_interval: 25

pacing_config:
  stagnation_threshold: 4
  strand_max: 3
  transition_allowance: 3
  pressure_release_ratio: "压8扬2"

special_rules:
  - "每次推进真相须绑定明确损失（理智下降/队友牺牲/记忆缺失/身体异变）"
  - "理性角色须逐渐失控；禁止主角完全理解未知存在——真相永远有更深一层"
  - "恐怖描写三层次：①表层不安（细节）②深层恐惧（认知颠覆）③存在主义恐慌（渺小感）"
  - "宇宙存在须用暗示而非直述；每个安全时刻都是下一次恐怖的铺垫；角色死亡不可逆转"
```

---

## 十二、history-travel（历史穿越）

**一句话定位：** 用现代智慧撬动历史杠杆——知识是最大的金手指，但历史有它自己的惯性。
**核心爽感来源：** 现代知识在古代场景中的降维打击，以及改变/顺应历史走向的抉择。
**节奏红线：** 知识优势展示必须包含推导过程，不能跳过"为什么知道"直接到"所以赢了"。
**典型反模式：** 现代知识万能无局限、历史人物变成NPC无自主性。

```yaml
hook_config:
  preferred_types: [渴望钩, 选择钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末必须有历史走向的悬念或人物命运的不确定性"

coolpoint_config:
  preferred_patterns: [装逼打脸, 越级反杀, 反派翻车]
  density: moderate
  small_coolpoint_interval: 4
  combo_interval: 8
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 4
  strand_max: 3
  transition_allowance: 3
  pressure_release_ratio: "压4扬6"

special_rules:
  - "知识优势>武力优势；知识应用须展示推导过程：知道什么→如何适用→预期→实际结果"
  - "历史事件影响须合理——蝴蝶效应不是无限的；历史人物须有自主性，不是主角棋子"
  - "主角历史知识须有边界——遗忘/记忆模糊/历史争议点都是限制"
  - "时代背景真实感必须保持；穿越者身份须始终是隐患"
```

---

## 十三、game-lit（游戏文）

**一句话定位：** 数值是节奏的脉搏——每一点属性增长都是读者的多巴胺，每次升级都是小高潮。
**核心爽感来源：** 可量化的成长反馈，以及游戏机制带来的清晰目标和奖励循环。
**节奏红线：** 属性面板每5章最多展示1次，多了就是水字数。
**典型反模式：** 数值膨胀失控、游戏机制变成单纯数字增长无策略深度。

```yaml
hook_config:
  preferred_types: [渴望钩]
  strength_baseline: moderate
  chapter_end_requirement: "章末必须有目标进展的期待（即将升级/新副本/奖励预告）"

coolpoint_config:
  preferred_patterns: [越级反杀, 装逼打脸, 反派翻车]
  density: high
  small_coolpoint_interval: 3
  combo_interval: 6
  milestone_interval: 15

pacing_config:
  stagnation_threshold: 3
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压3扬7"

special_rules:
  - "前1-2章必须亮出金手指（特殊技能/隐藏职业/系统特权）"
  - "数值反馈须可视化——属性增长、伤害数字、排名变化要让读者'看得到'"
  - "属性/技能面板每5章最多完整展示1次；平时只展示变化部分"
  - "游戏机制须有策略深度；其他玩家/公会/经济系统必须真实；数值膨胀须有天花板"
```

---

## 十四、slice-of-life（日常系）

**一句话定位：** 平凡生活中的温暖细节，以角色互动为核心吸引力——不需要拯救世界，只需要让人想继续住在这个世界里。
**核心爽感来源：** 角色关系的微妙变化和生活仪式感，读者的满足来自"这些人过得很好"。
**节奏红线：** 不能没有事件驱动（纯流水账 = 无聊），连续3章无任何事件推进即触发警告。
**典型反模式：** 填充式日常（事件无因果链，今天吃什么明天去哪里，没有累积意义）。

```yaml
hook_config:
  preferred_types: [情绪钩, 渴望钩]
  strength_baseline: soft
  chapter_end_requirement: "章末必须有角色关系的微妙变化或生活中的小悬念"

coolpoint_config:
  preferred_patterns: [甜蜜超预期]
  density: low
  small_coolpoint_interval: 5
  combo_interval: 15
  milestone_interval: 30

pacing_config:
  stagnation_threshold: 5
  strand_max: 3
  transition_allowance: 4
  pressure_release_ratio: "压2扬8"

special_rules:
  - "每5章必须有关系进展标志——好感度变化、信任升级、习惯磨合、默契建立，至少其一"
  - "不能连续3章无外部事件——外部事件不必是冲突，可以是季节变化、节日活动、新人物登场、意外发现"
  - "日常描写必须有感官细节（食物的香气、雨声、阳光的温度），这是日常系的生命线"
  - "角色互动必须展示个性差异——不同角色对同一事件的反应差异本身就是看点"
  - "生活仪式感需要反复出现并逐渐演变——同一场景在不同阶段出现时，角色关系的变化就是叙事"
```

---

## 十五、wuxia（武侠）

**一句话定位：** 江湖恩怨与侠义精神，武功是手段不是目的——侠之大者，为国为民；侠之小者，快意恩仇。
**核心爽感来源：** 侠义抉择的爽感 + 武学领悟的成就感，打斗是为了证明道心而非单纯暴力。
**节奏红线：** 武功体系不能变成修仙升级——武功有天花板，侠义无上限。
**典型反模式：** 唯武力论（武力解决一切问题）、武功描写只重破坏力不重招式意境。

```yaml
hook_config:
  preferred_types: [危机钩, 悬念钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末必须有江湖恩怨的悬念或侠义抉择的压力"

coolpoint_config:
  preferred_patterns: [装逼打脸, 越级反杀]
  density: moderate
  small_coolpoint_interval: 4
  combo_interval: 10
  milestone_interval: 25

pacing_config:
  stagnation_threshold: 4
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压5扬5"

special_rules:
  - "武功描写重在招式理念而非破坏力——'剑意'比'毁掉一座山'更有武侠味道"
  - "江湖规矩约束行为——江湖不是法外之地，门规、师命、道义、人情都有重量"
  - "侠义与私利的道德抉择是核心冲突——主角不能只在'正确'和'更正确'之间选"
  - "武功体系有天花板，不存在无限升级——突破瓶颈靠悟性而非灵丹妙药"
  - "恩怨逻辑必须清晰——'为什么打'比'怎么打'更重要；师门恩怨、血海深仇、道义担当必须有因果"
```

---

## 十六、isekai（异世界）

**一句话定位：** 现代人穿越到异世界，用原世界知识/视角创造优势——不是无敌，而是换了一种思考方式。
**核心爽感来源：** 信息差的利用 + 新世界的探索发现，"我知道你不知道的事"是核心驱动力。
**节奏红线：** 穿越优势不能无限（必须有限制条件），一旦主角变成万能角色就失去信息差的核心卖点。
**典型反模式：** 万能穿越者（什么都会、毫无障碍、异世界居民全是傻子）。

```yaml
hook_config:
  preferred_types: [悬念钩, 渴望钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末必须有探索发现的期待或穿越优势的边界挑战"

coolpoint_config:
  preferred_patterns: [扮猪吃虎, 越级反杀]
  density: moderate-high
  small_coolpoint_interval: 3
  combo_interval: 8
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 3
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压3扬7"

special_rules:
  - "穿越优势必须有明确边界——知识盲区、文化差异导致的误判、技术条件限制缺一不可"
  - "文化碰撞必须有代价——轻视异世界文化必遭反噬，尊重才可能获得回报"
  - "两个世界的联系随剧情发展——穿越原因、回去的可能性、两世界的关联须逐步揭示"
  - "异世界原住民不能是NPC——他们有自己的智慧、文化和立场，不是为主角服务的工具人"
  - "知识应用须展示过程——知道什么→能否适用→怎么改造→结果如何，不能跳步"
```

---

## 十七、litrpg（文字RPG）

**一句话定位：** 游戏化世界中的数值化成长，系统是核心设定——数值是读者的多巴胺开关，但数值本身不是故事。
**核心爽感来源：** 数值提升的成就感 + 系统交互的新奇感，叮的一声提示音就是最小的叙事单位。
**节奏红线：** 数值不能替代情节（升级不是高潮），纯系统面板连续3段以上展示=读者跳读区。
**典型反模式：** 系统面板堆砌（连续3+段纯数据展示，把小说写成数据库导出报告）。

```yaml
hook_config:
  preferred_types: [悬念钩, 渴望钩]
  strength_baseline: moderate-strong
  chapter_end_requirement: "章末必须有系统通知、任务更新或即将升级的期待"

coolpoint_config:
  preferred_patterns: [装逼打脸, 越级反杀]
  density: high
  small_coolpoint_interval: 2
  combo_interval: 6
  milestone_interval: 15

pacing_config:
  stagnation_threshold: 2
  strand_max: 3
  transition_allowance: 1
  pressure_release_ratio: "压3扬7"

special_rules:
  - "系统界面展示限制每章不超过200字——只展示关键变化，完整面板放在章节末附录或省略"
  - "数值变化必须伴随具体场景——'力量+5'后面必须跟着'他一拳砸碎了之前打不碎的门'"
  - "不能连续2章纯系统交互——至少隔一章有现实场景的剧情推进"
  - "系统规则必须逻辑自洽且稳定——中后期修改核心规则=自毁根基"
  - "任务/副本/技能设计须有策略深度——读者应该能跟着主角一起思考和判断"
```

---

## 十八、romance-same-sex（耽美/百合）

**一句话定位：** 以同性情感关系为核心的恋爱故事——爱情的本质不因性别而不同，但社会语境让它有了独特的张力。
**核心爽感来源：** 情感拉扯的甜蜜感 + 关系突破的满足感，每一次心动的瞬间都值得被放大。
**节奏红线：** 绝不能有任何非自愿情节——这是底线，触碰即弃书。
**典型反模式：** 强制爱/无尊重的关系动态、一方完全依附另一方无独立人格。

```yaml
hook_config:
  preferred_types: [情绪钩, 渴望钩]
  strength_baseline: moderate
  chapter_end_requirement: "章末必须有情感悬念或关系张力"

coolpoint_config:
  preferred_patterns: [甜蜜超预期, 越级反杀]
  density: moderate-high
  small_coolpoint_interval: 3
  combo_interval: 8
  milestone_interval: 20

pacing_config:
  stagnation_threshold: 4
  strand_max: 3
  transition_allowance: 2
  pressure_release_ratio: "压4扬6"

special_rules:
  - "双方必须有独立人格和成长弧线——不能一方是完全的附属品"
  - "关系进展必须建立在相互尊重基础上——理解→信任→依赖→承诺，每一步都不能跳过"
  - "外部冲突驱动关系变化而非误解——社会压力、家庭态度、身份冲突是合理的外部驱动"
  - "情感拉扯要有度——推拉不超过3轮，超过则读者疲劳"
  - "甜蜜场景必须写双方的感受和反应——只写一方是半成品"
```

---

## 十九、horror（恐怖）

**一句话定位：** 制造恐惧感和不安感，未知是最强大的武器——恐怖不是血腥，而是你对即将发生之事的无能为力。
**核心爽感来源：** 恐惧释放的快感 + 真相揭示的智力满足，读者害怕但又忍不住往下翻。
**节奏红线：** 主角不能完全安全（必须有真实的威胁感），如果读者确信主角不会死，恐怖就死了。
**典型反模式：** 跳吓堆砌（连续3+个无因果的惊吓，像恐怖主题公园而非叙事）。

```yaml
hook_config:
  preferred_types: [危机钩, 悬念钩]
  strength_baseline: strong
  chapter_end_requirement: "章末必须有未解除的不安或恐惧升级的暗示"

coolpoint_config:
  preferred_patterns: [反派翻车, 越级反杀]
  density: low
  small_coolpoint_interval: 7
  combo_interval: 15
  milestone_interval: 30

pacing_config:
  stagnation_threshold: 3
  strand_max: 2
  transition_allowance: 1
  pressure_release_ratio: "压8扬2"

special_rules:
  - "未知比已知更恐怖——展示限制规则：怪物/鬼魂/真相的描写，每次只揭示一个侧面，永远保留最核心的未知"
  - "恐怖元素递进增强——不能同一强度的恐惧重复出现，每次必须升级（从不安→恐惧→绝望→崩溃）"
  - "每5章必须有恐惧感升级——新的威胁、旧的威胁增强、安全区的崩塌，至少其一"
  - "安全感是恐怖的调料——短暂的安全时刻让读者放松警惕，下一个恐怖瞬间才有杀伤力"
  - "死亡/伤害必须有分量——不能死完就忘，每个损失都应该影响后续剧情和角色心理"
```

---

## 二十、military（军事）

**一句话定位：** 战争背景下的战略博弈和人性考验——胜利不是荣耀，而是另一种代价的开始。
**核心爽感来源：** 战略智慧的成就感 + 战友情的情感冲击，"我们为什么而战"比"怎么打赢"更重要。
**节奏红线：** 不能美化战争（必须有代价），没有伤亡的战争只是军事cosplay。
**典型反模式：** 兰博式单人英雄（无视战术逻辑、一人扭转战局、敌人配合送死）。

```yaml
hook_config:
  preferred_types: [危机钩, 选择钩]
  strength_baseline: strong
  chapter_end_requirement: "章末必须有战略悬念、生死危机或道德抉择"

coolpoint_config:
  preferred_patterns: [越级反杀, 装逼打脸]
  density: moderate
  small_coolpoint_interval: 5
  combo_interval: 10
  milestone_interval: 25

pacing_config:
  stagnation_threshold: 4
  strand_max: 4
  transition_allowance: 3
  pressure_release_ratio: "压6扬4"

special_rules:
  - "战术描写必须符合基本军事逻辑——兵力、地形、后勤、情报缺一不可"
  - "后勤和补给是真实约束——弹药不够、粮食短缺、援军延迟都必须是真实存在的问题"
  - "伤亡必须有情感分量——每个有名有姓的角色阵亡都应该让读者感到痛，而非数字加减"
  - "政治与军事交织——战争不是纯军事行为，后方政治、外交、舆论都是战场的一部分"
  - "敌我双方都须有合理动机和战略逻辑——敌人不是坏人，是立场不同的军人"
```

---

## 如何选择题材配置？

1. **确定主要题材** -- 从上方20个配置中选择最接近的一个，完全匹配则直接使用
2. **处理混合题材** -- 以主要题材配置为主体，从次要题材配置中提取 `special_rules`，节奏参数以主要题材为准
3. **无论选择哪个配置** -- Anti-AI规则和一致性规则不受题材配置覆盖

**常见混合题材参考：**
系统流+修仙=shuangwen+xianxia | 穿越+爽文=history-travel+shuangwen | 言情+替身=romance+substitute | 游戏+直播=game-lit+livestream | 悬疑+克苏鲁=mystery+cosmic-horror | 都市+修仙=urban-power+xianxia | 异世界+爽文=isekai+shuangwen | 文字RPG+游戏=litrpg+game-lit | 日常+言情=slice-of-life+romance | 耽美+甜宠=romance-same-sex+romance | 恐怖+规则怪谈=horror+rules-mystery | 武侠+修仙=wuxia+xianxia | 军事+历史穿越=military+history-travel

**注意：** 混合不超过2个题材。冲突时以读者期待为准。可微调参数，但不可删除基础规则。

## 各题材核心参数速查表

| 题材 | 停滞阈值 | 爽点密度 | combo间隔 | 压扬比 | 核心钩子 | 过渡容忍 |
|------|---------|---------|----------|-------|---------|---------|
| shuangwen | 3章 | high | 5章 | 压3扬7 | 渴望+选择 | 1章 |
| xianxia | 4章 | moderate | 10章 | 压5扬5 | 危机+渴望 | 3章 |
| romance | 3章 | mod-high | 8章 | 压3扬7 | 情绪+渴望 | 2章 |
| mystery | 5章 | low | 10章 | 压7扬3 | 悬念 | 3章 |
| rules-mystery | 2章 | moderate | 7章 | 压6扬4 | 危机+悬念 | 1章 |
| urban-power | 3章 | mod-high | 8章 | 压4扬6 | 危机+选择 | 2章 |
| zhihu-short | 1章 | extreme | 3章 | 压4扬6 | 悬念+情绪 | 0章 |
| substitute | 3章 | moderate | 12章 | 压7扬3 | 情绪 | 2章 |
| esports | 3章 | moderate | 8章 | 压4扬6 | 渴望+选择 | 2章 |
| livestream | 2章 | high | 5章 | 压3扬7 | 渴望+选择 | 1章 |
| cosmic-horror | 4章 | low-mod | 10章 | 压8扬2 | 悬念+危机 | 3章 |
| history-travel | 4章 | moderate | 8章 | 压4扬6 | 渴望+选择 | 3章 |
| game-lit | 3章 | high | 6章 | 压3扬7 | 渴望 | 2章 |
| slice-of-life | 5章 | low | 15章 | 压2扬8 | 情绪+渴望 | 4章 |
| wuxia | 4章 | moderate | 10章 | 压5扬5 | 危机+悬念 | 2章 |
| isekai | 3章 | mod-high | 8章 | 压3扬7 | 悬念+渴望 | 2章 |
| litrpg | 2章 | high | 6章 | 压3扬7 | 悬念+渴望 | 1章 |
| romance-same-sex | 4章 | mod-high | 8章 | 压4扬6 | 情绪+渴望 | 2章 |
| horror | 3章 | low | 15章 | 压8扬2 | 危机+悬念 | 1章 |
| military | 4章 | moderate | 10章 | 压6扬4 | 危机+选择 | 3章 |

---

> **使用建议：** 将本文件作为创作前的题材参数校准工具。每次开始新项目或新卷时，回顾对应题材的核心参数和特殊规则，确保AI辅助创作时不偏离该题材的节奏本质。
