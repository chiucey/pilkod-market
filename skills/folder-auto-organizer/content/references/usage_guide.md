# 文件夹自动整理工具 - 使用指南

## 功能特性

### 核心能力
1. **智能文件识别**: 自动识别 50+ 种文件类型
2. **多维度分类**: 支持按类型、主题、日期等多种方式分类
3. **内容摘要**: 提取文档内容预览，便于快速了解文件内容
4. **自动总结**: 在每级目录生成 Markdown 格式的内容总结文档
5. **安全机制**: 跳过敏感文件，支持预览模式

### 支持的文件类型

| 类别 | 扩展名 |
|------|--------|
| 📄 文档 | .pdf, .doc, .docx, .txt, .md, .rtf, .odt |
| 📊 表格 | .xls, .xlsx, .csv, .ods |
| 📽️ 演示 | .ppt, .pptx, .odp |
| 🖼️ 图片 | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico |
| 🎵 音频 | .mp3, .wav, .aac, .flac, .ogg, .m4a |
| 🎬 视频 | .mp4, .avi, .mov, .mkv, .wmv, .flv |
| 💻 代码 | .py, .js, .java, .cpp, .c, .html, .css, .json, .xml, .yaml, .sql, .go, .rs, .ts, .php, .rb |
| 📦 压缩 | .zip, .rar, .7z, .tar, .gz, .bz2 |
| 📚 电子书 | .epub, .mobi, .azw, .azw3 |
| 🔤 字体 | .ttf, .otf, .woff, .woff2 |

## 使用方法

### 基本命令

```bash
# 预览模式（默认）- 查看整理方案但不确定执行
python scripts/organize_folder.py /path/to/folder

# 执行模式 - 实际进行整理
python scripts/organize_folder.py /path/to/folder --execute

# 快速执行
python scripts/organize_folder.py /path/to/folder -e
```

### 高级选项

```bash
# 按主题深度分类（合同、报告、发票等）
python scripts/organize_folder.py /path/to/folder -t --execute

# 按年份组织文件
python scripts/organize_folder.py /path/to/folder -d --execute

# 组合使用：按主题 + 按年份
python scripts/organize_folder.py /path/to/folder -t -d --execute
```

## 分类规则

### 按类型分类（默认）

```
目标文件夹/
├── 📁 Documents/       # 所有文档类文件
│   ├── 📄 00_Documents_目录总结.md
│   ├── report.pdf
│   └── contract.docx
├── 📁 Images/          # 图片资源
│   ├── 📄 00_Images_目录总结.md
│   └── photo.jpg
├── 📁 Videos/          # 视频文件
├── 📁 Code/             # 代码文件
└── 📁 00_总目录总结.md  # 整体总结
```

### 按主题分类（-t 参数）

```
目标文件夹/
├── 📁 合同/            # 包含"合同"关键词的文件
├── 📁 报告/            # 包含"报告"关键词的文件
├── 📁 发票/            # 包含"发票"关键词的文件
├── 📁 简历/            # 包含"简历"关键词的文件
└── 📁 Others/          # 无法分类的文件
```

### 敏感文件保护

以下文件会被自动跳过并警告：
- 包含密码、密钥的文件 (password*, *secret*, *private*)
- API 密钥文件 (api_key*, api_token*)
- 配置文件 (*.env, .git/config)
- SSH 密钥 (id_rsa, id_dsa)

## 输出文档说明

### 文件清单表

每个整理后的文件夹会生成一个 `00_XXX_目录总结.md` 文件：

```markdown
# [文件夹名] 目录总结

**整理时间**: 2024-01-15 14:30
**文件总数**: 15 个
**子文件夹**: 3 个
**总大小**: 125.6 MB

## 内容概览
[简要描述此文件夹的主要内容和用途]

## 文件清单

| 文件名 | 类型 | 大小 | 修改时间 |
|--------|------|------|----------|
| 合同.pdf | 📄 PDF | 1.2MB | 2024-01-15 |
| 报告.docx | 📄 Word | 256KB | 2024-01-20 |

## 子文件夹
- 📁 `2024` - 包含 5 个文件
- 📁 `2023` - 包含 10 个文件
```

### 根目录总结

在目标文件夹根目录生成 `00_总目录总结.md`：
- 全局文件统计
- 分类结构概览
- 文件数量分布

## 常见问题

### Q: 整理后原文件还在吗？
A: 执行模式下，文件会被移动到对应分类文件夹。如果需要备份，建议先在预览模式下确认整理方案。

### Q: 遇到重名文件怎么办？
A: 工具会自动检测重名，并添加序号后缀（如 `文件_1.pdf`, `文件_2.pdf`）。

### Q: 可以回滚整理操作吗？
A: 目前需要手动备份或使用操作日志回滚。后续版本会增加自动回滚功能。

### Q: 支持中文文件名吗？
A: 完全支持，所有文件名、路径、总结文档都支持中文。

### Q: 大文件夹处理需要多长时间？
A: 扫描阶段约 1000 文件/秒。实际整理速度取决于文件系统性能。

## 最佳实践

1. **首次使用先用预览模式**
   ```bash
   python scripts/organize_folder.py /path/to/folder
   # 查看整理方案，确认无误后再执行
   python scripts/organize_folder.py /path/to/folder -e
   ```

2. **重要文件先备份**
   ```bash
   cp -r /path/to/folder /path/to/folder_backup
   ```

3. **定期整理**
   建议每月整理一次下载文件夹、工作目录等容易堆积文件的路径。

4. **自定义扩展**
   如需添加新的文件类型或主题分类，修改 `utils.py` 中的：
   - `FILE_TYPE_MAP`: 文件类型映射
   - `TOPIC_KEYWORDS`: 主题关键词

## 扩展开发

### 添加新的文件类型

在 `utils.py` 中编辑 `FILE_TYPE_MAP`:

```python
FILE_TYPE_MAP = {
    # ... 现有类型 ...
    'new_ext': ('CategoryFolder', '📄 Description'),
}
```

### 添加新的主题分类

在 `utils.py` 中编辑 `TOPIC_KEYWORDS`:

```python
TOPIC_KEYWORDS = {
    # ... 现有主题 ...
    '新主题': ['关键词1', '关键词2', 'keyword3'],
}
```

### 集成到其他工具

```python
from organize_folder import FolderOrganizer

organizer = FolderOrganizer('/path/to/folder', {
    'dry_run': False,
    'by_topic': True,
})
organizer.run()
```
