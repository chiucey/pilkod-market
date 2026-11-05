# Article Writer - 技术设计方案

## 一、架构对比分析

### 1.1 Novel-Writer 核心架构

```
novel-writer/
├── CLI系统 (cli.ts)
│   ├── init命令 - 项目初始化
│   ├── upgrade命令 - 版本升级
│   ├── plugins命令 - 插件管理
│   └── check命令 - 环境检查
│
├── 命令生成系统 (scripts/build/)
│   ├── generate-commands.sh - 多平台命令生成
│   └── 模板转换 (Markdown → TOML)
│
├── 插件系统 (src/plugins/)
│   ├── PluginManager - 插件加载/注入
│   └── config.yaml - 插件配置规范
│
├── 斜杠命令 (templates/commands/)
│   ├── constitution.md - 创作宪法
│   ├── specify.md - 故事规格
│   ├── clarify.md - 澄清决策
│   ├── plan.md - 创作计划
│   ├── tasks.md - 任务分解
│   ├── write.md - 章节写作
│   └── analyze.md - 综合验证
│
└── 支持文件
    ├── memory/ - 记忆系统(constitution等)
    ├── spec/ - 规范和预设
    └── scripts/ - 执行脚本(bash/powershell)
```

**核心优势:**
1. **跨平台命令系统** - 一套模板生成13个平台的命令
2. **插件热加载** - 动态注入命令到各AI平台
3. **脚本预检机制** - 命令执行前验证状态
4. **完善的文件管理** - 分层的配置和数据结构

### 1.2 Article-Writer 架构设计

```
article-writer/
├── CLI系统 (保留并改造)
│   ├── content init - 项目初始化
│   ├── content workspace - 工作区管理
│   ├── content materials - 素材库管理
│   └── content upgrade - 版本升级
│
├── 命令生成系统 (复用)
│   └── 保持不变,继续支持13个平台
│
├── 插件系统 (扩展)
│   ├── PluginManager (保留)
│   └── 新增插件:
│       ├── materials-manager - 素材库管理
│       ├── image-generator - 配图生成
│       └── research-assistant - 信息搜索
│
├── 斜杠命令 (重构)
│   ├── specify.md - 保存需求
│   ├── research.md - 信息搜索 ⭐
│   ├── topic.md - 选题讨论 ⭐
│   ├── collab-doc.md - 协作文档
│   ├── style-learn.md - 风格学习
│   ├── collect.md - 素材搜索 ⭐
│   ├── write.md - 创作初稿
│   ├── audit.md - 三遍审校 ⭐
│   └── images.md - 文章配图 ⭐
│
└── 支持文件
    ├── memory/ (改造)
    │   ├── constitution.md - 写作原则
    │   ├── style-reference.md - 风格参考
    │   └── personal-voice.md - 个人语料
    ├── materials/ (新增核心模块)
    │   ├── raw/ - 原始数据(CSV/JSON)
    │   ├── indexed/ - 主题索引
    │   └── archive/ - 历史文章
    ├── _knowledge_base/ (新增)
    │   └── 调研结果保存
    └── spec/ (简化)
        └── presets/ - 工作区模板、审校规范
```

## 二、核心模块设计

### 2.1 两层判断系统

#### 第一层: 工作区路由 (根目录 CLAUDE.md)

```typescript
// 伪代码逻辑
interface WorkspaceDetection {
  detectWorkspace(): WorkspaceType {
    const cwd = process.cwd()

    // 检测当前目录
    if (cwd.includes('workspaces/wechat')) {
      return 'wechat'
    } else if (cwd.includes('workspaces/video')) {
      return 'video'
    } else if (cwd.includes('workspaces/general')) {
      return 'general'
    } else {
      // 在根目录,询问用户
      return 'ask-user'
    }
  }

  loadWorkspaceConfig(type: WorkspaceType): WorkspaceConfig {
    // 读取对应工作区的 CLAUDE.md
    const configPath = `workspaces/${type}/CLAUDE.md`
    return parseConfig(configPath)
  }
}
```

