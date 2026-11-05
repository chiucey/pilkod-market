# scripts/ 目录说明

本 skill 的可执行代码位于 **`../tools/`**（`main.py` 为统一入口）。

部分 Agent Skills 平台约定用 `scripts/` 存放可执行代码；本包沿用 `tools/` 命名（历史原因，且文档、命令示例都以 `tools/` 为准）。

如果你使用的平台**强制要求** `scripts/` 目录，可任选一种方式：

1. **软链/别名**（推荐）：
   在包根目录执行
   ```bash
   # Linux / macOS
   ln -s tools scripts
   # Windows（管理员 PowerShell）
   New-Item -ItemType Junction -Path scripts -Target tools
   ```

2. **直接改名**：把 `tools/` 改名为 `scripts/`，并把文档中的 `tools/` 一并替换为 `scripts/`。

> 代码本身不依赖目录名——`main.py` 及各脚本都用 `__file__` 定位上级的 `cards/`，改名后仍可正常工作。
