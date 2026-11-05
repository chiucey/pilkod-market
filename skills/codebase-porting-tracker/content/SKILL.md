---
name: codebase-porting-tracker
description: Codebase porting tracker. Use when users need to migrate a codebase from one language/framework to another, such as TypeScript to Python, Java to Go, React to Vue, etc. Provides automatic source code scanning, porting progress management, status tracking, and Markdown report generation.
---

# Codebase Porting Tracker

Universal codebase porting project management and progress tracking tool.

## Core Features

### 1. Source Code Structure Scanning

Automatically scan the target codebase, identify all source files and group them by module/directory:

- **File Type Detection**: Supports .py, .ts, .js, .java, .go, .rs, .cpp, .vue, .jsx, .tsx, etc.
- **Module Analysis**: Group by top-level directories or namespaces
- **File Statistics**: Count files and total lines per module

### 2. Porting Manifest Generation

Create structured porting manifests containing:

| Field | Description |
|-------|-------------|
| module_name | Module name |
| source_path | Original source path |
| target_path | Target path (after porting) |
| status | Status: planned/in_progress/completed/blocked |
| priority | Priority: high/medium/low |
| notes | Additional notes |
| dependencies | Other modules this depends on |

### 3. Status Tracking

Track the porting progress of each module:

- **Status Flow**: planned -> in_progress -> review -> completed
- **Blocked Markers**: Mark modules blocked by dependencies or issues
- **Timestamp Tracking**: Record when status changes occur

### 4. Markdown Report Generation

Generate beautiful Markdown reports containing:

- Project overview statistics
- Module progress tables
- Dependency graph (text version)
- Blocked items list
- Estimated completion rate

## Usage Scenarios

### Scenario 1: New Porting Project

```
User: I want to port a TypeScript project to Python
Assistant: Sure, let me help you create a porting manifest...
```

Workflow:
1. Scan TypeScript source structure
2. Identify core modules and dependencies
3. Generate initial porting manifest
4. Output Markdown manifest file

### Scenario 2: Track Progress

```
User: Update the porting progress
Assistant: Let me check the current manifest status...
```

Workflow:
1. Read existing manifest file
2. Summarize module statuses
3. Generate progress report
4. Mark blocked items and risk points

### Scenario 3: Add New Module

```
User: Added a new auth module that needs porting
Assistant: Sure, I'll add it to the manifest...
```

Workflow:
1. Scan new module source
2. Analyze dependencies
3. Insert into manifest and update position
4. Regenerate report

## Manifest File Format

```markdown
# Porting Manifest

## Project Overview

| Metric | Value |
|--------|-------|
| Total Modules | 12 |
| Completed | 5 |
| In Progress | 3 |
| Planned | 4 |
| Completion Rate | 41.7% |

## Module Status

| Module | Source Path | Target Path | Status | Priority | Dependencies |
|--------|-------------|-------------|--------|----------|--------------|
| auth | src/auth/ | py_src/auth/ | completed | - | - |
| api | src/api/ | py_src/api/ | in_progress | high | auth |
| models | src/models/ | py_src/models/ | in_progress | high | auth |
| utils | src/utils/ | py_src/utils/ | planned | medium | - |
| ... | ... | ... | ... | ... | ... |

## Blocked Items

No blocked items

## Last Updated

2026-03-31 22:00:00
```

## Script Tools

### scan_source.py

Source code scanning script for automatic codebase structure discovery:

```python
from pathlib import Path
from collections import Counter

def scan_codebase(root: Path, extensions: list[str]) -> dict:
    """Scan codebase and return module statistics"""
    files = []
    for ext in extensions:
        files.extend(root.rglob(f'*{ext}'))

    # Group by directory
    counter = Counter()
    for f in files:
        if len(f.relative_to(root).parts) > 1:
            module = f.relative_to(root).parts[0]
        else:
            module = f.stem
        counter[module] += 1

    return dict(counter)
```

### generate_manifest.py

Manifest generation script that creates Markdown reports from scan results:

```python
def generate_manifest(modules: dict, output_path: Path) -> str:
    """Generate Markdown-format porting manifest"""
    lines = [
        "# Porting Manifest",
        "",
        "## Project Overview",
        "",
        f"| Total Modules | {len(modules)} |",
        "",
        "## Module Status",
        "",
        "| Module | Files | Status |",
        "|--------|-------|--------|",
    ]

    for name, count in sorted(modules.items()):
        lines.append(f"| {name} | {count} | planned |")

    return "\n".join(lines)
```

### update_status.py

Status update script:

```python
def update_module_status(manifest: dict, module: str, new_status: str) -> dict:
    """Update module status"""
    manifest['modules'][module]['status'] = new_status
    manifest['last_updated'] = datetime.now().isoformat()
    return manifest
```

## Best Practices

### 1. Module Division Principles

- **Single Responsibility**: Each module handles one functional domain
- **Clear Dependencies**: Explicitly define inter-module dependencies
- **Appropriate Granularity**: Avoid modules that are too large or too small

### 2. Priority Ordering

1. **High-frequency Core Modules** - Low-level modules widely depended on by others
2. **Independent Functional Modules** - Features that don't depend on other modules
3. **Interface Definition Modules** - Parts that define inter-module interfaces
4. **Edge Functional Modules** - Independent but rarely used features

### 3. Progress Tracking Recommendations

- Update status daily
- Record blocking reasons
- Estimate remaining work
- Mark risk points

## Example Workflow

### Complete Porting Tracking Example

```
User: Track porting src/ from TypeScript to Python
Assistant: Great! Let me scan the source structure...

1. Scan complete:
   - Core modules: auth (5 files), api (12 files), models (8 files)
   - Utility modules: utils (3 files), helpers (4 files)
   - Test modules: tests (15 files)

2. Generated initial manifest:
   [Manifest file generated]

3. Current progress:
   Completed: 3/6 modules (50%)
   In Progress: 1 module

4. Risk warnings:
   - api module depends on auth, cannot start until auth is complete
   - models module has circular reference risk
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| source_root | ./src | Source code root directory |
| target_root | ./target | Target path root directory |
| file_extensions | [.py, .ts, .js] | File types to scan |
| output_format | markdown | Output format |
| include_tests | true | Whether to include test files |

## Related Files

- `scripts/scan_source.py` - Source code scanning tool
- `scripts/generate_manifest.py` - Manifest generator
- `scripts/update_status.py` - Status update tool
- `examples/manifest_template.md` - Manifest template

## Extension Suggestions

### Add Test Verification

```python
def verify_porting(original: Path, ported: Path) -> list[str]:
    """Verify porting completeness, return diff list"""
    issues = []
    # Check file correspondence
    # Check syntax correctness
    # Check functional consistency
    return issues
```

### Add CI Integration

Integrate progress checking in CI:

```yaml
# .github/workflows/porting-progress.yml
- name: Check Porting Progress
  run: |
    python scripts/update_status.py --check-blocked
    python scripts/generate_manifest.py --diff
```
