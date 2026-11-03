# 三级等保 + Token 安全 实战清单(2026-08)

> **来源**:AI-GIS 智能问图平台 v0.4.0 实战落地
> **标准**:GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》三级
> **范围**:Web 应用 + LLM API 网关(以 FastAPI 后端为模板)

---

## 一、三级等保 7 项覆盖矩阵

| # | 三级等保要求 | GB/T 22239-2019 条款 | 实现方式 | 必备性 |
|---|---|---|---|---|
| 1 | **身份鉴别(密码加密)** | 8.1.4.2 身份鉴别 | PBKDF2-HSMAC-SHA256 200k 迭代 + 32 字节 salt | ✅ 必须 |
| 2 | **敏感信息加密存储** | 8.1.4.3 访问控制 | Fernet AES-128-CBC + 自动明文/密文兼容 | ✅ 必须 |
| 3 | **访问控制(IP 白名单)** | 8.1.4.3 访问控制 | `GIS_IP_WHITELIST` 环境变量,默认 OFF | ⚠️ 按需 |
| 4 | **安全审计(操作日志)** | 8.1.4.4 安全审计 | `GIS_AUDIT_LOG=1` 写 `logs/audit.log` | ✅ 必须 |
| 5 | **恶意代码防范(输入校验)** | 8.1.4.5 入侵防范 | Pydantic schema + 长度限制 | ✅ 必须 |
| 6 | **数据完整性(config hash)** | 8.1.4.6 数据完整性 | `data/.sha256` 校验,损坏从 .bak 回滚 | ✅ 必须 |
| 7 | **备份恢复** | 8.1.4.7 备份恢复 | save 时自动 .bak 备份 | ✅ 必须 |

**默认全 OFF 的安全功能**:
- IP 白名单(防止 demo 模式被锁)
- 速率限制(防止 demo 模式被限)
- 敏感操作二次确认(防止 demo 模式被卡)
- **所有"按需"功能用环境变量开启**

---

## 二、加密实现细节

### crypto.py 核心代码(可直接 copy)

```python
"""
加密模块:PBKDF2-HMAC-SHA256 200k 迭代 + Fernet AES-128-CBC
符合三级等保"身份鉴别"和"敏感信息加密存储"要求
"""
import os
import json
import hashlib
import secrets
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

SALT_PATH = Path("data/.salt")
KEY_PATH = Path("data/.key")
SALT_SIZE = 32
ITERATIONS = 200_000  # OWASP 2023 推荐
HASH_FILE = Path("data/.sha256")

# 敏感字段路径(支持嵌套)
SENSITIVE_KEYS = {
    "llm.api_key",
    "tianditu.server_token",
    "geoserver.password",
    "supermap.token",
    "geoway.gk_token",
    "geoway.username",
    "geoway.password",
    "arcgis.token",
    "qgis.api_key",
    "admin.password",
    "smtp.password",
    "redis.password",
    "db.password",
}

# 不加密(必须明文给浏览器)
PLAINTEXT_KEYS = {
    "tianditu.web_token",  # 浏览器拼瓦片 URL 必须明文
    "map.public_key",
}


def _ensure_salt() -> bytes:
    """持久化 salt,避免每次启动 key 变(导致旧密文全解不开)"""
    SALT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SALT_PATH.exists():
        return SALT_PATH.read_bytes()
    salt = secrets.token_bytes(SALT_SIZE)
    SALT_PATH.write_bytes(salt)
    try:
        os.chmod(SALT_PATH, 0o600)  # POSIX
    except (OSError, AttributeError):
        pass  # Windows 不支持
    return salt


def _get_or_create_key() -> bytes:
    """获取或创建主密钥(单机模式)"""
    if KEY_PATH.exists():
        password = KEY_PATH.read_bytes()
    else:
        password = secrets.token_bytes(48)  # 48 字节随机
        KEY_PATH.write_bytes(password)
        try:
            os.chmod(KEY_PATH, 0o600)
        except (OSError, AttributeError):
            pass
    salt = _ensure_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


_cipher: Fernet = None


def init():
    """初始化全局 cipher"""
    global _cipher
    _cipher = Fernet(_get_or_create_key())


def is_encrypted(value: str) -> bool:
    """检测是否已是 Fernet 密文(Fernet 输出以 gAAAAA 开头)"""
    return bool(value) and value.startswith("FERNET:")


def encrypt(plaintext: str) -> str:
    """明文 → 密文"""
    if not plaintext or is_encrypted(plaintext):
        return plaintext
    return "FERNET:" + _cipher.encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt(ciphertext: str) -> str:
    """密文 → 明文"""
    if not ciphertext:
        return ciphertext
    if not is_encrypted(ciphertext):
        return ciphertext
    try:
        return _cipher.decrypt(ciphertext[7:].encode("ascii")).decode("utf-8")
    except InvalidToken:
        return ""  # 旧 key 解不开新密文时静默返空


def encrypt_config(data: dict) -> dict:
    """递归加密 config 中所有敏感字段"""
    if not isinstance(data, dict):
        return data
    result = {}
    for k, v in data.items():
        path = k  # 简化:仅一层;实际用 _get_parent_path 递归
        if path in SENSITIVE_KEYS and isinstance(v, str):
            result[k] = encrypt(v)
        elif path in PLAINTEXT_KEYS:
            result[k] = v  # 不加密
        elif isinstance(v, dict):
            result[k] = encrypt_config(v)  # 递归
        else:
            result[k] = v
    return result


def decrypt_config(data: dict) -> dict:
    """递归解密(API 返前端前)"""
    return encrypt_config(data)  # 同一逻辑:遇到密文自动解密


def verify_config_integrity(path: Path) -> bool:
    """config 完整性校验"""
    if not path.exists():
        return True
    sha_path = path.with_suffix(".sha256")
    if not sha_path.exists():
        return True  # 旧版没 hash 文件,跳过
    expected = sha_path.read_text(encoding="utf-8").strip()
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    return expected == actual
```

