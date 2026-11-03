#!/usr/bin/env python3
"""
skill-integrator scanner v2
Three-layer skill integration analysis:
  L1: Containment    (A ⊇ B → keep A, delete B)
  L2: Overlap        (A ∩ B ≠ ∅ → user decides fusion)
  L3: Association    (no code overlap but context-linked → propose fusion)
"""

import json
import os
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

SKILLS_DIR = Path("/workspace/skills")
OUTPUT_FILE = Path("/workspace/skills/skill-integrator/references/scan-report.json")
STOPWORDS  = {"the", "and", "for", "with", "that", "this", "from", "your",
              "when", "skill", "use", "can", "are", "not", "you", "it",
              "will", "does", "doesn", "is", "or", "be", "to", "of", "a",
              "an", "in", "on", "at", "by"}


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class SkillProfile:
    name: str
    path: str
    raw_name: str          # 目录名（未规范化的名字）
    description: str
    functions: list[str]
    tech_stack: list[str]
    tech_details: list[str]
    keywords: set[str]     # 从描述+功能提取的语义词集合
    file_count: int
    sk_md_length: int


@dataclass
class L1Containment:
    superset: str
    subset: str
    reason: str


@dataclass
class L2Overlap:
    skill_a: str
    skill_b: str
    shared_keywords: list[str]
    shared_functions: list[str]
    overlap_score: float
    recommendation: str


@dataclass
class L3Association:
    skill_a: str
    skill_b: str
    link_reason: str
    proposal: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def norm(text: str) -> str:
    return re.sub(r"[^\w]", "", text.lower())

def ngrams(text: str, n=2) -> set[str]:
    t = norm(text)
    return {"".join(t[i:i+n]) for i in range(max(len(t)-n+1, 0))}

def _kw(text: str) -> set[str]:
    return {w for w in norm(text).split() if len(w) > 2 and w not in STOPWORDS}

def jaccard(a: set, b: set) -> float:
    if not a or not b: return 0.0
    return len(a & b) / max(len(a | b), 1.0)

def kw_jaccard(a: SkillProfile, b: SkillProfile) -> float:
    return jaccard(a.keywords, b.keywords)


# ── Scanner ───────────────────────────────────────────────────────────────────

SKILL_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def parse_fm(text: str) -> tuple[dict, str]:
    m = SKILL_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip("'\"").rstrip("/")
    return fm, text[m.end():]


def scan_skill(d: Path) -> Optional[SkillProfile]:
    sk_md = d / "SKILL.md"
    if not sk_md.exists():
        return None
    text = sk_md.read_text(encoding="utf-8", errors="ignore")
    fm, body = parse_fm(text)

    desc = fm.get("description", "") or (body.splitlines()[1].strip() if len(body.splitlines()) > 1 else "")
    if not desc:
        for line in body.splitlines():
            line = line.strip().strip("#*-\n")
            if 10 < len(line) < 200:
                desc = line
                break

    # File count
    files = [str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and "__pycache__" not in str(p)]

    # Tech stack
    tech_found = []
    for kw in ["python", "bash", "shell", "node", "npm", "yaml", "json", "cron",
               "webhook", "sqlite", "requests", "subprocess", "feishu", "lark",
               "tavily", "browser", "openclaw", "cherry studio", "cpolar",
               "feishu", "wecom", "weixin", "discord", "telegram"]:
        if kw in (text).lower():
            tech_found.append(kw)
    tech_found = list(dict.fromkeys(tech_found))

    # Extract tech details (unusual implementation clues)
    tech_details = []
    for pat, label in [
        (r"使用\s+([^\n，。、.]{3,30})", "使用"),
        (r"基于\s+([^\n，。、.]{3,30})", "基于"),
        (r"通过\s+([^\n，。、.]{3,30})", "通过"),
        (r"调用\s+([^\n，。、.]{3,30})", "调用"),
    ]:
        seen = set()
        for m in re.finditer(pat, text):
            val = m.group(1).strip()
            if 3 < len(val) < 35 and val not in seen:
                seen.add(val)
                tech_details.append(f"{label} {val}")
    tech_details = tech_details[:8]

    # Keywords
    keywords = _kw(desc) | _kw(body[:1000])

    return SkillProfile(
        name=fm.get("name", d.name),
        path=d.as_posix(),
        raw_name=d.name,
        description=desc[:250],
        functions=[],           # v2: skip unreliable function extraction
        tech_stack=tech_found,
        tech_details=tech_details,
        keywords=keywords,
        file_count=len(files),
        sk_md_length=len(text),
    )


