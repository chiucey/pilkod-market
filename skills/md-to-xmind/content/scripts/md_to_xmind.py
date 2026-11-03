#!/usr/bin/env python3
"""
MD to XMind Converter
Converts Markdown files to XMind format, compatible with XMind 8/2020/Zen versions.
"""

import json
import re
import uuid
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class Topic:
    """Represents a topic/node in the mind map."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    children: List['Topic'] = field(default_factory=list)
    notes: str = ""
    markers: List[str] = field(default_factory=list)
    weight: int = 0
    folded: bool = False


class MarkdownParser:
    """Parse Markdown content into a tree structure."""

    def __init__(self):
        self.topics: List[Topic] = []
        self.root = Topic(title="Root")

    def parse(self, content: str) -> Topic:
        """Parse markdown content into a Topic tree."""
        lines = content.strip().split('\n')
        self._parse_lines(lines)
        return self.root

    def _parse_lines(self, lines: List[str]) -> None:
        """Parse all lines and build the topic tree."""
        current_parent = self.root
        current_topic = None
        current_depth = 0
        in_code_block = False
        in_list_indent = 0

        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Skip empty lines
            if not line.strip():
                continue

            # Parse headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                depth = len(heading_match.group(1))
                title = heading_match.group(2).strip()

                # Remove markdown formatting from title
                title = self._clean_markdown(title)

                topic = Topic(title=title)

                # Adjust tree based on heading depth
                if depth == 1:
                    self.root = topic
                    current_parent = topic
                    current_topic = topic
                else:
                    # Find correct parent based on depth
                    while current_depth >= depth:
                        current_parent = self._get_parent(current_parent) or self.root
                        current_depth -= 1
                    current_parent.children.append(topic)
                    current_topic = topic
                current_depth = depth
                in_list_indent = 0
                continue

            # Parse unordered lists
            list_match = re.match(r'^(\s*)[-*+]\s*(?:\[([ xX])\])?\s*(.+)$', line)
            if list_match:
                indent = len(list_match.group(1)) // 2 + 1
                checked = list_match.group(2)
                text = list_match.group(3).strip()

                # Handle multi-line list content
                if text.endswith('\\'):
                    text = text[:-1].strip()

                title = self._clean_markdown(text)
                topic = Topic(title=title)

                # Set markers for todo items
                if checked == ' ':
                    topic.markers.append('task-empty')
                elif checked in ('x', 'X'):
                    topic.markers.append('task-done')

                # Find correct parent
                if indent > in_list_indent:
                    if current_topic:
                        current_parent = current_topic
                elif indent < in_list_indent:
                    for _ in range(in_list_indent - indent):
                        current_parent = self._get_parent(current_parent) or self.root

                current_parent.children.append(topic)
                current_topic = topic
                current_depth = 0
                in_list_indent = indent
                continue

            # Parse ordered lists
            ordered_match = re.match(r'^(\s*)\d+\.\s*(.+)$', line)
            if ordered_match:
                indent = len(ordered_match.group(1)) // 2 + 1
                text = ordered_match.group(2).strip()
                title = self._clean_markdown(text)

                topic = Topic(title=title)

                # Find correct parent
                if indent > in_list_indent:
                    if current_topic:
                        current_parent = current_topic
                elif indent < in_list_indent:
                    for _ in range(in_list_indent - indent):
                        current_parent = self._get_parent(current_parent) or self.root

                current_parent.children.append(topic)
                current_topic = topic
                current_depth = 0
                in_list_indent = indent
                continue

            # Parse blockquotes
            quote_match = re.match(r'^>\s*(.+)$', line)
            if quote_match:
                text = quote_match.group(1).strip()
                title = self._clean_markdown(text)
                topic = Topic(title=title, notes=f"Quote: {text}")
                if current_topic:
                    current_topic.children.append(topic)
                else:
                    current_parent.children.append(topic)
                continue

            # Continuation of previous line (indented content)
            if line.startswith('    ') or line.startswith('\t'):
                if current_topic:
                    current_topic.title += ' ' + self._clean_markdown(line.strip())
                continue

            # Plain text - add as child of current topic
            if current_topic:
                title = self._clean_markdown(line.strip())
                if title:
                    topic = Topic(title=title)
                    current_topic.children.append(topic)

    def _get_parent(self, topic: Topic) -> Optional[Topic]:
        """Find parent of a topic (simplified - returns None for root level)."""
        return None

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text."""
        # Remove bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        # Remove italic
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # Remove inline code
        text = re.sub(r'`(.+?)`', r'\1', text)
        # Remove links
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        # Remove images
        text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
        # Remove strikethrough
        text = re.sub(r'~~(.+?)~~', r'\1', text)
        return text.strip()


class XMind8Generator:
    """Generate XMind 8 format (XML)."""

    def generate(self, root: Topic) -> str:
        """Generate XMind 8 XML content."""
        children_xml = self._generate_children(root.children, 1)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"
              xmlns:svg="http://www.w3.org/2000/svg"
              xmlns:fo="http://www.w3.org/1999/XSL/Format"
              version="2.0">
  <sheet>
    <title>{self._escape_xml(root.title or 'Mind Map')}</title>
    <rootTopic>
      <title>{self._escape_xml(root.title or 'Central Topic')}</title>
{children_xml}
    </rootTopic>
  </sheet>
