---
name: cm0102-player-generator
description: 根据球员名字生成cm0102足球经理游戏的球员数据。当用户输入球员姓名要求生成或查询cm0102数据时使用。支持补充数据库中没有的球员数据，根据现实球员实力调整数据。触发词：cm0102球员、生成球员数据、球员能力值、补充球员、调整球员数据。
---

# CM0102 球员数据生成器

根据用户输入的球员名字，生成符合CM0102游戏规则的真实球员数据。

## 数据生成规则

### 核心数值规范

| 属性类别 | 数值范围 | 说明 |
|---------|---------|------|
| Potential Ability | 0-200 | 潜力值，最高200仅限球王级球员 |
| Current Ability | 0-200 | 当前能力，根据年龄和巅峰期调整 |
| 其他属性 | 0-20 | 通用属性范围 |

### 球王级球员（Potential Ability = 200）

以下球员可设最高潜力值200：
- C罗 (Cristiano Ronaldo)
- 梅西 (Lionel Messi)
- 齐达内 (Zinedine Zidane)
- 小罗 (Ronaldinho)
- 大罗 (Ronaldo)

### 能力等级参考（Potential Ability）

| 等级 | PA范围 | 描述 |
|-----|-------|------|
| 球王级 | 195-200 | 独一档，仅限历史级球星 |
| 超级巨星 | 180-194 | 顶级豪门核心，世界级球员 |
| 球星 | 160-179 | 豪门主力，联赛顶级球员 |
| 优秀球员 | 140-159 | 豪门轮换或中小球队主力 |
| 普通球员 | 120-139 | 联赛替补或小球会主力 |
| 潜力小妖 | 100-119 | 年轻球员，有培养价值 |

### 必填高值属性（至少一个为20）

1. **Left Foot / Right Foot**: 必须至少有一个为20（主力脚）
2. **Position Rating**: 必须至少有一个位置为20

### Injury Prone（伤病倾向）规则

| 数值 | 含义 |
|-----|------|
| 1-5 | 铁人，几乎不受伤 |
| 6-10 | 正常体质 |
| 11-15 | 容易受伤 |
| 16-19 | 玻璃人倾向 |
| 20 | 极度玻璃人 |

## 输出格式

生成完整的CM0102球员数据，格式如下：

```
### [球员姓名] - [国籍]

**特殊评分 (Special Rating)**
- Current Ability: [当前能力值]
- Potential Ability: [潜力值]
- Current Reputation: [当前声望]
- Home Reputation: [本国声望]
- World Reputation: [世界声望]

**精神评分 (Mental Rating)**
- Adaptability: [0-20]
- Ambition: [0-20]
- Determination: [0-20]
- Loyalty: [0-20]
- Pressure: [0-20]
- Professionalism: [0-20]
- Sportsmanship: [0-20]
- Temperament: [0-20]

**通用评分 (Common Rating - 0-20)**
- Acceleration: [值]
- Aggression: [值]
- Agility: [值]
- Anticipation: [值]
- Balance: [值]
- Bravery: [值]
- Consistency: [值]
- Corners: [值]
- Crossing: [值]
- Decisions: [值]
- Dirtiness: [值]
- Dribbling: [值]
- Finishing: [值]
- Flair: [值]
- Free Kicks: [值]
- Handling: [值]
- Heading: [值]
- Imprtnt Match: [值]
- Injury Prone: [值]
- Jumping: [值]
- Leadership: [值]
- Left Foot*: [值]
- Long Shots: [值]
- Marking: [值]
- Movement: [值]
- Natural Fitness: [值]
- One-on-One: [值]
- Pace: [值]
- Passing: [值]
- Penalties: [值]
- Positioning: [值]
- Reflexes: [值]
- Right Foot*: [值]
- Stamina: [值]
- Strength: [值]
- Tackling: [值]
- Team Work: [值]
- Technique: [值]
- Throw Ins: [值]
- Versatility: [值]
- Vision: [值]
- Work Rate: [值]

**位置评分 (Position Rating - 0-20)**
- Goalkeeper: [值]
- Defender: [值]
- Midfielder: [值]
- Attacker: [值]
- Sweeper: [值]
- Wing Back: [值]
- Anchor: [值]
- Support: [值]
- Right: [值]
- Left: [值]
- Center: [值]
- Free Role: [值]
```

## 生成逻辑

1. **分析球员位置**：根据球员场上位置分配主要属性点
2. **评估球员实力**：根据现实表现和荣誉确定能力等级
3. **考虑年龄因素**：
   - 28-32岁：Current Ability接近Potential Ability
   - 23-27岁：Current Ability通常为Potential Ability的80-90%
   - 18-22岁：Current Ability通常为Potential Ability的50-70%
4. **平衡属性分配**：根据位置特点分配属性权重
5. **确保必填项**：验证Left/Right Foot和Position Rating

## 常见球员类型参考

### 进攻型球员
- 高值：Finishing, Dribbling, Flair, Pace, Acceleration, Shooting
- 低值：Marking, Tackling, Heading

### 防守型球员
- 高值：Tackling, Marking, Strength, Heading, Positioning
- 低值：Finishing, Flair, Dribbling

### 门将
- 高值：Reflexes, Handling, One-on-One, Positioning
- 低值：所有进攻属性

### 组织型中场
- 高值：Passing, Vision, Technique, Decisions, Long Shots
- 中值：Stamina, Work Rate, Tackling
