# 输出模板:事件分析交付物结构

本文件提供事件分析输出物的内容骨架,而非格式化清单。判断逻辑如下:

- **默认形态**:当用户要求"完整事件分析 / 完整报告 / 可复用的特殊情境包"时,先输出事件型 `visual-page brief`，再调用 `visual-page` 生成独立 HTML 事件报告。
- **快速摘要(quick read)**:仅当用户**显式**要求 quick / short / summary / one-page / brief / TL;DR 时启用。
- **章节并非强制清单**:证据充分度与事件类型若指向不同形态,允许重排、合并或裁剪。

---

## 一、完整 HTML 事件报告

为内容充实的完整报告优先把事件逻辑整理成适合 `visual-page` 的页面 brief,而不是固定页面框架。两条硬性原则:

1. **决策姿态须与证据阶段对齐**——开头给出的建议(Buy / Avoid / Watch …)不能领先于证据成熟度。
2. **顶部置入该事件类型的核心分析对象**(例如分拆事件的"价值分配桥"、并购事件的"价差与隐含概率")。

> 交互对齐:交给 `visual-page` 时,按 SKILL.md「HTML 交付」的组件映射与交互规格落地——时间线节点可点击展开、审批 / 情景树用可点击 Mermaid、价差 / 隐含概率 KV cards 可 hover 展开计算口径、监控表可筛选、红队矩阵可行内展开;主题维持冰白纸 + 液态玻璃,并遵循事件语义:价差收窄 / 概率上升 / 审批推进 = 中国红,价差扩大 / 概率下降 / 审批受阻 = 稳绿。

若**用于执行决策所需的实时报价或成交数据缺失**,需把交付物**降级**为"承销框架 / 入场筛选"并在标题或开头说明启动条件,不要给出可执行的交易标题。

### 按事件类型的侧重

| 事件类型 | 报告顶部应置入的核心对象 |
|---|---|
| Spin-off / split-off | 分配机制与硬日期、价值分配桥、SpinCo / RemainCo 起点、技术流证据 vs. 论点、入场筛选、监控、红队 |
| 并购套利(merger arb) | 价差、下行、隐含概率、情景数学(仅在数据可支撑时呈现) |
| 监管 / 诉讼事件 | 程序路径、补救风险、对赔付的传导 |

下文"完整内容清单"按需取用即可。当市场定价、概率、情景或预期回报模块缺乏支撑时,用"证据缺口 / 估值筛 / 启动条件"替代,而不要呈现虚假精度。

---

## 二、快速 PM 摘要(显式触发时使用)

```markdown
# Event-Driven Quick Read: [Company / Ticker] - [Event Type]

**Recommendation:** [Buy / Avoid / Watch / Add / Trim / Use options / Wait]
**Preferred expression:** [Security/trade]
**Sizing view:** [Starter / core / small due to gap risk / no position]
**Market data timestamp:** [Date/time/source or unavailable]

## Setup
- Event:
- Current price:
- Event value / deal value / target value:
- Gross spread / expected return:
- Expected timing:
- Next catalyst:

## PM View
[3-6 bullets that state the variant view, not just facts.]

## Market-Implied vs Our View
- Market-implied probability:
- Our probability:
- Key difference:

## Downside / Break Value
- Downside value:
- Methodology:
- Main weakness in downside estimate:

## Scenario Tree
| Scenario | Probability | Timing | Value | Return | Rationale | Signposts |
|---|---:|---:|---:|---:|---|---|

## Gating Item
- Controlling issue:
- Who controls it:
- What evidence matters next:

## Trade Construction
- Instrument:
- Hedge:
- Liquidity/borrow/carry:
- Review threshold:

## Monitoring Plan
| CatalystName | WindowOrDate | Source | BullSignal | BearSignal | NextAction |
|---|---:|---|---|---|---|

## Red Team
- How we lose money:
- What would change our mind:
```

---

## 三、完整事件分析内容清单

