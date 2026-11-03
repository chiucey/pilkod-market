# XMind Generator - Complete Reference

## File Structure

XMind files are ZIP archives containing:

```
filename.xmind/
├── content.json      # Main mind map data
├── metadata.json     # File metadata
├── manifest.json     # File manifest
└── Thumbnails/
    └── thumbnail.png # Preview thumbnail
```

## content.json Structure

```json
[
  {
    "id": "sheet-uuid",
    "class": "sheet",
    "rootTopic": { ... },
    "structureClass": "org.xmind.ui.logic.right",
    "children": {
      "attached": [ ... ]
    },
    "relationships": [ ... ],
    "summaries": [ ... ],
    "title": "Sheet Title",
    "extensions": [ ... ],
    "theme": { ... }
  }
]
```

## Topic Object

```json
{
  "id": "topic-uuid",
  "title": "Topic Title",
  "titleUnedited": true,
  "notes": {
    "content": "Note content...",
    "type": "text"
  },
  "labels": ["label1", "label2"],
  "markers": {
    "task": {
      "status": "notStarted|inProgress|completed|paused|cancelled",
      "percent": 0-100
    }
  },
  "children": {
    "attached": [ ... ]
  }
}
```

## Structure Classes (布局结构)

| Class | Description |
|-------|-------------|
| `org.xmind.ui.logic.right` | Logic diagram, branches to right |
| `org.xmind.ui.logic.left` | Logic diagram, branches to left |
| `org.xmind.ui.map` | Radial/spider diagram |
| `org.xmind.ui.tree.right` | Tree diagram, branches to right |
| `org.xmind.ui.tree.left` | Tree diagram, branches to left |
| `org.xmind.ui.organization.top` | Organization chart, top-down |
| `org.xmind.ui.organization.bottom` | Organization chart, bottom-up |
| `org.xmind.ui.chronological.top` | Timeline, top-down |
| `org.xmind.ui.chronological.right` | Timeline, left-to-right |

## Shape Classes (形状)

| Class | Description |
|-------|-------------|
| `org.xmind.topicShape.roundedRect` | Rounded rectangle (default) |
| `org.xmind.topicShape.rect` | Rectangle |
| `org.xmind.topicShape.ellipse` | Ellipse/oval |
| `org.xmind.topicShape.underline` | Underlined text |
| `org.xmind.topicShape.none` | No shape (text only) |
| `org.xmind.boundaryShape.roundedRect` | Boundary rounded rectangle |

## Line Classes (分支样式)

| Class | Description |
|-------|-------------|
| `org.xmind.branchConnection.roundedElbow` | Rounded elbow (default) |
| `org.xmind.branchConnection.straight` | Straight line |
| `org.xmind.branchConnection.curved` | Curved line |
| `org.xmind.branchConnection.bezier` | Bezier curve |
| `org.xmind.relationshipShape.curved` | Relationship curved line |

## Theme Color Schemes

### Rainbow
```json
{
  "multi-line-colors": "#F9423A #F6A04D #F3D321 #00BC7B #486AFF #4D49BE",
  "color-list": "#000229 #1F2766 #52CC83 #4D86DB #99142F #245570"
}
```

### Fresh
```json
{
  "multi-line-colors": "#00B37C #4CD964 #5AC8FA #007AFF #5856D6 #AF52DE",
  "color-list": "#006B3C #1F7A4D #00A86B #00C853 #4CAF50 #2E7D32"
}
```

### Ocean
```json
{
  "multi-line-colors": "#00A0D6 #0072BC #004B66 #003D5B #002F47 #001E33",
  "color-list": "#004B66 #003D5B #002F47 #001E33 #001429 #000A1A"
}
```

### Passion
```json
{
  "multi-line-colors": "#FF3B30 #FF2D55 #FF6B6B #FF4757 #FF3838 #FF4D4D",
  "color-list": "#99142F #B91C3C #C41E3A #DC143C #E31B23 #CD5C5C"
}
```

