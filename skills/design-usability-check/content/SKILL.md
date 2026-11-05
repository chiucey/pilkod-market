---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7258e87cde68e569239503e93a3851e3
    PropagateID: 7258e87cde68e569239503e93a3851e3
    ReservedCode1: 3044022052c48fbada92ca2324a0bac5a46f973b8021e08e9bbe39012a25e6d66043e3b10220640a7493495566ab7820ca3d698ab414c341dbe4a3ecdad883861ecccc26eb82
    ReservedCode2: 3045022008bbd5d23ad4a9d4ecc917f2a584d9d5f9d4e5297ce57bd3de4625b45476b04d022100ec18dd79af4265c8db83576ebeb08e97abb427c57c02eadf9c73301bae03cba1
description: |-
    Provides systematic usability and accessibility evaluation for design solutions. Use when users ask to:

    **Core Trigger Phrases**:
    - "check the usability", "review this design/page/flow"
    - "is there a UX problem", "any usability issues with this"
    - "review my prototype", "design review", "usability audit"
    - "how is the user experience", "how to improve usability"
    - "optimize form/navigation/login page", "too complex, how to simplify"
    - "users don't know how to use it", "too many steps"
    - "recommend some design references", "similar design examples"
    - "is this interaction good", "is this interaction design reasonable"
name: design-usability-check
---

# 设计方案可用性评估
> Design Usability Evaluation

## 任务目标
> Task Objective

本 Skill 用于快速评估设计方案的可用性与易用性，帮助设计师在设计早期发现问题、降低改版成本，并提供优质设计案例作为参考。

*This Skill is used to quickly evaluate the usability of design solutions, helping designers identify problems early, reduce revision costs, and provide reference cases.*

