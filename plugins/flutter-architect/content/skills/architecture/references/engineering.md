# 工程化与发布

## 一、代码规范

- analysis_options.yaml 统一 lint，禁止各包各写一套。
- 提交规范（Conventional Commits）、PR 模板、review 检查表。
- 架构约束检查：依赖方向、禁止跨层 import，用脚本或自定义 lint 在 CI 里卡。
- 文档规范：模块 README、ADR（架构决策记录）、变更记录。

## 二、代码生成流水线

常用：build_runner、freezed、json_serializable、riverpod_generator、injectable、auto_route、drift/isar schema。

治理规则：
- 生成物默认不入库；CI 生成后校验无 diff。
- 生成代码禁止手改。
- 按包拆分生成任务，避免整仓全量生成拖慢迭代。
- 生成失败必须阻断合并，不允许"合并后补"。
- PR 中排除或折叠生成物，避免淹没真实改动。
- API 契约是否参与生成？（OpenAPI/Protobuf → 模型与错误码枚举；契约变更走 CI diff，禁止手写 DTO 与服务端漂移）

## 三、测试策略

| 层 | 测什么 | 要求 |
|---|---|---|
| 单元 | UseCase、Repository、Mapper、状态机、工具 | 领域层高覆盖，关键逻辑必须有 |
| Widget | 渲染、交互、状态切换、表单校验、空/错/加载态 | 核心组件必须覆盖 |
| Golden | 视觉一致性、主题、多尺寸、暗黑、字体缩放 | 用 matchesGoldenFile 或 alchemist；golden_toolkit 已停止维护 |
| 集成 | 登录、下单、支付、路由、权限、真实网络或 mock server | 关键链路冒烟 |
| 原生 E2E | 相机、权限、推送等原生交互 | integration_test + patrol |

可测试性检查：依赖可注入、副作用可隔离、时间可模拟、网络可 mock、随机性可控、状态可断言。

## 四、CI/CD

流水线至少包含：format → analyze → build_runner 校验 → test + coverage → 构建产物 → 版本号与变更记录 → 分发。

- 构建：apk/appbundle/ipa/desktop 安装包；Web 构建产出体积报告。
- 质量门禁：新增代码覆盖率、lint 零新增告警、包体积增量阈值。
- 移动端分发：Firebase App Distribution / TestFlight / 内部商店。
- 工具链：GitHub Actions、GitLab CI、Codemagic、Bitrise、Fastlane、Renovate/Dependabot。

## 五、构建与缓存成本

- 冷启动构建时间：CI 缓存 pub、Gradle、CocoaPods/SPM、build_runner 增量。
- 缓存失效条件要写清（lockfile、Flutter 版本、原生依赖）。
- 并行分片与产物复用，避免每个 PR 全量重建。

## 六、可观测性

必须覆盖：崩溃、异常、性能、网络、用户行为、业务指标、日志、开关、灰度、A/B、远程配置、告警。

工具：Firebase Crashlytics、Sentry、Datadog、OpenTelemetry、Mixpanel/Amplitude、自研 APM；国内可选 Bugly 等。

架构师要回答：
- 崩溃多久能发现？能否定位到用户路径与版本/渠道/平台？
- API 失败率、启动耗时、关键页面帧率是否有监控？
- 高风险功能能否在分钟级关闭（开关/远端配置）？
- 符号表是否上传，崩溃栈能否还原到源文件行号？

## 七、安全与合规

- 本地敏感数据加密（keychain/keystore/secure storage）。
- 网络安全：HTTPS、证书固定（评估成本）、防抓包（提升攻击成本，不要宣称绝对安全）。
- Token：短期 + 刷新、存储加密、登出清理。
- 权限最小化、日志脱敏、埋点最小必要。
- 三方 SDK 清单与数据流向说明；隐私政策与服务端数据留存一致。
- 应用商店合规：账号注销、权限说明、隐私清单。

## 八、发布工程

上线链路最容易出事故，必须显式设计：

- Dart 混淆：`flutter build ... --obfuscate --split-debug-info=<dir>`。
- 符号表 / mapping / dSYM 上传到崩溃平台，否则崩溃栈不可解。
- Android：R8/ProGuard 规则、签名 v2/v3、Play App Bundle 分阶段灰度。
- iOS：归档导出、TestFlight 分级发布、审核被拒的常见架构问题。
- 包体积归因：`--analyze-size --target-platform <单个 ABI>`，与 `--split-debug-info` 互斥，需拆成两条流水线；CI 设体积阈值告警。
- 回滚：开关降级、远端配置、灰度暂停；Flutter 无官方热修，第三方热修（如 Shorebird 类差分 AOT）要单独评估商店条款（Apple 2.5.2、Play 动态代码政策）、成本与维护风险，并预留审核路径。
- 发布清单：版本号策略、构建号自增、变更记录、灰度观察指标、回滚负责人。

验收问题：崩溃能定位到混淆前的行号吗？灰度出问题时多久能全量关闭？线上包如何对应到具体 commit 与符号表？

## 九、团队协作与决策记录

- ADR（架构决策记录）：每条写清背景、备选方案、决策、后果、复查时间；放在仓库 docs/decisions 下，评审时直接引用。
- 评审分层：架构变更走方案评审，接口变更走设计评审，实现走代码评审；不要所有事都用同一套流程。
- 技术债量化：构建时长、analyze 告警数、deprecated 与 TODO 计数、核心链路覆盖率、崩溃率、包体积、变更失败率与恢复时间。
- 规范只有进 CI 才有效：文档负责解释，检查负责执行。
- 关键模块指定 owner；故障复盘对事不对人，产出改进项并跟踪闭环。