**实现方式:**
```markdown
<!-- 根目录 CLAUDE.md -->
# 写作助手 - 工作区路由

当用户发起写作任务时:

1. **检测当前目录位置**
   - 使用 `pwd` 命令获取当前路径
   - 判断是否在 `workspaces/wechat|video|general/` 中

2. **加载工作区配置**
   - 如果在工作区内,读取该工作区的 `CLAUDE.md`
   - 如果在根目录,询问用户:
     ```
     请选择工作区:
     1. 公众号写作 (wechat)
     2. 视频脚本 (video)
     3. 通用内容 (general)
     或输入新文章主题,我将帮你创建项目
     ```

3. **执行工作区特定流程**
   - 公众号: 9步流程 + 配图需求
   - 视频: 简化流程 + 分镜说明
   - 通用: 灵活配置
```

#### 第二层: 任务类型识别 (工作区 CLAUDE.md)

```markdown
<!-- workspaces/wechat/CLAUDE.md -->
# 公众号写作工作区

## 任务类型判断

当用户发起任务时,先判断类型:

### A. 新写作任务(有完整brief)
**识别特征:** 用户提供了详细的写作需求/商单brief
**执行流程:** 完整9步流程
1. `/specify` 保存brief
2. `/research` 信息搜索
3. `/topic` 选题讨论
... (完整流程)

### B. 新写作任务(无brief只有需求)
**识别特征:** 用户只给了主题或简单描述
**执行流程:** 先补充brief
1. 询问关键信息(目标读者、字数、风格等)
2. 生成brief草稿,让用户确认
3. 保存后进入完整流程

### C. 修改已有文章
**识别特征:** 用户说"修改XX文章"或"优化XX部分"
**执行流程:** 简化流程
1. 读取原文 (`articles/*/draft.md` 或 `final.md`)
2. 理解修改需求
3. 应用修改并输出对比

### D. 文章审校/降AI味
**识别特征:** 用户说"审校"、"降低AI味"、"检查质量"
**执行流程:** 跳转审校命令
1. 直接调用 `/review` 命令
2. 询问审校模式(content/style/detail)
3. 输出修改建议

### E. 快速咨询
**识别特征:** 用户问问题,但不涉及文件操作
**执行流程:** 直接回答
- 不创建文件
- 不启动完整流程
- 快速响应后结束
```

### 2.2 个人素材库系统

#### 数据结构设计

```
materials/
├── raw/                          # 原始数据(不可编辑)
│   ├── jike-all.csv              # 即刻动态导出
│   │   格式: 时间,内容,链接,点赞数
│   ├── weibo-posts.json          # 微博导出
│   └── xiaohongshu-notes.json    # 小红书笔记
│
├── indexed/                      # 主题索引(手动整理)
│   ├── ai-tools.md               # AI工具相关素材集合
│   │   结构:
│   │   ## Claude Code使用体验
│   │   - 原始动态: "用了两周,确实比Cursor好"
│   │   - 发布时间: 2024-12-10
│   │   - 适用场景: 开头引入、工具对比
│   │
│   ├── product-dev.md            # 产品开发经验
│   └── personal-views.md         # 个人观点库
│
└── archive/                      # 历史文章存档
    └── 2024/
        ├── 12/
        │   └── claude-code-review.md
        └── 11/
```

#### 素材搜索实现

**方法A: 搜索原始CSV (推荐)**

```bash
# scripts/bash/collect.sh
#!/bin/bash

MATERIALS_DIR="materials/raw"
KEYWORD="$1"

# 检查素材库
if [ ! -d "$MATERIALS_DIR" ]; then
  echo "❌ 素材库未初始化"
  echo "运行: content materials init"
  exit 1
fi

# 列出可搜索数据源
echo "📚 可用数据源:"
ls -1 "$MATERIALS_DIR"

# 搜索示例
echo ""
echo "💡 搜索示例:"
echo "  使用 Grep 工具搜索关键词:"
echo "  pattern: '高德|扫街榜|地图'"
echo "  path: 'materials/raw/jike-all.csv'"
echo "  output_mode: 'content'"
echo "  -n: true  # 显示行号"
```

**命令模板 (`/collect`)**

```markdown
---
description: 从个人素材库搜索真实经历和观点
scripts:
  sh: .specify/scripts/bash/collect.sh
---

# 个人素材库搜索

## 执行流程

### 1. 分析当前文章主题
从 `articles/*/specification.md` 或用户需求中提取关键词。

**示例:**
- 文章主题: "高德扫街榜使用体验"
- 提取关键词: ["高德", "扫街榜", "地图", "导航"]

### 2. 搜索原始数据 (方法A - 推荐)

使用 **Grep** 工具搜索 CSV 文件:

```
pattern: "高德|扫街榜|地图"
path: "materials/raw/jike-all.csv"
output_mode: "content"
-i: true  # 忽略大小写
-n: true  # 显示行号
-C: 2     # 显示上下文(前后2行)
```

**返回示例:**
```
123: 2024-11-20,高德扫街榜太上头了,连续打卡三天...,https://...
156: 2024-12-01,地图导航还是高德准,百度老出错,https://...
```

### 3. 查询主题索引 (方法B - 辅助)

如果是常见主题,直接读取已整理的索引:

```
Read file_path="materials/indexed/ai-tools.md"
```

查找相关章节,例如:
```markdown
## 高德地图使用体验