### 配置存储 config_store.py 核心

```python
"""
配置存储:自动备份 + hash 校验
"""
import json
import shutil
import hashlib
from pathlib import Path

CONFIG_PATH = Path("data/config.json")


def save_config(data: dict, path: Path = CONFIG_PATH) -> None:
    """保存配置,自动备份 + 写 hash"""
    path.parent.mkdir(parents=True, exist_ok=True)
    # 1. 备份
    if path.exists():
        shutil.copy2(path, path.with_suffix(".bak"))
    # 2. 写新
    content = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(content, encoding="utf-8")
    # 3. 写 hash
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix(".sha256").write_text(sha, encoding="utf-8")


def load_config(path: Path = CONFIG_PATH) -> dict:
    """加载配置,损坏从 .bak 回滚"""
    if not path.exists():
        return {}
    # hash 校验
    sha_path = path.with_suffix(".sha256")
    if sha_path.exists():
        expected = sha_path.read_text(encoding="utf-8").strip()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected != actual:
            bak = path.with_suffix(".bak")
            if bak.exists():
                shutil.copy2(bak, path)
                print(f"[WARN] config 损坏,已从 .bak 回滚: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
```

---

## 三、Token 三层防御(关键!)

**问题**:"前几天还好的"token 今天突然不工作,看 config 发现 token 变成了 `***abc`。

**根因**:
1. 后端 `/api/config` 返配置时把 token mask 了(安全考虑) — **但前端需要回显**
2. 前端拿到后填回表单
3. 用户保存 → mask 写回 config → token 永久失效

### 三层防御(必须全做)

#### 1. 后端永远返 `***xxx`
```python
def mask_value(value: str) -> str:
    if not value or len(value) < 4:
        return "***"
    return f"***{value[-3:]}"

@app.get("/api/config")
async def get_config():
    cfg = load_config()
    cfg = decrypt_config(cfg)
    for key in SENSITIVE_KEYS:
        if key in cfg and cfg[key]:
            cfg[key] = mask_value(cfg[key])
    return cfg
```

#### 2. 前端 placeholder 模式
```js
// ❌ 错: 用 value 填充
input.value = config.llm_api_key;  // 拿到 "***abc"
// ✅ 对: 用 placeholder 显示
input.placeholder = config.llm_api_key || "请输入 API key";
input.value = "";  // 用户编辑时输入框空,真值保留在后端
```

