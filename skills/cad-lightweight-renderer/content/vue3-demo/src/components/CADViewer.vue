<template>
  <div class="cad-viewer" ref="containerRef">
    <canvas ref="canvasRef"></canvas>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <span>Loading model...</span>
    </div>

    <div class="viewer-controls">
      <button @click="resetCamera" title="Reset View">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
      </button>
      <button @click="fitCameraToModel" title="Fit to View">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
        </svg>
      </button>
      <button @click="toggleWireframe" :class="{ active: wireframeMode }" title="Wireframe">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"/>
          <polyline points="2 17 12 22 22 17"/>
          <polyline points="2 12 12 17 22 12"/>
        </svg>
      </button>
      <button @click="toggleMaterials" :class="{ active: !showMaterials }" title="Toggle Materials">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 2a10 10 0 0 1 0 20"/>
        </svg>
      </button>
    </div>

    <div class="coordinate-display">
      <span>X: {{ cameraPos.x.toFixed(1) }}</span>
      <span>Y: {{ cameraPos.y.toFixed(1) }}</span>
      <span>Z: {{ cameraPos.z.toFixed(1) }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, reactive } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const props = defineProps({
  modelData: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['stats-update']);

const containerRef = ref(null);
const canvasRef = ref(null);
const wireframeMode = ref(false);
const showMaterials = ref(true);
const cameraPos = reactive({ x: 0, y: 0, z: 0 });

let scene, camera, renderer, controls;
let cadModel = null;
let ambientLight, directionalLight;

const initScene = () => {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a2e);

  const { clientWidth, clientHeight } = containerRef.value;
  camera = new THREE.PerspectiveCamera(45, clientWidth / clientHeight, 0.1, 10000);
  camera.position.set(300, 200, 200);

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance',
  });
  renderer.setSize(clientWidth, clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = true;
  controls.minDistance = 10;
  controls.maxDistance = 10000;
  controls.maxPolarAngle = Math.PI;

  setupLighting();
  setupGrid();

  animate();
};

const setupLighting = () => {
  ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
  scene.add(ambientLight);

  directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(100, 150, 100);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  directionalLight.shadow.camera.near = 0.5;
  directionalLight.shadow.camera.far = 500;
  directionalLight.shadow.camera.left = -200;
  directionalLight.shadow.camera.right = 200;
  directionalLight.shadow.camera.top = 200;
  directionalLight.shadow.camera.bottom = -200;
  scene.add(directionalLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
  fillLight.position.set(-100, 50, -100);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0x00d4ff, 0.2);
  rimLight.position.set(0, -100, 100);
  scene.add(rimLight);
};

const setupGrid = () => {
  const gridHelper = new THREE.GridHelper(1000, 50, 0x333366, 0x222244);
  gridHelper.position.y = -0.5;
  scene.add(gridHelper);

  const axesHelper = new THREE.AxesHelper(150);
  scene.add(axesHelper);
};

const loadModel = (data) => {
  if (cadModel) {
    scene.remove(cadModel);
    cadModel.traverse((child) => {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach((m) => m.dispose());
        } else {
          child.material.dispose();
        }
      }
    });
  }

  cadModel = new THREE.Group();
  const { vertices, triangles } = data.geometry;

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

  const indices = new Uint32Array(triangles.length * 3);
  triangles.forEach((t, i) => {
    indices[i * 3] = t.v1;
    indices[i * 3 + 1] = t.v2;
    indices[i * 3 + 2] = t.v3;
  });

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
  geometry.setIndex(new THREE.BufferAttribute(indices, 1));
  geometry.computeVertexNormals();

  let material;
  if (data.materials && data.materials.length > 0) {
    const matData = data.materials[0];
    const color = new THREE.Color(matData.color.r, matData.color.g, matData.color.b);
    material = new THREE.MeshStandardMaterial({
      color,
      metalness: matData.metalness || 0.5,
      roughness: matData.roughness || 0.5,
      side: THREE.DoubleSide,
    });
  } else {
    material = new THREE.MeshStandardMaterial({
      color: 0x888888,
      metalness: 0.8,
      roughness: 0.3,
      side: THREE.DoubleSide,
    });
  }

  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  cadModel.add(mesh);

  scene.add(cadModel);

  emit('stats-update', {
    parts: data.parts?.length || 1,
    vertices: vertices.length,
    triangles: triangles.length,
  });

  fitCameraToModel();
};

