# SSE 实时数据流(2026-08)

> **来源**:AI-GIS v0.4.0 + 风控监控大屏实战
> **场景**:实时监控数据(IoT 传感器 / 告警 / 计数器 / sparkline 滚动)
> **技术栈**:FastAPI StreamingResponse + EventSource(浏览器原生)

---

## 一、为什么用 SSE 不用 WebSocket

| 维度 | SSE (EventSource) | WebSocket |
|---|---|---|
| 协议 | HTTP (单向 server→client) | 独立 ws:// 协议 |
| 浏览器支持 | 原生,所有现代浏览器 | 需 WS 库 |
| 重连 | 内置自动重连 | 需手写退避 |
| 方向 | 单向(server 推) | 双向 |
| nginx 反代 | 简单(加 `proxy_buffering off`) | 需 upgrade 头 |
| 鉴权 | Cookie / Header 都行 | 略复杂 |
| 适用场景 | **数据推**(本项目选这个) | 双向交互(聊天/协同编辑) |

**选型口诀**:
- **server→client 单向数据** → SSE
- **双向交互(聊天/游戏/协同)** → WebSocket
- **超低延迟(<10ms)** → WebSocket
- **简单推送 + 自动重连 + 跨域友好** → SSE(本项目推荐)

---

## 二、后端: FastAPI SSE

### 基础:逐行推送

```python
"""
FastAPI SSE:每 1s 推送一条数据
"""
import asyncio
import time
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def number_stream():
    """每 1s 推一个递增数字"""
    n = 0
    while True:
        n += 1
        # SSE 格式: data: <内容>\n\n
        yield f"data: {{\"value\": {n}, \"ts\": {time.time()}}}\n\n"
        await asyncio.sleep(1)


@app.get("/api/stream/numbers")
async def stream_numbers():
    return StreamingResponse(
        number_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 关键:防止 nginx buffer
            "Connection": "keep-alive"
        }
    )
```

### 进阶:LLM 流式输出 + 工具调用

```python
"""
LLM 流式输出 + 自动执行工具 + 回传 LLM
这是 AI 智能问答的核心
"""
import os
import json
import asyncio
import httpx
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_msg = data["message"]
    history = data.get("history", [])
    tools = data.get("tools", [])
    
    async def event_stream():
        try:
            # 1. 调 LLM 流式 API
            async with httpx.AsyncClient(timeout=60) as client:
                llm_resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                    json={
                        "model": "gpt-4",
                        "messages": history + [{"role": "user", "content": user_msg}],
                        "tools": tools,
                        "stream": True
                    }
                )
                
                tool_calls = []
                content_buf = []
                last_flush = time.time()
                
                async for line in llm_resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:].strip()
                    if chunk == "[DONE]":
                        break
                    
                    try:
                        delta = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
                    
                    choice = delta.get("choices", [{}])[0]
                    message = choice.get("delta", {})
                    
                    # 流式文本
                    if "content" in message and message["content"]:
                        content_buf.append(message["content"])
                        # 每 50ms flush 一次
                        if time.time() - last_flush > 0.05:
                            yield f"event: text\ndata: {json.dumps({'content': ''.join(content_buf)})}\n\n"
                            content_buf.clear()
                            last_flush = time.time()
                    
                    # 工具调用(增量)
                    if "tool_calls" in message:
                        for tc in message["tool_calls"]:
                            idx = tc.get("index", 0)
                            while len(tool_calls) <= idx:
                                tool_calls.append({"id": "", "name": "", "arguments": ""})
                            if tc.get("id"):
                                tool_calls[idx]["id"] = tc["id"]
                            if tc.get("function", {}).get("name"):
                                tool_calls[idx]["name"] += tc["function"]["name"]
                            if tc.get("function", {}).get("arguments"):
                                tool_calls[idx]["arguments"] += tc["function"]["arguments"]
                
                # flush 剩余文本
                if content_buf:
                    yield f"event: text\ndata: {json.dumps({'content': ''.join(content_buf)})}\n\n"
                
                # 2. 执行工具调用
                for tc in tool_calls:
                    if not tc["name"]:
                        continue
                    try:
                        args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                    except json.JSONDecodeError:
                        args = {}
                    
                    yield f"event: tool_call\ndata: {json.dumps({'name': tc['name'], 'args': args})}\n\n"
                    
                    # 实际执行
                    try:
                        # 这里根据工具名路由到不同实现
                        result = await execute_tool(tc["name"], args)
                        yield f"event: tool_result\ndata: {json.dumps({'name': tc['name'], 'result': result})}\n\n"
                    except Exception as e:
                        yield f"event: tool_error\ndata: {json.dumps({'name': tc['name'], 'error': str(e)})}\n\n"
            
            yield "event: done\ndata: {}\n\n"
        
        except asyncio.CancelledError:
            # 客户端断开
            print("[SSE] 客户端断开")
            raise
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


async def execute_tool(name: str, args: dict) -> dict:
    """工具路由(根据 name 分发)"""
    if name == "search_poi":
        # 实际查 POI
        return {"count": 5, "items": [...]}
    elif name == "get_weather":
        return {"temp": 25, "city": args.get("city")}
    raise ValueError(f"未知工具: {name}")
```

