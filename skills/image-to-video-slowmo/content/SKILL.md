---
name: image-to-video-slowmo
description: Convert static images into 5-second slow-motion videos. Use when users want to animate images, convert images to video, or make photos come alive. Supports landscapes, objects, animals, people, maintaining object consistency and physical laws.
---

# Image to Slow-Motion Video Skill

Convert any static image into a smooth 5-second slow-motion video, maintaining object consistency and physical world laws.

## Core Capabilities

- **Input**: Any type of static image (JPG, PNG, WebP, etc.)
- **Output**: 5-second MP4 slow-motion video
- **Features**:
  - Maintains object consistency from original image
  - Follows physical world motion laws
  - Slow-motion presentation with moderate motion amplitude
  - Applicable scenes: landscapes, objects, animals, people, etc.

## Execution Workflow

### Step 1: Receive Image

Check for user-provided images:
- Check uploaded files in `user_input_files/` directory
- Check image URLs in user messages
- Validate image format and accessibility

### Step 2: Generate Video

Use `batch_image_to_video` tool to convert image to video:

```
Tool parameters:
- count: 1 (single video)
- image_file_list: [image file path]
- output_file_list: ["imgs/output_video.mp4"]
- prompt_list: ["Natural smooth slow motion, gentle breeze, flowing light and shadows, following physical laws"]
- reference_type_list: ["first_frame"]
- duration_list: [6]
- resolution_list: ["768P"]
```

### Step 3: Output Result

Display the generated video file to the user and provide download link.

## Supported Image Types

| Type | Examples | Motion Description |
|------|----------|-------------------|
| Landscape | Mountains, oceans, cities | Gentle breeze, flowing clouds, changing light |
| Objects | Products, still life, buildings | Slight swaying, changing reflections |
| Animals | Cats, dogs, birds, marine life | Breathing, subtle movements, natural behaviors |
| People | Portraits, actions, expressions | Breathing rhythm, hair floating, subtle expression changes |

## Output Specifications

- **Video Duration**: 5 seconds
- **Resolution**: 768P (standard) or 1080P (optional)
- **Format**: MP4
- **Motion Style**: Slow motion, smooth and natural

## Error Handling

- Unsupported image format: Prompt user to convert format
- Image not accessible: Prompt user to provide valid image file
- Video generation failed: Provide alternative or retry suggestions

## Usage Examples

**Example 1: Landscape Image**
```
User: Make this landscape photo come alive
Skill: Receive image → Generate video with waves lapping, breeze blowing, clouds slowly moving
```

**Example 2: Animal Image**
```
User: Animate this cat photo
Skill: Receive image → Generate video with cat blinking, ears slightly moving, breathing
```

**Example 3: People Image**
```
User: Generate a dynamic video of this person
Skill: Receive image → Generate video with hair gently floating, subtle expression changes, natural breathing
```
