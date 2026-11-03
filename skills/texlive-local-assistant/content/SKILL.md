---
name: texlive-local-assistant
description: 当用户需要编写或调试 LaTeX 文档，或询问有关 TeX Live 工具的使用时，应调用本技能。技能的目标是优先使用用户本地安装的 TeX Live 工具和文档。触发短语包括："LaTeX"、"TeX Live"、"texdoc"、"tlmgr"、"xelatex"、"pdflatex"、宏包安装、编译错误等。
---

# TeX Live 本地助手

## 前提条件

- 用户已安装 TeX Live（假设路径 `C:\texlive\2026`）
- 拥有文件读写和命令执行能力
- TeX Live 二进制目录已加入 PATH

## 核心工具及用途

| 工具 | 用途 |
|------|------|
| `texdoc` | 查阅宏包或工具的本地文档 |
| `kpsewhich` | 查找 TeX 树中特定文件的路径 |
| `tlmgr` | 包管理器，安装、更新、卸载宏包 |
| `pdflatex`, `xelatex`, `lualatex` | 编译 `.tex` 生成 PDF（优先使用 `xelatex`）|
| `latex` | 编译生成 DVI |
| `bibtex`, `biber` | 处理参考文献 |
| `makeindex`, `xindy`, `upmendex` | 生成索引 |
| `dvips`, `dvipdfmx` | DVI 转换工具 |
| `mktexlsr` | 更新文件名数据库（`ls-R`）|
| `updmap`, `fmtutil` | 管理字体映射和格式文件 |

## 核心原则：先查文档，再用工具

**工具的具体参数和用法可能随版本变化。在使用任何工具前，遵循以下步骤：**

1. **查询工具用法**：执行 `<工具> -h` 或 `<工具> --help` 获取简要帮助
2. **根据帮助信息构造正确命令**，而不是依赖记忆中的参数
3. **执行命令并分析输出**，必要时结合用户反馈调整

## 宏包文档查阅流程

**重要限制**：`texdoc <工具/包>` 会调用系统 PDF 阅读器打开文档，用户能看到但 你 无法直接读取内容。

1. **获取文档路径**：`texdoc --list --machine <宏包名>`
2. **优先级顺序**：
   - **首选**：`.tex` 或 `.dtx` 文件（可直接读取源码和注释）
   - **次选**：PDF 文件
3. **处理 PDF 的方式**（按顺序尝试）：
   - 方式 A：用 `kpsewhich` 找到 PDF 路径后，尝试用 `pdftotext -layout <文件> -` 提取文本
   - 方式 B：要求用户手动打开 PDF 阅读器，阅读关键内容并复制粘贴相关段落给你
   - 方式 C：将 PDF 文件路径告诉用户，让用户描述问题，你 基于此给出建议
4. **无法读取时的备选**：读取 `.sty` 文件头部的注释或 `\ProvidesPackage` 说明
5. **最后手段**：查阅 CTAN 在线文档或网络搜索

## 文件查找

- 查找具体文件：`kpsewhich <完整文件名>`
- 查找所有匹配：`kpsewhich --all <文件名>`
- 不知确切文件名时：用 `tlmgr search --file <关键词>` 定位所属包

## 宏包管理（tlmgr）

- 安装：`tlmgr install <包名>`
- 卸载：`tlmgr remove <包名>`
- 更新：`tlmgr update --all`
- 搜索：`tlmgr search <关键词>`
- 首次使用前：运行 `tlmgr --help` 或 `texdoc tlmgr`

## 编译与错误诊断

1. 根据文档或用户指定选择引擎（含 `fontspec` 则用 `xelatex` 或 `lualatex`）
2. 编译失败时读取 `.log` 文件，定位错误行
3. 根据错误类型（缺失宏包、语法错误、字体问题等）给出针对性建议
4. 修复后重新编译，必要时运行 `bibtex`/`biber` 或 `makeindex`

## 安全事项

- 执行命令前，确保命令由已知工具名和合法参数构成
- 如需管理员权限，明确提醒用户

## 示例对话

**用户**："我想用 `tlmgr` 安装一个包"
- 执行 `tlmgr --help` 查看帮助，然后指导用户

**用户**："`amsmath` 的 `align` 环境怎么用？"
- 执行 `texdoc --list --machine amsmath` 获取文档路径
- 优先读取 `.tex` 或 `.dtx` 文件提取 `align` 相关说明

---

*本技能核心原则：永远先查文档，确保命令基于用户本地环境的真实支持。*
