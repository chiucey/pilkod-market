"""Read-only, bounded discovery of project instruction files and build markers."""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

RULES = {"AGENTS.md", "CLAUDE.md", "instructions.md", "INSTRUCTIONS.md", "instance.md", "INSTANCE.md"}
MARKERS = {"Package.swift", "package.json", "pyproject.toml", "requirements.txt", "Podfile", "Gemfile", "Cargo.toml", "go.mod"}
SKIP = {".git", ".venv", "venv", "node_modules", "DerivedData", "SourcePackages", ".build", "Pods", "output", "dist", "build"}

def inventory(root, max_depth=5):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    rules, markers, skipped = [], [], []
    seen = set()
    def add_rule(path, scope):
        if path.is_symlink() or not path.is_file() or path in seen:
            return
        seen.add(path)
        if path.stat().st_size > 1024 * 1024:
            skipped.append({"path": str(path), "reason": "rule exceeds 1 MiB"})
            return
        rules.append({"path": str(path), "scope": scope, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    for parent in reversed(root.parents):
        for name in sorted(RULES):
            add_rule(parent / name, "ancestor-candidate")
    for folder, dirs, files in os.walk(root, followlinks=False):
        here = Path(folder)
        depth = len(here.relative_to(root).parts)
        keep = []
        for name in sorted(dirs):
            p = here / name
            if name in SKIP or p.is_symlink() or depth >= max_depth:
                skipped.append({"path": str(p), "reason": "excluded, symlink, or depth limit"})
            elif p.suffix in {".xcodeproj", ".xcworkspace"}:
                markers.append(str(p))
            else:
                keep.append(name)
        dirs[:] = keep
        for name in sorted(files):
            p = here / name
            if name in RULES:
                add_rule(p, "root-candidate" if depth == 0 else "nested-candidate")
            elif name in MARKERS and not p.is_symlink():
                markers.append(str(p))
    return {"root": str(root), "max_depth": max_depth, "rules": rules, "build_markers": markers,
            "tools": {n: shutil.which(n) is not None for n in ("git", "node", "python3", "xcodebuild", "xcrun")},
            "skipped": skipped, "notice": "Discovery only. Read applicable files and check deeper target rules before edits; no instructions executed."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True)
    p.add_argument("--max-depth", type=int, default=5, choices=range(0, 13))
    a = p.parse_args()
    try:
        print(json.dumps(inventory(a.root, a.max_depth), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as e:
        p.exit(2, str(e) + "\n")

if __name__ == "__main__":
    main()