### Purple
```json
{
  "multi-line-colors": "#5856D6 #AF52DE #8B5CF6 #7C3AED #6D28D9 #5B21B6",
  "color-list": "#4D49BE #4338CA #4C1D95 #5B21B6 #6D28D9 #7C3AED"
}
```

## Text Properties

| Property | Values | Default |
|----------|--------|---------|
| `fo:font-family` | Font name | "Droid Serif" |
| `fo:font-size` | Size with unit (pt) | "14pt" |
| `fo:font-weight` | "400" (normal), "700" (bold) | "400" |
| `fo:font-style` | "normal", "italic" | "normal" |
| `fo:color` | Hex color or "inherited" | "inherited" |
| `fo:text-decoration` | "none", "line-through" | "none" |
| `fo:text-align` | "left", "center", "right" | "left" |

## Marker Types

### Task Marker
```json
{
  "task": {
    "status": "notStarted|inProgress|completed|paused|cancelled",
    "percent": 0-100
  }
}
```

### Priority Marker
```json
{
  "priority": 1-5
}
```

## Relationship Object

```json
{
  "id": "relationship-uuid",
  "end1Id": "topic1-uuid",
  "end2Id": "topic2-uuid",
  "controlPoints": {
    "0": {"x": 46.5, "y": -33.25},
    "1": {"x": 64.5, "y": 42.25}
  }
}
```

## Summary Object

```json
{
  "id": "summary-topic-uuid",
  "title": "概要",
  "titleUnedited": true,
  "children": {
    "attached": [ ... ]
  }
}
```

```json
{
  "id": "summary-marker-uuid",
  "range": "(0,3)",
  "topicId": "summary-topic-uuid"
}
```

## Extension Format

```json
{
  "provider": "org.xmind.ui.skeleton.structure.style",
  "content": {
    "centralTopic": "org.xmind.ui.logic.right"
  }
}
```

## API Reference

### XMindGenerator Class

```python
class XMindGenerator:
    def __init__(
        self,
        title: str = "Mind Map",
        structure: str = "logic.right",
        theme: str = "rainbow"
    )

    def set_root(
        self,
        title: str,
        children_data: Optional[Dict] = None
    )

    def add_relationship(
        self,
        end1_id: str,
        end2_id: str,
        control_points: Optional[Dict] = None
    )

    def add_summary(
        self,
        topic_id: str,
        range_str: str = "(0,1)"
    )

    def find_topic_by_title(
        self,
        title: str,
        topic: Optional[Topic] = None
    ) -> Optional[Topic]

    def save(self, output_path: str) -> str
```

### Topic Class

```python
@dataclass
class Topic:
    id: str
    title: str
    title_edited: bool = True
    notes: Optional[Dict] = None
    labels: List[str] = field(default_factory=list)
    children: Dict[str, List['Topic']] = field(default_factory=dict)
    style: Optional[TopicStyle] = None
    markers: Optional[Dict] = None
```

### TopicStyle Class

```python
@dataclass
class TopicStyle:
    text: TextStyle = field(default_factory=TextStyle)
    fill: str = "inherited"
    fill_pattern: str = "solid"
    line_width: str = "inherited"
    line_color: str = "inherited"
    line_pattern: str = "inherited"
    shape_class: str = "org.xmind.topicShape.roundedRect"
    line_class: str = "org.xmind.branchConnection.roundedElbow"
    arrow_end_class: str = "org.xmind.arrowShape.none"
```

### TextStyle Class

```python
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
```

## CLI Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--title` | `-t` | Mind map title | "Mind Map" |
| `--topics` | `-T` | JSON file path | - |
| `--markdown` | `-m` | Markdown text | - |
| `--output` | `-o` | Output file path | "output.xmind" |
| `--structure` | `-s` | Layout structure | "logic.right" |
| `--theme` | - | Color theme | "rainbow" |
| `--interactive` | `-i` | Interactive mode | False |
