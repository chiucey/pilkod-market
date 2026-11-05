# 任务分类算法

## 优先级推断规则

### 规则引擎

任务优先级根据以下因素自动推断：

1. **用户显式指定**（最高优先级）
2. **关键词匹配**
3. **任务类型模式**

### 关键词权重表

| 优先级 | 增强词 | 减弱词 |
|--------|--------|--------|
| A级 | 必须、紧急、重要、立刻、马上、今天必须、今日必做 | - |
| B级 | 应该、最好、建议、推荐、尽量、今天最好 | 可以、有空 |
| C级 | 可以、有空再做、之后、稍后、这周、不急 | 应该、最好 |
| D级 | 考虑、优化、改进、如果有空、锦上添花、可选 | - |

### 时间词处理

```javascript
const TIME_KEYWORDS = {
  hard: ['今天', '现在', '马上', '立刻', '上午', '下午', '晚上', /\d{1,2}[:：]\d{2}/],
  soft: ['有空', '之后', '稍后', '不急', '慢慢来', '有空再说']
};

function detectTimeType(taskText) {
  for (const keyword of TIME_KEYWORDS.hard) {
    if (taskText.includes(keyword) || keyword.test(taskText)) {
      return { isHardTime: true, keyword };
    }
  }
  for (const keyword of TIME_KEYWORDS.soft) {
    if (taskText.includes(keyword)) {
      return { isHardTime: false, keyword };
    }
  }
  return { isHardTime: null, keyword: null }; // 未指定
}
```

### 任务类型模式

```javascript
const TASK_PATTERNS = {
  // A级任务类型
  A: [
    /会议|开会|报告|汇报|演讲|演示/,
    /截止|deadline|最后期限/,
    /考试|面试|面谈/,
    /付款|缴费|账单/
  ],
  // B级任务类型
  B: [
    /买|购物|采购/,
    /健身|运动|跑步|瑜伽/,
    /学习|读书|课程/,
    /打扫|清洁|整理/
  ],
  // C级任务类型
  C: [
    /娱乐|看电影|玩游戏/,
    /社交|约会|聚会/,
    /休息|睡觉|午休/
  ],
  // D级任务类型
  D: [
    /优化|改进|重构/,
    /研究|探索|尝试/,
    /整理照片|清理/,
    /捐赠|处理旧物/
  ]
};

function inferPriority(taskText) {
  // 1. 先检查显式优先级指定
  const explicitMatch = taskText.match(/优先级\s*([A-D])/i);
  if (explicitMatch) {
    return explicitMatch[1].toUpperCase();
  }

  // 2. 检查关键词
  const priorityScore = { A: 0, B: 0, C: 0, D: 0 };

  for (const [priority, keywords] of Object.entries(KEYWORD_WEIGHTS)) {
    for (const keyword of keywords) {
      if (taskText.includes(keyword)) {
        priorityScore[priority] += 1;
      }
    }
  }

  // 3. 检查任务类型模式
  for (const [priority, patterns] of Object.entries(TASK_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(taskText)) {
        priorityScore[priority] += 2; // 模式匹配权重更高
      }
    }
  }

  // 4. 返回最高分数的优先级
  return Object.entries(priorityScore)
    .sort((a, b) => b[1] - a[1])[0][0];
}
```

### 任务继承优先级调整

```javascript
const INHERITANCE_RULES = {
  A: { keep: 'A', escalate: null, deescalate: 'B' },
  B: { keep: 'B', escalate: 'A', deescalate: 'C' },
  C: { keep: 'C', escalate: 'B', deescalate: 'D' },
  D: { keep: 'D', escalate: 'C', deescalate: null }
};

function calculateInheritedPriority(originalPriority, daysPending = 1) {
  const rules = INHERITANCE_RULES[originalPriority];

  if (daysPending === 1) {
    return rules.keep;
  } else if (daysPending === 2) {
    return rules.deescalate || rules.keep;
  } else {
    // 超过2天未完成，提示用户确认
    return null; // 需要用户确认
  }
}
```

### 分类置信度

```javascript
function getClassificationConfidence(taskText, inferredPriority) {
  let confidence = 0.5; // 基础置信度

  // 有显式优先级：+0.4
  if (/优先级\s*([A-D])/i.test(taskText)) {
    confidence = 0.9;
  }

  // 有关键词：+0.2
  const hasKeywords = ['必须', '紧急', '应该', '可以', '优化'].some(k =>
    taskText.includes(k)
  );
  if (hasKeywords) confidence += 0.2;

  // 有时间指定：+0.1
  if (/\d{1,2}[:：]\d{2}/.test(taskText)) {
    confidence += 0.1;
  }

  return Math.min(confidence, 0.99);
}
```

### 输出格式

```javascript
function classifyTask(taskText) {
  return {
    content: taskText,
    priority: inferPriority(taskText),
    isHardTime: detectTimeType(taskText).isHardTime,
    scheduledTime: extractTime(taskText),
    confidence: getClassificationConfidence(taskText, inferredPriority),
    autoClassified: confidence < 0.8 // 需要确认的低置信度分类
  };
}
```
