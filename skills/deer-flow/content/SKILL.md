---
name: deer-flow
description: Use DeerFlow for deep research and complex task automation. Activate when users request deep research, report generation, slide creation, web development, image/video generation, data pipeline construction, dashboard creation, content workflow automation, or need multi-step complex tasks using AI agent sub-agents, memory systems, and sandbox execution.
---

# DeerFlow - 深度探索与高效研究流

## 概述

DeerFlow 是一个开源的 **超级 Agent 框架**，通过编排 **子代理（Sub-Agents）**、**记忆（Memory）** 和 **沙箱（Sandbox）** 来完成几乎任何任务——由**可扩展技能（Skills）**驱动。它能够处理从几分钟到几小时不等的多步骤复杂任务。

DeerFlow 2.0 是基于 LangGraph 和 LangChain 从头重写的，具有文件系统、记忆、技能、沙箱执行以及规划和生成子代理来完成复杂多步骤任务的能力。

## 核心功能

### 技能系统（Skills）

技能是结构化的能力模块——Markdown 文件，定义工作流程、最佳实践和支持资源引用。DeerFlow 内置以下技能：

| 技能名称 | 功能描述 |
|---------|---------|
| research | 深度研究能力 |
| report-generation | 报告生成 |
| slide-creation | 幻灯片创建 |
| web-page | 网页开发 |
| image-generation | 图像生成 |
| video-generation | 视频生成 |

**渐进式加载**：技能仅在需要时加载，保持上下文窗口精简。

### 子代理系统（Sub-Agents）

- 主代理可以动态生成子代理
- 每个子代理拥有独立的上下文、工具和终止条件
- 子代理并行运行，报告结构化结果
- 主代理综合所有结果形成连贯输出

### 沙箱与文件系统

每个任务在隔离的 Docker 容器中运行，具备完整文件系统：

```
/mnt/user-data/
├── uploads/    ← 用户上传文件
├── workspace/  ← Agent 工作目录
└── outputs/    ← 最终交付物

/mnt/skills/public     ← 内置技能
├── research/
├── report-generation/
├── slide-creation/
├── web-page/
└── image-generation/

/mnt/skills/custom     ← 自定义技能
└── your-custom-skill/
```

### 上下文工程

- **隔离的子代理上下文**：每个子代理在独立隔离的上下文中运行
- **摘要管理**：积极管理上下文——总结已完成的子任务，将中间结果卸载到文件系统

### 长期记忆

跨会话持久化记忆，构建用户偏好、写作风格、技术栈和常见工作流程的档案。

## 使用场景

| 场景 | 适用技能 |
|-----|---------|
| 深度研究和探索 | research |
| 报告和文档生成 | report-generation |
| 幻灯片制作 | slide-creation |
| 网页开发 | web-page |
| 图像和视频生成 | image-generation, video-generation |
| 数据管道构建 | 自定义技能 |
| 仪表板创建 | web-page + 自定义技能 |
| 内容工作流自动化 | 多技能组合 |

## 安装配置

### 步骤 1：克隆仓库

```bash
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow
```

### 步骤 2：生成本地配置文件

```bash
make config
```

这会基于示例模板创建本地配置文件。

### 步骤 3：配置模型

编辑 `config.yaml`，定义至少一个模型：

```yaml
models:
  - name: gpt-4
    display_name: GPT-4
    use: langchain_openai:ChatOpenAI
    model: gpt-4
    api_key: $OPENAI_API_KEY
    max_tokens: 4096
    temperature: 0.7
```

### 步骤 4：设置 API 密钥

**方式 A（推荐）**：编辑 `.env` 文件

```env
TAVILY_API_KEY=your-tavily-api-key
OPENAI_API_KEY=your-openai-api-key
```

**方式 B**：导出环境变量

```bash
export OPENAI_API_KEY=your-openai-api-key
```

## 启动方式

### Docker 启动（推荐）

```bash
make docker-init  # 仅首次或镜像更新时运行
make docker-start # 启动服务
```

访问地址：http://localhost:2026

### 本地开发

```bash
make check              # 验证 Node.js 22+, pnpm, uv, nginx
make setup-sandbox     # 可选：预拉取沙箱镜像
make dev               # 启动服务
```

访问地址：http://localhost:2026

## 沙箱模式

| 模式 | 说明 |
|-----|-----|
| Local Execution | 在主机上直接运行沙箱代码 |
| Docker Execution | 在隔离的 Docker 容器中运行 |
| Kubernetes | 通过 provisioner 服务在 K8s Pod 中运行 |

在 `config.yaml` 的 `sandbox.use` 下配置。

## 模型推荐

DeerFlow 最佳运行于支持以下特性的模型：

- 长上下文窗口（100k+ tokens）
- 推理能力
- 多模态输入
- 可靠的工具调用（function calling）

## 配置文件参数说明

### 模型配置参数

| 参数 | 描述 |
|-----|------|
| name | 内部标识符 |
| display_name | 人类可读名称 |
| use | LangChain 类路径 |
| model | API 模型标识符 |
| api_key | API 密钥（支持环境变量） |
| max_tokens | 每请求最大 token 数 |
| temperature | 采样温度 |

## 官方资源

- **官网**: https://deerflow.tech/
- **GitHub**: https://github.com/bytedance/deer-flow
- **许可证**: MIT License

## 技术统计

- **Star**: 20.6k+
- **Fork**: 2.6k+
- **贡献者**: 105+
- **提交**: 1,523+

## 技术栈

- TypeScript: 40.7%
- Python: 34.8%
- HTML: 10.7%
- CSS: 6.3%
- JavaScript: 5.4%
- Shell: 1.3%
