#!/usr/bin/env python3
"""
identify_packer.py — 通过 APK 表面特征识别 Android 加固类型

Usage:
    python3 identify_packer.py <apk>
    python3 identify_packer.py /path/to/app.apk

Output:
    JSON: { "packer": "360-Jiagu", "confidence": "high", "evidence": [...],
            "entry_class": "com.stub.StubApp", "hook_template": "frida_hook_360.js" }
"""

import json
import sys
import zipfile
from pathlib import Path

# 加固指纹库 — so 库名 / 入口类 / 配置文件 / manifest 字段 / assets 标记
SIGNATURES = {
    "360-Jiagu": {
        "so_libs": ["libjiagu.so", "libjiagu_art.so", "libjiagu_x86.so",
                    "libprotectClass.so", "libX86Bridge.so", "libsgcore.so"],
        "assets_files": ["libjiagu_a64.so", "libjiagu_x86.so", ".jgapp"],
        "manifest_app_classes": [
            "com.qihoo.util.StubApplication",
            "com.qihoo.util.stub.StubApp",
            "com.stub.StubApp",
        ],
        "notes": "入口类 + libjiagu.so 是 360 加固的核心指纹。assets/.jgapp 是隐藏标记。",
    },
    "Tencent-Legu": {
        "so_libs": ["libtup.so", "libBugly.so", "libshellx-2.10.6.0.so",
                    "libshell.so", "libexec.so", "libDexHelper.so"],
        "manifest_app_classes": [
            "com.tencent.StubShell",
            "com.tencent.bugly.legu.stub.S",
            "com.tencent.qqprotectstub.StubApplication",
        ],
        "notes": "腾讯乐固 / 乐固 Pro / QQ 安全保护都是这一族",
    },
    "Bangcle": {
        "so_libs": ["libsecexe.so", "libsecmain.so", "libDexHelper.so",
                    "libSecShell.so", "libBangcle.so"],
        "manifest_app_classes": [
            "com.secshell.ShellApplication",
            "com.secneo.apkwrapper.AW",
            "com.bangcle.protect.StubApplication",
        ],
        "notes": "梆梆加固",
    },
    "iJiami": {
        "so_libs": ["libexec.so", "libexecmain.so"],
        "assets_files": ["ijiami.dat", "ijiami.ke"],
        "manifest_app_classes": [
            "com.shell.SuperApplication",
            "com.ijiami.StubApplication",
        ],
        "notes": "爱加密,特征是 assets 下 .dat + .ke 文件",
    },
    "Baidu": {
        "so_libs": ["libbaiduprotect.so", "libbdprotect.so"],
        "manifest_app_classes": ["com.baidu.protect.StubApplication"],
        "notes": "百度加固",
    },
    "Payegis": {
        "so_libs": ["libNSaferOnly.so", "libegis.so", "libNSaferEnhance.so"],
        "manifest_app_classes": ["com.payegis.StubApplication"],
        "notes": "通付盾加固,金融类 app 常见",
    },
    "NetEase-Yidun": {
        "so_libs": ["libnesec.so"],
        "manifest_app_classes": ["com.netease.nis.BuoyApplication"],
        "notes": "网易易盾",
    },
    "AppSealing": {
        "so_libs": ["libNSaferOnly.so"],  # 部分版本混淆在 NetEase
        "manifest_app_classes": ["com.appsealing.stab.StubApp"],
        "notes": "韩国 SaaS 加固,游戏类 app 多",
    },
    "Pairip": {
        "so_libs": ["libpairip.so", "libpairip_core.so"],
        "manifest_app_classes": ["com.pairip.application.PairipApplication"],
        "notes": "印度 Pairip, 2018 后新出现的加固,常见东南亚 app",
    },
    "DexProtector": {
        "so_libs": ["libdexprotector.so", "libDexProtector.so"],
        "manifest_app_classes": ["com.dexprotector.detector.envchecks"],
        "notes": "海外商业加固, 国际应用多",
    },
    "Secneo": {
        "so_libs": ["libsecneo.so"],
        "manifest_app_classes": ["com.secneo.guard.StubApplication"],
        "notes": "梆梆海外版",
    },
    "AppGuard": {
        "so_libs": ["libappguard.so"],
        "notes": "海外商业加固",
    },
    "Protectt.ai": {
        "so_libs": ["libprotectt.so"],
        "notes": "印度移动安全 SaaS",
    },
}


