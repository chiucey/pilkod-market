"""
MCP 多 Server 聚合网关 完整模板
直接 copy 到项目,改 config/mcp_servers.json 即可
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager


# ============================================================
# 单个子 MCP 客户端(JSON-RPC over stdio)
# ============================================================
class MCPClient:
    def __init__(self, name: str, command: List[str], env: Dict[str, str] = None):
        self.name = name
        self.command = command
        self.env = env or {}
        self.process: Optional[asyncio.subprocess.Process] = None
        self.tools: Dict[str, dict] = {}
        self.healthy = False
        self._req_id = 0
        self._lock = asyncio.Lock()
    
    async def start(self):
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
        # list tools
        result = await self._send_request("tools/list", {})
        self.tools = {t["name"]: t for t in result.get("tools", [])}
        self.healthy = True
        print(f"[MCP] {self.name} 启动,工具数: {len(self.tools)}")
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        async with self._lock:
            return await self._send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
    
    async def ping(self) -> bool:
        try:
            await self._send_request("ping", {})
            self.healthy = True
            return True
        except Exception:
            self.healthy = False
            return False
    
    async def stop(self):
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
            self.healthy = False
    
    async def _send_request(self, method: str, params: dict, timeout: float = 30) -> dict:
        if not self.process or self.process.returncode is not None:
            raise RuntimeError(f"{self.name} 进程已退出")
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
        
        try:
            resp_line = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise RuntimeError(f"{self.name}.{method} 超时 ({timeout}s)")
        
        return json.loads(resp_line.decode("utf-8"))


# ============================================================
# 主网关:聚合所有子 server
# ============================================================
class MCPGateway:
    def __init__(self, config_path: str = "config/mcp_servers.json"):
        self.servers: Dict[str, MCPClient] = {}
        self.config_path = config_path
        self._health_task: Optional[asyncio.Task] = None
    
    async def start_all(self):
        cfg = self._load_config()
        for name, server_cfg in cfg.get("mcpServers", {}).items():
            client = MCPClient(
                name=name,
                command=server_cfg["command"],
                env=server_cfg.get("env", {})
            )
            try:
                await client.start()
                self.servers[name] = client
            except Exception as e:
                print(f"[MCP] {name} 启动失败: {e},跳过")
        
        # 启动健康检查
        self._health_task = asyncio.create_task(self._periodic_health_check())
    
    async def stop_all(self):
        if self._health_task:
            self._health_task.cancel()
        for client in self.servers.values():
            await client.stop()
    
    def _load_config(self) -> dict:
        return json.loads(Path(self.config_path).read_text(encoding="utf-8"))
    
    def list_all_tools(self) -> List[dict]:
        """聚合所有工具,加 server 前缀"""
        result = []
        for server_name, client in self.servers.items():
            if not client.healthy:
                continue
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
        if "__" not in full_name:
            raise ValueError(f"工具名格式错: {full_name},应为 server__tool")
        server_name, tool_name = full_name.split("__", 1)
        if server_name not in self.servers:
            raise RuntimeError(f"server {server_name} 不可用")
        client = self.servers[server_name]
        if not client.healthy:
            # 尝试重启
            try:
                await client.start()
            except Exception:
                raise RuntimeError(f"server {server_name} 不可用,重启失败")
        return await client.call_tool(tool_name, arguments)
    
    async def _periodic_health_check(self):
        """每 30s 检查一次健康"""
        while True:
            await asyncio.sleep(30)
            for name, client in self.servers.items():
                ok = await client.ping()
                if not ok:
                    print(f"[MCP] {name} 不健康,尝试重启...")
                    try:
                        await client.stop()
                        await client.start()
                    except Exception as e:
                        print(f"[MCP] {name} 重启失败: {e}")


# ============================================================
# FastAPI 集成
# ============================================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="MCP Gateway")
gateway: Optional[MCPGateway] = None


@app.on_event("startup")
async def startup():
    global gateway
    gateway = MCPGateway()
    await gateway.start_all()


@app.on_event("shutdown")
async def shutdown():
    if gateway:
        await gateway.stop_all()


@app.get("/api/mcp/tools")
async def list_tools():
    """暴露给 LLM 的工具列表(OpenAI Function Calling 格式)"""
    tools = gateway.list_all_tools()
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


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict


@app.post("/api/mcp/call")
async def call_tool(req: ToolCallRequest):
    """直接调用工具(不走 LLM)"""
    try:
        result = await gateway.call_tool(req.name, req.arguments)
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(500, str(e))


# ============================================================
# 配置示例:config/mcp_servers.json
# ============================================================
EXAMPLE_CONFIG = {
    "mcpServers": {
        "gis": {
            "command": ["./.venv/Scripts/pythonw.exe", "mcp_gis_server.py"],
            "env": {"GIS_MCP_PORT": "9876"},
            "description": "GIS 数据源聚合"
        },
        "qgis": {
            "command": ["./.venv/Scripts/pythonw.exe", "qgis_mcp_bridge.py"],
            "env": {"QGIS_MCP_HOST": "127.0.0.1", "QGIS_MCP_PORT": "9876"},
            "description": "QGIS 桌面集成"
        }
    }
}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
