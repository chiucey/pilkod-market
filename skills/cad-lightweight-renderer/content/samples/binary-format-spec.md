---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 810996b73a93d530f4a91cc8a308cc15
    PropagateID: 810996b73a93d530f4a91cc8a308cc15
    ReservedCode1: 3045022003a1d51c3a21d6025aa2a6c300cb59d887cd64c260e9c2ab857ffd160ace982f02210094c4dce6c70b0bdb3c70a8aa44f9fb4a1d668cc207bd30698095abffe1b29aef
    ReservedCode2: 3045022033c5eec44bcbead1e655ab8734be358cabef2b40c7ac92a05471312f6ce91f56022100fd6416e20bc9fe0714e902b1ff185534e5b3c9b46900b1edac89d61bf40ad05b
---

# CAD Binary Format Specification

## Overview

The CAD Binary Format (`.bin`) is an efficient binary representation for lightweight CAD models optimized for web-based 3D rendering. It uses compact binary encoding to minimize file size and loading time.

## File Structure

```
┌─────────────────────────────────────────────────────┐
│                    FILE HEADER                       │
│                      (32 bytes)                      │
├─────────────────────────────────────────────────────┤
│                   METADATA SECTION                   │
│                    (Variable)                        │
├─────────────────────────────────────────────────────┤
│                  VERTEX DATA SECTION                │
│               (32 bytes per vertex)                  │
├─────────────────────────────────────────────────────┤
│               TRIANGLE DATA SECTION                 │
│               (12 bytes per triangle)               │
├─────────────────────────────────────────────────────┤
│                   PART DATA SECTION                 │
│               (20 bytes per part)                   │
└─────────────────────────────────────────────────────┘
```

## Header Section (32 bytes)

| Offset | Size | Field | Type | Description |
|--------|------|-------|------|-------------|
| 0-3 | 4 | Magic | char[4] | Format identifier: "CAD1" |
| 4-7 | 4 | Version | uint32 | Format version (1) |
| 8-11 | 4 | MetaLength | uint32 | Metadata JSON string length |
| 12-15 | 4 | VertexCount | uint32 | Number of vertices |
| 16-19 | 4 | TriangleCount | uint32 | Number of triangles |
| 20-23 | 4 | PartCount | uint32 | Number of parts |
| 24-31 | 8 | Reserved | byte[8] | Reserved for future use |

## Metadata Section (Variable)

A JSON-encoded string containing model metadata. Must be `MetaLength` bytes.

### Metadata JSON Schema

```json
{
  "productName": "string",
  "version": "string",
  "units": "string",
  "author": "string",
  "created": "ISO8601 string",
  "revision": "string"
}
```

## Vertex Data Section (32 bytes per vertex)

Each vertex stores position, normal, and texture coordinates.

| Offset | Size | Field | Type | Description |
|--------|------|-------|------|-------------|
| 0-3 | 4 | x | float32 | X coordinate |
| 4-7 | 4 | y | float32 | Y coordinate |
| 8-11 | 4 | z | float32 | Z coordinate |
| 12-15 | 4 | nx | float32 | Normal X component |
| 16-19 | 4 | ny | float32 | Normal Y component |
| 20-23 | 4 | nz | float32 | Normal Z component |
| 24-27 | 4 | u | float32 | U texture coordinate |
| 28-31 | 4 | v | float32 | V texture coordinate |

## Triangle Data Section (12 bytes per triangle)

Each triangle stores indices into the vertex array.

| Offset | Size | Field | Type | Description |
|--------|------|-------|------|-------------|
| 0-3 | 4 | v1 | uint32 | Index of first vertex |
| 4-7 | 4 | v2 | uint32 | Index of second vertex |
| 8-11 | 4 | v3 | uint32 | Index of third vertex |

## Part Data Section (20 bytes per part)

Each part defines a component of the CAD assembly.

