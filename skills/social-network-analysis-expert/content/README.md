# 社会网络分析技能 (Social Network Analysis Expert)

## 这个技能是什么？

社会网络分析（Social Network Analysis, SNA）是一种研究社会关系结构的定量与定性结合方法。本技能帮你用AI完成网络数据的收集、分析与可视化。

## 能解决什么问题？

- 组织内部关系网络如何量化分析
- 哪些是关键节点/意见领袖
- 社群/派系如何识别
- 如何用AI辅助收集关系数据

## 如何安装？（3步）

### 第1步：安装 Claude Code
参考 [5分钟快速上手](https://www.socienceai.com/GET_STARTED.html)。

### 第2步：下载技能
在 [SocienceAI技能页面](https://www.socienceai.com/agentskills/skills.html) 下载 `social-network-analysis-expert`。

### 第3步：加载技能
```bash
# macOS/Linux:
cp -r social-network-analysis-expert ~/.claude/skills/

# Windows:
Copy-Item -Recurse social-network-analysis-expert "$HOME\.claude\skills\"

# 重启 Claude Code，输入：
# /skills social-network-analysis-expert
```

## 如何使用？（示例）

```
请帮我分析这份组织网络数据：
[粘贴邻接矩阵或边列表]

请完成以下分析：
1. 计算中心性指标（点度中心性、接近中心性、中介中心性）
2. 识别关键节点（意见领袖、结构洞占据者）
3. 进行社区检测（识别派系/子群）
4. 生成网络可视化建议
```

## 核心概念

### 中心性分析
- **点度中心性**：连接数量越多越重要
- **接近中心性**：到所有节点距离之和越短越重要
- **中介中心性**：处于其他节点最短路径上的次数越多越重要

### 社区检测
识别网络中紧密连接的子群/社群：
- 派系分析（cliques）
- k-core 分析
- Louvain 算法

### 结构洞理论
识别占据结构洞位置的节点——他们是连接不同社群的桥梁。

## 常见问题

**Q: 数据格式是什么？**
A: 支持邻接矩阵、边列表（CSV/Excel）、GEXF等主流格式。

**Q: 如何收集关系数据？**
A: AI可以帮你设计问卷题项、生成关系矩阵模板、分析已有文本中的关系。

**Q: 可视化怎么做？**
A: AI会给出Python/R/Gephi的代码示例，可直接复制使用。

## 相关技能推荐

- [行动者网络理论](https://www.socienceai.com/agentskills/skills.html) — 质性的ANT分析
- [QCA定性比较分析](https://www.socienceai.com/agentskills/skills.html) — 补充性的因果分析
- [布迪厄场域分析](https://www.socienceai.com/agentskills/skills.html) — 权力关系的质性分析

---
*由 SocienceAI 提供 · 版本 5.0.0 · [反馈问题](https://www.socienceai.com/feedback.html)*