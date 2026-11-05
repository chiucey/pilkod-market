---
name: chongmingming-skill
description: 把目标文件夹（默认 ~/Desktop/downloads）根目录下的所有文件批量重命名为 EP{ep}-C{n}-T{t} 格式（C 编号从 01 递增，保留原扩展名）。优先按 macOS Finder / Windows Explorer 当前显示顺序；如果当前运行环境没有 GUI（比如云端 / workbuddy），脚本会自动列出文件并让用户手动指定顺序。当用户说"重命名视频"、"按顺序改名"、"改成 EP01-C01-T01 格式"、"按文件夹里的排序重命名"、"把 downloads 里的视频改名"、或类似按顺序批量改名诉求时必须触发。即使用户没明说"Finder/Explorer"或"EP-C-T"，只要意图是"按某种顺序批量重命名这些文件"，就用这个 skill。支持 macOS、Windows 以及无 GUI 云沙盒环境。
---

# 按顺序批量重命名（GUI + 手动双模式）

把目标文件夹根目录下的所有文件，按指定顺序重命名为：

```
EP{ep:02d}-C{n:02d}-T{t:02d}.{原扩展名}
```

- `EP` 默认 `01`，用户可指定（"这次是第 2 集" → `--ep 2`）
- `T` 默认 `01`，用户可指定
- `C` 中的数字从 `01` 开始递增（01、02、03、…）
- 默认目标文件夹：`~/Desktop/downloads`
- **只处理根目录文件，不递归子文件夹**
- 不限制扩展名

## 脚本三种运行模式

脚本位置：`~/.claude/skills/chongmingming-skill/scripts/rename.py`

| 模式 | 调用方式 | 说明 |
| --- | --- | --- |
| GUI 自动 | 不传 `--list` / `--order` | 读 Finder / Explorer 视觉顺序后直接改名 |
| 列清单 | `--list` | 只打印带编号的文件列表，不改名 |
| 手动指定 | `--order "3,1,2,4"` | 按用户给的索引（`--list` 编号）重命名 |

## 决策流程（关键）

**第一步：先试 GUI 自动模式**

调用脚本（不加 `--list` / `--order`）：

```bash
# macOS
python3 ~/.claude/skills/chongmingming-skill/scripts/rename.py --dry-run

# Windows
python "%USERPROFILE%\.claude\skills\chongmingming-skill\scripts\rename.py" --dry-run
```

**可能结果 A — 成功**：脚本输出编号 + 旧名 → 新名的预览表。把它展示给用户，确认后去掉 `--dry-run` 正式执行。这是本地有 GUI 的典型场景。

**可能结果 B — 脚本以 exit code 2 退出**，输出形如：

```
【无法读取 Finder / Explorer 视觉顺序】
可能当前环境没有 GUI（如云端沙盒），或文件管理器窗口未打开。

<folder> 里共 N 个文件（按字母序编号）:
  [ 1] xxxx.mp4
  [ 2] yyyy.mp4
  ...
下一步：...
```

这说明当前跑在**没有 GUI 的环境**（比如 workbuddy 的云端沙盒，或 Linux 容器）。这时：

**第二步（仅在 B 情况下）：把列表原样展示给用户，问顺序**

直接把脚本打印的编号列表完整转给用户看，然后问类似这样的问题：

> 这是文件夹里的 N 个文件（已编号）。请告诉我你实际想要的播放顺序——按顺序说编号就行，比如 `3,1,2,4,...`，或者你如果在自己 Finder 里看过，直接按那个顺序念给我。

**第三步：拿到顺序后用 `--order` 执行**

用户给的可能是：
- 明确索引列表：`3,1,2,4,5`
- 用自然语言描述："先是第 3 个，再第 1 个……" → 你把它整理成 `3,1,2,4,5`

然后：

```bash
python3 ~/.claude/skills/chongmingming-skill/scripts/rename.py --order "3,1,2,4,5" --dry-run
```

先 dry-run 给用户核对，用户确认后去掉 `--dry-run` 正式执行。

## 参数

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--folder` | `~/Desktop/downloads` | 目标文件夹 |
| `--ep` | `1` | EP 编号，格式化成两位数 |
| `--t` | `1` | T 编号，格式化成两位数 |
| `--dry-run` | 关 | 只预览不改名 |
| `--list` | 关 | 只列出文件带编号，不改名 |
| `--order` | 无 | 手动指定顺序，例 `"3,1,2,4"`；索引覆盖全部文件，是 `1..N` 的一个排列 |

## 工作机制要点

- **顺序来源**：GUI 模式下来自 Finder/Explorer 当前窗口（受用户排序方式和手动拖拽位置影响）；手动模式下来自 `--order` 指定的索引。
- **索引基准**：`--list` 和 `--order` 的编号都是基于"根目录所有非隐藏文件按字母序"这个固定基础排列的，所以同一个文件夹跑两次 `--list` 得到的编号是一致的。
- **冲突处理**：两步重命名（先改成 `.__rename_tmp_xxxx__` 临时名，再改成最终名），新旧名字范围重叠（比如里面已有一个 `EP01-C03-T01.mp4`）也不会冲突或丢文件。
- **子文件夹 / 隐藏文件**：都会被过滤掉，不参与编号也不会被改。
- **macOS 权限**：首次运行可能弹"允许控制 Finder"系统权限弹窗，点"好"即可。拿不到顺序去"系统设置 → 隐私与安全性 → 自动化"授权。
- **Windows 权限**：内联 `powershell -Command` 通常不受 `ExecutionPolicy=Restricted` 限制；如报错可加 `-ExecutionPolicy Bypass`。
- **云端 / 无 GUI**：脚本会直接 exit code 2，**不要试图重复调用 GUI 模式或强行让它工作**；立刻进入手动模式流程。

## 常见追加诉求

- "这次是第 3 集" → `--ep 3`
- "T 改成 02" → `--t 2`
- "改另一个文件夹" → `--folder /path/to/folder`
- "换个顺序再跑一遍" → 用新的 `--order` 重跑即可，两步改名机制允许已命名成目标格式的文件被重新整理
