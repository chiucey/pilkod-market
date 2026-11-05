# PPT and Video Generation Skill - Workflow Guide

## Complete Workflow Details

### Phase 1: Content Planning and Image Generation

#### Step 1: Collect User Input

Collect the following information:
- **PPT Topic**: Core topic description
- **Outline Points**: Initial content structure
- **Page Count**: Expected number of slides
- **Video Duration**: Total presentation video length
- **Style Preference** (optional): Business/Tech/Education/Creative
- **Special Requirements** (optional): Brand colors, Logo, etc.

#### Step 2: Web Search and Information Organization

Use search tools to collect:
- Latest news related to the topic
- Authoritative data reports
- Industry case studies
- Trend forecasts

Organize output format:
```
# [Topic] Research Report

## Key Data Points
- Data 1: xxx
- Data 2: xxx

## Key Trends
1. Trend 1
2. Trend 2

## Case References
- Case A: xxx
- Case B: xxx
```

#### Step 3: PPT Page Content Planning

Allocate content based on page count:
| Page | Type | Content Points | Visual Elements |
|------|------|----------------|-----------------|
| 1 | Cover | Topic, Subtitle | Large title background |
| 2 | TOC | Chapter overview | Icon list |
| 3 | Introduction | Background | Data charts |
| ... | ... | ... | ... |
| N | Closing | Summary & CTA | Contact info |

#### Step 4: Generate PPT Images

Call image generation tool:
```python
requests = []
for i, slide in enumerate(slides):
    requests.append({
        "prompt": f"Professional presentation slide about {slide['topic']}, {slide['style']} style, modern design, clean layout, data visualization",
        "output_file": f"slide_{i+1:02d}.png",
        "aspect_ratio": "16:9"
    })
```

### Phase 2: PPT File Generation

#### Step 5: Assemble PPT

Use pptx-generator skill:
- Import generated images
- Add titles and text
- Apply unified styles
- Generate PPTX file

### Phase 3: Presentation Video Generation

#### Step 6: Generate Script

Generate corresponding speech content for each page:
- Language style: Professional but accessible
- Duration control: Match page display time
- Key points: Align with visual elements

#### Step 7: Audio Generation and Confirmation

**Generate first page audio first**:
```python
audio_requests = [{
    "text": first_slide_script,
    "output_file": "audio_01.mp3",
    "voice": "professional_male",
    "speed": 1.0,
    "emotion": "neutral"
}]
```

**Wait for user confirmation**:
- Play audio
- Collect feedback
- Adjust parameters or regenerate

#### Step 8: Batch Audio Generation

After confirming first page effect, generate in sequence:
- Page 2 audio
- Page 3 audio
- ...
- Page N audio

#### Step 9: Video Synthesis

Integrate images with audio:
```python
video_requests = []
for i in range(slide_count):
    video_requests.append({
        "prompt": f"Professional presentation slide transition, {slide_topics[i]}",
        "image_file": f"slide_{i+1:02d}.png",
        "output_file": f"video_{i+1:02d}.mp4",
        "duration": audio_duration[i]
    })
```

## Quality Checklist

### Content Quality
- [ ] Topic is prominent, information is accurate
- [ ] Logic is clear, structure is well-organized
- [ ] Data sources are reliable
- [ ] No typos or grammatical errors

### Visual Quality
- [ ] High image resolution (recommended 1920x1080)
- [ ] Unified style, coordinated colors
- [ ] Good text readability
- [ ] No copyright-infringing materials

### Audio Quality
- [ ] Clear pronunciation
- [ ] Appropriate speaking speed
- [ ] Proper emotional expression
- [ ] No background noise

### Video Quality
- [ ] Audio and video synchronized
- [ ] Smooth transitions
- [ ] Good final format compatibility (MP4)
