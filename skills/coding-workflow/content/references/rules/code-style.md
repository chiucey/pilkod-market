# 代码风格规范

## 格式

- 缩进：2 空格（配置文件除外）
- 一行不超过 120 字符
- 文件末尾留一个空行
- import 按：内置 → 第三方 → 本地 排序

## 注释

- **注释 Why，不注释 What**：
  ```typescript
  // 用 Math.random 而不是自定义随机（密码学安全）
  const salt = crypto.randomBytes(16)

  // 注意：这里不用 else，因为上面已经 return 了
  ```

- **注释代码而不是注释掉代码**：有意义的注释保留，无用代码删除

## 函数

- 每个函数不超过 30 行
- 函数只做一件事
- 避免超过 3 个参数：用对象代替
  ```typescript
  // 不好
  createUser(name, email, age, role, avatar, bio)

  // 好
  createUser({ name, email, age, role, avatar, bio })
  ```

## 类型

- 显式类型注解（不依赖推断）
- 接口优于类型别名（可扩展）
- 不使用 `any`
