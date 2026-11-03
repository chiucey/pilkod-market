#!/usr/bin/env python3
"""
XMind Mind Map Generator
Generates standard .xmind files with rich visual elements and structural layouts.

Usage:
    python xmind_generator.py --title "标题" --topics topics.json --output output.xmind
    python xmind_generator.py --interactive
"""

import json
import zipfile
import uuid
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


# ============================================================
# Data Classes
# ============================================================

@dataclass
class TextStyle:
    font_family: str = "Droid Serif"
    font_size: str = "14pt"
    font_weight: str = "400"
    font_style: str = "normal"
    color: str = "inherited"
    text_transform: str = "manual"
    text_decoration: str = "none"
    text_align: str = "left"

    def to_properties(self) -> Dict[str, str]:
        return {
            "fo:font-family": self.font_family,
            "fo:font-size": self.font_size,
            "fo:font-weight": self.font_weight,
            "fo:font-style": self.font_style,
            "fo:color": self.color,
            "fo:text-transform": self.text_transform,
            "fo:text-decoration": self.text_decoration,
            "fo:text-align": self.text_align,
        }


@dataclass
class TopicStyle:
    text: TextStyle = field(default_factory=TextStyle)
    fill: str = "inherited"
    fill_pattern: str = "solid"
    line_width: str = "inherited"
    line_color: str = "inherited"
    line_pattern: str = "inherited"
    border_color: str = "inherited"
    border_width: str = "inherited"
    shape_class: str = "org.xmind.topicShape.roundedRect"
    line_class: str = "org.xmind.branchConnection.roundedElbow"
    arrow_end_class: str = "org.xmind.arrowShape.none"

    def to_properties(self) -> Dict[str, str]:
        props = self.text.to_properties()
        props.update({
            "svg:fill": self.fill,
            "fill-pattern": self.fill_pattern,
            "line-width": self.line_width,
            "line-color": self.line_color,
            "line-pattern": self.line_pattern,
            "border-line-color": self.border_color,
            "border-line-width": self.border_width,
            "border-line-pattern": self.border_width,
            "shape-class": self.shape_class,
            "line-class": self.line_class,
            "arrow-end-class": self.arrow_end_class,
        })
        return props


@dataclass
class Topic:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    title_edited: bool = True
    notes: Optional[Dict] = None
    labels: List[str] = field(default_factory=list)
    children: Dict[str, List['Topic']] = field(default_factory=dict)
    style: Optional[TopicStyle] = None
    markers: Optional[Dict] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "title": self.title,
            "titleUnedited": self.title_edited,
        }
        if self.notes:
            result["notes"] = self.notes
        if self.labels:
            result["labels"] = self.labels
        if self.markers:
            result["markers"] = self.markers
        if self.children:
            result["children"] = self.children
        return result


@dataclass
class Relationship:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    end1_id: str = ""
    end2_id: str = ""
    control_points: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "end1Id": self.end1_id,
            "end2Id": self.end2_id,
            "controlPoints": self.control_points
        }


@dataclass
class Summary:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "概要"
    title_edited: bool = True
    range_str: str = "(0,1)"
    topic_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "titleUnedited": self.title_edited,
        }


@dataclass
class SummaryMarker:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    range_str: str = "(0,1)"
    topic_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "range": self.range_str,
            "topicId": self.topic_id
        }


# ============================================================
# Theme Presets
# ============================================================

