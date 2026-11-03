#!/usr/bin/env python3
"""
Memory Index Generator - Generate index of all memories in /memories
Usage: python generate_index.py [--output index.md]
"""

import re
from pathlib import Path
from datetime import datetime

def parse_date_from_filename(filename):
    """Extract date from filename"""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None

def get_file_info(file_path):
    """Get file metadata"""
    stat = file_path.stat()
    return {
        'name': file_path.name,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
    }

def extract_title(file_path):
    """Extract title from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
                if line.startswith('## '):
                    return line[3:].strip()
    except:
        pass
    return file_path.stem

def generate_index(memory_dir="/memories", output_file=None):
    """Generate index of memory directory"""
    memory_path = Path(memory_dir)
    
    if not memory_path.exists():
        print(f"Error: Memory directory does not exist: {memory_dir}")
        return None
    
    lines = [
        "# Memory Index",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## Directory Structure",
        "",
        "```",
        "/memories/",
        "├── sessions/              # Session-specific memories",
        "├── projects/              # Project memories",
        "│   └── {project-name}/",
        "│       ├── overview.md",
        "│       ├── decisions.md",
        "│       └── progress.md",
        "├── knowledge/             # Knowledge base",
        "│   └── topics/",
        "├── archive/              # Archived memories (by month)",
        "└── index.md              # This index",
        "```",
        "",
    ]
    
    # Sessions
    sessions_dir = memory_path / "sessions"
    if sessions_dir.exists():
        session_files = sorted(sessions_dir.glob("*-session.md"), reverse=True)
        lines.extend(["## Sessions", ""])
        if session_files:
            lines.append("| Date | File | Modified |")
            lines.append("|------|------|----------|")
            for f in session_files[:20]:
                date = parse_date_from_filename(f.name) or '-'
                info = get_file_info(f)
                lines.append(f"| {date} | `{f.name}` | {info['modified']} |")
            if len(session_files) > 20:
                lines.append(f"\n*... and {len(session_files) - 20} more session files*")
        else:
            lines.append("*No session files*")
        lines.append("")
    
    # Projects
    projects_dir = memory_path / "projects"
    if projects_dir.exists():
        projects = [d for d in projects_dir.iterdir() if d.is_dir()]
        lines.extend(["## Projects", ""])
        if projects:
            for project in sorted(projects):
                overview = project / "overview.md"
                title = extract_title(overview) if overview.exists() else project.name
                lines.append(f"- **{project.name}**: {title}")
            lines.append("")
            lines.append("| Project | Overview |")
            lines.append("|---------|----------|")
            for project in sorted(projects):
                overview = project / "overview.md"
                title = extract_title(overview) if overview.exists() else '-'
                lines.append(f"| `{project.name}/` | {title} |")
        else:
            lines.append("*No projects*")
        lines.append("")
    
    # Knowledge
    knowledge_dir = memory_path / "knowledge" / "topics"
    if knowledge_dir.exists():
        topic_files = sorted(knowledge_dir.glob("*.md"))
        lines.extend(["## Knowledge Base", ""])
        if topic_files:
            lines.append("| Topic | Title |")
            lines.append("|-------|-------|")
            for f in topic_files:
                title = extract_title(f)
                lines.append(f"| `{f.stem}` | {title} |")
        else:
            lines.append("*No knowledge notes*")
        lines.append("")
    
    # Archive
    archive_dir = memory_path / "archive"
    if archive_dir.exists():
        months = sorted([d for d in archive_dir.iterdir() if d.is_dir()], reverse=True)
        lines.extend(["## Archive", ""])
        if months:
            lines.append("| Month | Files |")
            lines.append("|-------|-------|")
            for month in months[:12]:
                files = list(month.glob("*.md"))
                lines.append(f"| `{month.name}/` | {len(files)} files |")
            if len(months) > 12:
                lines.append(f"\n*... and {len(months) - 12} more months*")
        else:
            lines.append("*No archived files*")
        lines.append("")
    
    # Other files in root
    other_files = [f for f in memory_path.glob("*.md") if f.name not in ['index.md']]
    if other_files:
        lines.extend(["## Root Files", ""])
        lines.append("| File | Modified |")
        lines.append("|------|----------|")
        for f in sorted(other_files, key=lambda x: x.name):
            info = get_file_info(f)
            lines.append(f"| `{f.name}` | {info['modified']} |")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "*Managed by claw-memory-manager*",
    ])
    
    index_content = "\n".join(lines)
    
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = memory_path / "index.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"Index generated: {output_path}")
    return index_content

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate memory index')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--dir', '-d', default='/memories', help='Memory directory')
    args = parser.parse_args()
    
    generate_index(output_file=args.output, memory_dir=args.dir)

if __name__ == "__main__":
    main()
