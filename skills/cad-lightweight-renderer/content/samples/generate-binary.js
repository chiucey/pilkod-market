/**
 * Binary CAD Format Generator
 *
 * This script generates a sample CAD model in binary format.
 * Binary format is optimized for efficient data transfer and fast loading.
 *
 * File Structure:
 * - Header: 32 bytes (magic, version, metadata length, counts)
 * - Metadata: JSON string describing model metadata
 * - Vertex Data: 32 bytes per vertex (position, normal, uv)
 * - Triangle Data: 12 bytes per triangle (3 uint32 indices)
 * - Part Data: 20 bytes per part (id, parentId, triStart, triCount, materialId)
 *
 * Usage: node generate-binary.js [output_path]
 */

const fs = require('fs');
const path = require('path');

// CAD Binary Format Specification
const MAGIC = 'CAD1';
const VERSION = 1;
const VERTEX_SIZE = 32; // 8 floats * 4 bytes
const TRIANGLE_SIZE = 12; // 3 uint32 * 4 bytes
const PART_SIZE = 20; // 5 uint32 * 4 bytes

/**
 * Create a Buffer with big-endian or little-endian writing
 */
class BinaryWriter {
  constructor(size) {
    this.buffer = Buffer.alloc(size);
    this.offset = 0;
    this.littleEndian = true;
  }

  writeString(str) {
    for (let i = 0; i < str.length; i++) {
      this.buffer[this.offset++] = str.charCodeAt(i);
    }
  }

  writeUint32(value) {
    this.buffer.writeUInt32LE(value, this.offset);
    this.offset += 4;
  }

  writeFloat32(value) {
    this.buffer.writeFloatLE(value, this.offset);
    this.offset += 4;
  }

  writeBytes(bytes) {
    bytes.copy(this.buffer, this.offset);
    this.offset += bytes.length;
  }

  getBuffer() {
    return this.buffer;
  }
}

/**
 * Generate sample CAD model data
 */
function generateSampleModel() {
  const metadata = {
    productName: 'T53-8402000-002-20170727',
    version: '20170727',
    units: 'mm',
    author: 'CAD System',
    created: '2017-07-27T00:00:00Z',
    revision: 'A'
  };

  // Generate vertices for a simple box with 4 corner holes
  const vertices = [
    // Box vertices (8 corners)
    { x: -100, y: -60, z: 0, nx: 0, ny: 0, nz: -1, u: 0, v: 0 },
    { x: 100, y: -60, z: 0, nx: 0, ny: 0, nz: -1, u: 1, v: 0 },
    { x: 100, y: 60, z: 0, nx: 0, ny: 0, nz: -1, u: 1, v: 1 },
    { x: -100, y: 60, z: 0, nx: 0, ny: 0, nz: -1, u: 0, v: 1 },
    { x: -100, y: -60, z: 50, nx: 0, ny: 0, nz: 1, u: 0, v: 0 },
    { x: 100, y: -60, z: 50, nx: 0, ny: 0, nz: 1, u: 1, v: 0 },
    { x: 100, y: 60, z: 50, nx: 0, ny: 0, nz: 1, u: 1, v: 1 },
    { x: -100, y: 60, z: 50, nx: 0, ny: 0, nz: 1, u: 0, v: 1 },
    // Hole 1 center vertices (8)
    { x: 50, y: 30, z: 0, nx: 1, ny: 0, nz: 0, u: 0, v: 0 },
    { x: 50, y: 30, z: 55, nx: 1, ny: 0, nz: 0, u: 0, v: 1 },
    { x: 50, y: 30, z: 0, nx: 0, ny: 1, nz: 0, u: 0, v: 0 },
    { x: 50, y: 30, z: 55, nx: 0, ny: 1, nz: 0, u: 0, v: 1 },
    { x: 50, y: 30, z: 0, nx: -1, ny: 0, nz: 0, u: 0, v: 0 },
    { x: 50, y: 30, z: 55, nx: -1, ny: 0, nz: 0, u: 0, v: 1 },
    { x: 50, y: 30, z: 0, nx: 0, ny: -1, nz: 0, u: 0, v: 0 },
    { x: 50, y: 30, z: 55, nx: 0, ny: -1, nz: 0, u: 0, v: 1 }
  ];

  const triangles = [
    // Box faces (12 triangles)
    { v1: 0, v2: 2, v3: 1 },
    { v1: 0, v2: 3, v3: 2 },
    { v1: 4, v2: 5, v3: 6 },
    { v1: 4, v2: 6, v3: 7 },
    { v1: 0, v2: 1, v3: 5 },
    { v1: 0, v2: 5, v3: 4 },
    { v1: 2, v2: 3, v3: 7 },
    { v1: 2, v2: 7, v3: 6 },
    { v1: 3, v2: 0, v3: 4 },
    { v1: 3, v2: 4, v3: 7 },
    { v1: 1, v2: 2, v3: 6 },
    { v1: 1, v2: 6, v3: 5 }
  ];

  const parts = [
    { id: 1, parentId: 0, triStart: 0, triCount: 12, materialId: 0 },
    { id: 2, parentId: 1, triStart: 12, triCount: 8, materialId: 1 },
    { id: 3, parentId: 1, triStart: 20, triCount: 8, materialId: 1 },
    { id: 4, parentId: 1, triStart: 28, triCount: 8, materialId: 1 },
    { id: 5, parentId: 1, triStart: 36, triCount: 8, materialId: 1 }
  ];

  return { metadata, vertices, triangles, parts };
}

