---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 169cbce4e0b69f368bfdddd59233e4eb
    PropagateID: 169cbce4e0b69f368bfdddd59233e4eb
    ReservedCode1: 3046022100dfe78930b0286d602ad3a17d4308a2208f30e6e3bc55da0db5d8fdc991c81344022100b04fb5302b51758de4af8ef2f6bc31a289b9c8211c2e7936400036377bf3e8cb
    ReservedCode2: 3046022100b878cf9dff9c35a2d44de688b94ef716a5713cb394a23ee319d0f699b3023b16022100fb4ad7ce7c2a415ac911885f4a1423c1ae2f26d26bdc815e6ebf25a227c4e8ec
description: 创建交互式待办事项列表界面。当用户要求显示待办事项、创建任务清单、需要点击完成待办、或需要发送新消息功能时使用。
name: interactive-todolist
---

# 交互式待办事项技能

此技能生成一个功能完整的交互式待办事项 HTML 组件。

## 功能特性

- **待办列表展示**：以卡片或列表形式展示所有待办事项
- **完成操作**：点击"完成"按钮将待办标记为已完成（添加删除线样式）
- **新消息功能**：点击"发送新消息"按钮触发新消息输入界面
- **添加待办**：支持添加新的待办事项
- **删除待办**：支持删除不需要的待办事项
- **数据持久化**：使用 localStorage 保存数据，刷新页面后保留数据

## HTML 组件结构

组件必须包含以下核心元素：

### 容器结构
```html
<div class="todolist-container">
  <!-- 标题区域 -->
  <div class="todolist-header">
    <h2>待办事项</h2>
    <span class="todo-count">剩余: X 项</span>
  </div>

  <!-- 输入区域 -->
  <div class="todolist-input-area">
    <input type="text" class="todo-input" placeholder="添加新待办...">
    <button class="btn-add">添加</button>
  </div>

  <!-- 待办列表 -->
  <ul class="todo-list">
    <!-- 待办项模板 -->
    <li class="todo-item" data-id="1">
      <span class="todo-text">待办内容</span>
      <div class="todo-actions">
        <button class="btn-complete">完成</button>
        <button class="btn-delete">删除</button>
      </div>
    </li>
  </ul>

  <!-- 操作按钮区域 -->
  <div class="todolist-actions">
    <button class="btn-send-message">发送新消息</button>
  </div>
</div>
```

### 交互逻辑

#### 1. 完成待办
- 点击"完成"按钮时：
  - 为待办项添加 `.completed` 类（显示删除线）
  - 按钮文字变为"已取消"（再次点击可恢复）
  - 更新 localStorage 中的数据状态
  - 更新剩余计数

#### 2. 发送新消息
- 点击"发送新消息"按钮时：
  - 触发一个回调函数 `onSendMessage()`
  - 该函数返回预设的新消息内容或打开输入框
  - 示例：`window.parent.postMessage({ type: 'sendMessage', content: '新消息内容' }, '*')`

#### 3. 添加待办
- 在输入框输入内容后点击"添加"或按回车
- 新待办添加到列表顶部
- 自动保存到 localStorage
- 清空输入框

#### 4. 删除待办
- 点击"删除"按钮移除该项
- 从 localStorage 中同步删除
- 更新剩余计数

## 样式要求

### 视觉设计
- 使用现代扁平化设计风格
- 卡片式布局，带圆角和阴影
- 清晰的视觉反馈（hover、active 状态）
- 已完成项显示删除线和灰色文字

### 颜色方案
```css
:root {
  --primary-color: #4f46e5;      /* 主色-靛蓝 */
  --success-color: #10b981;      /* 完成-绿色 */
  --danger-color: #ef4444;       /* 删除-红色 */
  --bg-color: #f9fafb;           /* 背景色 */
  --card-bg: #ffffff;            /* 卡片背景 */
  --text-primary: #1f2937;        /* 主文字 */
  --text-secondary: #6b7280;      /* 次要文字 */
  --border-color: #e5e7eb;       /* 边框色 */
}
```

### 响应式设计
- 移动端：单列布局，按钮堆叠
- 桌面端：适中间距

## JavaScript API

### 全局函数
```javascript
// 初始化待办列表
function initTodoList(containerId)

// 添加新待办
function addTodo(text)

// 切换完成状态
function toggleComplete(todoId)

// 删除待办
function deleteTodo(todoId)

// 获取所有待办
function getAllTodos()

// 发送新消息回调
function onSendMessage(messageContent)
```

### 事件钩子
```javascript
// 可被外部覆盖的回调
window.onTodoComplete = function(todo) { }
window.onTodoUncomplete = function(todo) { }
window.onSendMessageClick = function() { }
```

## 使用示例

### 基本使用
```html
<div id="todolist-app"></div>
<script>
  initTodoList('todolist-app');
</script>
```

### 自定义配置
```javascript
initTodoList('todolist-app', {
  storageKey: 'my-todos',
  onSendMessage: function() {
    // 发送消息逻辑
  }
});
```

## 数据格式

### localStorage 存储格式
```json
{
  "todos": [
    {
      "id": "uuid-string",
      "text": "待办内容",
      "completed": false,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## 验收标准

1. ✅ 页面加载时自动恢复 localStorage 中的待办数据
2. ✅ 点击"完成"按钮，待办项变为已完成状态（删除线）
3. ✅ 再次点击可将已完成项恢复为未完成
4. ✅ 点击"发送新消息"按钮，触发消息发送回调
5. ✅ 可以添加新待办事项
6. ✅ 可以删除待办事项
7. ✅ 数据在刷新后保持持久化
8. ✅ 移动端界面友好
9. ✅ 视觉反馈清晰（hover、active 状态）
