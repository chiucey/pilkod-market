# 目录结构与交付模板

## 一、目录结构模板

### 小型项目（验证期）

```text
lib/
  app/
  core/
  features/
  main.dart
```

约束：页面可以直接依赖 Repository 接口（跳过 UseCase 层），但禁止直接触达 DataSource/HTTP/数据库；跨 feature 调用必须走接口；必须有统一网络与错误处理。

### 中型项目（Feature-First + 轻量 Clean）

```text
lib/
  app/
    app.dart
    router/{app_router.dart,route_paths.dart,route_guards.dart}
    di/injection.dart
    theme/{app_theme.dart,app_colors.dart,app_text_styles.dart}
  core/
    error/{app_exception.dart,failure.dart,result.dart}
    network/{api_client.dart,interceptors/,api_error_handler.dart}
    storage/{secure_storage.dart,local_storage.dart}
    logger/app_logger.dart
    analytics/analytics_service.dart
    utils/
  features/
    auth/
      data/{datasources/,models/,repositories/}
      domain/{entities/,repositories/,usecases/}
      presentation/{pages/,widgets/,controllers/}
    home/
    profile/
  shared/{widgets/,extensions/,constants/}
  main.dart
```

### 大型项目（Monorepo）

```text
packages/
  core/
  design_system/
  network/
  storage/
  feature_auth/
  feature_home/
  analytics/
  logger/
apps/
  mobile/
  admin/
```

根 pubspec 使用 workspace，子包 `resolution: workspace`。melos 只做版本发布与脚本编排。

环境配置：默认单入口 + `--dart-define`（或 define 文件），避免多 main 入口漏配；多入口只在需要不同初始化路径时使用，并纳入 CI 构建矩阵。

## 二、架构方案交付模板（正式评审用）

```markdown
# Flutter 架构设计方案

## 1. 项目背景假设
- 项目阶段：
- 团队规模：
- 业务复杂度：
- 目标平台：
- Flutter/Dart 版本：
- 性能要求：
- 维护周期：

## 2. 架构目标
- 可维护性：
- 可测试性：
- 可扩展性：
- 性能：
- 交付效率：

## 3. 总体架构
- 架构风格：
- 分层方式：
- 模块划分：
- 依赖方向：

## 4. 目录结构
（贴目录树）

## 5. 状态管理
- 局部状态：
- 页面状态：
- 全局状态：
- 服务端缓存：
- 本地缓存：

## 6. 路由设计
- 路由方案：
- 深链：
- 权限控制：
- 页面参数：
- 状态恢复：

## 7. 网络层设计
- HTTP 客户端：
- 拦截器：
- 错误处理：
- Token 刷新：
- 缓存策略：

## 8. 存储设计
- 安全存储：
- 普通存储：
- 数据库：
- 文件存储：

## 9. 测试策略
- 单元测试：
- Widget 测试：
- 集成测试：
- 关键验收指标：

## 10. 工程化
- Lint：
- Codegen：
- CI/CD：
- 多环境：
- 发布与灰度：

## 11. 风险与替代方案
- 风险 1：
- 替代方案：

## 12. 分阶段落地计划
- 第一阶段：
- 第二阶段：
- 第三阶段：
```

示例回答、自测题与代码示例原则见 `references/examples.md`。
