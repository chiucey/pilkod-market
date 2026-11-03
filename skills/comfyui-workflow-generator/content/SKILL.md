---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5777e734d4833b3ca8497ac231a5ea8a
    PropagateID: 5777e734d4833b3ca8497ac231a5ea8a
    ReservedCode1: 30460221009f1457e3d217f7b9cb43ae03e2777187f3da2860bfd59b51963c190f51ed162e022100dd17cb842d9863fb77fc124256db6f6661abdef191862b7c8feca5db618e0a7f
    ReservedCode2: 304402200812fc2ccc6d4bc24df209674622080ab7c77cbb31d29879e356a344cb9c2e5c0220662cc9cabe7f83e0c0e816a135cb8b88764340b87e71ef005834254a47d6e743
description: Generate ComfyUI workflows from natural language descriptions. Use when users ask to create AI image/video workflows, generate Stable Diffusion pipelines, build ComfyUI automation, design image generation workflows, or need workflow JSON files for ComfyUI. Supports text-to-image, image-to-image, video generation, ControlNet pipelines, LoRA integration, and more.
name: comfyui-workflow-generator
---

# ComfyUI Workflow Generator

A powerful skill that generates ComfyUI workflow JSON files from natural language descriptions. Perfect for creating AI image generation pipelines, video workflows, and custom automation.

## Features

- **Natural Language Interface**: Describe your workflow needs in plain English
- **Template Library**: Pre-built templates for common workflows
- **Multi-Modal Support**: Image generation, video generation, style transfer
- **Advanced Controls**: ControlNet, LoRA, IP-Adapter integration
- **Validation Engine**: Ensures generated workflows are valid and runnable
- **Plugin Awareness**: Detects and suggests required ComfyUI extensions

## Supported Workflow Types

### Image Generation
- Text-to-Image (Txt2Img)
- Image-to-Image (Img2Img)
- Inpainting/Outpainting
- Image Upscaling/Enhancement

### Video Generation
- AnimateDiff Text-to-Video
- Video Style Transfer
- Video Upscaling with RIFE
- IP-Adapter Character Consistent Video
- Multi-ControlNet Video Generation

### Advanced Pipelines
- ControlNet Pipelines (Canny, OpenPose, Depth, etc.)
- LoRA Integration
- IP-Adapter Face/Character Consistency
- Custom Node Workflows

## Usage Examples

### Basic Image Generation
```
Generate a workflow for creating cyberpunk-style cityscapes
```

### Video with ControlNet
```
Create a workflow that converts real video to anime style using ControlNet
```

### Character Consistent Video
```
Build a workflow to generate videos with consistent character from reference image
```

### Image Enhancement
```
Generate an upscaling and enhancement pipeline for old photos
```

## Workflow Structure

Each generated workflow includes:
- **Node Connections**: Proper input/output linking between nodes
- **Default Parameters**: Sensible defaults for immediate use
- **Position Layout**: Visual arrangement for ComfyUI canvas
- **Metadata**: Workflow title and description

## Node Library

The skill includes a comprehensive node library covering:

### Core Nodes
- CheckpointLoaderSimple, CLIPTextEncode, EmptyLatentImage
- KSampler, VAEDecode, VAEEncode, LoadImage/SaveImage

### Video Nodes (VideoHelperSuite)
- VHS_LoadVideo, VHS_VideoCombine, VHS_LoadAudio, VHS_SplitVideo

### Motion Generation
- AnimateDiffLoaderV2, AnimateDiffLoraLoader

### ControlNet Nodes
- ControlNetLoader, ControlNetApply
- Canny, OpenPosePreprocessor, DepthMapPreprocessor

### Enhancement Nodes
- RIFE_VFI (Frame Interpolation)
- UpscaleModelLoader, ImageUpscaleWithModel

### IP-Adapter Nodes
- CLIPVisionLoader, IPAdapterLoader, IPAdapterApply

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| user_requirement | string | required | Natural language description of desired workflow |
| workflow_format | string | "ui" | Output format: "ui" (visual) or "api" (compact) |
| base_model | string | "sd1.5" | Base model type: "sd1.5" or "sdxl" |
| max_resolution | int | 1024 | Maximum resolution dimension |
| batch_size | int | 1 | Number of images to generate |

## Output Format

The skill generates a complete ComfyUI workflow JSON that can be:
1. Saved as `.json` file
2. Dragged directly into ComfyUI canvas
3. Modified with custom parameters
4. Used with ComfyUI Manager

## Required Plugins

Depending on the workflow type, users may need:
- ComfyUI-VideoHelperSuite (video workflows)
- ComfyUI-AnimateDiff-Evolved (motion generation)
- ComfyUI-Advanced-ControlNet (ControlNet)
- ComfyUI-ControlNet (preprocessors)
- ComfyUI-RIFE (frame interpolation)
- ComfyUI_IPAdapter_plus (character consistency)

## Tips for Best Results

1. **Be Specific**: Include style keywords, quality modifiers
2. **Mention Hardware**: 8GB+ VRAM can handle most workflows
3. **Check Plugins**: The skill will list required plugins
4. **Start Simple**: Begin with basic workflows before advanced features
5. **Iterate**: Modify generated workflows to suit your needs

## Technical Notes

- Generated workflows use standard ComfyUI node types
- All node class_types match official ComfyUI documentation
- Workflows include automatic validation before output
- Position coordinates are auto-calculated for visual layout
