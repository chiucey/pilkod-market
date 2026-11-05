---
name: amazon-ecommerce-image
description: Create professional Amazon e-commerce product images using AI. Use when users need to generate Amazon product main images, lifestyle scenes, infographic images, or want to learn Amazon image creation workflow including image reverse prompting, product retouching, product blending, and object removal. Trigger phrases: "亚马逊产品图", "Amazon product image", "跨境电商图片", "亚马逊主图", "AI生图", "产品精修", "竞品图分析"
---

# Amazon E-commerce Product Image Generation Skill

## Overview

This skill provides comprehensive guidance for creating professional Amazon e-commerce product images using AI tools. It covers the complete workflow from competitor analysis to final image delivery, including prompt engineering techniques specifically optimized for Amazon marketplace requirements.

**Target Platform**: Amazon (Global marketplaces including US, EU, JP)
**Skill Type**: AI Image Generation & E-commerce Design
**Complexity Level**: Intermediate to Advanced

---

## Core Techniques

### 1. Image Reverse Prompting (图片反推)

Extract professional prompts from existing competitor images to replicate their visual style.

**Reverse Prompt Template**:
```
Please analyze this image and generate a structured, precise AI painting prompt. Your task is to perform reverse parsing and extraction on the image from multiple core dimensions: subject, scene environment, artistic style, color tone and lighting, composition perspective, and detail texture. Finally, integrate into high-quality text description to guide AI tools in recreating works with highly similar style and content.
```

**Use Case**: Analyze top-selling competitor images to extract their visual DNA, then apply to your own product.

**Workflow**:
1. Find 3-5 competitor products with high-quality images
2. Use the reverse prompt template to extract their prompts
3. Combine competitor scene/style prompts with your product details
4. Generate new images that match competitor quality

---

### 2. Product Retouching (产品精修)

Enhance product images to commercial-grade quality, removing imperfections and optimizing visual appeal.

**Product Retouching Prompt Template**:
```
Product retouching: The [PRODUCT TYPE] in the image is placed on a pure white background. [VIEW ANGLE] front view, eye-level perspective, 3D rendering, accurately restoring product color and packaging material (such as glass transparency, plastic matte finish, metallic luster). Remove all fingerprints, dust and imperfections, making the product look brand new. Enhance overall texture and premium feel. Soft, even lighting highlights product sophistication, meeting e-commerce main image standards.
```

