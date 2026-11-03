---
name: ponytail-gain
description: >
  展示 ponytail 在上游公开基准测试中实测到的收益：代码量、token、成本、耗时的对比数字，以及"该有测试的地方真的写了测试"的比例。
  一次性展示，不改任何东西。
  当用户说"ponytail 能省多少""ponytail 的效果如何""有什么实测数据"时使用，也可直接调用 ponytail:ponytail-gain。
---

# Ponytail Gain

被调用时展示下面这块计分板。**一次性任务：不要**切换模式、写状态文件或持久化任何东西。

下面这些数字来自上游 ponytail 5 的公开 agentic 基准测试：headless Claude Code（Opus 5.5，默认 effort）跑 39 个任务（一个真实 FastAPI + React 仓库里的功能需求单、bug 修复、安全与隐私用例、小型应用），每个任务 5 次运行，对照组是同一个不带该 Skill 的 Agent。39 个任务中有 18 个带隐藏检查，用来判正确性和安全性。每个数字是各任务中位数的几何平均。

数据来源：上游仓库 `benchmarks/results/2026-10-07-agentic.md` 与 README。

## 计分板

用纯 ASCII 条形图。条形长度表示 ponytail 相对无 Skill 基线的占比，标签带准确数字：

```
  ponytail gain           上游基准 · 39 任务 × 5 次运行 · Claude Code Opus 5.5

  无 Skill 基线     ████████████████████  100%
  代码行数         █████████···········   47%   ▼ 53%
  输出 token       ███████████·········   55%   ▼ 45%
  成本             ███████████████·····   74%   ▼ 26%
  耗时             ████████████········   59%   ▼ 41%
  隐藏检查通过率   97%  (无 Skill 96%)
  该有测试处的测试率 98%  (无 Skill 68%)

  这个仓库：  ponytail:ponytail-debt  (你推迟掉的 shortcut)
              ponytail:ponytail-audit (还有哪些能删)
```

## 诚实边界

这些是**上游在 Claude Code 上的基准平均值，不是当前仓库的数字，也不是 MiniMax Code 上的实测结果**。绝不要打印任何针对当前仓库的节省数字（"这里帮你省了 X 行"）：没被写出来的那个版本根本不存在，线上仓库里没有真实的基线可以相减。

唯一真实可信的、针对当前仓库的数字来自 `ponytail:ponytail-debt`（一份数得出来的台账）。这个计分板指向它，而不是编一个出来。

## 边界

一次性展示。不编辑任何东西，不切换模式。
