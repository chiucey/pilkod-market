---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f54ac488c4ae912a3bc6a96930851e17
    PropagateID: f54ac488c4ae912a3bc6a96930851e17
    ReservedCode1: 3044022065c76bfd10b0a5e3bff37b52a53fece6852dbf39f8c6da894aba0f36ce124c6202200a104455ae09beedcfef971e6d9c023cc8ce77decadc6e39399369d0052b6490
    ReservedCode2: 3045022100ba808cb795eb2366510955af11b6e3327ed825fba81039e7bc9b45374783a8ce02202f6198ae1c0d56a385a35160c17bad981ddeca7d4a34ec4c5f9bcc3f82c6e05c
description: AI 学术文本降 AIGC 率技能。当用户说"降 AIGC 率"、"去除 AI 味"、"让论文更像人写的"、"学术文本润色"、"降低 AI 检测"、"BypassAIGC"、"AI 写作痕迹"、"论文润色"时激活。本技能提供：① 学术文本降 AIGC 率的专业 Prompt（直接可用）；② chi111i/BypassAIGC 项目的部署指南；③ 完整的学术写作润色工作流。
name: bypass-aigc
---

# 🎓 AI 学术文本降 AIGC 率技能

> 基于 chi111i/BypassAIGC 核心算法 + 学术写作最佳实践

---

## 🎯 我能帮你做什么

| 需求 | 方案 |
|------|------|
| 直接降已有文本的 AIGC 率 | 使用下方 **核心降 AIGC Prompt**，粘贴即用 |
| 批量处理学术论文 | 读取文件后套用降 AIGC 工作流 |
| 部署 BypassAIGC 应用 | 查看 **部署指南**章节 |
| 从零写一篇"像人写的"论文 | 使用 **学术写作工作流** |
| 仅做学术润色（不改内容） | 使用 **学术润色 Prompt** |

---

## 🔥 核心降 AIGC Prompt（推荐直接用）

```
请帮我对以下学术文本进行深度润色，降低其 AI 生成特征，使其读起来更像人类学者撰写：

【原文】
[粘贴你需要修改的文本]

【润色要求】
1. 语言风格改造：
   - 将过于规整的句子打散，增加自然停顿
   - 替换 AI 惯用的套路化表达（如"显而易见"、"值得注意的是"）
   - 引入符合人类写作习惯的微小变化（语气、节奏）

2. 词汇与句式多样化：
   - 同义替换过度重复的词汇
   - 将重复句式改为多样句式（主动/被动/倒装/强调句交替）
   - 替换标准化的连接词（如"首先、其次、最后"改为更自然的过渡）

3. 增加人类写作特征：
   - 加入合理的省略和隐含逻辑（人类不会把每句话都说满）
   - 添加适度的口语化学术表达（符合该领域 human 写作习惯）
   - 引入轻微的"不完美"（人类写作本身就有自然的随机性）

4. 保持学术严谨性：
   - 不改变原文的学术含义和技术内容
   - 不降低论证的逻辑严密性
   - 不删除专业术语（术语是必要的）

5. 降低 AIGC 检测特征：
   - 减少过度使用的高频学术词汇
   - 避免过于完美的语法结构
   - 引入符合人类认知过程的自然表达顺序

【输出要求】
请直接输出润色后的文本，不需要说明改动点。
如果某些改动可能影响原意，请用 [原文：xxx → 润色：yyy] 标注即可。
```

---

## 📂 进阶 Prompt 系列

### Prompt 1：学术论文降 AIGC 率（强力版）

```
我有一篇由 AI 辅助撰写的学术论文，需要你进行深度降 AIGC 率处理。

【论文类型】：[如：期刊论文/学位论文/会议论文]
【学科领域】：[如：计算机/经济学/心理学等]
【目标期刊/会议】：(如有)

【降 AIGC 率核心原则】
1. 打乱过于规律的句子节奏——人类写作有自然的轻重缓急
2. 替换 AI 特征性表达：
   ❌ "显而易见" → 改为符合领域习惯的表达
   ❌ "值得注意的是" → 删除或改为"不过"
   ❌ "综上所述" → 改为"可见"或直接删除
   ❌ "首先、其次、最后" → 改为"第一步"、"接下来"或不明显的过渡
   ❌ "换句话说" → 改为"也就是说"或"意即"
3. 增加同义词多样性——同一概念用不同表达
4. 引入自然的认知跳跃——人类不会每步都完美衔接
5. 保留学术术语和数据——这些是内容核心，不能改

【操作步骤】
请逐段处理，每段：
1. 标记该段的主要 AI 特征（套路句式/过度规整/重复词汇）
2. 给出修改后的版本
3. 简要说明主要改动点

请开始处理全文。
```

---

### Prompt 2：极致降 AIGC（适合高风险检测场景）

```
以下文本来自 AI 生成，需要进行极致降 AIGC 率处理，使其通过主流 AIGC 检测工具（GPTZero、Turnitin、CopyLeaks 等）的检测。

【原文】
[粘贴文本]

【极端降 AIGC 策略】
1. 句式层面：
   - 将所有复合句中过多的"which/that/because"从句拆分为短句
   - 打乱主动/被动语态的规律使用
   - 故意引入轻微的主谓不一致（如偶尔的虚拟语气滥用）
   - 将规整的排比句改为不规则的强调方式

2. 词汇层面：
   - 替换所有 AI 高频词（significant/substantial/comprehensive 等）
   - 改写为该领域真实人类作者会用的小众词
   - 增加学科内常见的缩写和简称

3. 逻辑层面：
   - 删除"完美的"过渡——人类写作逻辑链有天然缺口
   - 移除所有"综上所述""综上所述"类总结句
   - 将结论性的完整句改为暗示性表达

4. 格式层面：
   - 减少标点符号的规整使用
   - 增加破折号、冒号、分号的自然混用
   - 允许逗号使用不完全符合语法规范（人类写作常见）

【注意】以上改动不能损害学术内容的正确性。技术术语、实验数据、引用必须保留原样。

输出：纯润色后文本，不附加说明。
```

