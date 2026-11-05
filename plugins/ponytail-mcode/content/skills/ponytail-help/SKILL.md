---
name: ponytail-help
description: >
  ponytail 的速查卡：强度档位、各个 Skill 分别做什么、怎么开关、怎么改默认档位。一次性展示，不改任何东西。
  当用户说"ponytail 怎么用""有什么命令""速查表"时使用，也可直接调用 ponytail:ponytail-help。
---

# Ponytail Help

被调用时展示下面这张速查卡。**一次性任务：不要**切换模式、写状态文件或持久化任何东西。

## 强度档位

| 档位 | 触发（直接说） | 行为变化 |
|------|------|---------|
| **lite** | 「ponytail 切到 lite 档」 | 按要求实现。用一行点出更小的方案，让用户自己选。 |
| **full** | 「ponytail 切到 full 档」 | 上面全部规则。默认档位。 |
| **ultra** | 「用 ultra 模式」 | 额外质疑需求本身：动手前先反驳需求里没有被证明的部分。先想删除，再想新增。 |

档位在**本次会话的后续任务**中保持。插件的 Hook 会把档位记在本仓的状态里，所以新会话继续沿用上次的档位；说「ponytail default ultra」可以改默认档位，让**所有**新会话都从它开始。说「用 ponytail」不带档位时报告当前档位，当前是 `off` 时则按默认档位开启。

> MiniMax Code 的 Skill 调用不接收参数：`ponytail:ponytail` 这种技能名形式有效，`ponytail:ponytail lite` 这种带参数形式不保证生效——投稿指南未记载这一点，所以上面一律用自然语言说。

## Skill 列表

| Skill | 触发方式 | 做什么 |
|-------|---------|--------|
| **ponytail** | `ponytail:ponytail` | 极简模式本体：最少的新代码、每条回复都讲清跳过了什么和风险在哪。 |
| **ponytail-review** | `ponytail:ponytail-review` | 对改动做质量评审：bug、安全、真实负载、缺失的测试、速度、能删的代码。每条发现都讲清会出什么问题和怎么修。 |
| **ponytail-audit** | `ponytail:ponytail-audit` | 同样的质量评审，范围是整个仓库，按重要性排序。 |
| **ponytail-debt** | `ponytail:ponytail-debt` | 把 `shortcut:` 注释汇成可追踪的债台账。 |
| **ponytail-gain** | `ponytail:ponytail-gain` | 实测收益计分板：更少代码、更低成本、更快。 |
| **ponytail-help** | `ponytail:ponytail-help` | 就是这张卡。 |

在 MiniMax Code 里，直接在对话里说「用 ponytail-review 审一下当前改动」也可以，Agent 会自己选中对应 Skill。

## 关闭与恢复

说「关掉 ponytail」或「恢复正常模式」即可关闭，任何时候说「用 ponytail」恢复。

## 改默认档位

默认是 `full`。想改，最简单的办法是直接说：

```
ponytail default ultra
```

Hook 会把它记进插件自己的数据目录，之后**新会话**也从这个档位开始。取值 `off | lite | full | ultra`。

> **上游那个 `PONYTAIL_DEFAULT_MODE` 环境变量在 MiniMax Code 上不生效** —— hook 的环境里只有 `PLUGIN_ROOT` / `PLUGIN_DATA` / 项目目录这类平台自带变量，自定义变量不会被注入。所以别指望 `export PONYTAIL_DEFAULT_MODE=ultra` 能起作用。
>
> 想要硬性常驻且不依赖 `node`，把本插件包里的 `AGENTS.md` 复制到你的项目根目录——MiniMax Code 会把项目根的 `AGENTS.md` 当作项目指令读取（若你的版本没有自动加载，手动引用该文件即可）。

## 上游与致谢

上游项目：https://github.com/DietrichGebert/ponytail （MIT 协议，作者 Dietrich Gebert）。本插件是面向 MiniMax Code 的移植版，保留了原始规则集与判定标准；MiniMax Code 的运行时已支持 Plugin 级生命周期 Hook，本插件已附带（会话开始注入规则集 + 档位切换 + 子代理注入，需要本机有 node）。状态栏 Band 等仅适用于 Claude Code 的部分已去除。