| Offset | Size | Field | Type | Description |
|--------|------|-------|------|-------------|
| 0-3 | 4 | id | uint32 | Unique part identifier |
| 4-7 | 4 | parentId | uint32 | Parent part ID (0 = root) |
| 8-11 | 4 | triStart | uint32 | Starting triangle index |
| 12-15 | 4 | triCount | uint32 | Number of triangles in part |
| 16-19 | 4 | materialId | uint32 | Material identifier |

## Byte Order

All multi-byte values use **little-endian** byte order for compatibility with x86/x64 architectures.

## Example File Size Calculation

For a model with:
- 10,000 vertices
- 20,000 triangles
- 10 parts
- 200 bytes of metadata JSON

```
Header:     32 bytes
Metadata:   200 bytes
Vertices:   10,000 × 32 = 320,000 bytes
Triangles:  20,000 × 12 = 240,000 bytes
Parts:      10 × 20 = 200 bytes
─────────────────────────────
Total:      560,432 bytes (~547 KB)
```

## Reference Implementation

See `generate-binary.js` for a complete reference implementation in Node.js including:
- Binary file generation
- Binary file parsing
- File verification

## Usage in Browser

```javascript
// Fetch and parse binary CAD file
async function loadCADBinary(url) {
  const response = await fetch(url);
  const buffer = await response.arrayBuffer();
  const parser = new CADBinaryParser(buffer);
  return parser.parse();
}

class CADBinaryParser {
  constructor(buffer) {
    this.buffer = buffer;
    this.view = new DataView(buffer);
    this.uint8 = new Uint8Array(buffer);
    this.offset = 0;
  }

  parse() {
    // Verify magic number
    const magic = this.readString(4);
    if (magic !== 'CAD1') throw new Error('Invalid format');

    // Read header
    const version = this.readUint32();
    const metaLength = this.readUint32();
    const vertexCount = this.readUint32();
    const triangleCount = this.readUint32();
    const partCount = this.readUint32();
    this.offset += 8; // Skip reserved

    // Read metadata
    const metaJson = this.readString(metaLength);
    const metadata = JSON.parse(metaJson);

    // Read vertices
    const vertices = [];
    for (let i = 0; i < vertexCount; i++) {
      vertices.push({
        x: this.readFloat32(), y: this.readFloat32(), z: this.readFloat32(),
        nx: this.readFloat32(), ny: this.readFloat32(), nz: this.readFloat32(),
        u: this.readFloat32(), v: this.readFloat32()
      });
    }

    // Read triangles
    const triangles = [];
    for (let i = 0; i < triangleCount; i++) {
      triangles.push({
        v1: this.readUint32(), v2: this.readUint32(), v3: this.readUint32()
      });
    }

    // Read parts
    const parts = [];
    for (let i = 0; i < partCount; i++) {
      parts.push({
        id: this.readUint32(), parentId: this.readUint32(),
        triStart: this.readUint32(), triCount: this.readUint32(),
        materialId: this.readUint32()
      });
    }

    return { metadata, vertices, triangles, parts };
  }

  readString(length) {
    const bytes = this.uint8.slice(this.offset, this.offset + length);
    this.offset += length;
    return String.fromCharCode(...bytes);
  }

  readUint32() {
    const value = this.view.getUint32(this.offset, true);
    this.offset += 4;
    return value;
  }

  readFloat32() {
    const value = this.view.getFloat32(this.offset, true);
    this.offset += 4;
    return value;
  }
}
```

## Format Comparison

| Format | Human Readable | File Size | Parse Speed | Use Case |
|--------|----------------|-----------|-------------|----------|
| XML | Yes (high) | Large | Slow | Documentation, debugging |
| JSON | Yes (medium) | Medium | Medium | Web APIs, config files |
| Binary | No | Small | Fast | Production data transfer |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1 | 2024-01 | Initial specification |
| 1.1 | - | Reserved for future extension |