---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: cc14c4b2b4af5fb8f2e698dd472e8d9b
    PropagateID: cc14c4b2b4af5fb8f2e698dd472e8d9b
    ReservedCode1: 3045022100d2ecd0d0340f1b8b32e69c1bc96d286f818da5257f76f1dc8dcea085a04bfc4a02206dbcc9b17a26e71e1074aa7bc027f99a29eed84b41810af72bccbaa91880e010
    ReservedCode2: 30440220619de693fde2825f3f0eccf474531d32593cd4222be2626093126584499dd77c02206016f5377081eaadf88ce177de3734745fee04f2a6e7bf3c1f980c49c6c917a0
description: 根据JSON配置文件批量生成故事插画图片。当用户提供包含图片生成配置的JSON文件，且文件中包含prompt、metadata、style_guide等结构，以及_character_profiles人物设定和中文【】括号包裹的提示词时使用此技能。
name: story-image-generator
---

# 故事图片生成器

根据JSON配置文件批量生成故事插画图片，支持人物/怪物一致性约束。

## 功能概述

此技能从JSON配置文件中提取图片生成提示词，结合`_character_profiles`中的人物统一设定，生成风格统一的系列图片。

### 核心特性

1. **人物参考图生成** - 先为每个`_character_profiles`中的人物生成参考图
2. **一致性约束** - 使用`subject_reference`模式保持人物形象一致性
3. **批量生成** - 按分组自动批量生成故事插画

### JSON配置结构

```json
{
  "0": { "prompt": "...", "metadata": {...}, "style_guide": "..." },
  "1": { "prompt": "...", "metadata": {...}, "style_guide": "..." },
  "-1": { "prompt": "...", "metadata": { "type": "title" } },
  "-2": { "prompt": "...", "metadata": { "type": "ending" } },
  "_character_profiles": {
    "人物名称": { "基础设定": "...", "完整描述": "...", "阶段状态": [...] }
  }
}
```

### 中文提示词标签解析

| 标签 | 说明 |
|------|------|
| 【场景描述】 | 图片整体场景内容 |
| 【构图要求】 | 画面构图要求说明 |
| 【道具细节】 | 道具、服装、足迹等细节 |
| 【人物基础设定】 | 主要人物基础设定，名称与`_character_profiles`对应 |
| 【人物当前状态】 | 特定场景中人物的具体描述 |
| 【风格定义】 | 图片风格定义 |

## 使用流程

### 步骤1：读取JSON配置

使用`Read`工具读取用户提供的JSON文件路径。

### 步骤2：生成人物参考图（关键步骤）

1. 遍历`_character_profiles`中的每个人物
2. 根据人物的基础设定和完整描述，生成英文提示词
3. 调用`image_synthesize`生成人物参考图
4. 保存参考图路径到人物映射表

**参考图命名**：`{人物名称}_ref.png`

### 步骤3：解析并组装提示词

从JSON中提取每个分组的数据：

1. 读取`prompt`字段中的各中文标签内容
2. 如有【人物形象名称】引用，从`_character_profiles`获取对应人物的`完整描述`
3. 组合`style_guide`作为风格约束
4. 组装完整英文提示词

### 步骤4：生成图片（带一致性约束）

对于每个分组：

1. 调用`image_synthesize`生成图片
2. **关键**：如果该分组中使用了`_character_profiles`中的人物：
   - 设置`reference_type`为`"subject"`
   - 使用`input_files`传入对应人物的参考图路径
3. 保持人物形象一致性

**图片输出路径（重要）**：
- 必须将 `output_file` 设置为完整路径：`/workspace/{故事标题}_images/frames/{文件名}.jpg`
- 人物参考图输出到：`/workspace/{故事标题}_images/characters/{人物名}_ref.png`
- 示例：`output_file: "/workspace/海人_images/frames/001.jpg"`
- 不要使用临时目录或 intermediate 文件夹，图片必须直接生成到最终目录

**API参数配置（重要）**：
- 分辨率：使用 `resolution: "1K"` 或留空（默认 1080x1920），避免使用 2K 导致图片过大
- 宽高比：使用 `aspect_ratio: "9:16"` 确保图片比例正确

