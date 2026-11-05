# Dart 语言与并发

## 一、用语言特性表达架构约束

| 特性 | 架构用途 |
|---|---|
| `sealed class` + 模式匹配 | 状态建模（Loading/Data/Error），switch 穷尽，漏分支编译期发现 |
| `final` / `base` / `interface` | 限制继承与实现，保护领域模型不被外部扩展 |
| `records` | 轻量多返回值，避免为 2 个字段造类 |
| extension type | 给 ID、金额、单位做零成本类型包装，防止参数混用 |
| `typedef` | 表达回调契约，避免裸函数类型散落 |

推荐的 UI 状态建模：

```dart
sealed class UiState<T> {
  const UiState();
}

final class Loading<T> extends UiState<T> { const Loading(); }
final class Data<T> extends UiState<T> { const Data(this.value); final T value; }
final class Failure<T> extends UiState<T> { const Failure(this.error); final Object error; }
```

好处：UI 用 switch 一次性处理全部状态，新增状态时编译器报错，避免漏写 loading/error。

## 二、异步与事件循环

- 单线程事件循环：microtask（Future 回调）先于 event queue（Timer、IO、事件）。
- 不要在 build 中创建 Future 或订阅；用 initState/生命周期入口。
- `await` 之后必须重新检查 `mounted` / `context.mounted` 再碰 Context。
- `Future` 不可取消：需要取消就用 `StreamSubscription`、Completer + 令牌，或把工作丢给 isolate。
- `Stream` 必须显式取消；broadcast stream 要确认监听者生命周期。
- Zone 只用于统一错误捕获/埋点，不要用它做业务状态传递。

## 三、并发与 isolate

必须移出主 isolate 的典型工作：大 JSON 解析、图片编解码、加解密、压缩、大文件 IO、复杂计算。

选择：
- 一次性任务：`Isolate.run` 或 `compute`。
- 常驻 worker：独立 isolate + SendPort，自己做任务队列与背压。
- 大量同构任务：固定并发上限（例如 4~8），不要 each 起一个 isolate。

注意：
- 消息是复制，不是共享内存；大对象传输有成本，优先传路径或 `TransferableTypedData`。
- isolate 内不能用 rootBundle、不能直接访问 UI；需要传初始化数据。
- 启动 isolate 有成本，热路径不要频繁创建。

## 四、并发缺陷清单

- 竞态：并发请求后写同一个状态，后到的旧结果覆盖新结果 → 用请求序号或取消令牌。
- 重复提交：按钮连点 → 提交中禁用 + 服务端幂等键。
- 泄漏：页面退出后 setState、Stream 未取消、Timer 未取消。
- 阻塞：同步文件/数据库调用、`jsonDecode` 大文本、正则回溯、递归深拷贝。
- 隐式共享可变对象：Repository 返回内部 List，UI 修改造成状态污染 → 返回不可变视图或副本。

## 五、性能相关的语言习惯

- `const` 与 `const` 构造用于可确定性创建，减少 rebuild 与内存。
- 避免在 build 里做字符串拼接、格式化、排序、过滤；提前算或缓存。
- 集合操作优先单次遍历；避免 `map(...).toList()` 链式在热路径反复执行。
- `late` 只用于确有初始化保证的场景；滥用会把崩溃推迟到更难定位的地方。
- 谨慎使用 `!`：能结构化判空就判空；空断言应伴随不变量说明。
- 动态调用（`dynamic`）会破坏树摇与类型检查，热路径避免。

## 六、评审要点

- 状态是否用 sealed/不可变模型表达，而不是一堆 nullable 字段？
- 长耗时任务是否在主 isolate？
- 订阅与控制器是否成对释放？
- 并发写同一份状态时，是否有明确的串行化或版本控制？
- 是否有依赖隐式全局可变状态的代码？