const resetCamera = () => {
  camera.position.set(300, 200, 200);
  controls.target.set(0, 0, 0);
  controls.update();
};

const fitCameraToModel = () => {
  if (!cadModel) return;
  const box = new THREE.Box3().setFromObject(cadModel);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());

  const maxDim = Math.max(size.x, size.y, size.z);
  const fov = (camera.fov * Math.PI) / 180;
  let cameraZ = Math.abs(maxDim / Math.tan(fov / 2)) * 1.5;

  camera.position.set(center.x + cameraZ * 0.5, center.y + cameraZ * 0.4, center.z + cameraZ * 0.8);
  controls.target.copy(center);
  controls.update();
};

const toggleWireframe = () => {
  wireframeMode.value = !wireframeMode.value;
  cadModel?.traverse((child) => {
    if (child.isMesh && child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach((m) => {
          m.wireframe = wireframeMode.value;
        });
      } else {
        child.material.wireframe = wireframeMode.value;
      }
    }
  });
};

const toggleMaterials = () => {
  showMaterials.value = !showMaterials.value;
  cadModel?.traverse((child) => {
    if (child.isMesh && child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach((m) => {
          m.wireframe = showMaterials.value ? wireframeMode.value : true;
          m.color.setHex(showMaterials.value ? 0x888888 : 0xffffff);
        });
      } else {
        child.material.wireframe = showMaterials.value ? wireframeMode.value : true;
        child.material.color.setHex(showMaterials.value ? 0x888888 : 0xffffff);
      }
    }
  });
};

const updateLighting = ({ ambient: ambientValue, directional: directionalValue }) => {
  if (ambientLight) ambientLight.intensity = ambientValue;
  if (directionalLight) directionalLight.intensity = directionalValue;
};

const updateBackground = (color) => {
  scene.background = new THREE.Color(color);
};

const animate = () => {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);

  cameraPos.x = camera.position.x;
  cameraPos.y = camera.position.y;
  cameraPos.z = camera.position.z;
};

const handleResize = () => {
  if (!containerRef.value) return;
  const { clientWidth, clientHeight } = containerRef.value;
  camera.aspect = clientWidth / clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(clientWidth, clientHeight);
};

watch(
  () => props.modelData,
  (newData) => {
    if (newData) {
      loadModel(newData);
    }
  },
  { immediate: true }
);

onMounted(() => {
  initScene();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  renderer?.dispose();
  controls?.dispose();
});

defineExpose({
  resetCamera,
  fitCameraToModel,
  toggleWireframe,
  toggleMaterials,
  updateLighting,
  updateBackground,
});
</script>

<style scoped>
.cad-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  background: #1a1a2e;
  overflow: hidden;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(26, 26, 46, 0.9);
  color: white;
  gap: 16px;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.viewer-controls {
  position: absolute;
  top: 16px;
  left: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 5;
}

.viewer-controls button {
  width: 40px;
  height: 40px;
  padding: 8px;
  background: rgba(26, 26, 46, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.viewer-controls button:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
}

.viewer-controls button.active {
  background: rgba(0, 212, 255, 0.3);
  border-color: #00d4ff;
  color: #00d4ff;
}

.viewer-controls button svg {
  width: 100%;
  height: 100%;
}

.coordinate-display {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  gap: 16px;
  padding: 8px 16px;
  background: rgba(26, 26, 46, 0.9);
  border-radius: 6px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.coordinate-display span {
  min-width: 60px;
}
</style>