- **原始动态**: "扫街榜功能让遛弯变成了游戏,每天多走2000步"
- **发布时间**: 2024-11-15
- **观点**: 游戏化设计激励效果显著
- **适用场景**: 产品设计案例、用户激励讨论
```

### 4. 展示搜索结果

将搜索到的素材展示给用户:

```
🔍 找到 3 条相关素材:

1️⃣ [2024-11-20] 高德扫街榜使用体验
   "连续打卡三天,发现这个功能太上头..."

2️⃣ [2024-12-01] 地图导航对比
   "地图导航还是高德准,百度老出错..."

3️⃣ [2024-11-15] 游戏化设计案例
   "扫街榜让遛弯变成游戏,每天多走2000步"

💡 我将在以下场景使用这些素材:
- 文章开头: 用素材1引入个人经历
- 观点支撑: 用素材3说明游戏化激励效果
- 对比论证: 用素材2增强可信度

是否继续? (yes/no)
```

### 5. 融入文章

**重要原则:**
- ✅ 改写成长文逻辑(扩展、解释、升华)
- ✅ 保持真实性(不夸大、不编造)
- ❌ 禁止直接复制粘贴
- ❌ 禁止拼接多条动态

**改写示例:**

❌ **直接粘贴** (生硬):
> 我在即刻发过:"高德扫街榜太上头了,连续打卡三天"。

✅ **改写融入** (自然):
> 最近迷上了高德的扫街榜功能。这个看似简单的打卡机制,让我每天遛弯都多了一份期待——路过新街道就能点亮地图,连续三天打卡还有徽章奖励。不知不觉,每天多走了2000步。

## 常见使用场景

### 场景1: 文章开头引入
**需求:** 用真实经历代替抽象开场
**搜索:** 主题相关的个人体验
**改写:** 扩展成200-300字的引入段落

### 场景2: 观点支撑
**需求:** 增强观点可信度
**搜索:** 个人评价、使用感受
**改写:** 结合论点展开说明

### 场景3: 案例展示
**需求:** 提供具体案例
**搜索:** 真实项目经历
**改写:** 补充背景和结果

### 场景4: 结尾升华
**需求:** 个人洞察总结
**搜索:** 深度思考类动态
**改写:** 提炼核心观点

## 注意事项

1. **优先使用最新素材** - 时间越近越真实
2. **避免过度引用** - 每篇文章最多使用3-5条素材
3. **保持语境一致** - 素材语气要与文章整体风格匹配
4. **标注时间节点** - 如需要,可说明"去年"、"最近"等时间信息
5. **尊重隐私** - 如涉及他人,进行匿名化处理
```

### 2.3 三遍审校机制

#### 审校模式设计

