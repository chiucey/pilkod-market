# CSS 粒子特效库参考

## 1. 基础粒子系统架构

```javascript
/**
 * 粒子特效基类
 */
class ParticleSystem {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.options = {
      particleCount: 200,
      particleSpeed: 2,
      particleColor: '#6366F1',
      particleOpacity: 0.8,
      particleSize: 3,
      ...options
    };
    this.animationId = null;
  }

  init() {
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.createParticles();
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  createParticles() {
    this.particles = [];
    for (let i = 0; i < this.options.particleCount; i++) {
      this.particles.push(this.createParticle());
    }
  }

  createParticle() {
    return {
      x: Math.random() * this.canvas.width,
      y: Math.random() * this.canvas.height,
      vx: (Math.random() - 0.5) * this.options.particleSpeed,
      vy: (Math.random() - 0.5) * this.options.particleSpeed,
      size: Math.random() * this.options.particleSize + 1,
      opacity: this.options.particleOpacity,
      hue: Math.random() * 60 + 220  // 蓝紫色调
    };
  }

  update() {
    // 子类实现
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    // 子类实现
  }

  animate() {
    this.update();
    this.draw();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  start() {
    this.init();
    this.animate();
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }
}
```

## 2. 特效类型实现

### 2.1 粒子汇聚特效 (Particle Gather)

```javascript
/**
 * 粒子汇聚成文字/图形
 */
class ParticleGatherEffect extends ParticleSystem {
  constructor(canvas, text, options = {}) {
    super(canvas, options);
    this.text = text;
    this.targetPositions = [];
    this.gathered = false;
    this.gatherProgress = 0;
  }

  // 获取文字像素点
  getTextPixels() {
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = this.canvas.width;
    tempCanvas.height = this.canvas.height;

    tempCtx.fillStyle = 'black';
    tempCtx.font = `${this.options.fontSize || 120}px Inter, sans-serif`;
    tempCtx.textAlign = 'center';
    tempCtx.textBaseline = 'middle';
    tempCtx.fillText(this.text, this.canvas.width / 2, this.canvas.height / 2);

    const imageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
    const pixels = [];

    for (let y = 0; y < imageData.height; y += 6) {
      for (let x = 0; x < imageData.width; x += 6) {
        const i = (y * imageData.width + x) * 4;
        if (imageData.data[i] < 128) {
          pixels.push({ x, y });
        }
      }
    }

    return pixels;
  }

  init() {
    super.resize();
    const textPixels = this.getTextPixels();

    this.particles = [];
    for (let i = 0; i < Math.min(this.options.particleCount, textPixels.length); i++) {
      const target = textPixels[i];
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        originX: Math.random() * this.canvas.width,
        originY: Math.random() * this.canvas.height,
        targetX: target.x,
        targetY: target.y,
        size: this.options.particleSize,
        currentX: 0,
        currentY: 0,
        color: this.options.particleColor
      });
    }

    this.targetPositions = textPixels;
  }

  update() {
    const speed = this.options.animationSpeed || 0.02;

    this.particles.forEach((p, i) => {
      if (this.gatherProgress < 1) {
        // 汇聚动画
        p.currentX += (p.targetX - p.currentX) * speed;
        p.currentY += (p.targetY - p.currentY) * speed;
      } else {
        // 散开动画
        p.currentX += (p.originX - p.currentX) * speed;
        p.currentY += (p.originY - p.currentY) * speed;
      }
    });

    this.gatherProgress += speed * 0.01;
    if (this.gatherProgress > 2) this.gatherProgress = 0;
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach(p => {
      this.ctx.beginPath();
      this.ctx.arc(p.currentX, p.currentY, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = p.color;
      this.ctx.globalAlpha = 0.8;
      this.ctx.fill();
    });
  }
}
```

### 2.2 粒子消散特效 (Particle Disperse)

