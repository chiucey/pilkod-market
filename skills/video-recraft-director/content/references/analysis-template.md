# Video Analysis Reference Template

## Complete Analysis Structure

### 1. Visual Analysis Dimensions

#### Character Identification
- Gender, age, appearance
- Hairstyle (color, length, styling)
- Clothing (color, style, material)
- Expression (natural, smiling, serious, etc.)
- Motion (gestures, movement, posture)

#### Product/Object
- Position (foreground, midground, background)
- Angle (front, side, 45-degree, etc.)
- Material (metal, plastic, glass, etc.)
- Packaging (color, brand logo)
- Holding method
- Display motion

#### Scene Environment
- Indoor/outdoor
- Specific location (balcony, kitchen, office, etc.)
- Lighting (natural light, artificial light, soft light, strong light)
- Weather (sunny, cloudy, indoor)
- Spatial structure
- Atmosphere

#### Photography Parameters
- Camera angle (eye level, top-down, low angle)
- Focal length (wide angle, standard, telephoto)
- Depth of field (shallow, deep)
- Camera motion (push, pull, pan, tilt, handheld)
- Composition (rule of thirds, center composition, etc.)
- Vertical/horizontal

### 2. Storyboard Structure

```
【Start Time】 → 【End Time】
Shot Number: [N]
Visual: [Description]
Motion: [Motion keypoint]
Transition: [Transition type]
```

### 3. Audio Analysis

| Time | Speaker | Original | Translation | Tone | Speed | Lip Sync |
|------|---------|----------|------------|------|-------|----------|
| 00:01 | Female | ... | ... | Warm | Medium | Natural |

### 4. Prompt Generation Rules

#### English Prompt Structure
1. **Subject Description**: Core features of character/scene
2. **Motion Description**: Specific action behavior
3. **Camera Description**: Cinematography movement
4. **Lighting Description**: Light and shadow characteristics
5. **Style Description**: Realism/texture
6. **Lip Sync**: Dialogue synchronization instruction

#### Negative Prompt Checklist
- Deformation issues: `deformed hands, extra fingers, twisted fingers`
- Object errors: `wrong product, incorrect label, wrong color`
- Style errors: `cartoon, anime, illustration, 3D render`
- Quality errors: `blur, noise, low quality, watermark`
- Lip sync errors: `out of sync lip movement`

### 5. Common Shot Terminology (English)

| Chinese | English |
|---------|---------|
| Push in | push in, dolly in |
| Pull back | pull back, dolly out |
| Orbit | orbit, circle around |
| Handheld | handheld, shaky cam |
| Static shot | static shot, locked off |
| Top-down | top-down shot, overhead |
| Low angle | low angle shot, worm's eye |
| Tracking | tracking shot, follow shot |
| Shallow DOF | shallow depth of field, bokeh |
| Deep focus | deep focus, all in focus |
| Soft light | soft lighting, diffused light |
| Hard light | harsh lighting, direct light |
| Backlight | backlight, rim light |
| Catch light | catch light in eyes |