"""
Semantic Structure Parser
=========================

Converts flat document text into a hierarchical tree structure.
Detects implicit headings (e.g., "一、研究背景" without outline level),
identifies semantic sections (Abstract, Keywords, References, etc.),
and extracts figures, tables, and formulas.

Output structure:
    DocumentNode
    ├── TitleNode
    ├── AbstractNode
    ├── KeywordsNode
    ├── SectionNode (level=1, "第一章 绪论")
    │   ├── SectionNode (level=2, "1.1 研究背景")
    │   │   ├── ParagraphNode
    │   │   ├── FigureNode
    │   │   └── ParagraphNode
    │   └── SectionNode (level=2, "1.2 相关工作")
    ├── SectionNode (level=1, "第二章 方法")
    ├── ReferenceSectionNode
    └── AcknowledgementNode
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Union

from .helpers import detect_heading_level, extract_heading_text


# ── Node Types ─────────────────────────────────────────────────────

class NodeType(Enum):
    DOCUMENT = auto()
    TITLE = auto()
    ABSTRACT = auto()
    ABSTRACT_EN = auto()
    KEYWORDS = auto()
    KEYWORDS_EN = auto()
    SECTION = auto()      # Generic section
    CHAPTER = auto()      # Level 1 (章)
    SUBSECTION = auto()   # Level 2 (节)
    SUBSUBSECTION = auto()# Level 3 (子节)
    PARAGRAPH = auto()
    FIGURE = auto()
    FIGURE_CAPTION = auto()
    TABLE = auto()
    TABLE_CAPTION = auto()
    FORMULA = auto()
    FORMULA_NUMBER = auto()
    REFERENCE_LIST = auto()
    REFERENCE_ITEM = auto()
    ACKNOWLEDGEMENT = auto()
    APPENDIX = auto()
    LIST_ITEM = auto()
    TOC = auto()
    UNKNOWN = auto()


@dataclass
class DocumentNode:
    """A node in the document tree."""
    type: NodeType
    text: str = ""
    level: int = 0            # Heading level (0=body, 1=chapter, 2=section, 3=subsection)
    children: List['DocumentNode'] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def add_child(self, child: 'DocumentNode'):
        self.children.append(child)

    def to_text(self, indent: int = 0) -> str:
        """Recursive text representation for debugging."""
        prefix = "  " * indent
        type_name = self.type.name
        text_preview = self.text[:50].replace("\n", "\\n")
        lines = [f"{prefix}[{type_name}] L{self.level}: {text_preview}"]
        for c in self.children:
            lines.append(c.to_text(indent + 1))
        return "\n".join(lines)

    def find_all(self, node_type: NodeType) -> List['DocumentNode']:
        """Recursively find all nodes of a given type."""
        results = []
        if self.type == node_type:
            results.append(self)
        for c in self.children:
            results.extend(c.find_all(node_type))
        return results

    def count_by_type(self) -> dict:
        """Count all node types in the tree."""
        counts = {}
        counts[self.type] = counts.get(self.type, 0) + 1
        for c in self.children:
            sub_counts = c.count_by_type()
            for k, v in sub_counts.items():
                counts[k] = counts.get(k, 0) + v
        return counts


# ── Pattern constants ──────────────────────────────────────────────

# Semantic section markers (case-insensitive after stripping spaces)
SEMANTIC_SECTIONS_L1 = {
    "摘要": NodeType.ABSTRACT,
    "abstract": NodeType.ABSTRACT_EN,
    "目录": NodeType.TOC,
    "致谢": NodeType.ACKNOWLEDGEMENT,
    "参考文献": NodeType.REFERENCE_LIST,
    "附录": NodeType.APPENDIX,
    "结论": NodeType.SECTION,
    "总结": NodeType.SECTION,
}

SEMANTIC_SECTIONS_L2 = {
    "引言": NodeType.SECTION,
    "前言": NodeType.SECTION,
    "绪论": NodeType.SECTION,
    "研究背景": NodeType.SECTION,
    "相关工作": NodeType.SECTION,
    "本章小结": NodeType.SECTION,
}

# Regex patterns
FIGURE_CAPTION_RE = re.compile(
    r'^(?:图|Figure|Fig\.?)\s*(\d+(?:[\.-]\d+)?)\s*(.*)', re.IGNORECASE
)
TABLE_CAPTION_RE = re.compile(
    r'^(?:表|表格|Table)\s*(\d+(?:[\.-]\d+)?)\s*(.*)', re.IGNORECASE
)
FORMULA_RE = re.compile(r'^\s*(?:$$|\\\[|\\begin{equation})')
FORMULA_NUMBER_RE = re.compile(r'^\s*\((\d+(?:[\.-]\d+)?)\)\s*$')
KEYWORDS_RE = re.compile(
    r'^(?:关键词|Key words|关键字)\s*[:：]?\s*(.*)', re.IGNORECASE
)
CITATION_PLACEHOLDER_RE = re.compile(r'\[[\d,\s\-]+\]|\[[\w\s,]+\(\d{4}\)\]')


# ── Parser ─────────────────────────────────────────────────────────

class SemanticParser:
    """Parse flat document text into hierarchical tree structure."""

    def __init__(self, numbering_system: str = "阿拉伯数字"):
        self.numbering_system = numbering_system
        self.root = DocumentNode(type=NodeType.DOCUMENT, text="root")

    def parse(self, text: str) -> DocumentNode:
        """Main entry point: parse text into a document tree."""
        if not text.strip():
            return self.root

        lines = text.split("\n")
        current_section = self.root
        section_stack: List[DocumentNode] = [self.root]
        pending_caption: Optional[str] = None
        in_formula = False
        formula_buffer: List[str] = []
        in_references = False
        in_acknowledgement = False
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                if in_formula and formula_buffer:
                    formula_buffer.append("")
                i += 1
                continue

            # ── Formula detection (multi-line $$...$$) ─────────
            if stripped.startswith("$$") or stripped.startswith("\\["):
                if in_formula:
                    # End formula
                    formula_buffer.append(stripped)
                    self._add_formula(current_section, "\n".join(formula_buffer))
                    formula_buffer = []
                    in_formula = False
                else:
                    in_formula = True
                    formula_buffer = [stripped]
                i += 1
                continue

            if in_formula:
                if stripped.endswith("$$") or stripped.endswith("\\]"):
                    formula_buffer.append(stripped)
                    self._add_formula(current_section, "\n".join(formula_buffer))
                    formula_buffer = []
                    in_formula = False
                else:
                    formula_buffer.append(stripped)
                i += 1
                continue

            # ── Section / heading detection ────────────────────
            heading_level = detect_heading_level(stripped, self.numbering_system)

            if heading_level >= 1:
                # Check for semantic overrides
                node_type = self._classify_semantic_section(stripped)

                new_section = DocumentNode(
                    type=node_type,
                    text=stripped,
                    level=heading_level,
                )

                if node_type == NodeType.REFERENCE_LIST:
                    in_references = True
                    in_acknowledgement = False
                elif node_type == NodeType.ACKNOWLEDGEMENT:
                    in_acknowledgement = True
                    in_references = False

                # Pop stack to correct level
                while len(section_stack) > 1 and section_stack[-1].level >= heading_level:
                    section_stack.pop()

                section_stack[-1].add_child(new_section)
                section_stack.append(new_section)
                current_section = new_section
                i += 1
                continue

            # ── Reference items in reference section ───────────
            if in_references and re.match(r'^\[\d+\]', stripped):
                ref_node = DocumentNode(
                    type=NodeType.REFERENCE_ITEM,
                    text=stripped,
                    level=0,
                )
                current_section.add_child(ref_node)
                i += 1
                continue

            # ── Figure caption ───────────────────────────────────
            fig_match = FIGURE_CAPTION_RE.match(stripped)
            if fig_match:
                fig_num = fig_match.group(1)
                fig_title = fig_match.group(2).strip()
                node = DocumentNode(
                    type=NodeType.FIGURE_CAPTION,
                    text=stripped,
                    metadata={"number": fig_num, "title": fig_title}
                )
                current_section.add_child(node)
                i += 1
                continue

            # ── Table caption ────────────────────────────────────
            tbl_match = TABLE_CAPTION_RE.match(stripped)
            if tbl_match:
                tbl_num = tbl_match.group(1)
                tbl_title = tbl_match.group(2).strip()
                node = DocumentNode(
                    type=NodeType.TABLE_CAPTION,
                    text=stripped,
                    metadata={"number": tbl_num, "title": tbl_title}
                )
                current_section.add_child(node)
                i += 1
                continue

            # ── Keywords ─────────────────────────────────────────
            kw_match = KEYWORDS_RE.match(stripped)
            if kw_match:
                node = DocumentNode(
                    type=NodeType.KEYWORDS,
                    text=stripped,
                    metadata={"keywords": kw_match.group(1)}
                )
                current_section.add_child(node)
                i += 1
                continue

            # ── Inline formula (single-line) ─────────────────────
            if stripped.startswith("$") and stripped.endswith("$") and len(stripped) > 2:
                node = DocumentNode(
                    type=NodeType.FORMULA,
                    text=stripped,
                )
                current_section.add_child(node)
                i += 1
                continue

            # ── Body paragraph ───────────────────────────────────
            para_type = NodeType.PARAGRAPH
            if in_references:
                para_type = NodeType.REFERENCE_ITEM
            elif in_acknowledgement:
                para_type = NodeType.ACKNOWLEDGEMENT

            # Check for list items
            if re.match(r'^[\(（]?\d+[\)）]', stripped) or stripped.startswith("•"):
                para_type = NodeType.LIST_ITEM

            node = DocumentNode(
                type=para_type,
                text=stripped,
                level=0,
                metadata={"citations": self._extract_citations(stripped)}
            )
            current_section.add_child(node)
            i += 1

        return self.root

    # ── Internal helpers ──────────────────────────────────────────

    def _classify_semantic_section(self, text: str) -> NodeType:
        """Classify a heading by its semantic meaning."""
        clean = re.sub(r'\s+', '', text.lower().strip())

        for keyword, node_type in SEMANTIC_SECTIONS_L1.items():
            if clean == keyword or clean == keyword.replace(" ", ""):
                return node_type

        for keyword, node_type in SEMANTIC_SECTIONS_L2.items():
            k_clean = re.sub(r'\s+', '', keyword.lower())
            if clean == k_clean:
                return node_type

        # Check for "第X章" pattern
        if re.match(r'^第[一二三四五六七八九十百千]+章', text):
            return NodeType.CHAPTER

        return NodeType.SECTION

    def _add_formula(self, parent: DocumentNode, formula_text: str):
        """Add a formula node, extracting number if present."""
        number = ""
        lines = formula_text.split("\n")
        for ln in lines:
            num_match = FORMULA_NUMBER_RE.match(ln.strip())
            if num_match:
                number = num_match.group(1)
                break

        node = DocumentNode(
            type=NodeType.FORMULA,
            text=formula_text,
            metadata={"number": number} if number else {}
        )
        parent.add_child(node)

    def _extract_citations(self, text: str) -> List[str]:
        """Extract citation placeholders from text."""
        return CITATION_PLACEHOLDER_RE.findall(text)


# ── Convenience function ──────────────────────────────────────────

def parse_document(text: str, numbering_system: str = "阿拉伯数字") -> DocumentNode:
    """Parse flat document text into a hierarchical tree."""
    parser = SemanticParser(numbering_system)
    return parser.parse(text)


def document_to_json(tree: DocumentNode) -> dict:
    """Convert document tree to JSON-serializable dict."""
    def _node_to_dict(node: DocumentNode) -> dict:
        d = {
            "type": node.type.name,
            "text": node.text,
            "level": node.level,
            "metadata": node.metadata,
        }
        if node.children:
            d["children"] = [_node_to_dict(c) for c in node.children]
        return d
    return _node_to_dict(tree)
