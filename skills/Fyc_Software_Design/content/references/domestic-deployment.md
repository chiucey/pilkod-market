# 国产化部署实战指南(2026-08)

> **来源**:AI-GIS 智能问图平台 v0.4.0 国产化适配实战
> **目标平台**:鲲鹏 ARM64 / 飞腾 ARM64 / 海光 x86_64 / 兆芯 x86_64 + 麒麟 V10 / UOS 1050 / openEuler
> **核心挑战**:cryptography 编译 / GLIBC 版本 / pip 源 / 国产 Python 发行版

---

## 一、国产化平台矩阵

| CPU 架构 | 操作系统 | Python 版本 | 关键差异 |
|---|---|---|---|
| **鲲鹏 920** (ARM64) | 麒麟 V10 SP3 / UOS 1050e | 3.8.5+ | cryptography 需 `*-manylinux2014_aarch64` |
| **飞腾 2000** (ARM64) | 银河麒麟 V10 | 3.8.5+ | 同上 |
| **海光 7285** (x86_64) | UOS 1050 / 麒麟 V10 | 3.8+ | 标准 wheel,无特殊处理 |
| **兆芯 KH-30000** (x86_64) | 麒麟 V10 | 3.8+ | 标准 wheel |
| 龙芯 3A5000 (LoongArch64) | 麒麟 V10 / Loongnix | 3.8+ (移植版) | 需 loongnix 源,部分包无预编译 wheel |
| 申威 1621 (SW_64) | 麒麟 V10 (军方) | 3.8+ (移植版) | 极少 wheel,大量本地编译 |

**最常见场景**:**鲲鹏 + 麒麟 V10** (政府/事业单位/国企标准配置)

---

## 二、4 级 cryptography Fallback

**问题**:ARM64 平台 cryptography 编译需要 glibc 2.28+,部分麒麟 V10 早期版本只有 2.23。

### 4 级 Fallback 实现

```python
"""
国产化 cryptography 4 级 fallback
"""
import sys, platform

def get_crypto_lib():
    """返回可用的加密库,4 级 fallback"""
    
    # 1 级: cryptography(首选,二进制 wheel 快)
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        return ("cryptography", Fernet, hashes, PBKDF2HMAC)
    except ImportError:
        pass
    
    # 2 级: pycryptodome(pure python 备选)
    try:
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Hash import SHA256, HMAC
        return ("pycryptodome", AES, PBKDF2, SHA256)
    except ImportError:
        pass
    
    # 3 级: hashlib + secrets(内置,只支持摘要不支持对称加密)
    try:
        import hashlib, secrets
        return ("hashlib", None, hashlib, None)
    except ImportError:
        pass  # 不会有这种情况
    
    # 4 级: 无加密(明文警告)
    return ("none", None, None, None)


def init():
    """初始化加密,选最佳可用方案"""
    name, *libs = get_crypto_lib()
    print(f"[CRYPTO] 使用加密库: {name}")
    print(f"[CRYPTO] Python: {sys.version.split()[0]}, 平台: {platform.platform()}")
    if name == "none":
        print("[WARN] 无加密库可用!敏感信息将以明文存储!")
        print("[WARN] 建议安装: pip install cryptography  (ARM64: manylinux2014_aarch64 版本)")
    return name
```

### ARM64 安装 cryptography(关键!)

```bash
# 方法 1: manylinux2014 wheel(优先)
pip install cryptography==41.0.7 \
  --only-binary=:all: \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 方法 2: 离线 wheel(国产化内网环境)
# 提前在能上网的机器下载:
pip download cryptography==41.0.7 \
  --dest ./wheels/ \
  --only-binary=:all: \
  --platform manylinux2014_aarch64 \
  --python-version 38 \
  --implementation cp

# 然后在内网:
pip install ./wheels/cryptography-41.0.7-cp38-cp38-manylinux2014_aarch64.whl

# 方法 3: 源码编译(慢,30-60s,需 gcc + libffi-devel + openssl-devel)
sudo yum install -y gcc libffi-devel openssl-devel python38-devel
pip install cryptography --no-binary cryptography
```

---

## 三、国产 pip 源(2026-08 推荐)

