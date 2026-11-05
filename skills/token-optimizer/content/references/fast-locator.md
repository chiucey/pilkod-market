# 错误快速定位器 (Fast-Locator) 详细参考

## 组件代码

```javascript
/**
 * TOKEN优化器 - 错误快速定位器 (Fast Locator)
 */
class FastLocator {
    constructor() {
        this.patterns = {
            http_404: {
                pattern: /404|Not\s+Found/i,
                type: 'HTTP_404',
                category: '前端',
                likely: ['路径错误', 'dist未更新', '路由未注册'],
                solutions: ['检查API路径', 'npm run build', '检查后端路由']
            },
            http_500: {
                pattern: /500|Internal\s+Server\s+Error/i,
                type: 'HTTP_500',
                category: '后端',
                likely: ['后端代码异常', '数据库错误', '服务崩溃'],
                solutions: ['查看后端日志', '检查最近修改', '验证数据库']
            },
            port_in_use: {
                pattern: /EADDRINUSE|address\s+already\s+in\s+use|端口.*占用|10048/i,
                type: 'PORT_IN_USE',
                category: '环境',
                likely: ['进程残留', '重复启动'],
                solutions: ['netstat -ano | findstr PORT', 'Stop-Process -Id PID -Force', '添加端口检测']
            },
            connection_refused: {
                pattern: /ECONNREFUSED|连接.*拒绝/i,
                type: 'CONNECTION_REFUSED',
                category: '网络',
                likely: ['服务未启动', '端口错误', '防火墙'],
                solutions: ['确认服务启动', '检查端口配置', '检查防火墙']
            },
            file_not_found: {
                pattern: /ENOENT|文件.*不存在|No\s+such\s+file/i,
                type: 'FILE_NOT_FOUND',
                category: '前端',
                likely: ['路径错误', '文件未创建', '拼写错误'],
                solutions: ['检查路径', '确认文件存在', '检查大小写']
            },
            permission_denied: {
                pattern: /EACCES|EPERM|权限.*拒绝|Permission\s+denied/i,
                type: 'PERMISSION_DENIED',
                category: '环境',
                likely: ['权限不足', '需管理员'],
                solutions: ['以管理员运行', '检查文件权限']
            },
            timeout: {
                pattern: /ETIMEDOUT|超时|timeout/i,
                type: 'TIMEOUT',
                category: '网络',
                likely: ['网络不稳定', '服务响应慢'],
                solutions: ['检查网络', '增加超时配置']
            },
            broken_pipe: {
                pattern: /EPIPE|Broken\s+pipe/i,
                type: 'BROKEN_PIPE',
                category: 'Electron',
                likely: ['stdout已关闭', 'console.log在Electron中'],
                solutions: ['禁用console.log', '改用文件日志', '捕获异常']
            },
            module_not_found: {
                pattern: /Cannot\s+find\s+module|Module\s+not\s+found|找不到.*模块/i,
                type: 'MODULE_NOT_FOUND',
                category: '前端',
                likely: ['依赖未安装', '路径错误'],
                solutions: ['npm install', '检查import路径']
            }
        };
    }

    locate(error) {
        if (error === null || error === undefined) {
            return { matched: false, type: 'UNKNOWN', category: '未知', likely: ['输入为空'], solutions: ['请提供有效错误信息'] };
        }
        const errorString = typeof error === 'string' ? error : (error.message || String(error));
        for (const [name, config] of Object.entries(this.patterns)) {
            if (config.pattern.test(errorString)) {
                return { matched: true, type: config.type, category: config.category, likely: config.likely, solutions: config.solutions, suggestions: config.solutions.join('\n') };
            }
        }
        return { matched: false, type: 'UNKNOWN', category: '未知', likely: ['需手动排查'], solutions: ['查看完整错误', '搜索关键字', '检查最近变更'] };
    }
}

module.exports = FastLocator;
```

## 使用示例

```javascript
const FastLocator = require('./fast-locator');

const locator = new FastLocator();

// 分析错误
const errors = [
    'Error: EADDRINUSE: address already in use :::7860',
    '404 Not Found: /api/users',
    'Cannot find module ./utils',
    'Connection refused to localhost:3000'
];

errors.forEach(err => {
    const result = locator.locate(err);
    console.log('─'.repeat(50));
    console.log(`错误: ${err}`);
    console.log(`类型: ${result.type}`);
    console.log(`类别: ${result.category}`);
    console.log(`可能原因: ${result.likely.join(', ')}`);
    console.log(`解决方案:\n${result.solutions.map(s => '  - ' + s).join('\n')}`);
});
```

## 输出示例

```
──────────────────────────────────────────────────
错误: Error: EADDRINUSE: address already in use :::7860
类型: PORT_IN_USE
类别: 环境
可能原因: 进程残留, 重复启动
解决方案:
  - netstat -ano | findstr PORT
  - Stop-Process -Id PID -Force
  - 添加端口检测
──────────────────────────────────────────────────
错误: 404 Not Found: /api/users
类型: HTTP_404
类别: 前端
可能原因: 路径错误, dist未更新, 路由未注册
解决方案:
  - 检查API路径
  - npm run build
  - 检查后端路由
```

## 错误分类速查表

| 错误代码 | 关键词 | 类别 | 优先检查 |
|----------|--------|------|----------|
| EADDRINUSE | 端口占用 | 环境 | 进程残留 |
| ECONNREFUSED | 连接拒绝 | 网络 | 服务状态 |
| ENOENT | 文件不存在 | 文件 | 路径正确性 |
| EACCES/EPERM | 权限拒绝 | 环境 | 管理员权限 |
| ETIMEDOUT | 超时 | 网络 | 网络连通性 |
| 404 | Not Found | HTTP | 路径/路由 |
| 500 | Server Error | HTTP | 后端日志 |
| EPIPE | Broken pipe | Electron | console.log |
| MODULE_NOT_FOUND | 模块未找到 | 依赖 | npm install |
