# 日志分析器 (Log-Analyzer) 详细参考

## 组件代码

```javascript
/**
 * TOKEN优化器 - 日志分析器 (Log Analyzer)
 */
class LogAnalyzer {
    constructor() {
        this.patterns = {
            port_error: {
                regex: /EADDRINUSE|address\s+already\s+in\s+use|端口.*占用|10048/i,
                severity: 'error',
                category: '环境',
                title: '端口冲突',
                suggestions: ['netstat -ano | findstr PORT', 'Stop-Process -Id PID']
            },
            http_error: {
                regex: /\b(404|500|502|503|504)\s+\w+/i,
                severity: 'error',
                category: '网络',
                title: 'HTTP错误',
                suggestions: ['检查路径', '查看服务端日志']
            },
            file_not_found: {
                regex: /ENOENT|No\s+such\s+file|文件.*不存在|Cannot\s+find/i,
                severity: 'error',
                category: '文件',
                title: '文件不存在',
                suggestions: ['检查路径', '确认文件存在']
            },
            permission_error: {
                regex: /EACCES|EPERM|Permission\s+denied|权限.*拒绝/i,
                severity: 'error',
                category: '权限',
                title: '权限不足',
                suggestions: ['以管理员运行', '检查文件权限']
            },
            timeout_error: {
                regex: /ETIMEDOUT|timeout|超时/i,
                severity: 'warning',
                category: '网络',
                title: '连接超时',
                suggestions: ['检查网络', '增加超时配置']
            },
            connection_refused: {
                regex: /ECONNREFUSED|连接.*拒绝/i,
                severity: 'error',
                category: '网络',
                title: '连接被拒绝',
                suggestions: ['确认服务启动', '检查端口配置']
            },
            module_error: {
                regex: /Cannot\s+find\s+module|Module\s+not\s+found|找不到.*模块/i,
                severity: 'error',
                category: '依赖',
                title: '模块未找到',
                suggestions: ['npm install', '检查import路径']
            },
            warning: {
                regex: /\[WARN[\s\]]?|WARNING|Warn|WARN[^I]|警告/i,
                severity: 'warning',
                category: '警告',
                title: '警告信息',
                suggestions: ['关注但不一定需处理']
            },
            json_error: {
                regex: /JSON\.parse|JSON\.unexpected|SyntaxError.*JSON/i,
                severity: 'error',
                category: '数据',
                title: 'JSON解析错误',
                suggestions: ['检查JSON格式', '验证语法']
            }
        };
    }

    analyze(content) {
        const lines = content.split('\n').filter(l => l.trim());
        const matches = [], errors = [], warnings = [];

        lines.forEach((line, index) => {
            for (const [name, config] of Object.entries(this.patterns)) {
                if (config.regex.test(line)) {
                    const entry = {
                        line: index + 1,
                        content: line.substring(0, 100),
                        pattern: name,
                        severity: config.severity,
                        category: config.category,
                        title: config.title,
                        suggestions: config.suggestions
                    };
                    matches.push(entry);
                    if (config.severity === 'error') errors.push(entry);
                    else warnings.push(entry);
                    break;
                }
            }
        });

        const byCategory = {};
        matches.forEach(m => byCategory[m.category] = (byCategory[m.category] || 0) + 1);
        const topCategory = Object.entries(byCategory).sort((a, b) => b[1] - a[1])[0];

        return {
            total: lines.length,
            matched: matches.length,
            errors,
            warnings,
            summary: {
                byCategory,
                topCategory
            },
            rootCause: topCategory ? {
                identified: true,
                primaryCategory: topCategory[0],
                message: `${topCategory[1]}个${topCategory[0]}类错误`
            } : { identified: false }
        };
    }
}

module.exports = LogAnalyzer;
```

## 使用示例

