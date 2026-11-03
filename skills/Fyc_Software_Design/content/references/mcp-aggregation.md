# MCP 多 Server 聚合模式(2026-08)

> **来源**:AI-GIS 智能问图平台 v0.4.0 实战
> **场景**:1 个主 MCP server (stdio) + N 个子 server (GIS / QGIS / 数据库 / ...)
> **核心价值**:LLM 通过 1 个入口访问所有工具,工具名空间隔离,跨 server 编排

---

## 一、为什么需要聚合

**问题**:LLM 调用工具时,工具数 > 100 时:
- 上下文窗口爆(每个工具的 schema 都占 token)
- 工具名冲突(不同 server 都有 `search`)
- 单 server 故障导致全部不可用
- 工具更新要重启 LLM 连接

**聚合解决**:
- 1 个主 server 暴露"工具集视图",按需懒加载
- 工具名空间隔离: `server_name__tool_name`
- 故障隔离:1 个子 server 挂了不影响其他
- 工具注册中心:统一管理

---

## 二、架构图

```
┌─────────────────┐
│   LLM (Claude)  │  ← 1 个 MCP 客户端
└────────┬────────┘
         │ stdio (JSON-RPC)
         ▼
┌─────────────────┐
│  mcp-gateway    │  ← 主 server,工具聚合
│  (Python)       │     路由 + 编排
└────────┬────────┘
         │ 内部协议 (HTTP/stdio/socket)
         │
   ┌─────┼──────────┬──────────┐
   ▼     ▼          ▼          ▼
┌─────┐ ┌─────┐  ┌──────┐  ┌──────┐
│ gis │ │qgis │  │ db   │  │ file │
│ MCP │ │bridge│ │ MCP  │  │ MCP  │
└─────┘ └─────┘  └──────┘  └──────┘
  37 工具  22 工具  15 工具   5 工具
```

**工具命名**:
- `gis__search_poi` (gis server 的 search_poi)
- `qgis__execute_processing` (qgis server 的执行处理)
- `db__query_postgres` (db server 的查询)

---

## 三、核心实现

### gateway.py - 主 server

```python
"""
MCP 多 server 聚合网关
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List
from contextlib import asynccontextmanager

# 选 1 种 MCP 客户端实现
# 方式 1: 官方 mcp SDK
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# 方式 2: 自实现 JSON-RPC stdio(更轻量,推荐)
class MCPClient:
    """单个子 MCP server 客户端"""
    
    def __init__(self, name: str, command: List[str], env: Dict = None):
        self.name = name
        self.command = command
        self.env = env or {}
        self.process = None
        self.tools = {}  # tool_name -> tool_schema
        self._req_id = 0
    
    async def start(self):
        """启动子进程"""
        import subprocess
        full_env = {**os.environ, **self.env}
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env
        )
        # initialize
        await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": f"gateway-{self.name}", "version": "1.0"}
        })
        # 拉取工具列表
        result = await self._send_request("tools/list", {})
        self.tools = {t["name"]: t for t in result.get("tools", [])}
        print(f"[MCP] {self.name} 已连接,工具数: {len(self.tools)}")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用工具"""
        return await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    async def _send_request(self, method: str, params: dict) -> dict:
        """JSON-RPC over stdio"""
        self._req_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": method,
            "params": params
        }
        line = json.dumps(req, ensure_ascii=False) + "\n"
        self.process.stdin.write(line.encode("utf-8"))
        await self.process.stdin.drain()
        
        # 读响应(单行 JSON)
        resp_line = await self.process.stdout.readline()
        return json.loads(resp_line.decode("utf-8"))


class MCPGateway:
    """主 server:聚合多个子 server"""
    
    def __init__(self, config_path: str = "config/mcp_servers.json"):
        self.servers: Dict[str, MCPClient] = {}
        self.config = self._load_config(config_path)
    
    def _load_config(self, path: str) -> dict:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    
    async def start_all(self):
        """启动所有子 server"""
        for name, cfg in self.config.get("mcpServers", {}).items():
            client = MCPClient(
                name=name,
                command=cfg["command"],
                env=cfg.get("env", {})
            )
            try:
                await client.start()
                self.servers[name] = client
            except Exception as e:
                print(f"[MCP] {name} 启动失败: {e},跳过")
    
    def list_all_tools(self) -> List[dict]:
        """聚合所有工具,加 server 前缀"""
        result = []
        for server_name, client in self.servers.items():
            for tool_name, tool_schema in client.tools.items():
                namespaced = f"{server_name}__{tool_name}"
                result.append({
                    **tool_schema,
                    "name": namespaced,
                    "original_name": tool_name,
                    "server": server_name,
                })
        return result
    
    async def call_tool(self, full_name: str, arguments: dict) -> dict:
        """根据全名路由到对应 server"""
        if "__" not in full_name:
            raise ValueError(f"工具名格式错:{full_name},应为 server__tool")
        server_name, tool_name = full_name.split("__", 1)
        if server_name not in self.servers:
            raise RuntimeError(f"server {server_name} 不可用")
        return await self.servers[server_name].call_tool(tool_name, arguments)
    
    async def stop_all(self):
        for client in self.servers.values():
            if client.process:
                client.process.terminate()
                await client.process.wait()
```

