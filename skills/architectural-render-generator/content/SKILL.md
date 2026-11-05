---
name: architectural-render-generator
description: Professional architectural visualization skill for generating photorealistic renders from Rhino/SU model screenshots. Use when users upload Rhino or SketchUp model screenshots and request professional architectural rendering with diverse atmospheric scenes.
---

# Architectural Render Generator

## Skill Overview

This skill transforms architectural massing models (Rhino/SU) into professional photorealistic renderings by understanding color-coded massing logic and generating diverse atmospheric scene compositions.

## Core Capabilities

- Analyze color-coded massing blocks to understand building program distribution
- Generate multiple scene atmospheres (golden hour, overcast, night, etc.)
- Create contextual landscape and urban environment elements
- Produce presentation-ready architectural visualizations

---

## Phase 1: Massing Analysis

### 1.1 Color Zone Identification

When analyzing a Rhino/SU model screenshot, identify color groupings and their spatial relationships:

```
Sample Analysis Pattern:
- Identify each distinct color zone
- Map color to likely programmatic function
- Note vertical vs horizontal massing relationships
- Assess overall building typology (tower, slab, podium + tower, etc.)
```

### 1.2 Building Logic Interpretation

| Color Zone Type | Likely Program | Design Implications |
|----------------|----------------|---------------------|
| Tall vertical blocks | Residential units | Balcony details, window patterns |
| Wide horizontal bands | Office/commercial | Curtain wall systems, plaza interfaces |
| Low podium base | Retail/public amenity | Ground activation, canopy features |
| Open/courtyard voids | Common space | Landscape integration, water features |
| Accent colors | Entry/landmark elements | Signature architectural moments |

### 1.3 Contextual Reading

- **Urban context**: Surrounding context buildings, street grids
- **Landscape integration**: Grade changes, planting zones, water bodies
- **Human scale elements**: Entry canopies, street furniture, pedestrian paths

---

## Phase 2: Rendering Strategy

### 2.1 Atmosphere Selection

Offer users multiple atmospheric options:

| Atmosphere | Time of Day | Lighting Character | Best For |
|------------|-------------|-------------------|----------|
| Golden Hour | Late afternoon | Warm, dramatic shadows | Hero shots, presentations |
| Blue Hour | Dawn/dusk | Cool blue tones, warm accents | Urban context, mood |
| Overcast | Diffuse daylight | Even, soft shadows | Technical clarity |
| Clear Day | Midday | Bright, high contrast | Material studies |
| Night | After dark | Artificial lighting, reflections | Atmosphere, drama |
| Rainy | Inclement | Reflections, moody | Emotional impact |

### 2.2 Perspective Strategy

- **Exterior perspective**: Main composition angle showing massing relationships
- **Aerial view**: Site context, urban relationships
- **Street-level**: Human experience, scale references
- **Interior cutaway**: Spatial quality demonstration

---

## Phase 3: Prompt Engineering

### 3.1 Core Prompt Structure

```english-prompt
Professional architectural visualization, [PERSPECTIVE] view.
[BUILDING TYPE] with [COLOR-ZONE LOGIC INTERPRETATION].
Building massing comprises:
- [ZONE A: function and characteristics]
- [ZONE B: function and characteristics]
- [ZONE C: function and characteristics]
Context: [SURROUNDING ENVIRONMENT DESCRIPTION].
Time: [TIME OF DAY], Atmosphere: [ATMOSPHERE TYPE].
Style: [ARCHITECTURAL STYLE], Materials: [MATERIAL PALETTE].
Lighting: [LIGHTING MOOD], Camera: [CAMERA SPECIFICATIONS].
[ADDITIONAL DETAILS: landscape, figures, vehicles, context buildings].
Photorealistic rendering, professional architectural presentation quality.
```

### 3.2 Color Zone Mapping

Translate color zones to architectural elements:

```english-prompt
Color-coded massing translated to architectural program:
- [COLOR A zones]: [PROGRAM - e.g., residential apartments] with [MATERIAL - e.g., aluminum cladding, glass balconies]
- [COLOR B zones]: [PROGRAM - e.g., office floors] with [MATERIAL - e.g., curtain wall glazing]
- [COLOR C zones]: [PROGRAM - e.g., retail base] with [MATERIAL - e.g., natural stone, canopy]
- [VOID/COURTYARD]: [PUBLIC SPACE - e.g., landscaped plaza] with [FEATURES - e.g., trees, water feature]
```