| 平台 | 源 | URL | 稳定性 |
|---|---|---|---|
| 通用 | 阿里云 | https://mirrors.aliyun.com/pypi/simple/ | ⭐⭐⭐⭐⭐ |
| 通用 | 清华 | https://pypi.tuna.tsinghua.edu.cn/simple/ | ⭐⭐⭐⭐ |
| 通用 | 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ | ⭐⭐⭐⭐ |
| 麒麟 | 麒麟官方 | https://mirrors.kylinos.cn/repository/pypi/simple/ | ⭐⭐⭐⭐ |
| UOS | 统信官方 | https://uos.packages.deepin.com/pypi/simple/ | ⭐⭐⭐ |
| **内网** | **本地 nexus** | **http://internal-nexus:8081/repository/pypi/simple/** | ⭐⭐⭐⭐⭐ |

### pip.conf 配置

```ini
# /etc/pip.conf (Linux 全局)
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 60

# 如果是内网环境
[global]
index-url = http://internal-nexus:8081/repository/pypi/simple/
trusted-host = internal-nexus
```

### requirements.txt 国产化版本锁定

```txt
# 基础
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# 国产化注意版本(避免 ABI 变化)
cryptography==41.0.7     # 41.x 兼容 manylinux2014, 42+ 需要 glibc 2.28
# ARM64 必备: --only-binary=:all:
```

---

## 四、Python 国产化版本选择

| 平台 | 推荐 Python | 备选 | 备注 |
|---|---|---|---|
| 麒麟 V10 SP3 | python3.8.5 (系统自带) | 3.9 / 3.10 | 选 3.8 兼容性最好 |
| UOS 1050 | python3.7 (系统) | 3.9 | 同上 |
| openEuler 22.03 | python3.9 / 3.11 | 3.10 | 标准 |
| Deepin V23 | python3.11 | 3.10 | 系统 3.11 |

### 跨平台代码 6 条铁律

1. **用 `pathlib.Path`, 不用 `os.path.join`**
```python
# ❌ 错
config_path = os.path.join("data", "config.json")
# ✅ 对
from pathlib import Path
config_path = Path("data") / "config.json"
```

2. **路径分隔符用 `/` 或 `Path`, 不用 `\\`**
```python
# ❌ 错
log = open("logs\\app.log", "a")
# ✅ 对
log = open(Path("logs") / "app.log", "a")
```

3. **文件权限用 try/except(chmod 在 Windows 会失败)**
```python
try:
    os.chmod(file, 0o600)
except (OSError, AttributeError):
    pass  # Windows
```

4. **进程调用用 `subprocess.run([...], shell=False)`(Windows/Linux 都安全)**
```python
# ❌ 错
subprocess.run(f"python {script}", shell=True)  # Windows/Linux 路径分隔符不同
# ✅ 对
subprocess.run([sys.executable, str(script)], shell=False)
```

5. **换行符不写死**(`\n` vs `\r\n`)
```python
# 用 io 模块,跨平台自动选
import io
with io.open(file, "w", newline="") as f:
    f.write(content)
```

6. **字体路径不写死**
```python
# ❌ 错
font_path = "C:\\Windows\\Fonts\\simhei.ttf"
# ✅ 对
import matplotlib.font_manager as fm
font = fm.findfont("SimHei")  # matplotlib 跨平台找字体
```

---

## 五、麒麟 V10 SP3 完整部署步骤(实战)

```bash
# ===== 1. 准备环境 =====
sudo yum update -y
sudo yum install -y python38 python38-pip python38-devel \
  gcc gcc-c++ make \
  libffi-devel openssl-devel \
  git wget

# ===== 2. 配置 pip 源 =====
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF

# ===== 3. 创建 venv =====
python3.8 -m venv .venv
source .venv/bin/activate

# ===== 4. ARM64 wheel 优先安装 cryptography =====
pip install --upgrade pip setuptools wheel
pip install cryptography==41.0.7 --only-binary=:all:

# ===== 5. 装其他依赖 =====
pip install -r requirements.txt

# ===== 6. 防火墙开端口 =====
sudo firewall-cmd --zone=public --add-port=7860/tcp --permanent
sudo firewall-cmd --reload

# ===== 7. SELinux 调整(可选) =====
# 如果报 Permission denied,临时关:
sudo setenforce 0
# 或永久允许 httpd 网络访问:
sudo setsebool -P httpd_can_network_connect 1

# ===== 8. systemd 服务 =====
sudo tee /etc/systemd/system/aigis.service << 'EOF'
[Unit]
Description=AI-GIS Smart Q&A Platform
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/aigis
Environment="PATH=/opt/aigis/.venv/bin"
Environment="GIS_AUDIT_LOG=1"
ExecStart=/opt/aigis/.venv/bin/pythonw /opt/aigis/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aigis
sudo systemctl start aigis
sudo systemctl status aigis
```

