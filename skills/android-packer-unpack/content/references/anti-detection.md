# 反 frida 检测绕过手册

加固厂商对 Frida 的检测在 2022 年后已经形成标准化方案, 下面列出所有已知检测点 + 绕过方法。

## 检测点清单

### 1. /proc/self/cmdline 检测

**检测方法**: 读取 `/proc/self/cmdline` 看是否含 `frida` / `gadget` / `linjector`
**加固实例**: 360 v4+, 乐固 v3+

**绕过**:
- 部署 frida-server 前重命名:
  ```bash
  adb shell "mv /data/local/tmp/frida-server /data/local/tmp/zygote64"
  ```
- Hook `openat` 把 `/proc/self/cmdline` 替换为 `/dev/null` (见 `frida_anti_anti.js` hook 2)

### 2. /proc/self/maps 检测

**检测方法**: 读 `/proc/self/maps` 找 `frida-agent` / `frida-gadget` 字符串
**加固实例**: 全部加固

**绕过**:
- Hook `strstr` 把 maps 里的 frida 字符串替换成 `libc.so` (见 `frida_anti_anti.js` hook 3)
- Hook `openat` 屏蔽 frida 相关路径

### 3. 端口检测 (27042)

**检测方法**: 扫描 `/proc/net/tcp` 看本地监听 27042 端口
**加固实例**: 360, 乐固

**绕过**:
- 改 frida 启动参数: `frida-server -l 0.0.0.0:31337` (用非常用端口)
- 端口检测通常在 frida attach 之前就发生, 改端口用处不大 — 实际主要靠 hook `fopen` 屏蔽 `/proc/net/tcp`

**完整 hook 模板**:
```javascript
const fopen = Module.findExportByName(null, 'fopen');
Interceptor.attach(fopen, {
    onEnter(args) {
        this.path = args[0].readCString();
    },
    onLeave(retval) {
        if (this.path && (this.path.indexOf('/proc/net/tcp') >= 0 ||
                          this.path.indexOf('/proc/net/tcp6') >= 0)) {
            // 抹除 frida 端口 — 需要解析 /proc/net/tcp 格式, 复杂
            // 简化: 让 read 返回空 — 通过拦截 read 系统调用实现
        }
    }
});
```

### 4. TracerPid 检测 (ptrace)

**检测方法**: 读 `/proc/self/status` 找 `TracerPid:\t<非零>`
**加固实例**: 全部加固, 几乎都做

**绕过**:
- TracerPid 由内核维护, 用户态改不了
- Hook `read` 系统调用, 读 `/proc/self/status` 时过滤 TracerPid 字段:
  ```javascript
  // 不推荐 — 复杂且易错
  // 更好的办法: 用 frida 启动时 -O 选项
  ```

**更简单的办法**:
```bash
# 启动 frida-server 时用 -O (--optimize) 减少痕迹
/data/local/tmp/zygote64 &
# 然后 frida attach
frida -U -f <pkg> ...
```

### 5. 自 ptrace 调试检测

**检测方法**: 加固自己在 `JNI_OnLoad` 里 `ptrace(PTRACE_TRACEME, 0, 0, 0)`, 如果已经被 trace 就失败
**加固实例**: 360 v5, 部分乐固

**绕过**:
- 这是加固检测自身被 ptrace, Frida 注入后等于已经 ptrace 了目标, 二次 ptrace 失败
- 需要 hook `ptrace` 自身, 拦截加固的 `PTRACE_TRACEME` 调用返回 0
```javascript
const ptrace = Module.findExportByName(null, 'ptrace');
Interceptor.attach(ptrace, {
    onEnter(args) {
        if (args[0].toInt32() === 0) {  // PTRACE_TRACEME
            this.skip = true;
        }
    },
    onLeave(retval) {
        if (this.skip) retval.replace(0);
    }
});
```

### 6. 时间差检测

**检测方法**: 关键函数前后测时间, 如果被 frida hook 会慢很多
**加固实例**: 高级加固 (DexProtector, AppSealing)

**绕过**:
- 用 frida 的 `Interceptor.replace` 比 `Interceptor.attach` 快
- 或者 hook `clock_gettime` / `gettimeofday` 抹掉时间差:
  ```javascript
  const cgt = Module.findExportByName(null, 'clock_gettime');
  Interceptor.attach(cgt, {
      onLeave(retval) {
          // 简化: 让时间差变 0 — 复杂, 一般不处理
      }
  });
  ```

### 7. signal handler 检测

**检测方法**: 加固自己注册 `SIGSEGV` / `SIGILL` handler, 触发后看是不是自己 handler
**加固实例**: 360 v5