THEMES = {
    "rainbow": {
        "map": {
            "id": str(uuid.uuid4()),
            "properties": {
                "svg:fill": "#ffffff",
                "multi-line-colors": "#F9423A #F6A04D #F3D321 #00BC7B #486AFF #4D49BE",
                "color-list": "#000229 #1F2766 #52CC83 #4D86DB #99142F #245570",
                "line-tapered": "none"
            }
        },
        "centralTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "Droid Serif",
                "fo:font-size": "30pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "center",
                "svg:fill": "#000229",
                "fill-pattern": "solid",
                "line-width": "3pt",
                "line-color": "#000229",
                "line-pattern": "solid",
                "border-line-color": "inherited",
                "border-line-width": "3pt",
                "border-line-pattern": "inherited",
                "shape-class": "org.xmind.topicShape.roundedRect",
                "line-class": "org.xmind.branchConnection.roundedElbow",
                "arrow-end-class": "org.xmind.arrowShape.none",
                "alignment-by-level": "inactived"
            }
        },
        "mainTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "Droid Serif",
                "fo:font-size": "18pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "left",
                "svg:fill": "inherited",
                "fill-pattern": "none",
                "line-width": "inherited",
                "line-color": "inherited",
                "line-pattern": "inherited",
                "border-line-color": "inherited",
                "border-line-width": "0pt",
                "border-line-pattern": "inherited",
                "shape-class": "org.xmind.topicShape.roundedRect",
                "line-class": "org.xmind.branchConnection.roundedElbow",
                "arrow-end-class": "inherited"
            }
        },
        "subTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "Droid Serif",
                "fo:font-size": "14pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "left",
                "svg:fill": "inherited",
                "fill-pattern": "none",
                "line-width": "2pt",
                "line-color": "inherited",
                "line-pattern": "inherited",
                "border-line-color": "inherited",
                "border-line-width": "0pt",
                "border-line-pattern": "inherited",
                "shape-class": "org.xmind.topicShape.roundedRect",
                "line-class": "org.xmind.branchConnection.roundedElbow",
                "arrow-end-class": "inherited"
            }
        },
        "floatingTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "Droid Serif",
                "fo:font-size": "14pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "center",
                "svg:fill": "#EEEBEE",
                "fill-pattern": "solid",
                "line-width": "inherited",
                "line-color": "inherited",
                "line-pattern": "solid",
                "border-line-color": "#EEEBEE",
                "border-line-width": "0pt",
                "border-line-pattern": "inherited",
                "shape-class": "org.xmind.topicShape.roundedRect",
                "line-class": "org.xmind.branchConnection.roundedElbow",
                "arrow-end-class": "org.xmind.arrowShape.none"
            }
        },
        "summaryTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "Droid Serif",
                "fo:font-size": "14pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "center",
                "svg:fill": "#000229",
                "fill-pattern": "solid",
                "line-width": "inherited",
                "line-color": "inherited",
                "line-pattern": "inherited",
                "border-line-color": "#000229",
                "border-line-width": "0pt",
                "border-line-pattern": "inherited",
                "shape-class": "org.xmind.topicShape.roundedRect",
                "line-class": "org.xmind.branchConnection.roundedElbow",
                "arrow-end-class": "inherited"
            }
        },
        "calloutTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "Droid Serif",
                "fo:font-size": "14pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "left",
                "svg:fill": "#000229",
                "fill-pattern": "solid",
                "line-width": "inherited",
                "line-color": "inherited",
                "line-pattern": "inherited",
                "border-line-color": "#000229",
                "border-line-width": "inherited",
                "border-line-pattern": "inherited",
                "shape-class": "org.xmind.topicShape.roundedRect",
                "arrow-end-class": "inherited"
            }
        },
        "importantTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "svg:fill": "#460400",
                "fill-pattern": "solid",
                "border-line-color": "#460400"
            }
        },
        "minorTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "svg:fill": "#703D00",
                "fill-pattern": "solid",
                "border-line-color": "#703D00"
            }
        },
        "expiredTopic": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:text-decoration": "line-through",
                "fill-pattern": "none"
            }
        },
        "boundary": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "'Droid Serif','NeverMind','Microsoft YaHei','PingFang SC','Microsoft JhengHei','sans-serif',sans-serif",
                "fo:font-size": "14pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "center",
                "svg:fill": "#000229",
                "fill-pattern": "solid",
                "line-width": "2",
                "line-color": "#000229",
                "line-pattern": "dash",
                "shape-class": "org.xmind.boundaryShape.roundedRect"
            }
        },
        "summary": {
            "id": str(uuid.uuid4()),
            "properties": {
                "line-width": "2pt",
                "line-color": "#000229",
                "line-pattern": "solid",
                "shape-class": "org.xmind.summaryShape.square"
            }
        },
        "relationship": {
            "id": str(uuid.uuid4()),
            "properties": {
                "fo:font-family": "'Droid Serif','NeverMind','Microsoft YaHei','PingFang SC','Microsoft JhengHei','sans-serif',sans-serif",
                "fo:font-size": "13pt",
                "fo:font-weight": "400",
                "fo:font-style": "normal",
                "fo:color": "inherited",
                "fo:text-transform": "manual",
                "fo:text-decoration": "none",
                "fo:text-align": "center",
                "line-width": "2",
                "line-color": "#000229",
                "line-pattern": "dash",
                "shape-class": "org.xmind.relationshipShape.curved",
                "arrow-begin-class": "org.xmind.arrowShape.none",
                "arrow-end-class": "org.xmind.arrowShape.triangle"
            }
        },
        "skeletonThemeId": str(uuid.uuid4()),
        "colorThemeId": "Rainbow-#000229-MULTI_LINE_COLORS"
    }
}


# ============================================================
# Layout Structure Presets
# ============================================================

LAYOUTS = {
    "logic.right": "org.xmind.ui.logic.right",
    "logic.left": "org.xmind.ui.logic.left",
    "map": "org.xmind.ui.map",
    "tree.right": "org.xmind.ui.tree.right",
    "tree.left": "org.xmind.ui.tree.left",
    "organization.top": "org.xmind.ui.organization.top",
    "organization.bottom": "org.xmind.ui.organization.bottom",
    "chronological.top": "org.xmind.ui.chronological.top",
    "chronological.right": "org.xmind.ui.chronological.right",
}