```markdown
---
description: 三遍审校机制 - 系统化降低AI检测率
argument-hint: [模式:content|style|detail] [文件路径]
allowed-tools: Read(//workspaces/**/articles/**), Write(//workspaces/**/articles/**)
---

# 三遍审校命令

## 模式选择

用户可以指定审校模式,或按推荐顺序依次执行:

### 模式1: content (内容审校)

**目标:** 确保事实准确、逻辑清晰、结构合理

**检查清单:**
- [ ] 事实准确性
  - 数据、时间、产品名称无误
  - 版本号、功能描述与实际一致
  - 引用信息有来源(检查 `_knowledge_base/`)

- [ ] 逻辑一致性
  - 论点与论据对应
  - 前后无矛盾表述
  - 因果关系成立

- [ ] 结构合理性
  - 开头hook有效(前3段抓人)
  - 中间论证充分
  - 结尾呼应主题
  - 无跑题内容

- [ ] 真实性验证
  - 所有案例、数据来自真实素材或调研
  - 标记可疑的"AI编造"内容
  - 检查是否有未溯源的数据

**输出格式:**
```
📋 内容审校报告

✅ 通过项 (5项)
- 产品名称准确
- 数据有来源(见 _knowledge_base/claude-code-2025-01-15.md)
- ...

⚠️ 需修改 (2项)
【位置】第3段第2句
【问题】"显著提升开发效率" - 过于抽象,无数据支撑
【建议】替换为具体数字,如"平均每个项目节省3-5小时"
【来源】检查 materials/ 是否有相关测试数据

【位置】第7段
【问题】时间线混乱 - 先提"去年"再提"最近",实际都是2024年
【建议】统一时间表述

是否应用修改? (yes/no/edit)
```

### 模式2: style (风格审校 - 降AI味核心)

**目标:** 删除AI痕迹,增加真实感和个性化

**检查清单:**
- [ ] 删除AI套话
  - "在当今时代"
  - "综上所述"
  - "值得注意的是"
  - "随着...的发展"
  - "不仅...而且..."(高频出现)

- [ ] 拆解AI句式
  - "不是...而是..."连续出现 → 改为多样化表达
  - 长排比句(3个以上) → 拆短或改为并列
  - 对称结构过多 → 打破规律

- [ ] 替换书面词汇
  - "显著提升" → 具体数字 + 简单动词
  - "充分利用" → "用好"
  - "进行XX操作" → 直接用动词
  - "呈现出XX特征" → "XX很明显"

- [ ] 口语化改造
  - 长句拆短(超过30字必拆)
  - 加入口语词("其实"、"说实话"、"你看")
  - 使用反问句增强互动感

- [ ] 加入真实细节
  - 抽象描述 → 具体数字/场景
  - 泛泛而谈 → 个人经历
  - 中立客观 → 明确态度

- [ ] 增强个性化
  - 从 `memory/personal-voice.md` 提取语言习惯
  - 加入个人观点(从 `materials/indexed/personal-views.md`)
  - 使用标志性表达方式

**对比示例库:**

❌ **AI化写法:**
> 在当今AI技术飞速发展的时代,编程工具也在不断进化。通过充分利用Claude Code的能力,可以显著提升开发效率,不仅能够加快编码速度,而且能够提高代码质量。值得注意的是,这种提升不是简单的工具替代,而是工作流程的全面优化。

✅ **自然化改写:**
> Claude Code出了两周,我每天都在用。
>
> 说实话,比Cursor好用不少。之前每个项目平均要敲5小时代码,现在缩短到2-3小时。不是打字快了,而是AI理解我的意图更准了——一个需求描述,直接生成70%能用的代码。
>
> 最明显的变化:再也不用来回改bug了。

**输出格式:**
```
🎨 风格审校报告

📊 AI特征统计:
- 套话出现: 8处
- AI句式: 12处
- 书面词汇: 15处
- 平均句长: 28字 (建议<25字)
- 段落过长: 3处

---

⚠️ 高优先级修改 (AI味浓重)

【位置】第1段
❌ 原文: "在当今AI技术飞速发展的时代,编程工具也在不断进化..."
✅ 改为: "Claude Code出了两周,我每天都在用。"
【理由】删除套话,用真实使用时长代替空洞开场

