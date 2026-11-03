# DEB维护脚本完整指南

## 脚本执行时机

| 脚本 | 何时执行 | 常见用途 |
|------|----------|----------|
| preinst | 文件解压前 | 创建用户、停止服务 |
| postinst | 文件解压后 | 配置、启动服务、设置权限 |
| prerm | 文件删除前 | 停止服务、保存状态 |
| postrm | 文件删除后 | 清理、恢复配置 |

## 脚本参数

所有脚本接收以下参数之一：

- `install`: 首次安装
- `upgrade`: 升级到新版本
- `configure`: 配配置已解压的包
- `remove`: 移除包
- `purge`: 彻底清除包
- `deconfigure`: 移除冲突包后

## 脚本模板

### preinst - 安装前脚本

```bash
#!/bin/bash
set -e

case "$1" in
    install)
        # 首次安装前的操作
        ;;
    upgrade)
        # 升级前的操作
        # 可使用 $2 访问旧版本
        ;;
    abort-upgrade|abort-remove|abort-deconfigure)
        # 失败回滚
        exit 0
        ;;
esac

exit 0
```

### postinst - 安装后脚本

```bash
#!/bin/bash
set -e

case "$1" in
    configure)
        # 最后配置步骤
        # $2 是旧版本号（仅在升级时）

        # 设置文件权限
        chmod 755 /usr/bin/myapp
        chmod 644 /etc/myapp/config.conf

        # 启用服务（systemd）
        if command -v systemctl &> /dev/null; then
            systemctl daemon-reload || true
            systemctl enable myapp.service || true
            systemctl start myapp.service || true
        fi

        # 或使用sysv-rc-conf/chkconfig
        ;;
    abort-upgrade|abort-remove|abort-deconfigure)
        exit 0
        ;;
esac

exit 0
```

### prerm - 移除前脚本

```bash
#!/bin/bash
set -e

case "$1" in
    remove|upgrade|deconfigure)
        # 停止服务
        if command -v systemctl &> /dev/null; then
            systemctl stop myapp.service || true
            systemctl disable myapp.service || true
        fi
        ;;
    failed-upgrade)
        # 处理升级失败
        ;;
esac

exit 0
```

### postrm - 移除后脚本

```bash
#!/bin/bash
set -e

case "$1" in
    remove|purge)
        # 清理操作

        # 删除用户（如创建）
        # userdel myapp || true

        # 删除数据目录（purge时）
        if [ "$1" = "purge" ]; then
            rm -rf /var/lib/myapp
            rm -rf /etc/myapp
            rm -rf /var/log/myapp
        fi
        ;;
    upgrade|failed-upgrade|abort-install|abort-upgrade|disappear)
        # 其他处理
        ;;
esac

# 始终重新加载systemd
if [ -d /run/systemd/system ]; then
    systemctl daemon-reload || true
fi

exit 0
```

## 最佳实践

### 1. 使用 set -e
```bash
#!/bin/bash
set -e
```
脚本遇到错误立即退出，避免部分执行。

### 2. 处理参数
```bash
case "$1" in
    configure|upgrade)
        # 安全操作
        ;;
esac
```

### 3. 优雅的错误处理
```bash
# 使用 || true 防止错误中断
systemctl stop myapp 2>/dev/null || true

# 或使用条件检查
if command -v systemctl &> /dev/null; then
    systemctl daemon-reload
fi
```

### 4. 版本检查
```bash
if [ "$1" = "upgrade" ] && [ -n "$2" ]; then
    OLD_VERSION="$2"
    # 迁移逻辑
fi
```

### 5. systemd处理
```bash
# 检查systemd是否可用
if [ -d /run/systemd/system ]; then
    systemctl daemon-reload
fi

# 不要在preinst中启动服务
# 在postinst中启动
```

### 6. 权限设置
```bash
# 在postinst中设置权限
chmod 755 /usr/bin/myapp
chown root:root /usr/bin/myapp
```

## 常见错误

### 错误1: 脚本不执行
- 检查权限是否为755
- 检查shebang是否正确
- 检查脚本是否为DOS换行符

### 错误2: 服务启动失败
- 不要在preinst中启动
- 确保依赖已安装
- 检查日志

### 错误3: 回滚不工作
- 确保所有操作都是幂等的
- 使用trap或回滚机制
