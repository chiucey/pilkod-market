# 技术指南模板规范

## 文档定位

技术指南用于指导用户完成特定任务，强调步骤化和可操作性。

## 标准结构

```markdown
# 技术指南标题

## 概述

简要说明本指南的目标和适用场景。

**目标：** 完成本指南后，你将能够...

**前置条件：**

- 已安装 Node.js 18+
- 已配置开发环境
- 了解基本的 TypeScript 语法

**预计时间：** 30 分钟

## 步骤 1：环境准备

### 1.1 安装依赖

首先，克隆项目仓库：

```bash
git clone https://github.com/example/project.git
cd project
```

安装项目依赖：

```bash
npm install
```

### 1.2 配置环境变量

创建 `.env` 文件：

```env
API_KEY=your_api_key
DATABASE_URL=postgresql://localhost:5432/mydb
```

### 验证步骤

运行以下命令验证环境是否配置正确：

```bash
npm run check-env
```

如果输出 `Environment is ready!`，说明配置成功。

## 步骤 2：核心实现

### 2.1 创建主模块

创建 `src/index.ts` 文件：

```typescript
import { Client } from './client';

export class Application {
  private client: Client;

  constructor(config: Config) {
    this.client = new Client(config);
  }

  async start() {
    await this.client.connect();
    console.log('Application started');
  }
}
```

### 2.2 实现业务逻辑

添加业务处理方法：

```typescript
async processData(input: Input): Promise<Output> {
  // 1. 验证输入
  this.validateInput(input);

  // 2. 调用 API
  const response = await this.client.request(input);

  // 3. 处理响应
  return this.transform(response);
}
```

## 步骤 3：测试与验证

### 3.1 编写测试用例

创建测试文件：

```typescript
describe('Application', () => {
  it('should process data correctly', async () => {
    const app = new Application(config);
    const result = await app.processData(testInput);
    expect(result.status).toBe('success');
  });
});
```

### 3.2 运行测试

```bash
npm test
```

### 预期结果

```
✓ should process data correctly (15ms)
Test Suites: 1 passed
Tests:       1 passed
```

## 步骤 4：部署

### 4.1 构建生产版本

```bash
npm run build
```

### 4.2 部署到服务器

```bash
npm run deploy
```

## 常见问题

### 问题 1：连接失败

**症状：** 运行时报错 `Connection refused`

**解决方案：**

1. 检查 API_KEY 是否正确
2. 确认网络连接正常
3. 验证服务端是否运行

### 问题 2：内存不足

**症状：** 进程被系统终止

**解决方案：**

增加 Node.js 内存限制：

```bash
NODE_OPTIONS="--max-old-space-size=4096" npm start
```

## 进阶主题

- [性能优化](./advanced/performance.md)
- [错误处理最佳实践](./advanced/error-handling.md)
- [扩展功能开发](./advanced/extensions.md)

## 总结

本指南介绍了如何：

1. 配置开发环境
2. 实现核心功能
3. 测试和部署应用

下一步建议：

- 阅读 [API 文档](./api.md)
- 查看 [示例项目](./examples/)
- 加入 [社区讨论](https://community.example.com)

## 参考资源

- [官方文档](https://docs.example.com)
- [API 参考](https://api.example.com/docs)
- [问题反馈](https://github.com/example/project/issues)
```

## 必选章节

| 章节 | 说明 |
|------|------|
| 概述 | 说明目标、前置条件、预计时间 |
| 步骤 | 分步骤的详细说明 |
| 验证 | 每步的验证方法 |
| 总结 | 回顾要点和下一步建议 |

## 推荐章节

| 章节 | 说明 |
|------|------|
| 常见问题 | 典型问题及解决方案 |
| 进阶主题 | 进阶内容链接 |
| 参考资源 | 相关文档和资源 |

## 质量检查要点

1. **前置条件**：明确列出所需环境
2. **步骤编号**：使用层级编号（1.1, 1.2）
3. **代码示例**：提供可直接运行的代码
4. **验证步骤**：说明如何验证每步是否成功
5. **预计时间**：提供时间估算

## 写作规范

### 步骤描述

使用祈使句，清晰明确：

❌ 错误：
```markdown
接下来你可以尝试安装依赖
```

✅ 正确：
```markdown
安装项目依赖：

```bash
npm install
```
```

### 验证说明

提供明确的验证方法：

❌ 错误：
```markdown
检查配置是否正确
```

✅ 正确：
```markdown
验证配置是否正确：

```bash
npm run check-env
```

预期输出：

```
Environment is ready!
```
```

### 错误处理

包含常见错误和解决方案：

```markdown
### 常见错误

**错误：** `ENOENT: no such file or directory`

**原因：** 文件路径不正确

**解决方案：**

1. 确认当前目录是否正确
2. 检查文件是否存在
3. 使用绝对路径重试
```
