---
name: ssh-scp-toolkit
description: SSH远程连接和文件传输工具集。当用户需要连接到Linux服务器执行Shell命令、上传文件到服务器、从服务器下载文件、使用PuTTY组件(plink/pscp)进行远程操作时使用此技能。支持密码认证和密钥认证。
---

# SSH-SCP Toolkit

通过PuTTY组件(plink/pscp)实现SSH远程连接和文件传输的专业工具集。

## 环境准备

### 首次使用：自动安装PuTTY组件

本技能会自动检测并安装所需的SSH工具：

**Windows环境**：
```powershell
# 自动下载安装PuTTY
Invoke-WebRequest -Uri "https://the.earth.li/~sgtatham/putty/latest/w64/putty.zip" -OutFile "$env:TEMP\putty.zip"
Expand-Archive -Path "$env:TEMP\putty.zip" -DestinationPath "$env:LOCALAPPDATA\PuTTY"
$env:PATH += ";$env:LOCALAPPDATA\PuTTY"
```

**Linux环境**：
```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y putty-tools

# CentOS/RHEL
sudo yum install -y putty

# Arch Linux
sudo pacman -S putty
```

**macOS环境**：
```bash
# 使用Homebrew
brew install putty

# 或使用MacPorts
sudo port install putty
```

### 工具检测

每次执行前自动检测工具可用性：

```bash
# 检测plink
which plink || echo "plink not found"

# 检测pscp
which pscp || echo "pscp not found"

# 检测puttygen
which puttygen || echo "puttygen not found"
```

## 核心能力

### 1. SSH远程命令执行

使用 `plink` 连接远程Linux服务器并执行命令：

```bash
# 密码认证执行单条命令
plink -pw "password" user@host "command"

# 密钥认证执行命令
plink -i "key.ppk" user@host "command"

# 执行多条命令（使用分号分隔）
plink -pw "password" user@host "cd /path && ls -la && cat file.txt"
```

### 2. SCP文件上传

上传本地文件到远程服务器：

```bash
# 上传单个文件
pscp -pw "password" local_file.txt user@host:/remote/path/

# 上传多个文件
pscp -pw "password" file1.txt file2.txt user@host:/remote/path/

# 上传整个目录（递归）
pscp -r -pw "password" local_dir/ user@host:/remote/path/

# 使用密钥认证
pscp -i "key.ppk" local_file.txt user@host:/remote/path/
```

### 3. SCP文件下载

从远程服务器下载文件到本地：

```bash
# 下载单个文件
pscp -pw "password" user@host:/remote/path/remote_file.txt ./

# 下载整个目录（递归）
pscp -r -pw "password" user@host:/remote/path/ ./local_download/

# 使用密钥认证
pscp -i "key.ppk" user@host:/remote/file.txt ./
```

## 认证方式

### 密码认证

适用于快速连接和测试环境：

```bash
# SSH执行
plink -pw "your_password" username@hostname "ls -la"

# SCP上传
pscp -pw "your_password" source.txt username@hostname:/dest/
```

### 密钥认证（推荐用于生产环境）

使用PPK格式私钥：

```bash
# 生成PPK密钥（如果需要转换）
puttygen original_key.pem -o key.ppk -O private

# SSH执行
plink -i "key.ppk" username@hostname "command"

# SCP传输
pscp -i "key.ppk" source.txt username@hostname:/dest/
```

## 执行流程

### 标准工作流

1. **环境检测**
   - 自动检测plink/pscp是否已安装
   - 如未安装，自动安装对应平台的工具
   - 验证工具可用性

2. **连接准备**
   - 确认目标服务器IP/主机名
   - 获取用户名和认证信息
   - 确认远程路径权限

3. **选择工具**
   - 执行命令 → 使用 `plink`
   - 上传文件 → 使用 `pscp`
   - 下载文件 → 使用 `pscp`

4. **执行操作**
   - 优先使用密钥认证
   - 敏感信息使用环境变量
   - 验证操作结果

5. **结果处理**
   - 检查返回码
   - 处理错误输出
   - 记录操作日志

## 常用命令示例

### 文件操作

```bash
# 查看远程目录
plink -pw "password" user@host "ls -la /var/www/"

# 创建目录
plink -pw "password" user@host "mkdir -p /var/www/html"

# 上传网站文件
pscp -r -pw "password" ./dist/* user@host:/var/www/html/
```

### 系统管理

```bash
# 查看系统信息
plink -pw "password" root@host "uname -a && df -h"

# 重启服务
plink -pw "password" user@host "sudo systemctl restart nginx"

# 检查服务状态
plink -pw "password" user@host "systemctl status nginx"
```

### 部署操作

```bash
# 部署应用
plink -pw "password" user@host "cd /app && git pull && npm install && npm run build"

# 备份数据库
plink -pw "password" user@host "mysqldump -u root -p dbname > /backup/db.sql"
```

## 错误处理

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `plink/pscp not found` | 工具未安装 | 运行安装脚本 |
| `Connection refused` | SSH服务未运行 | 检查远程服务器sshd状态 |
| `Authentication failed` | 密码/密钥错误 | 验证认证信息 |
| `Host key not found` | 首次连接 | 使用 `-batch` 或先手动确认 |
| `Permission denied` | 权限不足 | 检查远程目录权限或使用sudo |

### 安全建议

1. **优先使用密钥认证**，避免密码明文传输
2. **限制文件权限**：私钥文件设为600
3. **使用跳板机**访问内网服务器
4. **记录操作日志**便于审计
5. **敏感操作使用sudo**而非root直接登录

## 安装脚本

```bash
#!/bin/bash
# auto_install_putty.sh - 自动安装PuTTY组件

set -e

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "debian"
        elif command -v yum &> /dev/null; then
            echo "rhel"
        elif command -v pacman &> /dev/null; then
            echo "arch"
        else
            echo "linux-unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

install_putty() {
    local os=$(detect_os)

    case $os in
        debian)
            echo "安装 PuTTY tools (Debian/Ubuntu)..."
            sudo apt-get update && sudo apt-get install -y putty-tools
            ;;
        rhel)
            echo "安装 PuTTY (CentOS/RHEL)..."
            sudo yum install -y putty
            ;;
        arch)
            echo "安装 PuTTY (Arch Linux)..."
            sudo pacman -S putty
            ;;
        macos)
            if command -v brew &> /dev/null; then
                echo "安装 PuTTY (macOS via Homebrew)..."
                brew install putty
            else
                echo "请安装 Homebrew: https://brew.sh"
                exit 1
            fi
            ;;
        windows)
            echo "Windows环境请从 https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html 下载"
            ;;
        *)
            echo "不支持的操作系统: $os"
            exit 1
            ;;
    esac
}

# 主流程
echo "检测系统环境..."
os=$(detect_os)
echo "检测到系统: $os"

if command -v plink &> /dev/null && command -v pscp &> /dev/null; then
    echo "PuTTY 工具已安装"
    plink -V
else
    echo "PuTTY 工具未安装，开始安装..."
    install_putty
    echo "安装完成！"
fi
```

## 依赖说明

| 平台 | 必需工具 | 安装方式 |
|------|---------|---------|
| Linux | plink, pscp, puttygen | apt/yum/pacman install putty-tools |
| macOS | plink, pscp, puttygen | brew install putty |
| Windows | plink.exe, pscp.exe | 下载PuTTY安装包 |

## 参考资料

详细PuTTY使用指南请参阅：[references/putty_guide.md](references/putty_guide.md)
