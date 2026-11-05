---
name: ecommerce-image-generator
description: E-commerce product image generation expert. Use when users request generating product images, main images, detail pages, banners, infographics, A+ content images, and other visuals for platforms like Amazon, Taobao, Tmall, and Pinduoduo. Supports white background images, lifestyle scenes, detail page banners, product comparison charts, and various e-commerce image types.
---

# E-commerce Image Generator

Generate professional product images for major e-commerce platforms including Amazon, Taobao, Tmall, and Pinduoduo.

## Supported Platforms & Image Types

### Amazon
- **Main Images**: White background, 1000x1000px minimum
- **LifeStyle Images**: In-context lifestyle shots
- **Infographic Images**: Feature highlights with icons/text
- **A+ Content Images**: Enhanced brand content banners

### Taobao / Tmall
- **Main Images**: 800x800px or larger, white/light background
- **Detail Page Banners**: 750px width, variable height
- **Scene Images**: Product in realistic settings
- **Comparison Charts**: Product comparison visuals

### Pinduoduo
- **Main Images**: 800x800px, high contrast, promotional focus
- **Carousel Images**: Multiple product angles
- **Scene Images**: Value proposition imagery

## Available Tools

### Primary Tool
- **image_synthesize**: Generate images from text prompts with optional reference images

### Image Generation Parameters

| Parameter | Description | Options |
|-----------|-------------|---------|
| aspect_ratio | Image aspect ratio | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| resolution | Output resolution | 1K, 2K, 4K |
| input_files | Reference images for editing/synthesis | PNG, JPG files |

## Image Specifications

### Amazon Specifications

| Image Type | Size | Background | Notes |
|------------|------|------------|-------|
| Main Image | 1000x1000px min | Pure white (#FFFFFF) | No text, logos, or props |
| Infographic | 1000x1000px min | Light/white | Product features with icons |
| Lifestyle | 1000x1000px min | Natural settings | Show product in use |
| A+ Banner | 3000x600px | Varies | Full-width enhanced content |

### Taobao/Tmall Specifications

| Image Type | Size | Notes |
|------------|------|-------|
| Main Image | 800x800px min | First image: no text/watermark |
| Detail Page | 750px width | Vertical scrolling design |
| Banner | 1920x600px | Promotional headers |
| Scene Image | 800x800px | Realistic usage scenarios |

### Pinduoduo Specifications

| Image Type | Size | Style |
|------------|------|-------|
| Main Image | 800x800px | High contrast, price-focused |
| Carousel | 800x800px | Multiple angles |
| Scene Image | 800x800px | Value proposition |

## Generation Workflow

### Step 1: Identify Platform & Image Type
Determine the target e-commerce platform and specific image type needed.

### Step 2: Gather Product Information
Collect:
- Product name and category
- Key features and selling points
- Target audience
- Brand guidelines (if any)
- Reference images (optional)

### Step 3: Create Image Prompt
Construct detailed prompts including:

```
[Product Name] product photography
- Platform: [Amazon/Taobao/Tmall/Pinduoduo]
- Type: [Main image/Lifestyle/Infographic/Banner]
- Style: [Clean minimal/Lifestyle/Corporate]
- Key elements: [Product, background, props]
- Technical specs: [Size, aspect ratio]
```

### Step 4: Generate & Refine
- Generate initial image
- Review against platform specifications
- Refine prompt if needed
- Generate final version

## Prompt Templates

### Main Product Image (Amazon)
```
Professional [product name] product photography on pure white background.
Studio lighting, high-end commercial photography style.
[Product category] with [key features visible].
Sharp focus, no shadows, no props, no text.
Centered composition, 1000x1000px minimum.
```

### Lifestyle Image
```
[Product name] being used in [specific setting/scenario].
Natural lighting, lifestyle photography style.
[Target audience] using the product in [context].
Warm/general/cool tones depending on brand.
High resolution, professional quality.
```

### Infographic Image
```
Clean infographic design for [product name].
Features displayed: [list features with icons].
White/light background, professional typography.
Product image in [position].
Modern flat design style, high contrast.
```

### Banner Image (Taobao/Tmall)
```
E-commerce banner design for [promotion/event name].
[Product Name] featured prominently.
Promotional text space: [reserved area for text].
Color scheme: [brand colors/seasonal colors].
Modern Chinese e-commerce style, high visual impact.
```

### Comparison Chart Image
```
Product comparison chart for [product category].
[Product A] vs [Product B] comparison.
Clear data visualization, icons for features.
Professional business style.
White background with brand accent colors.
```

## Platform-Specific Best Practices

### Amazon
1. Main image must be pure white background
2. Product must fill 85% of image
3. No watermarks or text in main image
4. Lifestyle images should feel aspirational
5. Infographic images should highlight unique selling points

### Taobao/Tmall
1. First main image: no text overlays
2. Use Chinese text in details (localization)
3. Include size/measurement visuals
4. Scene images build emotional connection
5. Maintain consistent visual style

### Pinduoduo
1. High contrast images perform better
2. Price/value proposition should be visible
3. Use bright, saturated colors
4. Include social proof elements
5. Short, punchy messaging

## Use Cases

### Product Launch
1. Generate main product images (all platforms)
2. Create lifestyle shots for social media
3. Design promotional banners
4. Produce A+ content images (Amazon)

### Seasonal Campaign
1. Create themed banner images
2. Generate promotional graphics
3. Design email/social media assets
4. Produce landing page imagery

### Brand Refresh
1. Generate consistent new imagery
2. Create style guide compliant images
3. Update all platform visuals
4. Produce brand story content

## Quick Commands

When user provides:
- Product name + "main image" → Generate main product image
- Product name + "detail page" → Generate detail page imagery
- Product name + "Banner" → Generate promotional banner
- Product name + "scene image" → Generate lifestyle scene
- Product name + "comparison" → Generate comparison chart

## Notes

- Always specify platform and image type in requests
- Reference images help achieve better results
- Platform specifications may vary - check current requirements
- A/B test different image styles when possible