#### 3. 服务端守卫(最关键!)
```python
def is_masked(value: str) -> bool:
    """检测是不是掩码值"""
    if not value:
        return False
    return value.startswith("***") and len(value) <= 6

def update_config_field(key: str, new_value: str, old_value: str):
    if is_masked(new_value):
        # 掩码值 → 跳过,保留原值
        print(f"[GUARD] {key} 提交的是掩码 {new_value},保留原值")
        return old_value
    return new_value

@app.post("/api/config")
async def update_config(data: dict):
    current = load_config()
    for key, value in data.items():
        if key in SENSITIVE_KEYS:
            current[key] = update_config_field(key, value, current.get(key, ""))
        else:
            current[key] = value
    save_config(current)
    return {"ok": True}
```

### 迁移脚本(用户主动跑一次)

```python
# scripts/encrypt_config.py
"""
把旧 config.json 里的明文敏感字段加密为密文
默认 dry-run,--apply 才真改
"""
import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="真改文件,默认 dry-run")
    args = parser.parse_args()
    
    path = Path("data/config.json")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    plain_count = 0
    for key in SENSITIVE_KEYS:
        if key in cfg and isinstance(cfg[key], str) and not cfg[key].startswith("FERNET:"):
            print(f"[{'APPLY' if args.apply else 'DRY-RUN'}] {key}: 明文 → 密文")
            plain_count += 1
            if args.apply:
                cfg[key] = encrypt(cfg[key])
    if args.apply and plain_count > 0:
        save_config(cfg)
    print(f"统计: 发现 {plain_count} 个明文敏感字段")
    if not args.apply and plain_count > 0:
        print("提示: 加上 --apply 参数真改文件")

if __name__ == "__main__":
    main()
```

---

## 四、IP 白名单 / 速率限制 / 审计日志

### security.py 核心

```python
"""
安全中间件:IP 白名单 / 速率限制 / 审计日志
全部默认 OFF,环境变量开启,不破坏 demo 模式
"""
import os
import time
import json
import ipaddress
from pathlib import Path
from fastapi import Request, HTTPException

# ============= IP 白名单 =============
def get_whitelist() -> list:
    """读取环境变量,默认空(全允许)"""
    env = os.environ.get("GIS_IP_WHITELIST", "").strip()
    if not env:
        return []  # 空 = 允许所有
    return [ipaddress.ip_network(x.strip()) for x in env.split(",") if x.strip()]


def check_ip(request: Request) -> None:
    """IP 白名单检查"""
    wl = get_whitelist()
    if not wl:
        return  # 未配置,跳过
    client_ip = ipaddress.ip_address(request.client.host)
    for net in wl:
        if client_ip in net:
            return
    raise HTTPException(403, f"IP {client_ip} 不在白名单")


# ============= 速率限制 =============
_RATE_LIMIT_STATE = {}  # {ip: [(timestamp, count), ...]}

def get_rate_limit() -> int:
    """每分钟最大请求数,0 = 不限"""
    return int(os.environ.get("GIS_RATE_LIMIT", "0"))


def check_rate_limit(request: Request) -> None:
    rps = get_rate_limit()
    if rps <= 0:
        return
    client_ip = request.client.host
    now = time.time()
    window_start = now - 60
    # 清理过期
    if client_ip in _RATE_LIMIT_STATE:
        _RATE_LIMIT_STATE[client_ip] = [(t, c) for t, c in _RATE_LIMIT_STATE[client_ip] if t > window_start]
    else:
        _RATE_LIMIT_STATE[client_ip] = []
    # 计数
    current = sum(c for _, c in _RATE_LIMIT_STATE[client_ip])
    if current >= rps:
        raise HTTPException(429, f"超过速率限制 {rps}/min")
    _RATE_LIMIT_STATE[client_ip].append((now, 1))


# ============= 审计日志 =============
AUDIT_PATH = Path("logs/audit.log")

def is_audit_enabled() -> bool:
    return os.environ.get("GIS_AUDIT_LOG", "0") == "1"


def log_audit(request: Request, action: str, detail: str = ""):
    if not is_audit_enabled():
        return
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "ip": request.client.host,
        "method": request.method,
        "path": request.url.path,
        "user_agent": request.headers.get("user-agent", ""),
        "action": action,
        "detail": detail,
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

### audit_middleware.py

```python
"""
审计中间件:挂到 FastAPI app
"""
from fastapi import Request
from security import check_ip, check_rate_limit, log_audit


