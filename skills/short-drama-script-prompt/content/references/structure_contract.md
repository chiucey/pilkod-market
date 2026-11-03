# Structure Contract

## Document Hierarchy

The output follows a flat, lightweight structure with exactly **3 top-level sections**. No expansion beyond this hierarchy is permitted.

```
## 输出要求
├── 每集拆分规格 (bullet list)
└── 每组镜头必须包含
    ├── ### 1. 出场人物 (plain text)
    ├── ### 2. 位置关系 (bullet list)
    ├── ### 3. 剧本 + 情绪特写链（核心部分）
    │   ├── **剧本还原** (bullet list)
    │   └── **情绪特写链**（重点） (bullet list)
    └── ### 4. 情绪特写要求 (bullet list)

## 示例格式
└── ``` code block with template

## 注意事项
└── 1. 2. 3. 4. 5. 6. (numbered list)
```

## Section Definitions

### 1. ## 输出要求

Contains two sub-sections:

**A. 每集拆分规格**
Bullet list with exactly 3 items:
- 10 组镜头 × 15 秒 = 150 秒 / 集
- 时间范围格式：00:00-00:15, 00:15-00:30 ... 以此类推
- 每组镜头时长最大值为15秒，超过部分延长至下一组

**B. 每组镜头必须包含**
Four numbered sub-sections using `###`:

#### ### 1. 出场人物
Plain text description: 列出本组所有出场人物姓名

#### ### 2. 位置关系
Bullet list with 4 items:
- 每个人的站位/坐位
- 与其他人物的空间关系
- 人物面向方向
- 场景布局（如：站在客厅入户门口、端坐主位沙发、分列沙发两侧等）

#### ### 3. 剧本 + 情绪特写链（核心部分）
Contains two bold-labeled sub-parts:

**剧本还原** (bullet list):
- 完整还原该时间段的台词
- 保留所有标点符号
- 按说话顺序排列

**情绪特写链**（重点） (bullet list):
- 每个出场人物在该时刻的面部表情细节
- 眼神变化（瞳孔、眼神方向）
- 肢体动作细节（手指颤抖、后退半步、身体前倾等）
- 情绪层次变化
- 特殊道具（打火机、汽油、行李箱等）细节
- 氛围营造

#### ### 4. 情绪特写要求
Bullet list with 4 items:
- 面部表情：嘴角抽搐、眼眶泛红、瞳孔骤缩等
- 眼神：错愕、怨毒、癫狂、冰冷等
- 肢体：颤抖、僵硬、后退、扑倒等
- 声音：哽咽、嘶吼、冷笑等

### 2. ## 示例格式

A code block (```) containing the exact template:

```
第 X 集 场景描述
第 1 组 00:00-00:15
【出场人物】角色A、角色B
【位置关系】角色A站在门口，角色B端坐沙发...

【场景图】参考@图片 的场景布局，将人物放置在对应的位置根据剧本描述的对话内容和人物神态动作，生成连贯的室内对话视频
【全局提示词】你自己安排爆款短剧风格多机位与高预算运镜，多角度特写，超特写（避免全景）
【强制声明】：无背景音乐；无字幕，无文字叠加，无 UI，禁止出文字字幕在画面中

【剧本 + 情绪特写链】角色A推门而入，脸上堆着刻意讨好的假笑，扬声喊出台词【台词内容】△表情描述，肢体动作...
```

### 3. ## 注意事项

Numbered list with exactly 6 items:
1. 情绪特写要具体到肌肉层面
2. 善用△符号标记动作和表情
3. 台词用【】标注
4. 保持剧情的连贯性和情绪递进
5. 结尾组要有悬念或情感高潮
6. 禁止删减任何情节和台词，输出前必须核查

## Per-Shot Prompt Output Structure

When actually generating prompts from a script, each shot group follows this structure:

```
第 X 集 场景描述
第 N 组 00:00-00:15
【出场人物】角色A、角色B
【位置关系】角色A站在门口，角色B端坐沙发...

【场景图】参考@图片 的场景布局，将人物放置在对应的位置根据剧本描述的对话内容和人物神态动作，生成连贯的室内对话视频
【全局提示词】你自己安排爆款短剧风格多机位与高预算运镜，多角度特写，超特写（避免全景）
【强制声明】：无背景音乐；无字幕，无文字叠加，无 UI，禁止出文字字幕在画面中

【剧本 + 情绪特写链】角色A推门而入，脸上堆着刻意讨好的假笑，扬声喊出台词【台词内容】△表情描述，肢体动作...
```

### Fixed Elements Block
These three elements must appear **exactly as written**, with blank lines before and after:

```
【场景图】参考@图片 的场景布局，将人物放置在对应的位置根据剧本描述的对话内容和人物神态动作，生成连贯的室内对话视频
【全局提示词】你自己安排爆款短剧风格多机位与高预算运镜，多角度特写，超特写（避免全景）
【强制声明】：无背景音乐；无字幕，无文字叠加，无 UI，禁止出文字字幕在画面中
```

> Note: The parenthetical explanation "（【场景图】和 【全局提示词】 和【强制声明】 为固定不变项 直接输出即可，无需任何处理，但前后需要空一行）" is documentation only — do NOT include it in actual output.

### Core Section: 【剧本 + 情绪特写链】

**Composition rules:**
- Narrative action description comes first (character enters, gestures, etc.)
- Dialogue wrapped in `【】`
- After dialogue, append `△` followed by facial expression and body movement details
- Include emotional state transitions within the description
- Mention prop details when relevant

**Emotional detail taxonomy:**
| Category | Examples |
|----------|----------|
| 面部表情 | 嘴角抽搐、眼眶泛红、瞳孔骤缩、假笑、冷笑 |
| 眼神 | 错愕、怨毒、癫狂、冰冷、躲闪、直视 |
| 肢体 | 颤抖、僵硬、后退、扑倒、手指收紧、身体前倾 |
| 声音 | 哽咽、嘶吼、冷笑、低语、颤抖 |

## Repetition Rules

- The fixed elements block (`【场景图】`, `【全局提示词】`, `【强制声明】`) repeats **identically** in every shot group — never modify
- The shot-group structure repeats for every group in the episode
- Episode headers separate multi-episode scripts

## Cross-Reference and Numbering

- Episode numbers: consecutive integers (第 1 集, 第 2 集, ...)
- Shot group numbers: restart at 1 for each new episode
- Time ranges: continuous within an episode, do not reset between episodes

## Page Breaks and Front Matter

- **No formal front matter** — no cover page, no TOC, no headers/footers
- **No page breaks between sections** — the reference flows continuously
- Page breaks between episodes are acceptable but not mandatory
- No headers or footers needed
