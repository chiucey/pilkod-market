#!/usr/bin/env python3
"""Test script for quick_validate.py"""

import sys
import subprocess
from pathlib import Path

def test_validation():
    """Run validation tests."""
    script_path = Path(__file__).parent / "quick_validate.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    return result.returncode == 0

if __name__ == "__main__":
    success = test_validation()
    sys.exit(0 if success else 1)
