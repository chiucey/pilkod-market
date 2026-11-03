# SoloForest 分析引擎

## 概述

分析引擎是 SoloForest 生命地图系统的核心算法模块，负责将用户的测试答案转换为可视化的五行能量分布图、十神角色卡和人生大运轨迹，并生成个性化的决策建议。

---

## 一、五行人格分析算法

### 输入数据
- 25道五行人格测试题目的答案
- 每个答案对应一个五行能量（木/火/土/金/水）

### 处理流程

#### 1. 分数统计
```javascript
// 统计每个五行能量的得分
const wuxingScores = {
  wood: 0,  // 木
  fire: 0,  // 火
  earth: 0, // 土
  metal: 0, // 金
  water: 0  // 水
};

// 遍历25道题，统计各五行能量得分
answers.forEach((answer, index) => {
  const element = answerMapping[index][answer];
  wuxingScores[element]++;
});
```

#### 2. 百分比计算
```javascript
// 计算每个五行能量的百分比
const percentages = {
  wood: (wuxingScores.wood / 25) * 100,
  fire: (wuxingScores.fire / 25) * 100,
  earth: (wuxingScores.earth / 25) * 100,
  metal: (wuxingScores.metal / 25) * 100,
  water: (wuxingScores.water / 25) * 100
};
```

#### 3. 主导能量判定
```javascript
// 确定主导能量（≥40%）
// 确定辅助能量（25-39%）
// 确定短板能量（<20%）

const dominant = Object.entries(percentages)
  .filter(([key, value]) => value >= 40)
  .sort((a, b) => b[1] - a[1]);

const secondary = Object.entries(percentages)
  .filter(([key, value]) => value >= 25 && value < 40)
  .sort((a, b) => b[1] - a[1]);

const weakness = Object.entries(percentages)
  .filter(([key, value]) => value < 20);
```

### 输出格式

```json
{
  "wuxingProfile": {
    "wood": { "score": 10, "percentage": 40, "level": "dominant" },
    "fire": { "score": 7, "percentage": 28, "level": "secondary" },
    "earth": { "score": 5, "percentage": 20, "level": "normal" },
    "metal": { "score": 2, "percentage": 8, "level": "weakness" },
    "water": { "score": 1, "percentage": 4, "level": "weakness" }
  },
  "interpretation": {
    "dominantElement": "木",
    "secondaryElement": "火",
    "personalityType": "木火主导型",
    "coreTraits": ["创造力强", "战略思维", "热情表达", "行动驱动"],
    "potentialChallenges": ["行动力不足", "过于理想化"],
    "developmentSuggestions": ["搭配土型合伙人", "设置阶段性目标"]
  }
}
```

---

## 二、十神格局分析算法

### 输入数据
- 30道生命地图测试题目的答案
- 每个答案对应一个十神（比劫/食伤/财星/官杀/印星）

### 处理流程

#### 1. 分数统计
```javascript
const shishenScores = {
  bijie: 0,   // 比劫
  shishang: 0, // 食伤
  caixing: 0,  // 财星
  guansha: 0,  // 官杀
  yinxing: 0   // 印星
};
```

#### 2. 格局判定

| 格局类型 | 特征 | 十神组合 |
|---------|-----|---------|
| 身强格局 | 自信、独立、竞争意识强 | 比劫旺、食伤旺 |
| 身弱格局 | 需要支持、善于借力 | 印星旺、官杀旺 |
| 从格格局 | 极度依赖某种能量 | 某十神≥60% |
| 化格格局 | 能灵活转换角色 | 十神分布均衡 |

#### 3. 角色卡生成
```javascript
// 为每个十神生成角色卡
const roleCards = Object.entries(shishenScores)
  .sort((a, b) => b[1] - a[1])
  .map(([shishen, score]) => ({
    shishen,
    score,
    percentage: (score / 30) * 100,
    card: generateRoleCard(shishen, score)
  }));
```

### 输出格式

