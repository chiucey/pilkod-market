# 测试文件模板

## 原则

1. 测试名 = 描述行为：`describe("做某事", it("在某种情况下，期望结果"))`
2. Arrange-Act-Assert 结构
3. 一个测试只测一件事

## 模板

```typescript
// {模块名}.test.ts

describe("模块名", () => {
  describe("核心功能", () => {
    it("在 X 条件下，期望 Y 结果", () => {
      // Arrange：准备数据
      const input = "test value"

      // Act：执行操作
      const result = myFunction(input)

      // Assert：验证结果
      expect(result).toBe("expected")
    })

    it("在空值输入时，抛出错误", () => {
      expect(() => myFunction("")).toThrow("输入不能为空")
    })
  })
})
```

## 优先测试的场景

- 边界条件（空值、零、负数、超大值）
- 错误处理
- 核心业务逻辑
- 多条件分支（if/else 的每个分支）
