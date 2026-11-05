<template>
  <div class="app-container">
    <header class="app-header">
      <h1>CAD Lightweight Viewer</h1>
      <div class="header-actions">
        <button @click="loadSampleModel" class="btn-primary">Load Sample Model</button>
        <label class="btn-secondary">
          Load File
          <input type="file" accept=".json,.xml,.bin" @change="handleFileUpload" hidden />
        </label>
      </div>
    </header>

    <main class="app-main">
      <CADViewer
        ref="viewerRef"
        :modelData="modelData"
        :loading="loading"
        @stats-update="handleStatsUpdate"
      />
    </main>

    <aside class="app-sidebar">
      <div class="sidebar-section">
        <h3>Model Statistics</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Parts</span>
            <span class="stat-value">{{ stats.parts || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Vertices</span>
            <span class="stat-value">{{ stats.vertices || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Triangles</span>
            <span class="stat-value">{{ stats.triangles || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">File Size</span>
            <span class="stat-value">{{ formatFileSize(stats.fileSize || 0) }}</span>
          </div>
        </div>
      </div>

      <div class="sidebar-section">
        <h3>Camera Controls</h3>
        <div class="control-buttons">
          <button @click="resetView">Reset View</button>
          <button @click="fitToView">Fit to View</button>
          <button @click="toggleWireframe">Wireframe</button>
          <button @click="toggleMaterials">Materials</button>
        </div>
      </div>

      <div class="sidebar-section">
        <h3>Lighting</h3>
        <div class="slider-control">
          <label>Ambient</label>
          <input
            type="range"
            v-model.number="lighting.ambient"
            min="0"
            max="1"
            step="0.1"
            @input="updateLighting"
          />
          <span>{{ lighting.ambient.toFixed(1) }}</span>
        </div>
        <div class="slider-control">
          <label>Directional</label>
          <input
            type="range"
            v-model.number="lighting.directional"
            min="0"
            max="2"
            step="0.1"
            @input="updateLighting"
          />
          <span>{{ lighting.directional.toFixed(1) }}</span>
        </div>
      </div>

      <div class="sidebar-section">
        <h3>Background Color</h3>
        <div class="color-picker">
          <input type="color" v-model="backgroundColor" @change="updateBackground" />
          <span>{{ backgroundColor }}</span>
        </div>
      </div>

      <div class="sidebar-section">
        <h3>About</h3>
        <p class="about-text">
          CAD Lightweight Viewer demonstrates WebGL-based 3D rendering
          using Three.js and Vue 3. Supports XML, JSON, and binary CAD formats.
        </p>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import CADViewer from './components/CADViewer.vue';

const viewerRef = ref(null);
const loading = ref(false);
const modelData = ref(null);
const stats = reactive({
  parts: 0,
  vertices: 0,
  triangles: 0,
  fileSize: 0,
});

const lighting = reactive({
  ambient: 0.4,
  directional: 0.8,
});

const backgroundColor = ref('#1a1a2e');

const sampleModel = {
  format: 'CAD-LIGHTWEIGHT-v1',
  version: '1.0',
  metadata: {
    productName: 'T53-8402000-002-20170727',
    version: '20170727',
    units: 'mm',
    author: 'CAD System',
    created: '2017-07-27T00:00:00Z',
  },
  boundingBox: {
    min: { x: -120.5, y: -85, z: 0 },
    max: { x: 120.5, y: 85, z: 75 },
  },
  materials: [
    { id: 0, name: 'Steel', color: { r: 0.65, g: 0.65, b: 0.7, a: 1 }, metalness: 0.85, roughness: 0.45 },
    { id: 1, name: 'Aluminum', color: { r: 0.85, g: 0.85, b: 0.9, a: 1 }, metalness: 0.75, roughness: 0.15 },
    { id: 2, name: 'Plastic', color: { r: 0.15, g: 0.15, b: 0.18, a: 1 }, metalness: 0.05, roughness: 0.7 },
  ],
  geometry: {
    vertices: [
      { x: -100, y: -60, z: 0, nx: 0, ny: 0, nz: -1, u: 0, v: 0 },
      { x: 100, y: -60, z: 0, nx: 0, ny: 0, nz: -1, u: 1, v: 0 },
      { x: 100, y: 60, z: 0, nx: 0, ny: 0, nz: -1, u: 1, v: 1 },
      { x: -100, y: 60, z: 0, nx: 0, ny: 0, nz: -1, u: 0, v: 1 },
      { x: -100, y: -60, z: 50, nx: 0, ny: 0, nz: 1, u: 0, v: 0 },
      { x: 100, y: -60, z: 50, nx: 0, ny: 0, nz: 1, u: 1, v: 0 },
      { x: 100, y: 60, z: 50, nx: 0, ny: 0, nz: 1, u: 1, v: 1 },
      { x: -100, y: 60, z: 50, nx: 0, ny: 0, nz: 1, u: 0, v: 1 },
    ],
    triangles: [
      { v1: 0, v2: 2, v3: 1, materialId: 0 },
      { v1: 0, v2: 3, v3: 2, materialId: 0 },
      { v1: 4, v2: 5, v3: 6, materialId: 0 },
      { v1: 4, v2: 6, v3: 7, materialId: 0 },
      { v1: 0, v2: 1, v3: 5, materialId: 0 },
      { v1: 0, v2: 5, v3: 4, materialId: 0 },
      { v1: 2, v2: 3, v3: 7, materialId: 0 },
      { v1: 2, v2: 7, v3: 6, materialId: 0 },
      { v1: 3, v2: 0, v3: 4, materialId: 0 },
      { v1: 3, v2: 4, v3: 7, materialId: 0 },
      { v1: 1, v2: 2, v3: 6, materialId: 0 },
      { v1: 1, v2: 6, v3: 5, materialId: 0 },
    ],
  },
  parts: [
    { id: 1, name: 'MainBody', parentId: 0, triStart: 0, triCount: 12, materialId: 0 },
  ],
};

const loadSampleModel = () => {
  loading.value = true;
  setTimeout(() => {
    modelData.value = sampleModel;
    stats.fileSize = JSON.stringify(sampleModel).length;
    loading.value = false;
  }, 300);
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  loading.value = true;
  stats.fileSize = file.size;

  try {
    const text = await file.text();
    let data;

    if (file.name.endsWith('.json')) {
      data = JSON.parse(text);
    } else if (file.name.endsWith('.xml')) {
      data = parseXMLToJSON(text);
    } else if (file.name.endsWith('.bin')) {
      data = parseBinaryCAD(text);
    } else {
      throw new Error('Unsupported file format');
    }

    modelData.value = data;
  } catch (error) {
    console.error('Failed to load file:', error);
    alert('Failed to load file: ' + error.message);
  } finally {
    loading.value = false;
  }
};

const parseXMLToJSON = (xmlText) => {
  const parser = new DOMParser();
  const xml = parser.parseFromString(xmlText, 'text/xml');

  const getText = (el, tag) => el.querySelector(tag)?.textContent;
  const getAttr = (el, tag, attr) => el.querySelector(tag)?.getAttribute(attr);

  const metadata = {
    productName: getText(xml, 'ProductName') || 'Unknown',
    version: getText(xml, 'CreatedDate') || '',
    units: xml.documentElement.getAttribute('units') || 'mm',
  };

  const materials = [];
  xml.querySelectorAll('Material').forEach((mat, i) => {
    const color = mat.querySelector('Color');
    materials.push({
      id: i,
      name: mat.getAttribute('name'),
      color: {
        r: parseFloat(color?.getAttribute('r') || 0.5),
        g: parseFloat(color?.getAttribute('g') || 0.5),
        b: parseFloat(color?.getAttribute('b') || 0.5),
        a: parseFloat(color?.getAttribute('a') || 1),
      },
      metalness: parseFloat(mat.querySelector('Metalness')?.getAttribute('value') || 0.5),
      roughness: parseFloat(mat.querySelector('Roughness')?.getAttribute('value') || 0.5),
    });
  });

  const vertices = [];
  xml.querySelectorAll('Vertex').forEach((v) => {
    vertices.push({
      x: parseFloat(v.getAttribute('x') || 0),
      y: parseFloat(v.getAttribute('y') || 0),
      z: parseFloat(v.getAttribute('z') || 0),
      nx: 0, ny: 0, nz: 1, u: 0, v: 0,
    });
  });

  const triangles = [];
  xml.querySelectorAll('Triangle').forEach((t) => {
    triangles.push({
      v1: parseInt(t.getAttribute('v1') || 0),
      v2: parseInt(t.getAttribute('v2') || 0),
      v3: parseInt(t.getAttribute('v3') || 0),
      materialId: 0,
    });
  });

  const parts = [];
  xml.querySelectorAll('Part').forEach((p, i) => {
    parts.push({
      id: parseInt(p.getAttribute('id') || i + 1),
      name: p.getAttribute('name'),
      parentId: parseInt(p.getAttribute('parentId') || 0),
      triStart: 0,
      triCount: triangles.length,
      materialId: parseInt(p.getAttribute('materialId') || 0),
    });
  });

  return { format: 'CAD-LIGHTWEIGHT-v1', metadata, materials, geometry: { vertices, triangles }, parts };
};

const parseBinaryCAD = (buffer) => {
  const data = new Uint8Array(buffer);
  const view = new DataView(buffer.buffer);
  let offset = 0;

  const readString = (len) => {
    const str = String.fromCharCode(...data.slice(offset, offset + len));
    offset += len;
    return str;
  };
  const readUint32 = () => {
    const val = view.getUint32(offset, true);
    offset += 4;
    return val;
  };
  const readFloat32 = () => {
    const val = view.getFloat32(offset, true);
    offset += 4;
    return val;
  };

  const magic = readString(4);
  if (magic !== 'CAD1') throw new Error('Invalid binary format');

  const metaLength = readUint32();
  const vertexCount = readUint32();
  const triangleCount = readUint32();
  const partCount = readUint32();
  offset += 8;

  const metaJson = String.fromCharCode(...data.slice(offset, offset + metaLength));
  const metadata = JSON.parse(metaJson);
  offset += metaLength;

  const vertices = [];
  for (let i = 0; i < vertexCount; i++) {
    vertices.push({
      x: readFloat32(), y: readFloat32(), z: readFloat32(),
      nx: readFloat32(), ny: readFloat32(), nz: readFloat32(),
      u: readFloat32(), v: readFloat32(),
    });
  }

  const triangles = [];
  for (let i = 0; i < triangleCount; i++) {
    triangles.push({ v1: readUint32(), v2: readUint32(), v3: readUint32(), materialId: 0 });
  }

  const parts = [];
  for (let i = 0; i < partCount; i++) {
    parts.push({
      id: readUint32(), parentId: readUint32(),
      triStart: readUint32(), triCount: readUint32(),
      materialId: readUint32(),
    });
  }

  return { format: 'CAD-LIGHTWEIGHT-v1', metadata, geometry: { vertices, triangles }, parts };
};

const handleStatsUpdate = (newStats) => {
  Object.assign(stats, newStats);
};

const resetView = () => viewerRef.value?.resetCamera();
const fitToView = () => viewerRef.value?.fitCameraToModel();
const toggleWireframe = () => viewerRef.value?.toggleWireframe();
const toggleMaterials = () => viewerRef.value?.toggleMaterials();

const updateLighting = () => viewerRef.value?.updateLighting(lighting);
const updateBackground = () => viewerRef.value?.updateBackground(backgroundColor.value);

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};
</script>

<style scoped>
.app-container {
  display: grid;
  grid-template-columns: 1fr 280px;
  grid-template-rows: 60px 1fr;
  height: 100vh;
  background: #0f0f1a;
  color: #fff;
}

.app-header {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-header h1 {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  border: none;
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.app-main {
  position: relative;
  overflow: hidden;
}

.app-sidebar {
  background: rgba(26, 26, 46, 0.95);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 24px;
}

.sidebar-section h3 {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #00d4ff;
}

.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-buttons button {
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: white;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.control-buttons button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.slider-control {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.slider-control label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  min-width: 80px;
}

.slider-control input[type="range"] {
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  outline: none;
}

.slider-control input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: #00d4ff;
  border-radius: 50%;
  cursor: pointer;
}

.slider-control span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 30px;
  text-align: right;
}

.color-picker {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker input[type="color"] {
  width: 40px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: transparent;
}

.color-picker span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-family: monospace;
}

.about-text {
  font-size: 13px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.6);
}
</style>