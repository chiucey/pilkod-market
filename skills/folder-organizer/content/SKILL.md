---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9d53f9ec22f5b85efea52ad5068173f0
    PropagateID: 9d53f9ec22f5b85efea52ad5068173f0
    ReservedCode1: 304502204d714e21597868098a1a136d5d056f3162eac90ec3c48d6d1b68a217a8f86998022100be918930b121eab3bfa318c9b0f6a87daae3a80ecd6e50ba07b69eb65ea22960
    ReservedCode2: 304502204ecfc1d75f588c1384f7d9e8a00bf02dd2f5075332b5906c299ea858e5117ded022100f209d9994fd8fa23ba9f02f8100da9ff411bcf4189c63ef2f80b87b66e5a1495
description: 当用户请求整理下载文件夹、自动化文件归档、按类型分类文件、清理散乱文件、生成文件清单时使用。适用于"帮我整理Downloads文件夹"、"把文件按类型分类"、"清理桌面/下载目录"、"自动归档文件"等场景。
name: folder-organizer
---

# 下载文件夹智能整理助手

## 技能概述

自动整理 macOS/Windows 下载文件夹，将散乱文件按类型归档到对应子文件夹，并生成可视化文件清单。

## 触发条件

**适用场景：**
- 定期清理杂乱的下载文件夹
- 自动化文件归档管理
- 生成文件夹内容清单供查阅

**触发短语示例：**
- "帮我整理下载文件夹"
- "整理一下Downloads"
- "把文件按类型分类"
- "清理桌面/下载目录"
- "自动归档文件"
- "生成文件清单"
- "整理我的Downloads"

## 前置要求

- Python 3.8+（如需直接执行脚本）
- 操作系统：macOS / Windows / Linux
- 所需库：os, shutil, datetime, pathlib（标准库，无需安装）

## 核心文件分类规则

| 分类文件夹 | 文件扩展名 |
|-----------|-----------|
| 📚 Books & Reading | .pdf, .epub, .mobi, .txt, .doc, .docx |
| 🎬 Movies & Videos | .mp4, .mov, .avi, .mkv, .mp3, .wav, .m4a |
| 📊 Work - PPT & Power BI | .pptx, .xlsx, .pages, .numbers, .key |
| 📖 Manga & Comics | .cbz, .cbr, .zip（漫画相关） |
| 📸 Photography - Presets | .jpg, .jpeg, .png, .gif, .svg, .raw, .cr2, .nef |
| 🗂 Misc & Personal | 其他未分类文件 |

## 安全规则

1. **禁止删除**：仅移动文件，不删除任何数据
2. **禁止覆盖**：同名文件采用重命名策略（添加 `_1`, `_2` 等数字后缀）
3. **忽略系统文件**：自动跳过 `.DS_Store`, `.localized`, `_Folder_Manifest.md`

## 执行流程

### 方式一：AI Agent 执行（推荐）

将以下指令发送给 AI Agent：

```
# Role: 下载文件夹智能整理助手

## 任务描述
请帮我整理下载文件夹（Downloads），将散乱文件按类型移动到对应的子文件夹，并生成更新的文件清单。

## 文件夹结构规则

请创建以下子文件夹（如果不存在）：

1. 📚 Books & Reading/ - 文档和电子书
   - 移动文件：.pdf, .epub, .mobi, .txt, .doc, .docx, .xlsx

2. 🎬 Movies & Videos/ - 视频和音频
   - 移动文件：.mp4, .mov, .avi, .mkv, .mp3, .wav, .m4a

3. 📖 Manga & Comics/ - 漫画和期刊
   - 移动文件：.cbz, .cbr, .zip（漫画相关）

4. 📸 Photography - Presets/ - 图片和预设
   - 移动文件：.jpg, .jpeg, .png, .gif, .svg, .raw, .cr2, .nef

5. 🗂 Misc & Personal/ - 其他杂项
   - 移动文件：不符合上述分类的所有其他文件

## 重要约束

- 不要删除任何文件：仅执行移动操作
- 不要覆盖文件：如果目标路径存在同名文件，在文件名后添加 `_1`, `_2` 等数字后缀
- 保留现有结构：不要修改已经存在于子文件夹中的文件

## 需要忽略的文件
- .DS_Store
- .localized
- _Folder_Manifest.md

## 清单生成要求

整理完成后，在下载根目录生成一份 `_Folder_Manifest.md` 文件，包含：
1. 标题：下载文件夹文件清单
2. 更新时间：格式 YYYY-MM-DD HH:MM:SS
3. 统计信息：总文件数、各分类文件夹文件数量、文件夹总大小
4. 文件列表：按子文件夹分组，列出所有文件名

## 执行步骤

1. 首先扫描下载文件夹，列出所有需要整理的文件
2. 根据文件扩展名判断目标文件夹
3. 移动文件（如果目标存在同名文件则重命名）
4. 生成更新的清单文件
5. 展示整理结果摘要
```

### 方式二：直接运行 Python 脚本

如需直接执行自动化脚本，可使用 `/workspace/temp-skills/folder-organizer/references/organize_downloads.py` 中的代码：

```bash
# 保存脚本
python /workspace/temp-skills/folder-organizer/references/organize_downloads.py
```

## 用法示例

### 示例 1：基础整理请求

**用户输入：**
> 帮我整理一下下载文件夹

**AI 执行：**
1. 扫描 `~/Downloads` 目录
2. 按文件类型分类
3. 移动文件到对应子文件夹
4. 生成 `_Folder_Manifest.md` 清单
5. 展示整理结果摘要

### 示例 2：带条件的整理

**用户输入：**
> 只整理图片和视频文件，不要动文档

**AI 执行：**
1. 扫描 `~/Downloads` 目录
2. 仅处理 .jpg, .png, .mp4, .mov 等文件
3. 跳过文档类文件（.pdf, .docx 等）
4. 更新清单文件

### 示例 3：查看清单

**用户输入：**
> 生成了什么清单？下载文件夹现在有多少文件？

**AI 执行：**
1. 读取 `_Folder_Manifest.md`
2. 展示统计信息和文件列表

## 维护说明

### 扩展分类规则

如需添加新的文件分类，修改 `FILE_CATEGORIES` 字典，详见 `references/organize_downloads.py`。

### 注意事项

- 默认处理 `~/Downloads` 目录
- 如需处理其他目录，请指定完整路径
- 系统文件会被自动跳过
- 同名文件会自动添加数字后缀避免覆盖

## 相关资源

- **Python 脚本**：`references/organize_downloads.py`
- **详细文档**：查看 references 目录
