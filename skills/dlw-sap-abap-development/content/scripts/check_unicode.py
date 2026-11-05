#!/usr/bin/env python3
"""Scan .md and .py files for non-ASCII or special characters."""

import os
from pathlib import Path

def check_files(skill_dir: str) -> list:
    issues = []
    skill_path = Path(skill_dir)

    for ext in ["*.md", "*.py"]:
        for f in skill_path.rglob(ext):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read()

                for line_num, line in enumerate(content.split('\n'), 1):
                    for char_pos, char in enumerate(line, 1):
                        code = ord(char)
                        # Flag: non-ASCII (above U+007F)
                        if code > 127:
                            issues.append(f"{f}:{line_num}:{char_pos} - U+{code:04X} '{char}'")
                        # Also flag control chars
                        elif char in ['\x00', '\x1b']:
                            issues.append(f"{f}:{line_num}:{char_pos} - Control char U+{code:02X}")
            except Exception as e:
                issues.append(f"Error reading {f}: {e}")

    return issues

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    issues = check_files(skill_dir)

    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("All files are clean - no Unicode or special characters detected.")
        sys.exit(0)