---

## 三、前端:EventSource 客户端

### 基础:接收 + 显示

```js
// static/js/ai-chat-client.js
class AIChatClient {
    constructor() {
        this.es = null;
        this.history = [];
    }
    
    async send(userMsg) {
        // 1. 关闭旧连接
        if (this.es) this.es.close();
        
        // 2. 加到历史
        this.history.push({ role: "user", content: userMsg });
        this._renderHistory();
        
        // 3. 准备 UI
        const assistantMsg = this._appendMessage("assistant", "");
        const textSpan = assistantMsg.querySelector(".text-content");
        const toolLog = assistantMsg.querySelector(".tool-log");
        
        // 4. 开 SSE
        this.es = new EventSource("/api/chat/stream", {
            // EventSource 不支持 POST,所以一般用 fetch + ReadableStream
            // 这里用更现代的 fetch-stream 方式 ↓
        });
        // 实际上 EventSource 只能用 GET,POST 要用 fetch ↓
    }
    
    // 现代方法:用 fetch + ReadableStream(支持 POST)
    async sendWithFetch(userMsg) {
        const response = await fetch("/api/chat/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: userMsg,
                history: this.history,
                tools: TOOLS
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let textContent = "";
        let currentEvent = "message";
        
        const assistantMsg = this._appendMessage("assistant", "");
        const textSpan = assistantMsg.querySelector(".text-content");
        const toolLog = assistantMsg.querySelector(".tool-log");
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            
            // 按 \n\n 切分事件
            const events = buffer.split("\n\n");
            buffer = events.pop() || "";
            
            for (const event of events) {
                if (!event.trim()) continue;
                
                // 解析 SSE:event: xxx\ndata: yyy
                let eventName = "message";
                let data = "";
                for (const line of event.split("\n")) {
                    if (line.startsWith("event: ")) {
                        eventName = line.slice(7).trim();
                    } else if (line.startsWith("data: ")) {
                        data = line.slice(6).trim();
                    }
                }
                
                if (eventName === "text") {
                    const payload = JSON.parse(data);
                    textContent += payload.content;
                    textSpan.textContent = textContent;
                    this._scrollToBottom();
                } else if (eventName === "tool_call") {
                    const payload = JSON.parse(data);
                    this._appendToolCall(toolLog, payload);
                } else if (eventName === "tool_result") {
                    const payload = JSON.parse(data);
                    this._appendToolResult(toolLog, payload);
                } else if (eventName === "done") {
                    this.history.push({ role: "assistant", content: textContent });
                } else if (eventName === "error") {
                    const payload = JSON.parse(data);
                    textSpan.textContent = `❌ 错误: ${payload.error}`;
                }
            }
        }
    }
    
    _appendMessage(role, content) {
        const div = document.createElement("div");
        div.className = `message message-${role}`;
        div.innerHTML = `
            <div class="avatar">${role === "user" ? "我" : "AI"}</div>
            <div class="content">
                <div class="text-content">${content}</div>
                <div class="tool-log"></div>
            </div>
        `;
        document.getElementById("chat-messages").appendChild(div);
        return div;
    }
    
    _appendToolCall(container, { name, args }) {
        const div = document.createElement("div");
        div.className = "tool-call";
        div.innerHTML = `🔧 调用工具: <code>${name}</code> (${JSON.stringify(args)})`;
        container.appendChild(div);
    }
    
    _appendToolResult(container, { name, result }) {
        const div = document.createElement("div");
        div.className = "tool-result";
        div.innerHTML = `✅ <code>${name}</code> → ${JSON.stringify(result).slice(0, 100)}...`;
        container.appendChild(div);
    }
    
    _renderHistory() {
        // 重新渲染历史
    }
    
    _scrollToBottom() {
        const msg = document.getElementById("chat-messages");
        msg.scrollTop = msg.scrollHeight;
    }
}

const chat = new AIChatClient();
document.getElementById("send-btn").addEventListener("click", () => {
    const input = document.getElementById("user-input");
    if (input.value.trim()) {
        chat.sendWithFetch(input.value.trim());
        input.value = "";
    }
});
```

