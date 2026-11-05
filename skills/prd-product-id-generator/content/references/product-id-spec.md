---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220024bcf45b79011f4f3864bf80b9f0614af92c10b07b92d04ab703a3b59806059022100f74dd12d40583ab6f51ad6d65dcae1cdae6f8f22d27c8b0c137a70bd2414a254
    ReservedCode2: 3046022100e539418c2c8af6b73b93d086466710ba07685658d6dc07de6af8bae70741958a022100a33d85a9af0f977a6a64701ffb1397924e83875e302bae0b6ef6e08b5a5b3f2f
---

# Product ID (Industrial Design) Specification Guide

## 6-View Technical Drawing Standards

### Standard View Arrangement

```
    +-------+
    |  TOP  |
    +-------+
+-----+-----+-----+-----+
|LEFT |FRONT|RIGHT| BACK|
+-----+-----+-----+-----+
    +-------+
    |BOTTOM |
    +-------+
```

### View Definitions

| View | Orientation | Primary Focus |
|------|------------|---------------|
| Front | 0 degrees | Main user interface, primary controls |
| Back | 180 degrees | Secondary features, connections |
| Left | 90 degrees left | Thickness, side controls |
| Right | 90 degrees right | Mirrored features |
| Top | 90 degrees up | Plan view, sensors, display |
| Bottom | 90 degrees down | Mounting, ventilation |

### Required Annotations

```
For each view:
1. Overall dimensions (L x W x H)
2. Critical feature dimensions
3. Material callout
4. Surface finish specification
5. Tolerance notes
6. View label
```

### Dimension Standards

| Dimension Type | Format | Example |
|---------------|--------|---------|
| Overall | L x W x H | 120 x 60 x 25 mm |
| Feature | Single value | R2 (radius) |
| Tolerance | +/- value | +/- 0.1 mm |
| Angle | Degree | 45 degrees |

---

## Product Category Specifications

### Consumer Electronics

**Typical Products**: Smartphones, tablets, wearables, earbuds, speakers

| Element | Common Specs |
|---------|-------------|
| Materials | Aluminum, glass, plastic (PC/ABS) |
| Finish | Matte, glossy, soft-touch |
| Colors | 2-4 options typical |
| Display | 1-6 inch screens |
| Buttons | 1-5 physical buttons |

**View Focus**:
- Front view emphasis on screen/UI
- Detail on button placement
- Connection ports location
- Camera module details

### IoT Devices

**Typical Products**: Smart home hubs, sensors, cameras, locks

| Element | Common Specs |
|---------|-------------|
| Materials | Plastic, metal accents |
| Finish | Matte, rugged optional |
| Colors | 1-3 options |
| Indicators | LED status lights |
| Mounting | Wall mount, table stand |

**View Focus**:
- Status indicator placement
- Mounting interface details
- Sensor locations
- Environmental sealing

### Home Appliances

**Typical Products**: Kitchen gadgets, cleaning devices, air care

| Element | Common Specs |
|---------|-------------|
| Materials | Stainless, plastic, glass |
| Finish | Brushed, polished, coated |
| Colors | Neutral + accent |
| Safety | Certifications marked |
| Ergonomics | Handle design |

**View Focus**:
- Ergonomic curves
- Control panel layout
- Safety certifications
- Power connection

### Wearables

**Typical Products**: Smartwatches, fitness trackers, AR glasses

| Element | Common Specs |
|---------|-------------|
| Materials | Silicone, metal, glass |
| Finish | Anti-fingerprint coating |
| Colors | 3-8 options |
| Weight | < 50g typical |
| Display | 0.5-2 inch |

**View Focus**:
- Band attachment mechanism
- Sensor locations (rear)
- Button ergonomics
- Comfort curves

---

## Scene Rendering Guidelines

### Scene Types

| Scene | Description | Technical Setup |
|-------|-------------|----------------|
| Hero Shot | Primary product showcase | Studio, dramatic lighting |
| Lifestyle | Product in use | Natural environment, warm tones |
| Comparison | Scale reference | Everyday objects nearby |
| Detail | Texture/material | Macro, shallow depth |
| Unboxing | Packaging experience | Clean, anticipatory |

