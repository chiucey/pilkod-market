#!/usr/bin/env python3
"""
Self-Improving Agent Skill - Main Entry
Logs learnings, errors, and feature requests to markdown files.
Supports promotion of key insights to project memory files.
Enhanced with evolution tracking and pattern recognition.
"""

import os
import json
from datetime import datetime
import random
import string
import re

# Default configuration
DEFAULT_LEARNINGS_DIR = "./.learnings"
DEFAULT_PROMOTE_TARGETS = {
    "claude": "./CLAUDE.md",
    "agents": "./AGENTS.md",
    "soul": "./SOUL.md",
    "tools": "./TOOLS.md"
}

# Evolution tracking file
EVOLUTION_FILE = ".learnings/EVOLUTION.md"


def generate_id(entry_type, date_str=None):
    """Generate unique entry ID: TYPE-YYYYMMDD-XXX"""
    if not date_str:
        date_str = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{entry_type}-{date_str}-{random_suffix}"


def ensure_dir(path):
    """Ensure directory exists"""
    if not os.path.exists(path):
        os.makedirs(path)


def get_learnings_dir():
    """Get learnings directory from env or default"""
    return os.environ.get("LEARNINGS_DIR", DEFAULT_LEARNINGS_DIR)


def get_promote_target(target_type):
    """Get promotion target file path"""
    env_var = f"PROMOTE_TARGET_{target_type.upper()}"
    return os.environ.get(env_var, DEFAULT_PROMOTE_TARGETS.get(target_type, f"./{target_type.upper()}.md"))


def append_to_file(file_path, content):
    """Append content to file, creating if needed"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content + "\n")


def record_evolution(action_type, summary):
    """Record evolution event to evolution tracking file"""
    evolution_dir = os.path.join(get_learnings_dir(), "..")
    ensure_dir(evolution_dir)

    evolution_file = os.path.join(get_learnings_dir(), EVOLUTION_FILE)

    entry_id = generate_id("EVO")
    timestamp = datetime.utcnow().isoformat() + "Z"

    content = f"""
## [{entry_id}] {action_type}

**Logged**: {timestamp}

### Summary
{summary}

### Metadata
- Iteration-Count: {get_evolution_count() + 1}
- Experience-Count: {count_entries('LEARNINGS.md')}
- Lesson-Count: {count_entries('ERRORS.md')}
"""
    append_to_file(evolution_file, content.strip())


def get_evolution_count():
    """Get current evolution count"""
    evolution_file = os.path.join(get_learnings_dir(), EVOLUTION_FILE)
    if not os.path.exists(evolution_file):
        return 0

    with open(evolution_file, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'## \[EVO-(\d{8})-([A-Z0-9]+)\]', content)
        return len(matches)


def count_entries(file_name):
    """Count entries in a file"""
    file_path = os.path.join(get_learnings_dir(), file_name)
    if not os.path.exists(file_path):
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(r'^## \[', content, re.MULTILINE))


def extract_pattern_key(summary, details):
    """Extract pattern key from summary and details for pattern recognition"""
    # Look for common patterns
    pattern_indicators = [
        r'(\w+)\s+api\s+call',
        r'(\w+)\s+command\s+fails',
        r'(\w+)\s+method\s+works',
        r'(\w+)\s+pattern\s+repeats',
        r'similar\s+to\s+(\w+)',
        r'same\s+as\s+(\w+)',
        r'always\s+(\w+)'
    ]

    combined_text = f"{summary} {details}".lower()
    for pattern in pattern_indicators:
        match = re.search(pattern, combined_text)
        if match:
            return f"pattern-{match.group(1)}"

    return ""


def log_learning(params):
    """Log a learning entry"""
    learnings_dir = get_learnings_dir()
    file_path = os.path.join(learnings_dir, "LEARNINGS.md")

    entry_id = generate_id("LRN")
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Extract pattern key for pattern recognition
    pattern_key = params.get('pattern_key', '') or extract_pattern_key(
        params.get('summary', ''),
        params.get('details', '')
    )

    content = f"""
