# load_session

加载当前测试会话信息，获取 design_uid、workspace_id、TAPD配置等参数。

## 使用方式

```bash
python3 <skills_dir>/scripts/load_session.py
```

**注意**：执行脚本前**不要切换目录（不要 cd）**，确保在工作区根目录执行。

## 加载内容

### 1. 会话基本信息
- design_uid: 设计会话唯一标识
- namespace: 命名空间
- select_node: 当前选中的节点信息
- story_node: 需求节点信息

### 2. TAPD配置信息（从 .testbuddy/env/session.json 加载）

如果 `.testbuddy/env/session.json` 文件中包含 `tapd` 配置，则会加载以下信息：
- base_url: TAPD服务器地址
- cookie: TAPD认证Cookie
- workspace_id: TAPD工作空间ID

## 配置文件格式

`.testbuddy/env/session.json` 文件格式：

```json
{
  "token": "用户token",
  "knowledge_uids": ["知识库UID"],
  "tapd": {
    "base_url": "https://www.tapd.cn",
    "cookie": "your_cookie_string",
    "workspace_id": "12345678"
  }
}
```

## 注意事项

- <skills_dir>是脚本所在路径的前缀
- **脚本依赖当前工作目录，执行前不要 cd 切换目录**
- **TAPD配置是可选的**，如果不需要从TAPD获取需求，可以不配置

## 输出示例

```json
{
  "design_uid": "design-Az7SsiL3Ui",
  "namespace": "...",
  "select_node": {
    "uid": "test_point-X0krRg3bP2",
    "kind": "TEST_POINT",
    "name": "搜索结果展示"
  },
  "story_node": {
    "instance": {
      "WorkspaceUid": "69995517"
    }
  },
  "tapd": {
    "base_url": "https://www.tapd.cn",
    "cookie": "your_cookie_string",
    "workspace_id": "12345678"
  }
}
```
