---
name: feedback-loop-harness
description: 多源反馈采集与结构化技能。当用户要求收集反馈、实现反馈循环、整合显式与隐式反馈信号、驱动智能体复盘时使用。触发关键词：反馈收集、Feedback Loop、显式反馈、隐式反馈、任务评价、经验权重、复盘优先级。
---

# 多源反馈采集技能 (Feedback Loop Harness)

## 1. 技能概述

多源反馈采集技能是智能体自我进化系统的核心组件，负责系统性收集来自用户和环境的多元反馈信号，并将其转化为结构化数据用于驱动智能体的复盘优先级调整与经验权重优化。

### 1.1 核心职责

| 反馈类型 | 来源 | 信号示例 | 采集时机 |
|---------|------|---------|---------|
| 显式反馈 | 用户 | 点赞/踩、修改建议、评分 | 用户交互后 |
| 隐式反馈 | 环境 | 任务完成度、异常率、响应时间 | 系统运行中 |
| 上下文反馈 | 会话 | 意图识别准确度、上下文保持率 | 对话结束后 |

### 1.2 设计目标

本技能实现以下核心能力：

- **多源统一**：整合用户显式反馈与环境隐式反馈为统一的数据模型
- **信号量化**：将模糊反馈转化为可计算的数值信号
- **优先级排序**：基于反馈质量与影响范围确定复盘优先级
- **权重动态调整**：根据反馈更新各能力的经验权重

## 2. 数据模型

### 2.1 反馈信号结构

```typescript
interface FeedbackSignal {
  // 唯一标识
  signalId: string;

  // 反馈来源
  source: 'user_explicit' | 'environment_implicit' | 'contextual';

  // 反馈类型
  type: FeedbackType;

  // 信号强度 (-1.0 到 1.0)
  intensity: number;

  // 关联的能力/技能
  relatedCapabilities: string[];

  // 上下文信息
  context: {
    taskId?: string;
    sessionId: string;
    timestamp: number;
    metadata?: Record<string, any>;
  };

  // 原始反馈内容
  rawContent?: string;
}

type FeedbackType =
  | 'thumbs_up'           // 点赞
  | 'thumbs_down'         // 点踩
  | 'modification'        // 修改建议
  | 'rating'             // 评分
  | 'task_completion'     // 任务完成度
  | 'error_rate'          // 异常率
  | 'latency'             // 响应延迟
  | 'intent_accuracy'     // 意图识别准确度
  | 'context_retention';  // 上下文保持率
```

### 2.2 经验权重模型

```typescript
interface ExperienceWeight {
  capabilityId: string;

  // 当前权重值
  weight: number;

  // 置信度 (基于样本量)
  confidence: number;

  // 最近更新时间
  lastUpdate: number;

  // 样本统计
  stats: {
    positiveCount: number;
    negativeCount: number;
    totalCount: number;
    avgIntensity: number;
  };
}
```

## 3. 采集机制

### 3.1 显式反馈采集

显式反馈通过用户主动交互获取，具有高置信度但低频次的特点。

#### 3.1.1 交互接口

```
用户反馈接口示例：
┌─────────────────────────────────────────┐
│  回复质量评价                           │
│  ┌─────┐ ┌─────┐ ┌─────┐               │
│  │ 👍  │ │ 👎  │ │ ✏️  │               │
│  │满意 │ │不满 │ │建议 │               │
│  └─────┘ └─────┘ └─────┘               │
└─────────────────────────────────────────┘
```

#### 3.1.2 信号提取规则

| 用户行为 | 反馈类型 | 信号强度 | 关联能力 |
|---------|---------|---------|---------|
| 点赞 | thumbs_up | +0.8 | 最近响应的能力 |
| 点踩 | thumbs_down | -0.8 | 最近响应的能力 |
| 评分 5/5 | rating | +1.0 | 所有涉及能力 |
| 评分 1/5 | rating | -1.0 | 所有涉及能力 |
| 修改建议 | modification | 计算修正幅度 | 指定能力 |

### 3.2 隐式反馈采集

隐式反馈通过系统自动监测获取，具有低置信度但高频次的特点。

#### 3.2.1 环境监测指标