**绕过**:
- Hook `signal` / `sigaction`, 把加固的 handler 替换为默认
- 或直接禁用加固的 signal handler:
  ```javascript
  const sig = Module.findExportByName(null, 'sigaction');
  Interceptor.attach(sig, {
      onEnter(args) {
          // 把所有非标准 handler 都改成 SIG_DFL (0)
          if (args[1] && args[1].compare(0) > 0) {
              // 复杂 — 一般不处理
          }
      }
  });
  ```

### 8. Java 层检测 (最常见, 必须绕过)

**检测方法**: 加固在 Java 层遍历 `ClassLoader` 找 `de.robv.android.xposed.XposedBridge` / `frida` 相关类
**加固实例**: 全部

**绕过**:
- Hook `ClassLoader.loadClass`, 把 frida 相关类名屏蔽:
  ```javascript
  Java.perform(function() {
      const CL = Java.use('java.lang.ClassLoader');
      CL.loadClass.overload('java.lang.String').implementation = function(name) {
          if (name.indexOf('frida') >= 0 || name.indexOf('xposed') >= 0) {
              return null;  // 让加固查不到
          }
          return this.loadClass(name);
      };
  });
  ```

---

## 综合 hook 脚本

`scripts/frida_anti_anti.js` 已实现:
1. `__system_property_get` — 屏蔽 frida 端口 / 进程名相关 system property
2. `openat` — 屏蔽 frida 文件探测
3. `strstr` — 抹除 maps 里的 frida-agent
4. `strcmp` — 抹除 frida 字符串比对
5. 部分 `read` — 留 hook 位 (TracerPid)

## 完整绕过清单 (高级)

如果上面还不够, 加这几个:

```javascript
// 1. Hook pthread_create 防止加固的 watchdog 线程
const pthread = Module.findExportByName(null, 'pthread_create');
Interceptor.attach(pthread, {
    onEnter(args) {
        // 屏蔽加固自建的检测线程 — 需要识别线程函数, 复杂
    }
});

// 2. Hook access / stat / lstat 防止加固扫文件
const access = Module.findExportByName(null, 'access');
Interceptor.attach(access, {
    onEnter(args) {
        const path = args[0].readCString();
        if (path && /frida|gadget|linjector/i.test(path)) {
            args[0].writeUtf8String('/dev/null');
        }
    }
});

// 3. Java.perform 里 hook ClassLoader.loadClass
Java.perform(function() {
    const CL = Java.use('java.lang.ClassLoader');
    CL.loadClass.overload('java.lang.String').implementation = function(name) {
        if (/frida|xposed|epic/i.test(name)) return null;
        return this.loadClass(name);
    };
});
```

## 启动顺序很重要

1. **部署前重命名 frida-server 二进制** (不是启动后, 是 push 之前)
2. **frida-server 必须前台运行** (后台会被加固的进程扫描杀)
3. **attach 时机**: app 启动后, 但加固壳还没做反调试检测前

```bash
# 完整流程
adb push frida-server-XX-android-arm64 /data/local/tmp/fs
adb shell "chmod 755 /data/local/tmp/fs"
adb shell "mv /data/local/tmp/fs /data/local/tmp/zygote64"
adb shell "/data/local/tmp/zygote64 &"  # 改后台, 但日志会丢
# 实际上加固会扫 cmdline 杀进程, 所以前台跑更稳
```

## 失败排查表

| 症状 | 原因 | 修复 |
|------|------|------|
| app 启动后立刻闪退 | 加固检测到 frida-server 进程 | 改名 + 前台运行 |
| Frida attach 成功但 console 无输出 | hook 点选错 | 换 InMemoryDexClassLoader / OpenMemory |
| 反复 attach 几次后 frida-server 死掉 | 加固发 SIGKILL | 加 `--persist` 让 frida 自动重启 session |
| hook 到字节流但 jadx 打不开 | dump 的是加固自己生成的 dex, 不是原 dex | 触发更多页面, hook 时机延后 |
| console 出现 `qihoo` 关键字 | 你 hook 到了壳自己的代码执行, 不是原 dex | 改成 hook `OpenMemory` 而不是 `Open` |

## 高级技巧:用 frida 自身的反检测

Frida 17.0+ 引入 `--realm=gated` 模式, 绕过部分检测:

```bash
frida --realm=gated -U -f <pkg> -l hook.js
```

更激进: 用 frida-gadget 注入 (而不是 frida-server), 把 frida 库直接编进加固壳自己:

```bash
# 用 frida-gadget 模式, 但操作复杂, 留给需要的人
```

## 一个万能偏方: 多 hook 一起跑

如果单一 hook 失败, 同时跑:
- `frida_hook_360.js` (OpenMemory + InMemoryDexClassLoader)
- `frida_anti_anti.js` (反检测)
- `frida_dex_scanner.js` (内存扫描)

```bash
frida -U -f <pkg> \
  -l scripts/frida_hook_360.js \
  -l scripts/frida_anti_anti.js \
  -l scripts/frida_dex_scanner.js \
  --no-pause
```

三条线总有一条能拿到 dex。
