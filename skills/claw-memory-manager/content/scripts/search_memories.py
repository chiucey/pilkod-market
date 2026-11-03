#!/usr/bin/env python3
"""
Memory Search Tool - Search memory documents by keyword
Usage: python search_memories.py "keyword" [--type md] [--dir /memories]
"""

import re
import argparse
from pathlib import Path

def search_in_file(file_path, keyword, context_lines=2):
    """Search for keyword in file, return matches with context"""
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    context = ''.join(lines[start:end])
                    matches.append({
                        'line_num': i + 1,
                        'context': context.strip()
                    })
    except Exception as e:
        pass
    return matches

def search_memories(keyword, memory_dir="/memories", file_type="md"):
    """Search all memory files"""
    memory_path = Path(memory_dir)
    
    if not memory_path.exists():
        print(f"Error: Memory directory does not exist: {memory_dir}")
        return []
    
    results = []
    pattern = f"**/*.{file_type}"
    
    for file_path in memory_path.glob(pattern):
        matches = search_in_file(file_path, keyword)
        if matches:
            results.append({
                'file': str(file_path.relative_to(memory_path)),
                'matches': matches
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Search memory files')
    parser.add_argument('keyword', help='Search keyword')
    parser.add_argument('--type', '-t', default='md', help='File type to search (default: md)')
    parser.add_argument('--context', '-c', type=int, default=2, help='Context lines (default: 2)')
    parser.add_argument('--dir', '-d', default='/memories', help='Memory directory')
    args = parser.parse_args()
    
    print(f"Searching in: {args.dir}")
    print(f"Keyword: '{args.keyword}'\n")
    
    results = search_memories(args.keyword, file_type=args.type, memory_dir=args.dir)
    
    if not results:
        print("No matches found.")
        return
    
    print(f"Found matches in {len(results)} file(s):\n")
    
    for result in results:
        print(f"📄 {result['file']}")
        print("-" * 50)
        for match in result['matches'][:5]:  # Max 5 matches per file
            print(f"  Line {match['line_num']}:")
            for line in match['context'].split('\n'):
                highlighted = re.sub(
                    f'({re.escape(args.keyword)})',
                    r'**\1**',
                    line,
                    flags=re.IGNORECASE
                )
                print(f"    {highlighted}")
            print()
        if len(result['matches']) > 5:
            print(f"  ... and {len(result['matches']) - 5} more matches")
        print()

if __name__ == "__main__":
    main()
