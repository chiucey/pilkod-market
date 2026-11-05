# 翻译参考指南

## 计算机领域常用术语对照表

| 英文 | 中文 | 原文注释 |
|------|------|----------|
| API | 应用程序接口 | Application Programming Interface |
| SDK | 软件开发包 | Software Development Kit |
| SDK | 软件开发工具包 | Software Development Kit (alternative) |
| framework | 框架 | - |
| library | 库/函数库 | - |
| module | 模块 | - |
| package | 包 | - |
| dependency | 依赖项 | - |
| runtime | 运行时 | - |
| compile | 编译 | - |
| build | 构建 | - |
| deploy | 部署 | - |
| server | 服务器 | - |
| client | 客户端 | - |
| endpoint | 端点 | - |
| request | 请求 | - |
| response | 响应 | - |
| database | 数据库 | - |
| query | 查询 | - |
| cache | 缓存 | - |
| protocol | 协议 | - |
| serialization | 序列化 | - |
| deserialization | 反序列化 | - |
| asynchronous | 异步的 | - |
| synchronous | 同步的 | - |
| thread | 线程 | - |
| process | 进程 | - |
| concurrency | 并发 | - |
| parallelism | 并行 | - |
| recursion | 递归 | - |
| iteration | 迭代 | - |
| exception | 异常 | - |
| debugging | 调试 | - |
| logging | 日志记录 | - |
| configuration | 配置 | - |
| authentication | 身份验证/认证 | - |
| authorization | 授权 | - |
| encryption | 加密 | - |
| decryption | 解密 | - |
| middleware | 中间件 | - |
| scalability | 可扩展性 | - |
| reliability | 可靠性 | - |
| maintainability | 可维护性 | - |
| performance | 性能 | - |
| optimization | 优化 | - |

## 翻译常见问题处理

### 1. 缩写词处理

**规则**：
- 首次出现时：中文全称 + 英文缩写 + 英文原文
- 格式：`首字母大写的缩写 (English Full Name)`

**示例**：
- `gRPC (Remote Procedure Call)` → gRPC (远程过程调用，Remote Procedure Call)

### 2. 专有名词处理

**规则**：
- 采用业界通用译法
- 首次出现时保留英文并附中文

**示例**：
- `Kubernetes` → Kubernetes（容器编排平台）
- `Docker` → Docker（容器运行时）

### 3. 品牌与产品名

**规则**：
- 保持原文不变
- 已注册商标使用 TM 标注（如有需要）

### 4. 代码与命令

**规则**：
- 代码片段保留英文
- 命令行示例保留原格式
- 注释翻译为中文

**示例**：
```markdown
```bash
git commit -m "提交信息"  # Keep the command, translate comments
```
```

### 5. 句子结构转换

**英文 → 中文**：
- 英文重主语，中文重主题
- 英文长句 → 中文短句
- 被动语态 → 主动语态或无主语

**示例**：
> "It is recommended that you should..."

译文："建议您..."

## 格式保持规则

### 超链接

原样保留 Markdown 链接格式：
```markdown
[链接文本](URL)
```

### 图片引用

```markdown
![图片描述](图片路径)
```

### 表格

保持 Markdown 表格格式不变。

### 引用块

使用 `>` 保持引用层级：
```markdown
> 一级引用
>> 二级引用
```

## 文化背景翻译注意事项

1. **双关语**：尽量保留双关效果，无法保留时加注
2. **文化专有项**：保留原文化元素，必要时加注
3. **玩笑与讽刺**：理解意图，翻译效果而非字面

## 质量自检问题

1. 术语是否统一？
2. 是否有漏译？
3. 是否符合中文习惯？
4. 格式是否正确？
5. 专业术语是否有注解？