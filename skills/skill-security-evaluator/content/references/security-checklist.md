# Skill 安全评估检查清单

## 敏感信息检测模式

### API 密钥和凭证
```regex
(?i)(api[_-]?key|apikey|secret[_-]?key|private[_-]?key|access[_-]?token|auth[_-]?token|bearer)
```

### 密码模式
```regex
(?i)(password|passwd|pwd|login|credential)
```

### 数据库连接
```regex
(mongodb|mysql|postgres|redis):\/\/[^\s]+|[^\s]+@(localhost|127\.0\.0\.1)
```

### 云服务凭证
```regex
(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}
```

## 高危文件路径

### 系统关键目录
- `/etc/passwd`
- `/etc/shadow`
- `/etc/sudoers`
- `~/.ssh/`
- `~/.aws/`
- `/root/`

### 配置敏感文件
- `.env`
- `.git/config`
- `credentials.json`
- `secrets.json`
- `*.pem`
- `*.key`

## 危险函数/操作

### 命令执行
- `bash`, `sh`, `exec`, `system`
- `subprocess`, `os.system`
- `eval`, `exec`
- `child_process.spawn`

### 文件操作
- `read_file` 访问系统目录
- `write_file` 覆盖系统文件
- 任意文件读取模式

### 网络操作
- 发送敏感数据到外部
- HTTP 明文传输
- 无验证的回调

## 权限级别定义

### 极高危权限（需严格控制）
- 系统命令执行
- 任意代码执行
- 进程管理
- 服务管理

### 高危权限
- 文件系统全面读写
- 网络访问
- 环境变量读取
- 数据库操作

### 中危权限
- 目录遍历
- 子进程创建
- 外部 API 调用

### 低危权限
- 只读文件访问
- 只读 API 调用
- 日志写入

## 依赖安全检查

### 已知漏洞库特征
- 停止维护超过 2 年
- 最后更新超过 1 年
- 已知 CVE 记录
- 非官方来源

### 可疑包特征
- 名称混淆（如 typosquatting）
- 最小下载量
- 无签名验证
