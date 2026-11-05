"""
FastAPI 安全中间件 + 加密配置 完整模板
三级等保 7 项覆盖,直接 copy 到项目用
"""
import os
import json
import time
import hashlib
import secrets
import ipaddress
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

# === 加密(cryptography) ===
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# ============================================================
# 一、加密模块
# ============================================================
SALT_PATH = Path("data/.salt")
KEY_PATH = Path("data/.key")
ITERATIONS = 200_000

SENSITIVE_KEYS = {
    "llm.api_key", "tianditu.server_token", "geoserver.password",
    "supermap.token", "geoway.gk_token", "geoway.username", "geoway.password",
    "arcgis.token", "qgis.api_key", "admin.password",
    "smtp.password", "redis.password", "db.password",
}
PLAINTEXT_KEYS = {"tianditu.web_token"}


def _ensure_salt() -> bytes:
    SALT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SALT_PATH.exists():
        return SALT_PATH.read_bytes()
    salt = secrets.token_bytes(32)
    SALT_PATH.write_bytes(salt)
    try: os.chmod(SALT_PATH, 0o600)
    except (OSError, AttributeError): pass
    return salt


def _get_or_create_key() -> bytes:
    if KEY_PATH.exists():
        password = KEY_PATH.read_bytes()
    else:
        password = secrets.token_bytes(48)
        KEY_PATH.write_bytes(password)
        try: os.chmod(KEY_PATH, 0o600)
        except (OSError, AttributeError): pass
    salt = _ensure_salt()
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(password))


_cipher: Optional[Fernet] = None


def crypto_init():
    """应用启动时调一次"""
    global _cipher
    _cipher = Fernet(_get_or_create_key())


def is_encrypted(value: str) -> bool:
    return bool(value) and value.startswith("FERNET:")


def encrypt(plaintext: str) -> str:
    if not plaintext or is_encrypted(plaintext):
        return plaintext
    return "FERNET:" + _cipher.encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt(ciphertext: str) -> str:
    if not ciphertext or not is_encrypted(ciphertext):
        return ciphertext
    try:
        return _cipher.decrypt(ciphertext[7:].encode("ascii")).decode("utf-8")
    except InvalidToken:
        return ""


def encrypt_config(data: dict) -> dict:
    """递归加密"""
    if not isinstance(data, dict):
        return data
    result = {}
    for k, v in data.items():
        if k in SENSITIVE_KEYS and isinstance(v, str):
            result[k] = encrypt(v)
        elif k in PLAINTEXT_KEYS:
            result[k] = v
        elif isinstance(v, dict):
            result[k] = encrypt_config(v)
        else:
            result[k] = v
    return result


def decrypt_config(data: dict) -> dict:
    return encrypt_config(data)


def mask_value(value: str) -> str:
    if not value or len(value) < 4:
        return "***"
    return f"***{value[-3:]}"


def is_masked(value: str) -> bool:
    """掩码值检测,服务端守卫"""
    if not value:
        return False
    return value.startswith("***") and len(value) <= 6


# ============================================================
# 二、配置存储
# ============================================================
CONFIG_PATH = Path("data/config.json")


def save_config(data: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        shutil.copy2(CONFIG_PATH, CONFIG_PATH.with_suffix(".bak"))
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    sha = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
    CONFIG_PATH.with_suffix(".sha256").write_text(sha, encoding="utf-8")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    sha_path = CONFIG_PATH.with_suffix(".sha256")
    if sha_path.exists():
        expected = sha_path.read_text(encoding="utf-8").strip()
        actual = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
        if expected != actual:
            bak = CONFIG_PATH.with_suffix(".bak")
            if bak.exists():
                shutil.copy2(bak, CONFIG_PATH)
                print(f"[WARN] config 损坏,已从 .bak 回滚")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


# ============================================================
# 三、IP 白名单 / 速率限制 / 审计
# ============================================================
def get_whitelist() -> list:
    env = os.environ.get("GIS_IP_WHITELIST", "").strip()
    if not env:
        return []
    return [ipaddress.ip_network(x.strip()) for x in env.split(",") if x.strip()]


def check_ip(request: Request):
    wl = get_whitelist()
    if not wl:
        return
    client_ip = ipaddress.ip_address(request.client.host)
    for net in wl:
        if client_ip in net:
            return
    raise HTTPException(403, f"IP {client_ip} 不在白名单")


_RATE_LIMIT_STATE = {}


def get_rate_limit() -> int:
    return int(os.environ.get("GIS_RATE_LIMIT", "0"))


def check_rate_limit(request: Request):
    rps = get_rate_limit()
    if rps <= 0:
        return
    client_ip = request.client.host
    now = time.time()
    window_start = now - 60
    if client_ip in _RATE_LIMIT_STATE:
        _RATE_LIMIT_STATE[client_ip] = [(t, c) for t, c in _RATE_LIMIT_STATE[client_ip] if t > window_start]
    else:
        _RATE_LIMIT_STATE[client_ip] = []
    current = sum(c for _, c in _RATE_LIMIT_STATE[client_ip])
    if current >= rps:
        raise HTTPException(429, f"超过速率限制 {rps}/min")
    _RATE_LIMIT_STATE[client_ip].append((now, 1))


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


# ============================================================
# 四、中间件
# ============================================================
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
    # 4. 审计(只记写 + 错误)
    if request.method in ("POST", "PUT", "DELETE", "PATCH") or response.status_code >= 400:
        log_audit(request, f"{request.method} {request.url.path}", f"status={response.status_code}")
    return response


# ============================================================
# 五、FastAPI app
# ============================================================
app = FastAPI(title="安全配置 API")
app.add_middleware(BaseHTTPMiddleware, dispatch=security_middleware)


@app.on_event("startup")
async def startup():
    crypto_init()


# === 模型 ===
class ConfigUpdate(BaseModel):
    """更新配置的请求体(部分字段)"""
    data: dict


# === 端点 ===
@app.get("/api/config")
async def get_config():
    """返配置,敏感字段 mask"""
    cfg = load_config()
    cfg = decrypt_config(cfg)  # 先解密
    # mask 敏感字段
    def _mask_recursive(d):
        if isinstance(d, dict):
            return {k: (mask_value(v) if k in SENSITIVE_KEYS and isinstance(v, str) else _mask_recursive(v)) for k, v in d.items()}
        return d
    return _mask_recursive(cfg)


@app.post("/api/config")
async def update_config(payload: ConfigUpdate):
    """更新配置,守卫掩码值"""
    current = load_config()
    current = decrypt_config(current)  # 先解
    
    def _update_recursive(target, source):
        for k, v in source.items():
            if k in SENSITIVE_KEYS and isinstance(v, str):
                # 守卫: 掩码值不写
                if is_masked(v):
                    print(f"[GUARD] {k} 提交的是掩码 {v},保留原值")
                    continue
                target[k] = v
            elif isinstance(v, dict):
                target.setdefault(k, {})
                _update_recursive(target[k], v)
            else:
                target[k] = v
    
    _update_recursive(current, payload.data)
    
    # 加密后存
    encrypted = encrypt_config(current)
    save_config(encrypted)
    return {"ok": True}


@app.get("/api/security/status")
async def security_status():
    """安全状态"""
    return {
        "encryption_enabled": _cipher is not None,
        "algorithm": "PBKDF2-HMAC-SHA256 + Fernet" if _cipher else "none",
        "iterations": ITERATIONS,
        "ip_whitelist": bool(get_whitelist()),
        "rate_limit": get_rate_limit() or "off",
        "audit_log": is_audit_enabled(),
    }
