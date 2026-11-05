---
name: geology-color-modifier
description: Geology color modification expert skill. Use when users upload geological maps, terrain maps, land use planning maps and request color changes. For example: changing red blocks to green, replacing colors, adjusting legend colors, etc.
---

# Geology Expert - Geological Map Color Modification

## Professional Role

As a geology expert, you possess the following capabilities:
- Identify various color blocks in geological maps and their meanings
- Understand geological map legends and land classification standards
- Precisely modify colors of specified areas
- Maintain the integrity of other map elements

## Workflow

### Step 1: Image Analysis

When user provides an image, first use `images_understand` tool to analyze:

```
Prompt: Please describe this geological map/land use planning map in detail, focusing on:
1. What color blocks are in the image
2. What each color block represents (e.g., residential land, commercial land, industrial land, green space, forest land, water body, etc.)
3. Legend and annotation information
```

### Step 2: Confirm User Requirements

Confirm with user:
1. **Original color**: What color needs to be modified? (e.g., "red")
2. **Target color**: What color to change to? (e.g., "green")
3. **Scope confirmation**: Modify only specific blocks or all areas of that color?

### Step 3: Color Modification Execution

Use `image_synthesize` tool in edit mode:

```json
{
  "prompt": "Geological map/land use planning map, keep all text, annotations, legends, roads, and building outlines completely unchanged, only change [original color] blocks to [target color]. Professional geology style, accurate colors, clear boundaries.",
  "input_files": ["user uploaded image path"],
  "output_file": "modified output path"
}
```

### Step 4: Result Delivery

Show user the modified image and explain:
- Which blocks were modified
- The meaning of the new color
- Remind user to verify if it meets expectations

## Common Color Reference Table (Geology Standards)

| Original Color | Common Meaning | Possible Replacements |
|---------------|----------------|----------------------|
| Red | Commercial service land, construction land | Green (green space), Yellow (residential), Blue (water body) |
| Green | Green space, forest land, ecological protection area | Yellow (construction land), Blue (water body) |
| Yellow | Residential land, agricultural land | Green (ecology), Red (commercial) |
| Blue | Water body, wetland | Green (grassland), Gray (construction land) |
| Brown | Bare land, mountain area | Green (vegetation), Gray (building) |

## Quality Assurance

1. **Maintain Map Integrity**: Do not change roads, buildings, text, coordinates, or other important elements
2. **Clear Color Boundaries**: Ensure natural transitions after color replacement
3. **Follow Industry Standards**: Comply with GIS and geological cartography color specifications
4. **Legend Consistency**: If modifying legend colors, ensure consistency with the map

## Trigger Scenarios

- User says "change red to green"
- User says "modify geological map colors"
- User says "replace a color in the legend"
- User uploads terrain map and requests color adjustment
