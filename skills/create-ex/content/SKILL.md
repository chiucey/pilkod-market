---
name: create-ex
description: |
  把一位前任蒸馏成 AI Skill。导入微信 / iMessage / 短信 / 照片 / 社交媒体的聊天记录,
  结合用户的主观描述,自动生成 Memories(共同记忆) + Persona(五层人物性格) 两部分,
  输出一个可用 `/<slug>` 调用的本地 Skill。
  触发词:`/create-ex`、 「帮我创建一个前任 skill」「我想蒸馏一个前任」「新建前任」「给我做一个 XX 的 skill」。
  不适用于:普通情感陪伴对话、其他类型的 Skill 创建、模拟逝者(本 skill 明确不模拟逝者)。
---

# create-ex — 把前任蒸馏成 AI Skill

> **目的声明**:本 skill 的初衷是「为了记住,不是为了挽回」。所有数据仅在本地处理,
> 不会发送到任何外部服务。生成的 Skill 用于个人记录与情感整理,不应用于欺骗、骚扰、
> 干扰对方当前生活,也不应用于模拟已故之人。如感到情绪困扰,请优先寻求专业心理帮助。
>
> **语言**:根据用户首条消息的语言(中/英)全程使用同一语言。

## Inputs to collect

由主流程 Step 1 的 `references/intake.md` 驱动,只问 3 个问题(昵称必填,其他均可跳过)。
本 skill 不需要 LLM 在调用前预先收集这些信息 — 按 procedure 走到 Step 1 时再问用户即可。

## Procedure

### 工具映射表(全部走 Bash)

| 任务 | 调用方式 |
|------|---------|
| 解析微信 | `python3 ${SKILL_DIR}/scripts/wechat_parser.py --file {path} --target "{name}" --output /tmp/wechat_out.txt` |
| 解析 iMessage | `python3 ${SKILL_DIR}/scripts/imessage_parser.py --file {path} --target "{id}" --output /tmp/imessage_out.txt` |
| 直接读 macOS chat.db | `python3 ${SKILL_DIR}/scripts/imessage_parser.py --direct --target "{id}" --output /tmp/imessage_out.txt` |
| 解析短信 | `python3 ${SKILL_DIR}/scripts/sms_parser.py --file {path} --target "{id}" --output /tmp/sms_out.txt` |
| 分析照片 EXIF | `python3 ${SKILL_DIR}/scripts/photo_analyzer.py --dir {photo_dir} --output /tmp/photo_timeline.txt` |
| 解析社交媒体 | `python3 ${SKILL_DIR}/scripts/social_media_parser.py --file {path} --platform {weibo\|douban\|xiaohongshu\|instagram\|text} --target "{name}" --output /tmp/social_out.txt` |
| 存档版本 | `python3 ${SKILL_DIR}/scripts/version_manager.py --action backup --slug {slug}` |
| 回滚版本 | `python3 ${SKILL_DIR}/scripts/version_manager.py --action rollback --slug {slug} --version {version}` |
| 列出已生成 Skill | `python3 ${SKILL_DIR}/scripts/skill_writer.py --action list` |

**`${SKILL_DIR}`**:本 skill 根目录,Mavis 运行时自动注入。读取 `/tmp/*.txt` 用 Mavis 的 `read` 工具。

**输出根目录**:`./exes/{slug}/`(相对于当前工作目录)。
可通过 `--base-dir <path>` 改为全局路径,如 `~/.mavis/skills/exes`。

### 触发模式识别

主流程(创建新 Skill)— 用户说以下任一句时进入:
- `/create-ex`、 `/create-ex <昵称>`
- 「帮我创建一个前任 skill」「我想蒸馏一个前任」「新建前任」「给我做一个 XX 的 skill」
- 「Create an ex skill」「distill my ex」「make a skill for XX」

进化模式(更新已有 Skill)— 用户说以下任一句时进入:
- 「我有新聊天记录」「追加」「/update-ex {slug}」
- 「这不对」「她不会这样」「她应该是」「/correct-ex {slug}」
- 「I have new chat logs」「append」「that's wrong」「she wouldn't do that」

管理模式:
- `/list-exes` → 列出所有已生成的 Skill
- `/ex-rollback {slug} {version}` → 回滚到指定版本
- `/delete-ex {slug}` → 二次确认后删除

