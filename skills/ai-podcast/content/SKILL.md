---
name: ai-podcast
description: Use when users ask to create, generate, or produce AI podcasts. Handles text-to-speech, dialogue generation, and podcast content creation with customizable voice timbres. Triggers include phrases like "create a podcast", "generate AI voice", "make a podcast episode", "AI podcast generator", "text to speech podcast", "configure voice", "voice settings".
---

# AI Podcast Generator

An expert skill for creating AI-powered podcasts with synthesized voices, dialogue scripts, and audio production.

## Core Capabilities

- **Text-to-Speech Generation**: Convert text scripts into natural-sounding podcast audio
- **Dialogue Podcast Creation**: Generate multi-speaker conversations and interviews
- **Podcast Content Planning**: Structure episodes with intro, main content, and outro
- **Voice Configuration**: Select and configure voice timbres for different speakers
- **Multi-Language Support**: Generate podcasts in English, Chinese, Japanese, Korean, Spanish, and more

## Voice Configuration System

### Voice Selection Process

1. **Identify Speaker Roles**: Determine the number and type of speakers needed
2. **Match Voice to Persona**: Select appropriate voice timbre based on character traits
3. **Configure Voice Parameters**: Adjust speed, pitch, volume, and emotion
4. **Test Voice Compatibility**: Ensure voices work well together in dialogue

### Voice Parameters

| Parameter | Range | Description | Default |
|-----------|-------|-------------|---------|
| `voice` | Voice ID | Select from available voice library | System default |
| `speed` | 0.5 - 2.0 | Speech rate multiplier | 1.0 |
| `pitch` | -12 to 12 | Voice pitch adjustment | 0 |
| `volume` | 0.0 - 10.0 | Audio volume level | 1.0 |
| `emotion` | happy/sad/angry/fearful/disgusted/surprised/neutral | Voice emotional tone | neutral |

### Popular Voice Combinations

**For Interview/Discussion Podcasts:**
- Host: `English_Trustworth_Man` or `Chinese (Mandarin)_Reliable_Executive`
- Guest: `English_Compelling_lady1` or `Chinese (Mandarin)_Wise_Women`

**For Educational Content:**
- Teacher: `English_CalmWoman` or `Chinese (Mandarin)_Gentle_Senior`
- Student: `English_PlayfulGirl` or `Chinese (Mandarin)_Warm_Girl`

**For Storytelling:**
- Narrator: `English_CaptivatingStoryteller` or `Japanese_LoyalKnight`
- Character: Context-dependent selection from voice library

## Workflow

### 1. Content Planning

When creating a podcast:
- Determine the topic, target audience, and episode length
- Structure content with clear segments (intro, main topics, conclusion)
- Define speaker roles for multi-voice podcasts
- Select appropriate voice combinations

### 2. Script Generation

Create engaging podcast scripts:
- Use conversational tone and natural speech patterns
- Include transitions and segways between topics
- Add placeholder markers with voice configuration:

```
[Speaker:voice_id, speed=1.0, emotion=neutral]
Hello everyone, welcome to the show.
[/Speaker]
```

### 3. Audio Production

Use available tools to generate audio:
- Select appropriate voice for each speaker
- Configure voice parameters as needed
- Export in standard audio formats (MP3)

### 4. Enhancement Options

- Add background music or sound effects
- Include chapter markers
- Generate show notes and transcripts

## Tools Available

- `get_voice_list`: List all available AI voices with descriptions
- `gen_audios`: Generate speech with custom voice parameters
- `batch_text_to_audio`: Generate multiple audio segments in parallel
- `audios_understand`: Analyze audio content and quality

## Example Use Cases

1. **Educational Podcast**: Create a two-voice explanation with teacher and student characters
2. **News Recap**: Generate a single-voice summary with professional announcer voice
3. **Interview Simulation**: Create dialogue between host and guest with distinct voices
4. **Tutorial Series**: Produce step-by-step content with patient, clear voice
5. **Storytelling**: Generate narrative content with expressive storyteller voice

## Best Practices

- Keep scripts conversational and easy to speak
- Use short sentences for better pacing
- Include natural pause markers like `[pause]` or `[music]`
- Provide context for specialized terms when needed
- Match voice timbre to content type (serious for news, warm for interviews)
- Test voice settings before generating full episodes