---

## 六、容器化(Docker)部署 - 跨平台

### Dockerfile(多阶段,支持 x86_64 + ARM64)

```dockerfile
# ===== 阶段 1: 构建依赖 =====
FROM python:3.11-slim AS builder

# ARM64 build tools
RUN apt-get update && apt-get install -y \
    gcc libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== 阶段 2: 运行时 =====
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV GIS_AUDIT_LOG=1
ENV PYTHONUNBUFFERED=1

EXPOSE 7860
CMD ["pythonw", "app.py"]
```

### docker-compose.yml(国产化镜像源)

```yaml
version: "3.8"
services:
  aigis:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - GIS_AUDIT_LOG=1
      - PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
    restart: unless-stopped
```

### .dockerignore

```
.venv/
__pycache__/
*.pyc
.git/
logs/*.log
data/.key
data/.salt
data/config.json
data/*.bak
```

### 多架构构建(关键!)

```bash
# 创建 buildx builder(支持 ARM64 + x86_64)
docker buildx create --name multiarch --use

# 构建多架构镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t aigis:v0.4.0 \
  --push \
  .
```

---

## 七、检测脚本(自动判断平台)

```python
# scripts/check_platform.py
"""
国产化平台检测 + 报告
"""
import platform
import sys
import os


def detect():
    info = {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "is_domestic": False,
        "is_arm": False,
        "warnings": [],
    }
    
    machine = platform.machine().lower()
    if machine in ("aarch64", "arm64"):
        info["is_arm"] = True
    
    # 检测国产 OS
    if os.path.exists("/etc/kylin-release"):
        info["is_domestic"] = True
        info["os_type"] = "kylin"
    elif os.path.exists("/etc/uos-release") or os.path.exists("/etc/deepin-version"):
        info["is_domestic"] = True
        info["os_type"] = "uos"
    elif os.path.exists("/etc/openEuler-release"):
        info["is_domestic"] = True
        info["os_type"] = "openEuler"
    
    # 检查 cryptography
    try:
        from cryptography.fernet import Fernet
        info["cryptography"] = "ok"
    except ImportError:
        info["cryptography"] = "missing"
        info["warnings"].append("cryptography 未安装,需 ARM64 wheel")
    
    # 检查 GLIBC
    if info["is_arm"] and info["system"] == "Linux":
        try:
            import subprocess
            r = subprocess.run(["ldd", "--version"], capture_output=True, text=True, timeout=5)
            version_line = r.stdout.splitlines()[0]
            if "2.17" in version_line or "2.18" in version_line or "2.19" in version_line \
               or "2.20" in version_line or "2.21" in version_line or "2.22" in version_line \
               or "2.23" in version_line or "2.24" in version_line or "2.25" in version_line \
               or "2.26" in version_line or "2.27" in version_line:
                info["glibc"] = version_line
                info["warnings"].append(f"GLIBC 版本较老({version_line.split()[-1]}),cryptography 可能需要 manylinux2014 wheel")
        except Exception as e:
            info["warnings"].append(f"无法检测 GLIBC: {e}")
    
    return info


if __name__ == "__main__":
    import json
    info = detect()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if info["warnings"]:
        print("\n⚠️  警告:")
        for w in info["warnings"]:
            print(f"  - {w}")
    if info["is_domestic"]:
        print("\n✅ 检测到国产化平台")
```

---

## 八、避坑口诀

**ARM64 wheel / pathlib 跨平台 / 麒麟 GLIBC 2.23 / 内网 nexus / 容器化多架构 / 4 级 fallback**
