# 大屏 + AI 问答 双 Tab 模式(2026-08)

> **来源**:AI-GIS 智能问图平台 v0.4.0 实战
> **场景**:Dashboard 数据大屏 + AI 智能问答 复合应用
> **核心价值**:1 个入口满足"看数 + 问数"两件事

---

## 一、为什么需要双 Tab

**传统做法**:
- Dashboard:只看数据,不会提问
- AI 聊天:只回答文字,不动数据
- **割裂**:用户想问"为什么浙江省损耗这么高"得切换 2 个系统

**双 Tab 模式**:
- Tab 1 (Dashboard):8 大图表 + 地图 + 联动 + 跑马灯(沿用 v1 cream 风格)
- Tab 2 (AI 智能问答):聊天界面 + 流式输出 + 自动触发地图/图表
- **联动**:AI 回答"浙江省损耗高的 3 个原因",**自动在地图上标出** + 表格对应行高亮
- **记忆**:Tab 1 的高亮状态保留,切回仍可见

---

## 二、布局

```
+----------------------------------------------------------+
|  [Logo]  AI-GIS 智能问图平台    [Tab 1: Dashboard] [Tab 2: AI 问图]   14:32:08  2026-08-29 | 周五  |
+----------------------------------------------------------+
|  主内容区(Tab 1 或 Tab 2)                                |
|                                                          |
|  ┌─ Tab 1: Dashboard ─────────────────────────────────┐  |
|  │  [TOP10]  [折线]      [中国地图满屏]  [总计]  [环形]│  |
|  │  [表格]              [4 高优+跑马灯]   [柱状]      │  |
|  └────────────────────────────────────────────────────┘  |
|                                                          |
|  ┌─ Tab 2: AI 智能问答 ──────────────────────────────┐   |
|  │ ┌──────────┐ ┌──────────────────────────────┐    │   |
|  │ │  历史     │ │  对话窗口                     │    │   |
|  │ │  对话     │ │  - 用户消息                    │    │   |
|  │ │           │ │  - AI 流式回答                 │    │   |
|  │ │  [新对话] │ │  - 工具调用日志                │    │   |
|  │ │  [清空]   │ │  - 关联地图(右侧缩略图)        │    │   |
|  │ └──────────┘ └──────────────────────────────┘    │   |
|  │ [输入框: 问点什么...]                          [发送]   |
|  └────────────────────────────────────────────────────┘  |
|                                                          |
|              [Tab 1 底部蓝线 | Tab 2 底部蓝线]              |
+----------------------------------------------------------+
```

**Tab 1 激活态**:
- 底部 3px 蓝线 `box-shadow: inset 0 -4px 0 0 rgba(96, 165, 250, 0.85)` (上提 4px)
- 文字 `#1e3a6e` + 700 字重

**Tab 2 激活态**:同 Tab 1

---

## 三、HTML 结构

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>AI-GIS 智能问图平台</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/chat.css">
    <script src="assets/echarts.min.js"></script>
