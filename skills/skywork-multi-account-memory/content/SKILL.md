---
name: skywork-multi-account-memory
description: SkyWork多账号统一记忆管理系统。帮助用户管理多个SkyWork账号，实现积分联合调度、跨账号持久记忆、上下文连续恢复。长任务开发必备，支持项目追踪、知识积累、任务队列。当用户需要同时使用多个SkyWork账号、进行长周期开发项目、跨账号保持上下文连续时使用。
---

# SkyWork Multi-Account Memory Management System

## 1. 概述

这是一个专为SkyWork多账号用户设计的记忆管理系统，核心解决以下痛点：

- 多账号积分无法统一使用
- 切换账号时上下文丢失
- 长任务开发中记忆断裂
- 无法跨账号复用已积累的知识

**设计理念**：将所有SkyWork账号视为一个"计算资源池"，而共享记忆库作为"知识大脑"，实现资源与知识的解耦和复用。

## 2. 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     SkyWork Multi-Account Manager                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Account 1  │  │  Account 2  │  │  Account N  │              │
│  │ Session     │  │ Session     │  │ Session     │              │
│  │ Management  │  │ Management  │  │ Management  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  TASK QUEUE MANAGER                     │    │
│  │  - Priority Queue    - Auto-Dispatch                  │    │
│  │  - Load Balancing    - Failover Logic                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              SHARED MEMORY KNOWLEDGE BASE              │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │ Projects │ │ Contexts │ │ Knowledge│ │ Patterns │    │    │
│  │  │  Track   │ │ History  │ │  Base   │ │ Library  │    │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 3. 记忆存储结构

### 3.1 项目记忆 (Projects)

每个长期项目创建独立记忆空间：

```yaml
Project: project_id
  metadata:
    name: "项目名称"
    created_at: "2026-01-01"
    last_access: "2026-05-16"
    status: "in_progress"  # planning | in_progress | paused | completed

  context:
    current_phase: "architecture_design"
    last_discussion_summary: |
      讨论了系统架构，决定采用微服务模式
      主要模块：用户服务、订单服务、支付服务
      数据库选用PostgreSQL
    pending_issues:
      - "支付模块API对接方案待确定"
      - "需要评估性能瓶颈"
    decisions:
      - "使用Docker容器化部署"
      - "前端采用Vue3 + TypeScript"

  account_usage:
    account_1: "负责架构设计阶段"
    account_2: "负责核心功能开发"
    account_3: "负责测试和优化"
```

### 3.2 对话上下文 (Contexts)

每个对话轮次的重要输出都提取保存：

```yaml
Context: context_id
  project_id: "project_001"
  timestamp: "2026-05-16T10:30:00Z"

  content_type: "code_generation"  # code | analysis | design | discussion

  summary: "生成了用户认证模块的核心代码"

  key_outputs:
    - type: "file"
      path: "src/auth/login.py"
      description: "用户登录模块，包含JWT验证"
    - type: "decision"
      text: "采用JWT token进行会话管理"
    - type: "pattern"
      text: "发现了一个可复用的分页模式"

  follow_up_required:
    - "需要添加刷新token逻辑"
    - "缺少错误处理分支"

  related_contexts:
    - "context_023"  # 之前的认证设计讨论
    - "context_045"  # JWT最佳实践
```

### 3.3 知识积累 (Knowledge Base)

可复用的知识片段：