```javascript
/**
 * 粒子消散/爆炸效果
 */
class ParticleDisperseEffect extends ParticleSystem {
  constructor(canvas, originX, originY, options = {}) {
    super(canvas, options);
    this.originX = originX || canvas.width / 2;
    this.originY = originY || canvas.height / 2;
    this.disperseFactor = 1;
  }

  createParticle() {
    const angle = Math.random() * Math.PI * 2;
    const speed = Math.random() * this.options.particleSpeed + 1;

    return {
      x: this.originX,
      y: this.originY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      size: Math.random() * this.options.particleSize + 1,
      opacity: 1,
      decay: Math.random() * 0.02 + 0.01,
      hue: Math.random() * 360
    };
  }

  update() {
    this.particles.forEach(p => {
      p.x += p.vx * this.disperseFactor;
      p.y += p.vy * this.disperseFactor;
      p.vy += 0.05;  // 轻微重力
      p.opacity -= p.decay;
      p.size *= 0.99;
    });

    // 移除消逝的粒子
    this.particles = this.particles.filter(p => p.opacity > 0 && p.size > 0.5);

    // 重新生成粒子
    if (this.particles.length < this.options.particleCount * 0.3) {
      for (let i = 0; i < 10; i++) {
        this.particles.push(this.createParticle());
      }
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach(p => {
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = `hsla(${p.hue}, 80%, 60%, ${p.opacity})`;
      this.ctx.fill();
    });
  }
}
```

### 2.3 流光特效 (Flow Light)

```javascript
/**
 * 流光/星光飘动效果
 */
class ParticleFlowEffect extends ParticleSystem {
  constructor(canvas, options = {}) {
    super(canvas, {
      ...options,
      particleCount: options.particleCount || 300
    });
    this.flowLines = [];
    this.initFlowLines();
  }

  initFlowLines() {
    for (let i = 0; i < 50; i++) {
      this.flowLines.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        length: Math.random() * 100 + 50,
        speed: Math.random() * 3 + 1,
        angle: Math.random() * Math.PI * 2,
        opacity: Math.random() * 0.5 + 0.2
      });
    }
  }

  update() {
    // 更新粒子
    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      // 边界检测
      if (p.x < 0) p.x = this.canvas.width;
      if (p.x > this.canvas.width) p.x = 0;
      if (p.y < 0) p.y = this.canvas.height;
      if (p.y > this.canvas.height) p.y = 0;
    });

    // 更新流光线条
    this.flowLines.forEach(line => {
      line.x += Math.cos(line.angle) * line.speed;
      line.y += Math.sin(line.angle) * line.speed;

      if (line.x < 0 || line.x > this.canvas.width ||
          line.y < 0 || line.y > this.canvas.height) {
        line.x = Math.random() * this.canvas.width;
        line.y = Math.random() * this.canvas.height;
        line.angle = Math.random() * Math.PI * 2;
      }
    });
  }

  draw() {
    this.ctx.fillStyle = 'rgba(15, 23, 42, 0.1)';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // 绘制流光线条
    this.flowLines.forEach(line => {
      const gradient = this.ctx.createLinearGradient(
        line.x, line.y,
        line.x + Math.cos(line.angle) * line.length,
        line.y + Math.sin(line.angle) * line.length
      );
      gradient.addColorStop(0, `rgba(99, 102, 241, 0)`);
      gradient.addColorStop(0.5, `rgba(99, 102, 241, ${line.opacity})`);
      gradient.addColorStop(1, `rgba(139, 92, 246, 0)`);

      this.ctx.beginPath();
      this.ctx.moveTo(line.x, line.y);
      this.ctx.lineTo(
        line.x + Math.cos(line.angle) * line.length,
        line.y + Math.sin(line.angle) * line.length
      );
      this.ctx.strokeStyle = gradient;
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
    });

    // 绘制粒子
    this.particles.forEach(p => {
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
      this.ctx.fill();
    });
  }
}
```

### 2.4 漂浮上升特效 (Float Up)

