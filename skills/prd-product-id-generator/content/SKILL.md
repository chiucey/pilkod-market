---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30440220482035bf65f0ed812fc33f13fdd94a30d581f531467d65293a35bd87a985afcf02201dd7874de00143910bc475150a28afc1b5c645b1f09cbb802bfdd041934c993a
    ReservedCode2: 304502201fccfb478760e2877de892a52633af7fb530c153f60ba274f3152431d551cbb5022100ae917f19593899f8f3766a1e52a1ea1f6eb8d0529a3fbaeb7d52d86d11759957
description: Used when users request product ID (industrial design) image generation, including 6-view technical drawings (front, back, left, right, top, bottom), perspective views, and scene renderings based on PRD documents.
name: prd-product-id-generator
---

# PRD to Product ID (Industrial Design) Generator

Generate professional Product ID (Industrial Design) images from Product Requirements Documents, including technical 6-view orthographic projections and lifestyle scene renderings.

## Core Workflow

### 1. PRD Analysis

**Input**: Product Requirements Document or product description

**Extract for ID Generation**:
- Product type and category
- Physical dimensions and form factor
- Color schemes and materials
- Key UI elements and displays
- Target users and usage scenarios
- Brand positioning

**Output**:
```
## ID Design Brief

| Attribute | Value |
|-----------|-------|
| Product Type | [Category] |
| Form Factor | [Shape description] |
| Dimensions | [L x W x H] |
| Color Palette | [Primary, Secondary, Accent] |
| Material | [Primary material] |
| Target Users | [User personas] |
| Positioning | [Premium/Mid-range/Entry] |
```

### 2. 6-View Technical Drawings

Generate orthographic projections following standard ID conventions:

#### 2.1 Required Views

| View | Description | Key Elements |
|------|-------------|---------------|
| Front View | Primary facing | Main UI, brand logo position |
| Back View | Rear panel | Battery cover, ports, connectors |
| Left View | Left profile | Thickness, button placement |
| Right View | Right profile | Mirrored elements, slots |
| Top View | Plan view | Overall shape, sensors |
| Bottom View | Underside | Vents, feet, serial number |

#### 2.2 View Specifications

```
6-View Layout (Standard Arrangement):

        [Top View]
[Left] [Front] [Right] [Back]
        [Bottom]

Each view must include:
- Dimension lines with measurements
- Center lines
- View alignment indicators
- Scale indicator
```

#### 2.3 Technical Annotations

For each view, include:
- Critical dimensions (L x W x H)
- Important tolerances (+/- 0.1mm)
- Material callouts
- Surface finish notes
- Branding/logo positions

### 3. Perspective Views

Generate professional 3D perspective renders:

| View Type | Angle | Use Case |
|-----------|-------|----------|
| Isometric | 30-degree | General product showcase |
| Front-Perspective | 15-degree | Hero shots |
| Detail Views | Various | Component details |
| Exploded View | N/A | Internal components |

### 4. Scene Renderings

Generate lifestyle context images:

| Scene | Description | Mood |
|-------|-------------|------|
| Usage Scene | Product in actual use | Natural, relatable |
| Environment | Product in setting | Aspirational, lifestyle |
| Comparison | Size reference | Context, scale |
| Detail Close-up | Material/texture | Premium feel |
| Packaging | Unboxing experience | Presentation |

### 5. Output Deliverables

Generate complete ID documentation package:

1. **6-View Technical Drawing**
   - Front, Back, Left, Right, Top, Bottom
   - With dimensions and annotations
   - White background, technical style

2. **Perspective Renders**
   - Primary hero shot
   - Multiple angles
   - Material/color variants

3. **Scene Renderings**
   - Lifestyle contexts
   - Usage scenarios
   - Environment settings

4. **Detail Shots**
   - Key features
   - Material textures
   - Surface finishes

## Image Generation Prompts

### 6-View Technical Drawing Prompts

```
[Template]
Professional industrial design 6-view orthographic projection of [product type],
clean white background, technical drawing style, precise line work, dimension
annotations, front view, back view, left side view, right side view, top view,
bottom view, exact 6-view layout following engineering drawing standards,
center lines, dimension lines with measurements in millimeters, [dimensions],
[material] material finish, professional product ID documentation, blueprint
aesthetic, high detail, photorealistic CAD rendering style
```

### Perspective Render Prompts

```
[Template]
Professional 3D product render of [product type], isometric angle, studio
lighting, clean background, [color] color scheme, [material] material texture,
product design visualization, clean modern aesthetic, [form factor description],
soft shadows, high-end product photography style, commercial render,
photorealistic, detailed surface finish, professional lighting
```

### Scene Rendering Prompts

```
[Template]
[product type] product in [scene description], lifestyle photography,
natural lighting, [environment], modern [setting], realistic usage scenario,
the product is the hero element, soft focus background, aspirational mood,
professional product photography, editorial quality, [target audience] context,
warm natural tones, lifestyle brand aesthetic
```

## Quality Standards

- **Technical Accuracy**: Dimensions consistent across all views
- **View Alignment**: All 6 views properly aligned and proportional
- **Professional Style**: Clean, minimal, suitable for manufacturing
- **Scene Authenticity**: Lifestyle images feel natural and relatable
- **Brand Alignment**: Matches target market positioning

## Templates

See `references/product-id-spec.md` for detailed ID specifications and view requirements.
