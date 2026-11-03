---
name: ios-system-integration
description: 用于 App Intents、App Shortcuts、Siri、Spotlight、Widget/Control，以及 Liquid Glass 等版本受限界面能力。按用户动作和最低系统版本实施并验证路由与回退。
---

# 接入 iOS 系统动作与界面能力


读取 [系统接入](../../references/system-integration.md)，确认本轮是系统动作、系统 UI 或两者。只加载对应参考，不因为用户提 iOS 就添加所有入口。

## App Intents 与实体
从用户希望在 App 外完成的 1–3 个高价值动作开始，确定参数、结果、权限与是否需打开 App。固定选项可用 AppEnum；需要系统识别和查询的业务对象才建立小型 AppEntity 与 EntityQuery，不暴露完整数据库模型。

Intent 调用已有领域服务，避免另写一份业务逻辑。打开 App 的动作经过单一可追踪路由，覆盖冷启动、热启动、未登录和对象不存在。内联动作只在满足权限与执行条件时完成，不静默绕过确认或账号校验。

为有效动作增加 AppShortcutsProvider 和易理解短语；Widget/Control 使用同一动作与参数模型。构建成功后从实际系统入口触发，检查实体解析、动作结果与落地页；编辑器里调用 perform 不能替代 Siri/Shortcuts 可发现性验证。

## 系统视觉能力
读取工程 SDK 与 deployment target，查 Apple 对应 API 的 availability。优先采用标准导航/工具栏材质，只有明确需求才定制玻璃；不要用多层透明叠加破坏层级和可读性。

新 API 放入明确 availability 分支，为最低支持 OS 提供可用回退。Token 与共享组件承载样式；锁定背景、业务结构和导航不能因采用新材质被擅自修改。检查动态字体、对比度、减少透明度/动态效果和主操作可达性。

交付实际开放的动作、实体、入口、系统版本和测试结果；新系统运行与旧系统回退分别记录，SDK 可编译不代表两者都已体验。
