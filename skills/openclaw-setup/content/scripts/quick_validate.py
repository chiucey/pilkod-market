#!/usr/bin/env python3
"""Quick validator for skill folder integrity."""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")


def _extract_frontmatter(content: str) -> Optional[str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index])
    return None


def _parse_simple_frontmatter(frontmatter_text: str) -> Optional[dict[str, str]]:
    data: dict[str, str] = {}
    current_key: Optional[str] = None

    for raw_line in frontmatter_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        is_indented = raw_line[:1].isspace()
        if is_indented:
            if current_key is None:
                return None
            current = data[current_key]
            data[current_key] = f"{current}\n{stripped}" if current else stripped
            continue

        if ":" not in stripped:
            return None

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            return None
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        data[key] = value
        current_key = key

    return data


def _validate_meta(meta_path: Path) -> Tuple[bool, str]:
    if not meta_path.exists():
        return False, "_meta.json not found"
    if not meta_path.is_file():
        return False, "_meta.json exists but is not a file"

    try:
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"_meta.json invalid JSON: {exc}"
    except OSError as exc:
        return False, f"Could not read _meta.json: {exc}"

    if not isinstance(payload, dict):
        return False, "_meta.json must be a JSON object"

    if "id" not in payload:
        return False, "_meta.json missing required key: id"
    if "version" not in payload:
        return False, "_meta.json missing required key: version"

    skill_id = payload.get("id")
    if not isinstance(skill_id, str) or not skill_id.strip():
        return False, "_meta.json id must be a non-empty string"

    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        return False, "_meta.json version must be a non-empty string"
    if not SEMVER_PATTERN.match(version.strip()):
        return False, f"_meta.json version is not valid semver: {version}"

    return True, "meta ok"


def validate_skill(skill_path: Union[str, Path]) -> Tuple[bool, str]:
    root = Path(skill_path).resolve()
    if not root.exists():
        return False, f"Skill folder not found: {root}"
    if not root.is_dir():
        return False, f"Skill path is not a directory: {root}"

    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    meta_ok, meta_message = _validate_meta(root / "_meta.json")
    if not meta_ok:
        return False, meta_message

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"Could not read SKILL.md: {exc}"

    frontmatter_text = _extract_frontmatter(content)
    if frontmatter_text is None:
        return False, "Invalid frontmatter format"

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, "Frontmatter must be a YAML dictionary"
        except yaml.YAMLError as exc:
            return False, f"Invalid YAML in frontmatter: {exc}"
    else:
        frontmatter = _parse_simple_frontmatter(frontmatter_text)
        if frontmatter is None:
            return False, "Invalid YAML in frontmatter: unsupported syntax without PyYAML"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        allowed = ", ".join(sorted(ALLOWED_FRONTMATTER_KEYS))
        unexpected = ", ".join(sorted(unexpected_keys))
        return False, f"Unexpected frontmatter keys: {unexpected}. Allowed: {allowed}"

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name.strip():
        return False, "Missing or invalid 'name' in frontmatter"
    if not isinstance(description, str) or not description.strip():
        return False, "Missing or invalid 'description' in frontmatter"

    normalized_name = name.strip()
    if len(normalized_name) > MAX_SKILL_NAME_LENGTH:
        return False, f"Skill name too long ({len(normalized_name)}). Max is {MAX_SKILL_NAME_LENGTH}"
    if not re.match(r"^[a-z0-9-]+$", normalized_name):
        return False, "Skill name must be hyphen-case (lowercase letters, digits, hyphens)"
    if normalized_name.startswith("-") or normalized_name.endswith("-") or "--" in normalized_name:
        return False, "Skill name cannot start/end with hyphen or contain consecutive hyphens"

    normalized_description = description.strip()
    if len(normalized_description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description too long ({len(normalized_description)}). Max is {MAX_DESCRIPTION_LENGTH}"
    if "<" in normalized_description or ">" in normalized_description:
        return False, "Description cannot contain angle brackets"

    if root.name != normalized_name:
        return False, f"Skill directory name '{root.name}' must match frontmatter name '{normalized_name}'"

    return True, "Skill is valid"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/quick_validate.py <skill_directory>")
        return 1
    valid, message = validate_skill(sys.argv[1])
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