```typescript
const implicitMetrics = {
  // 任务执行层面
  taskExecution: {
    completionRate: number;      // 任务完成率
    successRate: number;         // 成功率
    retryCount: number;          // 重试次数
    timeoutRate: number;         // 超时率
  },

  // 错误监测层面
  errorMonitoring: {
    errorCount: number;          // 错误总数
    errorRate: number;           // 错误率
    criticalErrorCount: number;  // 严重错误数
    errorTypes: Map<string, number>; // 错误类型分布
  },

  // 性能层面
  performance: {
    avgLatency: number;          // 平均延迟
    p95Latency: number;          // P95延迟
    throughput: number;          // 吞吐量
  },

  // 质量层面
  quality: {
    intentAccuracy: number;      // 意图识别准确率
    contextRetentionRate: number; // 上下文保持率
    coherenceScore: number;      // 连贯性评分
  }
};
```

#### 3.2.2 信号计算公式

```
隐式信号强度 = f(指标值, 基线值, 波动系数)

示例计算：
- 任务完成率信号: (实际完成率 - 基线完成率) / 基线完成率
- 异常率信号: -(实际异常率 - 基线异常率) / 基线异常率
- 延迟信号: -(实际延迟 - 基线延迟) / 基线延迟
```

## 4. 信号处理流程

### 4.1 处理管道

```
┌──────────────┐
│  原始反馈    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  信号标准化  │ ──► │  信号验证    │
└──────────────┘     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  能力关联    │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  权重更新    │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  优先级队列  │
                     └──────────────┘
```

### 4.2 信号标准化

所有反馈信号统一映射到 [-1, 1] 区间：

```typescript
function normalizeSignal(rawValue: number, type: FeedbackType): number {
  switch (type) {
    case 'thumbs_up':
      return 0.8;
    case 'thumbs_down':
      return -0.8;
    case 'rating':
      // 评分 1-5 映射到 -1 到 1
      return (rawValue - 3) / 2;
    case 'task_completion':
      // 完成率 0-1 映射到 -1 到 1
      return rawValue * 2 - 1;
    case 'error_rate':
      // 异常率越低越好，取反
      return -(rawValue * 2 - 1);
    case 'modification':
      // 修改建议强度由修正幅度决定
      return Math.max(-1, Math.min(1, rawValue));
    default:
      return 0;
  }
}
```

### 4.3 能力关联算法

```typescript
function associateCapabilities(
  signal: FeedbackSignal,
  context: ExecutionContext
): string[] {
  const capabilities = new Set<string>();

  // 1. 显式指定的关联能力
  if (signal.relatedCapabilities.length > 0) {
    signal.relatedCapabilities.forEach(c => capabilities.add(c));
  }

  // 2. 从上下文推断关联能力
  if (context.currentTask) {
    // 添加任务涉及的主要能力
    context.currentTask.involvedCapabilities.forEach(c =>
      capabilities.add(c)
    );
  }

  // 3. 基于意图识别结果关联能力
  if (context.intentResult) {
    context.intentResult.matchedCapabilities.forEach(c =>
      capabilities.add(c)
    );
  }

  return Array.from(capabilities);
}
```

## 5. 权重调整机制

### 5.1 指数移动平均更新

```typescript
interface WeightUpdateParams {
  // 学习率
  learningRate: number;

  // 衰减因子
  decayFactor: number;

  // 最小样本量阈值
  minSampleThreshold: number;
}

function updateExperienceWeight(
  current: ExperienceWeight,
  newSignals: FeedbackSignal[],
  params: WeightUpdateParams
): ExperienceWeight {
  const { learningRate, decayFactor, minSampleThreshold } = params;

  // 计算加权平均信号强度
  const weightedIntensity = newSignals.reduce((sum, signal) => {
    const recency = Math.exp(
      -decayFactor * (Date.now() - signal.context.timestamp)
    );
    return sum + signal.intensity * recency;
  }, 0) / newSignals.length;

  // 动态学习率调整
  const adjustedLR = current.totalCount < minSampleThreshold
    ? learningRate * (current.totalCount / minSampleThreshold)
    : learningRate;

  // 指数移动平均更新
  const newWeight = current.weight + adjustedLR * (
    weightedIntensity - current.weight
  );

  // 更新统计信息
  const positiveCount = newSignals.filter(s => s.intensity > 0).length;
  const negativeCount = newSignals.filter(s => s.intensity < 0).length;

  return {
    capabilityId: current.capabilityId,
    weight: Math.max(-1, Math.min(1, newWeight)),
    confidence: calculateConfidence(current.stats.totalCount + newSignals.length),
    lastUpdate: Date.now(),
    stats: {
      positiveCount: current.stats.positiveCount + positiveCount,
      negativeCount: current.stats.negativeCount + negativeCount,
      totalCount: current.stats.totalCount + newSignals.length,
      avgIntensity: weightedIntensity
    }
  };
}

function calculateConfidence(sampleCount: number): number {
  // 置信度随样本量增加而提升
  return Math.min(1, sampleCount / 100);
}
```