```javascript
/**
 * 粒子漂浮上升效果
 */
class ParticleFloatEffect extends ParticleSystem {
  constructor(canvas, options = {}) {
    super(canvas, {
      ...options,
      particleCount: options.particleCount || 150
    });
    this.floatHeight = options.floatHeight || 200;
    this.cycleDuration = options.cycleDuration || 8;
  }

  createParticle() {
    return {
      x: Math.random() * this.canvas.width,
      y: this.canvas.height + Math.random() * 100,
      baseX: 0,
      size: Math.random() * 4 + 2,
      speedY: Math.random() * 1 + 0.5,
      amplitude: Math.random() * 50 + 20,
      frequency: Math.random() * 0.02 + 0.01,
      phase: Math.random() * Math.PI * 2,
      opacity: Math.random() * 0.5 + 0.3,
      color: this.options.particleColor || '#6366F1'
    };
  }

  init() {
    super.resize();
    this.particles = [];
    for (let i = 0; i < this.options.particleCount; i++) {
      const p = this.createParticle();
      p.baseX = p.x;
      this.particles.push(p);
    }
  }

  update() {
    const time = Date.now() * 0.001;

    this.particles.forEach(p => {
      p.y -= p.speedY;
      p.x = p.baseX + Math.sin(time * p.frequency * 10 + p.phase) * p.amplitude;
      p.opacity = 0.3 + Math.sin(time * 2 + p.phase) * 0.2;

      // 重置到屏幕底部
      if (p.y < -50) {
        p.y = this.canvas.height + 50;
        p.baseX = Math.random() * this.canvas.width;
        p.x = p.baseX;
      }
    });
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach(p => {
      // 绘制发光效果
      const gradient = this.ctx.createRadialGradient(
        p.x, p.y, 0,
        p.x, p.y, p.size * 3
      );
      gradient.addColorStop(0, `rgba(99, 102, 241, ${p.opacity})`);
      gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
      this.ctx.fillStyle = gradient;
      this.ctx.fill();

      // 核心粒子
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
      this.ctx.fill();
    });
  }
}
```

### 2.5 像素化扫描特效 (Pixelate Scan)

```javascript
/**
 * 像素化扫描效果
 */
class ParticlePixelEffect extends ParticleSystem {
  constructor(canvas, options = {}) {
    super(canvas, options);
    this.pixelSize = options.pixelSize || 8;
    this.scanLineY = 0;
    this.scanSpeed = options.scanSpeed || 5;
    this.text = options.text || '';
    this.textPixels = [];
  }

  getTextPixels() {
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = this.canvas.width;
    tempCanvas.height = this.canvas.height;

    tempCtx.fillStyle = 'black';
    tempCtx.font = `bold ${this.options.fontSize || 100}px Inter`;
    tempCtx.textAlign = 'center';
    tempCtx.textBaseline = 'middle';
    tempCtx.fillText(this.text, this.canvas.width / 2, this.canvas.height / 2);

    const imageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
    const pixels = [];

    for (let y = 0; y < imageData.height; y += this.pixelSize) {
      for (let x = 0; x < imageData.width; x += this.pixelSize) {
        const i = (y * imageData.width + x) * 4;
        if (imageData.data[i] < 128) {
          pixels.push({ x, y, revealed: false });
        }
      }
    }

    return pixels;
  }

  init() {
    super.resize();
    this.textPixels = this.getTextPixels();
    this.scanLineY = 0;
  }

  update() {
    this.scanLineY += this.scanSpeed;

    this.textPixels.forEach(p => {
      if (p.y < this.scanLineY) {
        p.revealed = true;
      }
    });
  }

  draw() {
    this.ctx.fillStyle = '#0F172A';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // 背景粒子
    for (let i = 0; i < 50; i++) {
      const x = Math.random() * this.canvas.width;
      const y = Math.random() * this.canvas.height;
      this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
      this.ctx.fillRect(x, y, 2, 2);
    }

    // 文字像素
    this.textPixels.forEach(p => {
      if (p.revealed) {
        const brightness = Math.random() * 50 + 50;
        this.ctx.fillStyle = `rgb(${brightness}, ${brightness + 20}, ${brightness + 100})`;
      } else {
        this.ctx.fillStyle = 'rgba(99, 102, 241, 0.1)';
      }
      this.ctx.fillRect(p.x, p.y, this.pixelSize, this.pixelSize);
    });

    // 扫描线
    this.ctx.fillStyle = 'rgba(139, 92, 246, 0.5)';
    this.ctx.fillRect(0, this.scanLineY - 2, this.canvas.width, 4);
  }
}
```

