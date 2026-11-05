# Android 加固指纹库

各商业加固在 APK 中留下的可识别痕迹。脱壳第一步:**先识别加固类型**, 再选对应 hook 模板。

## 主流加固指纹

### 360 加固 (Jiagu)
- **so 库**:`libjiagu.so` / `libjiagu_art.so` / `libjiagu_x86.so` / `libprotectClass.so` / `libX86Bridge.so`
- **assets**:`libjiagu_a64.so` / `libjiagu_x86.so`
- **入口类**:`com.qihoo.util.StubApplication` / `com.qihoo.util.stub.StubApp` / `com.stub.StubApp`
- **版本演进**:
  - v2.x: 单 dex, 简单加密
  - v3.x: 加入自定义 ClassLoader (`com.qihoo.util.QihooDexClassLoader`), DEX 按需加载
  - v4.x: 加入 multi-dex 分片, 内存解密后用 `InMemoryDexClassLoader` 加载
  - v5.x+: VMP 指令转换 + 反调试强化, hook 时机变难
- **hook 推荐**:`InMemoryDexClassLoader` (v4+) / `libart.so:OpenMemory` (v3) / 内存魔数扫描 (兜底)

### 腾讯乐固 (Legu)
- **so 库**:`libtup.so` / `libBugly.so` / `libshellx-2.10.6.0.so` / `libshell.so` / `libexec.so` / `libDexHelper.so`
- **入口类**:`com.tencent.StubShell` / `com.tencent.bugly.legu.stub.S` / `com.tencent.qqprotectstub.StubApplication`
- **特点**:
  - 早期版本: DEX 落盘到 `/data/data/<pkg>/files/txshell/`
  - 新版本 (VMP): DEX 仅在内存, hook 难度大
- **hook 推荐**:`libart.so:OpenMemory` / 内存魔数扫描

### 梆梆加固 (Bangcle)
- **so 库**:`libsecexe.so` / `libsecmain.so` / `libDexHelper.so` / `libSecShell.so` / `libBangcle.so`
- **入口类**:`com.secshell.ShellApplication` / `com.secneo.apkwrapper.AW` / `com.bangcle.protect.StubApplication`
- **特点**: 海外版叫 Secneo, 梆梆是国内版, so 名不同
- **hook 推荐**:`InMemoryDexClassLoader` (高版本) / `OpenMemory`

### 爱加密 (iJiami)
- **so 库**:`libexec.so` / `libexecmain.so`
- **assets**:`ijiami.dat` + `ijiami.ke` (这是最稳的指纹)
- **入口类**:`com.shell.SuperApplication` / `com.ijiami.StubApplication`
- **hook 推荐**: 同上

### 百度加固
- **so 库**:`libbaiduprotect.so` / `libbdprotect.so`
- **入口类**:`com.baidu.protect.StubApplication`
- **hook 推荐**: `OpenMemory`

### 网易易盾 (Yidun)
- **so 库**:`libnesec.so`
- **入口类**:`com.netease.nis.BuoyApplication`
- **hook 推荐**: `OpenMemory`

### 通付盾 (Payegis)
- **so 库**:`libNSaferOnly.so` / `libegis.so` / `libNSaferEnhance.so`
- **入口类**:`com.payegis.StubApplication`
- **特点**: 金融类 app 多
- **hook 推荐**: `OpenMemory`

### 海外加固

#### DexProtector
- **so 库**:`libdexprotector.so` / `libDexProtector.so`
- **入口类**:`com.dexprotector.detector.envchecks`
- **hook 推荐**:`OpenMemory` / 内存魔数扫描

#### Pairip
- **so 库**:`libpairip.so` / `libpairip_core.so`
- **入口类**:`com.pairip.application.PairipApplication`
- **特点**: 印度 Pairip, 2018 后新出现的加固, 东南亚 / 印度 app 多
- **hook 推荐**:`OpenMemory`

#### AppSealing
- **so 库**:`libNSaferOnly.so`
- **入口类**:`com.appsealing.stab.StubApp`
- **特点**: 韩国 SaaS, 游戏类 app
- **hook 推荐**:`OpenMemory`

#### Secneo
- **so 库**:`libsecneo.so`
- **入口类**:`com.secneo.guard.StubApplication`
- **特点**: 梆梆海外版

#### AppGuard
- **so 库**:`libappguard.so`
- **hook 推荐**:`OpenMemory`

#### Protectt.ai
- **so 库**:`libprotectt.so`
- **hook 推荐**:`OpenMemory`

---

## 识别顺序建议

脱壳前先用 `identify_packer.py` 扫一遍:

```bash
python3 scripts/identify_packer.py target.apk
```

输出示例:
```json
{
  "detected_packer": "360-Jiagu",
  "confidence": "high",
  "all_matches": [
    {"packer": "360-Jiagu", "confidence": "high", "evidence": ["so:libjiagu.so", "assets:libjiagu_a64.so", "manifest_application:com.stub.StubApp"]}
  ],
  "hook_template": "scripts/frida_hook_360.js"
}
```

拿到 `hook_template` 字段, 直接用对应脚本。

---

## 自研 / 未知加固

如果 `identify_packer.py` 报告 `detected_packer: "unknown"`, 但 classes.dex 明显是壳 (类名以 `a`/`b`/`c` 开头, 或者只有几百个类但 APK 体积大), 可能:

1. **壳 dex 名字混淆** — 找入口类(通常是 `<pkg>.Application` 的子类)
2. **so 名字混淆** — 看 `lib/<arch>/` 下所有 .so
3. **自定义加固** — 用通用 fallback hook (`frida_hook_inmemory_dex.js` + `frida_dex_scanner.js` 双跑)

---

## 加固检测能力对照

| 加固 | identify_packer.py | hook 模板 | 已知反制难度 |
|------|---------------------|-----------|------------|
| 360 v3-v4 | ✅ high | frida_hook_360.js | 中 (Frida 检测) |
| 360 v5+ | ✅ high | frida_hook_360.js + 魔数扫描 | 高 (VMP) |
| 乐固 v2-v3 | ✅ high | fallback | 中 |
| 乐固 VMP | ✅ high | 魔数扫描 + DexPathList | 高 |
| 梆梆 | ✅ high | fallback | 中 |
| 爱加密 | ✅ high (assets 双文件) | fallback | 低 |
| 百度 | ✅ high | fallback | 低 |
| 易盾 | ✅ high | fallback | 低 |
| Pairip | ✅ high | fallback | 中 |
| DexProtector | ✅ high | fallback | 高 |
| 自研 | ⚠️ unknown | 魔数扫描 | 取决于实现 |