### config/mcp_servers.json - 子 server 配置

```json
{
  "mcpServers": {
    "gis": {
      "command": ["./.venv/Scripts/pythonw.exe", "mcp_gis_server.py"],
      "env": {"GIS_MCP_PORT": "9876"},
      "description": "GIS 数据源聚合(天地图/GeoServer/SuperMap/...)"
    },
    "qgis": {
      "command": ["./.venv/Scripts/pythonw.exe", "qgis_mcp_bridge.py"],
      "env": {"QGIS_MCP_HOST": "127.0.0.1", "QGIS_MCP_PORT": "9876"},
      "description": "QGIS 桌面集成(需 QGIS + qgis_mcp 插件)"
    },
    "db": {
      "command": ["./.venv/Scripts/pythonw.exe", "mcp_db_server.py"],
      "env": {"DB_URL": "postgresql://user:pass@localhost/gis"},
      "description": "PostgreSQL/PostGIS 数据库"
    }
  }
}
```

---

## 四、Python 端调用(MCP 客户端 + LLM 编排)

```python
"""
FastAPI 端:接 LLM,工具调用通过 gateway 路由
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import json

app = FastAPI()
gateway = None


@app.on_event("startup")
async def startup():
    global gateway
    from gateway import MCPGateway
    gateway = MCPGateway()
    await gateway.start_all()


@app.get("/api/mcp/tools")
async def list_tools():
    """暴露给 LLM 的工具列表"""
    tools = gateway.list_all_tools()
    # 转 OpenAI Function Calling 格式
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("inputSchema", {"type": "object", "properties": {}})
                }
            }
            for t in tools
        ]
    }


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """流式对话,工具调用走 gateway"""
    data = await request.json()
    user_msg = data["message"]
    history = data.get("history", [])
    
    async def event_stream():
        # 1. 调 LLM
        async with httpx.AsyncClient() as client:
            llm_resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                json={
                    "model": "gpt-4",
                    "messages": history + [{"role": "user", "content": user_msg}],
                    "tools": (await list_tools())["tools"],
                    "stream": True
                },
                timeout=60
            )
            
            tool_calls = []
            content_buf = []
            async for line in llm_resp.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        delta = json.loads(chunk)
                        choice = delta.get("choices", [{}])[0]
                        # 流式文本
                        if "content" in choice.get("delta", {}):
                            content = choice["delta"]["content"]
                            content_buf.append(content)
                            yield f"data: {json.dumps({'type': 'text', 'content': content})}\n\n"
                        # 工具调用
                        if "tool_calls" in choice.get("delta", {}):
                            for tc in choice["delta"]["tool_calls"]:
                                if tc.get("index") is not None:
                                    while len(tool_calls) <= tc["index"]:
                                        tool_calls.append({"id": "", "name": "", "arguments": ""})
                                    if tc.get("id"):
                                        tool_calls[tc["index"]]["id"] = tc["id"]
                                    if tc.get("function", {}).get("name"):
                                        tool_calls[tc["index"]]["name"] += tc["function"]["name"]
                                    if tc.get("function", {}).get("arguments"):
                                        tool_calls[tc["index"]]["arguments"] += tc["function"]["arguments"]
                    except json.JSONDecodeError:
                        pass
            
            # 2. 执行工具调用
            for tc in tool_calls:
                if not tc["name"]:
                    continue
                args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                yield f"data: {json.dumps({'type': 'tool_call', 'name': tc['name'], 'args': args})}\n\n"
                try:
                    result = await gateway.call_tool(tc["name"], args)
                    yield f"data: {json.dumps({'type': 'tool_result', 'name': tc['name'], 'result': result})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'tool_error', 'name': tc['name'], 'error': str(e)})}\n\n"
            
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## 五、健康检查 + 故障转移

```python
async def health_check():
    """检查所有子 server 健康,挂掉的标记 disabled"""
    for name, client in gateway.servers.items():
        try:
            # 简单 ping
            await client._send_request("ping", {})
            client.healthy = True
        except Exception as e:
            print(f"[MCP] {name} 不健康: {e}")
            client.healthy = False

# 在主 server 定期跑
async def periodic_health_check():
    while True:
        await asyncio.sleep(30)
        await health_check()


# call_tool 路由时跳过不健康的
async def call_tool(self, full_name: str, arguments: dict) -> dict:
    server_name, tool_name = full_name.split("__", 1)
    client = self.servers[server_name]
    if not getattr(client, 'healthy', True):
        # 尝试重启
        try:
            await client.start()
        except Exception:
            raise RuntimeError(f"server {server_name} 不可用,已尝试重启失败")
    return await client.call_tool(tool_name, arguments)
```

---

## 六、避坑口诀

**单 gateway 入口 / 命名空间隔离 / 健康检查 + 重启 / 工具懒加载 / 跨 server 编排**
