# 错误处理规范

## 原则

- **防御编程**：信任外部输入，验证所有数据
- **fail fast**：出错了尽快暴露，不要静默传播
- **有意义的信息**：错误信息能帮助定位问题

## 规范

### 1. 参数校验
```typescript
function divide(a: number, b: number): number {
  if (b === 0) throw new Error("除数不能为0")
  return a / b
}
```

### 2. 网络/API 错误
```typescript
async function fetchData(url: string) {
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`请求失败: ${res.status}`)
    return await res.json()
  } catch (e) {
    throw new Error(`获取数据失败: ${url}, ${e.message}`)
  }
}
```

### 3. 空值处理
```typescript
// 有数据才处理
const balance = account?.balance ?? 0

// 列表空状态
if (!items.length) return "暂无数据"
```

### 4. 错误信息格式
```
[模块] 操作描述：失败原因 | 上下文信息
```