def identify(apk_path: str) -> dict:
    apk = Path(apk_path)
    if not apk.exists():
        return {"error": f"file not found: {apk_path}"}

    so_libs_found = set()
    assets_found = set()
    all_files = []

    with zipfile.ZipFile(apk, "r") as z:
        for name in z.namelist():
            all_files.append(name)
            base = name.rsplit("/", 1)[-1]
            if name.startswith("lib/") and name.endswith(".so"):
                so_libs_found.add(base)
            elif name.startswith("assets/"):
                assets_found.add(base)

    # 解析 manifest 看 application android:name
    entry_class = None
    try:
        from xml.etree import ElementTree as ET
        with zipfile.ZipFile(apk, "r") as z:
            with z.open("AndroidManifest.xml") as f:
                data = f.read()
        # 不解析二进制 manifest(需要 aapt2/apktool),只做字符串匹配
        # 找 "com.xxx.yyy.Application" 形式
        import re
        # AXML 解析这里简化,直接用 grep 方式
        text = data.decode("utf-8", errors="ignore")
        m = re.findall(rb'([a-zA-Z][a-zA-Z0-9_]*\.[a-zA-Z][a-zA-Z0-9_.]*Application)', data)
        if m:
            # 解码,挑最长的(避免被短字符串干扰)
            candidates = [c.decode("utf-8", errors="ignore") for c in m]
            # 排除系统类
            candidates = [c for c in candidates if not c.startswith(("android.", "java.", "javax."))]
            if candidates:
                entry_class = max(candidates, key=len)
    except Exception:
        pass

    # 匹配
    matches = []
    for packer, sig in SIGNATURES.items():
        evidence = []
        for so in sig.get("so_libs", []):
            if so in so_libs_found:
                evidence.append(f"so:{so}")
        for af in sig.get("assets_files", []):
            if af in assets_found:
                evidence.append(f"assets:{af}")
        for cls in sig.get("manifest_app_classes", []):
            if entry_class and entry_class == cls:
                evidence.append(f"manifest_application:{cls}")
            elif cls.split(".")[-1] in str(so_libs_found) or cls in " ".join(all_files):
                # 兜底:文件列表里出现类名
                pass

        if evidence:
            confidence = "high" if len(evidence) >= 2 or any("manifest" in e for e in evidence) else "medium"
            matches.append({
                "packer": packer,
                "confidence": confidence,
                "evidence": evidence,
                "notes": sig.get("notes", ""),
            })

    # 排序
    matches.sort(key=lambda x: (x["confidence"] != "high", -len(x["evidence"])))

    if matches:
        top = matches[0]
        return {
            "apk": str(apk),
            "apk_size": apk.stat().st_size,
            "detected_packer": top["packer"],
            "confidence": top["confidence"],
            "all_matches": matches,
            "entry_class": entry_class,
            "so_libs_found": sorted(so_libs_found),
            "assets_files": sorted(assets_found),
            "hook_template": _template_for(top["packer"]),
        }
    else:
        return {
            "apk": str(apk),
            "apk_size": apk.stat().st_size,
            "detected_packer": "unknown",
            "confidence": "none",
            "all_matches": [],
            "entry_class": entry_class,
            "so_libs_found": sorted(so_libs_found),
            "assets_files": sorted(assets_found),
            "hint": "未匹配到已知加固特征。可能是: (1) 没加固 (2) 自研加固 (3) 已知加固但特征被混淆。先用 jadx 看看 classes.dex 里有没有 com.stub / com.qihoo / com.shell 之类的壳包。",
        }


def _template_for(packer: str) -> str:
    table = {
        "360-Jiagu": "scripts/frida_hook_360.js",
        "Tencent-Legu": "scripts/frida_hook_legu.js",  # TODO
        "Bangcle": "scripts/frida_hook_bangcle.js",     # TODO
        "iJiami": "scripts/frida_hook_inmemory_dex.js",  # fallback
        "Baidu": "scripts/frida_hook_inmemory_dex.js",
        "Payegis": "scripts/frida_hook_inmemory_dex.js",
        "NetEase-Yidun": "scripts/frida_hook_inmemory_dex.js",
        "AppSealing": "scripts/frida_hook_inmemory_dex.js",
        "Pairip": "scripts/frida_hook_inmemory_dex.js",
        "DexProtector": "scripts/frida_hook_inmemory_dex.js",
        "Secneo": "scripts/frida_hook_inmemory_dex.js",
        "AppGuard": "scripts/frida_hook_inmemory_dex.js",
        "Protectt.ai": "scripts/frida_hook_inmemory_dex.js",
    }
    return table.get(packer, "scripts/frida_hook_inmemory_dex.js")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    result = identify(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
