#!/usr/bin/env python3
"""
Quick validation script for md-to-xmind skill.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from md_to_xmind import convert_markdown_to_xmind, MarkdownParser


def test_basic_markdown():
    """Test basic markdown parsing."""
    test_md = """# Main Title

## Section 1
### Subsection 1.1
- Item 1
- Item 2
  - Nested item

## Section 2
1. First item
2. Second item
"""

    parser = MarkdownParser()
    root = parser.parse(test_md)
    # First # heading becomes the root topic title
    assert root.title == "Main Title", f"Expected 'Main Title', got '{root.title}'"
    # Check that children are parsed
    assert len(root.children) >= 2, f"Expected at least 2 children, got {len(root.children)}"
    print("✓ Basic Markdown parsing works")


def test_xmind8_output():
    """Test XMind 8 format generation."""
    test_md = """# Test Mind Map

## Topic 1
- Item A
- Item B

## Topic 2
"""

    output_path = "/tmp/test_xmind8.xmind"
    result = convert_markdown_to_xmind(test_md, 'xmind8', output_path)
    assert os.path.exists(result), "XMind file not created"

    import zipfile
    with zipfile.ZipFile(result, 'r') as zf:
        assert 'content.xml' in zf.namelist(), "Missing content.xml"
        assert 'META-INF/manifest.xml' in zf.namelist(), "Missing manifest.xml"
    print("✓ XMind 8 format generation works")


def test_xmindzen_output():
    """Test XMind Zen format generation."""
    test_md = """# Test Mind Map

## Topic 1
- Item A
"""

    output_path = "/tmp/test_xmindzen.xmind"
    result = convert_markdown_to_xmind(test_md, 'xmindzen', output_path)
    assert os.path.exists(result), "XMind file not created"

    import zipfile
    with zipfile.ZipFile(result, 'r') as zf:
        assert 'content.json' in zf.namelist(), "Missing content.json"
    print("✓ XMind Zen format generation works")


def test_todo_items():
    """Test todo item parsing."""
    test_md = """# Tasks

- [ ] Todo item 1
- [x] Completed item
- [ ] Todo item 2
"""

    parser = MarkdownParser()
    root = parser.parse(test_md)
    # Check that todo markers are set
    has_todo = False
    has_done = False
    for child in root.children:
        if 'task-empty' in child.markers:
            has_todo = True
        if 'task-done' in child.markers:
            has_done = True

    assert has_todo, "Todo markers not parsed correctly"
    assert has_done, "Done markers not parsed correctly"
    print("✓ Todo item parsing works")


def run_all_tests():
    """Run all validation tests."""
    print("Running md-to-xmind validation tests...\n")

    try:
        test_basic_markdown()
        test_xmind8_output()
        test_xmindzen_output()
        test_todo_items()
        print("\n✅ All validation tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
