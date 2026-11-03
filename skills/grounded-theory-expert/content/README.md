# 扎根理论技能 (Grounded Theory Expert)

## 这个技能是什么？

扎根理论（Grounded Theory）是一种系统化的质性研究方法，通过对数据进行开放编码、主轴编码和选择式编码，从资料中归纳构建理论。本技能帮你用AI辅助完成完整的扎根理论研究流程。

## 能解决什么问题？

- 访谈数据不知道怎么编码
- 不知道如何从资料中提炼概念和范畴
- 不确定编码过程是否规范
- 理论饱和度如何判断

## 如何安装？（3步）

### 第1步：安装 Claude Code
如果还没安装 Claude Code，请参考 [5分钟快速上手](https://www.socienceai.com/GET_STARTED.html)。

### 第2步：下载技能
在 [SocienceAI技能页面](https://www.socienceai.com/agentskills/skills.html) 下载 `grounded-theory-expert` 技能包，或直接点击技能卡片的下载按钮。

### 第3步：加载技能
```bash
# 将技能解压到 Claude Code 的 skills 目录
# macOS/Linux:
cp -r grounded-theory-expert ~/.claude/skills/

# Windows (PowerShell):
Copy-Item -Recurse grounded-theory-expert "$HOME\.claude\skills\"

# 重启 Claude Code，然后输入：
# /skills grounded-theory-expert
```

## 如何使用？（示例）

启动技能后，可以这样开始：

```
请帮我分析这20份访谈记录，完成扎根理论编码：
[粘贴访谈记录]

请按以下步骤进行：
1. 开放编码：提炼初始概念
2. 主轴编码：归纳主范畴
3. 选择编码：构建核心范畴
4. 给出理论框架
```

## 编码流程说明

### 开放编码
将资料逐句/逐段分解，赋予概念标签（code）。AI会帮你：
- 识别资料中的关键事件和行动
- 为每个事件赋予简短的概念标签
- 将相似概念归类为范畴

### 主轴编码
将开放编码产生的范畴进行关联分析，建立：
- 主范畴与副范畴的关系
- 因果条件 → 现象 → 情境 → 干预条件 → 行动/互动策略 → 结果

### 选择编码
从所有主范畴中选出核心范畴，建立：
- 核心范畴与所有其他范畴的关系
- 形成扎根理论的核心叙事

## 常见问题

**Q: AI编码和人工编码哪个更准确？**
A: AI是辅助工具，最终判断权在研究者。建议AI初筛后，由研究者复核和确认。

**Q: 样本量多少合适？**
A: 扎根理论不追求样本量，而追求理论饱和。一般15-30份深度访谈可达到基本饱和。

**Q: 如何判断理论饱和？**
A: 当新数据不再产生新的范畴或关系时，即达到理论饱和。

## 相关技能推荐

- [主题分析](https://www.socienceai.com/agentskills/skills.html) — 如果你只需要提炼主题而非构建理论
- [案例研究](https://www.socienceai.com/agentskills/skills.html) — 结合案例法进行深度分析
- [社会网络分析](https://www.socienceai.com/agentskills/skills.html) — 分析关系数据

## 参考资料

- Charmaz, K. (2014). *Constructing Grounded Theory* (2nd ed.). SAGE.
- Strauss, A., & Corbin, J. (1998). *Basics of Qualitative Research*. SAGE.

---
*由 SocienceAI 提供 · 版本 5.2.1 · [反馈问题](https://www.socienceai.com/feedback.html)*