**核心能力 Core Capabilities**：
- 基于 Nielsen 原则的系统性评估 (Systematic evaluation based on Nielsen's principles)
- 识别影响用户体验的关键问题 (Identify key issues affecting user experience)
- 提供可操作的改进建议 (Provide actionable improvement suggestions)
- 搜索并推荐相关优质设计案例 (Search and recommend relevant design cases)

**适用场景 Applicable Scenarios**：
- 设计师提交设计稿/原型图/交互流程进行评审 (Designer submits design mockups/prototypes/flows for review)
- 产品经理需要验证功能设计的易用性 (PM needs to validate functional design usability)
- 开发团队需要理解设计的用户体验考量 (Dev team needs to understand UX considerations)
- 团队进行设计走查或设计复盘 (Team conducts design walkthrough or retrospective)
- 需要寻找特定功能模块的参考案例 (Need to find reference cases for specific features)

## 评估维度
> Evaluation Dimensions

智能体将基于以下 5 大维度进行评估，每个维度包含具体检查项：

*The agent evaluates across 5 major dimensions with specific checklist items:*

### 1. 学习成本 (Learnability)
- 核心功能是否易于发现 (Is core functionality discoverable)
- 操作流程是否符合用户心智模型 (Does flow match user mental models)
- 是否需要额外的学习或引导 (Requires additional learning or guidance)
- 新用户能否在 30 秒内理解主要功能 (Can new users understand main features in 30 seconds)

### 2. 操作效率 (Efficiency)
- 完成核心任务的步骤是否最简 (Are steps minimal for core tasks)
- 是否存在冗余操作或重复路径 (Redundant operations or duplicate paths)
- 常用功能是否触手可及 (Are common functions easily accessible)
- 快捷方式/高效路径是否提供 (Shortcuts or efficient paths provided)

### 3. 错误预防 (Error Prevention)
- 高危操作是否有二次确认 (Critical actions have confirmation)
- 输入错误是否有即时反馈 (Input errors have immediate feedback)
- 错误提示是否清晰且可操作 (Error messages are clear and actionable)
- 是否有撤销/回退机制 (Undo/recovery mechanisms exist)

### 4. 信息架构 (Information Architecture)
- 导航结构是否清晰合理 (Navigation structure is clear and logical)
- 信息层级是否明确 (Information hierarchy is explicit)
- 标签命名是否准确易懂 (Labels are accurate and understandable)
- 用户能否快速定位目标内容 (Users can quickly locate target content)

### 5. 视觉呈现 (Visual Design)
- 界面布局是否合理有序 (Layout is organized and logical)
- 视觉层级是否引导用户注意力 (Visual hierarchy guides attention)
- 文字可读性是否良好 (Text readability is good)
- 色彩对比度是否满足可访问性标准 (Color contrast meets accessibility standards)

## 操作步骤
> Workflow

### 标准流程 Standard Workflow

1. **接收设计方案 Receive Design Solution**
   - 设计师提供设计稿图片、原型链接或文字描述 (Designer provides mockup images, prototype links, or text descriptions)
   - 智能体理解方案的核心功能和目标用户 (Agent understands core functionality and target users)

2. **逐维度评估 Evaluate by Dimension**
   - 智能体基于 [references/usability-principles.md](references/usability-principles.md) 中的可用性原则 (Agent applies usability principles from reference document)
   - 对每个维度进行系统化检查 (Systematic check across all dimensions)
   - 记录发现的问题点 (Document identified issues)

3. **生成评估报告 Generate Evaluation Report**
   - 输出结构化的问题清单 (Structured issue list)
   - 标注问题严重等级（严重/中等/轻微）(Severity levels: Critical/Moderate/Minor)
   - 提供针对性的改进建议 (Targeted improvement suggestions)

4. **搜索优质案例参考 Search Reference Cases**
   - 根据评估对象的产品类型和功能模块，搜索相关优质设计案例 (Search relevant cases based on product type and feature module)
   - 参考 [references/design-patterns.md](references/design-patterns.md) 中的设计模式分类 (Reference design pattern classification)
   - 优先提供设计截图/图片链接，如无法获取则提供"产品名称 - 模块名称" (Prioritize screenshots/links, fallback to "Product Name - Module Name")
   - 标注每个案例的设计亮点，帮助设计师快速获取参考价值 (Highlight design strengths for quick reference)

### 输出格式 Output Format

```markdown
## 可用性评估报告

### 方案概览
- 评估对象：[方案名称/功能模块]
- 核心功能：[主要功能描述]
- 目标用户：[用户群体]

### 评估结果

#### 严重问题（影响核心体验，必须修复）
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| [问题描述] | [维度名称] | [影响说明] | [具体建议] |

#### 中等问题（影响使用效率，建议优化）
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| ... | ... | ... | ... |

#### 轻微问题（可优化体验，酌情处理）
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| ... | ... | ... | ... |

### 亮点总结
- [值得保留的设计优点]

### 优化优先级建议
1. [最优先修复的问题]
2. [次优先优化的问题]
3. ...

### 优质设计案例参考

#### 相关产品案例

| 产品名称 | 模块名称 | 设计亮点 | 参考链接 |
|----------|----------|----------|----------|
| [产品名] | [功能模块] | [亮点描述] | [图片链接或"暂无图片"] |

#### 设计灵感来源
- [Dribbble/Behance/Mobbin 等平台的相关设计集合]
- [具体设计案例的关键截图链接]

#### 可借鉴的设计模式
1. **[模式名称]**：[描述该模式如何解决类似问题]
2. **[模式名称]**：[描述该模式如何解决类似问题]
```

## 资源索引 Resources

- **评估标准参考**：见 [references/usability-principles.md](references/usability-principles.md)（包含 Nielsen 可用性原则、设计心理学要点、常见问题模式）
- **设计模式参考**：见 [references/design-patterns.md](references/design-patterns.md)（包含常见功能模块的设计模式、优质案例来源、搜索策略）

## 注意事项 Notes

- 评估时聚焦用户体验，避免主观审美判断 (Focus on UX, avoid subjective aesthetic judgments)
- 问题严重等级基于对用户目标完成的影响程度 (Severity based on impact to user goal completion)
- 改进建议应具体可执行，避免空泛表述 (Suggestions should be specific and actionable)
- 考虑方案的目标用户群体和使用场景 (Consider target users and use scenarios)
- 兼顾可用性与业务目标的平衡 (Balance usability with business objectives)
- 案例参考优先选择与评估对象同类型、同场景的产品 (Prioritize same-type product references)
- 标注案例亮点时聚焦与评估问题相关的设计决策 (Highlight design decisions relevant to evaluated issues)

## 使用示例 Usage Examples

### 示例 1：设计稿评估（上传图片）

```
设计师：这是我的登录页面设计稿，请帮我检查可用性，看看有没有用户体验问题。
[上传设计稿图片: login-page-v2.png]

智能体：
## 可用性评估报告

### 方案概览
- 评估对象：登录页面 V2
- 核心功能：用户身份认证
- 目标用户：首次使用产品的新用户、已有账号的回访用户

### 评估结果

#### 严重问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 未提供社交登录选项 | 学习成本 | 新用户注册门槛高，可能导致流失 | 增加 Google/Apple 登录按钮 |
| 密码找回入口不明显 | 错误预防 | 用户忘记密码时无法快速找回 | 在密码输入框下方增加"忘记密码"链接 |

#### 中等问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 邮箱/手机切换不够醒目 | 操作效率 | 需要切换登录方式的用户操作繁琐 | 使用 Tab 切换样式突出切换功能 |
| 缺少输入框清除按钮 | 操作效率 | 输入错误时无法快速重置 | 添加可点击的清除图标 |

### 优质设计案例参考

| 产品名称 | 模块名称 | 设计亮点 |
|----------|----------|----------|
| Airbnb | 登录模块 | 社交登录突出，减少注册摩擦 |
| Notion | 登录模块 | 魔法链接登录，无密码体验 |
| Slack | 登录模块 | 企业邮箱自动识别，智能填充 |

### 优化优先级
1. 首先添加社交登录（影响新用户转化）
2. 优化忘记密码入口位置
3. 考虑增加邮箱/手机 Tab 切换的视觉强调
```

---

### 示例 2：交互流程评估（描述流程）

```
产品经理：我们的下单流程是这样的：
1. 选择商品规格 → 2. 加入购物车 → 3. 查看购物车 →
4. 确认订单信息 → 5. 填写收货地址 → 6. 选择支付方式 → 7. 提交订单

用户反馈下单太麻烦了，总共要7步。帮我看看这个流程有什么问题？

智能体：
## 可用性评估报告

### 方案概览
- 评估对象：电商下单全流程
- 核心功能：完成商品购买
- 目标用户：电商平台普通消费者

### 评估结果

#### 严重问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 步骤过多导致放弃率升高 | 操作效率 | 用户在流程中流失，转化率下降 | 考虑精简流程或使用渐进式披露 |
| 收货地址每次都要填写 | 操作效率 | 回头客重复操作，增加负担 | 添加地址簿功能，记忆历史地址 |

#### 中等问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 订单确认与地址填写分离 | 信息架构 | 信息分散，增加认知负担 | 合并订单确认与地址编辑为同一页面 |
| 支付方式选择位置靠后 | 操作效率 | 用户需滚动到页面底部才能选择支付 | 将支付方式前置到更显眼位置 |

#### 轻微问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 缺少购物车修改入口 | 操作效率 | 用户想修改数量需返回商品页 | 在结算页直接提供数量修改功能 |

### 优化建议
1. **地址预填充**：已购买过的用户直接显示上次地址，一键确认
2. **合并步骤**：将订单确认和地址选择合并为一步
3. **即时支付选择**：在结算页顶部显示支付方式选择
4. **快捷购物**：考虑增加"立即购买"入口，跳过购物车

### 优质设计案例参考

| 产品名称 | 模块名称 | 设计亮点 | 参考价值 |
|----------|----------|----------|----------|
| 淘宝 | 购物车 | 一键结算、地址复用、优惠叠加 | 高效结算流程 |
| 京东 | 结算流程 | 地址智能填充、发票信息复用 | 减少重复输入 |
| Shopify | 结账流程 | 一页式结账、自动地址补全 | 步骤精简 |
| Nike | 购物车 | 库存预警、尺码快速切换 | 商品信息优化 |
```

---

### 示例 3：特定问题咨询

```
设计师：我们的注册表单有 20 个字段，用户普遍反馈填写时间太长，完成率只有 30%。有没有什么优化思路？顺便推荐一些好的表单设计参考。

智能体：
## 可用性评估报告

### 方案概览
- 评估对象：用户注册表单
- 核心功能：收集用户信息并创建账户
- 问题焦点：表单过长导致用户放弃

### 问题分析

#### 严重问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 20个字段全部展示 | 学习成本 | 用户看到表单长度产生畏难情绪 | 分步表单设计，每步3-5个字段 |
| 必填项与非必填项未区分 | 错误预防 | 用户不确定哪些必须填写导致提交失败 | 使用视觉标记区分必填/选填字段 |
| 无进度指示 | 学习成本 | 用户不知道还需要填写多久 | 添加进度条或步骤指示器 |

#### 中等问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 缺少智能默认值 | 操作效率 | 用户需要手动输入大量信息 | 根据上下文自动填充已知信息 |
| 输入方式单一 | 操作效率 | 某些字段可选择但只能用手动输入 | 使用下拉选择器、日期选择器等 |

### 优化建议

**短期优化（快速实施）**：
1. **分步表单**：将20个字段拆分为4-5步
   - 步骤1：账号信息（邮箱、密码）- 必填
   - 步骤2：基本信息（姓名、手机、生日）- 必填
   - 步骤3：详细资料（职业、兴趣、公司）- 选填
   - 步骤4：确认注册

2. **进度指示**：显示当前步骤和剩余步骤数量

3. **必填标记**：使用红色星号标记必填字段

**中期优化（体验提升）**：
1. **渐进式披露**：初始只显示核心字段
2. **智能填充**：记住用户上次填写的内容
3. **实时验证**：输入时即时反馈错误
4. **保存草稿**：意外关闭时可恢复填写进度

### 优质设计案例参考

| 产品名称 | 模块名称 | 设计亮点 | 参考价值 |
|----------|----------|----------|----------|
| Typeform | 表单设计 | 分步展示、进度指示、对话式体验 | 表单体验标杆 |
| Stripe | 结算表单 | 卡号自动识别、实时验证 | 高效输入体验 |
| LinkedIn | 注册流程 | 渐进式字段、职业信息引导 | 社交账号注册 |
| Notion | 账号创建 | 极简字段、后续补充 | 降低入门门槛 |
| Pinterest | 注册流程 | 社交账号快速注册、兴趣选择 | 减少注册摩擦 |
```

---

### 示例 4：移动端设计评估

```
设计师：帮我看看这个 App 首页的设计，主要想了解导航和内容组织是否合理。
[上传图片: mobile-homepage.png]

智能体：
## 可用性评估报告

### 方案概览
- 评估对象：App 首页
- 核心功能：内容浏览、入口导航
- 目标用户：移动端用户

### 评估结果

#### 严重问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 底部导航图标过小（<44px） | 视觉呈现 | 触控困难，容易误触相邻选项 | 确保图标尺寸 ≥ 44px |
| 重要功能入口被折叠 | 操作效率 | 用户需展开菜单才能使用核心功能 | 将高频功能前置到主导航 |

#### 中等问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 信息层级不清晰 | 信息架构 | 用户难以区分主次内容 | 通过大小、颜色、间距区分层级 |
| 搜索入口位置偏僻 | 操作效率 | 用户难以快速找到搜索功能 | 将搜索框放在顶部固定位置 |

#### 轻微问题
| 问题 | 所属维度 | 影响 | 改进建议 |
|------|----------|------|----------|
| 文字大小偏小 | 视觉呈现 | 阅读时眼睛疲劳 | 确保正文字号 ≥ 14sp |
| 卡片间距不均匀 | 视觉呈现 | 视觉上不够整洁 | 统一间距为 8dp 或 16dp 的倍数 |

### 优质设计案例参考

| 产品名称 | 模块名称 | 设计亮点 | 参考价值 |
|----------|----------|----------|----------|
| Instagram | 底部导航 | 图标+文字组合、热区合理 | 导航设计参考 |
| 支付宝 | 首页导航 | 九宫格布局、自定义入口 | 功能聚合设计 |
| 小红书 | 发现流 | 瀑布流、封面图吸引 | 内容浏览体验 |
| Spotify | 底部导航 | 图标动态反馈、创建按钮突出 | 操作引导设计 |
```

---

### 示例 5：空状态设计咨询

```
设计师：我们的产品有很多空状态页面（无数据、无内容），目前都是直接显示"暂无数据"，很单调。有什么更好的处理方式吗？

智能体：
## 空状态设计指南

### 当前问题
直接显示"暂无数据"缺乏引导性，浪费了与用户建立情感连接的机会。

### 设计策略

#### 1. 友好提示 + 行动引导
- 使用通俗语言描述当前状态
- 提供明确的下一步操作
- 示例："还没有订单，去逛逛有什么好东西"

#### 2. 插画缓解情绪
- 配合产品风格的插画
- 降低用户的失落感
- 示例：空文件夹配上传引导插画

#### 3. 引导内容填充
- 提供内容创建入口
- 或展示示例/样例数据激发用户兴趣
- 示例："看看其他人的作品"

#### 4. 场景化设计
根据不同场景定制空状态内容：

| 场景 | 插画风格 | 文案示例 | 行动按钮 |
|------|----------|----------|----------|
| 无订单 | 购物袋+问号 | "还没有订单~" | "去购物" |
| 无收藏 | 爱心+星星 | "还没有收藏哦" | "去看看推荐" |
| 无消息 | 邮件+气泡 | "暂无新消息" | 不需要按钮 |
| 无搜索结果 | 放大镜+问号 | "没有找到相关结果" | "试试其他关键词" |

### 优质设计案例参考

| 产品名称 | 场景 | 设计亮点 | 参考价值 |
|----------|------|----------|----------|
| Dropbox | 空文件夹 | 插画+引导上传按钮 | 引导性强 |
| Slack | 网络断开 | 顶部提示条+自动重连 | 智能恢复 |
| Chrome | 页面无法访问 | 恐龙游戏+错误说明 | 缓解负面情绪 |
| Asana | 空项目 | 引导创建第一个任务 | 新手引导 |
| Spotify | 无搜索结果 | 推荐相关内容 | 内容引导 |
| Notion | 空页面 | 示例模板选择 | 降低启动门槛 |
```

---

### 示例 6：错误提示优化

```
开发：用户说看到错误提示后不知道怎么解决，比如"操作失败"这种提示完全没有用。能帮我看看怎么改进吗？

智能体：
## 错误提示优化指南

### 当前问题
"操作失败"这类提示缺乏具体信息，用户无法理解发生了什么，也不知道如何解决。

### 优秀错误提示的标准

根据 Nielsen 原则，优秀的错误提示应包含：

1. **清晰性**：使用通俗语言，不使用技术术语
2. **具体性**：指出具体哪里出了问题
3. **建设性**：告诉用户如何解决问题
4. **礼貌性**：避免责备用户

### 问题对比

| 差示例 | 好示例 | 改进点 |
|--------|--------|--------|
| 操作失败 | 支付失败：余额不足，请充值或更换支付方式 | 说明原因+解决方案 |
| 格式错误 | 邮箱格式不正确，请输入 example@domain.com | 展示正确格式 |
| 提交失败 | 保存失败，可能是网络断开，请检查网络后重试 | 说明可能原因 |
| 错误 | 第3步出错：密码需包含8-20位字符，包含大小写字母和数字 | 指出具体位置和正确要求 |

### 设计建议

#### 1. 错误时机优化
- **实时验证**：输入时即时反馈，而非提交后才提示
- **输入框内联提示**：在输入框下方显示要求

#### 2. 错误提示位置
- 错误提示应紧邻相关输入框
- 使用红色标记错误
- 确保屏幕阅读器可读取

#### 3. 错误信息结构
```
[图标] [简短描述问题] - [解释原因] - [如何解决]
```

#### 4. 特殊场景处理
- **网络错误**：提供刷新按钮或自动重试
- **权限不足**：说明需要什么权限，并提供设置入口
- **服务不可用**：告知预计恢复时间

### 优质设计案例参考

| 产品名称 | 场景 | 设计亮点 | 参考价值 |
|----------|------|----------|----------|
| Stripe | 支付表单 | 实时验证、具体错误信息 | 表单验证标杆 |
| iOS | 权限请求 | 清晰说明权限用途 | 权限引导设计 |
| Google | 搜索无结果 | 建议修正关键词 | 搜索引导设计 |
| 微信 | 发送失败 | 红色感叹号+重发按钮 | 操作引导设计 |
```

---

### 示例 7：对比式评估

```
设计师：我做了两个版本的通知中心设计方案，帮我看看哪个更好，以及各自的优缺点。
[上传图片: notifications-v1.png]
[上传图片: notifications-v2.png]

智能体：
## 可用性对比评估报告

### 方案概览
- 评估对象：通知中心
- 版本对比：V1（列表式）vs V2（卡片式）
- 目标用户：需要频繁查看通知的用户

### 方案 A（列表式）

#### 优势
- 信息密度高，单屏可见更多通知
- 符合系统通知的既有心智模型
- 适合快速浏览标题

#### 问题
- 未读/已读区分不够明显
- 操作按钮入口较深
- 长文本通知需要展开

### 方案 B（卡片式）

#### 优势
- 卡片边界清晰，视觉分组明确
- 操作按钮更加醒目
- 未读状态更加突出

#### 问题
- 单屏可见通知数量减少
- 信息密度较低
- 滚动时需要加载更多

### 综合评估

| 评估维度 | 方案 A | 方案 B |
|----------|--------|--------|
| 学习成本 | ★★★★★ | ★★★★☆ |
| 操作效率 | ★★★☆☆ | ★★★★☆ |
| 错误预防 | ★★★☆☆ | ★★★★☆ |
| 信息架构 | ★★★★☆ | ★★★★★ |
| 视觉呈现 | ★★★☆☆ | ★★★★★ |

### 建议

**如果你的用户通知量大且需快速浏览**：
→ 选择方案 A（列表式），优化未读状态标识

**如果你的用户需要频繁操作通知**：
→ 选择方案 B（卡片式），强调操作便捷性

**融合建议**：
- 采用卡片式布局保持视觉清晰
- 增加紧凑模式满足信息浏览需求
- 保留重要的快捷操作按钮

### 优质设计案例参考

| 产品名称 | 模块 | 设计亮点 |
|----------|------|----------|
| 微信 | 消息列表 | 未读红点、时间线、操作菜单 |
| LinkedIn | 通知中心 | 分类标签、消息聚合 |
| GitHub | 通知 | 按仓库分组、已读/未读筛选 |
| Facebook | 通知 | 互动+推荐混合、图片预览 |