/**
 * Generate binary CAD file
 */
function generateBinaryFile(modelData) {
  const { metadata, vertices, triangles, parts } = modelData;
  const metaJson = JSON.stringify(metadata);
  const metaLength = metaJson.length;

  // Calculate total size
  const headerSize = 32;
  const vertexDataSize = vertices.length * VERTEX_SIZE;
  const triangleDataSize = triangles.length * TRIANGLE_SIZE;
  const partDataSize = parts.length * PART_SIZE;
  const totalSize = headerSize + metaLength + vertexDataSize + triangleDataSize + partDataSize;

  const writer = new BinaryWriter(totalSize);

  // Write header
  writer.writeString(MAGIC);
  writer.writeUint32(VERSION);
  writer.writeUint32(metaLength);
  writer.writeUint32(vertices.length);
  writer.writeUint32(triangles.length);
  writer.writeUint32(parts.length);
  writer.writeBytes(Buffer.alloc(8)); // Reserved bytes

  // Write metadata
  writer.writeString(metaJson);

  // Write vertex data
  for (const v of vertices) {
    writer.writeFloat32(v.x);
    writer.writeFloat32(v.y);
    writer.writeFloat32(v.z);
    writer.writeFloat32(v.nx);
    writer.writeFloat32(v.ny);
    writer.writeFloat32(v.nz);
    writer.writeFloat32(v.u);
    writer.writeFloat32(v.v);
  }

  // Write triangle indices
  for (const t of triangles) {
    writer.writeUint32(t.v1);
    writer.writeUint32(t.v2);
    writer.writeUint32(t.v3);
  }

  // Write part data
  for (const p of parts) {
    writer.writeUint32(p.id);
    writer.writeUint32(p.parentId);
    writer.writeUint32(p.triStart);
    writer.writeUint32(p.triCount);
    writer.writeUint32(p.materialId);
  }

  return writer.getBuffer();
}

/**
 * Parse binary CAD file (for verification)
 */
function parseBinaryFile(buffer) {
  const view = new DataView(buffer);
  let offset = 0;

  // Read magic
  const magicBytes = new Uint8Array(buffer, offset, 4);
  const magic = String.fromCharCode(...magicBytes);
  offset += 4;

  if (magic !== MAGIC) {
    throw new Error(`Invalid magic number: expected ${MAGIC}, got ${magic}`);
  }

  // Read header
  const version = view.getUint32(offset, true); offset += 4;
  const metaLength = view.getUint32(offset, true); offset += 4;
  const vertexCount = view.getUint32(offset, true); offset += 4;
  const triangleCount = view.getUint32(offset, true); offset += 4;
  const partCount = view.getUint32(offset, true); offset += 4;
  offset += 8; // Skip reserved

  // Read metadata
  const metaBytes = new Uint8Array(buffer, offset, metaLength);
  const metadata = JSON.parse(String.fromCharCode(...metaBytes));
  offset += metaLength;

  // Read vertices
  const vertices = [];
  for (let i = 0; i < vertexCount; i++) {
    vertices.push({
      x: view.getFloat32(offset, true); offset += 4,
      y: view.getFloat32(offset, true); offset += 4,
      z: view.getFloat32(offset, true); offset += 4,
      nx: view.getFloat32(offset, true); offset += 4,
      ny: view.getFloat32(offset, true); offset += 4,
      nz: view.getFloat32(offset, true); offset += 4,
      u: view.getFloat32(offset, true); offset += 4,
      v: view.getFloat32(offset, true); offset += 4
    });
  }

  // Read triangles
  const triangles = [];
  for (let i = 0; i < triangleCount; i++) {
    triangles.push({
      v1: view.getUint32(offset, true); offset += 4,
      v2: view.getUint32(offset, true); offset += 4,
      v3: view.getUint32(offset, true); offset += 4
    });
  }

  // Read parts
  const parts = [];
  for (let i = 0; i < partCount; i++) {
    parts.push({
      id: view.getUint32(offset, true); offset += 4,
      parentId: view.getUint32(offset, true); offset += 4,
      triStart: view.getUint32(offset, true); offset += 4,
      triCount: view.getUint32(offset, true); offset += 4,
      materialId: view.getUint32(offset, true); offset += 4
    });
  }

  return { metadata, vertices, triangles, parts };
}

// Main execution
function main() {
  const outputPath = process.argv[2] || path.join(__dirname, 'cad-geometry.bin');

  console.log('Generating sample CAD binary file...');
  console.log(`Output: ${outputPath}`);

  const modelData = generateSampleModel();
  console.log(`Model: ${modelData.metadata.productName}`);
  console.log(`Vertices: ${modelData.vertices.length}`);
  console.log(`Triangles: ${modelData.triangles.length}`);
  console.log(`Parts: ${modelData.parts.length}`);

  const binaryData = generateBinaryFile(modelData);
  fs.writeFileSync(outputPath, binaryData);
  console.log(`File size: ${binaryData.length} bytes`);

  // Verify by parsing
  console.log('\nVerifying generated file...');
  const parsed = parseBinaryFile(binaryData);
  console.log(`Parsed successfully!`);
  console.log(`Product: ${parsed.metadata.productName}`);

  console.log('\nDone!');
}

main();