---
name: cad-lightweight-renderer
description: A frontend rendering master skill for parsing CAD model files (XML, JSON, Binary) and rendering 3D geometry as WebGL/Three.js triangles. Use this skill when users need to render CAD models, parse geometric data, create 3D visualizations, or build CAD lightweight viewers using cutting-edge frontend technologies.
---

# CAD Lightweight Renderer - Frontend Rendering Master

## Overview

This skill is a **frontend rendering master** that specializes in reading CAD model files (XML, JSON, binary formats) and rendering them as 3D triangles on canvas using cutting-edge WebGL and Three.js technologies. No backend required - pure client-side power.

## Core Capabilities

- **File Parsing**: Read XML, JSON, and binary CAD model files directly in the browser
- **Geometry Rendering**: Convert parsed data into Three.js BufferGeometry triangles
- **Real-time Controls**: Orbit, zoom, pan with smooth animations
- **Material System**: PBR materials with metalness, roughness, and custom colors
- **Performance**: LOD, instancing, and progressive loading for large models

## Supported File Formats

### 1. XML Format

Human-readable format for CAD model hierarchy and geometry:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CADModel version="1.0" units="mm">
  <Metadata>
    <ProductName>T53-8402000-002</ProductName>
    <Author>CAD System</Author>
    <CreatedDate>2017-07-27</CreatedDate>
  </Metadata>
  <Assembly>
    <Part id="1" name="MainBody" parentId="0">
      <Geometry type="mesh">
        <Vertices count="1234">
          <Vertex index="0" x="0" y="0" z="0"/>
          <Vertex index="1" x="10" y="0" z="0"/>
        </Vertices>
        <Triangles count="2345">
          <Triangle v1="0" v2="1" v3="2" normal="0,0,1"/>
        </Triangles>
      </Geometry>
      <Material>
        <Color r="0.8" g="0.2" b="0.2" a="1.0"/>
        <Metalness value="0.8"/>
        <Roughness value="0.3"/>
      </Material>
    </Part>
  </Assembly>
</CADModel>
```

### 2. JSON Format

Lightweight format for easy JavaScript processing:

```json
{
  "format": "CAD-LIGHTWEIGHT-v1",
  "metadata": {
    "productName": "T53-8402000-002",
    "version": "20170727",
    "units": "mm",
    "author": "CAD System"
  },
  "geometry": {
    "vertices": [
      { "x": 0, "y": 0, "z": 0, "nx": 0, "ny": 0, "nz": 1, "u": 0, "v": 0 },
      { "x": 10, "y": 0, "z": 0, "nx": 0, "ny": 0, "nz": 1, "u": 1, "v": 0 }
    ],
    "triangles": [
      { "v1": 0, "v2": 1, "v3": 2, "materialId": 0 }
    ]
  },
  "materials": [
    {
      "id": 0,
      "name": "Steel",
      "color": { "r": 0.7, "g": 0.7, "b": 0.7, "a": 1.0 },
      "metalness": 0.9,
      "roughness": 0.2
    }
  ]
}
```

### 3. Binary Format

Efficient binary format for large models:

```
Header (32 bytes):
┌─────────────────────────────────────────┐
│ 0-3:   Magic "CAD1" (4 bytes)          │
│ 4-7:   Version (4 bytes, uint32)        │
│ 8-11:  Metadata length (4 bytes)        │
│ 12-15: Vertex count (4 bytes)           │
│ 16-19: Triangle count (4 bytes)          │
│ 20-23: Part count (4 bytes)             │
│ 24-31: Reserved (8 bytes)               │
└─────────────────────────────────────────┘

Vertex data (32 bytes per vertex):
┌─────────────────────────────────────────┐
│ x, y, z, nx, ny, nz, u, v (8x float32) │
└─────────────────────────────────────────┘

Triangle data (12 bytes per triangle):
┌─────────────────────────────────────────┐
│ v1, v2, v3 (3x uint32)                 │
└─────────────────────────────────────────┘
```

## Three.js Rendering Implementation

### Core Renderer Class

```javascript
/**
 * CADModelRenderer - Pure frontend 3D CAD renderer
 *
 * Features:
 * - File drag-and-drop support
 * - XML, JSON, binary parsing
 * - Real-time orbit controls
 * - Material customization
 * - Performance optimization
 */
class CADModelRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.model = null;
    this.animationId = null;

    this.init();
  }

  init() {
    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x1a1a2e);

    // Camera setup
    const aspect = this.canvas.clientWidth / this.canvas.clientHeight;
    this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100000);
    this.camera.position.set(200, 150, 200);

    // Renderer setup
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;

    // Controls setup
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.screenSpacePanning = true;
    this.controls.minDistance = 10;
    this.controls.maxDistance = 100000;

    // Lighting setup
    this.setupLighting();

    // Grid helper
    const grid = new THREE.GridHelper(1000, 50, 0x333366, 0x222244);
    this.scene.add(grid);

    // Axes helper
    const axes = new THREE.AxesHelper(150);
    this.scene.add(axes);

    // Start animation loop
    this.animate();
  }

  setupLighting() {
    // Ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambient);

    // Main directional light
    const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
    mainLight.position.set(100, 150, 100);
    mainLight.castShadow = true;
    this.scene.add(mainLight);

    // Fill light
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-100, 50, -100);
    this.scene.add(fillLight);

    // Rim light for edge definition
    const rimLight = new THREE.DirectionalLight(0x00d4ff, 0.2);
    rimLight.position.set(0, -100, 100);
    this.scene.add(rimLight);
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  // ========================================
  // FILE PARSING
  // ========================================

  /**
   * Load model from file (auto-detect format)
   */
  async loadFromFile(file) {
    const extension = file.name.split('.').pop().toLowerCase();

    try {
      let data;
      if (extension === 'json') {
        data = await this.parseJSON(file);
      } else if (extension === 'xml') {
        data = await this.parseXML(file);
      } else if (extension === 'bin' || extension === 'dat') {
        data = await this.parseBinary(file);
      } else {
        throw new Error(`Unsupported file format: .${extension}`);
      }

      this.renderModel(data);
      return { success: true, data };
    } catch (error) {
      console.error('Failed to load file:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Parse JSON file
   */
  async parseJSON(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          resolve(data);
        } catch (err) {
          reject(new Error('Invalid JSON format'));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }

  /**
   * Parse XML file
   */
  async parseXML(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const parser = new DOMParser();
        const xml = parser.parseFromString(e.target.result, 'text/xml');

        // Extract vertices
        const vertices = [];
        xml.querySelectorAll('Vertex').forEach((v, i) => {
          vertices.push({
            x: parseFloat(v.getAttribute('x') || 0),
            y: parseFloat(v.getAttribute('y') || 0),
            z: parseFloat(v.getAttribute('z') || 0),
            nx: 0, ny: 0, nz: 1, u: 0, v: 0
          });
        });

        // Extract triangles
        const triangles = [];
        xml.querySelectorAll('Triangle').forEach(t => {
          triangles.push({
            v1: parseInt(t.getAttribute('v1') || 0),
            v2: parseInt(t.getAttribute('v2') || 0),
            v3: parseInt(t.getAttribute('v3') || 0),
            materialId: 0
          });
        });

        // Extract metadata
        const metadata = {
          productName: xml.querySelector('ProductName')?.textContent || 'Unknown',
          created: xml.querySelector('CreatedDate')?.textContent || new Date().toISOString()
        };

        resolve({
          format: 'CAD-XML',
          metadata,
          geometry: { vertices, triangles }
        });
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }

  /**
   * Parse binary file
   */
  async parseBinary(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const buffer = e.target.result;
        const view = new DataView(buffer);
        const uint8 = new Uint8Array(buffer);
        let offset = 0;

        // Read magic number
        const magic = String.fromCharCode(...uint8.slice(offset, offset + 4));
        if (magic !== 'CAD1') {
          reject(new Error('Invalid binary format'));
          return;
        }
        offset += 4;

        // Read header
        const version = view.getUint32(offset, true); offset += 4;
        const metaLength = view.getUint32(offset, true); offset += 4;
        const vertexCount = view.getUint32(offset, true); offset += 4;
        const triangleCount = view.getUint32(offset, true); offset += 4;
        const partCount = view.getUint32(offset, true); offset += 4;
        offset += 8; // Reserved

        // Read metadata
        const metaJson = String.fromCharCode(...uint8.slice(offset, offset + metaLength));
        const metadata = JSON.parse(metaJson);
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

        resolve({
          format: 'CAD-BINARY',
          metadata,
          geometry: { vertices, triangles }
        });
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsArrayBuffer(file);
    });
  }

  // ========================================
  // MODEL RENDERING
  // ========================================

  /**
   * Render parsed model data
   */
  renderModel(data) {
    // Remove existing model
    if (this.model) {
      this.scene.remove(this.model);
      this.disposeModel(this.model);
    }

    // Create new model group
    this.model = new THREE.Group();

    const { vertices, triangles } = data.geometry;

    // Build position array
    const positions = new Float32Array(vertices.length * 3);
    const normals = new Float32Array(vertices.length * 3);

    vertices.forEach((v, i) => {
      positions[i * 3] = v.x;
      positions[i * 3 + 1] = v.y;
      positions[i * 3 + 2] = v.z;
      normals[i * 3] = v.nx || 0;
      normals[i * 3 + 1] = v.ny || 0;
      normals[i * 3 + 2] = v.nz || 0;
    });

    // Build index array
    const indices = new Uint32Array(triangles.length * 3);
    triangles.forEach((t, i) => {
      indices[i * 3] = t.v1;
      indices[i * 3 + 1] = t.v2;
      indices[i * 3 + 2] = t.v3;
    });

    // Create geometry
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    geometry.computeVertexNormals();

    // Create material
    let material;
    if (data.materials && data.materials.length > 0) {
      const matData = data.materials[0];
      material = new THREE.MeshStandardMaterial({
        color: new THREE.Color(matData.color.r, matData.color.g, matData.color.b),
        metalness: matData.metalness || 0.5,
        roughness: matData.roughness || 0.5,
        side: THREE.DoubleSide
      });
    } else {
      material = new THREE.MeshStandardMaterial({
        color: 0x888888,
        metalness: 0.8,
        roughness: 0.3,
        side: THREE.DoubleSide
      });
    }

    // Create mesh
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    this.model.add(mesh);

    // Add to scene
    this.scene.add(this.model);

    // Auto-fit camera
    this.fitCameraToModel();
  }

  /**
   * Dispose model resources
   */
  disposeModel(model) {
    model.traverse((child) => {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose());
        } else {
          child.material.dispose();
        }
      }
    });
  }

  /**
   * Fit camera to model bounds
   */
  fitCameraToModel() {
    if (!this.model) return;

    const box = new THREE.Box3().setFromObject(this.model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = (this.camera.fov * Math.PI) / 180;
    const cameraZ = Math.abs(maxDim / Math.tan(fov / 2)) * 1.5;

    this.camera.position.set(
      center.x + cameraZ * 0.5,
      center.y + cameraZ * 0.4,
      center.z + cameraZ * 0.8
    );
    this.controls.target.copy(center);
    this.controls.update();
  }

  // ========================================
  // CONTROLS
  // ========================================

  resetView() {
    this.fitCameraToModel();
  }

  toggleWireframe() {
    if (!this.model) return;
    this.model.traverse((child) => {
      if (child.isMesh && child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.wireframe = !m.wireframe);
        } else {
          child.material.wireframe = !child.material.wireframe;
        }
      }
    });
  }

  setBackgroundColor(color) {
    this.scene.background = new THREE.Color(color);
  }

  // ========================================
  // CLEANUP
  // ========================================

  dispose() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    if (this.model) {
      this.disposeModel(this.model);
    }
    this.renderer?.dispose();
    this.controls?.dispose();
  }
}
```

## Advanced Rendering Features

### 1. Progressive Loading for Large Models

```javascript
/**
 * Progressive CAD Model Loader
 * Loads model in chunks to prevent UI blocking
 */
