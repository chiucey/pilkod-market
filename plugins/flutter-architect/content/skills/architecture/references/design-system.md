# 设计系统与端适配

## 一、Design Token

先定义 token，再定义组件，最后拼页面。反过来做，主题永远收不回来。

- 颜色：语义命名（`color.text.primary`）而不是色值命名（`blue500`）。
- 字体：字号/行高/字重成对定义，避免页面各自写 TextStyle。
- 间距与圆角：固定阶梯（4/8/12/16/24），不要出现 13、17 这种自由值。
- 阴影与海拔：与平台视觉规范对齐，阴影不要层层叠加。
- 动效：时长与曲线也 token 化，统一"快/标准/强调"三档。

落地方式：Dart 常量类或 theme extension。禁止在业务代码里写死色值与字号。

## 二、主题

- Material 3（Flutter 3.16 起默认）：用 `ColorScheme.fromSeed` 生成配色，不要手拼 ColorScheme。
- 深浅色都要验证：对比度、图片、阴影、状态色。
- 支持动态取色（Android 12+）时，要验证品牌色不被破坏。
- 主题切换要持久化，且首帧前完成读取，避免闪屏。

## 三、组件库治理

组件库是资产，不是垃圾桶。准入与维护规则：

- 命名语义化，不使用页面名命名通用组件。
- API 稳定：破坏性变更走版本与迁移说明；提供废弃策略。
- 可主题化、可国际化、可无障碍（自带 Semantics）。
- 日常预览用 `flutter widget-preview`（3.47 工具内置）；视觉回归用 golden 兜底。
- 每个组件有示例与测试；复杂交互有 golden 或 widget 测试。
- 状态组件成套：Empty / Error / Loading / Skeleton，避免各页面自己写。

## 四、状态组件与空态

统一规范：加载、空、错误、无权限、网络异常、超时。每条都要有可执行动作（重试/返回/联系客服），不能只给图标加一句话。

## 五、多端与自适应

- 断点而非设备名：手机 / 平板 / 桌面三档，用 LayoutBuilder 或 MediaQuery。
- 折叠屏：处理展开/折叠时的布局重建与状态保留。
- 横竖屏、分屏、窗口缩放都要验证。
- 桌面端：鼠标悬停、右键、快捷键、滚动行为与移动端不同，组件要支持。

## 六、国际化

- 用 `flutter_localizations` + ARB + gen-l10n，禁止硬编码可见文案。
- 支持复数、性别、序数等 ICU 语法，不要用字符串拼接。
- RTL：用 Directionality 与逻辑属性（start/end），避免写死 left/right。
- 日期、数字、货币用 `intl` 格式化，不要手写格式。
- 文案 key 有命名规范与所有权；缺翻译时要有 fallback，并能在测试中发现。
- 翻译流程要进 CI：新增 key 必须同时更新所有目标语言，或显式标记待翻译。

## 七、无障碍

- Semantics 标注可交互元素；装饰性图片 excludeFromSemantics。
- 点击区域不小于 48x48dp。
- 文本缩放：用 `TextScaler`（`textScaleFactor` 已废弃），布局在大字号下不截断。
- 对比度符合 WCAG AA；不要只靠颜色传达状态。
- 焦点顺序合理，键盘可完成主要操作。
- 支持关闭动画（reduced motion）。

## 八、落地节奏

1. 先梳理现有色板/字号，收敛成 token（允许映射旧值，避免一次性改动全站）。
2. 抽出高频组件，建立组件库包与示例页。
3. 新页面强制用 token 与组件库，旧页面按改动频率逐步替换。
4. 加静态检查：禁止业务层直接写 `Color(0x...)`、`fontSize:` 等硬编码。

## 九、常见坑

- 主题分散在多个 ThemeData 与局部覆盖里，无法统一换肤。
- 组件库没有版本与废弃策略，升级时全站回归。
- 硬编码文案导致后续国际化返工。
- 只做浅色主题验证，深色上线才发现对比度问题。
- 大字号模式没有回归，系统字体放大后布局溢出。

## 十、设计库解耦（material_ui / cupertino_ui）

官方已把 Material 与 Cupertino 从框架内拆成独立包：`material_ui`、`cupertino_ui`（要求 Flutter ≥3.47）。SDK 内的实现保留兼容，但不再是新增能力的入口。

**要不要迁（存量项目）**：同时满足才建议排期——

- 团队已升到 3.47+ 且 CI 稳定；
- 依赖的第三方组件包大多已支持新包，或可用兼容桥隔开；
- 本地化不是重度依赖 `GlobalMaterialLocalizations` 旧路径；
- 近期没有大版本发版窗口。

**迁移步骤**：

1. 加依赖：`flutter pub add material_ui`（按需再加班 cupertino_ui）。
2. 自动改 import：`dart fix --apply --code=migrate_design_widgets`。
3. 本地化：改用新包的 `GlobalMaterialLocalizations.delegates`。
4. 兼容旧依赖：用 `MaterialUiCompatibilityBridge` 包住仍 import 旧路径的子树；它只桥接 ThemeData 与 MaterialLocalizations，属于过渡手段。
5. 回归：主题、字体与行高、暗色、手势、自定义组件、无障碍语义。

**双栈期约束**：禁止新增 `package:flutter/material.dart` 引用；CI 加 import 检查；兼容桥随依赖迁移逐块移除。

**暂不迁的判断**：版本还没到 3.47、依赖链大量未迁移、临近发版——先把解耦列为技术债，设复查时间。
