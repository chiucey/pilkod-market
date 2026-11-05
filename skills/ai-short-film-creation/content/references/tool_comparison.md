# Tool Comparison Reference

## 1. Video Generation Platforms

### Xiaoyunque (小云雀)

**Overview**: Integrated platform for AI video generation, not a model itself.

**Key Features**:
- Immersive Short Films with Seedance 2.0
- Voice Reference function for uniform voice timbre
- Web version with longer content generation
- "Generate video continuation" feature for extended videos

**Seedance 2.0 Model**:
- Physics feedback: Best
- Detail resolution: Highest
- Fidelity: Excellent
- Recommended for: Transformation sequences, action shots

**Seedance 2.0 Fast**:
- Speed: Fast
- Quality: Lower than standard
- Use case: Quick previews only

**Recommendation**: Use non-Fast standard version for final output.

**Pricing**: Contact platform directly

---

### FlowMuse

**Overview**: Enterprise-focused AI generation platform.

**Key Features**:
- Has official permissions and declaration rights
- Better for copyright-sensitive content
- Enterprise solutions available

**Use Case**: Commercial projects requiring copyright compliance

**Recommendation**: For corporate users or projects with IP concerns

---

## 2. Image Generation Models

### GPT Image (DALL-E)

**Usage**: ~80% of images in Mx-Shell's production

**Strengths**:
- Comprehensive and easy to use
- High quality across diverse styles
- Good balance of accuracy and creativity

**Best For**: Primary image generation, diverse content needs

**Model Versions**: Multiple iterations, latest generally recommended

---

### Midjourney

**Usage**: Secondary image generation

**Strengths**:
- Artistic creation capability exceptional
- Strong style interpretation
- Great for cinematic aesthetics

**Best For**: High-quality artistic materials, style-heavy content

**Note**: May not surpass GPT in accuracy but excels in artistic performance

---

### Flux

**Usage**: Material optimization, realism enhancement

**Strengths**:
- Excellent for material and texture detail
- Enhances realism of generated images
- Good for technical/sci-fi content

**Best For**:
- Material detail optimization
- Realism enhancement for scenes
- Technical equipment visualization

---

### Banana / Flus Max

**Usage**: Supplementary image generation

**Strengths**:
- Alternative option when primary tools unavailable
- Diverse model selection

**Best For**: Experimenting with different styles

---

### Nanobanan

**Usage**: Three-view generation for mecha/characters

**Strengths**:
- Perfect for multi-angle character/mecha display
- Maintains consistency across different views

**Best For**:
- Mecha design
- Character design three-view
- Product visualization

---

## 3. Workflow Recommendations

### Standard Workflow (Transformation Video)

```
1. Storyboard Image Generation
   - Use GPT/Midjourney to generate reference storyboards
   - Add to prompt: "黑白手稿 or 黑白手绘稿 用于分镜图参考"

2. Character/Costume Images
   - Use GPT for primary generation
   - Use Flux for material/realism optimization

3. Environment/Scene Images
   - Use GPT or specialized scene models
   - Ensure consistent color tone with overall project

4. Video Generation
   - Use Seedance 2.0 (non-Fast) for final output
   - Multiple attempts recommended
   - Post-production splicing for complex sequences

5. Editing
   - Jianying (CapCut) for timeline assembly
   - Color grading minimal (scene image determines tone)
```

### Mecha Production Workflow

```
1. Reference Images
   - GPT/Midjourney: Character and costume references
   - Flux: Material and texture optimization
   - Nanobanan: Three-view consistency check

2. Scene Images
   - Generate with consistent color palette
   - Include environmental details

3. Video Generation
   - Seedance 2.0 for transformations and action
   - Consider multi-segment generation for complex sequences
   - Post-production editing for final assembly

4. Post-Processing
   - Jianying for timeline work
   - Minimal color adjustment (rely on scene images)
```

---

## 4. Tool Selection Principles

### Core Selection Criteria

1. **Suitability for Content**: Different models excel at different content types
2. **Workflow Convenience**: Integration ease and usability
3. **Model Availability**: Access to needed AI models
4. **Pricing**: Acceptable within budget

### Platform Philosophy

> "Platform doesn't matter, as long as it suits you, workflow is convenient, has needed AI models, and price is acceptable. Don't be blinded, acceptable price to you is best."

---

## 5. Common Tool Combinations

### Transformation Video
- Image: GPT (primary) + Flux (optimization)
- Video: Seedance 2.0
- Edit: Jianying

### Mecha Project
- Image: GPT + Midjourney + Nanobanan (three-view)
- Video: Seedance 2.0
- Edit: Jianying

### Cyberpunk Style
- Image: Flux (for realism) + Midjourney (for style)
- Video: Seedance 2.0
- Edit: Jianying

---

## 6. Limitations and Workarounds

### Face Not Supported
**Issue**: Platform may not support real face photos

**Solutions**:
1. Ignore system prompts and continue (may not look like original)
2. Generate "realistic color sketch" via Doubao
3. Use detailed text descriptions instead of reference photos

### Prompt Violation
**Issue**: Content policy blocks generation

**Solutions**:
1. Remove/replace film/TV related terms
2. Simplify description without changing meaning
3. Use enterprise platforms with permissions (FlowMuse)

### Word Limit
**Issue**: Prompt exceeds character limits

**Solutions**:
1. Use computer web version (higher limits)
2. Trim redundant descriptions
3. Split into multiple generations

### Quality Inconsistency
**Issue**: AI may not follow prompts accurately

**Reality**:
- Multiple draws may be needed
- Post-production splicing is common
- "AI creation通病" - common issue requiring patience

---

## 7. Model Evolution Note

> "In recent years, AI iteration has been very fast. As models evolve, tool effectiveness may change. Stay updated with latest model capabilities and adjust workflow accordingly."

---

## 8. Complementary Tools

### For Audio
- **Xiaoyunque Voice Reference**: Uniform voice timbre across project

### For Editing
- **Jianying (CapCut)**: Simple timeline editing, widely used
- **Duration**: Complex works may take ~10 days for editing

### For Reference Generation
- **Image Models**: GPT, Midjourney, Banana, Flus Max
- **Prompt Addition**: "黑白手稿 用于分镜图参考"

---

## 9. Quick Reference Table

| Task | Primary Tool | Secondary Tool | Notes |
|------|-------------|----------------|-------|
| Transformation Video | Seedance 2.0 | - | Use non-Fast version |
| Character Image | GPT | Flux | 80% GPT in practice |
| Mecha Three-View | Nanobanan | - | Consistency focus |
| Material Enhancement | Flux | - | Realism optimization |
| Scene Image | GPT | Midjourney | Color tone consistency |
| Editing | Jianying | - | Simple and effective |
| Voice Uniformity | Xiaoyunque Voice | - | Reference function |