class ProgressiveCADLoader {
  constructor(renderer, onProgress) {
    this.renderer = renderer;
    this.onProgress = onProgress;
    this.loaded = 0;
    this.total = 0;
  }

  async load(data, chunkSize = 5000) {
    const vertices = data.geometry.vertices;
    const triangles = data.geometry.triangles;
    this.total = Math.ceil(vertices.length / chunkSize) +
                 Math.ceil(triangles.length / chunkSize);

    const geometry = new THREE.BufferGeometry();
    const positions = [];
    const normals = [];
    const indices = [];

    // Load vertices in chunks
    for (let i = 0; i < vertices.length; i += chunkSize) {
      const chunk = vertices.slice(i, Math.min(i + chunkSize, vertices.length));
      chunk.forEach(v => {
        positions.push(v.x, v.y, v.z);
        normals.push(v.nx || 0, v.ny || 0, v.nz || 0);
      });
      this.loaded++;
      this.onProgress?.(this.loaded / this.total);
      await new Promise(r => setTimeout(r, 0)); // Yield to main thread
    }

    // Load triangles in chunks
    for (let i = 0; i < triangles.length; i += chunkSize) {
      const chunk = triangles.slice(i, Math.min(i + chunkSize, triangles.length));
      chunk.forEach(t => {
        indices.push(t.v1, t.v2, t.v3);
      });
      this.loaded++;
      this.onProgress?.(this.loaded / this.total);
      await new Promise(r => setTimeout(r, 0));
    }

    // Finalize geometry
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setIndex(indices);

    return geometry;
  }
}
```

### 2. Level of Detail (LOD) System

```javascript
/**
 * CAD LOD Manager
 * Switches geometry detail based on camera distance
 */
