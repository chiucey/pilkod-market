---
name: android-packer-unpack
description: 研究 Android 加固 (packer) 脱壳的工作流框架。覆盖 360 加固 (libjiagu.so) 默认适配,以及乐固、梆梆、爱加密、百度加固、Pairip、AppSealing 等主流商业加固的 hook 模板。基于 Frida + 内存 dump + dex 魔数切片。Triggers: 脱壳、解加固、unpack、Android packer、jiagu、乐固、梆梆、libjiagu、libsecexe、360 加固、frida-dexdump、内存 dump dex、hook InMemoryDexClassLoader、hook OpenMemory。
---

# android-packer-unpack

Android 加固(360 / 乐固 / 梆梆 / 爱加密 / 百度 / Pairip / AppSealing)的研究型脱壳 workflow。

**定位:** 框架 + 关键 hook 点 + 调试指引。**不是**"一键脱壳器"——商业加固会持续升级反制,固化脚本很快失效。

**核心思路:** 加固壳的 DEX 必然要在内存里以明文形态短暂存在——脱壳就是抓住那一瞬间。Frida 注入后,在 DEX 落到 ART runtime 时,拦截关键 API 并把字节流写盘。

**默认适配:** 360 加固 (`com.stub.StubApp` + `libjiagu.so` + `libX86Bridge.so`)。其他加固提供 hook 模板,在 `references/packer-signatures.md` 选对应章节。

---

## 何时使用

- 拿到一个 APK,反编译只有壳 stub(几百个 `com.stub.*` 类),看不到业务代码
- 怀疑有 360 / 乐固 / 梆梆 / 爱加密等加固,需要 dump 原始 dex 做研究分析
- 想验证某个加固版本的反 frida 检测到底有几层
- 适配新型加固变种,需要快速搭一个 hook 框架

**不要用此 skill:**
- 去除广告 / 绕过付费 / 侵犯版权(技术中立不等于用途中立)
- 二次打包发布他人的商业 app
- 你已经知道 APK 没加固,直接用 `apk-decompiler` jadx 就行

---

## 工作流概览

```
[1] 查加固类型      identify_packer.py <apk>
        ↓
[2] 选 hook 模板    360 → scripts/frida_hook_360.js
                    乐固 → scripts/frida_hook_legu.js
                    梆梆 → scripts/frida_hook_bangcle.js
                    不确定 → scripts/frida_hook_inmemory_dex.js (通用 fallback)
        ↓
[3] 配反 frida 检测  scripts/frida_anti_anti.js
        ↓
[4] 跑                  frida -U -f <pkg> -l <hook>.js -l <anti>.js --no-pause
        ↓
[5] 验证 dump 结果      1) file 头部 64 65 78 0a (dex\n)  ?
                        2) jadx 能打开 ?
                        3) 搜 "qihoo/tencent/baidu" 搜不到 = 成功
        ↓
[6] (可选) 多 dex 拼接   scripts/dex_splitter.py
```

---

## 关键 hook 点(按推荐顺序)

商业加固无论怎么升级,dex 最终要交给 ART runtime。Hook 时机优先级:

| # | Hook 点 | 适配版本 | 成功率 | 备注 |
|---|---------|---------|-------|------|
| 1 | `dalvik.system.InMemoryDexClassLoader.<init>` | API 28+ | 90% | 360 v4+ 走这个 |
| 2 | `art::DexFile::OpenMemory` (libart.so) | Android 7-14 | 95% | 360 v3-v5 通用, 抓 `base+size` |
| 3 | `art::DexFile::OpenCommon` (libdexfile.so) | Android 10+ | 90% | 替代 OpenMemory 的新接口 |
| 4 | `art::DexFile::Create` (libdexfile.so) | Android 12+ | 85% | ART 7.0+ 统一构造 |
| 5 | `BaseDexClassLoader.findClass` | 通用 | 60% | 易触发加固反 hook |
| 6 | 内存 `dex\n035\0` 魔数扫描 | 通用 | 99% | 兜底方案,绕过一切 hook 检测 |
| 7 | `libjiagu.so` 导出函数 (jiagu_decrypt 等) | 360 特定 | 50% | 符号版本敏感,需 IDA 先看 |

详细参数与符号名见 `references/hook-points.md`。

---

## 快速开始(360 加固示例)

### 环境准备

```bash
# 1. 装 frida-tools (主机)
pip install frida-tools

# 2. 装 frida-server (设备),版本必须和主机 frida 一致
#    查看主机 frida 版本
frida --version
#    下载对应 frida-server(选 arm64 / armv7 / x86 对应设备架构)
#    https://github.com/frida/frida/releases
adb push frida-server-XX-android-arm64 /data/local/tmp/fs
adb shell "chmod 755 /data/local/tmp/fs"
# 3. 360 会扫 /proc/cmdline 检测 frida 进程名,重命名绕过
adb shell "mv /data/local/tmp/fs /data/local/tmp/zygote64"
adb shell "/data/local/tmp/zygote64 &"  # 前台运行
```

