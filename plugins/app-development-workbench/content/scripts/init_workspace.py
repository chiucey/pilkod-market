"""Create project delivery records in a new directory; never overwrite files."""
import argparse
import json
from pathlib import Path

TEMPLATES = {
    "scope.md": "# Scope\n\nProject: {name}\n\n- User objective: pending\n- Included/excluded: pending\n- Source baseline: pending\n- Locked decisions: pending\n- Acceptance path: pending\n",
    "rules.md": "# Applicable project rules\n\n| File | Scope | Constraint | Implementation | Verification |\n|---|---|---|---|---|\n",
    "api-contract.md": "# API contract\n\n| Operation | Method/path | Auth/owner | Request | Response | Errors | Idempotency/version |\n|---|---|---|---|---|---|---|\n",
    "component-map.md": "# Component map\n\n| Existing structure | Shared component | Semantic state | Callers | Proof |\n|---|---|---|---|---|\n",
}

def initialize(output, name):
    output = Path(output).absolute()
    if not name.strip() or len(name) > 200 or any(ord(c) < 32 for c in name):
        raise ValueError("project-name must be a nonblank single line of at most 200 characters")
    # mkdir is exclusive even if another process races with this invocation.
    output.mkdir(parents=True, exist_ok=False)
    for filename, content in TEMPLATES.items():
        with (output / filename).open("x", encoding="utf-8") as f:
            f.write(content.format(name=name))
    data = {
        "design-state.json": {"schema_version": 1, "project_name": name, "revision": "r1", "pages": [], "directions": [], "selections": [], "scenarios": []},
        "evidence.json": {"schema_version": 1, "checks": [], "user_acceptance": "not-run", "publication": "not-run"},
    }
    for filename, content in data.items():
        with (output / filename).open("x", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return {"output": str(output), "created": sorted([*TEMPLATES, *data]), "status": "templates-only"}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--project-name", required=True)
    a = p.parse_args()
    try:
        print(json.dumps(initialize(a.output, a.project_name), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as e:
        p.exit(2, str(e) + "\n")

if __name__ == "__main__":
    main()