def scan_all() -> list[SkillProfile]:
    skills = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            p = scan_skill(entry)
            if p:
                skills.append(p)
    return skills


# ── L1: Containment ────────────────────────────────────────────────────────────

def find_containment(skills: list[SkillProfile]) -> list[L1Containment]:
    """
    A contains B if:
      1. A's description fully covers B's domain (keyword inclusion)
      2. B is strictly smaller (fewer files or shorter SKILL.md)
    Special cases: backup/suffix versions of same skill → keep one
    """
    results = []
    done = set()

    for a in skills:
        for b in skills:
            if a.name == b.name or (a.name, b.name) in done:
                continue
            # Heuristic 1: B is a known backup/old/backup_vN version of A
            def _strip_v(name: str) -> str:
                return re.sub(r"_v\d+$", "", name)
            is_backup = (
                ("backup" in b.raw_name.lower() and _strip_v(a.raw_name) == _strip_v(b.raw_name)) or
                (b.raw_name.startswith(a.raw_name) and b.raw_name != a.raw_name) or
                (a.raw_name.startswith(b.raw_name) and a.raw_name != b.raw_name)
            )
            # Heuristic 2: A fully contains B's description domain
            score = jaccard(a.keywords, b.keywords)
            size_diff = b.sk_md_length < a.sk_md_length
            if (is_backup and score > 0.2) or (score > 0.55 and size_diff):
                results.append(L1Containment(
                    superset=a.name,
                    subset=b.name,
                    reason=(
                        f"[备份版本] {b.name} 是 {a.name} 的旧版本，功能完全相同"
                        if is_backup
                        else f"[包含] 描述重叠率 {score:.0%}，{a.name} 更大，{b.name} 被完全包含"
                    )
                ))
                done.add((a.name, b.name))
                done.add((b.name, a.name))
    return results


# ── L2: Overlap ────────────────────────────────────────────────────────────────

def find_overlaps(skills: list[SkillProfile]) -> list[L2Overlap]:
    """
    A and B overlap if:
      - Keyword Jaccard > 0.25  AND
      - Neither is in a containment relationship with the other
      - Combined overlap score >= 0.30
    """
    results = []
    done = set()
    contain_set = {(r.superset, r.subset) for r in find_containment(skills)}
    contain_set |= {(b, a) for a, b in contain_set}

    for a in skills:
        for b in skills:
            if a.name >= b.name or (a.name, b.name) in done:
                continue
            if (a.name, b.name) in contain_set:
                continue

            score = kw_jaccard(a, b)

            # Tech stack overlap bonus
            a_tech = set(a.tech_stack)
            b_tech = set(b.tech_stack)
            tech_overlap = len(a_tech & b_tech) / max(len(a_tech | b_tech), 1)

            # Shared bigrams
            shared_bigrams = ngrams(a.description, 2) & ngrams(b.description, 2)
            bigram_score = len(shared_bigrams) / 10.0

            combined = score * 0.6 + tech_overlap * 0.25 + min(bigram_score, 0.15)
            if combined >= 0.28:
                # Collect shared keywords
                shared_kw = sorted(a.keywords & b.keywords)[:12]
                results.append(L2Overlap(
                    skill_a=a.name,
                    skill_b=b.name,
                    shared_keywords=shared_kw,
                    shared_functions=[],
                    overlap_score=round(combined, 2),
                    recommendation=f"描述重叠率 {score:.0%}，技术栈重叠 {tech_overlap:.0%}，综合得分 {combined:.2f}"
                ))
                done.add((a.name, b.name))
    return results


# ── L3: Association ────────────────────────────────────────────────────────────

