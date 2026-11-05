# tools/ —— 引擎脚本目录

> **本文件只是一个指路牌。命令"怎么用"（参数、口径、边界）的唯一权威来源是 [`ENGINE.md`](ENGINE.md)。**
>
> 想看"这套东西是什么、怎么按节奏用" → 读包根的 [`../SKILL_GUIDE.md`](../SKILL_GUIDE.md)（给人看的唯一入口）

---

## 30 秒上手

```bash
pip install -r requirements.txt     # 装 pyyaml（复盘引擎只需这一个依赖）

python tools/main.py setup                # 首次向导：定义赛道 / 生成 config.yaml
python tools/main.py record new --company 某公司 --position 内容运营 --round 一面 --nature 正编
python tools/main.py report               # ⭐ 主入口：生成《求职总报.md》
```

> **命令从包根目录执行（写成 `python tools/main.py …`）。**
> 脚本用 `__file__` 定位上级的 `cards/`，**不依赖当前工作目录** ——
> 所以 `cd <包根>/tools && python main.py report` 同样成立，两种写法都可以。
> ⚠️ 但在包根写 `python main.py …`（漏掉 `tools/`）会 File not found。

## 全部子命令

见 [`ENGINE.md`](ENGINE.md) —— 那里按「建档 / 报告 / 备战 / 赛道 / 简历 / 找岗 / 维护」分组列全，
并说明每个命令的口径与边界。**本文件不重复列，避免两处不一致。**

## 模块一览（想看代码时）

| 模块 | 负责 |
|---|---|
| `main.py` | 统一入口，把子命令分发给下面各脚本 |
| `record.py` / `build_card.py` / `merge.py` | 建档、逐题追加、草稿转正式号 |
| `report_all.py` ⭐ / `report2.py` / `report3.py` / `decision.py` | 求职总报、轮次口径、动态洞察、浓缩决策 |
| `diagnosis.py` / `strategy.py` / `insights.py` | 自我诊断、求职定位、痛点优势体检 |
| `analyzer.py` / `predict.py` / `predict_apply.py` / `answer.py` | JD 备战、复盘评估、下场决策、应答框架 |
| `industry_taxonomy.py` | **共享内核**：赛道归类 / 公司体量 / 挂因 / 用工性质 / 轮次归一 |
| `tracks.py` | 赛道定义与逐卡指定 |
| `resume_check.py` / `resume_edit.py` / `resume_render.py` | 结构化简历校验 / 编辑 / 渲染 |
| `validate.py` | 卡片校验 + 7 组模块自检（**改动后请跑，0 告警再继续**） |
| `boss.py` + `boss.mjs` / `boss_jd.mjs` | 找岗（**可选模块**，需 Node 18+ 与 Chrome/Edge） |

## 找岗是可选模块

抓取功能额外需要 **Node.js 18+** 与 **Chrome/Edge**（自动探测）；
首次 `python tools/main.py setup` 会说明并询问是否启用。
**不启用不影响其余全部功能** —— 细节见 [`BOSS.md`](BOSS.md)。

## 终端中文乱码？

是 PowerShell 显示编码问题，文件本身为 UTF-8；用 `--report` 输出到文件即可正常查看。
