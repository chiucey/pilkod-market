#!/usr/bin/env python3
"""
Create Memory - Create generic memory files for sessions, projects, or knowledge.
Usage: python create_memory.py --type {session|project|knowledge} --name NAME [--date YYYY-MM-DD]
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def get_weekday(date):
    """Get weekday abbreviation"""
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return weekdays[date.weekday()]

def create_session_memory(date_str=None, memory_dir="/memories"):
    """Create session memory file"""
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")
    
    sessions_dir = Path(memory_dir) / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    file_path = sessions_dir / f"{date_str}-session.md"
    
    if file_path.exists():
        print(f"File already exists: {file_path}")
        return file_path
    
    template = f"""# Session: {date_str}

## Session Summary
Brief description of this session's purpose and context.

## Key Decisions
- Decision 1
- Decision 2

## Next Steps
- [ ] Task 1
- [ ] Task 2

## Important Findings
Notable discoveries or information gathered during the session.

## Notes
Additional notes and observations.

---

*Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"Created session memory: {file_path}")
    return file_path

def create_project_memory(project_name, memory_dir="/memories"):
    """Create project memory folder with overview"""
    projects_dir = Path(memory_dir) / "projects"
    project_dir = projects_dir / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    files_created = []
    
    # Create overview.md
    overview_path = project_dir / "overview.md"
    if not overview_path.exists():
        overview_content = f"""# Project: {project_name}

## Overview
What this project is about.

## Current Status
Current state and recent developments.

## Goals
- Primary goal
- Secondary goals

## Stakeholders
Who is involved in this project.

## Resources
Available resources and tools.

## Progress Log
### {datetime.now().strftime('%Y-%m-%d')}
- Project initialized
"""
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(overview_content)
        files_created.append(overview_path)
    
    # Create decisions.md
    decisions_path = project_dir / "decisions.md"
    if not decisions_path.exists():
        decisions_content = f"""# Decisions Log: {project_name}

## Architecture Decisions

### YYYY-MM-DD: [Title]
**Decision**: What was decided
**Rationale**: Why this approach was chosen
**Alternatives Considered**: Other options that were rejected

## Technical Decisions

## Process Decisions

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        with open(decisions_path, 'w', encoding='utf-8') as f:
            f.write(decisions_content)
        files_created.append(decisions_path)
    
    # Create progress.md
    progress_path = project_dir / "progress.md"
    if not progress_path.exists():
        progress_content = f"""# Progress: {project_name}

## Timeline

### {datetime.now().strftime('%Y-%m-%d')}
- Project started

## Milestones

| Milestone | Status | Due Date |
|-----------|--------|----------|
| Milestone 1 | [ ] | YYYY-MM-DD |

## Current Sprint/Phase

## Blockers

"""
        with open(progress_path, 'w', encoding='utf-8') as f:
            f.write(progress_content)
        files_created.append(progress_path)
    
    for f in files_created:
        print(f"Created: {f}")
    return files_created

def create_knowledge_memory(topic_name, memory_dir="/memories"):
    """Create knowledge note"""
    knowledge_dir = Path(memory_dir) / "knowledge" / "topics"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    file_path = knowledge_dir / f"{topic_name}.md"
    
    if file_path.exists():
        print(f"File already exists: {file_path}")
        return file_path
    
    template = f"""# Topic: {topic_name}

## Summary
One-paragraph overview of this topic.

## Key Concepts
- **Concept 1**: Explanation of the concept
- **Concept 2**: Explanation of the concept
- **Concept 3**: Explanation of the concept

## Details
Detailed explanation and examples.

## Examples
```python
# Example code or usage
```

## Common Use Cases
- Use case 1
- Use case 2

## Resources
- [Resource 1](url)
- [Resource 2](url)

## Related Topics
- Related Topic 1
- Related Topic 2

---
*Created: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"Created knowledge note: {file_path}")
    return file_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Create memory file')
    parser.add_argument('--type', '-t', required=True, 
                        choices=['session', 'project', 'knowledge'],
                        help='Type of memory to create')
    parser.add_argument('--name', '-n', 
                        help='Name for project or topic (required for project/knowledge)')
    parser.add_argument('--date', '-d', 
                        help='Date in YYYY-MM-DD format (for session memory)')
    parser.add_argument('--dir', default='/memories',
                        help='Base memory directory (default: /memories)')
    
    args = parser.parse_args()
    
    if args.type == 'session':
        create_session_memory(args.date, args.dir)
    elif args.type == 'project':
        if not args.name:
            print("Error: --name is required for project memory")
            sys.exit(1)
        create_project_memory(args.name, args.dir)
    elif args.type == 'knowledge':
        if not args.name:
            print("Error: --name is required for knowledge memory")
            sys.exit(1)
        create_knowledge_memory(args.name, args.dir)

if __name__ == "__main__":
    main()