```json
{
    "reference_type": "subject",
    "input_files": ["/workspace/海人_images/characters/姚某_ref.png"],
    "prompt": "...",
    "output_file": "/workspace/海人_images/frames/001.jpg",
    "aspect_ratio": "9:16",
    "resolution": "1K"
}
```

### 步骤5：保存输出 + 复制 JSON

将生成的图片保存到用户指定目录或与JSON文件同目录。

**目录命名规则**：
- 从 JSON 的 `story_theme` 字段获取故事标题
- 若 `story_theme` 为空，则从 `-1` 标题页或第一个分组的 `subtitle_text` 中提取故事标题
- 标题清洗：移除特殊字符、空格转下划线、截取前 20 字符
- 示例：`subtitle_text: "中国古代妖怪故事 之 《海人》"` → 目录名 `海人`
- 最终路径：`/workspace/{故事标题}_images/`（例如 `/workspace/海人_images/`）

**输出目录结构**：
```
/workspace/海人_images/
├── frames/          # 故事插画
│   ├── -1_title.jpg
│   ├── 000.jpg
│   ├── 001.jpg
│   └── ...
├── characters/      # 人物参考图
│   ├── 姚某_ref.png
│   └── 徒弟_ref.png
└── story.json       # 对应的 JSON 配置文件（自动复制，方便字幕对照）
```

**重要**：生成图片完成后，**必须**执行以下两步：

1. 将原始 JSON 文件复制到输出目录：
```bash
cp {原始JSON路径} /workspace/{故事标题}_images/story.json
# 同时复制一份到 web app 静态目录：
cp {原始JSON路径} /workspace/story-manager/public/story-images/{故事标题}_images/story.json
```

这样在字幕对照界面可以直接从故事目录加载 JSON，无需手动上传。

### 步骤6：验证图片分辨率（重要）

图片生成后，**必须**先检查分辨率是否符合要求，再进行打包。

**分辨率标准**：
- 宽高比：9:16（允许 ±5% 误差）
- 最小分辨率：宽或高 >= 800px
- 默认分辨率：1080x1920
- 可选分辨率：2K (2160x3840)

**检查命令**：
```bash
python scripts/validate_images.py /workspace/海人_images/
```

**详细检查（显示所有图片）**：
```bash
python scripts/validate_images.py /workspace/海人_images/ -v
```

**输出报告示例**：
```
============================================================
📊 图片分辨率检查报告
============================================================

📈 统计:
   总图片数: 25
   ✅ 符合要求: 22
   ⚠️ 需要处理: 3
   ❌ 错误: 0
```

### 步骤7：处理不符合要求的图片

如果检查发现图片不符合分辨率要求，使用处理脚本进行调整：

**干运行模式（预览需要处理的文件）**：
```bash
python scripts/process_images.py /workspace/海人_images/ --dry-run
```

**实际处理（调整所有不符合要求的图片）**：
```bash
python scripts/process_images.py /workspace/海人_images/
```

**使用 2K 分辨率处理**：
```bash
python scripts/process_images.py /workspace/海人_images/ --2k
```

**处理脚本功能**：
- 自动调整宽高比至 9:16（通过智能裁剪）
- 将图片缩放至目标分辨率
- 自动备份原始图片到 `_original_backup/` 目录
- 统一输出为高质量 JPEG 格式

### 步骤8：打包压缩（下载包）

图片生成完成后，将输出目录打包为 ZIP 文件，方便一次性下载全部内容：

```bash
cd /workspace && zip -r {故事标题}_images.zip {故事标题}_images/
```

**输出文件命名规则**：
- ZIP 包：`{故事标题}_images.zip`（例如 `海人_images.zip`）
- 内部目录结构保持不变

**ZIP 包内结构示例**：
```
海人_images.zip/
├── frames/          # 故事插画
│   ├── -1_title.jpg
│   ├── 000.jpg
│   ├── 001.jpg
│   └── ...
└── characters/      # 人物参考图
    ├── 姚某_ref.png
    └── 徒弟_ref.png
```

**提示**：生成完毕后告知用户 ZIP 包的路径（`/workspace/海人_images.zip`），并说明文件可直接在对话中点击下载。

