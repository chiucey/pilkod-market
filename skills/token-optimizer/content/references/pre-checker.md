# 问题预检器 (Pre-Checker) 详细参考

## 组件代码

```javascript
/**
 * TOKEN优化器 - 问题预检器 (Pre-Checker)
 *
 * 功能: 在执行任务前检查常见错误模式，预防问题发生
 */
const { execSync } = require('child_process');
const fs = require('fs');

class PreChecker {
    constructor() {
        this.results = [];
        this.config = { timeout: 5000 };
    }

    checkFile(filePath) {
        // 参数安全检查
        if (!filePath || typeof filePath !== 'string') return false;
        if (filePath.length > 10000) return false; // 防止DoS
        const exists = fs.existsSync(filePath);
        this.results.push({ type: 'file', path: filePath, exists });
        return exists;
    }

    checkPort(port) {
        try {
            const isWindows = process.platform === 'win32';
            const cmd = isWindows
                ? `netstat -ano | findstr :${port}`
                : `lsof -i :${port}`;
            const output = execSync(cmd, { encoding: 'utf-8', timeout: this.config.timeout });
            const inUse = new RegExp(`:${port}`).test(output);
            this.results.push({ type: 'port', port, inUse, available: !inUse });
            return !inUse;
        } catch { return true; } // 端口未被占用
    }

    checkProcess(processName) {
        try {
            const isWindows = process.platform === 'win32';
            const cmd = isWindows
                ? `powershell -Command "Get-Process -Name '${processName}' -ErrorAction SilentlyContinue | Select-Object Id"`
                : `pgrep -x "${processName}"`;
            const output = execSync(cmd, { encoding: 'utf-8' });
            const pids = output.trim().split('\n').filter(l => /^\d+$/.test(l.trim())).map(Number);
            const result = { type: 'process', name: processName, running: pids.length > 0, count: pids.length, pids };
            this.results.push(result);
            return result;
        } catch {
            return { type: 'process', name: processName, running: false, count: 0, pids: [] };
        }
    }

    getReport() {
        return { timestamp: new Date().toISOString(), total: this.results.length, results: this.results };
    }
}

module.exports = PreChecker;
```

## 使用示例

```javascript
const PreChecker = require('./pre-checker');

const preChecker = new PreChecker();

// 检查文件
preChecker.checkFile('./src/index.js');
preChecker.checkFile('./dist/bundle.js');

// 检查端口
preChecker.checkPort(7860);
preChecker.checkPort(3000);

// 检查进程
preChecker.checkProcess('electron');
preChecker.checkProcess('node');

// 获取报告
const report = preChecker.getReport();
console.log(JSON.stringify(report, null, 2));
```

## 输出示例

```json
{
  "timestamp": "2026-03-27T06:30:00.000Z",
  "total": 5,
  "results": [
    { "type": "file", "path": "./src/index.js", "exists": true },
    { "type": "file", "path": "./dist/bundle.js", "exists": true },
    { "type": "port", "port": 7860, "inUse": true, "available": false },
    { "type": "port", "port": 3000, "inUse": false, "available": true },
    { "type": "process", "name": "electron", "running": true, "count": 2, "pids": [1234, 5678] }
  ]
}
```
