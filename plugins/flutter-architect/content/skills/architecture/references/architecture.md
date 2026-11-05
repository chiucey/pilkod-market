# 架构与模块化

## 一、分层

两种常见分法，二选一并在团队内统一：

```text
Presentation / Domain / Data
```

```text
UI / Application / Domain / Infrastructure
```

| 层 | 负责 | 禁止 |
|---|---|---|
| Presentation | 展示、交互、路由、UI 状态 | 业务规则、直接网络/数据库访问 |
| Domain | 实体、用例、仓储接口、值对象、领域事件 | 依赖 Flutter、网络库、数据库库 |
| Data | 仓储实现、远端/本地数据源、缓存、映射、DTO | 承载业务规则、直接驱动 UI |

依赖方向永远向内：Presentation → Domain ← Data。Domain 不 import Flutter 与三方数据框架。

## 二、Clean Architecture 的适用判断

适合：
- 业务规则复杂，且需要长期维护
- 多端复用同一份领域逻辑
- 团队有人能维护分层约定
- 有测试投入

不适合（要明确说出来）：
- 生命周期短、验证期项目
- 页面以 CRUD 为主，无复杂规则
- 团队对分层不熟且没有时间培训
- 强行分层会让文件数翻数倍、心智负担大于收益

判断句式：业务规则能不能脱离 UI 独立描述？能 → 值得分层；不能 → 先简化。

## 三、Feature-First

每个 feature 内部自带三层，feature 之间禁止直接 import 彼此的 presentation 层。

```text
lib/
  app/          # 启动、路由、DI、主题
  core/         # 网络、存储、错误、日志、埋点、工具
  features/
    auth/{data,domain,presentation}
    home/{data,domain,presentation}
  shared/       # 跨 feature 的通用 UI 与扩展
```

规则：
- feature 只能依赖 core / shared / 自己的内部。
- 跨 feature 调用走 use case 或事件，不直接读对方的页面状态。
- 公共能力下沉到 core 前先确认被 2 个以上 feature 使用。

## 四、模块化与 Monorepo

拆包的判断标准（满足 2 条以上才拆）：
- 有独立发布节奏或独立团队
- 需要编译隔离来约束依赖
- 被多个 App 复用
- 构建时间已经明显影响迭代

优先用 Dart 官方 pub workspace（Dart 3.6+）：

```yaml
# 根 pubspec.yaml
name: my_app_workspace
environment:
  sdk: ^3.6.0
workspace:
  - packages/core
  - packages/design_system
  - apps/mobile
```

各子包写 `resolution: workspace`，共享一份依赖解析与 lockfile。

melos 只解决 workspace 之外的问题：跨包版本发布、changelog、脚本编排。不要用自研脚本替代 pub workspace。

拆包代价必须提前说：依赖管理复杂、版本对齐成本、IDE 索引变慢、CI 需要分片。

## 五、依赖规则落地

- 用目录约定 + CI 检查（自定义 lint、import 检查脚本）保证依赖方向。
- 禁止循环依赖：A 依赖 B 且 B 依赖 A 时，抽出接口到第三方包或 core。
- 可用手段：`custom_lint`（跨包/跨层 import 规则）+ CI 里跑 `dart run custom_lint`；analyzer 本身表达不了"A 禁止依赖 B"，需要自定义规则或脚本。
- 公共代码下沉前先看是否只有一个使用者。
- 大文件、巨 Widget 是职责不清的信号，不是格式问题。

## 六、路由设计

| 场景 | 建议 |
|---|---|
| 单栈小应用 | Navigator 1.0 + 集中路由表 |
| 需要深链、Web URL、多入口 | go_router（声明式，官方维护） |
| 大量页面且要 codegen | auto_route |
| 状态恢复 | Router API + RestorationMixin |

集中管理至少包含：
- 路由常量/枚举，禁止字符串散落
- 守卫（登录、权限、灰度）
- 参数解析与默认值
- 深链映射与兜底页
- 页面级埋点与时长统计的挂钩点

架构师要回答：路由是否可测试？是否支持深链？能否统一加权限？能否统一埋点？

## 七、依赖注入

| 方案 | 适用 |
|---|---|
| 构造函数注入 + 简单作用域 | 首选，成本最低 |
| provider / riverpod | 依赖与状态一起管理 |
| get_it + injectable | 已有存量项目、需要 service locator |
| bloc provider | 生态内统一 |

原则：
- 依赖显式，不在 Widget 内部 new 服务
- 生命周期清晰：单例 / 页面级 / 请求级
- 避免全局单例膨胀，避免把 service locator 当全局变量用
- 可测试：测试能替换任意实现

## 八、多环境

需要支持：dev / staging / prod（可加 mock、local）。

差异化项：API host、密钥占位、feature flag、日志级别、监控开关、调试工具、三方 SDK key。

实现方式优先级：
1. `--dart-define` + 编译期常量（推荐，避免敏感值进仓库）
2. flavor / scheme 双端配置（Android productFlavors、iOS scheme）
3. 独立 main 入口文件（简单但易漏配）

禁止把生产密钥写进仓库或写进客户端可读配置。

## 九、演进策略

治理技术债的顺序：
1. 建立规范与模板（新代码必须合规）
2. 修复高频变更模块
3. 抽象公共层（网络、错误、日志、路由）
4. 试点重构一个核心页面，形成模板
5. 每迭代留 10%~20% 处理技术债

不要一次性全量重写。验收标准示例：页面不直接依赖 Dio、业务逻辑可单测、仓储可 mock、错误提示统一。
