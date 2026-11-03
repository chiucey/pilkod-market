---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 403d716aa3110cb2ebd7211e26b8321e
    PropagateID: 403d716aa3110cb2ebd7211e26b8321e
    ReservedCode1: 3045022100a6267cb7d9c6f6d71efdfe0ae2018eabc8c3f13493024c1e3e164c944775d0e80220510e2cc1fd6c1bc3d50b466aac900d8811be0456b49c5d6f06916512a0f2209a
    ReservedCode2: 3046022100b5069bedd80b8e8cd54c70315ed889e3d6ca402a45587148fb07418275e0de01022100db71b7dd602e68f23f95af6ed1d8d73eb604a4262176bb24546a36bf8d8445da
---

# AI Short Film Creation Skill

> **Professional Director's Perspective**: This skill integrates traditional storytelling principles with large language model capabilities, designed for AI-native video creation workflows.

---

## Core Philosophy: From "Controller" to "System Designer"

| Traditional Director | AI-Era Director |
|---------------------|-----------------|
| Control every frame | Design prompt systems |
| Linear execution | Parallel exploration + iteration |
| Pursue determinism | Manage probability |
| Focus on single decisions | Focus on overall architecture |

---

## Three-Layer Prompt Architecture

### L1: Concept Layer (Strategic)

```yaml
Purpose: Establish overall direction and visual identity
AI Use: Understanding style, theme, and emotional tone
```

```
Core Theme: Realistic Dark Tokusatsu | BLACK SUN Aesthetics | Broken Flesh | Battle Damage Transformation | Apocalypse Battlefield

Style Keywords:
- Anamorphic widescreen cinematic quality
- IMAX film camera + Panavision C Series lens
- Low saturation gray-blue main tone
- Film grain texture, soft focus on edges

Emotional Baseline: Oppressive, heavy, realistic flesh pain feeling
```

### L2: Structure Layer (Tactical)

```yaml
Purpose: Control timing, rhythm, and sequence flow
AI Use: Temporal coherence, pacing management
```

```
【Camera Rules】
- Single Shot: One-take, no editing
- Angles: Opening low-angle → Orbit to front → Overhead after completion
- Breathing Feel: Handheld shot, subtle camera floating

【Timeline】
0-3s · Gaze: Tension building (slow)
3-6s · Activation: Energy accumulation (accelerating)
6-9s · Tearing: High-impact climax (fast)
9-12s · Growth: Transition (decelerating)
12-15s · Completion: Resolution (stop/hold)
```

### L3: Execution Layer (Operational)

```yaml
Purpose: Define specific actions, effects, and visual details
AI Use: Fine-grained generation
```

```text
Example: Transformation Activation

"话音刚落，手掌用力按压腰带核心，水晶核心本体被挤压而开裂，
红光伴随晶体的裂纹亮起，启动装置后慢慢松开手"

Example: Mecha Landing

"巨大的机体犹如陨石般砸向海面，为减少缓冲，
以单脚跪姿、单手撑地的英雄登场方式安全着陆"
```

---

## Professional Workflow

### Phase 1: Ideation & Planning (10% of effort)

#### 1.1 Inspiration Acquisition
- **No complete script needed** - use agile creation method
- Discuss with friends, create 2-3 test shots to validate visual direction
- Mx-Shell approach: "边做边想" - work as you go

#### 1.2 Visual Pre-visualization
- Form scene in mind: position (up/down/left/right/center/edge)
- Only describe after clear mental picture
- **Do not fully rely on AI** - guide the generation

#### 1.3 Style Definition
- Choose language: English for retro, Chinese for modern
- Color tone: Scene image determines overall palette

### Phase 2: Prompt Engineering (20% of effort)

**Core Principle**: 95% hand-written, AI only for special actions

#### Attention Guidance Principles

```yaml
High-Frequency Emphasis → Low-Frequency Details

# Inefficient
主角按压腰带，腰带发出红光

# Efficient (keyword repetition for attention)
主角用力按压腰带核心，水晶核心本体被挤压而开裂，
红光伴随晶体的裂纹亮起，启动装置后慢慢松开手
```

