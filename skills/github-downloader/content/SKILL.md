---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 30cbd414f2ce5b805b110be02bc917ff
    PropagateID: 30cbd414f2ce5b805b110be02bc917ff
    ReservedCode1: 304402205aad96ecf32a70b25eba16a16527098a249834e057b7e6333ee9862a74821e3602204beafe003d3dcabd4a479b878a27aa1ff0223b08c63aa854f26e58bd94e258a5
    ReservedCode2: 304502206f87cd41774689446fd46dbbffcaedf2743a7aae9974fb0a9c0a7481ae6817a4022100efe4b132adf0f6511af99f0cc5ba36493163b9512ac394dea4f08923e4ef7548
description: GitHub 源码下载技能。当用户要求下载 GitHub 项目源码、压缩包或仓库文件时使用，例如："帮我下载 https://github.com/xxx/yyy 源码"、"下载这个 GitHub 项目"、"获取项目压缩包"。跳过科学上网问题，云端下载源码包到临时目录，返回文件供用户下载。
name: github-downloader
---

# GitHub 源码下载技能

## 核心能力

快速帮用户下载 GitHub 任意仓库的源码压缩包，无需科学上网。云端下载源码包后返回文件给用户下载。

## 工作流程

### 1. 解析 GitHub URL

识别并提取以下格式的 URL 信息：
- `https://github.com/{owner}/{repo}`
- `https://github.com/{owner}/{repo}/tree/{branch}`
- `https://github.com/{owner}/{repo}/releases`
- `git@github.com:{owner}/{repo}.git`

**提取参数：**
- `owner`: 仓库所有者
- `repo`: 仓库名称
- `branch`: 分支名称（可选，默认为 main 或 master）

### 2. 获取仓库信息

通过 GitHub API 获取仓库基本信息：
```
https://api.github.com/repos/{owner}/{repo}
```
返回：default_branch, description, stargazers_count

### 3. 云端下载源码包

**优先方案（GitHub API）—— 稳定快速：**
```bash
curl -L -o /workspace/downloads/{repo}-{branch}.zip \
  https://api.github.com/repos/{owner}/{repo}/zipball/{branch}
```

**备选方案（直接下载）：**
```bash
curl -L -o /workspace/downloads/{repo}-{branch}.zip \
  https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip
```

### 4. 确保下载目录存在

```bash
mkdir -p /workspace/downloads
```

### 5. 返回结果给用户

向用户返回：
1. 项目基本信息（名称、描述、star 数）
2. 下载状态确认
3. 使用 deliver_assets 格式返回文件

## 响应格式

**项目信息**
- 仓库：{owner}/{repo}
- 分支：{branch}
- 描述：{description}

**下载状态**
✅ 源码包已下载完成（文件大小：{size}）

**Summary**: {repo}-source-code.zip
**Description**: {owner}/{repo} 源码压缩包，分支：{branch}

<deliver_assets>
<item><path>downloads/{repo}-{branch}.zip</path></item>
</deliver_assets>

## 特殊处理

### 分支识别
- 优先使用 URL 中指定的分支
- 如未指定，通过 API 获取默认分支：`https://api.github.com/repos/{owner}/{repo}`
- 常见默认值：main, master

### 子目录下载
如用户要求下载特定子目录或文件：
- 说明 GitHub 不支持直接下载子目录
- 建议用户克隆整个仓库后提取所需内容
- 提供完整的仓库下载

### releases 下载
如用户要求下载 release 资产：
- 获取最新 release 信息
- 下载 release 资产文件
- 返回对应的下载文件

## 错误处理

| 情况 | 处理方式 |
|------|----------|
| URL 格式无效 | 提示用户正确的 GitHub URL 格式 |
| 仓库不存在 | 提示检查 URL 是否正确 |
| 直接下载超时 | 自动切换到 API 下载方案 |
| API 下载失败 | 尝试备选下载方案 |
| 私有仓库 | 说明需要认证，不支持公开下载 |
| 网络超时 | 增加超时时间重试 |

## 示例

**用户输入：**
```
帮我下载 https://github.com/Nahiyi/simple-webserver 源码
```

**技能执行步骤：**
1. 解析 URL：owner=Nahiyi, repo=simple-webserver
2. 获取仓库信息（通过 API）
3. 确定分支：main
4. 云端下载：
   ```bash
   curl -L -o /workspace/downloads/simple-webserver-main.zip \
     https://api.github.com/repos/Nahiyi/simple-webserver/zipball/main
   ```
5. 验证文件完整性
6. 返回文件给用户

**技能响应：**
```
**项目信息**
- 仓库：Nahiyi/simple-webserver
- 分支：main
- 描述：简单Web服务器

**下载状态**
✅ 源码包已下载完成（文件大小：80 KB）

**Summary**: simple-webserver-source-code.zip
**Description**: Nahiyi/simple-webserver 源码压缩包，分支：main

<deliver_assets>
<item><path>downloads/simple-webserver-main.zip</path></item>
</deliver_assets>
```

## 技术要点

1. **跳过科学上网**：使用云端 curl + GitHub API 直接访问
2. **-L 参数**：跟随重定向，确保下载完整
3. **优先 API**：GitHub API 方式更稳定快速
4. **临时目录**：使用 `/workspace/downloads/` 作为下载目录
5. **文件名格式**：`{repo}-{branch}.zip` 便于识别
6. **验证文件**：检查下载文件大小和格式有效性
