#!/usr/bin/env python3
"""
产品质量检查引擎 - inspect.py
==============================
从管控方案动态生成检查项，用 regex + LLM 对检查材料进行自动化核查。
"""

import re, os, sys, json, argparse
from pathlib import Path
from typing import Optional

# ---------- 路径配置 ----------
SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT_DIR   = SCRIPT_DIR.parent
CONTROL_PLAN_PATH   = ROOT_DIR / "references" / "管控方案.md"
REPORT_TEMPLATE_PATH = ROOT_DIR / "references" / "检查报告模板.md"
DEFAULT_MATERIALS_DIR = ROOT_DIR / "materials"
DEFAULT_EXTENSIONS = {".md",".txt",".docx",".xlsx",".xls",".pdf",".pptx",".html",".csv"}

# ============================================================================
# 第一步：解析管控方案
# ============================================================================

def parse_control_plan(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    result = {
        "dimensions": {},
        "veto_rules": [],
        "cross_doc_rules": [],
        "raw": text
    }
    sections = re.split(r"\n(?=## Q\d)", text)
    for section in sections:
        m = re.match(r"## Q(\d)[：:]*(.+?)（(\d+)分）", section)
        if not m:
            continue
        q_num  = m.group(1)
        q_name = m.group(2).strip()
        q_total = int(m.group(3))
        dim_key = f"Q{q_num}"
        result["dimensions"][dim_key] = {
            "name": q_name, "total": q_total, "items": []
        }
        if q_num == "2":
            _parse_q2_section(result["dimensions"][dim_key], section)
        else:
            _parse_q345_section(result["dimensions"][dim_key], section)

    for m in re.finditer(r"🔴 \*\*一票否决[：:]*(.+?)\*\*.*?→ (.+?)[。\n]", text, re.DOTALL):
        result["veto_rules"].append({"trigger": m.group(1).strip(), "action": m.group(2).strip()})
    return result


def _parse_q2_section(dim_entry, section):
    m = re.search(r"### 通用规范（所有交付文档）\s*\n(.*?)(?=### |## |$)", section, re.DOTALL)
    if m:
        tbl = _parse_check_table(m.group(1), "通用规范", "2")
        dim_entry["items"].append({
            "doc_name": "通用规范（所有交付文档）",
            "full_score": 10, "weight": 100,
            "veto": False, "checks": tbl
        })
    for m2 in re.finditer(
            "\*\\*(.+?)（(\d+)%）：\\s*\n(.*?)(?=\n\\*\\*|### |## Q|$)",
            section, re.DOTALL):
        doc_name = m2.group(1).strip()
        doc_wt   = int(m2.group(2))
        bullet_text = m2.group(3)
        bullets = []
        for line in bullet_text.split("\n"):
            bm = re.match(r"- (.+?)（(\d+)%）", line.strip())
            if bm:
                kname = bm.group(1).strip()
                kw    = int(bm.group(2))
                kws   = _extract_keywords(kname)
                bullets.append({
                    "name": kname, "weight": kw,
                    "keywords": kws,
                    "regex_friendly": _is_regex_friendly(kname),
                    "regex_patterns": _build_regex_patterns(kname, kws)
                })
        dim_entry["items"].append({
            "doc_name": doc_name,
            "full_score": 10, "weight": doc_wt,
            "veto": False, "checks": bullets
        })


def _parse_q345_section(dim_entry, section):
    """支持两种格式：
    - ### 文档名（满分X分，权重：Y%）[可选附加标题]  ← Q4/Q5
    - ### 文档名（X%）[可选附加标题]                 ← Q3（只有权重%）
    """
    for m in re.finditer(
            "### (.+?)（(满分(\\d+)分，权重：)?(\\d+)%\\）[^\\n]*\\n(.*?)(?=\\n### [^|]|\\n## |\\Z)",
            section, re.DOTALL):
        doc_name    = m.group(1).strip()
        doc_full_sc = int(m.group(3)) if m.group(3) else int(m.group(4))
        doc_weight  = int(m.group(4))
        doc_content = m.group(5)
        veto = "一票否决" in doc_name
        table_items = _parse_check_table(doc_content, doc_name, "")
        dim_entry["items"].append({
            "doc_name": doc_name,
            "full_score": doc_full_sc, "weight": doc_weight,
            "veto": veto, "checks": table_items
        })


def _parse_check_table(text: str, doc_name: str, q_num: str) -> list:
    items = []
    text = re.sub(r"⚠️.*?\n", "", text)
    for line in text.split("\n"):
        m = re.match(r"\|\s*(.+?)\s*\|\s*(\d+)%\s*\|", line)
        if m:
            check_name = m.group(1).strip()
            weight     = int(m.group(2))
            keywords   = _extract_keywords(check_name)
            items.append({
                "name": check_name, "weight": weight,
                "keywords": keywords,
                "regex_friendly": _is_regex_friendly(check_name),
                "regex_patterns": _build_regex_patterns(check_name, keywords)
            })
    return items


def _extract_keywords(text: str) -> list:
    text = re.sub(r"[（(].*?[）)]", "", text)
    text = re.sub(r"[/、，,]+", " ", text)
    return [w.strip() for w in text.split() if len(w.strip()) >= 2]


def _is_regex_friendly(check_name: str) -> bool:
    kws = [
        "格式","命名","编号","模板","版本号","产品名",
        "包含","涵盖","提供","具备","有",
        "数量","总数","个数","项","条","个",
        "URL","url","参数","字段","表名","类型",
        "签字","公章","签章","印模",
        "步骤","命令","脚本","数据",
        "接口","功能","模块","章节","目录",
        "部署","卸载","回滚","监控",
        "常见问题","故障排查",
    ]
    return any(kw in check_name for kw in kws)


def _build_regex_patterns(check_name: str, keywords: list) -> list:
    patterns = []
    for kw in keywords:
        patterns.append(re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
    if "公章" in check_name or "签章" in check_name or "签字" in check_name:
        patterns.append(re.compile(r"(公章|签章|印章|签字|签名)", re.IGNORECASE))
    if "版本" in check_name:
        patterns.append(re.compile(r"v?\d+[.]\d+[.]\d+|版本[：:\s]*\d"))
    if "URL" in check_name or ("请求" in check_name and "地址" in check_name):
        patterns.append(re.compile(r"https?://[^\s'\"<>]+"))
    if "参数" in check_name:
        patterns.append(re.compile(r"(参数|parameter|field|字段)[：:\s]+[\w]+"))
    if "步骤" in check_name:
        patterns.append(re.compile(r"\d+[.、]\s*\S+"))
    if any(k in check_name for k in ["数量","总数","项"]):
        patterns.append(re.compile(r"\d+\s*(项|个|条|份|页|张|步)"))
    return patterns


# ============================================================================
# 第二步：读取检查材料
# ============================================================================

def load_materials(materials_dir: Path) -> dict:
    if not materials_dir.exists():
        return {}
    materials = {}
    for fpath in sorted(materials_dir.rglob("*")):
        if fpath.is_file() and fpath.suffix.lower() in DEFAULT_EXTENSIONS:
            try:
                sys.path.insert(0, str(SCRIPT_DIR))
                from reader import read_document
                result = read_document(str(fpath))
                text = result["text"]
            except Exception:
                text = "[读取失败]"
            name = fpath.stem
            materials[name] = {
                "path": str(fpath),
                "filename": fpath.name,
                "text": text,
                "size": fpath.stat().st_size
            }
    return materials


# ============================================================================
# 第三步：Regex 核查
# ============================================================================

def run_regex_check(check_item: dict, doc_text: str, doc_context: dict = None) -> dict:
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from regex_checker import run_regex_checks
        cr = run_regex_checks(check_item, doc_text, doc_context or {})
        if hasattr(cr, "result"):
            return {"result": cr.result, "score": cr.score,
                    "matched_texts": cr.matched_texts, "reason": cr.reason}
        return cr
    except Exception as e:
        return {"result": "skip", "score": 0.0, "matched_texts": [],
                "reason": f"regex检查出错: {e}"}


# ============================================================================
# 第四步：LLM 核查（生成提示词）
# ============================================================================

def build_llm_prompt(check_item: dict, doc_text: str, doc_name: str) -> str:
    return (
        f"你是产品质量检查员。请根据以下检查标准，对《{doc_name}》进行核查。\n\n"
        f"## 检查项\n"
        f"- 检查内容：{check_item['name']}\n"
        f"- 权重分：{check_item['weight']}分（满分）\n\n"
        f"## 检查材料正文（摘录）：\n---\n{doc_text[:3000]}\n---\n\n"
        f"请返回 JSON：{{\"result\":\"pass|partial|fail\",\"score\":float,"
        f"\"evidence\":\"在《{doc_name}》第X节找到...\","
        f"\"issue\":\"若不通过，说明问题\"}}"
    )


# ============================================================================
# 第五步：运行完整检查
# ============================================================================

def run_inspection(materials: dict, control_plan: dict,
                   doc_name: str, doc_text: str) -> dict:
    results = {
        "doc_name": doc_name,
        "dimensions": {},
        "veto_triggered": False,
        "veto_type": None,
        "dimension_scores": {},
        "items_detail": []
    }
    for dim_key, dim_info in control_plan["dimensions"].items():
        dim_results = {
            "name": dim_info["name"],
            "total": dim_info["total"],
            "score": 0.0,
            "items": []
        }
        for doc_item in dim_info["items"]:
            if not _doc_matches(doc_name, doc_item["doc_name"]):
                continue
            if doc_item["veto"] and not results["veto_triggered"]:
                vr = _check_veto(doc_item, doc_text)
                if vr["triggered"]:
                    results["veto_triggered"] = True
                    results["veto_type"] = doc_item["doc_name"]
                    dim_results["items"].append({
                        "name": doc_item["doc_name"], "result": "fail",
                        "score": 0.0, "evidence": vr["evidence"]
                    })
                    if dim_key == "Q3":
                        dim_results["score"] = 0.0
                        break
                    continue
            for check_item in doc_item["checks"]:
                if check_item.get("regex_friendly", False):
                    cr = run_regex_check(check_item, doc_text, {"filename": doc_name})
                else:
                    cr = {
                        "result": "skip", "score": 0.0,
                        "matched_texts": [],
                        "reason": "非regex项，请Agent用LLM核查",
                        "llm_prompt": build_llm_prompt(check_item, doc_text, doc_name)
                    }
                dim_results["items"].append({
                    "name": check_item["name"],
                    "weight": check_item["weight"],
                    **cr
                })
                dim_results["score"] += cr.get("score", 0)
        results["dimensions"][dim_key] = dim_results
        results["dimension_scores"][dim_key] = dim_results["score"]
    return results


def _doc_matches(doc_name: str, ctrl_name: str) -> bool:
    aliases = {
        "立项材料": ["立项材料","项目立项","立项文档"],
        "产品白皮书": ["产品白皮书","白皮书"],
        "需求规格说明书": ["需求规格说明书","需求说明","需求文档"],
        "功能/接口清单": ["功能清单","接口清单","功能接口清单","功能与接口清单"],
        "接口说明文档": ["接口说明","接口文档","API文档"],
        "概要设计说明书": ["概要设计","系统概要"],
        "详细设计说明书": ["详细设计","详细设计文档"],
        "产品操作手册": ["操作手册","使用手册","用户手册"],
        "测试用例": ["测试用例","用例文档"],
        "报告文档": ["测试报告","报告文档","检测报告"],
        "测试执行记录": ["测试执行记录","执行记录"],
        "部署文档": ["部署文档","部署说明","部署手册"],
        "运维手册": ["运维手册","运维文档","运维说明"],
        "二开开发能力": ["二开","二次开发","开发能力"],
    }
    for alias in aliases.get(ctrl_name, [ctrl_name]):
        if alias in doc_name:
            return True
    return False


def _check_veto(doc_item: dict, doc_text: str) -> dict:
    doc_name = doc_item["doc_name"]
    if "测试执行记录" in doc_name:
        required = ["基本信息","总体概述","测试范围","执行情况","用例执行列表","测试结果截图"]
    elif "二开" in doc_name or "开发能力" in doc_name:
        required = ["配置级","组装级","编码级"]
    else:
        return {"triggered": False, "evidence": ""}
    found = [r for r in required if re.search(re.escape(r), doc_text, re.IGNORECASE)]
    if len(found) < len(required):
        return {"triggered": True,
                "evidence": f"一票否决：缺少 {set(required)-set(found)}，仅找到 {found}"}
    return {"triggered": False, "evidence": f"一票否决项全部找到：{found}"}


# ============================================================================
# 第六步：生成报告
# ============================================================================

def generate_report(inspection_results: list, control_plan: dict,
                    output_path: Path = None) -> str:
    lines = [
        "# 产品交付质量检查报告\n",
        "**生成时间：** 2026-04-21\n",
        "**检查维度：** Q2+Q3+Q4+Q5\n",
        f"**文档数量：** {len(inspection_results)}份\n",
        "---\n"
    ]
    total_score = 0.0
    total_max   = sum(d["total"] for d in control_plan["dimensions"].values())

    for res in inspection_results:
        lines.append(f"\n## 《{res['doc_name']}》\n")
        for dim_key, dim_result in res["dimensions"].items():
            dim_info = control_plan["dimensions"][dim_key]
            score    = dim_result["score"]
            veto_note = (" ⚠️ 一票否决触发" if res["veto_triggered"] and dim_key=="Q3" else "")
            lines.append(
                f"\n### {dim_key} {dim_info['name']}（{score:.2f}/{dim_info['total']}分）{veto_note}\n"
            )
            if not dim_result["items"]:
                lines.append("（未涉及该维度）\n")
                continue
            lines.append("| # | 检查项 | 权重 | 结果 | 得分 | 得分依据/扣分位置 |\n")
            lines.append("|---|--------|------|------|------|-------------------|\n")
            for i, item in enumerate(dim_result["items"], 1):
                icon = {"pass":"✅","partial":"⚠️","fail":"❌","skip":"➖"}.get(
                    item.get("result","skip"), "➖")
                ev = (item.get("matched_texts") or [item.get("evidence", item.get("reason",""))])
                ev = ev[0] if ev else ""
                if len(str(ev)) > 55: ev = str(ev)[:55]+"..."
                lines.append(
                    f"| {i} | {item['name']} | {item.get('weight','-')} | "
                    f"{icon} | {item.get('score',0):.2f} | {ev} |\n"
                )
        for dim_key, sc in res["dimension_scores"].items():
            total_score += sc

    score_rate = (total_score / total_max * 100) if total_max > 0 else 0
    if score_rate >= 93:   rating = "⭐⭐⭐ 优秀"
    elif score_rate >= 80: rating = "⭐⭐ 良好"
    elif score_rate >= 60: rating = "⭐ 合格"
    else:                  rating = "❌ 不合格"

    lines.extend([
        f"\n---\n\n## 综合结论\n\n",
        f"**Q2-Q5 合计得分：** {total_score:.2f}/{total_max:.2f}（{score_rate:.1f}%）\n",
        f"**综合评级：** {rating}\n"
    ])

    report = "".join(lines)
    if output_path:
        output_path.write_text(report, encoding="utf-8")
    return report


# ============================================================================
# CLI 入口
# ============================================================================

def main():
    ap = argparse.ArgumentParser(description="产品质量检查引擎")
    ap.add_argument("--materials","-m", default=str(DEFAULT_MATERIALS_DIR))
    ap.add_argument("--doc","-d", help="指定检查单个文档（materials目录下文件名）")
    ap.add_argument("--output","-o", default=str(ROOT_DIR/"检查报告_输出.md"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--verbose","-v", action="store_true")
    args = ap.parse_args()

    print("=== 产品质量检查引擎 ===")
    if not CONTROL_PLAN_PATH.exists():
        print(f"ERROR: 管控方案不存在: {CONTROL_PLAN_PATH}")
        sys.exit(1)

    plan = parse_control_plan(CONTROL_PLAN_PATH)
    dims = list(plan["dimensions"].keys())
    print(f"解析完成: {len(dims)} 个维度 [{', '.join(dims)}]")
    print(f"一票否决: {len(plan['veto_rules'])} 条")

    materials_dir = Path(args.materials)
    materials = load_materials(materials_dir)
    print(f"加载材料: {len(materials)} 个文件")

    target = {args.doc: materials[args.doc]} if args.doc else materials
    if args.doc and args.doc not in materials:
        print(f"ERROR: 未找到文档 '{args.doc}'")
        sys.exit(1)

    all_results = []
    for doc_key, doc_info in target.items():
        print(f"\n检查: {doc_key} ({len(doc_info['text'])}字符)")
        res = run_inspection(materials, plan, doc_key, doc_info["text"])
        all_results.append(res)
        for dk, sc in res["dimension_scores"].items():
            di = plan["dimensions"][dk]
            print(f"  {dk} {di['name']}: {sc:.2f}/{di['total']}分")

    output_path = Path(args.output)
    report = generate_report(all_results, plan, output_path)
    print(f"\n报告已保存: {output_path}")

    if args.json:
        jp = output_path.with_suffix(".json")
        def make_serializable(obj):
            if hasattr(obj, "__dict__"): return make_serializable(obj.__dict__)
            if isinstance(obj, dict): return {k: make_serializable(v) for k,v in obj.items()}
            if isinstance(obj, list): return [make_serializable(x) for x in obj]
            return obj
        jp.write_text(json.dumps(make_serializable(all_results), ensure_ascii=False, indent=2),
                      encoding="utf-8")
        print(f"JSON已保存: {jp}")

    ts = sum(sum(r["dimension_scores"].values()) for r in all_results)
    tm = sum(d["total"] for d in plan["dimensions"].values())
    print(f"\n=== 综合得分: {ts:.2f}/{tm:.2f}（{ts/tm*100:.1f}%）===")


if __name__ == "__main__":
    main()