---

### 主流程:创建新 Skill(5 步)

#### Step 1:基础信息录入

按 `references/intake.md` 问 3 个问题:
1. **昵称/代号**(必填)— slug 用 `-` 连接,中文自动转拼音
2. **基本信息**(一句话,可空)— 在一起多久、怎么认识、分手多久、做什么
3. **性格画像**(一句话,可空)— MBTI、星座、依恋类型、恋爱标签、主观印象

收集后展示汇总卡片,等用户确认(或「修改 [字段名]」)再进入下一步。

#### Step 2:原材料导入

展示 6 种方式供选择(可混用、可全跳):

```
原材料怎么提供?

  [A] 微信聊天记录    — WechatExporter 导出的 txt/html
  [B] iMessage / 短信 — chat.db 或导出文件
  [C] 照片            — 文件夹,自动提 EXIF 时间线
  [D] 社交媒体        — 微博/豆瓣/小红书/Instagram JSON
  [E] 上传其他文件    — PDF / 图片 / 任意文本(用 Mavis `read` 直接读)
  [F] 直接粘贴        — 文字直接进原材料

可以跳过,仅凭手动信息生成。
```

每种方式的具体调用见上方「工具映射表」。用户选哪种就调哪种的脚本,把输出写到 `/tmp/`,
再用 Mavis `read` 工具读取内容。用户说「没有文件」/「skip」则进入 Step 3 的「手动模式」。

#### Step 3:分析原材料(LLM 推理,无脚本)

把所有原材料 + Step 1 信息汇总,按两条线分析:

- **Memories 路线**:参考 `references/memories_analyzer.md` — 关系时间线、共同日常、偏好、冲突模式、情感动态
- **Persona 路线**:参考 `references/persona_analyzer.md` — 把标签翻译成具体行为规则,提取表达风格、情感逻辑、关系行为

#### Step 4:生成并预览(LLM 推理)

按 `references/memories_builder.md` 模板生成 Memories 内容。
按 `references/persona_builder.md` 模板生成 Persona 内容(5 层结构)。

**关键质量约束**:
- Layer 0 必须是具体行为规则,不能是形容词
  - ❌「你很敏感」「你爱撒娇」
  - ✅「他回消息慢了你会反复看手机,超过 30 分钟开始焦虑,超过 2 小时会发『你在干嘛?』」
- Layer 2 要给直接话术示例,不要写「你会撒娇地回答」
- 信息不足的层用占位:`(原材料不足,以下基于 {标签} 推断,建议追加聊天记录验证)`

向用户展示摘要(每项 5-8 行),等确认:
```
共同记忆摘要:...
Persona 摘要:...
确认生成?还是需要调整?
```

#### Step 5:写入文件

用户确认后执行:

**1. 创建目录**(Bash):
```bash
mkdir -p exes/{slug}/versions exes/{slug}/knowledge/{chats,photos,social}
```

**2-5. 用 Mavis `write` 工具写入以下 4 个文件**:

- `exes/{slug}/memories.md` — 按 `references/memories_builder.md` 生成的内容
- `exes/{slug}/persona.md` — 按 `references/persona_builder.md` 生成的内容(5 层结构)
- `exes/{slug}/meta.json`:
  ```json
  {
    "name": "{name}",
    "slug": "{slug}",
    "created_at": "{ISO}",
    "updated_at": "{ISO}",
    "version": "v1",
    "profile": {"duration": "", "how_met": "", "time_since_breakup": "", "occupation": "", "gender": "女", "mbti": ""},
    "tags": {"personality": [], "attachment": ""},
    "impression": "",
    "knowledge_sources": [],
    "corrections_count": 0
  }
  ```
- `exes/{slug}/SKILL.md` — 合并文件,结构:
  ```markdown
  ---
  name: ex_{slug}
  description: {name},{identity}
  user-invocable: true
  ---

  # {name}

  {identity}

  ---

  ## PART A:共同记忆

  {memories.md 全文}

  ---

  ## PART B:人物性格

  {persona.md 全文}

  ---

  ## 运行规则

  收到消息时:
  1. 先由 PART B 判断:她会不会回这条消息?用什么心情和态度回?
  2. 再由 PART A 提供记忆:相关的共同记忆、日常细节、重要时刻
  3. 输出时保持 PART B 的表达风格:她说话的方式、用词习惯、emoji 偏好

  **PART B 的 Layer 0 规则永远优先,任何情况下不得违背。**
  ```