### 性能优化:节流 + 取消

```js
class AIChatClient {
    constructor() {
        this.abortController = null;
        this.pendingText = "";
        this.rafScheduled = false;
    }
    
    async sendWithFetch(userMsg) {
        // 1. 取消上一次(用户连续发)
        if (this.abortController) {
            this.abortController.abort();
        }
        this.abortController = new AbortController();
        
        const response = await fetch("/api/chat/stream", {
            method: "POST",
            signal: this.abortController.signal,
            // ...
        });
        
        const reader = response.body.getReader();
        // ...
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            // 解析 SSE event,textContent 累积到 this.pendingText
            this.pendingText += newText;
            
            // 用 requestAnimationFrame 节流 DOM 更新
            if (!this.rafScheduled) {
                this.rafScheduled = true;
                requestAnimationFrame(() => {
                    textSpan.textContent = this.pendingText;
                    this.rafScheduled = false;
                    this._scrollToBottom();
                });
            }
        }
    }
}
```

---

## 四、nginx 反代配置(SSE 关键)

```nginx
location /api/stream {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # === SSE 关键配置 ===
    proxy_buffering off;              # 关闭 buffering(默认 on 会攒)
    proxy_cache off;
    chunked_transfer_encoding off;    # 禁用分块(跟 SSE 冲突)
    
    # 超时(默认 60s 太短)
    proxy_read_timeout 86400s;        # 24h
    proxy_send_timeout 86400s;
    
    # 后端响应头也建议加
    add_header X-Accel-Buffering no;
}
```

---

## 五、避坑 7 条

| # | 踩坑 | 解决 |
|---|---|---|
| 1 | nginx 卡 60s | `proxy_buffering off` + `X-Accel-Buffering: no` |
| 2 | EventSource 只能 GET | 改用 `fetch + ReadableStream` 支持 POST |
| 3 | buffer 太大,内存爆 | 后端每 50ms flush + 前端 rAF 节流 |
| 4 | 断线重连风暴 | `AbortController` + 退避(本项目用 fetch,不自动重连) |
| 5 | EventSource 6 连接/浏览器限制 | 多 Tab 共享用 `SharedWorker` |
| 6 | CORS 跨域 | `Access-Control-Allow-Origin: *` + `withCredentials: false` |
| 7 | 客户端断开后端还在跑 | `try/except asyncio.CancelledError` 清理资源 |

---

## 六、避坑口诀

**nginx off buffer / fetch+stream / 50ms flush / rAF 节流 / 取消旧连接 / SSE 单向适合**