【位置】第3段第2句
❌ 原文: "通过充分利用Claude Code的能力,可以显著提升开发效率"
✅ 改为: "用好Claude Code,每个项目能省3-5小时"
【理由】替换书面词汇 + 加入具体数字

【位置】第5段
❌ 原文: "不仅能够加快编码速度,而且能够提高代码质量"
✅ 改为: "代码写得快了,bug还少了"
【理由】拆解AI句式,口语化改造

---

🔧 中优先级修改 (可优化)

【位置】第7段
❌ 原文: "这种提升不是简单的工具替代,而是工作流程的全面优化"
✅ 改为: "关键不是工具本身,是整个开发流程都变了"
【理由】"不是...而是..."是AI常用句式,且过于书面

【位置】第9段
❌ 原文: "值得注意的是,功能覆盖度达到90%以上"
✅ 改为: "说实话,我测了50个功能,能用的有45个,覆盖率90%"
【理由】删除套话,加入真实测试细节

---

💡 个性化建议:

1. 从 materials/indexed/ai-tools.md 找到你的真实评价,融入第4段
2. 在第8段加入个人态度(例如:"我觉得XX很重要")
3. 结尾太中立,建议明确立场(推荐/不推荐)

应用所有修改? (yes/no/edit/skip-to-detail)
```

### 模式3: detail (细节打磨)

**目标:** 优化标点、排版、节奏,提升阅读体验

**检查清单:**
- [ ] 句子长度控制
  - 统计每句字数
  - 标记超过30字的长句
  - 建议拆分点

- [ ] 段落长度优化
  - 手机阅读友好(3-5行)
  - 重点信息独立成段(单句成段)
  - 避免超过100字的段落

- [ ] 标点自然化
  - 减少逗号连接(改为句号)
  - 适度使用感叹号(表达情绪)
  - 问号互动(1-2个反问句)

- [ ] 节奏变化
  - 长短句搭配
  - 快慢结合(紧凑段落+舒缓段落)
  - 高潮前的铺垫

**输出格式:**
```
✨ 细节打磨报告

📏 长度统计:
- 平均句长: 23字 ✅
- 最长句: 38字 ⚠️ (第4段第3句)
- 平均段长: 65字 ✅
- 最长段: 145字 ❌ (第7段)

---

🔧 需调整

【长句拆分】
❌ 第4段第3句 (38字):
"Claude Code的核心优势在于它不仅能够理解代码上下文,还能根据项目结构提供针对性的建议和优化方案"

✅ 拆分建议:
"Claude Code的核心优势是什么?
理解代码上下文。
不止如此,它还能根据项目结构,给出针对性的建议。"

【段落拆分】
❌ 第7段 (145字,过长):
"测试过程中我发现..."

✅ 拆分建议:
- 前半部分(测试过程)独立成段
- 中间(发现问题)独立成段
- 后半部分(解决方案)独立成段

【标点优化】
❌ 第5段:
"功能很强大,操作很简单,效率很高,体验很好"

✅ 改为:
"功能强大。操作简单。效率高,体验好。"
(句号增加节奏感,避免流水账)

---

🎵 节奏建议:

- 第2-3段节奏过慢(都是长句),建议加入短句调节
- 第6段可作为高潮段,前面加铺垫(第5段末尾增加悬念)
- 结尾太急促,建议补充一段过渡

应用修改? (yes/no)
```

### 组合执行

用户可以一次性执行全部三遍审校:

```
/review all
```

AI将依次执行 content → style → detail,中间暂停让用户确认修改。

## 审校后验证

完成三遍审校后,可选:
1. **AI检测验证** - 调用腾讯朱雀API,查看AI浓度
2. **可读性评分** - 基于句长、段长、节奏评分
3. **对比报告** - 生成审校前后对比文档

```
📊 审校效果报告

AI检测率:
- 审校前: 85%
- 审校后: 28% ✅

可读性评分:
- 句长: 8.5/10 (优秀)
- 段长: 9/10 (优秀)
- 节奏: 7/10 (良好)

修改统计:
- 删除套话: 8处
- 拆解AI句式: 12处
- 口语化改造: 15处
- 加入真实细节: 6处
- 拆分长句: 5处
- 优化段落: 3处