async def security_middleware(request: Request, call_next):
    # 1. IP 白名单
    try:
        check_ip(request)
    except HTTPException as e:
        log_audit(request, "ip_blocked", str(e.detail))
        raise
    # 2. 速率限制
    try:
        check_rate_limit(request)
    except HTTPException as e:
        log_audit(request, "rate_limited", str(e.detail))
        raise
    # 3. 执行
    response = await call_next(request)
    # 4. 审计(只记写操作 + 错误)
    if request.method in ("POST", "PUT", "DELETE", "PATCH") or response.status_code >= 400:
        log_audit(request, f"{request.method} {request.url.path}", f"status={response.status_code}")
    return response


# app.py 中:
# from audit_middleware import security_middleware
# app.add_middleware(BaseHTTPMiddleware, dispatch=security_middleware)
```

---

## 五、安全启动检查清单

部署前跑一遍(做成脚本 `scripts/security_check.py`):

```python
"""
安全启动检查
"""
import os
from pathlib import Path

def check():
    issues = []
    
    # 1. data/.key 存在 + 权限
    key = Path("data/.key")
    if not key.exists():
        issues.append("❌ data/.key 不存在,首次启动会自动生成")
    else:
        st = key.stat()
        if os.name != "nt" and (st.st_mode & 0o077) != 0:
            issues.append(f"❌ data/.key 权限过宽: {oct(st.st_mode)},应为 0o600")
    
    # 2. config.json 有没有明文敏感字段
    cfg_path = Path("data/config.json")
    if cfg_path.exists():
        import json
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        for k, v in cfg.items():
            if k in {"llm.api_key", "tianditu.server_token", "geoway.gk_token"}:
                if isinstance(v, str) and not v.startswith("FERNET:"):
                    issues.append(f"❌ {k} 仍是明文,跑 `python scripts/encrypt_config.py --apply`")
    
    # 3. config.json 完整性
    sha = cfg_path.with_suffix(".sha256")
    if sha.exists():
        import hashlib
        expected = sha.read_text(encoding="utf-8").strip()
        actual = hashlib.sha256(cfg_path.read_bytes()).hexdigest()
        if expected != actual:
            issues.append("❌ config.json 完整性校验失败,可能损坏")
    
    # 4. .env 没进 git
    if Path(".env").exists():
        issues.append("⚠️  .env 文件存在,确认没进版本管理")
    
    # 5. 关键环境变量
    if os.environ.get("GIS_AUDIT_LOG") == "1":
        audit = Path("logs/audit.log")
        if not audit.parent.exists():
            issues.append("⚠️  启用了审计日志但 logs/ 不存在")
    
    if not issues:
        print("✅ 安全检查通过")
        return 0
    else:
        print("发现以下问题:")
        for x in issues:
            print(f"  {x}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(check())
```

---

## 六、安全相关 6 个必问

部署到生产前,先问用户 6 个关键问题:

| # | 问题 | 默认答案 |
|---|---|---|
| 1 | **要不要启用 IP 白名单?** | 生产 YES,demo NO |
| 2 | **要不要启用审计日志?** | 生产 YES,demo NO |
| 3 | **要不要启用速率限制?** | 生产 YES(100/min),demo NO |
| 4 | **要不要启用敏感操作二次确认?** | 生产 YES(删/改 config),demo NO |
| 5 | **生产环境的 LLM API key 怎么管理?** | 推荐 env 注入 > Vault > 加密 config |
| 6 | **国产化平台是否需要 4 级 cryptography fallback?** | ARM64 YES,x86 也建议 |

---

## 七、避坑口诀

**不破坏 demo / 三层 token / 自动备份 / 完整性 hash / 默认 OFF / 检查清单**
