#!/usr/bin/env python3
"""
数据源管理器
功能：添加/启用/测试/删除用户自定义数据源
支持类型：joinquant / tushare / custom_rest / tencent（腾讯）
用法:
  python3 source_manager.py --list                          # 列出所有数据源
  python3 source_manager.py --add joinquant               # 添加聚宽数据源
  python3 source_manager.py --test jq_001               # 测试指定数据源
  python3 source_manager.py --enable jq_001              # 启用数据源
  python3 source_manager.py --disable jq_001             # 禁用数据源
  python3 source_manager.py --remove jq_001             # 删除数据源
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from datetime import datetime

# =============================================================================
# 配置路径
# =============================================================================
CONFIG_DIR = os.path.expanduser("~/.openclaw/stock_sources")
CONFIG_FILE = os.path.join(CONFIG_DIR, "sources.json")
os.makedirs(CONFIG_DIR, exist_ok=True)

# =============================================================================
# 内置数据源（不可删除）
# =============================================================================
BUILTIN_SOURCES = {
    "tencent": {
        "id": "tencent",
        "name": "腾讯财经",
        "type": "tencent",
        "enabled": True,
        "priority": 1,
        "description": "A股主要数据源，速度快，准确率高",
        "test_codes": ["sh600519", "sz000858"],
    },
    "sina": {
        "id": "sina",
        "name": "新浪财经",
        "type": "sina",
        "enabled": False,
        "priority": 2,
        "description": "备用数据源，支持A股/港股",
        "test_codes": ["sh600519", "sz000858"],
    },
}

# =============================================================================
# 数据源配置模板（用户可添加的类型）
# =============================================================================
SOURCE_TEMPLATES = {
    "joinquant": {
        "name": "聚宽 JoinQuant",
        "description": "专业量化数据平台，数据全面准确",
        "config_fields": [
            {"key": "username", "label": "用户名/手机号", "required": True, "type": "string"},
            {"key": "password", "label": "密码", "required": True, "type": "password"},
        ],
        "test_fn": "test_joinquant",
        "env_prefix": "JQ",
        "install_cmd": "pip install jqdatasdk",
        "note": "注册地址：https://www.joinquant.com",
    },
    "tushare": {
        "name": "TuShare Pro",
        "description": "免费开源财经数据接口",
        "config_fields": [
            {"key": "token", "label": "API Token", "required": True, "type": "string"},
        ],
        "test_fn": "test_tushare",
        "env_prefix": "TUSHARE",
        "install_cmd": "pip install tushare",
        "note": "注册地址：https://tushare.pro",
    },
    "custom_rest": {
        "name": "自定义 REST API",
        "description": "接入您自己的行情API服务",
        "config_fields": [
            {"key": "url", "label": "API URL（{codes}占位符）", "required": True, "type": "string"},
            {"key": "auth_header", "label": "Authorization Header（可选）", "required": False, "type": "string"},
            {"key": "response_format", "label": "返回格式", "required": True,
             "type": "select", "options": ["tencent", "sina", "eastmoney", "custom"]},
        ],
        "test_fn": "test_custom_rest",
        "env_prefix": "CUSTOM_API",
        "install_cmd": None,
        "note": "URL示例：https://api.example.com/price?codes={codes}",
    },
}

# =============================================================================
# 配置读写
# =============================================================================

def load_config() -> dict:
    """加载用户数据源配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sources": [], "env_vars": {}}


def save_config(cfg: dict) -> None:
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_all_sources() -> List[dict]:
    """获取所有数据源（含内置）"""
    cfg = load_config()
    # 内置源永远在
    result = [v.copy() for v in BUILTIN_SOURCES.values()]
    # 用户源
    for s in cfg.get("sources", []):
        s_copy = s.copy()
        s_copy["is_builtin"] = False
        result.append(s_copy)
    # 按优先级排序
    result.sort(key=lambda x: x.get("priority", 99))
    return result


def get_enabled_sources() -> List[dict]:
    """获取已启用的数据源"""
    return [s for s in get_all_sources() if s.get("enabled", False)]


def find_source(source_id: str) -> Optional[dict]:
    """按ID查找数据源"""
    for s in get_all_sources():
        if s["id"] == source_id:
            return s
    return None


# =============================================================================
# 数据源测试函数
# =============================================================================