#### Spatial Description Principles

AI understands **spatial positions** better than abstract concepts:

```yaml
# Abstract
"英雄登场"

# Spatial (better for AI)
"单脚跪姿、单手撑地、水墙环形扩散"
```

#### Temporal Decomposition Principles

Large models have **context window limits** - long sequences cause attention decay:

```yaml
# NOT Recommended: 15s continuous description
0-15s: Full sequence (后半段质量下降)

# Recommended: Segmented timeline
0-3s: Gaze phase
3-6s: Activation phase
6-9s: Tearing phase
# Each segment maintains independent completeness
```

### Phase 3: Generation (40% of effort)

#### Quality Control Nodes

```
Stage 1: Concept Validation (2-3 test shots)
  ├─ Evaluate: Is style correct?
  ├─ Decision: Continue this direction?
  └─ Output: Viable prompt framework

Stage 2: Segment Generation (each 15-20s)
  ├─ Evaluate: Is timing smooth?
  ├─ Decision: Need adjustments?
  └─ Output: Usable video clips

Stage 3: Post-production Integration
  ├─ Evaluate: Overall rhythm/emotion consistent?
  ├─ Decision: Need supplementary shots (regenerate)?
  └─ Output: Final film
```

#### Resource Investment Ratio

```
Concept: 10% (quick test, direction validation)
Prompt Writing: 20% (refinement, structuring)
Generation: 40% (massive draws, screening)
Post-production: 30% (editing, color, audio)
```

#### Effective Generation Rate

Based on analysis of Mx-Shell's workflow (400 images, 200+ clips, 10 days editing):

```
Effective generation rate ≈ 50% (requires extensive screening)
Budget for multiple attempts: Plan 2-3x expected generation count
```

### Phase 4: Post-production & Editing

#### Editing Workflow

| Statistic | Value |
|-----------|-------|
| Image-to-video ratio | ~80% images generate clips |
| Total clips generated | 200+ for complex works |
| Editing duration | ~10 days for complex projects |

#### Multi-clip Splicing Strategy

```yaml
Multi-segment Generation:
1. Use web "generate video continuation" feature
2. Split into two parts (weapon charge + fight)
3. Multiple draws + post-production splicing
4. Common practice for complex sequences
```

#### Audio Processing

- **Minimal dialogue**: One true voice line is enough
- **Voice reference**: Use Xiaoyunque Voice Reference for uniform timbre

---

## Traditional Storytelling → AI Translation

### Three-Act Structure → AI Video Mapping

| Traditional Act | AI Video Phase | Duration |
|----------------|---------------|----------|
| Setup | Gaze + Activation | 0-6s |
| Confrontation | Tearing + Growth | 6-12s |
| Resolution | Completion + End | 12-15s |

### Hero's Journey (Simplified)

```
Normal World → Call → Refusal → Acceptance →
Threshold → Trial → Reward → Return

AI Simplified Version:
变形前 → 按压腰带 → 能量爆发 → 战衣成型 → 战斗姿态
```

### Visual Rhythm Control

```yaml
Timeline Rhythm Design:
0-3s: SLOW (establish tension)
3-6s: GRADUALLY FASTER (energy accumulation)
6-9s: FAST (peak climax, tearing)
9-12s: GRADUALLY SLOWER (transition)
12-15s: STOP (freeze frame, resolution)
```

This rhythm follows traditional **crescendo-burst-decrescendo** pattern.

---

## Large Model Limitations & Solutions

### 1. Long-sequence Consistency Problem

**Issue**: Content over 10s容易出现风格漂移、穿帮累积

**Solution Matrix**:

| Solution | Principle | Cost | Effect |
|----------|-----------|------|--------|
| Segmented Generation | Divide long content into short clips | Medium | High |
| Reference Anchoring | Provide keyframe screenshots as reference | Low | Medium |
| Post-fix | Use image models to repair single frames | High | Medium |
| Abandon Long Take | Use montage instead | Low | Medium |

**Professional Advice**: Single shots under 15s are most stable; segment if longer.

