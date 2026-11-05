#!/usr/bin/env python3
"""
Memory Archive Tool - Archive old memory files by date
Usage: python archive_memories.py [--days 30] [--dry-run]
"""

import re
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

def parse_date_from_filename(filename):
    """Extract date from filename YYYY-MM-DD"""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))
    return None

def should_archive(file_date, days_threshold=30):
    """Check if file should be archived (older than N days)"""
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    return file_date < cutoff_date

def archive_memories(memory_dir="/memories", days_threshold=30, dry_run=False):
    """Archive old memory files"""
    memory_path = Path(memory_dir)
    
    if not memory_path.exists():
        print(f"Error: Memory directory does not exist: {memory_dir}")
        return []
    
    archived = []
    
    # Archive session files older than threshold
    sessions_dir = memory_path / "sessions"
    if sessions_dir.exists():
        for file_path in sessions_dir.glob("*-session.md"):
            file_date = parse_date_from_filename(file_path.name)
            if file_date and should_archive(file_date, days_threshold):
                archive_dir = memory_path / "archive" / file_date.strftime("%Y-%m")
                target_path = archive_dir / file_path.name
                
                if dry_run:
                    print(f"[DRY-RUN] Would move: {file_path.name} -> {archive_dir}/")
                else:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(target_path))
                    print(f"Archived: {file_path.name} -> {archive_dir}/")
                
                archived.append({
                    'source': str(file_path),
                    'target': str(target_path),
                    'date': file_date
                })
    
    # Archive root-level date files
    for file_path in memory_path.glob("*.md"):
        if file_path.name in ['index.md']:
            continue
        file_date = parse_date_from_filename(file_path.name)
        if file_date and should_archive(file_date, days_threshold):
            archive_dir = memory_path / "archive" / file_date.strftime("%Y-%m")
            target_path = archive_dir / file_path.name
            
            if dry_run:
                print(f"[DRY-RUN] Would move: {file_path.name} -> {archive_dir}/")
            else:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(target_path))
                print(f"Archived: {file_path.name} -> {archive_dir}/")
            
            archived.append({
                'source': str(file_path),
                'target': str(target_path),
                'date': file_date
            })
    
    return archived

def main():
    parser = argparse.ArgumentParser(description='Archive old memory files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview what would be archived')
    parser.add_argument('--days', type=int, default=30, 
                       help='Archive files older than N days (default: 30)')
    parser.add_argument('--dir', '-d', default='/memories', 
                       help='Memory directory')
    args = parser.parse_args()
    
    print(f"Memory Archive Tool")
    print(f"Mode: {'DRY-RUN (preview)' if args.dry_run else 'LIVE'}")
    print(f"Directory: {args.dir}")
    print(f"Archive files older than {args.days} days\n")
    
    archived = archive_memories(
        memory_dir=args.dir,
        days_threshold=args.days, 
        dry_run=args.dry_run
    )
    
    if archived:
        print(f"\nTotal archived: {len(archived)} files")
    else:
        print("\nNo files to archive")

if __name__ == "__main__":
    main()
