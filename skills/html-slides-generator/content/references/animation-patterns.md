# Animation Patterns Reference

Use this reference when generating presentations. Match animations to the intended feeling.

## Effect-to-Feeling Guide

| Feeling | Animations | Visual Cues |
|---------|------------|-------------|
| **Dramatic / Cinematic** | Slow fade-ins (1-1.5s), large scale transitions (0.9 to 1), parallax scrolling | Dark backgrounds, spotlight effects, full-bleed images |
| **Techy / Futuristic** | Neon glow (box-shadow), glitch/scramble text, grid reveals | Particle systems (canvas), grid patterns, monospace accents, cyan/magenta/electric blue |
| **Playful / Friendly** | Bouncy easing (spring physics), floating/bobbing | Rounded corners, pastel/bright colors, hand-drawn elements |
| **Professional / Corporate** | Subtle fast animations (200-300ms), clean slides | Navy/slate/charcoal, precise spacing, data visualization focus |
| **Calm / Minimal** | Very slow subtle motion, gentle fades | High whitespace, muted palette, serif typography, generous padding |
| **Editorial / Magazine** | Staggered text reveals, image-text interplay | Strong type hierarchy, pull quotes, grid-breaking layouts, serif headlines + sans body |

## Entrance Animations

```css
/* Fade + Slide Up (most versatile) */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s var(--ease-out-expo),
              transform 0.6s var(--ease-out-expo);
}
.visible .reveal {
  opacity: 1;
  transform: translateY(0);
}

/* Scale In */
.reveal-scale {
  opacity: 0;
  transform: scale(0.9);
  transition: opacity 0.6s, transform 0.6s var(--ease-out-expo);
}

/* Slide from Left */
.reveal-left {
  opacity: 0;
  transform: translateX(-50px);
  transition: opacity 0.6s, transform 0.6s var(--ease-out-expo);
}

/* Blur In */
.reveal-blur {
  opacity: 0;
  filter: blur(10px);
  transition: opacity 0.8s, filter 0.8s var(--ease-out-expo);
}

/* Staggered Delays for List Items */
.reveal-stagger > * {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.reveal-stagger.visible > *:nth-child(1) { transition-delay: 0.1s; }
.reveal-stagger.visible > *:nth-child(2) { transition-delay: 0.2s; }
.reveal-stagger.visible > *:nth-child(3) { transition-delay: 0.3s; }
.reveal-stagger.visible > *:nth-child(4) { transition-delay: 0.4s; }
.reveal-stagger.visible > *:nth-child(5) { transition-delay: 0.5s; }
.reveal-stagger.visible > *:nth-child(6) { transition-delay: 0.6s; }
.reveal-stagger.visible > * {
  opacity: 1;
  transform: translateY(0);
}
```

## Background Effects

```css
/* Gradient Mesh — layered radial gradients for depth */
.gradient-bg {
  background:
    radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
    var(--bg-primary);
}

/* Noise Texture — inline SVG for grain */
.noise-bg {
  background-image: url("data:image/svg+xml,..."); /* Inline SVG noise */
}

/* Grid Pattern — subtle structural lines */
.grid-bg {
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* Animated Gradient */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
.animated-gradient {
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}
```

## Particle Effects (Canvas)

```javascript
class ParticleSystem {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.options = {
      count: options.count || 50,
      color: options.color || '#00ffcc',
      speed: options.speed || 1,
      size: options.size || 2,
      ...options
    };
    this.init();
  }

  init() {
    for (let i = 0; i < this.options.count; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * this.options.speed,
        vy: (Math.random() - 0.5) * this.options.speed,
        size: Math.random() * this.options.size
      });
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      // Wrap around edges
      if (p.x < 0) p.x = this.canvas.width;
      if (p.x > this.canvas.width) p.x = 0;
      if (p.y < 0) p.y = this.canvas.height;
      if (p.y > this.canvas.height) p.y = 0;

      // Draw particle
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = this.options.color;
      this.ctx.fill();
    });

    requestAnimationFrame(() => this.animate());
  }
}
```

## Interactive Effects

```javascript
/* 3D Tilt on Hover — adds depth to cards/panels */
class TiltEffect {
  constructor(element) {
    this.element = element;
    this.element.style.transformStyle = 'preserve-3d';
    this.element.style.perspective = '1000px';
    this.element.addEventListener('mousemove', (e) => {
      const rect = this.element.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      this.element.style.transform = `rotateY(${x * 10}deg) rotateX(${-y * 10}deg)`;
    });
    this.element.addEventListener('mouseleave', () => {
      this.element.style.transform = 'rotateY(0) rotateX(0)';
    });
  }
}

/* Magnetic Button Effect */
class MagneticButton {
  constructor(button, strength = 0.3) {
    this.button = button;
    this.strength = strength;

    this.button.addEventListener('mousemove', (e) => {
      const rect = this.button.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      this.button.style.transform = `translate(${x * this.strength}px, ${y * this.strength}px)`;
    });

    this.button.addEventListener('mouseleave', () => {
      this.button.style.transform = 'translate(0, 0)';
    });
  }
}
```

## Neon/Glow Effects

```css
/* Neon Glow Text */
.neon-text {
  text-shadow:
    0 0 5px #fff,
    0 0 10px #fff,
    0 0 20px #00ffcc,
    0 0 40px #00ffcc;
}

/* Neon Glow Box */
.neon-box {
  box-shadow:
    0 0 5px #00ffcc,
    0 0 10px #00ffcc,
    0 0 20px #00ffcc,
    inset 0 0 5px rgba(0, 255, 204, 0.3);
  border: 2px solid #00ffcc;
}

/* Pulsing Glow Animation */
@keyframes neonPulse {
  0%, 100% {
    box-shadow: 0 0 5px #00ffcc, 0 0 10px #00ffcc;
  }
  50% {
    box-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc, 0 0 30px #00ffcc;
  }
}
.pulsing-glow {
  animation: neonPulse 2s ease-in-out infinite;
}
```

## Loading Animations

```css
/* Typing Cursor */
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
.typing-cursor::after {
  content: '|';
  animation: blink 1s infinite;
}

/* Skeleton Loading */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Fonts not loading | Check Fontshare/Google Fonts URL; ensure font names match in CSS |
| Animations not triggering | Verify Intersection Observer is running; check `.visible` class is being added |
| Scroll snap not working | Ensure `scroll-snap-type: y mandatory` on html; each slide needs `scroll-snap-align: start` |
| Mobile issues | Disable heavy effects at 768px breakpoint; test touch events; reduce particle count |
| Performance issues | Use `will-change` sparingly; prefer `transform`/`opacity` animations; throttle scroll handlers |
