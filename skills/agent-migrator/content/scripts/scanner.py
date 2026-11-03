#!/usr/bin/env python3
"""
Agent Migrator Scanner - Analyze agent configurations and generate migration plans
Supports: OpenClaw, CherryBot, Dify, AnythingLLM, AutoGen, and custom platforms

Usage:
    python3 scanner.py --source <platform> --target <target> [--path /scan/path]

Workflow:
  Step 0: Confirm target platform (--target required)
  Step 1: Scan source platform config
  Step 2: Platform diff analysis (source vs target)
  Step 3: Categorize files (direct/convert/rebuild/skip)
  Step 4: Detect extended components (sub-agents, MCP, external DB)
  Step 5: Generate migration plan document
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

__version__ = "1.0.0"

# ============================================================================
# Platform Configuration
# ============================================================================

PLATFORMS = {
    "openclaw": {
        "name": "OpenClaw",
        "indicators": [".openclaw", "openclaw.json", "skills/"],
    },
    "cherrybot": {
        "name": "CherryBot (飞书桥接)",
        "indicators": ["feishu_bridge.py", "CherryBot"],
    },
    "dify": {
        "name": "Dify",
        "indicators": ["docker-compose.yml", "dify/", ".env"],
    },
    "anythingllm": {
        "name": "AnythingLLM",
        "indicators": ["AnythingLLM", "config.json"],
    },
    "autogen": {
        "name": "AutoGen",
        "indicators": ["config.yaml", "autogen", "agents/"],
    },
    "coze": {
        "name": "Coze",
        "indicators": ["coze", "bot.json"],
    },
}

PLATFORM_COMPAT = {
    ("openclaw", "openclaw"): {
        "can_direct": True,
        "needs_conversion": False,
        "notes": "同一平台，直接迁移几乎所有文件"
    },
    ("openclaw", "cherrybot"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "OpenClaw 配置与 CherryBot 架构不同，需重新设计桥接方案"
    },
    ("openclaw", "dify"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "OpenClaw skills 系统与 Dify 工作流完全不同，需重建"
    },
    ("openclaw", "coze"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "Coze 不支持自定义 skill 目录，仅支持 Bot 工作流"
    },
    ("cherrybot", "openclaw"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "CherryBot 桥接逻辑需在 OpenClaw 中重新实现"
    },
    ("dify", "coze"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "Dify 工作流与 Coze Bot 格式不兼容，需重建"
    },
    ("dify", "openclaw"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "Dify API 配置可迁移，但 skills 需重新编写"
    },
    ("openclaw", "anythingllm"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "OpenClaw 与 AnythingLLM 架构完全不同，需重建"
    },
    ("anythingllm", "openclaw"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "AnythingLLM 向量数据需导出后在 OpenClaw 重建"
    },
    ("openclaw", "autogen"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "OpenClaw JSON 配置需转换为 Python 代码"
    },
    ("autogen", "openclaw"): {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "AutoGen Python 代码需转换为 OpenClaw JSON 配置"
    },
}

# ============================================================================
# Utility Functions
# ============================================================================

def _deep_get(obj, *keys, default=None):
    """Safely traverse nested dict/list structures."""
    for k in keys:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(k, default)
        elif isinstance(obj, list) and isinstance(k, int):
            obj = obj[k] if k < len(obj) else default
        else:
            return default
    return obj


def _mask(s, keep_end=6):
    """Mask a string, keeping first 2 and last `keep_end` chars."""
    if not s or len(s) <= keep_end + 2:
        return "****"
    return s[:2] + "****" + s[-keep_end:]


def _safe_read_json(filepath):
    """Safely read and parse JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return None


def _detect_platform(path="."):
    """Auto-detect platform from directory contents."""
    detected = []
    try:
        files = os.listdir(path)
    except OSError:
        return None

    for plat_id, plat_info in PLATFORMS.items():
        for indicator in plat_info.get("indicators", []):
            if indicator in files or os.path.exists(os.path.join(path, indicator)):
                detected.append(plat_id)
                break

    return detected[0] if len(detected) == 1 else (detected[0] if detected else None)


# ============================================================================
# Extended Component Detection
# ============================================================================