### 2. Physics Simulation Problem

**Issue**: AI has weak understanding of physics, common "phase through walls", "floating", "gravity violations"

**Solutions**:

1. **Prioritize Seedance**: Best physics feedback model
2. **Simplify physics scenes**: Avoid complex physics interactions (liquids, cloth)
3. **Accept and leverage**: "Glitch" sometimes becomes style (slow motion, dramatic treatment)

### 3. Face Consistency Problem

**Issue**: Cross-clip face changes are hardest to control

**Solutions**:

```yaml
Solution 1: Sketch Method
  Convert photo to realistic color sketch → AI generates new image
  Pros: Bypass face detection limits
  Cons: Distortion

Solution 2: Description Anchoring
  Provide detailed facial description (features, face shape, hairstyle)
  Pros: Maintain authenticity
  Cons: Unstable

Solution 3: Clone Tool Method
  Use AI clone tool
  Pros: Maintain consistency
  Cons: High cost, fixed style
```

---

## Tool Selection

### Recommended Tool Chain

| Purpose | Recommended Tool | Notes |
|---------|-----------------|-------|
| Video Generation | Xiaoyunque Seedance 2.0 | Best physics feedback, detail, fidelity |
| Image Generation | GPT (80%) > Midjourney > Banana > Flux | GPT comprehensive, Midjourney artistic |
| Image Enhancement | Flux | Optimize material and realism |
| Three-View | Nanobanan | For mecha and multi-angle display |
| Editing | Jianying (CapCut) | Simple and effective |
| Audio | Xiaoyunque Voice Reference | Unify voice timbre |

### Model Selection Principles

- **Prioritize Seedance 2.0** (non-Fast version)
- Fast mode: Fast but lower quality
- Every model has strengths - choose based on content

### Core Selection Criteria

1. **Suitability for Content**: Different models excel at different content types
2. **Workflow Convenience**: Integration ease and usability
3. **Model Availability**: Access to needed AI models
4. **Pricing**: Acceptable within budget

---

## Quality Assessment Standards

| Dimension | Score | Checkpoints |
|-----------|-------|-------------|
| Style Consistency | 1-5 | Similarity to reference images |
| Temporal Smoothness | 1-5 | Coherence between clips |
| Detail Completeness | 1-5 | Glitch count, corruption degree |
| Emotion Conveyance | 1-5 | Can audience feel expected emotion? |
| Technical Quality | 1-5 | Resolution, frame rate, clarity |

---

## Common Problem Solutions

### Generation Failure
- Simply regenerate
- Prompt violation: Delete words/punctuation without changing meaning

### Copyright Issues
- Replace phrases related to film/TV works
- Enterprise users can use FlowMuse (with permissions)

### Face Not Supported
- Ignore system prompts, continue generating (may not look like original)
- Method 1: Use Doubao to generate "realistic style color sketch"
- Method 2: Provide multiple photos + detailed description

### Unideal Effects
- Common AI creation issue - try multiple times
- Modify prompt yourself, add detailed requirements
- Reference images need high quality (realistic, detailed)

### Armor Design
- Not recommended to use reference images
- Use description for AI to create freely - unique designs are more meaningful
- Everyone having different armor is more interesting

### Word Limit
- Use computer web version
- Or trim content yourself

---

## Storyboard Templates

### Template Structure (Muxin Style)

```
Core Theme: [Realistic Dark Tokusatsu] | [BLACK SUN Aesthetics] | [Broken Flesh] | [Battle Damage Transformation] | [Apocalypse Battlefield]

【Character & Basic Settings】
- Face: Reference uploaded photo, 100% restoration of features, no beautification
- Costume: [Detailed description]
- Scene: [Environment description]

【Atmosphere & Visual Quality】
- Visual Baseline: Anamorphic widescreen cinematic quality
- Simulated Equipment: IMAX film camera + Panavision C Series lens (35mm, f4)
- Color & Tone: Low saturation gray-blue main tone, soft focus on edges, film grain texture

【Camera Rules】
- Single Shot: One-take, no editing
- Angles: Open with low-angle, orbit to front view, top-down after transformation
- Breathing Feel: Handheld shot, subtle camera floating for immersion

【Storyboard Content】
0-3s · Gaze: [Action] + [Camera] + [Effects]
3-6s · Activation: [Sound] + [Action] + [Effects]
6-9s · Tearing: [Core] + [Body] + [Jacket] + [Camera]
9-12s · Growth: [New Substance] + [Shoulder Armor] + [Chest Armor] + [Face Cover]
12-15s · Completion: [Helmet] + [Armor] + [Final Shot]
```