</xmap-content>'''

    def _generate_children(self, topics: List[Topic], depth: int) -> str:
        """Generate XML for child topics."""
        if not topics:
            return ""

        xml_parts = []
        indent = "      " + "  " * depth

        for topic in topics:
            children_xml = self._generate_children(topic.children, depth + 1)
            notes_xml = f'\n{indent}  <notes><plain-text><content>{self._escape_xml(topic.notes)}</content></plain-text></notes>' if topic.notes else ''

            markers_xml = ''
            if topic.markers:
                markers_xml = f'\n{indent}  <markers><marker-ref marker-id="{topic.markers[0]}"/></markers>'

            if children_xml:
                xml_parts.append(f'''{indent}<topic id="{topic.id}" folded="false">
{indent}  <title>{self._escape_xml(topic.title)}</title>{markers_xml}{notes_xml}
{children_xml}
{indent}</topic>''')
            else:
                xml_parts.append(f'''{indent}<topic id="{topic.id}" folded="false">
{indent}  <title>{self._escape_xml(topic.title)}</title>{markers_xml}{notes_xml}
{indent}</topic>''')

        return '\n'.join(xml_parts)

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))


class XMindZenGenerator:
    """Generate XMind Zen/2020 format (JSON)."""

    def generate(self, root: Topic) -> dict:
        """Generate XMind Zen JSON content."""
        return {
            "schema": "xmind-zen",
            "version": "1.0.0",
            "rootTopic": {
                "id": root.id,
                "title": root.title or "Central Topic",
                "children": {
                    "attached": self._generate_children(root.children),
                    "detached": []
                },
                "notes": self._generate_notes(root.notes) if root.notes else None,
                "markers": root.markers if root.markers else None
            },
            "preferences": {
                "showRelations": True,
                "showFloatingTopics": True
            }
        }

    def _generate_children(self, topics: List[Topic]) -> List[Dict]:
        """Generate JSON for child topics."""
        result = []
        for topic in topics:
            result.append({
                "id": topic.id,
                "title": topic.title,
                "children": {
                    "attached": self._generate_children(topic.children),
                    "detached": []
                },
                "notes": self._generate_notes(topic.notes) if topic.notes else None,
                "markers": topic.markers if topic.markers else None,
                "foldable": topic.folded
            })
        return result

    def _generate_notes(self, text: str) -> Dict:
        """Generate notes structure."""
        return {
            "type": "plain",
            "content": text
        }


def create_xmind_package(content: str, version: str = 'xmind8', output_path: str = 'output.xmind') -> str:
    """Create XMind ZIP package."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if version == 'xmind8':
            # XMind 8 format
            zf.writestr('META-INF/manifest.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:2.0" version="2.0">
  <file path="content.xml" type="content/xml"/>
  <file path="content.json" type="content/json"/>
  <file path="styles.xml" type="styles/xml"/>
  <file path="comments.xml" type="comments/xml"/>
</manifest>''')
            zf.writestr('styles.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<xmap-styles xmlns:svg="http://www.w3.org/2000/svg"
             xmlns:fo="http://www.w3.org/1999/XSL/Format"
             xmlns="urn:xmind:xmap:xmlns:style:2.0"
             version="2.0">
  <style id="preferred" type="topic">
    <font-family>Segoe UI</font-family>
    <font-size>16</font-size>
  </style>
</xmap-styles>''')
            zf.writestr('comments.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<comments xmlns="urn:xmind:xmap:xmlns:comments:2.0" version="2.0">
</comments>''')
            zf.writestr('content.xml', content)
            zf.writestr('content.json', '{}')

        elif version in ('xmind2020', 'xmindzen'):
            # XMind Zen/2020 format
            content_json = json.loads(content)
            zf.writestr('content.json', json.dumps(content_json, indent=2, ensure_ascii=False))

    return output_path


def convert_markdown_to_xmind(
    markdown_content: str,
    version: str = 'xmind8',
    output_path: Optional[str] = None
) -> str:
    """
    Convert Markdown to XMind format.

    Args:
        markdown_content: The Markdown text to convert
        version: XMind version - 'xmind8', 'xmind2020', or 'xmindzen'
        output_path: Output file path (optional)

    Returns:
        Path to the generated XMind file
    """
    # Parse Markdown
    parser = MarkdownParser()
    root = parser.parse(markdown_content)

    # Generate XMind content based on version
    if version == 'xmind8':
        generator = XMind8Generator()
        content = generator.generate(root)
    else:
        generator = XMindZenGenerator()
        content = json.dumps(generator.generate(root), indent=2, ensure_ascii=False)

    # Determine output path
    if not output_path:
        output_path = 'output.xmind'

    # Create package
    create_xmind_package(content, version, output_path)

    return output_path


def convert_file_to_xmind(
    input_path: str,
    version: str = 'xmind8',
    output_path: Optional[str] = None
) -> str:
    """
    Convert a Markdown file to XMind format.

    Args:
        input_path: Path to the Markdown file
        version: XMind version - 'xmind8', 'xmind2020', or 'xmindzen'
        output_path: Output file path (optional)

    Returns:
        Path to the generated XMind file
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine output path
    if not output_path:
        input_file = Path(input_path)
        output_path = str(input_file.with_suffix('.xmind'))

    return convert_markdown_to_xmind(content, version, output_path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: md_to_xmind.py <input.md> [output.xmind] [--version=xmind8|xmind2020|xmindzen]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    version = 'xmind8'

    for arg in sys.argv[3:]:
        if arg.startswith('--version='):
            version = arg.split('=')[1]

    result = convert_file_to_xmind(input_file, version, output_file)
    print(f"Created: {result}")
