---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5282d543add8072b9878699edc211fb0
    PropagateID: 5282d543add8072b9878699edc211fb0
    ReservedCode1: 3046022100f08c7a6975ef7a4387563429a8120e4ab79cb5ad7d41c4267cc637681acc899f022100ca2aaa4853dc830a1607b57a86755f6eb81398beb2b2f17d2bbdd0e692875d55
    ReservedCode2: 3045022057c25d43ffd6f94e2c7c68fba886004d0c3e8828a823f9eff52bd9ce9b34dc56022100ebeaaf1311141b4d00bf392ec576d5c080e1ab1ae439a9301279ba094f7df3f0
description: CNB 云原生构建平台的 Git 操作技能。使用 git 和 CNB Open API 进行代码克隆、提交、推送、分支管理、Merge Request 管理、流水线触发、流水线结果读取等操作。首次使用需收集用户的 Git 用户名和邮箱信息。
name: cnb-cool-git
---

# CNB Git Skill

在 CNB（cnb.cool）平台上进行 Git 操作和 API 调用。

## 认证配置

**凭证环境变量**：

| 变量名 | 类型 | 说明 |
|--------|------|------|
| CNB_COOL_GIT_TOKEN | **SECRET** | Git 访问令牌，用于 Git 操作时的身份验证 |
| CNB_COOL_API_TOKEN | **SECRET** | API 服务令牌，用于调用 CNB Open API |
| CNB_COOL_GIT_USER_NAME | 普通变量 | Git 用户名称，用于提交代码时标识作者 |
| CNB_COOL_GIT_USER_EMAIL | 普通变量 | Git 用户邮箱，用于提交代码时标识作者 |

> **安全提示**：标注为 **SECRET** 的环境变量为敏感凭证，在日志输出、命令展示等场景中应确保其值不被泄露。

**首次使用**：需要向用户收集 Git 用户名和邮箱，存储后应用于 `git config user.name` 和 `git config user.email`。

```bash
# 克隆仓库（用户名固定为 cnb，密码使用 CNB_COOL_GIT_TOKEN）
git clone https://cnb.cool/your-group/your-repo
# 输入用户名: cnb
# 输入密码: ${CNB_COOL_GIT_TOKEN}

# 配置用户信息
git config user.name "${CNB_COOL_GIT_USER_NAME}"
git config user.email "${CNB_COOL_GIT_USER_EMAIL}"
```

## API 基础调用

API 服务地址：`https://api.cnb.cool`

```bash
# 所有 API 调用都需携带认证头
curl -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
     -H "accept: application/json" \
     "https://api.cnb.cool/..."
```

## Merge Request（MR）操作

**创建 MR**：

```bash
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "feat: 功能描述",
    "source_branch": "feature/branch-name",
    "target_branch": "main",
    "description": "变更内容..."
  }' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls"
```

**列出 MR**：

```bash
# 查看所有 MR
curl "https://api.cnb.cool/repos/{owner}/{repo}/pulls?state=open" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}"

# 查看指定 MR
curl "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}"
```

**添加评论**：

```bash
# 普通评论
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"body": "评论内容"}' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}/comments"
```

**提交评审**：

```bash
# APPROVE - 批准
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"event": "APPROVE", "body": "LGTM"}' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}/reviews"

# REQUEST_CHANGES - 需要改进
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"event": "REQUEST_CHANGES", "body": "请修复..."}' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}/reviews"
```

**合并 MR**：

```bash
curl -X "PUT" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "merge_method": "merge",  # merge | squash | rebase
    "commit_title": "Merge PR #123"
  }' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}/merge"
```

**管理标签和评审人**：

```bash
# 添加标签
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"labels": ["bug", "high-priority"]}' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}/labels"

# 添加评审人
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"reviewers": ["username1", "username2"]}' \
  "https://api.cnb.cool/repos/{owner}/{repo}/pulls/{number}/reviewers"
```

## Pipeline 构建结果

**获取构建历史**：

```bash
curl "https://api.cnb.cool/repos/{owner}/{repo}/builds?page=1&page_size=20" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}"
```

**获取构建详情和日志**：

```bash
# 构建详情
curl "https://api.cnb.cool/repos/{owner}/{repo}/builds/{build_id}" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}"

# 构建日志
curl "https://api.cnb.cool/repos/{owner}/{repo}/builds/{build_id}/logs" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}"
```

## Pipeline 触发

**手动触发 Pipeline**：

```bash
# 通过 API 触发流水线
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "event": "api_trigger",
    "env": {
      "KEY": "value"
    }
  }' \
  "https://api.cnb.cool/repos/{owner}/{repo}/trigger"
```

**获取触发器列表**：

```bash
# 列出仓库的触发器
curl "https://api.cnb.cool/repos/{owner}/{repo}/triggers" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}"
```

**重新触发构建**：

```bash
# 重新触发指定构建
curl -X "POST" \
  -H "Authorization: Bearer ${CNB_COOL_API_TOKEN}" \
  "https://api.cnb.cool/repos/{owner}/{repo}/builds/{build_id}/retry"
```

## 关键环境变量

| 变量名 | 说明 |
|--------|------|
| CNB_REPO_SLUG | 仓库路径（group/repo） |
| CNB_BRANCH | 分支名 |
| CNB_COMMIT | 提交 SHA |
| CNB_BUILD_ID | 构建流水号 |
| CNB_BUILD_STATUS | 构建状态（success/error/cancel） |
| CNB_PIPELINE_STATUS | Pipeline 状态 |
| CNB_BUILD_WEB_URL | 构建日志地址 |
| CNB_PULL_REQUEST | 是否为 PR 触发 |
| CNB_TOKEN | 流水线临时令牌（系统注入） |

## 最佳实践

- 不要在代码中硬编码访问令牌
- 使用环境变量或密钥仓库存储敏感信息
- 定期轮换令牌
- 不可信事件（PR评论、Issue评论）的流水线权限受限，敏感操作应在可信事件中执行