```javascript
const LogAnalyzer = require('./log-analyzer');

const analyzer = new LogAnalyzer();

// 示例日志内容
const logContent = `
[2026-03-27 10:00:01] INFO: Server started on port 7860
[2026-03-27 10:00:02] INFO: Database connected
[2026-03-27 10:00:05] WARN: High memory usage detected
[2026-03-27 10:00:10] ERROR: EADDRINUSE: address already in use :::7860
[2026-03-27 10:00:15] ERROR: Connection refused to localhost:3000
[2026-03-27 10:00:20] INFO: Retry attempt 1
[2026-03-27 10:00:25] ERROR: Cannot find module './utils'
[2026-03-27 10:00:30] WARN: Response time exceeded threshold
`;

// 分析日志
const result = analyzer.analyze(logContent);

console.log('=== 日志分析报告 ===');
console.log(`总行数: ${result.total}`);
console.log(`匹配项: ${result.matched}`);
console.log(`错误数: ${result.errors.length}`);
console.log(`警告数: ${result.warnings.length}`);
console.log(`\n=== 按类别统计 ===`);
Object.entries(result.summary.byCategory).forEach(([cat, count]) => {
    console.log(`  ${cat}: ${count}`);
});

if (result.rootCause.identified) {
    console.log(`\n=== 主要问题 ===`);
    console.log(`类别: ${result.rootCause.primaryCategory}`);
    console.log(`描述: ${result.rootCause.message}`);
}

console.log(`\n=== 详细错误 ===`);
result.errors.forEach((err, i) => {
    console.log(`${i + 1}. [行${err.line}] ${err.title}`);
    console.log(`   内容: ${err.content}`);
    console.log(`   建议: ${err.suggestions.join(', ')}`);
});
```

## 输出示例

```
=== 日志分析报告 ===
总行数: 8
匹配项: 7
错误数: 3
警告数: 2

=== 按类别统计 ===
  环境: 1
  网络: 2
  依赖: 1
  警告: 2

=== 主要问题 ===
类别: 网络
描述: 2个网络类错误

=== 详细错误 ===
1. [行4] 端口冲突
   内容: [2026-03-27 10:00:10] ERROR: EADDRINUSE: address already in use
   建议: netstat -ano | findstr PORT, Stop-Process -Id PID
2. [行5] 连接被拒绝
   内容: [2026-03-27 10:00:15] ERROR: Connection refused to localhost
   建议: 确认服务启动, 检查端口配置
3. [行7] 模块未找到
   内容: [2026-03-27 10:00:25] ERROR: Cannot find module './utils'
   建议: npm install, 检查import路径
```

## 日志模式速查

| 模式名称 | 正则表达式 | 严重性 | 类别 |
|----------|------------|--------|------|
| port_error | EADDRINUSE\|address already in use | error | 环境 |
| http_error | \b(404\|500\|502\|503\|504)\s+ | error | 网络 |
| file_not_found | ENOENT\|No such file | error | 文件 |
| permission_error | EACCES\|EPERM\|Permission denied | error | 权限 |
| timeout_error | ETIMEDOUT\|timeout | warning | 网络 |
| connection_refused | ECONNREFUSED | error | 网络 |
| module_error | Cannot find module | error | 依赖 |
| warning | \[WARN\]\|WARNING | warning | 警告 |
| json_error | JSON\.parse | error | 数据 |

## 与其他组件集成

```javascript
// 完整集成示例
const PreChecker = require('./pre-checker');
const Checkpoint = require('./checkpoint');
const FastLocator = require('./fast-locator');
const LogAnalyzer = require('./log-analyzer');

const preChecker = new PreChecker();
const checkpoint = new Checkpoint({ tokenBudget: 5000 });
const locator = new FastLocator();
const analyzer = new LogAnalyzer();

// 任务开始预检
preChecker.checkFile('./src/index.js');
preChecker.checkPort(7860);
preChecker.checkProcess('electron');

// 设置检查点
checkpoint.setPhase('需求分析');
checkpoint.updateToken(200);

// 读取并分析日志
const fs = require('fs');
const logContent = fs.readFileSync('./logs/app.log', 'utf-8');
const logResult = analyzer.analyze(logContent);

// 如果有错误，快速定位
if (logResult.errors.length > 0) {
    const firstError = logResult.errors[0].content;
    const errorInfo = locator.locate(firstError);
    console.log('错误类型:', errorInfo.type);
    console.log('解决方案:', errorInfo.solutions);
}
```