---

### Prompt 3：学术润色（不改内容，仅提升质量）

```
请帮我对以下学术文本进行专业润色，只提升语言质量，不改变任何技术含义：

【原文】
[粘贴文本]

【润色标准】
- 拼写、语法、标点零错误
- 句意清晰，无歧义
- 逻辑连贯，过渡自然
- 用词精准，符合学术规范
- 适当简练，删除冗余

【不做的改动】
- 不改技术内容
- 不改数据
- 不改作者原创观点
- 保持原有的学术风格倾向

请输出润色后的文本。
```

---

### Prompt 4：分章节处理大段文本

```
以下是一篇 [X] 字学术论文的 [具体章节名]，需要降 AIGC 率处理。

【章节名称】：如"文献综述"、"研究方法"、"实验结果"等
【原文】
[粘贴该章节内容]

【分处理策略】
本章内容更适合的降 AIGC 方式：
- 文献综述类：保留引用格式，打乱综述句式，增加评价性语句
- 研究方法类：保留技术细节，润色操作描述，增加方法对比讨论
- 实验结果类：保留数据描述，丰富结果分析语气，增加局限性讨论
- 讨论与结论类：增加前瞻性表述，强化贡献声明，自然收尾

请先说明对本章的降 AIGC 策略，然后输出处理后的文本。
```

---

## 📖 BypassAIGC 项目部署指南

> chi111i/BypassAIGC 完整部署指南（支持 Linux 服务器）

### 系统要求

| 项目 | 要求 |
|------|------|
| 系统 | Ubuntu 20.04+ / Debian 11+ |
| 内存 | ≥ 2GB |
| 磁盘 | ≥ 5GB |
| 网络 | 可访问 OpenAI API 或兼容 API |

### 快速部署（推荐）

```bash
# 1. 安装依赖
apt update && apt install -y python3 python3-pip git

# 2. 克隆项目
git clone https://github.com/chi111i/BypassAIGC.git
cd BypassAIGC/package

# 3. 安装 Python 依赖
pip3 install -r requirements.txt

# 4. 创建 .env 配置文件
cat > .env << 'EOF'
# 数据库（SQLite 轻量默认）
DATABASE_URL=sqlite:///./ai_polish.db

# OpenAI API（代理地址，如用官方则省略 BASE_URL）
OPENAI_API_KEY=YOUR_API_KEY
OPENAI_BASE_URL=https://api.openai.com/v1
# 如用代理：OPENAI_BASE_URL=http://你的代理IP:端口/v1

# Gemini API（推荐，免费额度充足）
POLISH_MODEL=gemini-2.5-pro
POLISH_API_KEY=YOUR_GEMINI_API_KEY
POLISH_BASE_URL=https://generativelanguage.googleapis.com/v1beta

ENHANCE_MODEL=gemini-2.5-pro
ENHANCE_API_KEY=YOUR_GEMINI_API_KEY
ENHANCE_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# JWT 安全配置
SECRET_KEY=你的32位以上随机字符串
ADMIN_PASSWORD=你的管理员密码

# 并发配置
MAX_CONCURRENT_USERS=5
EOF

# 5. 启动服务
python3 main.py
```

服务运行于 `http://your-server-ip:8000`

### Docker 部署（可选）

```bash
cd BypassAIGC/package

# 构建镜像
docker build -t bypass-aigc .

# 运行容器
docker run -d -p 8000:8000 \
  --name bypass-aigc \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=YOUR_KEY \
  -e SECRET_KEY=YOUR_SECRET \
  bypass-aigc
```

### 访问地址

| 页面 | 地址 |
|------|------|
| 用户界面 | `http://服务器IP:8000` |
| 管理后台 | `http://服务器IP:8000/admin` |
| API 文档 | `http://服务器IP:8000/docs` |

默认管理员账户：`admin` / `admin123`（**部署后立即修改！**）

---

## 🔄 学术写作降 AIGC 工作流

适合已有论文草稿，想完整过一遍的情况：

```
步骤 1：标题 + 摘要降 AIGC
→ 用核心 Prompt 处理，300字以内

步骤 2：逐章节处理
→ 文献综述、研究方法、实验结果、讨论结论
→ 用 Prompt 4（分章节处理）

步骤 3：全文通读检查
→ 确认学术内容未被改变
→ 确认逻辑连贯

步骤 4：术语一致性检查
→ 确保同一术语全程表达一致
→ 用"学术润色 Prompt"精修表达

步骤 5：敏感词预检
→ 用极致降 AIGC Prompt 做最后一遍
→ 重点处理检测高风险段落
```

---

## 💡 使用建议

**日常润色** → 直接用核心 Prompt，粘贴即用  
**期末/毕业论文明审** → 用强力版 + 工作流全套  
**高风险检测（Turnitin 等）** → 用极致降 AIGC 版  
**仅提升质量不降率** → 学术润色 Prompt

---

## ⚠️ 重要原则

- **内容为本**：降 AIGC 率不能损害学术内容正确性
- **术语不可改**：专业术语和数据必须保留原样
- **多次迭代**：一次不够，建议 2-3 遍迭代效果更好
- **人工审核**：AI 润色后务必通读一遍，确认语义未走偏

---

直接粘贴你的论文文本，我来帮你处理！📝
