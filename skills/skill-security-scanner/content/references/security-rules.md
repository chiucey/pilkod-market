# Skill 安全检测规则

本文档定义 Skill 安全扫描器使用的详细检测规则。

## 规则分类

### 1. 信息泄露检测

#### 1.1 凭证泄露

| 模式 | 严重级别 | 说明 |
|------|----------|------|
| API Key 格式 | Critical | 检测常见的 API Key 模式 |
| 密码硬编码 | Critical | 源码中的明文密码 |
| Token 泄露 | Critical | 认证 Token 暴露 |
| 私钥文件 | Critical | RSA/SSH 私钥暴露 |
| 连接字符串 | Critical | 数据库连接凭证 |

#### 1.2 常见凭证正则

```python
# OpenAI API Key
r'sk-[a-zA-Z0-9]{48}'

# GitHub Token
r'ghp_[a-zA-Z0-9]{36}'

# AWS Access Key
r'AKIA[A-Z0-9]{16}'

# Slack Token
r'xox[baprs]-[0-9]{10,}'
```

### 2. 代码漏洞检测

#### 2.1 命令注入

| 函数 | 风险 | 说明 |
|------|------|------|
| `eval()` | Critical | 动态执行代码 |
| `exec()` | Critical | 动态执行代码 |
| `subprocess.run(shell=True)` | Critical | Shell 注入 |
| `os.system()` | High | 命令注入 |
| `os.popen()` | High | 命令注入 |
| `__import__()` | High | 动态导入 |

#### 2.2 路径遍历

路径遍历允许攻击者访问预期目录之外的文件。

常见模式：
- `../` 或 `..\\` 序列
- 不安全的 `open(path + user_input)`
- 未验证的 `Path` 拼接

#### 2.3 不安全反序列化

| 库 | 风险 | 安全替代 |
|---|------|----------|
| `pickle.loads()` | Critical | JSON / SafePickle |
| `yaml.load()` | High | `yaml.safe_load()` |
| `marshal.loads()` | High | 避免使用 |
| `eval(ast.literal_eval)` | Medium | 解析后验证 |

### 3. 上传/下载检测

#### 3.1 文件上传风险

检测模式：
- `Content-Disposition: filename`
- `multipart/form-data`
- 任意文件写入操作

防护措施：
1. 验证文件类型（魔数检测）
2. 限制文件大小
3. 生成随机文件名
4. 禁止执行上传目录

#### 3.2 文件下载风险

检测模式：
- 从 URL 下载文件
- 动态构建下载路径
- 任意文件读取

### 4. 网络请求安全

#### 4.1 SSL/TLS 验证

禁用 SSL 验证的模式：
- `verify=False`
- `ssl._create_unverified_context()`

#### 4.2 隐藏的网络活动

- DNS-over-HTTP
- 隐蔽信道
- 异常的后台连接

### 5. 文件结构安全

#### 5.1 符号链接逃逸

检测符号链接指向工作目录之外：
```python
if path.is_symlink():
    target = path.resolve()
    if not target.startswith(base_path):
        # 符号链接逃逸
```

#### 5.2 隐藏文件

以 `.` 开头的文件可能隐藏恶意代码。

#### 5.3 可执行脚本

检测 shell 脚本和可执行文件：
```python
r'#!/bin/(ba)?sh'
r'\.sh$'
r'chmod\s*\+x'
```

## 修复建议

### 命令注入防护

```python
# 不推荐
cmd = f"ls {user_input}"
os.system(cmd)

# 推荐
import subprocess
cmd = ["ls", user_input]  # 列表形式
subprocess.run(cmd)  # 无 shell=True
```

### 反序列化安全

```python
# 不推荐
import pickle
data = pickle.loads(raw)

# 推荐
import json
data = json.loads(raw)  # JSON 是安全的
```

### 路径安全

```python
from pathlib import Path
import os

# 不推荐
path = base_dir + "/" + user_input

# 推荐
path = base_dir / user_input
# 验证路径在基准目录内
path = path.resolve()
if not path.is_relative_to(base_dir):
    raise ValueError("Path traversal detected")
```

### 文件上传安全

```python
import hashlib
import mimetypes

def secure_upload(file, upload_dir):
    # 验证文件类型
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Disallowed file type")

    # 生成安全文件名
    safe_name = hashlib.sha256(file.filename.encode()).hexdigest()[:16] + ext

    # 限制大小
    if len(file.read()) > MAX_SIZE:
        raise ValueError("File too large")

    # 保存
    save_path = Path(upload_dir) / safe_name
    file.save(save_path)

    return save_path
```

## 检测阈值

| 严重级别 | 条件 | 行动 |
|----------|------|------|
| Critical | 检测到凭证/命令注入 | 阻止安装 |
| High | 检测到路径遍历/上传漏洞 | 警告并建议修复 |
| Medium | 检测到低风险模式 | 建议改进 |
| Low | 仅是提示 | 可选修复 |

## 参考资料

- OWASP Top 10
- CWE-79: Cross-site Scripting
- CWE-89: SQL Injection
- CWE-78: OS Command Injection
- CWE-22: Path Traversal
- CWE-502: Deserialization of Untrusted Data