def _detect_subagents(config):
    """
    Detect sub-agent / sessions_spawn configurations.
    Looks in:
      - openclaw.json > agents[]
      - openclaw.json > sessions[]
      - openclaw.json > subagents[]
      - openclaw.json > sessions_spawn[]
      - skills/*/agent.json
    """
    agents = []

    # Top-level agents array
    for a in config.get("agents", []):
        agents.append({
            "name": a.get("name", a.get("id", "未命名")),
            "type": a.get("type", a.get("runtime", "unknown")),
            "model": a.get("model", a.get("llm", "—")),
            "prompt": a.get("prompt", a.get("description", "—")),
            "notes": "在 openclaw.json > agents[] 中定义",
        })

    # sessions / sessions_spawn configs
    for s in config.get("sessions", config.get("sessionConfigs", config.get("sessions_spawn", []))):
        agents.append({
            "name": s.get("name", s.get("id", "未命名")),
            "type": s.get("runtime", s.get("type", "subagent")),
            "model": s.get("model", "default"),
            "prompt": s.get("prompt", s.get("description", "—")),
            "notes": "在 openclaw.json > sessions[] 中定义",
        })

    # subagents array (alternative naming)
    for s in config.get("subagents", []):
        agents.append({
            "name": s.get("name", s.get("id", "未命名")),
            "type": s.get("runtime", s.get("type", "subagent")),
            "model": s.get("model", "default"),
            "prompt": s.get("prompt", s.get("description", "—")),
            "notes": "在 openclaw.json > subagents[] 中定义",
        })

    # skills/*/agent.json files
    if os.path.isdir("skills"):
        for skill in os.listdir("skills"):
            agent_json = os.path.join("skills", skill, "agent.json")
            if os.path.exists(agent_json):
                adata = _safe_read_json(agent_json)
                if adata:
                    agents.append({
                        "name": adata.get("name", skill),
                        "type": adata.get("runtime", adata.get("type", "subagent")),
                        "model": adata.get("model", "default"),
                        "prompt": adata.get("prompt", adata.get("description", "—")),
                        "notes": f"skills/{skill}/agent.json",
                    })

    # Deduplicate by name
    seen = set()
    deduped = []
    for a in agents:
        if a["name"] not in seen:
            seen.add(a["name"])
            deduped.append(a)
    return deduped


def _detect_mcp_servers(config):
    """
    Detect MCP server connections.
    Looks in:
      - openclaw.json > mcpServers[]
      - openclaw.json > mcp > servers{}
      - openclaw.json > plugins[].mcp
      - .env > MCP_* variables
      - mcp.json / mcp_config.json / mcp_servers.json
    """
    servers = []

    # Standard mcpServers array
    for srv in config.get("mcpServers", []):
        servers.append({
            "name": srv.get("name", srv.get("id", "未命名")),
            "url": srv.get("url", srv.get("endpoint", "—" )),
            "auth": srv.get("auth", srv.get("token", "—" )),
            "type": "mcpServers[] Array",
            "migratable": False,
            "note": "MCP Server 地址和 Token 需在目标平台重新配置",
        })

    # mcp > servers{} object style
    mcp_cfg = config.get("mcp", {})
    for name, srv in mcp_cfg.get("servers", {}).items():
        url = srv.get("url", srv.get("endpoint", "—" )) if isinstance(srv, dict) else "—"
        auth = srv.get("auth", srv.get("token", "—" )) if isinstance(srv, dict) else "—"
        servers.append({
            "name": name,
            "url": url,
            "auth": _mask(auth) if auth and auth != "—" else "无",
            "type": "mcp.servers{} Object",
            "migratable": False,
            "note": "MCP Server 连接需在目标平台重新注册",
        })

    # plugins with mcp field
    for plugin in config.get("plugins", []):
        if "mcp" in plugin:
            mcp = plugin["mcp"]
            if isinstance(mcp, dict):
                for name, srv in mcp.items():
                    servers.append({
                        "name": name,
                        "url": srv.get("url", srv.get("endpoint", "—" )) if isinstance(srv, dict) else "—",
                        "auth": _mask(srv.get("token", srv.get("auth", "—" ))) if isinstance(srv, dict) else "—",
                        "type": f"Plugin MCP: {plugin.get('name', plugin.get('id', '?'))}",
                        "migratable": False,
                        "note": "插件 MCP 需在目标平台重新配置",
                    })

    # .env MCP variables
    if os.path.exists(".env"):
        with open(".env", encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("MCP_"):
                    key = line.split("=", 1)[0]
                    servers.append({
                        "name": key,
                        "url": "（见 .env）",
                        "auth": "（见 .env）",
                        "type": ".env MCP 变量",
                        "migratable": False,
                        "note": "在 .env 中定义，需迁移变量名但重新填写值",
                    })

    # mcp.json / mcp_config.json files
    for fname in ["mcp.json", "mcp_config.json", "mcp_servers.json"]:
        if os.path.exists(fname):
            mcp_data = _safe_read_json(fname)
            if mcp_data:
                # Flatten all server-like entries
                def flatten(obj, prefix=""):
                    items = []
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, dict) and ("url" in v or "endpoint" in v):
                                items.append({"name": prefix + k, **v})
                            elif isinstance(v, list):
                                items.extend(flatten(v, prefix + k + "."))
                            elif isinstance(v, dict):
                                items.extend(flatten(v, prefix + k + "."))
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj):
                            items.extend(flatten(v, prefix + str(i) + "."))
                    return items

                for srv in flatten(mcp_data):
                    servers.append({
                        "name": srv.get("name", srv.get("id", "未识别")),
                        "url": srv.get("url", srv.get("endpoint", "—" )),
                        "auth": _mask(srv.get("token", srv.get("auth", "—" ))),
                        "type": fname,
                        "migratable": False,
                        "note": f"MCP Server 配置在 {fname}，需重新注册",
                    })

    # Deduplicate by name+type
    seen = set()
    deduped = []
    for s in servers:
        key = (s["name"], s["type"])
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped


def _detect_external_databases(config):
    """
    Detect external database connections.
    Looks in:
      - openclaw.json > databases[]
      - openclaw.json > plugins[].database
      - .env > DATABASE_URL / SUPABASE_* / POSTGRES_* / MONGO_*
      - supabase.json / database.json / db_config.json
    """
    dbs = []
    db_patterns = {
        "supabase": ["SUPABASE_", "NEXT_PUBLIC_SUPABASE_", "SUPABASE_URL", "SUPABASE_KEY"],
        "postgresql": ["POSTGRES_", "PG_", "DATABASE_URL"],
        "mysql": ["MYSQL_", "DB_HOST", "DB_PORT"],
        "mongodb": ["MONGO_", "MONGODB_"],
        "redis": ["REDIS_", "REDIS_URL"],
        "sqlite": ["SQLITE_", "DATABASE_PATH"],
    }

    def db_type_from_key(key):
        for db_type, prefixes in db_patterns.items():
            for p in prefixes:
                if key.startswith(p):
                    return db_type
        return "unknown"

    # openclaw.json databases array
    for db in config.get("databases", []):
        dbs.append({
            "type": db.get("type", db.get("engine", "unknown")),
            "host": db.get("host", db.get("url", "—" )),
            "port": db.get("port", "—" ),
            "name": db.get("name", db.get("database", "—" )),
            "auth": _mask(db.get("auth", db.get("user", "—" ))),
            "migratable": False,
            "note": "数据库连接配置必须在目标平台重新配置，禁止明文传输",
        })

    # .env database variables
    if os.path.exists(".env"):
        found_types = set()
        with open(".env", encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key = line.split("=", 1)[0]
                    db_type = db_type_from_key(key)
                    if db_type != "unknown" and db_type not in found_types:
                        found_types.add(db_type)
                        dbs.append({
                            "type": db_type,
                            "host": "（见 .env）",
                            "port": "（见 .env）",
                            "name": "（见 .env）",
                            "auth": "（见 .env）",
                            "migratable": False,
                            "note": f".env 中发现 {db_type.upper()} 变量（如 {key}），需重新配置连接",
                        })

    # supabase.json / database.json
    for fname in ["supabase.json", "database.json", "db_config.json"]:
        if os.path.exists(fname):
            data = _safe_read_json(fname)
            if data:
                ref_url = (data.get("projectUrl") or data.get("url") or
                          data.get("host") or data.get("connectionString", "—" ))
                dbs.append({
                    "type": "supabase" if "supabase" in fname else "external_db",
                    "host": ref_url,
                    "port": data.get("port", "—" ),
                    "name": data.get("name", data.get("database", "—" )),
                    "auth": _mask(data.get("apiKey", data.get("token", "—" ))),
                    "migratable": False,
                    "note": f"数据库配置在 {fname}，需在目标平台重新配置",
                })

    # Deduplicate
    seen = set()
    deduped = []
    for db in dbs:
        key = (db["type"], db.get("host", ""))
        if key not in seen:
            seen.add(key)
            deduped.append(db)
    return deduped


def scan_extended_components():
    """
    Scan for sub-agents, MCP servers, and external databases.
    Returns a dict with 'subagents', 'mcp_servers', 'databases' keys.
    """
    result = {"subagents": [], "mcp_servers": [], "databases": [], "warnings": []}
    config = {}

    # Load openclaw.json if exists
    if os.path.exists("openclaw.json"):
        config = _safe_read_json("openclaw.json") or {}
    elif os.path.exists("config.json"):
        config = _safe_read_json("config.json") or {}

    if not config:
        result["warnings"].append("未找到配置文件 (openclaw.json/config.json)，无法检测扩展组件")

    result["subagents"] = _detect_subagents(config)
    result["mcp_servers"] = _detect_mcp_servers(config)
    result["databases"] = _detect_external_databases(config)

    # Summary warnings
    if result["subagents"]:
        result["warnings"].append(
            f"检测到 {len(result['subagents'])} 个子代理配置，迁移时需确认目标平台支持对应的 runtime 类型"
        )
    if result["mcp_servers"]:
        result["warnings"].append(
            f"检测到 {len(result['mcp_servers'])} 个 MCP Server 连接，这些配置无法直接迁移，必须在目标平台重新注册"
        )
    if result["databases"]:
        result["warnings"].append(
            f"检测到 {len(result['databases'])} 个外挂数据库连接，必须在目标平台重新配置连接，禁止传输凭证"
        )

    return result


# ============================================================================
# Core Scanner
# ============================================================================

def platform_diff(source, target):
    """Analyze compatibility between source and target platforms."""
    compat = PLATFORM_COMPAT.get((source, target), {
        "can_direct": False,
        "needs_conversion": True,
        "notes": "暂无预设迁移路径，需人工评估",
    })
    return {
        "source": source,
        "target": target,
        "can_direct_migrate": compat["can_direct"],
        "needs_conversion": compat["needs_conversion"],
        "notes": compat["notes"],
        "dimensions": _diff_dimensions(source, target),
    }


def _pf(p):
    return {
        "openclaw": "JSON5/JSON",
        "cherrybot": "Python",
        "dify": "YAML+Docker",
        "anythingllm": "JSON",
        "autogen": "YAML/Python",
        "coze": "JSON"
    }.get(p, "—" )


def _pc(p):
    return {
        "openclaw": "多渠道（飞书/Telegram/Discord等）",
        "cherrybot": "仅飞书",
        "dify": "REST API",
        "anythingllm": "Web UI",
        "autogen": "代码内置",
        "coze": "多渠道（飞书/微信/Discord等）"
    }.get(p, "—" )


def _ps(p):
    return {
        "openclaw": "skills/ 目录（Markdown）",
        "cherrybot": "Python 脚本",
        "dify": "Dify 工作流/应用",
        "anythingllm": "内置",
        "autogen": "Python 类",
        "coze": "Coze Bot 插件"
    }.get(p, "—" )


def _same(s, t):
    return s == t


def _diff_dimensions(source, target):
    return [
        ("配置格式", _pf(source), _pf(target), _same(source, target)),
        ("渠道接入", _pc(source), _pc(target), _same(source, target)),
        ("技能系统", _ps(source), _ps(target), True),
        ("记忆机制", "memory/*.md", "memory/*.md", _same(source, target)),
        ("子代理/MCP", "视配置而定", "视目标平台而定", True),
        ("外挂数据库", "视配置而定", "视目标平台而定", False),
        ("凭证存储", ".env / credentials", ".env / credentials", False),
        ("运行环境", {
            "openclaw": "Node.js 18+",
            "cherrybot": "Python 3.9+",
            "dify": "Docker",
            "anythingllm": "Node.js + Python",
            "autogen": "Python 3.10+",
            "coze": "云端（无需自托管）"
        }.get(source, "—"),
        {
            "openclaw": "Node.js 18+",
            "cherrybot": "Python 3.9+",
            "dify": "Docker",
            "anythingllm": "Node.js + Python",
            "autogen": "Python 3.10+",
            "coze": "云端（无需自托管）"
        }.get(target, "—"),
        True),
    ]


def scan_openclaw(path="."):
    """Scan OpenClaw platform configuration."""
    results = {
        "platform": "OpenClaw",
        "scan_path": str(Path(path).resolve()),
        "timestamp": datetime.now().isoformat(),
        "files": [],
        "dirs": [],
        "warnings": [],
        "migration_category": {},
    }
    orig_cwd = os.getcwd()
    if path != ".":
        os.chdir(path)
    try:
        # Main config file
        if os.path.exists("openclaw.json"):
            config = _safe_read_json("openclaw.json")
            if config:
                results["files"].append({
                    "path": "openclaw.json",
                    "required": True,
                    "type": "config",
                    "purpose": "核心配置",
                    "size": os.path.getsize("openclaw.json"),
                    "has_secrets": _check_secrets(config),
                })
                results["migration_category"]["openclaw.json"] = "需转换"
            else:
                results["warnings"].append("openclaw.json 解析失败，请手动检查")

        # Environment file
        if os.path.exists(".env"):
            results["files"].append({
                "path": ".env",
                "required": True,
                "type": "secrets",
                "purpose": "环境变量/API密钥",
                "size": os.path.getsize(".env"),
                "secrets_found": _scan_env_secrets(".env"),
            })
            results["migration_category"][".env"] = "需重建"
            results["warnings"].append(".env 包含敏感信息，必须在目标平台重新配置")

        # Skills directory
        if os.path.exists("skills/"):
            for item in sorted(os.listdir("skills/")):
                ipath = os.path.join("skills/", item)
                if os.path.isdir(ipath):
                    results["dirs"].append({
                        "path": f"skills/{item}/",
                        "required": True,
                        "type": "skill",
                        "purpose": f"技能包: {item}",
                    })
                    results["migration_category"][f"skills/{item}/"] = "需转换"

        # Memory files
        if os.path.exists("memory/"):
            for f in sorted(os.listdir("memory/")):
                if f.endswith(".md"):
                    results["files"].append({
                        "path": f"memory/{f}",
                        "required": True,
                        "type": "memory",
                        "purpose": "记忆文件",
                    })
                    results["migration_category"][f"memory/{f}"] = "可迁移"

        # Identity files
        for f in ["SOUL.md", "USER.md", "IDENTITY.md", "AGENTS.md", "HEARTBEAT.md"]:
            if os.path.exists(f):
                results["files"].append({
                    "path": f,
                    "required": False,
                    "type": "config",
                    "purpose": "智能体配置文件",
                })
                results["migration_category"][f] = "可迁移"

        # Channel and credentials files
        for f in ["channels.yaml", "channels.json", "credentials.json"]:
            if os.path.exists(f):
                results["files"].append({
                    "path": f,
                    "required": False,
                    "type": "config",
                    "purpose": "渠道配置",
                })
                results["migration_category"][f] = "需重建"

    finally:
        if path != ".":
            os.chdir(orig_cwd)
    return results


def _check_secrets(config):
    """Check for secret fields in configuration."""
    secret_fields = ["apiKey", "api_key", "token", "secret", "password", "credential", "auth"]
    found = []

    def check(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(s in k.lower() for s in secret_fields):
                    found.append(k)
                check(v)
        elif isinstance(obj, list):
            for item in obj:
                check(item)

    check(config)
    return found


def _scan_env_secrets(env_path):
    """Scan .env file for key names (not values)."""
    secrets = []
    with open(env_path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0]
                secrets.append(key)
    return secrets


# ============================================================================
# Report Generation Helpers
# ============================================================================

def _file_table(items):
    if not items:
        return "| — | — | — | — | — |\n"
    rows = ""
    for f in items:
        notes = ""
        if f.get("secrets_found"):
            notes = "⚠️ 敏感字段: " + ", ".join(f["secrets_found"][:3])
        elif f.get("has_secrets"):
            notes = "⚠️ 含敏感字段: " + ", ".join(f["has_secrets"][:3])
        rows += "| `{}` | {} | {} | {} | {} |\n".format(
            f["path"],
            "是" if f.get("required") else "否",
            f.get("type", "—"),
            f.get("purpose", "—"),
            notes
        )
    return rows


def _diff_table(diff_results):
    rows = ""
    for dim in diff_results.get("dimensions", []):
        name, src, tgt, diff = dim
        status = "⚠️ 需调整" if not diff else "✅ 相同"
        rows += "| {} | {} | {} | {} |\n".format(name, src, tgt, status)
    return rows


def _subagent_table(subagents):
    if not subagents:
        return "| — | — | — | — |\n"
    rows = ""
    for a in subagents:
        rows += "| {} | {} | {} | {} |\n".format(
            a.get("name", "—"),
            a.get("type", "—"),
            a.get("model", "—"),
            a.get("notes", "—")
        )
    return rows


def _mcp_table(servers):
    if not servers:
        return "| — | — | — |\n"
    rows = ""
    for s in servers:
        rows += "| {} | {} | {} |\n".format(
            s.get("name", "—"),
            s.get("url", "—"),
            s.get("note", "—")
        )
    return rows


def _db_table(dbs):
    if not dbs:
        return "| — | — | — |\n"
    rows = ""
    for db in dbs:
        rows += "| {} | {} | {} |\n".format(
            db.get("type", "—").upper(),
            db.get("host", "—"),
            db.get("note", "—")
        )
    return rows


def _skip_table():
    return """| `openclaw.log` | 平台运行时生成，无需迁移 |
| `__pycache__/` | Python 缓存，无需迁移 |
| `.git/` | Git 版本控制，应使用 Git 迁移 |
| `*.tmp` | 临时文件，无需迁移 |
| `*.log` | 日志文件，无需迁移 |
"""


def generate_migration_plan(source_results, diff_results, ext_results, target_platform="未知"):
    """Generate complete migration plan document."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    source_platform = source_results.get("platform", "未知")
    cat = source_results.get("migration_category", {})

    can_migrate, needs_conv, needs_rebuild = [], [], []
    for f in source_results.get("files", []) + source_results.get("dirs", []):
        path = f["path"]
        c = cat.get(path, "")
        if "可迁移" in c:
            can_migrate.append(f)
        elif "需转换" in c:
            needs_conv.append(f)
        elif "需重建" in c:
            needs_rebuild.append(f)
        else:
            if f.get("type") == "memory" or path in ["SOUL.md", "USER.md", "IDENTITY.md"]:
                can_migrate.append(f)
            elif f.get("type") == "secrets":
                needs_rebuild.append(f)
            else:
                needs_conv.append(f)

    # Risk assessment
    risk = "🟢 低"
    if needs_rebuild or ext_results.get("mcp_servers") or ext_results.get("databases"):
        risk = "🟡 中"
    if ext_results.get("databases") and len(ext_results["databases"]) > 2:
        risk = "🔴 高（存在多个外挂数据库迁移风险）"

    # Build document
    plan = ""
    plan += "# 智能体迁移方案\n\n"
    plan += "> **生成时间:** {}  \n".format(timestamp)
    plan += "> **源平台:** {}  \n".format(source_platform)
    plan += "> **目标平台:** {}  \n".format(target_platform)
    plan += "> **风险等级:** {}\n\n".format(risk)
    plan += "---\n\n"

    # Executive Summary
    plan += "## 📋 执行摘要\n\n"
    plan += "| 项目 | 内容 |\n|------|------|\n"
    plan += "| 源平台 | {} |\n".format(source_platform)
    plan += "| 目标平台 | {} |\n".format(target_platform)
    plan += "| 扫描路径 | `{}` |\n".format(source_results.get("scan_path", "."))
    plan += "| 发现文件 | {} 个 |\n".format(len(source_results.get("files", [])))
    plan += "| 发现目录 | {} 个 |\n".format(len(source_results.get("dirs", [])))
    plan += "| 子代理 | {} 个 |\n".format(len(ext_results.get("subagents", [])))
    plan += "| MCP Server | {} 个 |\n".format(len(ext_results.get("mcp_servers", [])))
    plan += "| 外挂数据库 | {} 个 |\n".format(len(ext_results.get("databases", [])))
    plan += "| 风险等级 | {} |\n\n".format(risk)
    plan += "**迁移可行性结论:** {}\n\n".format(diff_results.get("notes", "请参考平台差异分析"))

    # Platform Diff Analysis
    plan += "---\n\n"
    plan += "## 🔍 平台差异分析\n\n"
    plan += "| 维度 | 源平台 | 目标平台 | 状态 |\n"
    plan += "|------|--------|----------|------|\n"
    plan += _diff_table(diff_results)
    plan += "\n> 💡 **说明:** \"⚠️ 需调整\" 意味着两个平台间存在差异，迁移时需要特别处理。\n\n"

    # Extended Components
    subagents = ext_results.get("subagents", [])
    mcp_srvs = ext_results.get("mcp_servers", [])
    databases = ext_results.get("databases", [])

    if subagents or mcp_srvs or databases:
        plan += "---\n\n"
        plan += "## 🔌 扩展组件检测\n\n"

        # Subagents
        plan += "### 🤖 子代理配置（{} 个）\n\n".format(len(subagents))
        plan += "| 名称 | 运行时类型 | 模型 | 来源 |\n"
        plan += "|------|-----------|------|------|\n"
        plan += _subagent_table(subagents)
        if subagents:
            plan += "\n".join([
                "- **{}:** 类型=`{}`，模型=`{}`，来源=`{}`".format(
                    a.get("name", "—"), a.get("type", "—"),
                    a.get("model", "—"), a.get("notes", "—"))
                for a in subagents
            ]) + "\n"
            plan += "\n> ⚠️ **子代理迁移说明:** 不同平台的 subagent runtime 不兼容。\n"
            plan += "> 建议：在目标平台重新创建子代理定义，参考上述表格中的 `model` 和 `prompt` 字段。\n\n"

        # MCP Servers
        plan += "### 🔗 MCP Server 连接（{} 个）\n\n".format(len(mcp_srvs))
        plan += "| 名称 | 连接地址 | 迁移说明 |\n"
        plan += "|------|----------|----------|\n"
        plan += _mcp_table(mcp_srvs)
        if mcp_srvs:
            plan += "\n> ⚠️ **MCP Server 迁移规则（强制）：**\n"
            plan += "> 1. MCP Server 连接地址（URL）和 Token **禁止直接传输**\n"
            plan += "> 2. 必须在目标平台逐个重新注册 MCP Server\n"
            plan += "> 3. 如 MCP Server 部署在本地，确认目标平台服务器网络可达\n\n"

        # Databases
        plan += "### 🗄️ 外挂数据库（{} 个）\n\n".format(len(databases))
        plan += "| 数据库类型 | 连接地址 | 迁移说明 |\n"
        plan += "|-----------|----------|----------|\n"
        plan += _db_table(databases)
        if databases:
            plan += "\n> ⚠️ **外挂数据库迁移规则（强制）：**\n"
            plan += "> 1. 所有数据库连接信息 **禁止明文传输**，必须在目标平台重新配置\n"
            plan += "> 2. Supabase: 重新创建项目，导出/导入数据后更新 .env\n"
            plan += "> 3. PostgreSQL/MySQL: 确认网络可达后更新连接字符串\n\n"

    # File Migration List
    plan += "---\n\n"
    plan += "## 📁 文件迁移清单\n\n"

    # Can Migrate
    plan += "### ✅ 可迁移文件（直接复制可用）\n\n"
    plan += "| 文件路径 | 必需 | 类型 | 用途 | 备注 |\n"
    plan += "|----------|------|------|------|------|\n"
    plan += _file_table(can_migrate)
    if can_migrate:
        plan += "\n**直接复制命令:**\n```bash\n"
        for f in can_migrate:
            plan += f"cp -r {f['path']} /目标路径/\n"
        plan += "```\n"

    # Needs Conversion
    plan += "### 🔁 需转换文件（格式/语法需调整）\n\n"
    plan += "| 文件路径 | 必需 | 类型 | 用途 | 备注 |\n"
    plan += "|----------|------|------|------|------|\n"
    plan += _file_table(needs_conv)
    if needs_conv:
        plan += "\n> 💡 复制后需对照目标平台文档调整配置格式。\n"

    # Needs Rebuild
    plan += "### 🔧 需重建文件（无法迁移，必须重新配置）\n\n"
    plan += "| 文件路径 | 必需 | 类型 | 用途 | 备注 |\n"
    plan += "|----------|------|------|------|------|\n"
    plan += _file_table(needs_rebuild)
    plan += "\n> ⚠️ 这些文件包含敏感信息，禁止直接传输！\n"

    # Can Skip
    plan += "### ⏭️ 可跳过文件\n\n"
    plan += "| 文件 | 原因 |\n"
    plan += "|------|------|\n"
    plan += _skip_table()

    # Migration Phases
    plan += "---\n\n"
    plan += "## 📝 分步迁移指南\n\n"

    # Phase 1: Preparation
    plan += "### Phase 1: 准备阶段\n\n"
    plan += "1. **备份当前配置**\n"
    plan += "   ```bash\n"
    plan += "   tar -czf backup-{}.tar.gz /path/to/agent-config/\n".format(datetime.now().strftime("%Y%m%d"))
    plan += "   ```\n\n"
    plan += "2. **导出敏感信息清单**（不导出值，只记录字段名）\n"
    plan += "   ```bash\n"
    plan += "   grep -E '^[A-Z]' .env | cut -d= -f1 > env-fields.txt\n"
    plan += "   ```\n\n"
    plan += "3. **确认目标平台环境**\n"
    plan += "   - Node.js/Python 版本要求\n"
    plan += "   - 网络连通性（数据库、MCP Server）\n"
    plan += "   - 渠道 Webhook URL 准备\n\n"

    # Phase 2: Migration
    plan += "### Phase 2: 迁移阶段\n\n"
    plan += "1. **复制可迁移文件**\n"
    for f in can_migrate:
        plan += f"   ```bash\n   cp -r {f['path']} /目标路径/\n   ```\n"
    plan += "\n2. **转换配置文件**\n"
    plan += "   - 参照平台差异分析，调整配置格式\n"
    plan += "   - 更新渠道、插件等平台特定字段\n\n"
    plan += "3. **重建敏感配置**\n"
    plan += "   - 在目标平台后台重新填写 API Key、Token\n"
    plan += "   - 重新注册 MCP Server\n"
    plan += "   - 重新配置数据库连接\n\n"

    # Phase 3: Verification
    plan += "### Phase 3: 验证阶段\n\n"
    plan += "- [ ] 核心配置加载正常（无报错）\n"
    plan += "- [ ] 渠道机器人响应消息\n"
    plan += "- [ ] 记忆数据正常读取\n"
    plan += "- [ ] 技能包加载正常\n"
    plan += "- [ ] 子代理功能正常（如有）\n"
    plan += "- [ ] MCP Server 连接正常（如有多）\n"
    plan += "- [ ] 数据库连接正常（如有多）\n"
    plan += "- [ ] 日志无 ERROR\n\n"

    # Verification Checklist
    plan += "---\n\n"
    plan += "## ✅ 迁移后校验清单\n\n"
    plan += "| 检查项 | 状态 | 备注 |\n"
    plan += "|--------|------|------|\n"
    plan += "| 核心配置加载 | ⬜ 未检查 | |\n"
    plan += "| 渠道机器人响应 | ⬜ 未检查 | |\n"
    plan += "| 记忆数据读取 | ⬜ 未检查 | |\n"
    plan += "| 技能包加载 | ⬜ 未检查 | |\n"
    if subagents:
        plan += "| 子代理运行 | ⬜ 未检查 | |\n"
    if mcp_srvs:
        plan += f"| MCP Server 连接 | ⬜ 未检查 | 共 {len(mcp_srvs)} 个 |\n"
    if databases:
        plan += f"| 数据库连接 | ⬜ 未检查 | 共 {len(databases)} 个 |\n"
    plan += "| 日志无 ERROR | ⬜ 未检查 | |\n\n"

    # Warnings
    if ext_results.get("warnings"):
        plan += "---\n\n"
        plan += "## ⚠️ 重要警告\n\n"
        for w in ext_results["warnings"]:
            plan += f"- {w}\n"
        plan += "\n"

    plan += "---\n\n"
    plan += f"*此文档由 Agent Migrator Scanner v{__version__} 自动生成*\n"

    return plan


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Agent Migrator Scanner — 智能体迁移分析器（含子代理/MCP/数据库检测）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scanner.py --source openclaw --target coze
  python3 scanner.py --source openclaw --target dify --path /home/user/agent
  python3 scanner.py --source openclaw --target openclaw --path . --output migration.md
        """
    )
    parser.add_argument("--source", default="openclaw", choices=list(PLATFORMS.keys()),
                        help="源平台类型")
    parser.add_argument("--path", default=".", help="扫描路径（默认当前目录）")
    parser.add_argument("--target", required=True, help="目标平台名称（必填！）")
    parser.add_argument("--output", help="输出 Markdown 文件路径")
    parser.add_argument("--auto-detect", action="store_true",
                        help="自动检测源平台（覆盖 --source）")

    args = parser.parse_args()

    # Auto-detect platform if requested
    if args.auto_detect:
        detected = _detect_platform(args.path)
        if detected:
            args.source = detected
            print(f"[Agent Migrator] 自动检测到源平台: {detected}")
        else:
            print("[Agent Migrator] 警告: 无法自动检测平台，使用默认: openclaw")

    print("[Agent Migrator] 扫描源平台: {} -> 目标平台: {}".format(args.source, args.target))

    # Scan source platform
    scan_results = scan_openclaw(args.path)

    # Platform diff analysis
    diff_results = platform_diff(args.source, args.target)

    # Detect extended components
    print("[Agent Migrator] 检测子代理、MCP Server、外挂数据库...")
    orig_cwd = os.getcwd()
    if args.path != ".":
        os.chdir(args.path)
    try:
        ext_results = scan_extended_components()
    finally:
        if args.path != ".":
            os.chdir(orig_cwd)

    # Print warnings
    for w in scan_results.get("warnings", []) + ext_results.get("warnings", []):
        print(f"[Agent Migrator] ⚠️ {w}")

    # Generate migration plan
    print("[Agent Migrator] 生成迁移文档...")
    plan = generate_migration_plan(scan_results, diff_results, ext_results, args.target)

    # Output files
    output_path = args.output or "/workspace/migration-plan-{}.md".format(
        datetime.now().strftime("%Y%m%d-%H%M%S")
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(plan)
    print(f"[Agent Migrator] 已保存: {output_path}")

    # Generate summary JSON
    summary = {
        "version": __version__,
        "source_platform": args.source,
        "target_platform": args.target,
        "timestamp": datetime.now().isoformat(),
        "scan_path": scan_results.get("scan_path", args.path),
        "files_found": len(scan_results.get("files", [])),
        "dirs_found": len(scan_results.get("dirs", [])),
        "subagents": ext_results.get("subagents", []),
        "mcp_servers": ext_results.get("mcp_servers", []),
        "databases": ext_results.get("databases", []),
        "warnings": scan_results.get("warnings", []) + ext_results.get("warnings", []),
        "risk_level": "🟢 低" if not ext_results.get("mcp_servers") and not ext_results.get("databases")
                      else "🟡 中" if not (ext_results.get("databases") and len(ext_results["databases"]) > 2)
                      else "🔴 高",
    }
    with open(output_path.replace(".md", "-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[Agent Migrator] 摘要已保存: {output_path.replace('.md', '-summary.json')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