### 5.2 权重边界约束

```
权重约束条件：
- 权重范围: [-1, 1]
- 权重接近 -1: 能力表现持续不佳，需要优先复盘
- 权重接近 0: 能力表现一般
- 权重接近 1: 能力表现优秀

权重变化触发阈值：
- 变化 > 0.1: 触发能力状态变更通知
- 变化 > 0.3: 触发深度复盘
- 变化 > 0.5: 触发紧急审查
```

## 6. 复盘优先级计算

### 6.1 优先级评分模型

```typescript
interface ReflectionPriority {
  capabilityId: string;
  priority: number;
  reasons: string[];
  suggestedActions: string[];
}

function calculatePriority(
  weight: ExperienceWeight,
  recentSignals: FeedbackSignal[]
): ReflectionPriority {
  const { priority, reasons } = computePriorityComponents(weight, recentSignals);

  return {
    capabilityId: weight.capabilityId,
    priority,
    reasons,
    suggestedActions: generateActionSuggestions(priority, weight)
  };
}

function computePriorityComponents(
  weight: ExperienceWeight,
  signals: FeedbackSignal[]
): { priority: number; reasons: string[] } {
  const reasons: string[] = [];
  let priority = 0;

  // 1. 权重偏离度 (权重越偏离 0，优先级越高)
  const weightDeviation = Math.abs(weight.weight);
  priority += weightDeviation * 0.4;
  if (weightDeviation > 0.5) {
    reasons.push(`权重严重偏离中性值 (${weight.weight.toFixed(2)})`);
  }

  // 2. 信号波动性 (波动越大，说明能力不稳定)
  const signalVariance = calculateVariance(signals.map(s => s.intensity));
  priority += Math.min(signalVariance, 1) * 0.2;
  if (signalVariance > 0.5) {
    reasons.push(`信号波动性高 (方差: ${signalVariance.toFixed(2)})`);
  }

  // 3. 样本量置信度 (低置信度需要更多复盘来建立基线)
  if (weight.confidence < 0.3) {
    priority += (1 - weight.confidence) * 0.2;
    reasons.push(`样本量不足，需要建立基线 (置信度: ${(weight.confidence * 100).toFixed(0)}%)`);
  }

  // 4. 最近趋势 (连续负向信号需要优先关注)
  const recentTrend = calculateRecentTrend(signals);
  if (recentTrend < -0.2) {
    priority += Math.abs(recentTrend) * 0.2;
    reasons.push(`最近呈下降趋势 (趋势值: ${recentTrend.toFixed(2)})`);
  }

  return { priority, reasons };
}
```

### 6.2 优先级队列

```typescript
class ReflectionPriorityQueue {
  private queue: ReflectionPriority[] = [];

  enqueue(priority: ReflectionPriority): void {
    // 按优先级插入排序
    const index = this.queue.findIndex(p => p.priority < priority.priority);
    if (index === -1) {
      this.queue.push(priority);
    } else {
      this.queue.splice(index, 0, priority);
    }
  }

  dequeue(): ReflectionPriority | undefined {
    return this.queue.shift();
  }

  peek(): ReflectionPriority | undefined {
    return this.queue[0];
  }

  getTopN(n: number): ReflectionPriority[] {
    return this.queue.slice(0, n);
  }

  // 批量更新优先级
  refresh(
    weights: ExperienceWeight[],
    signals: Map<string, FeedbackSignal[]>
  ): void {
    this.queue = weights.map(w =>
      calculatePriority(w, signals.get(w.capabilityId) || [])
    );
    this.queue.sort((a, b) => b.priority - a.priority);
  }
}
```

## 7. 集成接口

### 7.1 反馈采集接口