## [{entry_id}] {params.get('category', 'general')}

**Logged**: {timestamp}
**Priority**: {params.get('priority', 'medium')}
**Status**: pending
**Area**: {params.get('area', 'unknown')}

### Summary
{params.get('summary', '')}

### Details
{params.get('details', '')}

### Suggested Action
{params.get('suggested_action', '')}

### Metadata
- Source: {params.get('source', 'conversation')}
- Related Files: {params.get('related_files', '')}
- Tags: {params.get('tags', '')}
- See Also: {params.get('see_also', '')}
- Pattern-Key: {pattern_key}
- Recurrence-Count: {params.get('recurrence_count', '1')}
- First-Seen: {params.get('first_seen', timestamp)}
- Last-Seen: {params.get('last_seen', timestamp)}

---
"""
    append_to_file(file_path, content.strip())

    # Record evolution event
    record_evolution("New Learning", params.get('summary', ''))

    return {"entry_id": entry_id, "file_path": file_path}


def log_error(params):
    """Log an error entry"""
    learnings_dir = get_learnings_dir()
    file_path = os.path.join(learnings_dir, "ERRORS.md")

    entry_id = generate_id("ERR")
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Extract pattern key
    pattern_key = params.get('pattern_key', '') or extract_pattern_key(
        params.get('summary', ''),
        params.get('error_message', '')
    )

    content = f"""
## [{entry_id}] {params.get('skill_or_command', 'unknown')}

**Logged**: {timestamp}
**Priority**: {params.get('priority', 'high')}
**Status**: pending
**Area**: {params.get('area', 'unknown')}

### Summary
{params.get('summary', '')}

### Error
```
{params.get('error_message', '')}
```

### Context
- Command/operation attempted: {params.get('command_attempted', '')}
- Input or parameters used: {params.get('input_params', '')}
- Environment details: {params.get('env_details', '')}

### Suggested Fix
{params.get('suggested_fix', '')}

### Root Cause Analysis
{params.get('root_cause', '')}

### Metadata
- Reproducible: {params.get('reproducible', 'unknown')}
- Related Files: {params.get('related_files', '')}
- Pattern-Key: {pattern_key}
- See Also: {params.get('see_also', '')}

---
"""
    append_to_file(file_path, content.strip())

    # Record evolution event
    record_evolution("Error Learned", params.get('summary', ''))

    return {"entry_id": entry_id, "file_path": file_path}


def log_feature_request(params):
    """Log a feature request entry"""
    learnings_dir = get_learnings_dir()
    file_path = os.path.join(learnings_dir, "FEATURE_REQUESTS.md")

    entry_id = generate_id("FEAT")
    timestamp = datetime.utcnow().isoformat() + "Z"

    content = f"""
## [{entry_id}] {params.get('capability_name', 'unknown')}

**Logged**: {timestamp}
**Priority**: {params.get('priority', 'medium')}
**Status**: pending
**Area**: {params.get('area', 'unknown')}

### Requested Capability
{params.get('requested_capability', '')}

### User Context
{params.get('user_context', '')}

### Complexity Estimate
{params.get('complexity', 'medium')}

### Suggested Implementation
{params.get('suggested_implementation', '')}

### Metadata
- Frequency: {params.get('frequency', 'first_time')}
- Related Features: {params.get('related_features', '')}

