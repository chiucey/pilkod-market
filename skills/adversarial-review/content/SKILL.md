---
name: adversarial-review
description: 对抗式内容审核 Skill。笔杆子写稿→参谋挑刺→裁判打分循环2-3轮，8分以上才过。触发场景：内容审核、文章质量把关、公众号草稿审阅、写作质量循环提升、对抗式评审。
---

# adversarial-review — 对抗式内容审核

## 核心机制

借鉴 Insight Debator 的对抗式推理，用于内容创作的质量把关。

```
总指挥派发任务（含需求+标准）
→ 笔杆子(writer) 出 v1 草稿
→ 参谋(critic) 当"反方"挑刺（5维度攻击）
→ 笔杆子根据批评改 v2
→ 循环 2-3 轮
→ 总指挥(judge) 做最终裁判，过了才交付老板
```

---

## 快速启动

```bash
# 1. 进入工作目录
cd /tmp/adversarial-review-session

# 2. 写好任务简报（必须有：主题、目标读者、核心论点、字数要求）
cat > task-brief.md << 'EOF'
主题：[你的文章主题]
目标读者：[谁会看这篇文章]
核心论点：[这篇文章要说什么观点]
写作风格：[公众号/日记/观点文/演讲稿]
字数要求：[大约多少字]
参考素材：[任何相关的素材、数据、故事]
EOF

# 3. 运行编排脚本
bash ~/.openclaw/skills/adversarial-review/orchestrate.sh
```

---

## 文件结构

```
~/.openclaw/skills/adversarial-review/
├── SKILL.md              # 本文件：主入口
├── writer-prompt.md      # 笔杆子的写作系统提示
├── critic-prompt.md      # 参谋的挑刺系统提示
├── judge-prompt.md       # 裁判的评分系统提示
├── orchestrate.sh        # 编排脚本（控制轮次、文件传递）
└── examples/
    ├── task-brief-example.md     # 任务简报示例
    ├── round-1-draft.md          # 示例：第一轮草稿
    ├── round-1-critique.md       # 示例：第一轮挑刺
    └── round-1-judgment.md       # 示例：第一轮裁判

# 运行时产生（在当前工作目录）：
./task-brief.md
./round-N-draft.md
./round-N-critique.md
./round-N-judgment.md
./final-draft.md
./review-summary.md
```

---

## 角色分工

| 角色 | 职责 | 模型 | Prompt文件 |
|------|------|------|-----------|
| 笔杆子 (writer) | 写作/修改 | Sonnet | `writer-prompt.md` |
| 参谋 (critic) | 挑刺/质疑 | Sonnet | `critic-prompt.md` |
| 裁判 (judge) | 评分/裁决 | Opus | `judge-prompt.md` |

**隔离原则**：
- 笔杆子只读：`task-brief.md` + `round-(N-1)-critique.md`（上轮挑刺）
- 参谋只读：`task-brief.md` + `round-N-draft.md`（当前草稿）
- 裁判只读：`task-brief.md` + `round-N-draft.md` + `round-N-critique.md`
- **互相看不到对方的完整上下文，只通过文件通信**

---

## 评分标准

| 分数 | 裁判决定 |
|------|---------|
| 9-10分 | ✅ 直接通过，输出 final-draft.md |
| 8分 | ✅ 通过（可带轻微修改建议） |
| 6-7分 | 🔁 打回，下一轮继续 |
| ≤5分 | 🔁 强制打回，重写 |

---

## 参谋5维度攻击框架

每次批评必须覆盖以下5个维度：

1. **标题吸引力** — 这个标题能让人点开吗？
2. **结构逻辑** — 文章的骨架稳不稳？开头-中间-结尾有没有漏洞？
3. **数据支撑** — 观点有没有数据/案例支撑？哪里是空话？
4. **读者视角** — 读者看完有没有收获？会不会弃读？
5. **篇幅比例** — 每个部分的篇幅合理吗？哪里写多了哪里写少了？

---

## 注意事项

- 每轮产出3个文件：`round-N-draft.md`、`round-N-critique.md`、`round-N-judgment.md`
- 最多3轮，第3轮如果还不过，输出当前最佳版本 + 说明原因
- 最终产出：`final-draft.md`（最佳草稿）+ `review-summary.md`（全程记录）
- 被骂记录参考：`~/.openclaw/workspace/drafts/scolding-record.md`
- 傅盛写作风格参考：`~/.openclaw/workspace/skills/wechat-article/SKILL.md`
