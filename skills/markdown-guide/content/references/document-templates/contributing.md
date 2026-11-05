# 贡献指南模板规范

## 文档定位

贡献指南用于指导开发者如何参与项目开发，包括环境搭建、代码规范、提交流程等。

## 标准结构

```markdown
# 贡献指南

感谢你考虑为本项目做出贡献！

## 行为准则

本项目采用贡献者公约作为行为准则。
参与此项目即表示你同意遵守其条款。
请阅读 [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) 了解详情。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请通过 [GitHub Issues](https://github.com/example/project/issues) 提交。

**提交前请确认：**

- 使用最新版本测试
- 搜索已有 Issues，避免重复
- 提供完整的复现步骤

**Bug 报告模板：**

```markdown
**描述**
清晰简洁地描述 Bug。

**复现步骤**
1. 进入 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

**预期行为**
描述你期望发生的情况。

**实际行为**
描述实际发生的情况。

**截图**
如适用，添加截图帮助解释问题。

**环境信息**
- OS: [e.g. macOS 14.0]
- Browser: [e.g. Chrome 120]
- Version: [e.g. 2.1.0]

**附加信息**
其他任何有助于解决问题的信息。
```

### 提出新功能

如果你有新功能建议，欢迎创建 Feature Request。

**建议模板：**

```markdown
**功能描述**
清晰描述你希望添加的功能。

**使用场景**
描述这个功能能解决什么问题。

**建议方案**
如果你有实现思路，请描述。

**替代方案**
描述你考虑过的其他方案。

**附加信息**
其他相关信息或截图。
```

### 提交代码

#### 1. Fork 项目

点击右上角 Fork 按钮，将项目复制到你的账户。

#### 2. 克隆仓库

```bash
git clone https://github.com/your-username/project.git
cd project
```

#### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
```

分支命名规范：
- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档更新
- `refactor/` - 代码重构

#### 4. 安装依赖

```bash
npm install
```

#### 5. 进行开发

编写代码，确保：

- 遵循代码规范
- 添加必要的测试
- 更新相关文档

#### 6. 运行测试

```bash
npm test
```

确保所有测试通过。

#### 7. 提交更改

```bash
git add .
git commit -m "feat: add new feature"
```

提交信息格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型说明：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：

```
feat(auth): add OAuth2 support

- Add Google OAuth provider
- Add GitHub OAuth provider
- Update auth documentation

Closes #123
```

#### 8. 推送分支

```bash
git push origin feature/your-feature-name
```

#### 9. 创建 Pull Request

前往 GitHub 页面创建 PR。

**PR 模板：**

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 变更说明
描述此 PR 的变更内容。

## 相关 Issue
Closes #

## 测试
描述如何测试此变更。

## 检查清单
- [ ] 代码符合项目规范
- [ ] 已添加测试
- [ ] 所有测试通过
- [ ] 已更新文档
```

## 开发环境

### 系统要求

- Node.js 18+
- npm 9+
- Git

### 项目结构

```
project/
├── src/           # 源代码
├── tests/         # 测试文件
├── docs/          # 文档
├── examples/      # 示例代码
└── scripts/       # 构建脚本
```

### 本地运行

```bash
# 开发模式
npm run dev

# 构建
npm run build

# 测试
npm test

# 代码检查
npm run lint
```

## 代码规范

### TypeScript 规范

- 使用 TypeScript 严格模式
- 所有公共 API 必须有类型注解
- 使用接口定义数据结构

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类 | PascalCase | `UserService` |
| 函数 | camelCase | `getUserById` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 文件 | kebab-case | `user-service.ts` |

### 注释规范

```typescript
/**
 * 获取用户信息
 * @param userId 用户 ID
 * @returns 用户信息对象
 * @throws UserNotFoundError 用户不存在时抛出
 */
async function getUser(userId: string): Promise<User> {
  // 实现
}
```

## 测试规范

### 单元测试

每个模块都应有对应的测试文件：

```
src/
  user-service.ts
tests/
  user-service.test.ts
```

测试示例：

```typescript
describe('UserService', () => {
  it('should return user by id', async () => {
    const user = await userService.getById('user_123');
    expect(user.id).toBe('user_123');
  });
});
```

### 测试覆盖率

保持测试覆盖率在 80% 以上：

```bash
npm run test:coverage
```

## 发布流程

1. 更新 CHANGELOG.md
2. 更新版本号
3. 创建 Git Tag
4. 构建发布包
5. 发布到 npm

## 获取帮助

- 查看 [文档](./docs/)
- 加入 [Discord 社区](https://discord.gg/example)
- 在 [Discussions](https://github.com/example/project/discussions) 提问

## 许可证

提交代码即表示你同意你的代码将根据项目的 MIT 许可证授权。
```

## 必选章节

| 章节 | 说明 |
|------|------|
| 行为准则 | 社区规范 |
| 如何贡献 | Bug 报告、功能建议、代码提交流程 |
| 开发环境 | 环境搭建说明 |
| 代码规范 | 编码标准 |

## 推荐章节

| 章节 | 说明 |
|------|------|
| 项目结构 | 目录结构说明 |
| 测试规范 | 测试要求 |
| 发布流程 | 发布步骤 |
| 获取帮助 | 社区资源 |

## 质量检查要点

1. **流程清晰**：步骤编号明确
2. **模板完整**：提供 Issue/PR 模板
3. **代码规范**：有明确的编码标准
4. **测试要求**：说明测试覆盖率要求
5. **联系方式**：提供获取帮助的途径
