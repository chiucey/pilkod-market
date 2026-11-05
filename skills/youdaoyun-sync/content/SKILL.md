---
name: youdaoyun-sync
description: 同步有道云笔记文件。当用户想要同步、下载、备份有道云笔记中的文件树和具体文件，或需要将分享链接转换为本地文件时使用。
---

# 有道云笔记同步工具

本技能帮助用户从有道云笔记同步文件，包括通过 token 或分享链接获取文件并保存到本地资产文件夹。

## 工作流程

### 步骤 1：收集认证信息

向用户收集以下信息之一：
- **Token 方式**：有道云访问令牌（有效期较长）
- **分享链接方式**：有道云笔记分享链接

使用确认表单收集信息：

```xml
<genui-form-wizard title="有道云笔记同步" action-id="youdaoyun_auth">
<genui-form-page title="选择认证方式">
<genui-radio-group name="authType">
<genui-radio value="token">我已经有所道云Token</genui-radio>
<genui-radio value="shareLink">使用分享链接</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="tokenOrLink" placeholder="请输入Token或分享链接..."></genui-input>
</genui-form-page>
</genui-form-wizard>
```

### 步骤 2：解析认证信息

**如果是 Token**：
- 直接使用 token 进行 API 调用获取文件列表

**如果是分享链接**：
- 解析分享链接获取分享 ID
- 调用有道云分享 API 获取文件信息
- 获取下载 token（如需要）

### 步骤 3：获取文件树结构

调用同步脚本获取完整的文件目录结构：

```bash
python /workspace/temp-skills/youdaoyun-sync/scripts/sync_files.py --action=list --source={source_type} --auth={auth_info}
```

返回的文件树结构示例：
```
📁 我的笔记/
├── 📄 工作文档.docx
├── 📁 项目/
│   ├── 📄 需求文档.md
│   └── 📄 技术方案.md
└── 📄 日程安排.xlsx
```

### 步骤 4：用户确认同步范围

向用户展示文件树并确认同步选项：

```xml
<genui-form-wizard title="选择同步范围" action-id="sync_scope">
<genui-form-page title="选择同步模式">
<genui-radio-group name="syncMode">
<genui-radio value="full">完整同步（所有文件）</genui-radio>
<genui-radio value="selective">选择性同步</genui-radio>
<genui-radio value="incremental">增量同步（仅新增/修改）</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="customPath" placeholder="指定同步目录（可选）..."></genui-input>
</genui-form-page>
</genui-form-wizard>
```

### 步骤 5：执行同步

根据用户选择执行同步：

**完整同步**：
```bash
python /workspace/temp-skills/youdaoyun-sync/scripts/sync_files.py \
  --action=sync \
  --source={source_type} \
  --auth={auth_info} \
  --mode=full \
  --output=/workspace/assets/youdaoyun
```

**选择性同步**：
```bash
python /workspace/temp-skills/youdaoyun-sync/scripts/sync_files.py \
  --action=sync \
  --source={source_type} \
  --auth={auth_info} \
  --mode=selective \
  --paths={selected_paths} \
  --output=/workspace/assets/youdaoyun
```

**增量同步**：
```bash
python /workspace/temp-skills/youdaoyun-sync/scripts/sync_files.py \
  --action=sync \
  --source={source_type} \
  --auth={auth_info} \
  --mode=incremental \
  --output=/workspace/assets/youdaoyun
```

### 步骤 6：记录同步状态

同步完成后，生成同步报告：

```json
{
  "sync_time": "2024-01-15T10:30:00Z",
  "total_files": 25,
  "downloaded": 23,
  "skipped": 2,
  "failed": 0,
  "total_size": "125MB",
  "changes": {
    "added": 5,
    "modified": 3,
    "deleted": 1
  }
}
```

### 步骤 7：通知用户完成

向用户展示同步结果摘要：

```
✅ 同步完成！

📊 同步统计：
- 总文件数：25
- 已下载：23
- 跳过：2
- 失败：0
- 总大小：125MB

📁 文件位置：/workspace/assets/youdaoyun
```

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| Token 过期 | 提示用户重新获取 token |
| 分享链接失效 | 提示链接已失效，需重新分享 |
| 网络错误 | 重试 3 次后提示用户检查网络 |
| 文件下载失败 | 记录失败文件，继续下载其他文件 |
| 存储空间不足 | 提示用户清理空间或选择性同步 |

## 同步脚本接口

### 主脚本：`sync_files.py`

```python
# 参数说明
--action: list|sync|check      # 列出文件|同步文件|检查更新
--source: token|share           # 认证来源
--auth: string                  # Token 或分享链接
--mode: full|selective|incremental  # 同步模式
--paths: string                 # 选择性同步的路径（逗号分隔）
--output: string                # 输出目录
--exclude: string               # 排除的文件模式（如 "*.tmp,*.log"）
--log-file: string              # 日志文件路径
```

### 返回码

- `0`: 同步成功
- `1`: 参数错误
- `2`: 认证失败
- `3`: 网络错误
- `4`: 存储错误
- `5`: 部分失败（部分文件同步失败）

## 技术实现说明

### 有道云 API 端点

1. **获取文件列表**：
   - Token 方式：`https://note.youdao.com/yws/api/v1/files`
   - 需要 Authorization header

2. **分享链接解析**：
   - 分享页面：`https://note.youdao.com/share/?id={share_id}`
   - 解析 API：`https://note.youdao.com/yws/api/v1/share/{share_id}`

3. **文件下载**：
   - 下载 API：`https://note.youdao.com/yws/api/v1/file/{file_id}`

### 文件标识

使用 MD5 哈希或文件 ID 进行增量同步判断：
- 本地记录每个文件的 hash 和修改时间
- 与远程比较，只下载有变化的文件
- 删除操作需要用户确认
