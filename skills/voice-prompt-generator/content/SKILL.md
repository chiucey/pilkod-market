---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 565eb5b7e75ec20f4307183755ca0ee6
    PropagateID: 565eb5b7e75ec20f4307183755ca0ee6
    ReservedCode1: 304502205f28d33886daa584a08106396005c46579af0da376ee57072eb78f5b1ab4d64402210099786c03615b13afd9f65c9d5be55f7d75ac507e17a736ea46a1a67d3c341309
    ReservedCode2: 3046022100d39f106553c61b9ee5b0d0f17cb3ef8e79adc7a23678de8ffb839b24c974801c022100d977e82f26d02dda18eb20f10f48d28633b47daf4ebc72fa9ee609c3fdbc0d65
description: Generate professional AI voice/timbre description prompts from natural language. Use when users ask to create voice synthesis prompts, customize AI voices, generate voice cloning descriptions, or convert voice descriptions into TTS-compatible format. Supports Chinese and English voice description conversion.
name: voice-prompt-generator
---

# Voice Prompt Generator

Generate professional AI voice description prompts from natural language descriptions. Transform intuitive voice descriptions into structured prompts compatible with major TTS (Text-to-Speech) platforms.

## Core Workflow

### Step 1: Parse User Description

Analyze the user's voice description and extract key attributes:

- **Gender**: Male, Female, Neutral
- **Age Range**: Child, Teen, Young Adult, Middle-aged, Senior
- **Emotional Tone**: Warm, Cold, Enthusiastic, Calm, Sad, Cheerful
- **Speaking Style**: Formal, Casual, Broadcast, Conversational
- **Regional Accent**: Standard, Regional, Foreign accent
- **Physical Traits**: Breathiness, Raspiness, Clarity

### Step 2: Build Structured Prompt

Transform extracted attributes into a professional voice prompt using this template:

```
[Gender] voice, [Age] years old, [Emotional tone] personality,
[Speaking style], [Accent] accent, [Additional traits]
```

### Step 3: Add Technical Parameters (Optional)

Supplement with technical parameters for fine-tuning:

- **Pitch**: Very Low / Low / Normal / High / Very High
- **Speed**: Slow / Normal / Fast / Very Fast
- **Volume**: Soft / Normal / Loud
- **Clarity**: Muffled / Normal / Crystal Clear
- **Breathiness**: Minimal / Moderate / Breathy

### Step 4: Format for Target Platform

Adjust output format based on target TTS platform:

| Platform | Format Style |
|----------|-------------|
| Qwen-TTS | Natural language description |
| PromptTTS | Structured label-based |
| ElevenLabs | Character trait list |
| Generic | Flexible structured format |

## Input Examples

**Example 1 - Chinese Input:**
```
User: "一个温柔的年轻女声，说话带点磁性，适合有声书"
```

**Generated Output:**
```
A warm, young adult female voice with slight huskiness, gentle and nurturing personality, suitable for audiobook narration with a soothing storytelling style.
```

**Example 2 - English Input:**
```
User: "A authoritative middle-aged male voice, British accent, news broadcast style"
```

**Generated Output:**
```
Middle-aged male voice, authoritative and professional, RP British accent, news broadcast speaking style, clear enunciation, confident delivery.
```

## Output Format

Always provide output in the following structure:

```
## Generated Voice Prompt

**Structured Prompt:**
[Primary voice description]

**Technical Parameters:**
- Gender: [value]
- Age: [value]
- Pitch: [value]
- Speed: [value]
- Emotion: [value]
- Style: [value]
- Accent: [value]

**Platform-Ready Format:**
[Formatted for selected platform]
```

## Parameter Reference

See `references/voice-parameters.md` for complete parameter definitions and valid values.

## Quality Guidelines

1. **Preserve User Intent**: Maintain the core feeling described by the user
2. **Add Professional Context**: Enhance with acoustic/technical terms
3. **Multiple Options**: Offer 2-3 variations when ambiguous
4. **Platform Awareness**: Consider target TTS system capabilities
5. **Cultural Sensitivity**: Respect regional accent descriptions