```json
{
  "shishenProfile": {
    "bijie": { "score": 8, "percentage": 27 },
    "shishang": { "score": 12, "percentage": 40 },
    "caixing": { "score": 5, "percentage": 17 },
    "guansha": { "score": 3, "percentage": 10 },
    "yinxing": { "score": 2, "percentage": 6 }
  },
  "patternType": "食伤主导型",
  "roleCards": [
    {
      "shishen": "食伤",
      "talent": "创意与执行力",
      "advantage": "善于创新，行动力强",
      "trap": "容易自我，不服管束",
      "direction": "独立工作室、创意领域"
    }
  ],
  "relationshipAdvice": {
    "need": "比劫型合伙人",
    "connection": "共同经历和战斗",
    "valueExchange": "提供创意，接受指导"
  }
}
```

---

## 三、人生大运分析算法

### 输入数据
- 25道人生大运测试题目的答案
- 分四个维度：人生阶段、病药分析、转折期、调候用神

### 处理流程

#### 1. 阶段判定
```javascript
// 统计1-8题答案分布
const stageVotes = {
  early: 0,      // 初期
  growth: 0,     // 成长期
  mature: 0,     // 成熟期
  transition: 0, // 转型期
  late: 0        // 后期
};

// 最多票数确定当前阶段
const currentStage = Object.entries(stageVotes)
  .sort((a, b) => b[1] - a[1])[0];
```

#### 2. 病药配对
```javascript
// 统计9-16题答案，确定五行偏性
const disease = {
  wood: 0,  // 木病：方向不明
  fire: 0,  // 火病：行动不足
  earth: 0, // 土病：过于保守
  metal: 0, // 金病：决断过强
  water: 0  // 水病：缺乏定力
};

// 药方推导（相生相克原理）
const medicine = {
  wood: "搭配土型人才，增强落地",
  fire: "增加刺激，激发热情",
  earth: "适度冒险，突破舒适",
  metal: "增加包容，提升弹性",
  water: "明确目标，建立习惯"
};
```

#### 3. 转折期识别
```javascript
// 统计17-21题答案
const transitionStatus = {
  oncoming: 0,   // 前兆期
  imminent: 0,    // 临近期
  brewing: 0,     // 酝酿期
  stable: 0,     // 稳定期
  confused: 0    // 迷茫期
};

// 判断是否处于转折点
const isTransition = transitionStatus.oncoming + transitionStatus.imminent >= 2;
```

#### 4. 调候用神
```javascript
// 统计22-25题答案
const yongshen = {
  wood: 0,  // 木用神
  fire: 0,  // 火用神
  earth: 0, // 土用神
  metal: 0, // 金用神
  water: 0  // 水用神
};

// 最强能量即调候用神
const tiaoHouYongShen = Object.entries(yongshen)
  .sort((a, b) => b[1] - a[1])[0];
```

### 输出格式

```json
{
  "lifeStage": {
    "current": "成长期",
    "confidence": 75,
    "tasks": ["抓住机会", "快速成长", "建立资源"]
  },
  "diseaseMedicine": {
    "disease": "土病：过于保守",
    "medicine": "增加冒险精神，适度突破",
    "practice": ["接触新事物", "尝试小规模冒险", "加入创新社群"]
  },
  "transitionAnalysis": {
    "status": "临近期",
    "signals": ["感觉需要变化", "遇到新机会"],
    "strategy": "主动求变，把握机会"
  },
  "tiaoHouYongShen": {
    "element": "火",
    "activation": "寻找高能量环境，设定挑战目标",
    "environment": "需要激励和认可的氛围",
    "avoid": "冷漠、停滞的环境"
  },
  "decisionTiming": {
    "favorable": "顺运期加大投入",
    "caution": "逆运期收缩蓄势",
    "action": "转折期主动出击"
  }
}
```

---

## 四、综合分析算法

### 输入数据
- 五行人格分析结果
- 十神格局分析结果
- 人生大运分析结果

### 处理流程