### 启动脱壳

```bash
# 1. 查包名
aapt2 dump packagename target.apk
# 例: com.example.gamebox

# 2. 跑 hook 脚本(同时挂反检测)
frida -U -f com.example.gamebox \
  -l scripts/frida_hook_360.js \
  -l scripts/frida_anti_anti.js \
  --no-pause

# 3. 触发 app 各页面加载,让所有类都过一遍 hook
#    等 5-10 秒,dex 文件会落到 /data/data/<pkg>/files/ 目录
```

### 验证

```bash
# 1. 拉出 dump 的 dex
adb pull /data/data/com.example.gamebox/files/

# 2. 检查魔数(前 8 字节应该是 64 65 78 0a 30 33 35 00)
xxd -l 8 dump.dex
# 期望: 00000000: 6465 780a 3033 3500  dex.035.

# 3. jadx 打开看包名
jadx-gui dump.dex
# 期望: 包名不是 com.stub / com.qihoo,而是真实业务包

# 4. 快速判断有没有把壳 dex 当成原 dex dump 出来
#    jadx 里 Ctrl+Shift+F 搜 "qihoo" / "Stub" 搜不到 = 成功
```

---

## 关键文件说明

| 路径 | 用途 |
|------|------|
| `scripts/frida_hook_360.js` | 360 加固专用(OpenMemory + InMemoryDexClassLoader 双 hook) |
| `scripts/frida_hook_inmemory_dex.js` | 通用 fallback,只 hook InMemoryDexClassLoader |
| `scripts/frida_anti_anti.js` | 反 frida 检测(端口 / 进程名 / maps / openat 扫描) |
| `scripts/frida_dex_scanner.js` | 内存 dex 魔数扫描,绕过所有 hook 检测的兜底 |
| `scripts/identify_packer.py` | 通过 so / class / manifest 特征识别加固类型 |
| `scripts/dex_splitter.py` | dump 出的多 dex 拼接/校验和修复 |
| `references/packer-signatures.md` | 各加固的特征指纹(so 库 / 入口类 / 配置文件) |
| `references/hook-points.md` | 各 hook 点的完整签名 / 参数 / 版本适配表 |
| `references/anti-detection.md` | 360 / 乐固反 frida 检测全清单 + 绕过方法 |

---

## 调试指引(常见失败)

| 症状 | 原因 | 修复 |
|------|------|------|
| Frida attach 成功但 app 立刻闪退 | 360 检测到 frida 进程 | 跑 `frida_anti_anti.js`,改 frida-server 进程名 |
| Hook 没触发,console 无输出 | hook 点选错 / 时机太晚 | 换 OpenMemory → InMemoryDexClassLoader |
| Dump 出来只有 1-2KB | 拿到的是壳 stub dex | 检查 `qihoo` 关键字是否还在;换更深的 hook 点 |
| Dump 出来 jadx 打不开,报 `Invalid dex` | DEX 校验和错误 | 跑 `dex_splitter.py --fix-checksum` |
| Dump 出来体积大但全是 `com.stub.*` | dump 的是壳 dex,不是原 dex | 触发更多页面;hook 时机延后 |
| 反复 attach 后 app 不响应 | Frida session 残留 | `frida-kill` 清理;重启 app |

---

## 法律 / 道德边界

- 商业加固本身是合法的技术保护手段,脱壳研究也是公开的安全研究领域
- 但**用脱壳结果绕过付费、去除广告、二次发布、商业盗版**在任何司法管辖区都违法
- 此 skill 假设你脱壳是为了:
  - 验证自家 app 的加固强度
  - 学术研究加固 / 反加固的攻防对抗
  - 已获授权的渗透测试 / 漏洞研究
  - 个人学习目的(仅自己分析,不传播 dump 结果)
- **如果用户用此 skill 做上述之外的用途,默认视为用户自己承担责任**

---

## 相关项目

- [hluwa/frida-dexdump](https://github.com/hluwa/frida-dexdump) (4.6k stars, archived) — 此领域最主流工具,本 skill 的 hook 点优先级参考了它
- [zhiyu-zeng/Android_Dump_Dex](https://github.com/zhiyu-zeng/Android_Dump_Dex) (2025 维护) — 多 packer 识别 + 通用 hook 脚本
- [enovella/fridroid-unpacker](https://github.com/enovella/fridroid-unpacker) — 精简版,适配 OpenMemory + OpenCommon
- [CrackerCat/frdia-hook](https://github.com/CrackerCat/frdia-hook) — 工业级,带自动 dex 校验和修复
- [XIT07/JiaguSentinelPro](https://github.com/XIT07/JiaguSentinelPro) — 2026 新,360 专项

本 skill **不复制** 这些项目的代码,而是提供**框架 + 关键 hook 点 + 调试指引**。需要更完整现成工具时,直接用上面这些项目;本 skill 适合**想自己理解 / 改 hook 点 / 适配新加固变种**的场景。
