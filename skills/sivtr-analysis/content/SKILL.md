---
name: "sivtr-analysis"
description: "Analyzes the sivtr open source project (terminal output workspace for AI era). Invoke when user asks to analyze or extract advantages from sivtr project URL."
---

# sivtr 项目分析技能

## 项目概述

**sivtr** 把终端输出变成可复用的文本资产，专为 AI 时代设计。

### 核心定位
- **不是** 终端模拟器
- **不是** 多路复用器
- **不是** 替代 shell
- **是** 现有终端工作流程的**配套工具伴侣**

### 问题解决
终端输出通常是一次性的。命令滚出屏幕后，有用的内容就困在 scrollback、复制模式或巨大的日志里。**sivtr 给这些输出一个小型工作区**。

---

## 核心优势详解

### 1. 多模式输出捕获

| 模式 | 命令 | 说明 |
|------|------|------|
| **管道模式** | `some-command 2>&1 \| sivtr` | 将现有命令输出管道传入 |
| **运行模式** | `sivtr run cargo test` | sivtr 执行并捕获命令输出 |
| **导入模式** | `sivtr import` | 打开当前会话日志 |

**优势**：支持 stdin 捕获、子进程捕获、shell 集成捕获三种方式，灵活性极高。

---

### 2. 键盘优先的 TUI 浏览器

**Vim 风格键位设计**，无需离开键盘：

#### 导航键
| 键 | 动作 |
|----|------|
| `j` / `↓` | 下移 |
| `k` / `↑` | 上移 |
| `h` / `←` | 左移 |
| `l` / `→` | 右移 |
| `Ctrl-D` | 半页下 |
| `Ctrl-U` | 半页上 |
| `g` | 跳到顶部 |
| `G` | 跳到底部 |

#### 搜索与选择
| 键 | 动作 |
|----|------|
| `/` | 开始搜索 |
| `n` | 下一个匹配 |
| `N` | 上一个匹配 |
| `v` | 字符级可视选择 |
| `V` | 行级可视选择 |
| `Ctrl-V` | 块级可视选择 |
| `y` | 复制选中内容 |
| `Esc` | 取消操作 |

**优势**：对于熟悉 Vim 的开发者，学习成本几乎为零。

---

### 3. 语义化命令块复制

启用 shell 集成后，sivtr 会记录命令块，支持**语义化选择**：

```bash
sivtr copy              # 最新输入 + 输出
sivtr copy out          # 最新输出
sivtr copy in           # 最新输入
sivtr copy in 2..4      # 第2到第4条输入
sivtr copy cmd --pick   # 交互式选择命令
```

#### 选择器规则
- **编号规则**：1 = 最新块，2 = 次新块，以此类推
- **范围支持**：`2..4` 选择多个连续块
- **类型过滤**：`out`(输出) / `in`(输入) / `cmd`(裸命令)

**优势**：不用手动选中复制，直接用编号语义选择。

---

### 4. 智能文本过滤

复制时支持**后处理过滤**：

```bash
sivtr copy out --regex panic           # 正则匹配
sivtr copy out --lines 10:40           # 行范围
sivtr copy out --regex "error" --lines 20:60  # 组合使用
```

#### 过滤器类型
| 过滤器 | 语法 | 用途 |
|--------|------|------|
| 正则 | `--regex <pattern>` | 匹配包含正则的行 |
| 行范围 | `--lines <start>:<end>` | 提取指定行 |

**优势**：在复制阶段就完成数据清洗，无需后续处理。

---

### 5. Codex 会话深度集成

`sivtr copy codex` 读取 `~/.codex/sessions` 下的 JSONL 文件，自动匹配当前目录的会话：

```bash
sivtr copy codex          # 最新用户+助手完整回合
sivtr copy codex out       # 最新助手回复
sivtr copy codex in        # 最新用户消息
sivtr copy codex tool      # 最新工具输出
sivtr copy codex all       # 完整解析会话
sivtr copy codex --pick    # 交互式选择区块
```

#### 智能过滤
- **进度注释自动过滤**：默认返回最终回复，而非中间状态
- **目录自动匹配**：选择 cwd 与当前目录匹配的会话
- **区块类型分离**：user / assistant / tool 三种区块分开访问

**优势**：无需手动打开 Codex transcript，一键提取目标内容。

---