def test_tencent(codes: List[str] = None) -> dict:
    """测试腾讯财经"""
    codes = codes or ["sh600519"]
    q = ",".join(codes)
    url = f"http://qt.gtimg.cn/q={q}"
    try:
        req = urllib.request.Request(url, headers={"Referer": "https://finance.qq.com", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("gbk", errors="replace")
        lines = [l for l in raw.strip().split("\n") if l]
        if len(lines) >= len(codes):
            return {"ok": True, "count": len(lines), "latency_ms": 0}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "返回数据为空"}


def test_sina(codes: List[str] = None) -> dict:
    """测试新浪财经"""
    codes = codes or ["sh600519"]
    q = ",".join(codes)
    url = f"https://hq.sinajs.cn/list={q}"
    try:
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("gbk", errors="replace")
        lines = [l for l in raw.strip().split("\n") if l]
        ok_count = sum(1 for l in lines if "hq.sinajs.cn" not in l)
        return {"ok": True, "count": ok_count}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def test_joinquant(config: dict) -> dict:
    """测试聚宽"""
    try:
        import jqdatasdk as jq
        username = config.get("username", "").replace("${JQ_USERNAME}", "")
        password = config.get("password", "").replace("${JQ_PASSWORD}", "")
        jq.auth(username, password)
        df = jq.get_price("000001.XSHG", count=1, end_date=datetime.now())
        jq.logout()
        return {"ok": True, "sample": df.iloc[0]["close"]}
    except ImportError:
        return {"ok": False, "error": "jqdatasdk 未安装，运行：pip install jqdatasdk"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def test_tushare(config: dict) -> dict:
    """测试TuShare"""
    try:
        import tushare as ts
        token = config.get("token", "").replace("${TUSHARE_TOKEN}", "")
        if not token:
            return {"ok": False, "error": "Token未配置"}
        ts.set_token(token)
        pro = ts.pro_api()
        df = pro.daily(ts_code="000001.SZ", trade_date=datetime.now().strftime("%Y%m%d"))
        return {"ok": True, "count": len(df)}
    except ImportError:
        return {"ok": False, "error": "tushare 未安装，运行：pip install tushare"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def test_custom_rest(config: dict) -> dict:
    """测试自定义REST API"""
    url_tpl = config.get("url", "")
    codes = config.get("test_codes", ["sh600519"])
    if not url_tpl:
        return {"ok": False, "error": "URL未配置"}
    url = url_tpl.replace("{codes}", ",".join(codes))
    headers = {}
    auth = config.get("auth_header", "")
    if auth:
        auth = auth.replace("${API_KEY}", os.environ.get("CUSTOM_API_KEY", ""))
        if " " in auth:
            headers["Authorization"] = auth
        else:
            headers["X-API-Key"] = auth
    headers["User-Agent"] = "Mozilla/5.0"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        return {"ok": True, "raw_sample": raw[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def test_source(source_id: str) -> dict:
    """测试指定数据源"""
    src = find_source(source_id)
    if not src:
        return {"ok": False, "error": f"数据源 {source_id} 不存在"}

    test_fn_map = {
        "tencent": test_tencent,
        "sina": test_sina,
        "joinquant": lambda cfg: test_joinquant(cfg),
        "tushare": lambda cfg: test_tushare(cfg),
        "custom_rest": lambda cfg: test_custom_rest(cfg),
    }
    fn = test_fn_map.get(src["type"])
    if not fn:
        return {"ok": False, "error": f"未知类型: {src['type']}"}
    return fn(src.get("config", {}))


# =============================================================================
# 数据源管理操作
# =============================================================================

def add_source(source_type: str, name: str, config: dict, priority: int = 10) -> dict:
    """添加用户数据源"""
    template = SOURCE_TEMPLATES.get(source_type)
    if not template:
        return {"ok": False, "error": f"不支持的数据源类型：{source_type}，可用：{list(SOURCE_TEMPLATES.keys())}"}

    # 检查必填字段
    for field in template.get("config_fields", []):
        if field.get("required") and not config.get(field["key"]):
            return {"ok": False, "error": f"缺少必填字段：{field['label']}"}

    # 替换环境变量占位符
    env_prefix = template.get("env_prefix", "")
    if env_prefix:
        for k, v in config.items():
            if isinstance(v, str):
                env_key = f"{env_prefix}_{k.upper()}"
                # 存原始值（实际生产中应该加密）
                config[f"${env_prefix}_{k.upper()}"] = v

    source_id = f"user_{source_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    new_source = {
        "id": source_id,
        "name": name,
        "type": source_type,
        "enabled": False,
        "priority": priority,
        "config": config,
        "description": template["description"],
        "note": template.get("note", ""),
        "test_codes": ["sh600519"],
        "created_at": datetime.now().isoformat(),
    }
    cfg = load_config()
    cfg["sources"].append(new_source)
    save_config(cfg)
    return {"ok": True, "source": new_source}


def enable_source(source_id: str) -> dict:
    """启用数据源"""
    cfg = load_config()
    found = False
    for s in cfg["sources"]:
        if s["id"] == source_id:
            s["enabled"] = True
            found = True
            break
    if not found:
        return {"ok": False, "error": f"数据源 {source_id} 不存在"}
    save_config(cfg)
    return {"ok": True}


def disable_source(source_id: str) -> dict:
    """禁用数据源"""
    cfg = load_config()
    found = False
    for s in cfg["sources"]:
        if s["id"] == source_id:
            s["enabled"] = False
            found = True
            break
    if not found:
        return {"ok": False, "error": f"数据源 {source_id} 不存在"}
    save_config(cfg)
    return {"ok": True}


def remove_source(source_id: str) -> dict:
    """删除数据源"""
    if source_id in BUILTIN_SOURCES:
        return {"ok": False, "error": "内置数据源不可删除"}
    cfg = load_config()
    orig_len = len(cfg["sources"])
    cfg["sources"] = [s for s in cfg["sources"] if s["id"] != source_id]
    if len(cfg["sources"]) == orig_len:
        return {"ok": False, "error": f"数据源 {source_id} 不存在"}
    save_config(cfg)
    return {"ok": True}


def print_sources_table(sources: List[dict]) -> None:
    """打印数据源列表"""
    print(f"\n{'='*60}")
    print(f"📡 数据源管理")
    print(f"{'='*60}")
    print(f"  {'名称':<20}{'类型':<12}{'状态':<8}{'优先级':<6} 说明")
    print(f"  {'-'*60}")
    for s in sources:
        status = "✅启用" if s.get("enabled") else "❌禁用"
        builtin = "【内置】" if s.get("is_builtin") else "【用户】"
        print(f"  {builtin}{s['name']:<14}{s['type']:<12}{status:<8}{s.get('priority','-'):<6}{s.get('description','')}")
    print(f"  {'-'*60}")


def print_help() -> None:
    print(__doc__)


# =============================================================================
# 主入口
# =============================================================================

def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print_help()
        return

    if "--list" in args:
        sources = get_all_sources()
        print_sources_table(sources)
        return

    if "--add" in args:
        idx = args.index("--add")
        source_type = args[idx + 1] if idx + 1 < len(args) else None
        name_idx = args.index("--name") if "--name" in args else None
        name = args[name_idx + 1] if name_idx and name_idx + 1 < len(args) else f"{source_type}数据源"

        # 解析 --config 参数（key=value格式）
        config = {}
        for arg in args:
            if "=" in arg and not arg.startswith("-"):
                k, v = arg.split("=", 1)
                config[k] = v

        result = add_source(source_type, name, config)
        if result["ok"]:
            print(f"✅ 数据源添加成功：{result['source']['name']} (ID: {result['source']['id']})")
            print(f"   运行 --test {result['source']['id']} 测试")
        else:
            print(f"❌ 添加失败：{result['error']}")
        return

    if "--test" in args:
        idx = args.index("--test")
        source_id = args[idx + 1] if idx + 1 < len(args) else None
        if not source_id:
            print("❌ 请指定数据源ID")
            return
        print(f"🧪 测试数据源：{source_id}")
        result = test_source(source_id)
        if result["ok"]:
            print(f"✅ 测试通过！{result.get('count', result.get('sample', ''))}")
        else:
            print(f"❌ 测试失败：{result['error']}")
        return

    if "--enable" in args:
        idx = args.index("--enable")
        source_id = args[idx + 1]
        result = enable_source(source_id)
        print(f"✅ 启用" if result["ok"] else f"❌ {result['error']}")
        return

    if "--disable" in args:
        idx = args.index("--disable")
        source_id = args[idx + 1]
        result = disable_source(source_id)
        print(f"✅ 禁用" if result["ok"] else f"❌ {result['error']}")
        return

    if "--remove" in args:
        idx = args.index("--remove")
        source_id = args[idx + 1]
        result = remove_source(source_id)
        print(f"✅ 删除" if result["ok"] else f"❌ {result['error']}")
        return

    print_help()


if __name__ == "__main__":
    main()
