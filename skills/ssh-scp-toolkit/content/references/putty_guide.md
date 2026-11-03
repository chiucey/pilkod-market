# PuTTY 完整使用指南

PuTTY是一套免费的SSH/Telnet网络客户端工具，主要组件包括：
- **plink**: 命令行SSH客户端
- **pscp**: 命令行SCP客户端
- **puttygen**: 密钥生成和转换工具
- **pageant**: SSH认证代理

## 1. plink 详解

### 基本语法

```bash
plink [选项] [用户@]主机 [命令]
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `-pw password` | 指定密码 |
| `-i keyfile` | 指定私钥文件(PPK格式) |
| `-P port` | 指定SSH端口(默认22) |
| `-l username` | 指定用户名 |
| `-batch` | 禁用交互式提示 |
| `-v` | 显示详细输出 |
| `-C` | 启用压缩 |
| `-agent` | 使用Pageant认证 |
| `-proxycmd command` | 使用代理命令 |

### 实际应用示例

#### 交互式会话

```bash
plink user@hostname
```

#### 执行单条命令

```bash
plink -pw "mypassword" user@hostname "uname -a"
```

#### 执行脚本文件

```bash
plink -pw "mypassword" user@hostname -m commands.txt
```

其中commands.txt内容示例：
```
cd /var/log
ls -lh
tail -n 20 syslog
```

#### 管道操作

```bash
cat local_file.txt | plink -pw "pass" user@hostname "cat > remote_file.txt"
```

#### 保持连接

```bash
plink -pw "pass" user@hostname -N "sleep 3600" &
```

## 2. pscp 详解

### 基本语法

```bash
pscp [选项] 源文件 目标位置
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `-pw password` | 指定密码 |
| `-i keyfile` | 指定私钥文件(PPK格式) |
| `-P port` | 指定SSH端口(默认22) |
| `-l username` | 指定用户名 |
| `-r` | 递归复制整个目录 |
| `-v` | 显示详细输出 |
| `-C` | 启用压缩 |
| `-p` | 保留文件属性 |
| `-q` | 静默模式，不显示传输进度 |
| `-batch` | 禁用交互式提示 |

### 实际应用示例

#### 上传单个文件

```bash
pscp -pw "mypassword" localfile.txt user@hostname:/home/user/
```

#### 上传到指定位置并重命名

```bash
pscp -pw "mypassword" localfile.txt user@hostname:/home/user/renamed.txt
```

#### 从远程下载到本地

```bash
pscp -pw "mypassword" user@hostname:/var/log/syslog ./downloads/
```

#### 批量上传多个文件

```bash
pscp -pw "mypassword" file1.txt file2.txt file3.txt user@hostname:/path/
```

#### 递归上传整个目录

```bash
pscp -r -pw "mypassword" local_directory/ user@hostname:/remote/path/
```

#### 复制远程目录到本地

```bash
pscp -r -pw "mypassword" user@hostname:/remote/directory/ ./local_directory/
```

#### 使用密钥认证

```bash
pscp -i "mykey.ppk" localfile.txt user@hostname:/path/
```

#### 指定非标准端口

```bash
pscp -P 2222 -pw "mypassword" file.txt user@hostname:/path/
```

## 3. puttygen 密钥管理

### 密钥格式转换

#### OpenSSH 私钥转 PPK

```bash
puttygen openssh_key.pem -o mykey.ppk -O private
```

#### PPK 转 OpenSSH 格式

```bash
puttygen mykey.ppk -o openssh_key -O private-openssh-new
```

#### 生成新密钥对

```bash
puttygen -t rsa -b 4096 -o mykey.ppk -C "user@hostname"
```

参数说明：
- `-t rsa`: 密钥类型(rsa/dsa/ecdsa/ed25519)
- `-b 4096`: 密钥位数
- `-o mykey.ppk`: 输出文件
- `-C "comment"`: 密钥注释