### 3.3 Atmospheric Variations

**Golden Hour Prompt**:
```english-prompt
Golden hour architectural visualization, warm sunlight casting long dramatic shadows.
Time: 5:30 PM, Season: Autumn. Sun angle: low, approximately 25 degrees.
Warm orange-gold light temperature (3200K), cool blue shadows.
Cast shadows visible on ground plane, interior light spill from windows.
Dramatic contrast between sunlit and shadow faces.
Professional architectural photography aesthetic.
```

**Blue Hour Prompt**:
```english-prompt
Blue hour architectural visualization, twilight atmosphere.
Time: 6:45 AM / 7:15 PM. Sky: deep blue gradient (#1a1a3e to #4a6fa5).
Warm interior lights contrasting with cool exterior.
Artificial exterior lighting: ground-level uplighting, window glow.
City lights beginning to appear in background context.
Atmospheric, cinematic quality, contemplative mood.
```

**Night Scene Prompt**:
```english-prompt
Night architectural visualization, fully dark sky.
Artificial lighting dominant: office interior glow, landscape lighting, signage.
Reflective surfaces: wet pavement, glass curtain wall reflections.
Car headlights/taillights for life and movement.
Luminous atmosphere, city energy, modern urban context.
Accent lighting on architectural features, dramatic contrast.
```

**Overcast Day Prompt**:
```english-prompt
Overcast daylight architectural visualization.
Soft diffused lighting, minimal shadows, even illumination.
Sky: neutral gray gradient, no harsh contrasts.
Ideal for showing material qualities and spatial relationships.
Professional, technical presentation aesthetic.
Muted color palette, architectural clarity prioritized.
```

---

## Phase 4: Composition Guidelines

### 4.1 Setting the Scene

| Element | Description | Purpose |
|---------|-------------|---------|
| Foreground | Entry plaza, landscape buffer | Scale reference, visual anchor |
| Midground | Main building massing | Primary subject, focal point |
| Background | Context buildings, skyline | Urban context, depth |
| Sky | Atmosphere selection | Mood, time of day |
| Ground plane | Paved surfaces, planting | Grounding, environmental |

### 4.2 Human Scale References

Include contextual elements for scale:

- Human figures (silhouettes or detailed)
- Vehicles (cars, buses)
- Street furniture
- Trees and planting (verified heights)
- Adjacent buildings (known scale)

### 4.3 Environmental Context

```
Context Elements by Setting:
- Urban Core: tall surrounding buildings, streets, plazas
- Suburban: lower context, parking, landscape buffers
- Waterfront: sea/lake views, promenades, boats
- Parkland: mature trees, open space, minimal context
- Industrial: warehouses, infrastructure, grit
```

---

## Complete Working Examples

### Example 1: Mixed-Use Tower Complex

**Input Analysis**:
```
Rhino model with color-coded massing:
- Dark blue vertical towers (2 towers): Residential
- Light blue horizontal bands: Office floors
- Green ground level: Retail/public amenities
- Yellow accent at base: Main entry canopy
- Void/courtyard: Landscaped plaza
Building type: Podium + Twin Towers
Height: 35 floors residential, 20 floors office
Setting: Urban downtown, waterfront proximity
```

**Generated Prompts**:

*Golden Hour Exterior*:
```english-prompt
Professional architectural visualization, 3/4 aerial perspective showing twin tower mixed-use development.
Two residential towers (dark blue massing) rising from shared office podium (light blue massing).
Ground floor retail activated with transparent glazing and canopy (yellow accent).
Central courtyard: landscaped plaza with mature trees, seating areas, water feature.
Urban context: surrounding glass curtain wall office towers, busy street level with cars and pedestrians.
Time: golden hour, 5:45 PM autumn, warm west-facing sunlight with long dramatic shadows.
Architectural style: contemporary international, aluminum and glass cladding system.
Materials: dark aluminum panels, clear glazing with blue tint, stone base, planted terraces.
Lighting: warm sunset illumination (3000K), interior office glow, dramatic shadow play.
Context: waterfront promenade visible in distance, boats on water.
Add: human figures at entry, street trees, contextual cars, atmospheric haze.
Photorealistic architectural rendering, professional presentation quality, 8K resolution.
```