### Lighting Recommendations

| Scene Type | Lighting Style |
|-----------|---------------|
| Technical | Cool white, even, shadowless |
| Lifestyle | Warm natural, window light |
| Product | Soft box, diffused |
| Detail | Rim light, accent lighting |

### Color Grading

| Mood | Color Temperature | Saturation |
|------|------------------|------------|
| Premium | Cool (5500K+) | Neutral |
| Warm | Warm (3500K) | Rich |
| Modern | Neutral | Slightly desaturated |
| Playful | Variable | Vibrant |

---

## Image Output Specifications

### Resolution Requirements

| Use Case | Minimum Resolution | Recommended |
|----------|-------------------|-------------|
| Print | 300 DPI | 600 DPI |
| Digital | 72 DPI | 150 DPI |
| Social Media | 72 DPI | 1080px min |
| Presentation | 72 DPI | 1920px min |

### File Formats

| Format | Use Case | Transparency |
|--------|----------|--------------|
| PNG | General use | Supported |
| JPEG | Photos/scenes | Not supported |
| SVG | Technical drawings | Supported |
| PSD | Further editing | Supported |

### Naming Convention

```
[Product]-[View]-[Variant].[ext]

Examples:
SmartBottle-Front-White.png
SmartBottle-6View-Technical.png
SmartBottle-Scene-Kitchen.png
```

---

## Prompt Engineering Templates

### 6-View Drawing Prompt

```
Professional industrial design 6-view orthographic projection of a [PRODUCT TYPE],
white background, technical blueprint style, precise line art, dimension annotations
in millimeters, orthographic projection following engineering drawing standards:

- FRONT VIEW: Main interface, primary controls, [KEY ELEMENTS]
- BACK VIEW: Rear panel, [FEATURES], connection ports
- LEFT VIEW: Side profile, thickness, [DETAILS]
- RIGHT VIEW: Opposite side, [FEATURES]
- TOP VIEW: Plan view, [ELEMENTS]
- BOTTOM VIEW: Underside, [DETAILS]

Dimensions: [L] x [W] x [H] mm
Material: [MATERIAL TYPE]
Color: [PRIMARY COLOR]
Surface finish: [FINISH TYPE]

Clean white background, professional ID documentation, CAD rendering aesthetic,
high contrast lines, center lines included, scale indicator, view labels,
photorealistic technical illustration style
```

### Perspective Render Prompt

```
Professional 3D product visualization of [PRODUCT TYPE],
[ANGLE] angle view, modern studio lighting, [BACKGROUND],
[MATERIAL] material with [FINISH] finish,

Product details:
- [DIMENSIONS]
- [COLOR] color scheme
- [MATERIAL TEXTURE]
- [KEY FEATURES]

Soft studio shadows, clean composition, product design render,
[STYLE: modern/minimalist/premium],
high-end product photography aesthetic, commercial quality,
photorealistic, 4K detail, professional lighting setup
```

### Scene Render Prompt

```
[PRODUCT TYPE] product photography, [SCENE TYPE] scene,

Setting: [DETAILED ENVIRONMENT DESCRIPTION]
Lighting: [NATURAL/WARM/SOFT] lighting, [LIGHT SOURCE]
Mood: [MOOD DESCRIPTION], aspirational lifestyle

Product is the hero element, [PRODUCT POSITIONING],
[BACKGROUND DETAILS], realistic context,
professional editorial photography style,
[COLOR GRADING: WARM/COOL/MUTED],
high-end brand aesthetic, [TARGET AUDIENCE] appeal
```

---

## Quality Checklist

### Technical Drawing
- [ ] All 6 views present
- [ ] Dimensions accurate and consistent
- [ ] Views properly aligned
- [ ] Material callouts included
- [ ] Scale indicator present
- [ ] Clean white background

### Perspective Render
- [ ] Correct viewing angle
- [ ] Realistic lighting
- [ ] Accurate proportions
- [ ] Material textures visible
- [ ] Clean composition
- [ ] Appropriate background

### Scene Render
- [ ] Natural setting
- [ ] Product is hero
- [ ] Appropriate mood
- [ ] Quality lighting
- [ ] Authentic context
- [ ] Target audience relevant