</head>
<body class="dashboard-active">  <!-- 默认 Tab 1 -->

    <!-- 顶部导航 -->
    <header class="topbar">
        <div class="brand">
            <span class="logo">🗺️</span>
            <span class="title">AI-GIS 智能问图平台</span>
        </div>
        <nav class="tabs">
            <button class="tab-item active" data-tab="dashboard">
                <span class="tab-icon">📊</span>
                <span class="tab-text">数据大屏</span>
            </button>
            <button class="tab-item" data-tab="ai-chat">
                <span class="tab-icon">🤖</span>
                <span class="tab-text">AI 问图</span>
            </button>
        </nav>
        <div class="time-info">
            <div class="clock" id="clock">--:--:--</div>
            <div class="date" id="date">--</div>
        </div>
    </header>

    <!-- 主内容区 -->
    <main class="content">
        <!-- Tab 1: Dashboard -->
        <section id="tab-dashboard" class="tab-panel active">
            <!-- 8 大图表沿用 v1 布局 -->
            <div class="col col-left">
                <div class="panel" id="top10-panel"></div>
                <div class="panel" id="line-panel"></div>
                <div class="panel" id="table-panel"></div>
            </div>
            <div class="map-bg" id="map-chart"></div>
            <div class="col col-right">
                <div class="panel" id="summary-panel"></div>
                <div class="panel" id="quarter-panel"></div>
                <div class="panel" id="equipment-panel"></div>
            </div>
        </section>

        <!-- Tab 2: AI 智能问答 -->
        <section id="tab-ai-chat" class="tab-panel">
            <aside class="chat-sidebar">
                <button class="btn-new-chat" id="new-chat-btn">+ 新对话</button>
                <div class="chat-history" id="chat-history-list"></div>
            </aside>
            <div class="chat-main">
                <div class="chat-messages" id="chat-messages">
                    <div class="empty-state">
                        <h2>👋 问我点什么</h2>
                        <p>比如:"查浙江省的所有 POI"</p>
                        <p>"天地图矢量瓦片"</p>
                        <p>"我配置的 LLM key 是什么"</p>
                    </div>
                </div>
                <div class="chat-input-area">
                    <textarea id="user-input" placeholder="问点什么... (Shift+Enter 换行)" rows="2"></textarea>
                    <button id="send-btn">发送</button>
                </div>
            </div>
        </section>
    </main>

    <script src="js/dual-tab-controller.js"></script>
    <script src="js/ai-chat-client.js"></script>
    <script src="js/main.js"></script>
</body>
</html>
```

---

## 四、CSS 样式

```css
/* css/style.css */

/* === Tab 切换 === */
.topbar {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    height: 80px;
    padding: 0 20px;
    background: rgba(255, 255, 255, 0.92);
    border-bottom: 1px solid rgba(143, 188, 255, 0.3);
}

.tabs {
    display: flex;
    gap: 4px;
    background: rgba(143, 188, 255, 0.12);
    border-radius: 6px;
    padding: 4px;
}

.tab-item {
    position: relative;
    padding: 10px 20px;
    border: none;
    background: transparent;
    color: #6b8fc4;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
}

.tab-item:hover {
    background: rgba(143, 188, 255, 0.15);
    color: #3a5a8c;
}

.tab-item.active {
    background: rgba(255, 255, 255, 0.95);
    color: #1e3a6e;
    /* 关键: 底部 3px 蓝线, 上提 4px */
    box-shadow: 
        inset 0 -4px 0 0 rgba(96, 165, 250, 0.85),
        0 2px 8px rgba(96, 165, 250, 0.2);
    transform: translateY(-1px);  /* 整体上提一点,更有"激活"感 */
}

/* === Tab 面板 === */
.tab-panel {
    display: none;
    height: calc(100vh - 80px);
    overflow: hidden;
}

.tab-panel.active {
    display: block;
}
```

```css
/* css/chat.css */

/* === AI 问答界面 === */
#tab-ai-chat {
    display: none;
    grid-template-columns: 240px 1fr;
    height: calc(100vh - 80px);
}

#tab-ai-chat.active {
    display: grid;
}

.chat-sidebar {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(6px);
    border-right: 1px solid rgba(143, 188, 255, 0.3);
    padding: 16px;
    overflow-y: auto;
}

.btn-new-chat {
    width: 100%;
    padding: 10px;
    background: #4a7bb8;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    margin-bottom: 12px;
}

.btn-new-chat:hover {
    background: #3a5a8c;
}

.chat-history {
    list-style: none;
    padding: 0;
    margin: 0;
}

.chat-history li {
    padding: 8px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    color: #3a5a8c;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-history li:hover {
    background: rgba(143, 188, 255, 0.15);
}

.chat-main {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: rgba(255, 255, 255, 0.4);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
}

.message {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    max-width: 80%;
}

.message-user {
    margin-left: auto;
    flex-direction: row-reverse;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #4a7bb8;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

.message-user .avatar {
    background: #ff9a3c;
}

.content {
    background: rgba(255, 255, 255, 0.92);
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(143, 188, 255, 0.15);
    color: #1e3a6e;  /* 深色背景注意: 暗色模式要用 slate-200 */
}

.text-content {
    white-space: pre-wrap;
    line-height: 1.6;
}

.tool-log {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed rgba(143, 188, 255, 0.3);
    font-size: 12px;
    color: #6b8fc4;
}

.tool-call, .tool-result {
    padding: 4px 0;
}

.tool-call code, .tool-result code {
    background: rgba(96, 165, 250, 0.18);
    color: #1e3a6e;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 11px;
}

.chat-input-area {
    display: flex;
    gap: 8px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.85);
    border-top: 1px solid rgba(143, 188, 255, 0.3);
}