**Key Parameters**:
| Element | Options | Description |
|---------|--------|-------------|
| Background | Pure white (#FFFFFF) | Mandatory for Amazon main images |
| Angle | Front view, 45-degree, side view | Varies by product type |
| Rendering | 3D render, product photography | Style consistency |
| Material | Glass, metal, plastic, fabric | Material-specific handling |
| Lighting | Soft diffused, studio lighting | Professional look |
| Quality | No fingerprints, dust, scratches | Clean presentation |

**Material-Specific Keywords**:
- **Glass**: "crystal clear", "transparent glass texture", "refraction"
- **Metal**: "metallic luster", "brushed steel", "mirror finish"
- **Plastic**: "matte texture", "smooth surface", "soft-touch coating"
- **Fabric**: "soft fabric texture", "realistic weave pattern"

---

### 3. Product Blending (产品溶图)

Seamlessly integrate products into lifestyle scenes for immersive advertising.

**Product Blending Prompt Template**:
```
Remove the white background from the product, maintaining product position and fine details. Correct unrealistic overlapping effects, enhance lighting consistency, naturally blend elements giving them natural light and shadow. Color temperature, brightness and saturation must coordinate with the environment, presenting realistic highlights and shadows, eliminating visual seams, ultimately presenting a seamless fusion effect.
```

**Blending Principles**:
- **Lighting Consistency**: Match product lighting with scene lighting direction and intensity
- **Shadow Integration**: Ensure product casts appropriate shadow on scene surface
- **Color Harmony**: Adjust color temperature to match scene ambiance
- **Scale Accuracy**: Product size relative to scene elements must be realistic
- **Edge Blending**: No visible outlines or halos around product edges

**Common Issues & Solutions**:
| Issue | Solution |
|-------|----------|
| Unnatural shadows | Add "realistic shadow casting on surface" to prompt |
| Color mismatch | Include "match scene color temperature" |
| Visible edges | Add "seamless edge blending", "anti-halation" |
| Scale issues | Specify "realistic product-to-scene scale ratio" |

---

### 4. Object Removal (万物移除)

Cleanly remove unwanted elements from images while preserving scene integrity.

**Object Removal Prompt Template**:
```
Remove the [ELEMENT TO REMOVE] from the image, including its shadow, reflection and all related projections. The original product position should be naturally filled based on surrounding environment (such as extending background patterns, continuing material textures or restoring original surface), leaving no trace of deletion. All other elements in the image must remain 100% unchanged in position, shape, color and detail.
```

**Use Cases**:
- Remove background distractions (wires, tags, watermarks)
- Clean up product imperfections (scratches, dust)
- Remove competitor branding from reference images
- Eliminate AI-generated watermarks

---

### 5. Product Swap (产品互换)

Replace a product in an existing scene while maintaining scene authenticity.

**Product Swap Prompt Template**:
```
- Replace the product in Image 2 with the product from Image 1
- Maintain Image 2's scene, lighting and atmosphere unchanged
- Preserve Image 1 product position and fine details
- Correct unrealistic overlapping effects, enhance lighting consistency
- Naturally blend elements giving them natural light and shadow
- Color temperature, brightness and saturation must coordinate with environment
- Present realistic highlights and shadows, eliminate visual seams
- Ultimately present seamless fusion effect
```

---

## Amazon Image Types & Specifications

### Main Image (主图) - First Image

**Requirements**:
- Pure white background (#FFFFFF, RGB 255, 255, 255)
- Product occupies 85% or more of image area
- No text, logos, or graphics
- Professional lighting, centered product
- Maximum resolution: 3000 x 3000 pixels minimum

**Prompt Example**:
```
Amazon main image: Professional product photography on pure white background. [PRODUCT TYPE] centered, occupying 85% of frame. Clean studio lighting with soft shadows. No text or graphics. High resolution, commercial quality. Realistic 3D render showing product texture clearly.
```

---

### Lifestyle/Scene Images (场景图)

**Requirements**:
- Show product in realistic usage context
- Lifestyle-oriented, aspirational imagery
- Professional composition and lighting
- Can include lifestyle elements and props

**Prompt Example**:
```
Lifestyle scene: [PRODUCT TYPE] elegantly displayed in modern [SCENE TYPE] setting. Natural ambient lighting with professional soft shadows. Lifestyle props complementing product. Clean composition with bokeh background. Aspirational mood, commercial photography style.
```

---

### Infographic Images (信息图)

**Requirements**:
- Clear hierarchy of information
- Professional layout with visual balance
- High contrast for readability
- Brand-consistent color scheme

**Common Elements**:
- Size comparison charts
- Feature callouts with icons
- Comparison tables
- Usage instructions

---

### Exploded/Explained View (拆解图)

**Requirements**:
- Clear component breakdown
- Professional technical illustration style
- Labels and annotations in clean typography
- Technical yet accessible presentation

**Prompt Example**:
```
Exploded view: [PRODUCT TYPE] disassembled into component parts, neatly arranged. Technical illustration style with clean lines. Professional lighting highlighting each component. Clear visual hierarchy showing relationship between parts. Minimal background, product-focused composition.
```

---

## Complete Workflow: Amazon Image SOP

### Phase 1: Pre-production Research

**Step 1.1: Competitor Analysis**
1. Search Amazon with product keywords
2. Use "search by image" feature to find similar products
3. Select 3-5 top-performing competitor products
4. Analyze their image strategy:
   - Main image style (white background vs. lifestyle)
   - Image sequence and types
   - Visual hierarchy and information flow
   - Color palette and mood

**Step 1.2: Product Photography**
1. Shoot product from multiple angles (front, side, back, 45-degree)
2. Use white background or white paper as backdrop
3. Ensure adequate lighting
4. Capture high-resolution images (minimum 2000px)

---

### Phase 2: AI-Assisted Generation

**Step 2.1: Extract Prompts**
1. Input competitor images into AI tool
2. Use reverse prompting template to extract prompts
3. Refine extracted prompts for your specific product

**Step 2.2: Generate Drafts**
1. Input refined prompts with your product image
2. Generate multiple versions (recommend 4-6 variations)
3. Evaluate based on:
   - Visual quality
   - Accuracy to prompt
   - Product detail preservation
   - Brand consistency

**Step 2.3: Selection & Iteration**
1. Select 1-2 most promising drafts
2. Identify specific issues for refinement
3. Iterate with targeted adjustments
4. Final quality check

---

### Phase 3: Post-processing & Delivery

**Step 3.1: Watermark Removal**
- Use AI remove tool to eliminate watermarks
- Verify no artifacts remain

**Step 3.2: Template Application**
- Apply standardized layout templates
- Add brand-consistent typography
- Ensure information hierarchy is clear

**Step 3.3: Export & Optimization**
- Export as JPEG format
- Verify Amazon dimension requirements
- Compress for optimal file size without quality loss

---

## Prompt Engineering Best Practices

### Do's

1. **Be Specific**: Include exact details (colors, materials, lighting type)
2. **Use Visual References**: Reference similar high-quality images
3. **Specify Dimensions**: Include angle, perspective, scale
4. **Emphasize Quality**: Include "professional", "commercial grade"
5. **Match Platform Standards**: Reference Amazon requirements
6. **Iterate Systematically**: Build prompts incrementally

### Don'ts

1. **Avoid Vague Descriptions**: "good looking" vs. "premium finish"
2. **Don't Overload Prompts**: Focus on 3-4 key elements per image
3. **Avoid Contradictory Instructions**: Ensure prompt coherence
4. **Don't Skip Quality Markers**: Always include resolution/quality terms

---

## Quality Checklist

### Main Image
- [ ] Pure white background (#FFFFFF)
- [ ] Product centered and properly sized
- [ ] No text, logos, or graphics
- [ ] Professional lighting
- [ ] High resolution (3000x3000 minimum)
- [ ] Accurate color representation

### Secondary Images
- [ ] Consistent visual style
- [ ] Clear information hierarchy
- [ ] Professional typography
- [ ] Brand color consistency
- [ ] Readable on mobile devices
- [ ] Proper contrast and sharpness

### Technical Requirements
- [ ] Correct file format (JPEG)
- [ ] Optimal file size (<10MB recommended)
- [ ] Proper aspect ratio
- [ ] No compression artifacts
- [ ] Metadata removed (if required)

---

## Common Issues & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Product looks distorted | Wrong perspective prompt | Add "accurate perspective", "correct proportions" |
| Colors inaccurate | Lighting mismatch | Specify "natural color rendering", "accurate colors" |
| Background not pure white | Environment bleed | Add "pure white background", "remove color cast" |
| Text hard to read | Low contrast | Specify "high contrast typography", "bold text" |
| Product looks fake | Unrealistic rendering | Add "photorealistic", "natural texture", "authentic lighting" |
| Scene looks artificial | Poor blending | Include "natural scene integration", "realistic environment" |

---

## Resources & Tools

### AI Image Generation Tools
- **Primary**: Use available AI image generation platforms
- **Recommended Features**: Background removal, inpainting, outpainting

### Image Editing Tools
- **Watermark Removal**: AI-powered remove tools
- **Background Removal**: Automatic subject isolation
- **Color Correction**: Match scene lighting
- **Composition**: Layer compositing, masking

### Amazon Compliance
- **Image Dimensions**: Minimum 1000x1000 pixels
- **Color Space**: sRGB recommended
- **File Format**: JPEG preferred, TIFF accepted
- **Aspect Ratio**: 1:1 (square) or 3:2 for lifestyle

---

## Summary

1. **Master Reverse Prompting**: Extract professional prompts from competitors
2. **Know Your Image Types**: Main image, lifestyle, infographic, exploded view
3. **Follow the SOP**: Research → Generate → Refine → Deliver
4. **Prioritize Quality**: Professional, commercial-grade output
5. **Stay Platform-Compliant**: Amazon-specific requirements
6. **Iterate and Improve**: Systematic refinement leads to best results

---

*This skill is designed to help you create professional Amazon e-commerce images efficiently using AI tools, following industry best practices and platform requirements.*
