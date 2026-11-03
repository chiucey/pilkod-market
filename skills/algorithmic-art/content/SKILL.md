---
name: algorithmic-art
description: Create algorithmic art and generative visual designs using mathematical formulas, algorithms, and code. Use when users ask to create generative art, algorithmic graphics, mathematical visualizations, procedural patterns, code-generated images, or visual designs based on algorithms.
---

# Algorithmic Art Skill

Create stunning visual art using mathematical algorithms, formulas, and generative code.

## Core Concepts

### Mathematical Foundations

**Common Algorithms:**
- Fractals (Mandelbrot, Julia, Sierpinski)
- L-systems (plants, trees)
- Cellular automata
- Perlin noise
- Voronoi diagrams
- Fourier transforms

### Visual Techniques

**Color Generation:**
- Gradient mapping
- Color palettes (complementary, analogous, triadic)
- HSL color manipulation
- Color theory applications

**Pattern Generation:**
- Tessellations
- Geometric transformations
- Recursive patterns
- Symmetry operations

## Implementation Approaches

### Python (Recommended)

```python
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Create algorithmic pattern
def create_fractal():
    x = np.linspace(-2, 1, 1000)
    y = np.linspace(-1.5, 1.5, 1000)
    # Mandelbrot calculation
    # ...
    plt.imsave('fractal.png', image)
```

### JavaScript/Canvas

```javascript
// Canvas-based algorithmic art
const ctx = canvas.getContext('2d');
// Fractals, noise, particles
```

### SVG

```xml
<svg viewBox="0 0 100 100">
  <!-- Geometric patterns -->
</svg>
```

## Animation Concepts

### Time-Based Animation
- Frame-by-frame rendering
- Interpolation techniques
- Easing functions

### Parameter Animation
- Morphing between states
- Color cycling
- Scale and rotation transforms

## Best Practices

1. **Start Simple**: Begin with basic shapes and patterns
2. **Iterate**: Build complexity gradually
3. **Export**: Generate high-resolution outputs
4. **Document**: Note algorithm parameters for reproducibility

## Output Formats

- PNG/JPEG for static images
- SVG for vector graphics
- MP4/GIF for animations
- PDF for print-ready artwork