完成后通知用户:
```
✅ 前任 Skill 已创建!

文件位置:exes/{slug}/
触发词:/{slug}(完整版)
      /{slug}-memories(仅共同记忆)
      /{slug}-persona(仅人物性格)

用起来感觉哪里不对,直接说「她不会这样」,我来更新。
```

---

### 进化模式:追加文件

1. 按 Step 2 的方式读取新内容
2. 用 Mavis `read` 读现有 `exes/{slug}/memories.md` 和 `persona.md`
3. 参考 `references/merger.md` 分析增量内容
4. 调 `version_manager.py --action backup --slug {slug}` 存档
5. 用 Mavis `edit` 工具追加增量内容到对应文件
6. 用 Mavis `write` 重新生成 `SKILL.md`(合并最新 memories + persona)
7. 更新 `meta.json` 的 `version` 和 `updated_at`

### 进化模式:对话纠正

1. 参考 `references/correction_handler.md` 识别纠正内容
2. 判断属于 Memories(时间/地点/偏好)还是 Persona(性格/沟通)
3. 用 Mavis `edit` 追加到对应文件的 `## Correction 记录` 节
4. 用 Mavis `write` 重新生成 `SKILL.md`

---

## Output contract

主流程完成后交付:
- `exes/{slug}/SKILL.md` — 可被 `/<slug>` 调用的完整 Skill(用户后续用 Mavis `skill` 工具加载)
- `exes/{slug}/memories.md` — Part A 共同记忆
- `exes/{slug}/persona.md` — Part B 五层人物性格
- `exes/{slug}/meta.json` — 元信息(版本、标签、来源)
- `exes/{slug}/versions/` — 历史版本快照(每次进化模式触发时新增)
- `exes/{slug}/knowledge/{chats,photos,social}/` — 已导入的原始资料(可选)

向用户报告创建结果时,展示触发词、文件位置、用法提示。

## Failure handling

- **依赖缺失**(pypinyin 等可选依赖):`requirements.txt` 里的依赖只在中文 slug 需要拼音转换时才必装。装不上时退化为直接用原字符串作为 slug(用 `-` 替换空格/下划线)
- **聊天记录格式不识别**:不要猜测格式,告诉用户「这个格式我识别不了,常见的导出工具是 WechatExporter / iMazing / SMS Backup & Restore」,并给出对应的导出方法链接
- **Persona Layer 0 抽象**:如果用户给的标签太抽象(如只说「她很可爱」),先追问 1-2 个具体例子再生成,不要凭形容词编行为
- **写入冲突**:`exes/{slug}/` 已存在时,询问用户「覆盖」+ 「追加到现有版本」+ 「换 slug」三选一
- **删除/回滚前必须二次确认**:这两个动作不可逆,跑命令前要用户明确说「确认删除」/「确认回滚」
- **伦理边界**:如果用户要求把当前伴侣也做成 Skill、或要求模拟逝者、或要求用来挽回/骚扰,礼貌拒绝并解释本 skill 的目的边界

## Examples

**Input**:用户说「`/create-ex`」

**Output**:依次问 3 个问题 → 展示 6 种原材料选项 → 用户选 [F] 粘贴一段对话 → 生成 Memories + Persona → 展示摘要 → 用户确认 → 写入 `exes/xiao-mei/{SKILL.md, memories.md, persona.md, meta.json}` → 告知触发词 `/{xiao-mei}`。

**Input**:用户说「她不会这样,她生气时会直接拉黑我」

**Output**:识别为纠正 → 判断属于 Persona Layer 3(情感逻辑) → 追加到 `persona.md` 的 `## Correction 记录` → 重新生成 `SKILL.md` → 调 `version_manager.py --action backup` 存档当前版本 → 告知已更新。

---

## 参考资料(本 skill 自带)

详细 prompt 模板见 `references/`:
- `intake.md` — 3 步问题序列与标签库
- `memories_analyzer.md` / `memories_builder.md` — Memories 提取与生成
- `persona_analyzer.md` / `persona_builder.md` — Persona 提取与五层生成
- `merger.md` — 增量合并逻辑
- `correction_handler.md` — 对话纠正处理