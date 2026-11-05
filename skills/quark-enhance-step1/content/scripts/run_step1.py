#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_step1.py  —  第一步 一站式编排

    体检 → 判定是否上云 → 免费预处理 → 调用夸克 MCP → 结果核验 → 产出 result.json

用法:
    python run_step1.py --input "图.jpg" --outdir "./_out" --purpose 证件卡
    python run_step1.py --input "图.jpg" --outdir "./_out" --cloud no        # 只体检，不调用
    python run_step1.py --input "图.jpg" --outdir "./_out" --cloud yes --tool scan_image_hd_enhance

本脚本只做处理，不做归档；输出目录整体交回调用方即可。
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or "python"
NODE = os.environ.get("NODE_BIN", "node")

LOG = []


def log(msg):
    line = "[%s] %s" % (dt.datetime.now().strftime("%H:%M:%S"), msg)
    LOG.append(line)
    print(line)


def run(cmd, allow_fail=False):
    log("RUN " + " ".join(str(c) for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 and not allow_fail:
        log("FAIL rc=%d %s" % (r.returncode, (r.stderr or "").strip()[:400]))
        raise SystemExit(1)
    if r.stderr and r.stderr.strip():
        log("stderr: " + r.stderr.strip()[:300])
    return r


def pick_tool(purpose, allow_ocr=False):
    """默认走安全侧：不丢人像/国徽/底纹/印章/签名。"""
    if allow_ocr and purpose == "文档":
        return "scan_image_to_pdf"
    if purpose in ("证件卡", "票据"):
        return "scan_certificate_invoice_enhance"
    if purpose == "图片":
        return "scan_image_hd_enhance"
    return "scan_certificate_invoice_enhance"


def main():
    ap = argparse.ArgumentParser(description="第一步 · 图像增强服务（一站式）")
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--purpose", default="auto", choices=["auto", "证件卡", "文档", "票据", "图片"])
    ap.add_argument("--cloud", default="auto", choices=["auto", "yes", "no"])
    ap.add_argument("--tool", default=None, help="覆盖工具选择")
    ap.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270])
    ap.add_argument("--max-long-edge", type=int, default=800)
    ap.add_argument("--quality", type=int, default=85)
    ap.add_argument("--keep-format", action="store_true", help="含底纹件：不转 JPEG")
    ap.add_argument("--allow-ocr", action="store_true",
                    help="允许对纯文字文档使用 scan_image_to_pdf（会丢弃人像/底纹/签名，确认无这些要素再用）")
    a = ap.parse_args()

    outdir = os.path.abspath(a.outdir)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir, "enhanced"), exist_ok=True)   # 先建目录：避免存盘失败重调

    src = os.path.abspath(a.input)
    base = os.path.splitext(os.path.basename(src))[0]
    billing = {"calls": 0, "note": "每图 1 次；跨页图不拆分；结果已落盘可直接复用"}

    # ─── ⓪ 体检
    probe_json = os.path.join(outdir, "probe.json")
    run([PY, os.path.join(HERE, "probe.py"), "--input", src, "-o", probe_json, "--pretty"])
    probe = json.load(open(probe_json, encoding="utf-8"))
    is_pdf = str(probe.get("kind", "")).endswith("PDF") or src.lower().endswith(".pdf")
    log("体检：kind=%s  %s" % (probe.get("kind"), probe.get("cloud_reason", "")))

    # ─── 判定是否上云
    if a.cloud == "yes":
        use_cloud, reason = True, "调用方指定 --cloud yes"
    elif a.cloud == "no":
        use_cloud, reason = False, "调用方指定 --cloud no"
    else:
        if is_pdf:
            use_cloud, reason = False, probe.get("cloud_reason", "既有 PDF：本地处理即可（0 计费）")
        else:
            sug = probe.get("cloud_suggest")
            if sug is None:
                use_cloud = True          # 判定落在模糊带 → 按安全侧处理
                reason = probe.get("cloud_reason", "") + "（判定不确定，按安全侧=上云）"
            else:
                use_cloud = bool(sug)
                reason = probe.get("cloud_reason", "")
    log("路线：%s（%s）" % ("上云增强" if use_cloud else "本地", reason))

    decision = {"cloud": use_cloud, "reason": reason, "tool": None}
    result = {"path": None, "md5": None, "size": 0, "geometry_change_pct": None, "verdict": None}

    if not use_cloud:
        # 本地路径：源件原样交回（真正落版由下游按其规则处理）
        dst = os.path.join(outdir, "enhanced", os.path.basename(src))
        shutil.copy2(src, dst)
        result["path"] = dst
        result["size"] = os.path.getsize(dst)
        result["verdict"] = {"level": "A", "note": "本地路径：源件原样交回，未做任何重编码", "todo": []}
        if is_pdf:
            result["verdict"]["todo"].append(
                "PDF 落版请走页面级克隆 / 字节复制 / 只改 MediaBox，保留 /Rotate；切勿转图片再拼")
        else:
            result["verdict"]["todo"].append(
                "落版请用 JPEG 通道零重编码装箱（/DCTDecode 直嵌），不要用 PIL 另存为 PDF")
        log("本地路径完成：%s" % dst)
    else:
        # ─── ① 预处理
        prep = run([PY, os.path.join(HERE, "prepare.py"), "--input", src, "--outdir", outdir,
                    "--max-long-edge", str(a.max_long_edge), "--quality", str(a.quality),
                    "--rotate", str(a.rotate)] + (["--keep-format"] if a.keep_format else []))
        prep_rep = None
        for ln in reversed(prep.stdout.strip().split("\n")):
            try:
                prep_rep = json.loads(prep.stdout[prep.stdout.index("{"):])
                break
            except Exception:
                continue
        if not prep_rep:
            log("预处理未返回 JSON，终止")
            raise SystemExit(1)
        log("预处理：%s -> %s (%.3f MB, base64 %.1f KB)"
            % (os.path.basename(src), os.path.basename(prep_rep["out"]),
               prep_rep["mb"], prep_rep["base64_kb"]))
        if not prep_rep.get("base64_within_limit", True):
            log("警告：载荷可能超限，建议调低 --max-long-edge")

        # ─── ② 上云
        tool = a.tool or pick_tool(a.purpose, a.allow_ocr)
        decision["tool"] = tool
        if tool == "scan_image_to_pdf" and not a.allow_ocr:
            log("拒绝：scan_image_to_pdf 属 OCR 重建，会丢弃人像/底纹/手写签名；"
                "如确认无这些要素请显式加 --allow-ocr")
            raise SystemExit(2)
        call = run([NODE, os.path.join(HERE, "call_mcp.js"), tool,
                    "@" + prep_rep["args_json"], "--outdir", outdir, "--name", base])
        try:
            call_rep = json.loads(call.stdout[call.stdout.index("{"):])
        except Exception:
            log("调用器未返回 JSON，原始输出：" + call.stdout[:400])
            raise SystemExit(1)
        billing["calls"] += 1
        log("上云完成：%s  %sms" % (tool, call_rep.get("elapsed_ms")))

        # ─── ③ 核验
        enh = call_rep.get("image") or call_rep.get("pdf")
        if enh and str(enh).lower().endswith(".jpg"):
            vjson = os.path.join(outdir, "verify.json")
            run([PY, os.path.join(HERE, "verify.py"), "--src", prep_rep["out"], "--out", enh, "-o", vjson])
            vrep = json.load(open(vjson, encoding="utf-8"))
            result.update({"path": enh, "size": os.path.getsize(enh),
                           "md5": vrep["after"]["md5"],
                           "width": vrep["after"]["width"], "height": vrep["after"]["height"],
                           "geometry_change_pct": vrep["geometry_change_pct"],
                           "sharpness_ratio": vrep.get("sharpness_ratio"),
                           "verdict": vrep["verdict"]})
        else:
            result.update({"path": enh, "size": os.path.getsize(enh) if enh else 0,
                           "verdict": {"level": "B",
                                       "note": "返回为 PDF（无图像核验）；请下游按页面级克隆落版",
                                       "todo": ["增强后落版须零重编码"]}})

    # ─── ④ 汇总报告
    report = {
        "run_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source": probe,
        "prepare": None if not use_cloud else prep_rep,
        "decision": decision,
        "result": result,
        "billing": billing,
        "verdict": result.get("verdict"),
        "outdir": outdir,
    }
    rp = os.path.join(outdir, "result.json")
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "run.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    log("完成 -> %s" % rp)
    print(json.dumps({"ok": True, "result_json": rp, "billing_calls": billing["calls"],
                      "verdict": result.get("verdict", {}).get("level")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
