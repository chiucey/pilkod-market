---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1a4c2f5ca76e7ce78ddad62bf73c686d
    PropagateID: 1a4c2f5ca76e7ce78ddad62bf73c686d
    ReservedCode1: 304502206fb1a4866489fb7d64766695a32a24eaec1b96ea8225c5ce917e9e969a83462d022100e90ffbe87a029bfafdf84c5ed2cab24945ce6537088ad01e8465f656bd06bf49
    ReservedCode2: 304502204f5ff050bcb07a59722899ca506e9714dc73e2ca7d9c9187a47df0b8c84fccd0022100e1101cb2ba204d9f1254c5096cbc2b431ba22f988683b297d245c422c1917fd4
---

# draw.io Diagram Generator

Generate interactive draw.io diagrams that users can open and edit in their browser.

## Supported Diagram Types

| Category | Diagram Types |
|----------|---------------|
| **Standard** | Flowcharts, org charts, mind maps, timelines, Venn diagrams |
| **Software** | UML (class, sequence, activity, use case), ERD, architecture diagrams |
| **Cloud/Infrastructure** | AWS, Azure, GCP, Kubernetes, network topology |
| **Engineering** | Electrical circuits, digital logic, P&ID, floor plans |
| **Business** | BPMN, value streams, customer journeys, SWOT |
| **UI/UX** | Wireframes, mockups, sitemaps |
| **And more** | Infographics, data flows, decision trees |

## Format Selection Guide

| Format | Best For |
|--------|----------|
| **Mermaid** | Flowcharts, sequences, ERD, Gantt, state diagrams, class diagrams |
| **CSV** | Hierarchical data (org charts), bulk import from spreadsheets |
| **XML** | Complex layouts, precise positioning, custom styling, icons, shapes |

## Usage

### Step 1: Determine the best format

- Use **Mermaid** for most standard diagrams (flowcharts, sequence diagrams, ERD)
- Use **CSV** for hierarchical data like org charts
- Use **XML** when you need precise control over positioning or custom shapes

### Step 2: Generate the diagram code

Write the diagram code in the chosen format.

### Step 3: Execute the script

Run the Python script to create the draw.io URL:

```bash
python scripts/generate_drawio_url.py -t <type> -c "<code>"
```

## Code Examples

### Mermaid Example

```
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[End]
```

### XML Example

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="Box" style="rounded=1;fillColor=#d5e8d4;" vertex="1" parent="1">
      <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

### CSV Example

```
# label: %name%
# style: rounded=1;whiteSpace=wrap;html=1;
# connect: {"from":"manager","to":"name","invert":true}
# layout: auto
name,manager
CEO,
CTO,CEO
CFO,CEO
```

## Script Arguments

| Argument | Description |
|----------|-------------|
| `-t, --type` | Diagram type (required): `mermaid`, `xml`, `csv` |
| `-c, --code` | Diagram code content (required) |

## Output

The script outputs a markdown link: `[Click to view diagram](<URL>)`

## Critical: XML Well-Formedness

When generating draw.io XML:
- **NEVER use double hyphens (`--`) inside XML comments**
- Escape special characters: `&amp;`, `&lt;`, `&gt;`, `&quot;`

## Security Notes

- The generated URL encodes diagram content; when opened, content is sent to `app.diagrams.net`
- Avoid embedding sensitive data in diagrams
- For sensitive content, use the draw.io desktop app