#### 1. 三维生命地图构建
```javascript
const lifeMap = {
  ming: { // 命：先天禀赋
    wuxingDominant: "木",
    shishenDominant: "食伤",
    talent: "创造力和战略思维",
    direction: "科技创新、教育、绿色产业"
  },
  yuan: { // 缘：关系网络
    neededPeople: [
      { type: "比劫型", purpose: "并肩作战" },
      { type: "土型", purpose: "增强落地" }
    ],
    avoidPeople: [
      { type: "过于消极的人" }
    ]
  },
  yun: { // 运：时运轨迹
    currentStage: "成长期",
    transitionStatus: "临近期",
    favorableAction: "加大投入，抓住机会"
  }
};
```

#### 2. 创业决策建议生成
```javascript
// 基于五行和十神组合生成创业建议
const entrepreneurialAdvice = generateAdvice(wuxingProfile, shishenProfile);

// 木火主导 + 食伤旺：创新领域
// 土金主导 + 官杀旺：传统行业
// 水主导 + 印星旺：知识服务
```

#### 3. 风险预警
```javascript
// 基于五行偏性识别风险
const riskWarnings = [
  { risk: "过于理想化", mitigation: "设置阶段性目标" },
  { risk: "缺乏执行力", mitigation: "搭配土型合伙人" }
];
```

### 输出格式

```json
{
  "comprehensiveAnalysis": {
    "lifeMap": {
      "ming": {
        "dominantElement": "木",
        "dominantShishen": "食伤",
        "coreTalent": "创造力和战略思维",
        "suitableIndustries": ["科技创新", "教育培训", "绿色产业"]
      },
      "yuan": {
        "neededPartners": [
          { type: "土型", role: "执行落地" },
          { type: "金型", role: "风险控制" }
        ],
        "relationshipStrategy": "建立平等互助的伙伴关系"
      },
      "yun": {
        "currentStage": "成长期（30-40岁）",
        "favorablePeriod": "未来3-5年",
        "keyOpportunity": "科技创新红利",
        "action": "加大研发投入，组建核心团队"
      }
    },
    "entrepreneurialAdvice": {
      "suitability": 85,
      "recommendedDirection": "科技创新/内容创作",
      "strengths": ["创新能力强", "战略思维好"],
      "weaknesses": ["执行力不足", "过于理想化"],
      "partnerSuggestions": ["土型执行合伙人", "金型风控合伙人"],
      "riskMitigation": ["设置阶段性目标", "建立反馈机制"]
    },
    "lifeGuidance": {
      "nextYear": "适合加大投入，抓住机遇",
      "nextThreeYears": "深耕核心能力，建立护城河",
      "nextTenYears": "稳健发展，考虑传承"
    }
  }
}
```

---

## 五、可视化输出

### 五行能量分布图
```
木: ████████████████░░░░░░ 42%
火: ████████████░░░░░░░░░░ 28%
土: ████████░░░░░░░░░░░░░░ 18%
金: ████░░░░░░░░░░░░░░░░░░  8%
水: ██░░░░░░░░░░░░░░░░░░░░  4%
```

### 十神角色卡
```
┌─────────────────────────────┐
│      🍃 食伤星 · 创意之魂      │
├─────────────────────────────┤
│ 天赋特质：创新思维、执行力强   │
│ 事业优势：适合独立创业        │
│ 潜在陷阱：容易自我，不服管束   │
│ 适合方向：创意工作室、产品创新 │
└─────────────────────────────┘
```

### 人生阶段图
```
    播种期  成长期  成熟期  转型期  收获期
      │       │       │       │       │
      │   ★当前   │       │       │
      │    │      │       │       │
      └────┴───────┴───────┴───────┴────→ 时间
```

---

## 六、API 接口规范

### 分析请求
```json
POST /api/v1/analyze
{
  "testType": "wuxing|lifeMap|destiny|comprehensive",
  "answers": [1, 2, 3, 4, 5, ...]
}
```

### 分析响应
```json
{
  "success": true,
  "data": {
    // 根据 testType 返回对应分析结果
  },
  "generatedAt": "2026-03-26T10:39:07Z"
}
```
