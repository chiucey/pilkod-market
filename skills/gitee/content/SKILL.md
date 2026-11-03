---
name: gitee
description: 提供Gitee仓库创建与代码提交功能；当用户需要创建Gitee仓库、提交代码到Gitee或管理Gitee项目时使用
dependency:
  python: []
  system: []
---

# Gitee 仓库管理

## 任务目标
- 本 Skill 用于:管理 Gitee 仓库的创建与代码提交
- 能力包含:通过 API 创建 Gitee 仓库、将本地代码提交到 Gitee 仓库
- 触发条件:用户提到需要提交代码到 Gitee、创建 Gitee 仓库或同步代码到 Gitee

## 前置准备
- 凭证配置:首次使用需要提供 Gitee Personal Access Token
  - 访问 https://gitee.com/profile/personal_access_tokens 点击"生成新令牌"
  - 设置令牌描述并勾选"projects"权限
  - 生成后复制令牌填写到凭证配置中
  - 此令牌相当于账号密码，请妥善保管

## 操作步骤
- 标准流程:
  1. **创建仓库**(如果仓库不存在)
     - 调用 `scripts/create_repo.py --name <仓库名> --description <描述> --private <是否私有>`
     - 脚本会自动使用 Personal Access Token 认证并调用 Gitee API 创建仓库
     - 成功后返回仓库的克隆 URL
  2. **提交代码到仓库**
     - 调用 `scripts/commit_code.py --repo-url <仓库URL> --commit-message <提交信息>`
     - 脚本会执行 git 初始化、添加文件、提交并推送
     - 支持首次初始化和后续更新
- 可选分支:
  - 当仓库已存在:跳过创建步骤，直接执行代码提交
  - 当需要提交特定目录:使用 `--local-path` 参数指定本地路径

## 资源索引
- 必要脚本:
  - [scripts/create_repo.py](scripts/create_repo.py)(用途:通过 Gitee API 创建新仓库)
  - [scripts/commit_code.py](scripts/commit_code.py)(用途:执行 git 操作提交代码)

## 注意事项
- 首次使用必须提供 Gitee Personal Access Token，脚本会自动从环境变量读取凭证
- 仓库名称必须符合 Gitee 命名规范(字母、数字、下划线、短横线)
- 代码提交前请确保本地路径下有有效的 git 配置(user.name 和 user.email)
- 如果仓库已存在，create_repo.py 会返回错误信息，可跳过创建步骤

## 使用示例

### 示例 1: 创建新仓库并提交代码
```bash
# 1. 创建名为 my-project 的私有仓库
python scripts/create_repo.py --name my-project --description "我的项目" --private true

# 2. 提交当前目录代码到仓库
python scripts/commit_code.py --repo-url https://gitee.com/用户名/my-project.git --commit-message "初始提交"
```

### 示例 2: 提交到已存在的仓库
```bash
# 直接提交代码到现有仓库
python scripts/commit_code.py --repo-url https://gitee.com/用户名/existing-repo.git --commit-message "更新功能"
```

### 示例 3: 提交指定目录的代码
```bash
# 提交 /path/to/project 目录的代码
python scripts/commit_code.py --local-path /path/to/project --repo-url https://gitee.com/用户名/my-project.git --commit-message "添加项目文件"
```