### 15-Second Transformation Template

```
Core Theme: Realistic Dark Tokusatsu | Broken Flesh | Battle Damage Transformation | Alien Bio-Tech | Live Action

【Character & Basic Settings】
- Face: Reference uploaded photo, 100% restoration, no beautification
- Costume: Black tight tank top, khaki camouflage pants, khaki high-top combat boots
- Scene: Desert, gentle breeze, sandstorm, giant void creature

【Atmosphere & Visual Quality】
- Simulated Equipment: IMAX film camera + Panavision C Series lens
- Color & Tone: Low saturation cyan-orange, film grain texture
- Core Effects: Hollywood film quality, commercial VFX

【Storyboard Control】
- Shot 1 (35mm): Opening → Character speaking, low-angle medium shot push-in
- Shot 2 (24mm): Hands hitting ground → Vines appearing, overhead panoramic orbit
- Shot 3 (35mm): Vines whipping → Complete standing, FPV orbit
- Shot 4 (50mm): Pain relief → Face mask closing, front close-up
- Shot 5 (24mm): Power charging → End, overhead shot rocket launch

【Timeline】
0-3s Gaze: Kneeling desperate, exhausted expression, eyes light up purple
3-6s Awakening: Hands hitting ground, shockwave, rifts appearing
6-9s Erosion: Purple mist surge, vines connecting limbs, face tattoos
9-12s Coverage: New substance seeping, bodysuit forming, vines forming armor
12-15s Completion: Armor complete, mask closes, launch and fire
```

### Mecha Transformation Template

```
Core Theme: Realistic Tech | Sci-Fi Mecha | Heavy Industrial Mechanical Aesthetics | Live Action

【Camera Rules (FPV Mode)】
- Opening: Outside spacecraft overhead → Push + descend + tilt up → Front close-up eye-level
- Transformation: Pull back + descend + tilt up → Wide shot overhead → Jump + transform
- Landing: Follow mecha descent and maintain overhead → Crash into sea
- Stand: Push and orbit → Follow mecha stand and rise → Over-shoulder shot enemy

【Content】
0-1s Departure: Hatch opens, activate controller
1-4s Activation: Vest projection, virtual glove wearing
4-6s Jump: High-altitude dive posture
6-8s Combine: Red grid overlay, 50x mecha outline
8-11s Manifest: Mecha appears, thrusters light up, high-temp edges
11-12s Land: Single-knee hero landing, giant wave wall
12-14s Rise: Sea water washes, steam fills air
14-15s Threat: Glowing creature appears in front, roars
```

---

## Professional Tips

### Prompt Optimization Do's

- Be specific about camera angles, movements, and timing
- Include detailed descriptions of effects (light, particles, textures)
- Describe character's emotional state throughout sequence
- Use professional cinematography terminology
- Break down into timeline phases for complex sequences

### Prompt Optimization Don'ts

- Don't over-rely on reference images
- Don't use overly beautified photos
- Don't skip breathing feel in camera work
- Don't expect perfect results on first try - multiple draws needed

### Style Keywords

```yaml
- Anamorphic widescreen
- IMAX film camera
- Panavision C Series lens
- Low saturation gray-blue/cyan-orange
- Film grain texture
- Soft focus on edges
- Breathing handheld feel
- One-take no editing
```

---

## Reference Resources

- `references/prompt_templates.md` - Complete prompt template library
- `references/tool_comparison.md` - Detailed tool comparison
- `references/llm_analysis.md` - LLM capability analysis for AI directors
- `assets/scene_examples/` - Scene reference examples