## 输出配置

| 配置项 | 值 |
|--------|------|
| 分辨率 | 1080x1920（默认）或 2K (2160x3840) |
| 宽高比 | 9:16（允许 ±5% 误差） |
| 最小分辨率 | 宽或高 >= 800px |
| 文件命名 | `{group_id:03d}.jpg` |
| 人物参考图命名 | `{人物名称}_ref.png` |
| 参考模式 | subject_reference |
| 输出格式 | JPG/PNG |
| 输出目录 | `/workspace/{故事标题}_images/` |
| ZIP 包 | `/workspace/{故事标题}_images.zip` |

## subject_reference 模式说明

MiniMax图片生成API支持`subject_reference`模式，用于保持主体一致性：

- **适用场景**：系列图片中需要保持人物/怪物外观一致
- **使用方式**：先为角色生成参考图，后续图片以参考图为主体
- **参数配置**：
  - `reference_type`: `"subject"` 表示以参考图为主体的模式
  - `input_files`: 参考图片路径

## 提示词组装示例

### 人物参考图提示词

基于`_character_profiles`中的"北方商人"：

```
Male, about 45 years old, square-round face, bronze complexion, grey hair tied up in hair bun, short grey beard, wearing black headscarf, height about 170cm, medium build, aged and weathered face, wearing wide-sleeved long robe with waist belt. Traditional Chinese ink painting style.
```

### 分组图片提示词

原始prompt：
```
【场景描述】：辽阔的海面上，一艘铜船正在缓缓航行...
【人物基础设定】：
【北方商人】基础设定：男性，约45岁，方圆脸，古铜色肤色...
【人物当前状态】：
【北方商人】当前状态：头戴斗笠，衣衫被海风吹干...
```

组装后提示词：
```
Vast sea surface, a copper-clad merchant ship sailing slowly. Male, about 45 years old, square-round face, bronze complexion, grey hair, short grey beard, wearing black headscarf, long robe. He is standing on the ship bow, clothes dried by sea wind, weathered face showing fatigue. Traditional Chinese ink painting style, light ink colors, freehand elegance, appropriate white space, elegant coloring.
```

## 错误处理

- JSON解析失败：提示用户检查文件格式
- 人物参考图生成失败：记录失败的人物名，跳过使用该人物的分组
- 图片生成失败：记录失败的group_id并继续处理其他分组
- 文件命名冲突：自动添加序号后缀

## 工作流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      JSON配置文件                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐     ┌─────────────────┐                │
│  │ _character_profiles │ ──→ │  生成参考图      │                │
│  │  (人物定义)      │     │  (subject_ref) │                │
│  └─────────────────┘     └────────┬────────┘                │
│                                   │                         │
│                                   ▼                         │
│  ┌─────────────────┐     ┌─────────────────┐                 │
│  │ 分组数据         │ ──→ │  组装提示词      │                 │
│  │ (0, 1, 2...)    │     │  + 参考图引用    │                 │
│  └─────────────────┘     └────────┬────────┘                 │
│                                   │                         │
│                                   ▼                         │
│                          ┌─────────────────┐                 │
│                          │  image_synthesize│                 │
│                          │ (带reference)   │                 │
│                          └────────┬────────┘                 │
│                                   │                         │
│                                   ▼                         │
│                          ┌─────────────────┐                 │
│                          │  输出图片文件    │                 │
│                          │  (000.jpg...)   │                 │
│                          └────────┬────────┘                 │
│                                   │                         │
│                                   ▼                         │
│                          ┌─────────────────┐                 │
│                          │  验证分辨率      │                 │
│                          │ validate_images │                 │
│                          └────────┬────────┘                 │
│                                   │                         │
│                                   ▼                         │
│                          ┌─────────────────┐                 │
│                          │  处理不符合要求   │                 │
│                          │ process_images  │                 │
│                          │ (可选步骤)       │                 │
│                          └────────┬────────┘                 │
│                                   │                         │
│                                   ▼                         │
│                          ┌─────────────────┐                 │
│                          │  打包为ZIP文件   │                 │
│                          │  (海人_images.zip)│                 │
│                          └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```