#user-input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid rgba(143, 188, 255, 0.4);
    border-radius: 6px;
    resize: none;
    font-size: 14px;
    font-family: inherit;
}

#user-input:focus {
    outline: none;
    border-color: #4a7bb8;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.18);
}

#send-btn {
    padding: 0 24px;
    background: #4a7bb8;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}

#send-btn:hover {
    background: #3a5a8c;
}
```

---

## 五、JS 控制器

```js
// js/dual-tab-controller.js

class DualTabController {
    constructor() {
        this.tabs = document.querySelectorAll('.tab-item');
        this.panels = document.querySelectorAll('.tab-panel');
        this.activeTab = 'dashboard';
        this.tabHistory = ['dashboard'];
        
        this._initEvents();
    }
    
    _initEvents() {
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => this.activate(tab.dataset.tab));
        });
        
        // 键盘快捷键: Ctrl+1/2 切 Tab
        document.addEventListener('keydown', e => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === '1') this.activate('dashboard');
                else if (e.key === '2') this.activate('ai-chat');
            }
        });
    }
    
    activate(tabName) {
        if (this.activeTab === tabName) return;
        
        // 1. 更新按钮
        this.tabs.forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tabName);
        });
        
        // 2. 更新面板
        this.panels.forEach(p => {
            p.classList.toggle('active', p.id === `tab-${tabName}`);
        });
        
        // 3. 更新 body class(用于 CSS 状态)
        document.body.classList.remove(`${this.activeTab}-active`);
        document.body.classList.add(`${tabName}-active`);
        
        // 4. 触发自定义事件(让其他模块响应)
        const event = new CustomEvent('tab-changed', { 
            detail: { from: this.activeTab, to: tabName } 
        });
        document.dispatchEvent(event);
        
        // 5. AI 问答 tab: 强制 resize ECharts 地图(从隐藏切到显示)
        if (tabName === 'dashboard' && this._lastTab === 'ai-chat') {
            // 让 ECharts 重新计算尺寸
            window.dispatchEvent(new Event('resize'));
        }
        
        this.tabHistory.push(tabName);
        this._lastTab = this.activeTab;
        this.activeTab = tabName;
    }
}

window.dualTab = new DualTabController();
```

```js
// js/ai-chat-client.js
class AIChatClient {
    constructor() {
        this.history = [];
        this.currentStream = null;
        this._initEvents();
    }
    
