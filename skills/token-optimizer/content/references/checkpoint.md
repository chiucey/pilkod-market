# 进度检查点 (Checkpoint) 详细参考

## 组件代码

```javascript
/**
 * TOKEN优化器 - 进度检查点 (Checkpoint)
 */
const fs = require('fs');

class Checkpoint {
    constructor(options = {}) {
        this.storagePath = options.storagePath || './checkpoint-data.json';
        this.autoSave = options.autoSave !== false;
        this.data = {
            checkpoints: [],
            currentPhase: null,
            tokenBudget: options.tokenBudget || null,
            tokenUsed: 0
        };
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(this.storagePath)) {
                this.data = JSON.parse(fs.readFileSync(this.storagePath, 'utf-8'));
            }
        } catch (e) { /* 忽略 */ }
    }

    save() {
        try {
            this.data.lastUpdate = new Date().toISOString();
            const dir = require('path').dirname(this.storagePath);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(this.storagePath, JSON.stringify(this.data, null, 2));
            return true;
        } catch { return false; }
    }

    create(name, metadata = {}) {
        const checkpoint = {
            id: `cp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name,
            timestamp: new Date().toISOString(),
            phase: this.data.currentPhase,
            status: metadata.status || 'in_progress',
            data: metadata,
            tokenAtPoint: this.data.tokenUsed
        };
        this.data.checkpoints.push(checkpoint);
        if (this.autoSave) this.save();
        return checkpoint;
    }

    setPhase(phase) {
        this.data.currentPhase = phase;
        this.create(`阶段切换 → ${phase}`, { type: 'phase_change' });
    }

    updateToken(used) {
        this.data.tokenUsed += used;
        this.create('TOKEN更新', { type: 'token', increment: used, total: this.data.tokenUsed });
        if (this.autoSave) this.save();
        const ratio = this.data.tokenUsed / this.data.tokenBudget;
        if (ratio > 0.9) return 'critical';
        if (ratio > 0.75) return 'warning';
        return 'ok';
    }

    getState() {
        return {
            currentPhase: this.data.currentPhase,
            totalCheckpoints: this.data.checkpoints.length,
            latestCheckpoint: this.data.checkpoints[this.data.checkpoints.length - 1],
            tokenBudget: this.data.tokenBudget,
            tokenUsed: this.data.tokenUsed,
            tokenRemaining: this.data.tokenBudget ? this.data.tokenBudget - this.data.tokenUsed : null
        };
    }
}

module.exports = Checkpoint;
```

## 使用示例

```javascript
const Checkpoint = require('./checkpoint');

// 创建检查点实例，设置 TOKEN 预算为 5000
const checkpoint = new Checkpoint({ tokenBudget: 5000 });

// 任务开始
console.log('=== 任务开始 ===');
checkpoint.setPhase('需求分析');
checkpoint.updateToken(200);

// 子任务完成
checkpoint.create('需求文档完成', { status: 'completed' });
checkpoint.updateToken(300);

console.log('=== 当前状态 ===');
console.log(JSON.stringify(checkpoint.getState(), null, 2));

// 下一阶段
checkpoint.setPhase('代码开发');
checkpoint.updateToken(500);

console.log('=== TOKEN 警戒检查 ===');
const state = checkpoint.getState();
const ratio = state.tokenUsed / state.tokenBudget;
console.log(`使用率: ${(ratio * 100).toFixed(1)}%`);
```

## 检查点模板 (Markdown 格式)

```markdown
## 检查点 [#]

**时间**: YYYY-MM-DD HH:MM
**任务**: [当前任务描述]
**状态**: ⬜ 进行中 | ✅ 完成 | ❌ 失败

### 已完成
- [x] 子任务1
- [x] 子任务2

### 当前问题
> 描述遇到的问题（如有）

### 下一步
- [ ] 子任务3
- [ ] 子任务4

### TOKEN消耗
- 预估: XXX
- 实际: YYY
- 状态: ⚠️ 超预算 | ✅ 正常
```

## TOKEN 警戒阈值

| 使用率 | 状态 | 建议操作 |
|--------|------|----------|
| < 50% | ✅ 正常 | 继续当前工作 |
| 50-75% | ⚠️ 提醒 | 关注消耗，评估是否精简 |
| 75-90% | 🔴 警告 | 需评估任务优先级 |
| > 90% | 🚨 紧急 | 仅执行核心任务 |
| 100% | ⛔ 停止 | 暂停或拆分任务 |

## 典型任务流程检查点设置

```
[任务开始]
    ↓
[检查点1: 需求确认] - TOKEN预估
    ↓
[子任务1: 需求分析] - 记录完成
    ↓
[检查点2: 方案设计] - TOKEN消耗检查
    ↓
[子任务2: 方案评审] - 确认方案
    ↓
[检查点3: 开发准备] - 预检执行
    ↓
[子任务3: 编码实现] - 分阶段提交
    ↓
[检查点4: 测试验证] - TOKEN最终检查
    ↓
[任务完成] - 评估总结
```
