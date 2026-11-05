---
name: professional-translator
description: Professional Chinese-to-English translation skill (compliance report level). Used when users require translation of compliance news, legal documents, preserving entity names (legal/game/national), interactive modifications, exporting to PDF/Word/HTML formats, professional intelligence-style expression, and continuous memory-optimized terminology.
---

# 专业中译英翻译器

## 核心原则

1. **专业情报报告级翻译** - 采用 McKinsey/Deloitte/律所简报风格
2. **保留实体名称** - 法律条文、游戏名称、国家名称、平台名称等专有名词保持原样
3. **交互式修改** - 用户可随时提出修改点，逐条确认后修改
4. **多格式导出** - 支持导出为PDF、Word、HTML格式
5. **持续记忆优化** - 自动记录并学习用户添加的专业术语，下次翻译自动应用

## 核心区别：合规报告翻译标准

| 维度 | 普通翻译 | 合规报告级翻译 |
|-----|---------|--------------|
| 标题 | High Priority Signals | **Key Global Compliance Developments** |
| 断言 | will ban | **may impose restrictions on** |
| 定性 | extreme/positive signal | **notably restrictive / indicates favorable development** |
| 语气 | 资讯口吻 | **情报克制、分析性** |
| 结构 | 事件→影响 | **What happened / Why it matters / Implication** |

## 工作流程

### 步骤 1：初始化与记忆加载

每次翻译任务开始时：
1. 读取用户自定义术语库 (`/memories/professional-translator-user-glossary.json`)
2. 读取全局专业术语表 (`references/terminology-guide.md`)
3. 合并生成当前会话的翻译对照表

### 步骤 2：接收翻译内容

接收用户提供的翻译任务：
- 可直接粘贴文本内容
- 可提供文件路径
- 确认翻译范围和格式要求

### 步骤 3：执行翻译

**翻译质量标准（合规报告级）：**

1. **判断语气 vs 信息语气**
   - ❌ "ban on all" / "will mandatory raise"
   - ✅ "broad restrictions on" / "may be subject to"

2. **避免情绪化词汇**
   - ❌ blockade / extreme / positive signal
   - ✅ compliance challenges / notably restrictive / suggests favorable development

3. **专业术语规范化**
   - PROGA → PROGA (unofficial translation)
   - EU AI Act → Artificial Intelligence Act (EU AI Act)
   - KOSA → Kids Online Safety Act (KOSA)

4. **结构化表达**
   - What happened（发生了什么）
   - Why it matters（为何重要）
   - Enforcement context（执法背景）
   - Ongoing developments（进展动态）
   - Implication（合规启示）

**翻译优先级：**
1. **用户自定义术语**（最高优先级）
   - 来自 `/memories/professional-translator-user-glossary.json`

2. **内置专业术语**
   - 法律名称：ECA Digital, GDPR, PEGI, DMA, CNPD, PROGA
   - 游戏名称：League of Legends, Fortnite, GTA, Roblox, EA Sports FC
   - 平台名称：Steam, App Store, Google Play
   - 公司名称：Apple, Amazon, Tencent, NetEase, Valve, Meta, OpenAI

3. **合规报告表达规则**
   - 合规阻塞 → compliance challenges
   - 未成年人 → minors
   - 出海 → going global
   - 实时服务 → live service

**翻译质量检查清单：**
- [ ] 无中文字符遗留
- [ ] 专有名词保留原样
- [ ] 用户自定义术语已应用
- [ ] 句子结构与原文对应
- [ ] 专业术语翻译准确
- [ ] 无过度断言（avoid over-assertion）
- [ ] 语气克制（neutral tone）
- [ ] 结构化表达（if applicable）

### 步骤 4：交互式修改

用户可随时提出修改要求：

**修改类型：**
1. **逐点修改** - 用户指出具体位置，说明修改原因
2. **批量替换** - 同类术语统一修改
3. **风格调整** - 正式程度、语气调整
4. **确认修改** - 显示修改前后对比，用户确认后生效

**修改确认流程：**
```
用户提出修改 → 显示原文+译稿对应段 → 确认修改 → 执行修改 → 用户确认结果
```

