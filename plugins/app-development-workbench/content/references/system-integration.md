# 系统入口与新版本界面

## 动作链路

按“外部触发 → 参数/实体解析 → 当前身份/权限 → 领域服务 → 结果或 App 路由”逐步核验。记录动作是否可后台完成，是否需用户确认，是否打开 App。实体查询只返回调用身份可访问的数据，不把系统搜索当作授权绕过。

AppIntent 保持薄层；AppEntity 只包含系统理解所需标识与展示字段，EntityQuery 处理查找/歧义，固定选项优先 AppEnum。通过 AppShortcutsProvider 提供少量有价值短语。实际命名和 API availability 以所用 SDK 为准。

测试冷/热启动、未登录、对象删除、权限拒绝与取消；开 App 的动作确认实际落地页，内联动作确认真实业务结果。系统中可发现、编译通过和直接调用 perform 是不同证据。

## Liquid Glass 与兼容

按当前 Apple 文档与工程 SDK 检查 glassEffect 等 API 的 OS 版本要求。使用 availability 保护，旧系统保持可读、可点击的明确回退；不拿圆角加模糊冒称原生材质。

先使用标准容器，再根据明确需求组合自定义材质。考虑 Reduced Transparency/Motion、动态字体、背景对比和工具栏边界。新视觉不改变项目锁定的背景/配色，不引入第二套主题或擅改业务结构。

来源：[App Intents](https://developer.apple.com/documentation/appintents)、[Creating your first app intent](https://developer.apple.com/documentation/appintents/creating-your-first-app-intent)、[Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)。
