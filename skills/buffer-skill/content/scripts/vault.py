#!/usr/bin/env python3
"""
Buffer Vault - 多账号加密管理 + 自动 MCP 注册
用法:
    export BUFFER_VAULT_KEY='你的加密密钥'

    # 账号管理
    python3 vault.py add <账号名> <API Key>          # 添加账号 + 自动注册 MCP
    python3 vault.py list                              # 列出所有账号
    python3 vault.py get <账号名>                      # 获取 Key
    python3 vault.py remove <账号名>                    # 删除账号
    python3 vault.py servers                           # 列出已注册的 MCP server 名称

    # MCP Server 操作
    python3 vault.py register <账号名>                 # 为账号注册 MCP Server
    python3 vault.py unregister <账号名>               # 删除账号的 MCP Server
"""
import sys
import json
import os
import base64
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("请先安装: pip install cryptography")
    sys.exit(1)

SALT = b"buffer-vault-salt-v1-2026"

# ---------------------------------------------------------------------------
# 加密 / 解密
# ---------------------------------------------------------------------------
def get_fernet(passphrase: str) -> Fernet:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=100000)
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return Fernet(key)


def require_key():
    k = os.environ.get("BUFFER_VAULT_KEY", "").strip()
    if not k:
        raise ValueError("请先设置环境变量 BUFFER_VAULT_KEY")
    return k


def vault_path() -> Path:
    return Path(__file__).parent / ".vault"


def load_vault(key: str) -> dict:
    f = get_fernet(key)
    p = vault_path()
    if not p.exists():
        return {}
    data = p.read_text()
    if not data.strip():
        return {}
    try:
        return json.loads(f.decrypt(data.encode()))
    except Exception:
        raise ValueError("密钥错误或 vault 文件损坏")


def save_vault(key: str, data: dict):
    f = get_fernet(key)
    vault_path().write_bytes(f.encrypt(json.dumps(data, ensure_ascii=False).encode()))


# ---------------------------------------------------------------------------
# MCP Server 配置读写
# ---------------------------------------------------------------------------
MCP_PATH = Path("/root/.mcporter/mcporter.json")


def load_mcp() -> dict:
    if MCP_PATH.exists():
        try:
            return json.loads(MCP_PATH.read_text())
        except Exception:
            pass
    return {"mcpServers": {}}


def save_mcp(data: dict):
    MCP_PATH.parent.mkdir(parents=True, exist_ok=True)
    MCP_PATH.write_text(json.dumps(data, indent=2))


def mcp_server_name(account: str, channel_id: str = "") -> str:
    """账号 + 渠道 → 唯一 server 名"""
    return f"buf_{account}"


def get_mcp_server_name_for_account(account: str) -> str:
    """同一账号所有渠道共用同一个 MCP server"""
    return f"buf_{account}"


# ---------------------------------------------------------------------------
# Buffer API 查询（不依赖 MCP，直接 HTTP）
# ---------------------------------------------------------------------------
def buffer_api(api_key: str, query: str, variables: dict = None) -> dict:
    """通过 Buffer REST/GraphQL API 查询"""
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "execute_query", "arguments": {"query": query, "variables": variables or {}}}
    }).encode()

    req = urllib.request.Request(
        "https://mcp.buffer.com/mcp",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json, text/event-stream"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            # 解开 MCP 包装
            result = data.get("result", [])
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("text", "{}")
                return json.loads(text)
            return data
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}


def get_buffer_channels(api_key: str) -> list:
    """获取 Buffer 账号下的所有 channel"""
    # 先获取 organization id
    acct = buffer_api(api_key, "query { account { organizations { id name } } }")
    orgs = acct.get("data", {}).get("account", {}).get("organizations", [])
    if not orgs:
        return []

    org_id = orgs[0]["id"]
    channels = buffer_api(
        api_key,
        "query ListChannels($org: ID!) { channels(organizationId: $org) { id name service } }",
        {"org": org_id}
    )
    return channels.get("data", {}).get("channels", [])


# ---------------------------------------------------------------------------
# MCP Server 注册 / 注销
# ---------------------------------------------------------------------------
def register_account_mcp(account: str, api_key: str):
    """为账号注册一个 MCP Server（共用一个 server，Header 携带 API Key）"""
    mcp = load_mcp()
    servers = mcp.setdefault("mcpServers", {})

    server_name = get_mcp_server_name_for_account(account)
    servers[server_name] = {
        "baseUrl": "https://mcp.buffer.com/mcp",
        "headers": {
            "Authorization": f"Bearer {api_key}"
        }
    }
    save_mcp(mcp)

    # 验证连通性
    try:
        result = subprocess.run(
            ["npx", "-y", "mcporter@latest", "--root", "/root/.mcporter",
             "call", f"{server_name}.get_account"],
            capture_output=True, text=True, timeout=20,
            env={**os.environ, "BUFFER_VAULT_KEY": api_key}
        )
        if result.returncode == 0:
            print(f"  ✅ MCP Server [{server_name}] 注册成功并已验证")
        else:
            print(f"  ⚠️  注册完成但验证失败: {result.stderr[:100]}")
    except Exception as e:
        print(f"  ⚠️  注册完成，验证超时: {e}")

    return server_name


def unregister_account_mcp(account: str):
    server_name = get_mcp_server_name_for_account(account)
    mcp = load_mcp()
    servers = mcp.get("mcpServers", {})
    if server_name in servers:
        del servers[server_name]
        save_mcp(mcp)
        print(f"✅ 已删除 MCP Server: {server_name}")
    else:
        print(f"账号 [{account}] 没有注册的 MCP Server")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
