#!/usr/bin/env python3
"""Research Stack Validator v3 — respects code blocks in duplicate detection."""
import re, sys
from pathlib import Path
from collections import Counter

def validate(path):
    c = path.read_text()
    lines = c.split('\n')
    issues = []

    if not c.startswith('---'):
        issues.append("Missing YAML front matter")
    name_m = re.search(r'^name:\s*(.+)$', c, re.MULTILINE)
    name = name_m.group(1).strip() if name_m else "MISSING"
    if not name_m:
        issues.append("Missing 'name:' field")
    elif not re.match(r'^[a-z0-9-]+$', name):
        issues.append(f"Name '{name}' not kebab-case")
    if 'research-stack' not in name and 'orchestrator' not in name.lower():
        issues.append(f"Name should include 'research-stack' prefix")
    desc_m = re.search(r'^description:\s*(.+)$', c, re.MULTILINE)
    if not desc_m:
        issues.append("Missing 'description:'")
    else:
        desc = desc_m.group(1)
        if len(desc) > 1024: issues.append(f"Description too long ({len(desc)} chars)")
        if '<' in desc or '>' in desc: issues.append("Description has angle brackets")

    # Skip code blocks when checking for duplicate headers
    in_code = False
    headers = []
    for l in lines:
        if l.strip().startswith('```'):
            in_code = not in_code
            continue
        if not in_code and l.startswith('## ') and l.strip() != '## ':
            headers.append(l.strip())
    dups = [(h, n) for h, n in Counter(headers).items() if n > 1]
    for h, n in dups:
        issues.append(f"Duplicate header: '{h[:50]}' x{n}")

    if len(lines) > 700:
        issues.append(f"File too long ({len(lines)} lines)")

    return len(issues) == 0, issues, len(lines)


BASE = Path('/workspace/skills/research-stack')
files = {
    'ORCHESTRATOR': BASE / 'ORCHESTRATOR.md',
    'PM':            BASE / 'roles/project-manager/SKILL.md',
    'LR':            BASE / 'roles/literature-reviewer/SKILL.md',
    'ED':            BASE / 'roles/experimental-designer/SKILL.md',
    'DA':            BASE / 'roles/data-analyst/SKILL.md',
    'AW':            BASE / 'roles/academic-writer/SKILL.md',
    'PR':            BASE / 'roles/peer-reviewer/SKILL.md',
}

print("🔍 Research Stack Validation v3\n")
all_pass = True
for role, path in sorted(files.items()):
    ok, issues, n = validate(path)
    if not ok: all_pass = False
    print(f"{'✅ PASS' if ok else '❌ FAIL'}  {role}: {n} lines")
    for iss in issues:
        print(f"        {iss}")

refs = sorted((BASE / 'references').glob('*.md'))
scripts = sorted((BASE / 'scripts').glob('*.py'))
print(f"\n📦 references/: {len(refs)} files")
for r in refs:
    print(f"   {r.name} ({len(r.read_text().splitlines())} lines)")
print(f"\nscripts/: {len(scripts)} files")
for s in scripts:
    print(f"   {s.name}")
baks = list(BASE.rglob('*.bak'))
print(f"\n.bak files: {len(baks)} {'✅ none' if not baks else '❌ ' + str([str(b) for b in baks])}")
print(f"\n{'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME ISSUES REMAIN'}")
sys.exit(0 if all_pass else 1)