### 步骤 5：记忆优化（核心功能）

**自动记录场景：**
- 用户每次手动修改术语翻译时
- 用户明确要求"记住这个词"时
- 用户添加新的实体名称时

**记忆存储：**
- 术语 → 翻译对照（用户自定义规则）
- 实体名称 → 保持原样（新增白名单）
- 错误修正 → 正确翻译（学习修正）

**记忆文件位置：**
- `/memories/professional-translator-user-glossary.json` - 用户术语库
- `/memories/professional-translator-entity-list.json` - 实体名称白名单

### 步骤 6：导出格式

支持以下导出格式：

| 格式 | 说明 | 适用场景 |
|------|------|----------|
| HTML | 保留样式和结构 | 网页展示、邮件发送 |
| PDF | 固定排版，高质量打印 | 正式文档、存档 |
| Word (.docx) | 可编辑，便于后续修改 | 编辑审阅、团队协作 |

**导出命令：**
- "导出PDF" → 调用 html_to_pdf 工具
- "导出Word" → 使用 minimax-docx 技能
- "导出HTML" → 直接保存HTML文件

## 持续记忆系统

### 术语添加命令

| 命令 | 功能 | 示例 |
|------|------|------|
| "记住 [术语] = [翻译]" | 添加术语对照 | "记住 loot box = loot box" |
| "新增实体 [名称]" | 添加实体白名单 | "新增实体 HoYoverse" |
| "清除记忆" | 清空用户术语库 | "清除记忆" |
| "查看记忆" | 显示当前术语库 | "查看记忆" |

### 记忆文件格式

```json
// /memories/professional-translator-user-glossary.json
{
  "version": "1.0",
  "last_updated": "2026-03-27",
  "terms": {
    "术语A": "TranslationA",
    "术语B": "TranslationB"
  },
  "entities": {
    "原样保留的名称": {
      "category": "法律/游戏/公司/平台/其他",
      "added_date": "2026-03-27"
    }
  },
  "corrections": {
    "错误翻译": "正确翻译",
    "错误翻译2": "正确翻译2"
  },
  "style_rules": {
    "ban": "restrictions",
    "blockade": "compliance challenges",
    "extreme": "notably restrictive"
  }
}
```

### 记忆应用规则

1. **首次出现**：检测到新术语时，询问用户是否记忆
2. **自动匹配**：已记忆术语在后续翻译中自动应用
3. **优先级**：用户记忆 > 内置术语 > 通用规则
4. **跨会话**：术语库持久化到 `/memories`，重启后仍生效

## 实体名称参考表

### 法律与监管
```
ECA Digital | GDPR | PEGI | DMA | CNPD | GRB | CERO | COPPA
PROGA (unofficial translation) | KOSA | EU AI Act | Digital Fairness Act
```

### 游戏与IP
```
League of Legends | Fortnite | GTA Online | Roblox | Minecraft
EA Sports FC | Overwatch 2 | Ultimate Team | Genshin Impact
CS2 | Valorant | PUBG
```

### 平台与公司
```
Steam | App Store | Google Play | Epic Games Store
Apple | Amazon | Tencent | NetEase | Valve | PDD Holdings
Meta | Google | OpenAI | PDD Holdings
```

### 国家与地区
```
Brazil | Belgium | Luxembourg | Singapore | US | EU | UK
China | Japan | Korea | Australia | India
Texas | Arizona | Arkansas | Nebraska | Kentucky | New Mexico | California
```

## 输出格式

翻译完成后：
1. 直接在对话中展示翻译内容
2. 保存到工作区文件（.html格式）
3. 显示本次翻译应用的记忆术语数量
4. 等待用户确认或提出修改

## 修改追踪

每次修改后记录：
- 修改位置（行号/段落）
- 修改原因
- 原文 vs 译文对比
- 是否保存为记忆

---

## 参考资料

- `references/terminology-guide.md` - 内置专业术语对照表
- `/memories/professional-translator-user-glossary.json` - 用户术语库（自动创建）
- `/memories/professional-translator-entity-list.json` - 实体名称白名单（自动创建）
