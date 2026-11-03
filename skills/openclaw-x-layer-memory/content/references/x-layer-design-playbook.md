# X-Layer Design Playbook

## Layer 1: Core Memory

**文件：** `MEMORY.md`

**职责：**
- 用户偏好
- 长期不变事实
- 关键规则与约束
- 经反思后沉淀的高价值稳定知识

**规则：**
- 小而精
- 推荐控制在 3000 tokens 左右
- 不放原始聊天流水

## Layer 2: Episodic Memory

**文件：** `memory/YYYY-MM-DD.md`

**职责：**
- 当天事件
- 临时上下文
- 决策过程
- 当日未完成事项

**规则：**
- 追加式记录
- 尽量包含 `## Retain` 标记
- 适合作为事实抽取输入，不适合作为长期知识终态

## Layer 3: Semantic / Entity Memory

**文件：**
- `bank/world.md`
- `bank/experience.md`
- `bank/opinions.md`
- `bank/entities/*.md`

**职责：**
- 把分散在日记里的事实重组成可检索语义块
- 把"人、项目、公司、地点、系统"变成稳定对象
- 存储可随证据演化的意见和偏好

**规则：**
- 事实、经历、意见尽量分开
- 实体页只保留当前态和高价值证据，不要变成长流水账

## Layer 4: Reflection Memory

**文件建议：** `bank/reflections.md`

**职责：**
- 定期做 consolidation
- 发现冲突事实并标记 superseded
- 把 repeated observations 升级为 stable patterns
- 生成应该进入 `MEMORY.md` 的候选项

**适用场景：**
- 用户偏好经常变化
- 项目跨周或跨月推进
- 需要"模型不只是记住，还要学会总结"

## Layer 5: Retrieval / Index Memory

**文件或后端：**
- `.memory/index.sqlite`
- OpenClaw `memory_search`
- Hybrid search
- QMD sidecar

**职责：**
- 把大量 memory source 压缩成可高召回的 machine recall 层
- 支持 lexical、semantic、temporal、entity-aware 检索

**规则：**
- 这是 derived layer，不是 canonical source
- 索引可以重建
- 先从轻量方案开始，再考虑更复杂 ANN

## Promotion Rules

**从 Layer 2 升到 Layer 1：**
- 长期有效
- 跨会话反复有用
- 对行为风格或关键约束有明显影响

**从 Layer 2 升到 Layer 3：**
- 某个实体、项目、偏好被多次提及
- 单天日志已经无法清楚表达关系

**从 Layer 3 升到 Layer 1：**
- 已经被反复验证
- 冲突已基本解决
- 必须每次都让模型看见

## Recommended Bundles

| 场景 | 层数 | 组合 |
|------|------|------|
| 最低可用 | 3 | L1 + L2 + L3 |
| 推荐生产 | 4 | L1 + L2 + L3 + L4 |
| 复杂工作区 | 5 | L1 + L2 + L3 + L4 + L5 |

## Default File Layout

```
workspace/
├── MEMORY.md
├── memory/
│   └── YYYY-MM-DD.md
├── bank/
│   ├── world.md
│   ├── experience.md
│   ├── opinions.md
│   ├── reflections.md
│   └── entities/
│       ├── Alice.md
│       └── Project-X.md
└── .memory/
```
