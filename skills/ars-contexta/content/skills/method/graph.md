# /graph — 知识图谱概览

## 功能说明
分析笔记数量、连接关系、孤立节点、MOC 覆盖，输出图谱健康报告。

## 使用方式
```
/graph
```

## 执行步骤

### Step 1: 统计概览

使用 Glob 和 Grep 工具收集数据：

**总笔记数（排除 inbox/archive）：**
```bash
find vault/notes/ -name "*.md" \
  ! -path "*/inbox/*" \
  ! -path "*/archive/*" \
  ! -name ".gitkeep" | wc -l
```

**按类型分布：**
```bash
# 原子笔记
find vault/notes/atomic/ -name "*.md" ! -name ".gitkeep" 2>/dev/null | wc -l

# 领域笔记
find vault/notes/domains/ -name "*.md" ! -name ".gitkeep" 2>/dev/null | wc -l

# MOC 导览
find vault/notes/mocs/ -name "*.md" ! -name ".gitkeep" 2>/dev/null | wc -l
```

### Step 2: 分析连接

**有 wiki 链接的笔记：**
```bash
rg -l "\[\[" vault/notes/atomic/ --glob "*.md" | wc -l
```

**总 wiki 链接数：**
```bash
rg "\[\[.*?\]\]" vault/notes/ --glob "*.md" -o | wc -l
```

**孤立节点：**
```bash
rg -L "\[\[" vault/notes/atomic/ --glob "*.md" | wc -l
```

### Step 3: 识别中心节点

**被引用最多的笔记（Top 5）：**
```bash
rg "\[\[(.*?)\]\]" vault/notes/ --glob "*.md" -o '$1' | \
  sort | uniq -c | sort -rn | head -5
```

### Step 4: MOC 覆盖检查

**MOC 数量：**
```bash
find vault/notes/mocs/ -name "*.md" ! -name ".gitkeep" | wc -l
```

### Step 5: 计算健康评分

| 指标 | 权重 | 评分标准 |
|------|------|----------|
| 连接率 | 40% | 有链接笔记 / 总笔记 |
| 链接密度 | 30% | 平均每笔记链接数 |
| MOC 覆盖 | 20% | MOC 数量 / 领域数量 |
| 孤立率 | 10% | 1 - 孤立笔记 / 总笔记 |

### Step 6: 输出报告

```
🗺️ /graph 知识图谱概览
━━━━━━━━━━━━━━━━━━━━━━
📊 总笔记：{N} 条

📁 按类型分布：
  • 原子笔记：{X} 条
  • 领域笔记：{Y} 条
  • MOC 导览：{Z} 条

🔗 连接状态：
  • 有链接的笔记：{A}/{N} ({B}%)
  • 总 wiki 链接数：{C} 条
  • 平均链接数：{D} 条/笔记
  • 孤立节点：{E} 个

📈 热门笔记（被引用最多）：
  1. [[笔记名]] — {N} 次引用
  2. [[笔记名]] — {M} 次引用
  ...

🏥 健康评分：{分数}/10 [{状态}]

💡 建议：
  • {建议1}
  • {建议2}
━━━━━━━━━━━━━━━━━━━━━━
```

## 健康评分标准

| 评分 | 状态 | 建议行动 |
|------|------|----------|
| 9-10 | 🟢 优秀 | 继续保持，定期 /review |
| 7-8 | 🟡 良好 | 关注孤立节点 |
| 5-6 | 🟠 一般 | 运行 /review 补充链接 |
| <5 | 🔴 需修复 | 运行 /pipeline 全面修复 |

## 孤立节点处理

孤立节点（无任何链接的笔记）需要：
1. 检查 description 是否准确
2. 尝试在 MOC 中引用
3. 搜索相关关键词建立链接
4. 若确实无关联，标记为 `status: needs-review`