TOPIC_MAP = {
    "feishu":   ["feishu", "lark", "飞书"],
    "wechat":   ["weixin", "wechat", "微信", "个人微信"],
    "schedule": ["cron", "schedule", "定时", "调度", "heartbeat"],
    "search":   ["search", "find", "tavily", "搜索", "查找"],
    "skill":    ["skill", "install", "技能", "安装"],
    "update":   ["update", "updater", "更新", "升级"],
    "memory":   ["memory", "learn", "记忆", "学习", "improving"],
    "finance":  ["investment", "stock", "fund", "finance", "投资", "基金", "股票"],
    "docs":     ["doc", "文档", "tencent", "腾讯"],
    "migrate":  ["migrat", "迁移", "migrator"],
    "cron":     ["cron", "remind", "定时", "调度"],
    "browser":  ["browser", "browser", "浏览器"],
    "automation": ["automation", "workflow", "自动化", "工作流"],
    "coding":   ["code", "coding", "agent", "编码", "代理"],
}

def get_topic_kw(s: SkillProfile) -> set[str]:
    out = set()
    full = (s.description + " " + " ".join(s.tech_stack)).lower()
    for topic, kws in TOPIC_MAP.items():
        if any(kw in full for kw in kws):
            out.add(topic)
    return out


def find_associations(skills: list[SkillProfile]) -> list[L3Association]:
    """
    A and B are associated if:
      - Same topic bucket but NOT in L1/L2
      - OR cross-topic but complementary context
    """
    results = []
    done = set()
    contain_set = {(r.superset, r.subset) for r in find_containment(skills)}
    contain_set |= {(b, a) for a, b in contain_set}
    overlap_pairs = {(r.skill_a, r.skill_b) for r in find_overlaps(skills)}
    overlap_pairs |= {(b, a) for a, b in overlap_pairs}

    for a in skills:
        for b in skills:
            if a.name >= b.name or (a.name, b.name) in done:
                continue
            if (a.name, b.name) in contain_set or (a.name, b.name) in overlap_pairs:
                continue

            ta, tb = get_topic_kw(a), get_topic_kw(b)
            common_topics = ta & tb

            # Same topic but not L1/L2 → suggest integration
            if common_topics:
                results.append(L3Association(
                    skill_a=a.name,
                    skill_b=b.name,
                    link_reason=f"同属主题: {', '.join(sorted(common_topics))}",
                    proposal=f"主题相同但功能分立，建议评估是否可融合——{a.name} 负责 X，{b.name} 负责 Y，合并后统一调度。"
                ))
                done.add((a.name, b.name))
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    skills = scan_all()
    print(f"[skill-integrator] 扫描到 {len(skills)} 个 skills\n")

    l1 = find_containment(skills)
    l2 = find_overlaps(skills)
    l3 = find_associations(skills)

    # Save structured report
    report = {
        "skills": [{
            "name": s.name,
            "raw_name": s.raw_name,
            "description": s.description,
            "functions": s.functions,
            "tech_stack": s.tech_stack,
            "tech_details": s.tech_details,
            "file_count": s.file_count,
            "sk_md_length": s.sk_md_length,
        } for s in skills],
        "l1_containment": [asdict(r) for r in l1],
        "l2_overlap":     [asdict(r) for r in l2],
        "l3_association": [asdict(r) for r in l3],
    }
    OUTPUT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Pretty print
    print("=" * 60)
    print(f"📊 Skills 总数: {len(skills)}")
    print("=" * 60)

    print(f"\n📦 L1【包含关系】({len(l1)} 对) — 建议直接删除被包含方")
    if not l1:
        print("   无")
    for r in l1:
        print(f"   ✅ {r.superset}  ⊇  {r.subset}")
        print(f"      原因: {r.reason}\n")

    print(f"🔀 L2【重叠关系】({len(l2)} 对) — 请确认是否融合")
    if not l2:
        print("   无")
    for r in l2:
        print(f"   ⚠️  {r.skill_a}  ∩  {r.skill_b}")
        print(f"      共享词: {r.shared_keywords}")
        print(f"      {r.recommendation}\n")

    print(f"🔗 L3【关联关系】({len(l3)} 对) — 建议评估是否融合")
    if not l3:
        print("   无")
    for r in l3:
        print(f"   💡 {r.skill_a}  ↔  {r.skill_b}")
        print(f"      {r.link_reason}")
        print(f"      提议: {r.proposal}\n")

    print(f"完整报告 → {OUTPUT_FILE}")
    return report


if __name__ == "__main__":
    main()