```typescript
interface FeedbackCollector {
  // 采集用户显式反馈
  collectExplicitFeedback(feedback: {
    type: 'thumbs_up' | 'thumbs_down' | 'rating' | 'modification';
    intensity?: number;
    content?: string;
    relatedCapabilities?: string[];
  }): FeedbackSignal;

  // 采集环境隐式反馈
  collectImplicitFeedback(metrics: Partial<ImplicitMetrics>): FeedbackSignal[];

  // 批量提交反馈
  submitFeedback(signals: FeedbackSignal[]): Promise<void>;
}
```

### 7.2 反馈查询接口

```typescript
interface FeedbackQuery {
  // 获取指定能力的反馈历史
  getCapabilityHistory(
    capabilityId: string,
    options?: {
      startTime?: number;
      endTime?: number;
      limit?: number;
    }
  ): Promise<FeedbackSignal[]>;

  // 获取当前权重状态
  getWeightStatus(capabilityId: string): Promise<ExperienceWeight>;

  // 获取复盘优先级队列
  getReflectionQueue(): Promise<ReflectionPriority[]>;

  // 获取统计摘要
  getStatsSummary(): Promise<{
    totalSignals: number;
    avgSignalIntensity: number;
    topCapabilities: string[];
    bottomCapabilities: string[];
  }>;
}
```

## 8. 使用场景

### 8.1 场景一：用户评分反馈

```
用户操作：完成交互后对回复进行评分
触发时机：用户点击 1-5 星评分
处理流程：
  1. 收集评分值 (1-5)
  2. 标准化信号强度 ((评分-3)/2)
  3. 关联到涉及的所有能力
  4. 更新能力权重
  5. 重新计算复盘优先级
```

### 8.2 场景二：异常检测反馈

```
系统事件：任务执行过程中发生异常
触发时机：异常处理器捕获错误
处理流程：
  1. 收集异常类型、堆栈信息
  2. 计算异常率变化信号
  3. 关联到执行异常的能力
  4. 更新错误率相关权重
  5. 生成复盘建议
```

### 8.3 场景三：周期性健康检查

```
系统事件：定时健康检查
触发时机：每小时执行一次
处理流程：
  1. 收集各项隐式指标
  2. 计算与基线的偏差
  3. 识别指标异常的能力
  4. 更新综合权重
  5. 生成健康报告
```

## 9. 配置参数

```typescript
const defaultConfig = {
  // 信号处理
  signal: {
    // 信号有效期 (毫秒)
    signalTTL: 7 * 24 * 60 * 60 * 1000,
    // 最小信号强度阈值
    minIntensityThreshold: 0.1,
    // 批量提交大小
    batchSize: 10,
  },

  // 权重更新
  weight: {
    // 学习率
    learningRate: 0.1,
    // 衰减因子
    decayFactor: 1e-7,
    // 最小样本量阈值
    minSampleThreshold: 5,
    // 权重变化触发阈值
    changeThreshold: 0.1,
  },

  // 复盘优先级
  priority: {
    // 权重偏离度系数
    deviationWeight: 0.4,
    // 波动性系数
    varianceWeight: 0.2,
    // 置信度系数
    confidenceWeight: 0.2,
    // 趋势系数
    trendWeight: 0.2,
    // 复盘队列长度
    queueSize: 10,
  },

  // 隐式反馈基线
  baseline: {
    taskCompletionRate: 0.85,
    errorRate: 0.05,
    avgLatency: 2000,
    intentAccuracy: 0.90,
  }
};
```

## 10. 最佳实践

### 10.1 反馈采集原则

1. **及时性**：显式反馈应在用户行为发生后立即采集
2. **最小干扰**：隐式反馈采集应对用户透明，不影响正常操作
3. **去噪处理**：过滤偶发性异常信号，避免单次事件过度影响
4. **上下文完整**：保留足够的上下文信息，便于后续分析

### 10.2 权重调整原则

1. **渐进式更新**：避免大幅度的权重跳变
2. **样本量考量**：低样本量时降低更新幅度
3. **周期性重置**：长时间无更新的能力可考虑回归基线
4. **异常保护**：当权重接近边界时启用特殊处理

### 10.3 复盘优先级原则

1. **影响范围优先**：影响多个能力的反馈优先处理
2. **趋势判断**：关注趋势而非单点值
3. **成本效益**：评估复盘成本与预期收益
4. **实时调整**：根据新反馈动态调整优先级
