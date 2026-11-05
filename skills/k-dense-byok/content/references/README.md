# K-Dense BYOK 参考文档

## 项目概述

K-Dense BYOK (Bring Your Own Keys) 是一个开源的 AI 研究助手应用，允许用户在本地运行强大的 AI 工作空间。

## 核心架构

### 1. 编排层 (Orchestrator)
- **Kady**: 主 AI 协调器，负责接收用户请求并委托给合适的专家
- 使用 `delegate_task` 进行任务分发

### 2. 专家层 (Experts)
- 专门的 AI 专家处理特定领域任务
- 支持 170+ 科学技能
- 预置 326 个工作流

### 3. 工具层 (Tools)
- MCP (Model Context Protocol) 集成
- 文件管理工具
- 网络搜索能力
- 文档转换工具

## 文件转换支持

| 源格式 | 目标格式 | 状态 |
|--------|----------|------|
| PDF | Markdown | ✓ |
| PPTX | Markdown | ✓ |
| DOCX | Markdown | ✓ |
| XLSX | CSV/JSON | ✓ |

## API 配置

### 支持的提供商
- OpenAI
- Anthropic (Claude)
- Google Gemini
- Azure OpenAI
- 自定义端点

### 环境变量
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
MODAL_TOKEN_ID=...
MODAL_TOKEN_SECRET=...
```

## 工作流示例

### 1. 文件分析流程
```
用户上传文件 → Kady 识别文件类型 → 选择合适专家 → 执行分析 → 返回结果
```

### 2. 科学计算流程
```
用户描述需求 → 匹配科学技能 → 准备环境 → 执行计算 → 生成报告
```

### 3. 并行任务流程
```
复杂任务 → 分解为子任务 → 并行执行 → 结果汇总 → 最终输出
```

## 安全特性

- 文件路径限制在沙箱目录
- 防止路径遍历攻击
- API 密钥本地存储
- 不上传敏感数据

## 扩展开发

### 添加自定义 MCP 服务器
1. 在设置中添加 MCP 配置
2. 定义工具和资源
3. 重新加载配置

### 创建自定义工作流
1. 定义工作流 YAML
2. 注册到工作流库
3. 通过 Kady 调用
