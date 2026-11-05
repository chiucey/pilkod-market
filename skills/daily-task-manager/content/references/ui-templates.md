# 网页清单模板

## 完整 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>每日任务清单 - {date}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f7fa;
      min-height: 100vh;
      padding: 20px;
    }

    .container {
      max-width: 600px;
      margin: 0 auto;
    }

    .header {
      background: white;
      padding: 20px;
      border-radius: 12px;
      margin-bottom: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .header h1 {
      font-size: 20px;
      color: #1a1a2e;
      margin-bottom: 8px;
    }

    .header .stats {
      display: flex;
      gap: 20px;
      font-size: 14px;
      color: #666;
    }

    .header .stats span {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .priority-section {
      background: white;
      border-radius: 12px;
      margin-bottom: 16px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .priority-section h3 {
      padding: 12px 16px;
      font-size: 14px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .priority-a h3 { background: #fef2f2; color: #dc2626; }
    .priority-b h3 { background: #eff6ff; color: #2563eb; }
    .priority-c h3 { background: #f3f4f6; color: #6b7280; }
    .priority-d h3 { background: #f9fafb; color: #9ca3af; }

    .task-list {
      list-style: none;
    }

    .task-item {
      display: flex;
      align-items: center;
      padding: 14px 16px;
      border-bottom: 1px solid #f3f4f6;
      transition: background 0.2s;
    }

    .task-item:last-child {
      border-bottom: none;
    }

    .task-item:hover {
      background: #f9fafb;
    }

    .task-item input[type="checkbox"] {
      width: 20px;
      height: 20px;
      margin-right: 12px;
      cursor: pointer;
      accent-color: #2563eb;
    }

    .task-item label {
      flex: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
    }

    .task-item .task-content {
      color: #1a1a2e;
      font-size: 15px;
    }

    .task-item.completed .task-content {
      text-decoration: line-through;
      color: #9ca3af;
    }

    .task-item .task-time {
      font-size: 13px;
      color: #666;
      background: #f3f4f6;
      padding: 4px 8px;
      border-radius: 4px;
    }

    .task-item .task-time.hard {
      background: #fee2e2;
      color: #dc2626;
    }

    .task-actions {
      display: flex;
      gap: 8px;
      margin-left: 8px;
    }

    .task-actions button {
      width: 28px;
      height: 28px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .task-actions .priority-btn {
      background: #f3f4f6;
      color: #666;
    }

    .task-actions .delete-btn {
      background: #fee2e2;
      color: #dc2626;
    }

    .empty-section {
      padding: 20px 16px;
      text-align: center;
      color: #9ca3af;
      font-size: 14px;
    }

    .add-task-form {
      background: white;
      padding: 16px;
      border-radius: 12px;
      margin-top: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .add-task-form input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      font-size: 15px;
      margin-bottom: 12px;
    }

    .add-task-form input:focus {
      outline: none;
      border-color: #2563eb;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    .add-task-form button {
      width: 100%;
      padding: 12px;
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
    }

    .add-task-form button:hover {
      background: #1d4ed8;
    }

    .sync-indicator {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: white;
      padding: 8px 12px;
      border-radius: 20px;
      font-size: 12px;
      color: #666;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .sync-indicator.synced { color: #10b981; }
    .sync-indicator.syncing { color: #f59e0b; }
    .sync-indicator.error { color: #ef4444; }

    .sync-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .syncing .sync-dot {
      animation: pulse 1s infinite;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📋 每日任务清单</h1>
      <p style="color: #666; font-size: 14px; margin-bottom: 12px;">{date}</p>
      <div class="stats">
        <span>总任务: <strong>{total}</strong></span>
        <span>已完成: <strong>{completed}</strong></span>
        <span>完成率: <strong>{rate}%</strong></span>
      </div>
    </div>

    <!-- A级任务 -->
    <div class="priority-section priority-a">
      <h3>🔴 A级任务 - 必须完成</h3>
      <ul class="task-list" id="tasks-a">
        <!-- 任务项将动态插入 -->
      </ul>
      <div class="empty-section" id="empty-a" style="display: none;">
        暂无A级任务
      </div>
    </div>

    <!-- B级任务 -->
    <div class="priority-section priority-b">
      <h3>🔵 B级任务 - 最好完成</h3>
      <ul class="task-list" id="tasks-b"></ul>
      <div class="empty-section" id="empty-b" style="display: none;">
        暂无B级任务
      </div>
    </div>

    <!-- C级任务 -->
    <div class="priority-section priority-c">
      <h3>⚪ C级任务 - 可延迟</h3>
      <ul class="task-list" id="tasks-c"></ul>
      <div class="empty-section" id="empty-c" style="display: none;">
        暂无C级任务
      </div>
    </div>

    <!-- D级任务 -->
    <div class="priority-section priority-d">
      <h3>🔘 D级任务 - 未来优化</h3>
      <ul class="task-list" id="tasks-d"></ul>
      <div class="empty-section" id="empty-d" style="display: none;">
        暂无D级任务
      </div>
    </div>

    <!-- 添加任务表单 -->
    <div class="add-task-form">
      <input type="text" id="new-task-input" placeholder="添加新任务... (例如: 下午3点开会 优先级B级)">
      <button onclick="addTask()">添加任务</button>
    </div>
  </div>

  <div class="sync-indicator synced" id="sync-indicator">
    <span class="sync-dot"></span>
    <span id="sync-text">已同步</span>
  </div>

  <script>
    // 任务数据
    let tasks = { a: [], b: [], c: [], d: [] };

    // 渲染任务列表
    function renderTasks() {
      ['a', 'b', 'c', 'd'].forEach(priority => {
        const list = document.getElementById(`tasks-${priority}`);
        const empty = document.getElementById(`empty-${priority}`);

        if (tasks[priority].length === 0) {
          list.innerHTML = '';
          empty.style.display = 'block';
        } else {
          empty.style.display = 'none';
          list.innerHTML = tasks[priority].map((task, index) => `
            <li class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
              <input type="checkbox" ${task.completed ? 'checked' : ''}
                onchange="toggleTask('${task.id}')">
              <label>
                <span class="task-content">${task.content}</span>
                ${task.scheduledTime ? `
                  <span class="task-time ${task.isHardTime ? 'hard' : ''}">${task.scheduledTime}</span>
                ` : ''}
              </label>
              <div class="task-actions">
                <button class="priority-btn" onclick="changePriority('${task.id}')" title="调整优先级">⚡</button>
                <button class="delete-btn" onclick="deleteTask('${task.id}')" title="删除">✕</button>
              </div>
            </li>
          `).join('');
        }
      });
    }

    // 添加任务
    function addTask() {
      const input = document.getElementById('new-task-input');
      const content = input.value.trim();
      if (!content) return;

      // TODO: 调用后端 API 添加任务
      console.log('Adding task:', content);

      input.value = '';
    }

    // 切换任务完成状态
    function toggleTask(taskId) {
      // TODO: 调用后端 API 更新状态
      console.log('Toggle task:', taskId);
    }

    // 调整优先级
    function changePriority(taskId) {
      const newPriority = prompt('请输入新优先级 (A/B/C/D):');
      if (!['A', 'B', 'C', 'D'].includes(newPriority)) return;

      // TODO: 调用后端 API 更新优先级
      console.log('Change priority:', taskId, newPriority);
    }

    // 删除任务
    function deleteTask(taskId) {
      if (!confirm('确定要删除这个任务吗?')) return;

      // TODO: 调用后端 API 删除任务
      console.log('Delete task:', taskId);
    }

    // 同步状态指示器
    function updateSyncStatus(status) {
      const indicator = document.getElementById('sync-indicator');
      const text = document.getElementById('sync-text');

      indicator.className = `sync-indicator ${status}`;
      text.textContent = {
        synced: '已同步',
        syncing: '同步中...',
        error: '同步失败'
      }[status];
    }

    // 初始化
    renderTasks();
  </script>
</body>
</html>
```

## 响应式设计注意事项

1. **移动端适配** - 任务项在移动端应占满宽度
2. **触摸优化** - 按钮最小尺寸 44x44px
3. **语音输入** - 使用 Web Speech API 支持语音输入
4. **离线支持** - 使用 Service Worker 缓存

## 交互状态

| 状态 | 视觉反馈 |
|------|----------|
| 默认 | 白色背景 |
| 悬停 | 浅灰背景 #f9fafb |
| 已完成 | 文字删除线 + 灰色 |
| 同步中 | 底部指示器闪烁 |
| 同步失败 | 红色提示 + 重试按钮 |