    _initEvents() {
        const sendBtn = document.getElementById('send-btn');
        const input = document.getElementById('user-input');
        
        sendBtn.addEventListener('click', () => this._send());
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this._send();
            }
        });
        
        document.getElementById('new-chat-btn').addEventListener('click', () => {
            this.history = [];
            document.getElementById('chat-messages').innerHTML = `
                <div class="empty-state">
                    <h2>👋 问我点什么</h2>
                    <p>比如:"查浙江省的所有 POI"</p>
                </div>
            `;
        });
    }
    
    async _send() {
        const input = document.getElementById('user-input');
        const msg = input.value.trim();
        if (!msg) return;
        input.value = '';
        
        // 1. 隐藏空状态
        const emptyState = document.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        
        // 2. 加用户消息
        this._appendMessage('user', msg);
        this.history.push({ role: 'user', content: msg });
        
        // 3. 准备 AI 消息框
        const assistantMsg = this._appendMessage('assistant', '');
        const textSpan = assistantMsg.querySelector('.text-content');
        const toolLog = assistantMsg.querySelector('.tool-log');
        let textContent = '';
        
        // 4. 取消旧流
        if (this.currentStream) this.currentStream.abort();
        this.currentStream = new AbortController();
        
        // 5. 发请求
        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    history: this.history.slice(0, -1)  // 最后一个是当前 user msg,后端会加
                }),
                signal: this.currentStream.signal
            });
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const events = buffer.split('\n\n');
                buffer = events.pop() || '';
                
                for (const event of events) {
                    let eventName = 'message', data = '';
                    for (const line of event.split('\n')) {
                        if (line.startsWith('event: ')) eventName = line.slice(7).trim();
                        else if (line.startsWith('data: ')) data = line.slice(6).trim();
                    }
                    if (!data) continue;
                    
                    try {
                        const payload = JSON.parse(data);
                        if (eventName === 'text') {
                            textContent += payload.content;
                            textSpan.textContent = textContent;
                        } else if (eventName === 'tool_call') {
                            const div = document.createElement('div');
                            div.className = 'tool-call';
                            div.innerHTML = `🔧 <code>${payload.name}</code> (${JSON.stringify(payload.args)})`;
                            toolLog.appendChild(div);
                        } else if (eventName === 'tool_result') {
                            const div = document.createElement('div');
                            div.className = 'tool-result';
                            div.innerHTML = `✅ <code>${payload.name}</code> → ${JSON.stringify(payload.result).slice(0, 80)}...`;
                            toolLog.appendChild(div);
                            // 🆕 工具结果触发地图更新
                            if (window.aiMap && payload.result?.geojson) {
                                window.aiMap.update(payload.result.geojson);
                            }
                        } else if (eventName === 'done') {
                            this.history.push({ role: 'assistant', content: textContent });
                        } else if (eventName === 'error') {
                            textSpan.textContent = `❌ ${payload.error}`;
                        }
                    } catch (e) {
                        console.warn('解析 SSE 失败:', e);
                    }
                }
            }
        } catch (e) {
            if (e.name !== 'AbortError') {
                textSpan.textContent = `❌ 请求失败: ${e.message}`;
            }
        }
        
        this._scrollToBottom();
    }
    
    _appendMessage(role, content) {
        const div = document.createElement('div');
        div.className = `message message-${role}`;
        div.innerHTML = `
            <div class="avatar">${role === 'user' ? '我' : 'AI'}</div>
            <div class="content">
                <div class="text-content">${this._escapeHtml(content)}</div>
                <div class="tool-log"></div>
            </div>
        `;
        document.getElementById('chat-messages').appendChild(div);
        this._scrollToBottom();
        return div;
    }
    
    _escapeHtml(s) {
        return s.replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
    }
    
    _scrollToBottom() {
        const m = document.getElementById('chat-messages');
        m.scrollTop = m.scrollHeight;
    }
}

// 启动
window.aiChat = new AIChatClient();
```

---

## 六、跨 Tab 联动

**AI 生成的图层 / 高亮,在 Tab 1 也能看到**:

```js
// 工具调用结果:查"浙江省 POI"返回 5 个点
// 切回 Tab 1 时地图自动高亮这 5 个点

// ai-chat-client.js 中:
if (payload.result?.highlight) {
    window.__aiHighlights = payload.result.highlight;  // 暂存
}

// dual-tab-controller.js 中:
activate(tabName) {
    // ...
    if (tabName === 'dashboard' && this._lastTab === 'ai-chat') {
        // 把 AI 高亮应用到地图
        if (window.windMap && window.__aiHighlights) {
            window.__aiHighlights.forEach(h => {
                window.windMap.highlight(h.province);
            });
        }
    }
}
```

---

## 七、避坑 6 条

| # | 踩坑 | 解决 |
|---|---|---|
| 1 | 切回 Tab 1 地图空白 | ECharts resize: `window.dispatchEvent(new Event('resize'))` |
| 2 | Tab 1 激活态线"差一点点" | 加粗到 3px + offset -4px + translateY(-1px) |
| 3 | 对话太长内存爆 | 历史限 50 条,超过截断 |
| 4 | F5 刷新对话全没 | 默认行为(用户接受);持久化用 IndexedDB |
| 5 | SSE 断了用户不知道 | UI 显示"重连中..." + `AbortController` 重试 |
| 6 | 暗色模式文字看不清 | 硬性:深色背景 ≥ slate-200 |

---

## 八、避坑口诀

**Tab 切换 resize ECharts / 高亮跨 Tab 保留 / rAF 节流 / AbortController 取消旧流 / placeholder 模式 / F5 默认清空**
