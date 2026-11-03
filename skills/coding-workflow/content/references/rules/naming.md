# 命名规范

## 核心原则

> 好的命名是最重要的注释，让人不用看代码就能理解意图。

## 函数命名

| 场景 | 命名规则 | 示例 |
|------|---------|------|
| 执行操作 | 动词 + 宾语 | `saveAccount()`, `deleteUser()` |
| 返回布尔 | is/has/can/should | `isValidEmail()`, `hasPermission()` |
| 查询数据 | get/find/fetch | `getBalance()`, `findById()` |
| 转换数据 | to/toXxx/parse | `toYuan()`, `parseDate()` |
| 判断条件 | 形容词或名词 | `isEmpty()`, `isExpired()` |

## 变量命名

- 布尔：`isXxx`, `hasXxx`, `canXxx`（用 is/has/can）
- 数组：`名词复数` 或 `xxxList`：`accounts`, `items`
- 数字：`xxxCount`, `xxxTotal`
- 时间：`xxxAt`（时间点）, `xxxSince`（时长）

## 常量命名

- 全大写下划线分隔：`MAX_RETRY_COUNT`
- 或 PascalCase：`ApiEndpoints`

## 禁止的命名

- 拼音、中文缩写
- 纯类型名：`data`, `info`, `temp`
- 单字母（循环除外：`i`, `j`）
- 模糊缩写：`x` 代替 `account`