# ============================================================
# XMind Generator Class
# ============================================================

class XMindGenerator:
    """Generates XMind mind map files with rich visual elements."""

    def __init__(
        self,
        title: str = "Mind Map",
        structure: str = "logic.right",
        theme: str = "rainbow",
    ):
        self.title = title
        self.structure = LAYOUTS.get(structure, structure)
        self.theme_name = theme
        self.root_topic: Optional[Topic] = None
        self.relationships: List[Relationship] = []
        self.summaries: List[SummaryMarker] = []

    def _normalize_notes(self, notes: Any) -> Optional[Dict]:
        """Normalize notes to XMind format.

        Accepts:
        - Dict: passed through if already in correct format
        - str: converted to {"plain": {"content": str}}
        - None: returns None
        """
        if notes is None:
            return None
        if isinstance(notes, dict):
            # Already in correct format, pass through
            return notes
        if isinstance(notes, str):
            # Convert string to XMind notes format
            return {"plain": {"content": notes}}
        # For other types, convert to string
        return {"plain": {"content": str(notes)}}

    def build_topic_tree(self, data: Dict[str, Any], parent_id: Optional[str] = None) -> List[Topic]:
        """Recursively build topic tree from nested data."""
        topics = []
        for item in data.get("topics", []):
            # Normalize notes to XMind format
            notes = self._normalize_notes(item.get("notes"))
            topic = Topic(
                title=item.get("title", ""),
                notes=notes,
                labels=item.get("labels", []),
                markers=item.get("markers"),
            )

            if "children" in item:
                # Handle both array format and {"topics": [...]} format
                children_data = item["children"]
                if isinstance(children_data, dict) and "topics" in children_data:
                    children_data = children_data["topics"]
                topic.children = {
                    "attached": self.build_topic_tree({"topics": children_data}, topic.id)
                }

            topics.append(topic)

        return topics

    def set_root(self, title: str, children_data: Optional[Dict] = None):
        """Set the root topic of the mind map."""
        self.root_topic = Topic(
            id=str(uuid.uuid4()),
            title=title,
            title_edited=True,
        )

        if children_data:
            self.root_topic.children = {
                "attached": self.build_topic_tree(children_data)
            }
            # Add summaries if present
            if "summaries" in children_data:
                self._process_summaries(children_data["summaries"])

    def add_relationship(self, end1_id: str, end2_id: str,
                        control_points: Optional[Dict] = None):
        """Add a relationship (connection) between two topics."""
        rel = Relationship(
            end1_id=end1_id,
            end2_id=end2_id,
            control_points=control_points or {}
        )
        self.relationships.append(rel)

    def add_summary(self, topic_id: str, range_str: str = "(0,1)"):
        """Add a summary marker to a range of topics."""
        summary = SummaryMarker(
            topic_id=topic_id,
            range_str=range_str
        )
        self.summaries.append(summary)

    def _process_summaries(self, summaries_data: List[Dict]):
        """Process summary data from input."""
        for s in summaries_data:
            self.add_summary(
                topic_id=s.get("topicId", ""),
                range_str=s.get("range", "(0,1)")
            )

    def find_topic_by_title(self, title: str, topic: Optional[Topic] = None) -> Optional[Topic]:
        """Find a topic by its title (DFS)."""
        if topic is None:
            topic = self.root_topic
        if topic is None:
            return None
        if topic.title == title:
            return topic
        for child_list in topic.children.values():
            for child in child_list:
                result = self.find_topic_by_title(title, child)
                if result:
                    return result
        return None

    def _topic_to_dict(self, topic: Topic) -> Dict[str, Any]:
        """Convert Topic object to dictionary."""
        result = {
            "id": topic.id,
            "title": topic.title,
            "titleUnedited": topic.title_edited,
        }
        if topic.notes:
            result["notes"] = topic.notes
        if topic.labels:
            result["labels"] = topic.labels
        if topic.markers:
            result["markers"] = topic.markers
        if topic.children:
            result["children"] = {}
            for key, children in topic.children.items():
                result["children"][key] = [self._topic_to_dict(child) for child in children]
        return result

    def generate_content_json(self) -> str:
        """Generate the content.json string."""
        root = self._topic_to_dict(self.root_topic)
        content = [{
            "id": str(uuid.uuid4()),
            "class": "sheet",
            "rootTopic": root,
            "structureClass": self.structure,
            "children": root.get("children", {}),
            "relationships": [r.to_dict() for r in self.relationships],
            "title": self.title,
            "extensions": [{
                "provider": "org.xmind.ui.skeleton.structure.style",
                "content": {
                    "centralTopic": self.structure
                }
            }],
            "theme": THEMES.get(self.theme_name, THEMES["rainbow"])
        }]

        # Add summaries
        if self.summaries:
            content[0]["summaries"] = [s.to_dict() for s in self.summaries]

        return json.dumps(content, ensure_ascii=False, indent=2)

    def generate_metadata_json(self) -> str:
        """Generate the metadata.json string."""
        metadata = {
            "dataStructureVersion": "2",
            "layoutEngineVersion": "3",
            "creator": {
                "name": "XMindGenerator",
                "version": "1.0.0"
            }
        }
        return json.dumps(metadata, ensure_ascii=False, indent=2)

    def generate_manifest_json(self) -> str:
        """Generate the manifest.json string."""
        manifest = {
            "file-entries": {
                "content.json": {},
                "metadata.json": {},
                "Thumbnails/thumbnail.png": {}
            }
        }
        return json.dumps(manifest, ensure_ascii=False, indent=2)

    def save(self, output_path: str):
        """Save the XMind file to the specified path."""
        output_path = Path(output_path)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as xmind:
            # Write content.json
            xmind.writestr(
                "content.json",
                self.generate_content_json()
            )

            # Write metadata.json
            xmind.writestr(
                "metadata.json",
                self.generate_metadata_json()
            )

            # Write manifest.json
            xmind.writestr(
                "manifest.json",
                self.generate_manifest_json()
            )

            # Create a simple placeholder thumbnail
            import base64
            # Minimal 1x1 transparent PNG
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            )
            xmind.writestr("Thumbnails/thumbnail.png", png_data)

        return str(output_path)