```markdown
# Event-Driven Analysis: [Company / Ticker] - [Event Type]

## 1. PM Decision Summary
- Recommendation:
- Preferred expression:
- Suggested sizing:
- Current price:
- Event value:
- Gross spread / expected return:
- Annualized return if relevant:
- Market-implied probability:
- Our probability:
- Primary gating item:
- Next catalyst:
- Kill criteria:

## 2. Facts / Assumptions / Judgments
### Facts
- [Source-backed facts]
### Assumptions
- [User or model assumptions]
### Judgments
- [Analyst/PM estimates]

## 3. Situation Overview
- Event:
- Parties:
- Securities:
- Announcement date:
- Consideration / transaction mechanics:
- Expected timing:
- Required approvals:
- Source documents reviewed:
- Missing critical sources:

## 4. Timeline
| Date/window | Event | Known or estimated | Why it matters | Source |
|---|---|---|---|---|

## 5. Market Pricing
- Current price and timestamp:
- Spread / return:
- Carry, dividends, borrow, financing:
- Market-implied probability:
- Sensitivity to timing:

## 6. Downside / Terminal Value
- Method 1:
- Method 2:
- Selected downside:
- Why selected:
- Key downside uncertainty:

## 7. Scenario Tree
| Scenario | Probability | Timing | Terminal value | Return | Rationale | Signposts |
|---|---:|---:|---:|---:|---|---|

## 8. Event-Specific Analysis
[Use the relevant playbook: merger, spin, activism, litigation/regulatory, restructuring, technical situation.]

## 9. Trade Construction and Risk
- Best expression:
- Alternative expression:
- Hedge:
- Sizing:
- Liquidity:
- Borrow/carry:
- Factor/beta exposure:
- Mark-to-market path:

## 10. Monitoring Dashboard
| Monitor | Date/window | Source | Positive signal | Negative signal | Action |
|---|---:|---|---|---|---|

## 11. Red-Team / Bear Case
- Strongest bear argument:
- What the market may know:
- Hidden risks:
- Crowding/liquidity/path risk:
- Kill criteria:

## 12. Open Questions
- [Question]
- Why it matters:
- How to resolve:

## 13. Sources and Assumptions
- Sources:
- Market data timestamp:
- Unverified items:
```

---

## 四、监控更新交付物

用途:当事件触发新事实或新数据点,需复盘原始论点是否仍然成立时使用。

```markdown
# Event-Driven Monitoring Update: [Company / Ticker]

## What changed
- New fact:
- Source:
- Date:

## Impact on thesis
- Prior probability:
- Updated probability:
- Prior recommendation:
- Updated recommendation:
- Why:

## Updated scenario tree
| Scenario | Prior probability | Updated probability | Value | Comment |
|---|---:|---:|---:|---|

## Action
- Add / hold / trim / exit / wait:
- Review threshold:
- Next catalyst:
```

---

## 五、红队反证模板

用途:对既有 bull / base 论点做反向压力测试,而非给出新论点。

```markdown
# Event-Driven Red Team: [Company / Ticker]

## Thesis being tested
[State the bull/base thesis in one paragraph.]

## Biggest ways this loses money
1. [Risk]
2. [Risk]
3. [Risk]

## Weakest assumptions
| Assumption | Why it may be wrong | Evidence needed | Impact if wrong |
|---|---|---|---|

## Downside challenge
- User downside:
- Alternative downside:
- Difference:

## Probability challenge
- User probability:
- Market-implied probability:
- Alternative probability:
- Why:

## Path risk
- Delay:
- Liquidity:
- Borrow/carry:
- Crowding:
- Forced selling:

## Revised recommendation
[Decision and why.]
```

---

## 六、PM 视角的事件判断输出:必含要素

任何 PM 取向的事件判断,起手须明确**边缘来源(edge type)**,从以下五选一进行声明:

1. 承销(underwriting):对事件赔付分布的认知差
2. 时机(timing):对节奏与窗口的判断差
3. 资金流(flow):对技术性买卖盘的把握
4. 法律 / 程序(legal / process):对程序结果的反向推演
5. 错定价的期权性(mispriced optionality):非线性赔付被低估

声明边缘后,内容须覆盖:基准率视角、交易表达菜单、事件概率、下行估算方法、流动性 / 融券 / 拥挤度、路径风险、退出计划。
