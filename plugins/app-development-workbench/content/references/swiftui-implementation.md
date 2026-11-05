# SwiftUI 实施细则

先读取当前 deployment target、SDK 和工程惯例。API 选择以 Apple 对应版本文档为准，不能把最新 API 无条件塞进旧系统路径。

## 数据所有权

| 情况 | 选择方向 |
|---|---|
| 页面自己的值状态 | @State |
| 子视图需要改父级值 | @Binding |
| iOS 17+ 根视图拥有 Observable 引用 | @State + @Observable |
| 注入的 Observable | 显式传入，按需 @Bindable |
| 跨功能真正共享的服务 | 有明确生命周期的依赖容器或 Environment |
| 旧系统 ObservableObject | owner 用 @StateObject，注入用 @ObservedObject，环境共享按实际范围 |

现有 ViewModel 合理时保留；不要强制全部改 MV，也不要给每个值包装类。依赖初始化明确，不用 optional 模型掩盖必要依赖缺失。

## 导航与副作用

NavigationStack 路径、Tab 和 sheet 使用明确路由/对象；互斥显示不要依靠多个互相冲突布尔值。每个 Tab 的历史、深链和退出登录重置按产品语义设计。异步任务与输入身份绑定，处理取消与迟到响应；重试沿用原输入并保留错误状态。

body 表达 UI，复杂动作有命名入口，领域逻辑放服务。列表稳定 ID 不能使用每次生成的 UUID。高代价格式化、解码或排序不反复放 body；性能优化需测量，不盲目缓存。

## 页面完成检查

核对标题、信息优先级、主操作、返回、表单验证、键盘避让、安全区域、长内容、动态字体、VoiceOver 与可点击区域。从设计样例中识别假的数据与权限，并以真实业务返回替换。使用 fixtures 能演示状态，但真实接口与持久化独立验证。

新页面先构建骨架，编译问题解决后再扩展。共享组件样式变更核对所有调用方。普通开发用正常 App 与 Simulator，#Preview 是隔离检查工具，不能代替整条业务运行。

来源：[SwiftUI](https://developer.apple.com/documentation/swiftui)、[Observation](https://developer.apple.com/documentation/observation)、[Migrating to Observation](https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro)。