✅ 已达到发布标准
```
```

### 2.4 信息搜索与知识管理

#### `/research` 命令设计

```markdown
---
description: 多渠道信息搜索,保存到知识库
scripts:
  sh: .specify/scripts/bash/check-network.sh
allowed-tools: WebSearch, WebFetch, Write(//knowledge_base/**)
---

# 信息搜索与知识管理

## 执行条件

当满足以下任一条件时,**必须**执行信息搜索:
- 涉及新产品/新技术(2024年后发布)
- 涉及专业领域知识(需要权威资料)
- 用户明确要求调研
- brief中包含"需要真实数据"

## 搜索流程

### 1. 确定搜索主题

从 brief 或用户需求中提取关键主题:
```
主题: Claude Code
关键词: Claude Code, Anthropic, AI编程工具, Cursor对比
时间范围: 2024年11月至今
```

### 2. 多渠道搜索

按优先级依次搜索:

**优先级1: 官方信息**
- 产品官网
- 官方博客/文档
- 官方发布公告

**优先级2: 权威媒体**
- TechCrunch
- The Verge
- Hacker News

**优先级3: 社区讨论**
- Reddit (r/programming, r/MachineLearning)
- Twitter/X
- GitHub Discussions

**优先级4: 中文社区**
- 少数派
- V2EX
- 掘金

⚠️ **禁止使用:** 知乎、百度(信息质量低,AI生成内容多)

### 3. 信息验证

对每条信息进行验证:
- [ ] 信息源可靠性(官方>媒体>社区)
- [ ] 发布时间(越新越好)
- [ ] 交叉验证(至少2个来源确认)
- [ ] 是否为一手信息

### 4. 保存到知识库

文件命名格式: `主题-YYYY-MM-DD.md`

**模板:**
```markdown
# 主题 - 信息调研

## 元信息
- **调研时间**: 2025-01-15
- **调研人**: AI (Claude)
- **下次更新建议**: 2025-02-15 (产品迭代后)
- **可信度评分**: 8/10

## 核心信息