# ============================================================
# CLI Interface
# ============================================================

def parse_markdown_to_structure(markdown_text: str) -> Dict[str, Any]:
    """Parse markdown text into topic structure."""
    lines = markdown_text.strip().split('\n')
    root_title = ""
    result = {"topics": []}

    if not lines:
        return result

    # First non-empty line is the root
    for line in lines:
        if line.strip():
            root_title = line.strip().lstrip('#').strip()
            break

    if not root_title and lines:
        root_title = lines[0].strip().lstrip('#').strip()

    current_path = []  # Stack of parent indices

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Count leading # for level
        level = 0
        for ch in stripped:
            if ch == '#':
                level += 1
            else:
                break

        if level == 0:
            if root_title and not result["topics"]:
                root_title = stripped.lstrip('#').strip()
            continue

        title = stripped.lstrip('#').strip()

        # Build the topic structure
        topic_data = {"title": title, "topics": []}

        # Find parent level
        while current_path and len(current_path) >= level:
            current_path.pop()

        if not current_path:
            result["topics"].append(topic_data)
            current_path.append(len(result["topics"]) - 1)
        else:
            parent_idx = current_path[-1]
            parent = result["topics"]
            for idx in current_path[:-1]:
                parent = parent[idx]["topics"]
            parent[parent_idx]["topics"].append(topic_data)
            current_path.append(len(parent[parent_idx]["topics"]) - 1)

    return {"root": root_title, "structure": result}


def main():
    parser = argparse.ArgumentParser(
        description="Generate XMind mind map files"
    )
    parser.add_argument(
        "--title", "-t",
        help="Mind map title",
        default="Mind Map"
    )
    parser.add_argument(
        "--topics", "-T",
        help="JSON file containing topic structure"
    )
    parser.add_argument(
        "--markdown", "-m",
        help="Markdown text to convert to mind map"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path",
        default="output.xmind"
    )
    parser.add_argument(
        "--structure", "-s",
        help="Layout structure (logic.right, map, tree.right, etc.)",
        default="logic.right"
    )
    parser.add_argument(
        "--theme",
        help="Color theme (rainbow, fresh, ocean, etc.)",
        default="rainbow"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode"
    )

    args = parser.parse_args()

    if args.interactive:
        print("Interactive mode - coming soon!")
        return

    generator = XMindGenerator(
        title=args.title,
        structure=args.structure,
        theme=args.theme
    )

    # Parse input data
    if args.topics:
        with open(args.topics, 'r', encoding='utf-8') as f:
            data = json.load(f)
        root_title = data.get("root", args.title)
        # Get topics from data["topics"], regardless of structure format
        topics_data = data.get("topics", [])
        structure = {"topics": topics_data}
    elif args.markdown:
        parsed = parse_markdown_to_structure(args.markdown)
        root_title = parsed.get("root", args.title)
        topics_data = parsed.get("topics", [])
        structure = {"topics": topics_data}
    else:
        # Default empty structure
        root_title = args.title
        structure = {"topics": []}

    generator.set_root(root_title, structure)
    output_path = generator.save(args.output)
    print(f"XMind file generated: {output_path}")


if __name__ == "__main__":
    main()