```yaml
Knowledge: knowledge_id
  category: "coding_pattern"  # coding_pattern | api_usage | error_solving | best_practice

  title: "Python异步编程模式"

  content: |
    常用的异步模式总结：

    1. async/await 基本用法
    ```python
    async def fetch_data(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
    ```

    2. 并发请求模式
    ```python
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    ```

  tags:
    - "python"
    - "async"
    - "concurrency"

  usage_count: 5
  last_used: "2026-05-15"
```

### 3.4 模式库 (Patterns)

从多次实践中提取的可复用模式：

```yaml
Pattern: pattern_id
  name: "CRUD API模板"
  language: "python"

  template: |
    @app.route('/api/{{resource}}', methods=['GET'])
    def list_{{resource}}():
        items = {{model}}.query.all()
        return jsonify([item.to_dict() for item in items])

    @app.route('/api/{{resource}}/<int:id>', methods=['GET'])
    def get_{{resource}}(id):
        item = {{model}}.query.get_or_404(id)
        return jsonify(item.to_dict())

    # ... create, update, delete methods

  variables:
    - resource
    - model

  times_used: 12
  effectiveness: "high"  # high | medium | low
```

## 4. 工作流程

### 4.1 任务启动流程 (Session Start)

```
用户打开SkyWork新会话
        │
        ▼
┌───────────────────┐
│ 加载项目上下文     │
│ - 最近项目列表     │
│ - 选中项目记忆     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 加载相关知识      │
│ - 项目相关知识    │
│ - 相关模式库      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 构建上下文提示    │
│ - 系统提示词      │
│ - 项目背景       │
│ - 历史决策摘要   │
│ - 相关代码模式   │
└─────────┬─────────┘
          │
          ▼
    开始对话
```

**上下文注入示例**：

```
[系统上下文 - 项目: 用户管理系统]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【项目状态】开发中 - Phase 3/5: 用户认证模块

【最近进展】
- 已完成：用户注册、邮箱验证基础功能
- 进行中：JWT Token刷新机制实现
- 计划中：第三方登录集成(OAuth2)

【历史决策】
✓ 采用JWT进行会话管理
✓ 使用bcrypt进行密码加密
✓ PostgreSQL存储用户数据

【待解决问题】
- Token刷新时机选择
- 异地登录检测机制

【相关代码模式】
// 项目中使用的用户认证模式
// 详见: pattern_auth_flow.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 任务结束流程 (Session End)

```
对话完成或切换账号
        │
        ▼
┌───────────────────┐
│ 分析本次对话      │
│ - 提取关键输出   │
│ - 识别新知识     │
│ - 记录决策       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 更新记忆库        │
│ - 保存上下文     │
│ - 补充知识库     │
│ - 更新项目状态   │
│ - 记录待办       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 准备下次会话     │
│ - 生成摘要       │
│ - 设置下次提示   │
└───────────────────┘
```

### 4.3 多账号任务分配

```
收到任务请求
        │
        ▼
┌───────────────────┐
│ 任务分析          │
│ - 任务类型判断    │
│ - 所需能力评估    │
│ - 预计Token消耗   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 账号选择          │
│ - 检查积分余额   │
│ - 检查历史关联   │
│ - 负载均衡       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 执行任务          │
│ - 加载对应上下文 │
│ - 执行任务       │
│ - 记录结果       │
└───────────────────┘
```

## 5. 账号管理

### 5.1 账号配置

```yaml
accounts:
  - id: account_1
    name: "主开发账号"
    email: "dev1@xxx.com"
    priority: 1  # 优先级，1最高
    quota:
      daily_limit: 100000
      used_today: 35000
      reset_hour: 0  # UTC时间重置时间

  - id: account_2
    name: "辅助开发账号"
    email: "dev2@xxx.com"
    priority: 2
    quota:
      daily_limit: 100000
      used_today: 0
      reset_hour: 0

  # ... 更多账号
```

### 5.2 积分池策略

| 策略 | 适用场景 | 说明 |
|------|---------|------|
| **优先级分配** | 高优先级任务 | 优先使用高优先级账号 |
| **轮询分配** | 普通任务 | 轮流向各账号分配任务 |
| **负载均衡** | 大规模并行 | 选择积分最充裕的账号 |
| **亲和性分配** | 项目连续性 | 同一项目尽量使用同一账号 |

### 5.3 账号健康检查

```yaml
health_check:
  enabled: true
  interval_minutes: 30

  checks:
    - name: "session_valid"
      action: "verify_with_light_request"

    - name: "rate_limit"
      action: "check_if_rate_limited"

    - name: "response_time"
      action: "measure_avg_response_time"
      alert_if_above_ms: 5000

  auto_recovery:
    - detected: "rate_limited"
      action: "switch_to_backup_account"

    - detected: "session_expired"
      action: "prompt_manual_login"
```

## 6. 上下文压缩与优化

### 6.1 对话历史压缩

当对话历史过长时，自动进行压缩：

```yaml
compression_rules:
  max_history_tokens: 8000  # 保留的最后上下文上限

  compression_strategy:
    - priority: 1
      action: "keep_system_prompt"

    - priority: 2
      action: "keep_recent_turns"  # 最近3-5轮完整保留

    - priority: 3
      action: "summarize_old_turns"  # 早期对话生成摘要

    - priority: 4
      action: "prune_redundant"  # 删除重复内容
```

### 6.2 记忆优先级

| 优先级 | 内容类型 | 保留策略 |
|--------|---------|---------|
| P0 | 项目核心上下文 | 永远保留，按项目存储 |
| P1 | 技术决策记录 | 永远保留 |
| P2 | 相关代码模式 | 保留，有限数量 |
| P3 | 中间讨论过程 | 压缩成摘要 |
| P4 | 临时验证代码 | 不保留对话结束后 |

## 7. 使用指南

### 7.1 初始化设置

1. **配置账号**
   ```yaml
   # 在配置文件中添加所有SkyWork账号
   accounts:
     - id: "account_1"
       # ... 账号信息
   ```

2. **创建或加入项目**
   ```bash
   # 创建新项目
   swm project create "我的项目"

   # 加入现有项目
   swm project join "project_id"
   ```

3. **启动管理服务**（可选）
   ```bash
   # 启动后台服务，支持自动上下文恢复
   swm service start
   ```

### 7.2 日常使用

1. **开始新的开发会话**
   ```bash
   # 自动加载上一个项目的上下文
   swm continue

   # 或指定项目
   swm continue --project "用户管理系统"
   ```

2. **跨账号继续工作**
   ```bash
   # 切换到另一个账号，但保持同一项目上下文
   swm switch --to account_2
   ```

3. **查询记忆库**
   ```bash
   # 搜索相关知识
   swm search "JWT token"

   # 查看项目历史
   swm history --project "用户管理系统"
   ```

### 7.3 知识提取

对话过程中，系统会自动：

1. 识别并保存代码文件路径
2. 提取技术决策和选择理由
3. 记录遇到的问题和解决方案
4. 保存可复用的代码片段
5. 标记待完成的任务

## 8. 数据存储

### 8.1 存储位置

```
~/.skywork-memory/
├── config.yaml           # 全局配置
├── accounts.yaml         # 账号配置（加密存储）
├── memory/
│   ├── projects/         # 项目记忆
│   ├── contexts/         # 对话上下文
│   ├── knowledge/        # 知识库
│   └── patterns/         # 模式库
└── logs/
    └── session_*.log     # 会话日志
```

### 8.2 数据安全

- 账号凭据使用本地加密存储
- 支持设置主密码保护
- 可选同步到私有云存储

## 9. 多语言支持

系统支持中文和英文界面：

```yaml
language:
  default: "zh-CN"  # 中文
  supported:
    - "zh-CN"
    - "en-US"
```

## 10. 扩展功能

### 10.1 插件系统

```yaml
plugins:
  - name: "code-indexer"
    description: "自动索引生成的代码"
    enabled: true

  - name: "git-integration"
    description: "自动commit生成的代码"
    enabled: false
```

### 10.2 自动化规则

```yaml
automation:
  on_session_end:
    - action: "extract_code"
    - action: "save_context"
    - action: "update_knowledge"

  on_large_output:
    - action: "compress_and_save"
    - action: "index_for_search"
```

## 11. 故障排除

| 问题 | 解决方案 |
|------|---------|
| 上下文加载失败 | 检查记忆库完整性，尝试重建索引 |
| 账号切换后记忆丢失 | 确认项目ID一致，检查存储权限 |
| 知识搜索结果不准确 | 重新生成知识库索引，增加tags |
| 多账号积分显示不准 | 手动同步积分记录，检查API可用性 |

---

**使用前提**：
- 需要手动登录至少一个SkyWork账号
- 定期维护记忆库清理冗余数据
- 多账号切换需要浏览器配合（SessionBox等工具）

**适用场景**：
- 长期开发项目
- 需要跨会话保持上下文
- 多账号协同工作
- 知识积累与复用