### 产品基本信息
- **名称**: Claude Code
- **开发商**: Anthropic
- **发布时间**: 2024年12月
- **版本**: Beta
- **来源**: [Anthropic官网](https://...)

### 核心特性
1. **功能A**
   - 描述: ...
   - 来源: [TechCrunch报道](https://...)
   - 验证: ✅ 官方确认

2. **功能B**
   - 描述: ...
   - 来源: [Reddit讨论](https://...)
   - 验证: ⚠️ 社区反馈,未官方确认

### 竞品对比
| 维度 | Claude Code | Cursor | 来源 |
|-----|------------|--------|------|
| 价格 | $20/月 | $20/月 | 官网 |
| ... | ... | ... | ... |

### 用户评价
**正面反馈:**
- "速度比Cursor快" - [Reddit](https://...), 23 upvotes
- "理解上下文更准" - [Twitter](https://...), 156 likes

**负面反馈:**
- "偶尔会卡顿" - [Reddit](https://...), 12 upvotes

## 关键数据

- **用户数量**: 未公开
- **GitHub Stars**: 12.5K (截至2025-01-15)
- **定价**: $20/月 (Pro), $0/月 (Free, 限额)

## 信息源列表

1. [Anthropic官方](https://...) - 官方,可靠度10/10
2. [TechCrunch报道](https://...) - 媒体,可靠度9/10
3. [Reddit讨论](https://...) - 社区,可靠度7/10

## 待补充

- [ ] 实际性能测试数据(需自己测试)
- [ ] 与GPT-4o对比(缺少权威对比)
- [ ] 企业版定价(未公开)

## 使用建议

写作时可引用:
- 产品基本信息(核心特性)
- 竞品对比数据
- 真实用户评价(带来源)

避免引用:
- 未验证的社区猜测
- 过时信息(2024年11月前)
```

### 5. 向用户报告

```
📚 信息搜索完成

已保存到: _knowledge_base/claude-code-2025-01-15.md

🔍 搜索统计:
- 搜索渠道: 5个
- 有效信息: 23条
- 权威来源: 3个
- 社区反馈: 8个

✅ 高可信度信息 (8条)
- Claude Code 核心特性 (官方)
- 定价信息 (官方)
- TechCrunch 评测 (媒体)
...

⚠️ 中可信度信息 (12条)
- Reddit 用户评价 (需交叉验证)
- 性能对比 (非官方测试)
...

❌ 缺失信息 (3条)
- 企业版定价 (未公开)
- 实际性能数据 (需测试)

💡 建议:
1. 可直接使用高可信度信息写作
2. 中可信度信息需标注"据用户反馈"
3. 缺失信息需补充测试或明确说明"未公开"

继续下一步? (yes/查看详情/补充调研)
```
```

---

## 三、CLI命令设计

### 3.1 初始化命令

```bash
# 创建新项目
content init my-article

# 创建并选择工作区
content init my-article --workspace wechat

# 安装插件
content init my-article --plugins materials-manager,image-generator

# 导入已有素材库
content init my-article --import-materials ~/jike-export.csv
```

### 3.2 工作区管理

```bash
# 初始化工作区
content workspace init wechat "我的公众号"

# 切换工作区
content workspace switch video

# 查看工作区配置
content workspace config wechat

# 列出所有工作区
content workspace list
```

### 3.3 素材库管理

```bash
# 初始化素材库
content materials init

# 导入CSV
content materials import ~/Downloads/jike-all.csv --type jike

# 建立主题索引
content materials index ai-tools

# 统计素材数量
content materials stats
```

---

## 四、数据流设计

### 4.1 完整写作流程数据流

```
[用户需求]
    ↓
[specify] → _briefs/项目名-brief.md
    ↓
[research] → WebSearch → _knowledge_base/主题-日期.md
    ↓
[topic] → 读取: brief + knowledge_base
                 → 输出: 3-4个选题 + 大纲
    ↓
[用户选择选题2]
    ↓
[collab-doc] → _协作文档/项目名-协作文档.md
    ↓
[collect] → Grep: materials/raw/*.csv
                    → Read: materials/indexed/*.md
                    → 输出: 相关素材列表
    ↓
[write] → 读取: brief + knowledge + materials
               → 输出: articles/001-主题/draft.md
    ↓
[audit style] → 读取: draft.md
               → 输出: 修改建议 + 对比
               → 更新: draft.md
    ↓
[audit detail] → 读取: draft.md
                → 输出: 优化建议
                → 更新: draft.md
    ↓
[images] → 读取: draft.md
          → 生成: articles/001-主题/images/*.png
          → 更新: draft.md (插入图片引用)
    ↓
[发布] final.md
```

### 4.2 文件依赖关系

```
articles/001-主题/
├── specification.md     # 依赖: _briefs/*.md
├── tasks.md            # 依赖: specification.md
├── draft.md            # 依赖: tasks.md + _knowledge_base/*.md + materials/**
├── final.md            # 依赖: draft.md (审校后)
└── images/             # 依赖: draft.md (分析配图需求)
```

---

## 五、关键技术实现

### 5.1 命令模板生成脚本改造

保留 `scripts/build/generate-commands.sh` 的核心逻辑,修改模板路径:

```bash
# novel-writer 原逻辑
TEMPLATES_DIR="templates/commands"
COMMANDS=(
  "constitution"
  "specify"
  "clarify"
  "plan"
  "tasks"
  "write"
  "analyze"
)

# article-writer 改造
TEMPLATES_DIR="templates/commands"
COMMANDS=(
  "specify"
  "research"
  "topic"
  "collab-doc"
  "style-learn"
  "collect"
  "write"
  "audit"
  "images"
)
```

### 5.2 插件系统扩展

在 `PluginManager` 基础上,新增材料插件支持:

```typescript
// src/plugins/manager.ts 扩展

class MaterialsPlugin extends Plugin {
  async install() {
    // 1. 复制插件文件
    await this.copyFiles([
      { source: 'commands/collect.md', target: '.claude/commands/' },
      { source: 'commands/materials-import.md', target: '.claude/commands/' }
    ])

    // 2. 初始化素材库目录
    await fs.ensureDir('materials/raw')
    await fs.ensureDir('materials/indexed')
    await fs.ensureDir('materials/archive')

    // 3. 创建示例索引
    await this.createSampleIndex()
  }

  async createSampleIndex() {
    const template = `# AI工具相关素材

## 使用说明
将你的真实经历、观点按主题整理在这里,AI写作时可以引用。

## Claude Code 使用体验

- **原始动态**: "用了两周,确实比Cursor好"
- **发布时间**: 2024-12-10
- **观点**: 理解上下文更准,速度快
- **适用场景**: 开头引入、工具对比

## Cursor 使用问题

- **原始动态**: "Cursor偶尔会卡顿,尤其是大项目"
- **发布时间**: 2024-11-20
- **观点**: 稳定性待提升
- **适用场景**: 对比论证、问题分析
`
    await fs.writeFile('materials/indexed/ai-tools.md', template)
  }
}
```

---

## 六、性能优化

### 6.1 素材库搜索优化

**问题:** CSV文件过大(>10MB)时,Grep搜索可能较慢

**解决方案:**
1. **分片索引** - 每月一个CSV文件,减少单文件大小
2. **SQLite缓存** - 首次导入时建立SQLite索引,加速后续搜索
3. **热门主题预加载** - 常用主题提前提取到indexed/

```typescript
// materials/indexed/.cache/index.db (SQLite)
CREATE TABLE materials (
  id INTEGER PRIMARY KEY,
  source TEXT,      -- 'jike' | 'weibo'
  content TEXT,     -- 动态内容
  publish_time TEXT,
  keywords TEXT,    -- 提取的关键词
  theme TEXT        -- 关联的主题
);

CREATE INDEX idx_keywords ON materials(keywords);
CREATE INDEX idx_theme ON materials(theme);
```

### 6.2 命令执行缓存

对于调研类命令,避免重复搜索:

```typescript
// _knowledge_base/.cache/search-history.json
{
  "claude-code": {
    "last_search": "2025-01-15",
    "file": "claude-code-2025-01-15.md",
    "freshness": "fresh"  // fresh | stale | expired
  }
}
```

AI执行 `/research` 时,先检查缓存:
- fresh (< 7天) - 直接使用
- stale (7-30天) - 询问是否更新
- expired (> 30天) - 强制重新搜索

---

## 七、测试策略

### 7.1 单元测试

```typescript
// tests/commands/collect.test.ts
describe('MaterialsSearch', () => {
  it('should search CSV by keywords', async () => {
    const result = await materialsSearch('高德|扫街榜')
    expect(result.length).toBeGreaterThan(0)
    expect(result[0]).toHaveProperty('content')
  })

  it('should fallback to indexed files', async () => {
    const result = await materialsSearch('ai-tools')
    expect(result.source).toBe('indexed')
  })
})
```

### 7.2 集成测试

```bash
# tests/integration/full-workflow.sh
#!/bin/bash

# 完整流程测试
content init test-article --workspace wechat
cd test-article/workspaces/wechat

# 模拟用户输入
echo "写一篇关于Claude Code的文章" | claude /specify
claude /research
claude /topic  # 选择选题1
claude /collect
claude /write
claude /review style
claude /images

# 验证输出
test -f articles/001-claude-code/final.md || exit 1
echo "✅ Full workflow test passed"
```

---

## 八、部署与发布

### 8.1 NPM包发布

```json
{
  "name": "article-writer-cn",
  "version": "0.1.0",
  "bin": {
    "content": "dist/cli.js"
  },
  "scripts": {
    "build": "tsc && npm run build:commands",
    "build:commands": "bash scripts/build/generate-commands.sh"
  }
}
```

### 8.2 用户安装流程

```bash
# 安装
npm install -g article-writer-cn

# 初始化项目
content init my-blog --workspace wechat

# 导入素材库
cd my-blog
content materials import ~/Downloads/jike-export.csv

# 在AI助手中使用
# Claude Code: /specify, /research, /topic...
```

---

**技术方案完成,可进入开发阶段!**
