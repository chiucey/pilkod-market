# 命令参考表

## 常用命令分类

### 文件系统操作

| 命令 | 描述 | 示例 |
|------|------|------|
| `cat` | 显示文件内容 | `cat file.txt` |
| `ls` | 列出目录内容 | `ls -la /workspace` |
| `pwd` | 显示当前目录 | `pwd` |
| `cd` | 切换目录 | `cd /workspace` |
| `find` | 查找文件 | `find /workspace -name "*.py"` |
| `grep` | 文本搜索 | `grep "pattern" file.txt` |

### 环境与系统信息

| 命令 | 描述 | 示例 |
|------|------|------|
| `env` | 显示环境变量 | `env` |
| `whoami` | 显示当前用户 | `whoami` |
| `uname` | 显示系统信息 | `uname -a` |
| `hostname` | 显示主机名 | `hostname` |
| `date` | 显示日期时间 | `date` |

### 文本处理

| 命令 | 描述 | 示例 |
|------|------|------|
| `echo` | 输出文本 | `echo "Hello"` |
| `head` | 显示文件开头 | `head -n 10 file.txt` |
| `tail` | 显示文件结尾 | `tail -n 10 file.txt` |
| `wc` | 统计行数/字数 | `wc -l file.txt` |
| `sort` | 排序 | `sort file.txt` |

### 进程管理

| 命令 | 描述 | 示例 |
|------|------|------|
| `ps` | 显示进程 | `ps aux` |
| `top` | 显示资源使用 | `top` |
| `kill` | 终止进程 | `kill 1234` |
| `pgrep` | 查找进程 | `pgrep python` |

### 网络诊断

| 命令 | 描述 | 示例 |
|------|------|------|
| `ping` | 测试连接 | `ping google.com` |
| `curl` | HTTP 请求 | `curl https://example.com` |
| `wget` | 下载文件 | `wget https://example.com/file` |
| `netstat` | 网络状态 | `netstat -tuln` |

## 风险等级说明

### 低风险（直接执行）
无需用户确认即可执行，用于信息查询和只读操作。

### 中等风险（意图确认）
需要用户明确意图后才执行，如文件创建、复制、移动等。

### 高风险（明确确认）
需要用户明确确认后才能执行，如删除、系统修改等。

## 常见问题处理

### 命令不存在
```
$ ls: cannot access '/nonexistent': No such file or directory
```
处理：检查路径拼写是否正确

### 权限不足
```
$ cat /etc/shadow
cat: /etc/shadow: Permission denied
```
处理：说明需要 sudo 权限

### 执行超时
长时间运行的命令（如 `ping`、`top`）设置超时限制