### 密钥加载到Pageant

```bash
pageant.exe mykey.ppk
```

或使用plink自动加载：
```bash
plink -agent user@hostname "command"
```

## 4. 高级用法

### 批量操作脚本

```bash
#!/bin/bash
# 批量部署脚本

HOSTS=("server1" "server2" "server3")
USER="deploy"
PASS="password"

for HOST in "${HOSTS[@]}"; do
    echo "部署到 $HOST..."
    pscp -pw "$PASS" deploy.tar.gz "$USER@$HOST:/tmp/"
    plink -pw "$PASS" "$USER@$HOST" "cd /tmp && tar -xzf deploy.tar.gz && ./install.sh"
    echo "$HOST 部署完成"
done
```

### 远程命令执行并捕获结果

```bash
RESULT=$(plink -pw "pass" user@host "cat /proc/loadavg")
echo "服务器负载: $RESULT"
```

### 安全的密码处理

#### 使用环境变量

```bash
export SSHPASS='your_password'
sshpass -e pscp file.txt user@host:/path/
```

#### 使用密码文件

```bash
echo "mypassword" > .passfile
chmod 600 .passfile
plink -pw "$(cat .passfile)" user@host "command"
```

### SSH隧道转发

```bash
# 本地端口转发
plink -L 8080:localhost:80 user@hostname

# 远程端口转发
plink -R 9090:localhost:3000 user@hostname

# 动态SOCKS代理
plink -D 1080 user@hostname
```

### 连接超时设置

```bash
plink -connect_timeout 30 -pw "pass" user@host "command"
```

## 5. 故障排除

### 常见错误

#### Host key not found

首次连接时需要确认主机密钥：
```bash
plink -hostkey "ssh-rsa 2048 xx:xx:..." user@host "command"
```

或使用-batch参数跳过：
```bash
plink -batch -pw "pass" user@host "command"
```

#### Connection refused

检查SSH服务状态：
```bash
plink -pw "pass" user@host "sudo systemctl status sshd"
```

#### Authentication failed

验证认证方式：
```bash
# 测试密码
plink -v -pw "pass" user@host "exit"

# 测试密钥
plink -v -i "key.ppk" user@host "exit"
```

### 调试连接问题

使用 `-v` 参数查看详细输出：
```bash
plink -v -pw "pass" user@host "command"
```

### 代理设置

#### HTTP代理

```bash
plink -proxycmd "corkscrew proxy 8080 %host %port" user@host "command"
```

#### SOCKS代理

```bash
plink -proxycmd "nc -X 5 -x proxy:1080 %host %port" user@host "command"
```

## 6. 安全最佳实践

1. **优先使用密钥认证**
   - 禁用密码登录
   - 使用强密码保护私钥

2. **保护私钥文件**
   ```bash
   chmod 600 mykey.ppk
   ```

3. **限制密钥使用**
   - 在 authorized_keys 中限制命令
   - 使用 from= 选项限制来源IP

4. **日志审计**
   - 记录所有SSH操作
   - 定期审计日志

5. **使用非默认端口**
   ```bash
   plink -P 22022 -pw "pass" user@host "command"
   ```

6. **最小权限原则**
   - 避免使用root直接登录
   - 使用sudo执行特权操作

## 7. Windows 批处理示例

```batch
@echo off
REM 批量部署脚本 for Windows

set HOST=%1
set USER=deploy
set PASS=password

echo 正在部署到 %HOST%...
pscp -pw %PASS% deploy.zip %USER%@%HOST%:/tmp/
plink -pw %PASS% %USER%@%HOST% "cd /tmp && unzip -o deploy.zip && ./deploy.sh"
echo 部署完成
```

## 8. 参考资源

- PuTTY官方文档: https://www.chiark.greenend.org.uk/~sgtatham/putty/
- PuTTY下载: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
- PPK格式说明: https://the.earth.li/~sgtatham/putty/latest/html/AppendixC.html