### 2.6 发光呼吸特效 (Glow Breathe)

```javascript
/**
 * 发光呼吸效果
 */
class ParticleGlowEffect extends ParticleSystem {
  constructor(canvas, options = {}) {
    super(canvas, {
      ...options,
      particleCount: options.particleCount || 100
    });
    this.glowRadius = options.glowRadius || 50;
    this.breathePhase = 0;
    this.breathSpeed = options.breathSpeed || 0.02;
    this.centerX = canvas.width / 2;
    this.centerY = canvas.height / 2;
  }

  createParticle() {
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * this.glowRadius;

    return {
      angle,
      distance,
      baseAngle: angle,
      baseDistance: distance,
      size: Math.random() * 3 + 1,
      phase: Math.random() * Math.PI * 2,
      speed: Math.random() * 0.5 + 0.5
    };
  }

  update() {
    this.breathePhase += this.breathSpeed;
    const breatheFactor = (Math.sin(this.breathePhase) + 1) / 2;

    this.particles.forEach(p => {
      p.angle = p.baseAngle + Math.sin(this.breathePhase * p.speed + p.phase) * 0.1;
      p.currentDistance = p.baseDistance * (0.5 + breatheFactor * 0.5);
    });
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const breatheFactor = (Math.sin(this.breathePhase) + 1) / 2;

    // 中心光晕
    const centerGradient = this.ctx.createRadialGradient(
      this.centerX, this.centerY, 0,
      this.centerX, this.centerY, this.glowRadius * 2
    );
    centerGradient.addColorStop(0, `rgba(99, 102, 241, ${0.3 + breatheFactor * 0.3})`);
    centerGradient.addColorStop(0.5, `rgba(139, 92, 246, ${0.1 + breatheFactor * 0.1})`);
    centerGradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

    this.ctx.beginPath();
    this.ctx.arc(this.centerX, this.centerY, this.glowRadius * 2, 0, Math.PI * 2);
    this.ctx.fillStyle = centerGradient;
    this.ctx.fill();

    // 粒子
    this.particles.forEach(p => {
      const x = this.centerX + Math.cos(p.angle) * p.currentDistance;
      const y = this.centerY + Math.sin(p.angle) * p.currentDistance;

      const particleGradient = this.ctx.createRadialGradient(x, y, 0, x, y, p.size * 2);
      particleGradient.addColorStop(0, `rgba(255, 255, 255, ${0.8 + breatheFactor * 0.2})`);
      particleGradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

      this.ctx.beginPath();
      this.ctx.arc(x, y, p.size * 2, 0, Math.PI * 2);
      this.ctx.fillStyle = particleGradient;
      this.ctx.fill();
    });
  }
}
```

## 3. CSS 粒子特效（无 Canvas）

### 3.1 背景粒子 CSS 动画

```css
/* 背景粒子容器 */
.particle-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: -1;
}

/* 单个粒子 */
.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(99, 102, 241, 0.6);
  border-radius: 50%;
  animation: float-up 8s infinite ease-in-out;
}

.particle:nth-child(1) { left: 10%; animation-delay: 0s; animation-duration: 8s; }
.particle:nth-child(2) { left: 20%; animation-delay: 1s; animation-duration: 10s; }
.particle:nth-child(3) { left: 30%; animation-delay: 2s; animation-duration: 7s; }
.particle:nth-child(4) { left: 40%; animation-delay: 0.5s; animation-duration: 9s; }
.particle:nth-child(5) { left: 50%; animation-delay: 1.5s; animation-duration: 11s; }
.particle:nth-child(6) { left: 60%; animation-delay: 2.5s; animation-duration: 8s; }
.particle:nth-child(7) { left: 70%; animation-delay: 0.8s; animation-duration: 10s; }
.particle:nth-child(8) { left: 80%; animation-delay: 1.8s; animation-duration: 9s; }
.particle:nth-child(9) { left: 90%; animation-delay: 3s; animation-duration: 7s; }
.particle:nth-child(10) { left: 95%; animation-delay: 2.2s; animation-duration: 12s; }

@keyframes float-up {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(1);
    opacity: 0;
  }
}

/* 闪烁粒子 */
.particle-sparkle {
  animation: sparkle 2s infinite ease-in-out;
}

@keyframes sparkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.5); }
}
```