### 6. SQLite FTS5 全文搜索

保存的输出使用 **SQLite FTS5** 存储，支持高性能全文搜索：

```bash
sivtr history                     # 列出历史
sivtr history search "panic"      # 搜索关键词
sivtr history show <id>           # 查看特定捕获
```

**优势**：历史输出可持久化检索，不依赖终端 scrollback。

---

### 7. 命令输出对比

迭代开发时快速对比两个输出的差异：

```bash
sivtr diff 1 2    # 对比最新和次新的命令块
```

**优势**：测试失败时快速定位输出变化，无需打开两个窗口。

---

### 8. IDE 深度集成

#### VS Code 扩展
- 插件名：`ariestar.sivtr-vscode`
- 默认快捷键：`Alt+Y`（可自定义）
- 功能：从 VS Code 直接打开 Codex 选择器

#### Windows 全局热键
```bash
sivtr hotkey start     # 启动热键守护
sivtr hotkey status    # 查看状态
sivtr hotkey stop      # 停止
```
默认热键：`Alt+Y`，可在全局打开 Codex 选择器。

**优势**：开发工作流不中断，随时调取历史内容。

---

## 技术架构

### 模块设计
```
sivtr/
├── crates/sivtr-core/    # 核心库
│   └── 捕获、解析、缓冲区、选择、搜索、历史、导出
├── src/                   # 应用层
│   └── CLI、TUI、命令处理、热键集成
├── docs-site/             # 文档站 (Astro/Starlight)
├── editors/vscode/        # VS Code 扩展
└── .github/workflows/     # CI/CD
```

### 技术选型
| 组件 | 技术 | 原因 |
|------|------|------|
| 语言 | Rust | 高性能、低内存、跨平台 |
| 存储 | SQLite + FTS5 | 轻量、可靠、全文搜索 |
| TUI | 终端渲染 | 无需 GUI依赖 |
| 构建 | Cargo | Rust 官方生态 |

---

## 典型使用场景

### 场景 1：构建日志分析
```bash
cargo build 2>&1 | sivtr
# 在 TUI 中用 / 搜索 "error"，v 选择问题行，y 复制
```

### 场景 2：测试失败溯源
```bash
cargo test 2>&1 | sivtr
# 搜索 "FAILED"，用 Ctrl-V 块选择相关日志
```

### 场景 3：AI 对话内容复用
```bash
sivtr copy codex out --regex "```"  # 提取含代码块的回复
```

### 场景 4：多版本输出对比
```bash
sivtr run cargo build  # v1
sivtr run cargo build  # v2
sivtr diff 1 2         # 对比两次构建输出
```

### 场景 5：命令块历史复用
```bash
sivtr copy cmd 3    # 复制第3个历史命令（裸命令）
```

---

## 安装与配置

### 安装方式
```bash
# 方式1：crates.io
cargo install sivtr

# 方式2：源码
git clone https://github.com/Ariestar/sivtr.git
cd sivtr
cargo install --path .
```

### Shell 集成初始化
```bash
sivtr init bash   # Bash
sivtr init zsh    # Zsh
sivtr init fish   # Fish
```

### VS Code 扩展
在 VS Code 中搜索 `ariestar.sivtr-vscode` 安装。

---

## 快速命令参考

| 命令 | 用途 |
|------|------|
| `cmd \| sivtr` | 管道模式浏览输出 |
| `sivtr run <cmd>` | 执行并浏览 |
| `sivtr copy` | 复制最新命令块 |
| `sivtr copy out` | 复制最新输出 |
| `sivtr copy codex` | 复制 Codex 回复 |
| `sivtr diff 1 2` | 对比两个输出 |
| `sivtr history search "keyword"` | 搜索历史 |
| `sivtr hotkey start` | 启动全局热键 |

---

## 竞争优势

| 特性 | sivtr | 传统方案 |
|------|-------|----------|
| 输出持久化 | SQLite FTS5 搜索 | 依赖 scrollback |
| 命令块捕获 | 语义化编号选择 | 手动复制 |
| Codex 集成 | 原生支持 | 需要手动提取 |
| 输出对比 | `sivtr diff` | 多窗口对照 |
| 键盘操作 | Vim 风格 | 鼠标/复制粘贴 |
| 全局访问 | Windows 热键 | 需切换窗口 |

---

## 许可证

Apache License 2.0