CMDS = {}


def cmd(fn):
    CMDS[fn.__name__.replace("cmd_", "")] = fn
    return fn


def find_account(vault: dict, name: str) -> str:
    """模糊匹配账号名"""
    if name in vault:
        return name
    # 前缀匹配
    matches = [k for k in vault if k.startswith(name)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(f"账号模糊匹配结果不唯一: {matches}")
    raise ValueError(f"账号不存在: {name}")


@cmd
def add(name: str, api_key: str):
    """
    添加账号 + 自动注册 MCP Server
    用法: vault.py add <账号名> <API Key>
    """
    key = require_key()
    vault = load_vault(key)

    # 保存到 vault
    vault[name] = {"api_key": api_key}
    save_vault(key, vault)

    # 注册 MCP Server
    print(f"  正在注册 MCP Server ...")
    server_name = register_account_mcp(name, api_key)

    masked = api_key[:6] + "..." + api_key[-4:]
    print(f"✅ 账号 [{name}] 已添加 | MCP: {server_name} | Key: {masked}")

    # 列出账号下的 channel
    print(f"  正在探测账号下的渠道 ...")
    try:
        channels = get_buffer_channels(api_key)
        if channels:
            ch_list = ", ".join(f"{c['service']}({c['id'][:12]}...)" for c in channels)
            print(f"  渠道: {ch_list}")
        else:
            print("  渠道: （未发现，请到 Buffer 后台确认已连接）")
    except Exception as e:
        print(f"  渠道探测失败: {e}")


@cmd
def remove(name: str):
    """删除账号 + 注销 MCP Server"""
    key = require_key()
    vault = load_vault(key)
    name = find_account(vault, name)
    del vault[name]
    save_vault(key, vault)
    unregister_account_mcp(name)
    print(f"✅ 已删除账号: {name}")


@cmd
def list_(verbose: str = ""):
    """列出所有账号"""
    try:
        key = require_key()
        vault = load_vault(key)
    except Exception:
        vault = {}
    if not vault:
        print("（暂无账号）")
        return
    for name, data in sorted(vault.items()):
        k = data.get("api_key", "")
        m = k[:6] + "..." + k[-4:] if len(k) > 12 else "***"
        server = get_mcp_server_name_for_account(name)
        print(f"  [{name}] {m} | MCP: {server}  ({len(k)} chars)")


@cmd
def get(name: str):
    """获取指定账号的 API Key"""
    key = require_key()
    vault = load_vault(key)
    name = find_account(vault, name)
    print(vault[name]["api_key"])


@cmd
def servers():
    """列出已注册的 MCP Server"""
    mcp = load_mcp()
    servers = mcp.get("mcpServers", {})
    if not servers:
        print("（无已注册的 MCP Server）")
        return
    for name, cfg in sorted(servers.items()):
        header = cfg.get("headers", {}).get("Authorization", "???")
        print(f"  {name}: {header[:15]}...  →  {cfg.get('baseUrl', '')}")


@cmd
def register(name: str):
    """为已存在的账号重新注册 MCP Server"""
    key = require_key()
    vault = load_vault(key)
    name = find_account(vault, name)
    api_key = vault[name]["api_key"]
    server_name = register_account_mcp(name, api_key)
    print(f"✅ [{name}] MCP Server 已注册: {server_name}")


@cmd
def unregister(name: str):
    """注销账号的 MCP Server（但保留 Key）"""
    key = require_key()
    vault = load_vault(key)
    name = find_account(vault, name)
    unregister_account_mcp(name)


@cmd
def add_channel(name: str, channel_id: str, service: str = ""):
    """为账号手动添加一个 channel（当账号已有渠道但未被自动探测时）"""
    key = require_key()
    vault = load_vault(key)
    name = find_account(vault, name)
    if "channels" not in vault[name]:
        vault[name]["channels"] = []
    vault[name]["channels"].append({"id": channel_id, "service": service or "unknown"})
    save_vault(key, vault)
    print(f"✅ 已为 [{name}] 添加 channel: {channel_id} ({service})")


@cmd
def channels(name: str = ""):
    """查看账号下的所有渠道"""
    key = require_key()
    vault = load_vault(key)
    if not name:
        # 列出所有账号的渠道摘要
        for acc, data in sorted(vault.items()):
            chs = data.get("channels", [])
            if chs:
                s = ", ".join(f"{c['service']}({c['id'][:10]}...)" for c in chs)
            else:
                s = "（无手动记录，需重新 register）"
            print(f"  [{acc}]: {s}")
        return

    name = find_account(vault, name)
    api_key = vault[name]["api_key"]
    print(f"  正在查询 Buffer API ...")
    chs = get_buffer_channels(api_key)
    if chs:
        for c in chs:
            print(f"  {c['service']:12} | {c['id']} | {c.get('name', '')}")
    else:
        print("  未查到渠道，请确认账号已连接渠道")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    # 内置环境变量：BUFFER_VAULT_KEY=xxx python3 vault.py ...
    # 优先用命令行指定的
    if len(args) >= 3 and args[0] == "add":
        # python3 vault.py add <name> <key> - 自动设置临时 key
        pass

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    cmd_name = args[0]
    cmd_args = args[1:]

    # list_ 别名
    if cmd_name == "list":
        cmd_name = "list_"

    fn = CMDS.get(cmd_name)
    if not fn:
        print(f"未知命令: {cmd_name}")
        print("可用:", ", ".join(sorted(CMDS.keys())))
        sys.exit(1)

    try:
        fn(*cmd_args)
    except TypeError as e:
        print(f"参数错误: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)