### 3.2 文字粒子特效 CSS

```css
/* 文字粒子效果 - 鼠标悬停 */
.text-particle {
  position: relative;
  display: inline-block;
}

.text-particle::before {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  color: transparent;
  background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899);
  -webkit-background-clip: text;
  background-clip: text;
  opacity: 0;
  transition: opacity 0.3s;
}

.text-particle:hover::before {
  opacity: 1;
  animation: particle-shimmer 1s linear infinite;
}

@keyframes particle-shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
```

### 3.3 流光边框特效

```css
/* 流光边框 */
.glow-border {
  position: relative;
  padding: 2px;
  background: linear-gradient(#0F172A, #0F172A) padding-box,
              linear-gradient(var(--angle, 0deg), #6366F1, #8B5CF6, #EC4899, #6366F1) border-box;
  border: 2px solid transparent;
  background-size: 100% 100%, 300% 100%;
  animation: glow-rotate 4s linear infinite;
}

@keyframes glow-rotate {
  to { --angle: 360deg; }
}

@property --angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}
```

## 4. 特效参数对照表

| 特效名称 | 核心参数 | 默认值 | 调节范围 |
|----------|----------|--------|----------|
| Gather | particleCount | 300 | 100-1000 |
| Gather | fontSize | 120px | 48-200 |
| Gather | animationSpeed | 0.02 | 0.01-0.05 |
| Disperse | particleCount | 200 | 50-500 |
| Disperse | particleSpeed | 3 | 1-10 |
| Disperse | decay | 0.015 | 0.005-0.03 |
| Flow | particleCount | 300 | 100-500 |
| Flow | lineLength | 100 | 50-200 |
| Float | floatHeight | 200 | 100-500 |
| Float | cycleDuration | 8s | 4-15s |
| Pixel | pixelSize | 8 | 4-32 |
| Pixel | scanSpeed | 5 | 1-10 |
| Glow | glowRadius | 50 | 20-100 |
| Glow | breathSpeed | 0.02 | 0.01-0.05 |

## 5. 性能优化建议

```javascript
// 1. 使用 requestAnimationFrame
// 2. 限制粒子数量
const MAX_PARTICLES = 500;

// 3. 使用对象池避免 GC
class ParticlePool {
  constructor(size) {
    this.pool = new Array(size);
    this.size = size;
    this.init();
  }

  init() {
    for (let i = 0; i < this.size; i++) {
      this.pool[i] = { active: false };
    }
  }

  get() {
    for (let p of this.pool) {
      if (!p.active) {
        p.active = true;
        return p;
      }
    }
    return null;
  }

  release(p) {
    p.active = false;
  }
}

// 4. 离屏 Canvas 预渲染
const offscreen = document.createElement('canvas');
offscreen.width = 100;
offscreen.height = 100;
const offCtx = offscreen.getContext('2d');
// 预渲染粒子图像
```

## 6. 浏览器兼容性

```javascript
// 特性检测
const supportsCanvas = !!document.createElement('canvas').getContext;
const supportsWebGL = (() => {
  try {
    return !!document.createElement('canvas').getContext('webgl');
  } catch(e) {
    return false;
  }
})();

// 回退方案：纯 CSS 动画
if (!supportsCanvas) {
  document.body.classList.add('fallback-mode');
}
```
