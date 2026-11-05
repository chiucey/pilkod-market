---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3db8b861f215f9626eed7f0168d0611a
    PropagateID: 3db8b861f215f9626eed7f0168d0611a
    ReservedCode1: 3046022100f97c2499a19212e0a81765b68bf146f151bed6ab4a1bff3ff7a33320ee74154f022100db2fc44fb70768eba5a995c5e1cc69f00f108f948b1bac5f2e4a6b0593c69bf5
    ReservedCode2: 3045022100ad7dbc41a24bb2f76e7e25f91cf25ac6309f59ea978bce04c2f0a5be273af1cf0220501fe380bc6d874c31999cbb62fb5e0b31cf80feb76797c69d7e49e1bb0e7b03
description: 自动梳理和整理文件夹中的各类文件。当用户要求整理文件夹、自动分类文件、按内容组织资料、或需要对大量文件进行归档整理时使用。
name: folder-auto-organizer
---

# Folder Auto Organizer

自动分析文件夹内容，根据文件类型、主题和相关性进行智能分类整理，并在每级目录生成内容总结文档。

## 工作流程

### 阶段 1: 环境与依赖检查

1. **Python 环境验证**
   ```bash
   python3 --version  # 确保 Python 3.8+
   ```

2. **必需依赖安装**
   ```bash
   pip install python-magic-bin  # 文件类型识别
   pip install python-docx       # Word 文档解析
   pip install openpyxl          # Excel 文件解析
   pip install Pillow            # 图片处理
   pip install pypdf2            # PDF 文本提取
   ```

### 阶段 2: 文件扫描与分析

1. **递归扫描目标文件夹**
   - 遍历所有文件和子文件夹
   - 记录文件路径、大小、修改时间、扩展名

2. **文件类型识别与分类**

   | 类型 | 扩展名 | 分类标签 |
   |------|--------|----------|
   | 文档 | .doc/.docx/.pdf/.txt/.md/.rtf | 📄 Documents |
   | 表格 | .xls/.xlsx/.csv | 📊 Spreadsheets |
   | 演示 | .ppt/.pptx | 📽️ Presentations |
   | 图片 | .jpg/.jpeg/.png/.gif/.bmp/.svg | 🖼️ Images |
   | 音频 | .mp3/.wav/.aac/.flac | 🎵 Audio |
   | 视频 | .mp4/.avi/.mov/.mkv | 🎬 Videos |
   | 代码 | .py/.js/.java/.cpp/.html/.css | 💻 Code |
   | 压缩 | .zip/.rar/.7z/.tar | 📦 Archives |
   | 其他 | 其他扩展名 | 📁 Others |

3. **内容深度分析** (可选，针对文档类文件)
   - 提取文本内容摘要
   - 识别关键词和主题
   - 检测文件关联性

### 阶段 3: 智能分类策略

#### 分类维度 (按优先级应用)

1. **主分类: 按文件类型**
   ```
   /Documents/    - 所有文档类文件
   /Images/      - 图片资源
   /Media/       - 音视频文件
   /Code/        - 代码文件
   /Archives/    - 压缩包
   ```

2. **次级分类: 按内容主题**
   - 基于文件名关键词分析
   - 基于文件内容语义识别
   - 常见主题预设: 合同、报告、方案、简历、发票等

3. **时间分类** (可选)
   - 按年份组织: /2024/, /2023/
   - 按月份组织: /2024-01/, /2024-02/

4. **项目分类** (可选)
   - 识别同一项目相关文件
   - 基于文件名的项目名提取

### 阶段 4: 生成目录总结文档

#### 目录总结文件命名规范
```
[序号]_[文件夹名]_目录总结.md
```

#### 总结文档模板

```markdown
# [文件夹名] 目录总结

**整理时间**: YYYY-MM-DD HH:mm
**文件总数**: N 个
**总大小**: XX MB

## 内容概览

[简要描述此文件夹的主要内容和用途]

## 文件清单

| 文件名 | 类型 | 大小 | 修改时间 | 摘要 |
|--------|------|------|----------|------|
| xxx.pdf | PDF | 1.2MB | 2024-01-15 | 合同文件... |
| xxx.docx | Word | 256KB | 2024-01-20 | 项目方案... |

## 子文件夹

- 📁 `子文件夹名` - 包含 N 个文件，简要描述
```

#### 根目录汇总报告
在目标文件夹根目录生成 `00_总目录总结.md`:
- 全局文件统计
- 分类结构概览
- 关键文件索引

### 阶段 5: 执行整理

1. **预览模式** (默认)
   - 仅生成整理报告，不移动文件
   - 用户确认后再执行实际移动

2. **执行模式**
   - 创建必要的分类子文件夹
   - 按计划移动文件到对应位置
   - 生成所有层级的总结文档

3. **安全机制**
   - 移动前备份原目录结构 (以注释形式记录)
   - 重名文件自动添加序号后缀
   - 跳过系统文件和隐藏文件

### 阶段 6: 输出报告

整理完成后，输出：
1. **操作摘要**: 创建的文件夹数、移动的文件数、生成的文件数
2. **目录结构树**: 可视化展示最终的文件组织结构
3. **详细日志**: 每个文件的具体处理结果

## 核心脚本

### 主整理脚本 `scripts/organize_folder.py`

关键功能:
- `scan_directory(path)`: 递归扫描目录
- `classify_file(file_path)`: 分类单个文件
- `generate_summary(folder_path, files)`: 生成目录总结
- `organize_files(target_path, dry_run=True)`: 执行整理

### 工具函数 `scripts/utils.py`

- `get_file_type(path)`: 获取精确文件类型
- `extract_content_summary(path)`: 提取文本摘要
- `calculate_folder_size(path)`: 计算文件夹大小
- `format_file_size(bytes)`: 格式化文件大小显示

## 使用示例

### 示例 1: 基础整理
```
用户: 帮我整理桌面上的"工作资料"文件夹
技能: 扫描、分析、分类、生成报告
```

### 示例 2: 按类型深度整理
```
用户: 把下载文件夹里的文档按合同、报告、方案分类
技能: 内容分析 + 主题分类 + 执行
```

### 示例 3: 预览模式
```
用户: 给我看看整理方案，不急着执行
技能: 生成详细预览报告，等待确认
```

## 注意事项

1. **大文件处理**: 超过 100MB 的文件单独标记，避免阻塞
2. **敏感文件**: 检测到密码文件、密钥等自动跳过并警告
3. **符号链接**: 不跟随符号链接，避免循环引用
4. **执行权限**: 不修改文件权限属性
5. **增量整理**: 支持对已有整理结构的文件夹进行增量更新

## 扩展建议

- **定期自动整理**: 结合系统任务定时执行
- **多级分类深度**: 可配置分类层级数 (默认 2 级)
- **自定义规则**: 用户可添加文件名模式匹配规则
- **云同步兼容**: 整理前暂停云同步服务，避免冲突