*Night Scene*:
```english-prompt
Professional architectural visualization, night scene perspective of twin tower mixed-use complex.
Two residential towers illuminated: warm interior apartment lights, balcony downlights.
Office floors: illuminated workspaces with blue-white task lighting visible.
Retail base: warm shop lighting, illuminated signage, café spill light onto plaza.
Entry canopy: dramatic accent lighting, warm welcome glow.
Courtyard: subtle landscape lighting, soft shadows, intimate atmosphere.
Urban nightlife: distant city lights, moving car trails, ambient urban energy.
Reflective wet pavement, puddle reflections of building.
Time: 9:30 PM, clear autumn night, deep blue-black sky.
Style: contemporary international, luminous modern architecture.
Mood: vibrant yet intimate, urban sophistication, evening ambiance.
Photorealistic rendering, cinematic quality, dramatic contrast.
```

### Example 2: Cultural Institution

**Input Analysis**:
```
Rhino model with sculptural massing:
- White flowing forms: main exhibition halls
- Gray cantilevered volumes: galleries, reading rooms
- Large glazed apertures: natural light wells
- Landscaped berms: sculpture garden
- Entry: recessed portal, water feature
Building type: Museum/cultural center
Setting: Parkland campus
Form language: Organic, sculptural, light-focused
```

**Generated Prompts**:

*Overcast Day Material Study*:
```english-prompt
Professional architectural visualization, museum building in parkland setting.
Organic sculptural white forms: main exhibition halls, flowing rooflines.
Cantilevered gray concrete volumes: gallery spaces, reading rooms.
Large glazed apertures: clerestory windows, light wells flooding interiors.
Recessed entry portal: dramatic threshold, reflecting pool entry feature.
Surrounding: sculpted landscape berms, mature trees, sculpture garden with artworks.
Setting: contemporary art museum in natural parkland, campus context.
Time: overcast midday, soft diffused light, minimal shadows.
Architectural style: contemporary organic, sculptural concrete and glass.
Materials: white stucco, board-formed concrete, structural glass, water features.
Atmosphere: serene, contemplative, focused on natural light and form.
Add: sculptural artworks in garden, museum visitors, natural landscape.
Photorealistic rendering, professional architectural photography aesthetic.
```

*Dawn Aerial*:
```english-prompt
Professional architectural visualization, aerial dawn perspective of museum complex.
Organic sculptural building forms: pristine white against soft morning sky.
Distant mountains: layered blue-gray silhouette, atmospheric perspective.
Morning mist: subtle fog in valleys, ethereal quality.
Landscaped grounds: dew-covered grass, highlighted by early light.
Entry reflection pool: mirror-like water surface, perfect reflection.
Time: 6:15 AM, clear autumn dawn, soft pink-orange eastern glow.
Lighting: cool blue ambient (shadow side), warm sunrise highlights (east faces).
Atmosphere: peaceful, contemplative, spiritual quality.
Distant parkland: golf course, tree-lined paths, early morning joggers.
Mood: optimistic new day, architectural elegance, natural serenity.
Professional presentation rendering, dramatic yet refined.
```

### Example 3: Transit-Oriented Development

**Input Analysis**:
```
Rhino model showing:
- Linear brown massing: residential blocks
- Orange accent bands: amenity floors
- Ground-level transparent zone: transit station integration
- Public skybridge: connecting residential to transit
- Plaza: commuter gathering space
Building type: TOD mixed-use linear development
Setting: Urban transit corridor, adjacent rail station
```

**Generated Promrompt**:

*Street-Level Commuter Scene*:
```english-prompt
Professional architectural visualization, street-level perspective of transit-oriented development.
Linear residential blocks (brown brick massing) with orange accent amenity floors.
Ground level: fully transparent station integration, commuter flow visible.
Public plaza: gathering space with seating, transit information, food vendors.
Skybridge: connecting residential complex to elevated rail station above.
Setting: busy urban transit corridor, morning commuter rush.
Human activity: commuters with bags, cyclists, people waiting at station entrance.
Time: 8:30 AM, clear morning, bright but not harsh sunlight.
Architectural style: urban contemporary, brick and glass materiality.
Materials: warm brown brick, aluminum windows, orange accent panels, glass station canopy.
Urban life: street vendors, bike share station, transit signage, wayfinding elements.
Mood: energetic, convenient, modern urban living.
Add: bikes, commuter bags, morning sunlight on glass, transit maps.
Photorealistic architectural rendering, urban vitality, professional quality.
```

---

## Advanced Techniques

### 4.1 Material Specification

| Material | Visual Characteristics | Prompt Keywords |
|----------|----------------------|-----------------|
| Glass Curtain Wall | Reflections, transparency, depth | "reflective glazing", "curtain wall system" |
| Aluminum Panel | Metallic sheen, subtle reflections | "aluminum cladding", "metal panel system" |
| Brick | Warm texture, pattern, human scale | "brick cladding", "masonry pattern" |
| Concrete | Matte, textured, monolithic | "board-formed concrete", "exposed aggregate" |
| Stone | Natural variation, premium feel | "natural stone", "limestone cladding" |
| Wood | Warmth, organic, sustainable | "timber cladding", "wood screen" |
| Living Wall | Green, textured, sustainable | "planting facade", "green wall system" |

### 4.2 Seasonal Variations

**Spring/Summer**:
```english-prompt
Season: summer, vibrant greenery, full deciduous tree canopy.
Blooming plants: flowering shrubs, perennial borders.
Bright, fresh atmosphere, long days, warm temperatures implied.
Water features active, outdoor seating occupied.
```

**Autumn/Fall**:
```english-prompt
Season: autumn, deciduous trees with orange-red foliage.
Golden light quality, fallen leaves on ground.
Warm color palette, contemplative atmosphere.
Harvest season feeling, cozy urban ambiance.
```

**Winter**:
```english-prompt
Season: winter, deciduous trees without leaves, evergreens prominent.
Bare branches creating shadow patterns.
Cool blue-gray atmosphere, possible snow dusting.
Warm interior glow emphasized by contrast.
Holiday lighting optional, winter urban scene.
```

### 4.3 Special Lighting Effects

**Rooftop Garden at Dusk**:
```english-prompt
Rooftop terrace garden, dusk lighting.
Upper floors: golden interior light, outdoor terrace illumination.
Sky: deep blue-purple gradient, first stars visible.
City skyline: distant lights beginning to appear.
Atmosphere: romantic, private, urban oasis feeling.
Add: string lights, fire pits, outdoor furniture, terrace planters.
Mood: intimate gathering, sophisticated urban life.
```

**Atrium Interior with Skylight**:
```english-prompt
Interior atrium visualization, natural daylight from skylight above.
Central atrium space: planting, circulation bridges, natural light flooding.
Upper gallery levels visible, people on bridges.
Time: noon, clear day, direct sunlight through skylight creating light shaft.
Atmospheric particles: dust motes visible in light beam.
Materials: concrete, glass, steel, living plants.
Mood: magnificent interior space, connection to nature inside.
Professional interior architectural rendering.
```

---

## Quality Assurance Checklist

### Pre-Generation Verification
- [ ] Color zones identified and mapped to programs
- [ ] Building typology and massing relationships understood
- [ ] Context setting established (urban/suburban/landscape)
- [ ] Atmosphere option selected or multiple offered
- [ ] Perspective angle determined
- [ ] Scale references identified

### Prompt Quality Verification
- [ ] Building program accurately described
- [ ] Materials specified for each zone
- [ ] Lighting mood matches requested atmosphere
- [ ] Context elements included for grounding
- [ ] Human scale references added
- [ ] Camera/view specifications included
- [ ] Resolution and quality standards specified

### Post-Generation Review
- [ ] Massing logic preserved in rendering
- [ ] Color zones translated to appropriate materials
- [ ] Atmosphere matches requested mood
- [ ] Scale appears correct with references
- [ ] Architectural style consistent throughout
- [ ] Professional presentation quality achieved

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-02 | Initial release |

---

**Author**: MiniMax Agent
**Specialization**: Architectural visualization, massing analysis, photorealistic rendering
