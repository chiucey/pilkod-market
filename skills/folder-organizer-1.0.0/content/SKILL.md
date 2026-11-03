---
name: folder-organizer
description: 专业的文件夹整理助手。当用户需要整理文件夹、清理桌面、自动归类文件时激活。核心原则：清理前先创建压缩备份，用移动代替删除确保数据安全，支持Mac和Windows桌面系统。
---

# 专业的文件夹整理助手 Skill

## 触发条件

以下任意场景触发本 skill：
- 用户说"整理文件夹"、"清理文件夹"、"归类文件"
- 用户说"帮我整理桌面"、"桌面太乱了"
- 用户说"按类型整理文件"、"按时间分组"
- 用户上传一个文件夹路径，要求整理

---

## 核心原则（绝对遵守）

### 安全优先
1. **先备份，再操作**：任何清理/移动前，必须先创建压缩备份
2. **移动代替删除**：文件一律移动到 `~/folder-organizer-trash/` 或用户指定目录，不直接删除
3. **备份可还原**：所有备份保留在 `~/.folder-organizer/backups/` 下，带时间戳

### 系统兼容
- **Mac**：使用 `zip`、`mv`、`find` 等标准 Unix 命令
- **Windows**：使用 PowerShell 的 `Compress-Archive`、`Move-Item`、`Get-ChildItem`
- **自动识别**：执行前检测系统类型，选择对应命令集

### 桌面端限制
- ⚠️ 本 skill 必须在**桌面端环境**使用（有图形界面）
- 不适用于纯服务器/无头环境
- 整理前必须获得用户确认（显示计划操作清单）

---

## 执行流程

### 第 1 步：确认基础信息

向用户询问（如果用户未提供）：

```
请提供以下信息：
1. 要整理的文件夹路径（例：~/Desktop 或 C:\Users\xxx\Desktop）
2. 整理规则（按类型/按时间/按大小/自定义）
3. 目标结构（简单说明你希望整理成什么样）
```

---

### 第 2 步：扫描 + 生成计划

根据用户指定的路径和规则，扫描文件夹，生成一份**操作计划**，格式如下：

```
📁 整理计划：/xxx/xxx
━━━━━━━━━━━━━━━━━━
【备份】
✅ 将创建压缩备份至：~/.folder-organizer/backups/yyyymmdd_hhmmss.zip

【移动操作】（共 N 个文件）
📦 图片(.jpg/.png/.gif)     → ~/Pictures/整理/YYYY-MM/
📦 文档(.pdf/.docx/.txt)   → ~/Documents/整理/YYYY-MM/
📦 视频(.mp4/.mov)         → ~/Videos/整理/YYYY-MM/
📦 压缩包(.zip/.rar)        → ~/Downloads/整理/压缩包/
📦 其他                    → ~/folder-organizer-trash/其他/

【不移动】（用户指定保留）
✅ .DS_Store / Thumbs.db 等系统文件
✅ 以 . 开头的隐藏文件
```

---

### 第 3 步：用户确认

**必须等用户回复"确认"或"开始整理"，才执行操作。**

如果用户说"部分修改" → 根据反馈调整计划 → 重新展示计划 → 再次确认。

---

### 第 4 步：执行备份

```bash
# Mac
zip -r ~/.folder-organizer/backups/$(date +%Y%m%d_%H%M%S)_backup.zip /path/to/target_folder

# Windows (PowerShell)
Compress-Archive -Path "C:\path\to\folder" -DestinationPath "$env:USERPROFILE\.folder-organizer\backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')_backup.zip"
```

备份创建成功后，才进入下一步。

---

### 第 5 步：执行移动

按计划逐一执行移动操作，每个类别完成后显示进度：

```
[1/5] 📦 正在移动图片文件...
[2/5] 📦 正在移动文档文件...
...
```

---

### 第 6 步：完成报告

整理完成后，生成报告：

```
✅ 整理完成！

📊 整理报告
━━━━━━━━━━━━━━━━━━
备份位置：~/.folder-organizer/backups/yyyymmdd_hhmmss_backup.zip
处理文件：N 个
节省空间：约 XX MB
移动详情：
  📦 图片 → N 个
  📄 文档 → N 个
  🎬 视频 → N 个
  📦 压缩包 → N 个
  📁 其他 → N 个

⚠️ 误删？可在备份中还原：
  解压备份文件，找到对应文件移回原位即可。
```

---

## 整理规则预设

### 规则 A：按文件类型（默认）
```
图片(.jpg/.jpeg/.png/.gif/.webp/.svg/.bmp)
视频(.mp4/.mov/.avi/.mkv/.wmv)
音频(.mp3/.wav/.aac/.flac)
文档(.pdf/.doc/.docx/.xls/.xlsx/.ppt/.pptx/.txt/.md)
压缩包(.zip/.rar/.7z/.tar/.gz)
代码(.py/.js/.html/.css/.json/.java/.cpp/.go)
```

### 规则 B：按时间（年月）
文件移动到对应年份/月份子目录。

### 规则 C：按文件大小
- 大文件（>100MB）→ 单独目录
- 中等（10-100MB）→ 合并
- 小文件（<10MB）→ 合并

---

## 特殊处理

| 场景 | 处理方式 |
|:---|:---|
| 文件名冲突 | 加数字后缀：`file_1.jpg`, `file_2.jpg` |
| 目标目录不存在 | 自动创建（含中间目录） |
| 系统文件 | 跳过（.DS_Store, Thumbs.db 等） |
| 隐藏文件（以.开头） | 默认保留，不移动 |
| 空文件夹 | 整理后删除 |
| 权限不足 | 报错，提示用户授权 |

---

## 禁止事项

- ❌ 不创建备份就移动文件
- ❌ 直接删除文件（只移动到 trash 目录）
- ❌ 在未经用户确认的情况下执行任何操作
- ❌ 修改文件名（只改变位置）
- ❌ 操作用户目录外的路径（除非明确授权）

---

## 一句话原则

**安全第一：先备份，再整理；只移动，不删除；用户不确认，绝不动手。**