class CADLODManager {
  constructor() {
    this.levels = [];
    this.currentLevel = -1;
  }

  addLevel(distance, geometry, material) {
    this.levels.push({ distance, geometry, material });
    this.levels.sort((a, b) => a.distance - b.distance);
  }

  getLevel(cameraDistance) {
    let targetLevel = this.levels[this.levels.length - 1];

    for (const level of this.levels) {
      if (cameraDistance > level.distance) {
        targetLevel = level;
      }
    }

    return targetLevel;
  }

  update(camera, mesh) {
    const distance = camera.position.distanceTo(mesh.position);
    const targetLevel = this.getLevel(distance);
    const targetIndex = this.levels.indexOf(targetLevel);

    if (this.currentLevel !== targetIndex) {
      mesh.geometry = targetLevel.geometry;
      mesh.material = targetLevel.material;
      this.currentLevel = targetIndex;
    }
  }
}
```

### 3. Instanced Mesh Rendering

```javascript
/**
 * CAD Instanced Renderer
 * Efficiently renders repeated geometries (bolts, holes, etc.)
 */
class CADInstancedRenderer {
  constructor(scene) {
    this.scene = scene;
    this.instances = new Map();
  }

  addInstance(key, geometry, material, positions) {
    const instanceCount = positions.length;
    const instancedMesh = new THREE.InstancedMesh(geometry, material, instanceCount);

    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    const scale = new THREE.Vector3(1, 1, 1);

    positions.forEach((pos, i) => {
      position.set(pos.x, pos.y, pos.z);
      matrix.compose(position, quaternion, scale);
      instancedMesh.setMatrixAt(i, matrix);
    });

    instancedMesh.instanceMatrix.needsUpdate = true;
    this.scene.add(instancedMesh);
    this.instances.set(key, instancedMesh);
  }

  removeInstance(key) {
    const mesh = this.instances.get(key);
    if (mesh) {
      this.scene.remove(mesh);
      mesh.geometry?.dispose();
      mesh.material?.dispose();
      this.instances.delete(key);
    }
  }
}
```

## Usage Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>CAD Viewer - Frontend Rendering</title>
  <style>
    body { margin: 0; overflow: hidden; background: #0a0a0f; }
    #canvas { display: block; }
    .controls {
      position: fixed;
      top: 20px;
      left: 20px;
      display: flex;
      gap: 10px;
    }
    button {
      padding: 10px 20px;
      background: rgba(0, 212, 255, 0.2);
      border: 1px solid #00d4ff;
      border-radius: 8px;
      color: white;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.3s;
    }
    button:hover {
      background: rgba(0, 212, 255, 0.4);
      transform: translateY(-2px);
    }
    .drop-zone {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 212, 255, 0.1);
      border: 3px dashed #00d4ff;
      display: none;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: #00d4ff;
    }
    .drop-zone.active { display: flex; }
  </style>
</head>
<body>
  <canvas id="canvas"></canvas>
  <div class="controls">
    <button onclick="renderer.resetView()">Reset View</button>
    <button onclick="renderer.toggleWireframe()">Wireframe</button>
    <button onclick="document.getElementById('fileInput').click()">Load File</button>
    <input type="file" id="fileInput" accept=".json,.xml,.bin" hidden onchange="handleFile(this.files[0])">
  </div>
  <div class="drop-zone" id="dropZone">Drop CAD file here</div>

  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
      }
    }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    // Initialize renderer
    const canvas = document.getElementById('canvas');
    const renderer = new CADModelRenderer(canvas);

    // Global function for file input
    window.handleFile = async (file) => {
      if (file) {
        const result = await renderer.loadFromFile(file);
        console.log(result);
      }
    };

    // Drag and drop support
    const dropZone = document.getElementById('dropZone');

    document.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('active');
    });

    document.addEventListener('dragleave', () => {
      dropZone.classList.remove('active');
    });

    document.addEventListener('drop', async (e) => {
      e.preventDefault();
      dropZone.classList.remove('active');
      const file = e.dataTransfer.files[0];
      if (file) {
        await renderer.loadFromFile(file);
      }
    });
  </script>
</body>
</html>
```

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| Model not visible | Check coordinate system and scale |
| Material issues | Verify normal calculations |
| Performance lag | Enable instancing or LOD |
| Memory overflow | Use progressive loading |
| File won't load | Verify format matches extension |
| Black canvas | Check WebGL context initialization |

## Related Resources

- [Three.js Documentation](https://threejs.org/docs/)
- [WebGL Specification](https://www.khronos.org/webgl/)
- [BufferGeometry API](https://threejs.org/docs/#api/en/core/BufferGeometry)