---
"""
    append_to_file(file_path, content.strip())

    # Record evolution event
    record_evolution("Feature Request", params.get('requested_capability', ''))

    return {"entry_id": entry_id, "file_path": file_path}


def promote_learning(params):
    """Promote a learning to project memory"""
    target_type = params.get('target_type', 'claude')
    target_file = get_promote_target(target_type)
    content = params.get('content', '')

    if not content:
        return {"status": "error", "message": "No content provided for promotion"}

    append_to_file(target_file, f"\n{content.strip()}\n")

    # Record promotion evolution
    record_evolution("Knowledge Promoted", f"Promoted to {target_type}: {content[:50]}...")

    return {"status": "success", "target_file": target_file}


def review_learnings(params=None):
    """Review learnings and generate status report"""
    learnings_dir = get_learnings_dir()

    learnings_file = os.path.join(learnings_dir, "LEARNINGS.md")
    errors_file = os.path.join(learnings_dir, "ERRORS.md")
    features_file = os.path.join(learnings_dir, "FEATURE_REQUESTS.md")

    learnings_count = count_entries("LEARNINGS.md")
    errors_count = count_entries("ERRORS.md")
    features_count = count_entries("FEATURE_REQUESTS.md")
    evolution_count = get_evolution_count()

    # Count pending items
    pending_learnings = 0
    pending_errors = 0
    pending_features = 0

    for file_name, count_var in [("LEARNINGS.md", "learnings"), ("ERRORS.md", "errors"), ("FEATURE_REQUESTS.md", "features")]:
        file_path = os.path.join(learnings_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                pending = len(re.findall(r'\*\*Status\*\*: pending', content))
                if file_name == "LEARNINGS.md":
                    pending_learnings = pending
                elif file_name == "ERRORS.md":
                    pending_errors = pending
                else:
                    pending_features = pending

    return {
        "status": "success",
        "data": {
            "experience_count": learnings_count,
            "lesson_count": errors_count,
            "feature_request_count": features_count,
            "iteration_count": evolution_count,
            "pending_learnings": pending_learnings,
            "pending_errors": pending_errors,
            "pending_features": pending_features,
            "evolution_trend": "improving" if evolution_count > 10 else "growing"
        }
    }


def update_evolution_state(params):
    """Update evolution state with new metrics"""
    learnings_dir = get_learnings_dir()
    evolution_file = os.path.join(learnings_dir, "EVOLUTION_STATE.md")

    learnings_count = count_entries('LEARNINGS.md')
    errors_count = count_entries('ERRORS.md')
    evolution_count = get_evolution_count()

    content = f"""# Evolution State

**Last Updated**: {datetime.utcnow().isoformat()}Z

## Statistics
- Total Learnings: {learnings_count}
- Total Errors/Lessons: {errors_count}
- Total Iterations: {evolution_count}
- Success Rate: {calculate_success_rate()}

## Growth Trend
{generate_growth_trend()}

## Recent Evolutions
"""
    append_to_file(evolution_file, content.strip())

    return {"status": "success", "evolution_count": evolution_count}


def calculate_success_rate():
    """Calculate success rate from learnings vs errors"""
    learnings = count_entries('LEARNINGS.md')
    errors = count_entries('ERRORS.md')
    total = learnings + errors

    if total == 0:
        return "N/A"

    rate = (learnings / total) * 100
    return f"{rate:.1f}%"


def generate_growth_trend():
    """Generate visual growth trend"""
    learnings = count_entries('LEARNINGS.md')
    errors = count_entries('ERRORS.md')

    if learnings > errors:
        return "📈 Learning faster than failing - positive growth"
    elif learnings < errors:
        return "📉 Need to learn from more mistakes"
    else:
        return "➡️ Balanced learning and adapting"


def run(input_data=None):
    """Main skill entry point"""
    try:
        if not input_data:
            input_data = {}

        action = input_data.get('action', 'log_learning')
        params = input_data.get('params', {})

        if action == 'log_learning':
            result = log_learning(params)
        elif action == 'log_error':
            result = log_error(params)
        elif action == 'log_feature_request':
            result = log_feature_request(params)
        elif action == 'promote_learning':
            result = promote_learning(params)
        elif action == 'review_learnings':
            result = review_learnings(params)
        elif action == 'update_evolution_state':
            result = update_evolution_state(params)
        else:
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"Unknown action: {action}"
            }

        return {
            "status": "success",
            "data": result,
            "message_for_user": f"Action '{action}' completed successfully."
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"Execution failed: {str(e)}"
        }


if __name__ == "__main__":
    import sys
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        if input_json:
            input_data = json.loads(input_json)
        else:
            input_data = {}
    else:
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False))
