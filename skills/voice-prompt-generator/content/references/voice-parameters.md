# Voice Parameters Reference Guide

Complete parameter definitions and valid values for generating professional voice prompts.

## Voice Gender

| Value | Description |
|-------|-------------|
| Male | Adult male voice |
| Female | Adult female voice |
| Neutral | Gender-neutral voice |
| Boy | Young male child |
| Girl | Young female child |

## Age Ranges

| Value | Approximate Age | Characteristics |
|-------|-----------------|----------------|
| Child | 5-12 | Higher pitch, innocent tone |
| Teen | 13-19 | Transitional voice, youthful energy |
| Young Adult | 20-35 | Vibrant, energetic |
| Middle-aged | 36-55 | Mature, balanced |
| Senior | 55+ | Weathered, wise, sometimes raspy |

## Emotional Tones

| Value | Description | Use Cases |
|-------|-------------|-----------|
| Warm | Friendly, approachable | Narration,客服 |
| Cold | Distant, professional | News, formal |
| Enthusiastic | Excited, energetic | Commercials, promos |
| Calm | Peaceful, soothing | Meditation, audiobooks |
| Sad | Melancholic, somber | Dramatic content |
| Cheerful | Happy, bright | Children's content |
| Authoritative | Commanding, confident | Training, corporate |
| Playful | Fun, mischievous | Entertainment, games |

## Speaking Styles

| Style | Characteristics |
|-------|-----------------|
| Formal | Precise, professional language |
| Casual | Relaxed, conversational |
| Broadcast | Clear, measured delivery |
| Conversational | Natural, spontaneous |
| Theatrical | Dramatic, expressive |
| Whisper | Soft, intimate |
| Read-aloud | Storytelling, animated |
| Report | Factual, neutral |

## Accents & Regional Features

### English Accents
- **RP (Received Pronunciation)**: Standard British
- **General American**: Standard US
- **Southern US**: Warm, drawled vowels
- **Australian**: Rising intonation
- **Irish**: Musical, rhythmic
- **Scottish**: Rolled Rs, distinctive vowels
- **Indian English**: Rhythmic, clear consonants

### Chinese Accents
- **Standard Mandarin**: Beijing-based pronunciation
- **Taiwanese Mandarin**: Soft, flowing
- **Cantonese**: Distinct tonal patterns
- **Regional accents**: Shanghai, Sichuan,东北, etc.

## Physical Voice Traits

| Trait | Description | Effect |
|-------|-------------|--------|
| Breathiness | Air passing through vocal cords | Intimate, vulnerable |
| Raspiness | Rough, textured sound | Character, age |
| Nasality | Sound resonating in nasal cavity | Regional markers |
| Brightness | High-frequency emphasis | Clarity, energy |
| Darkness | Low-frequency emphasis | Warmth, depth |
| Clarity | Distinct consonant sounds | Understandability |

## Technical Parameters

### Pitch Level
```
Very Low: ~100Hz average (male, bass)
Low: ~150Hz (male baritone)
Normal: ~200Hz (typical adult)
High: ~300Hz (female alto)
Very High: ~400Hz+ (female soprano)
```

### Speed
```
Very Slow: 80-100 words/minute
Slow: 100-120 words/minute
Normal: 120-150 words/minute
Fast: 150-180 words/minute
Very Fast: 180-200 words/minute
```

### Volume/Dynamic Range
```
Soft: Quiet, intimate
Normal: Standard speaking volume
Loud: Projected, emphatic
Wide Dynamic: Range from soft to loud
```

## Platform-Specific Formats

### Qwen-TTS (Alibaba Cloud)
```
Natural language description:
"A warm, middle-aged female voice with a slight British accent, professional yet approachable news anchor style."
```

### ElevenLabs
```
Character traits in JSON format:
{
  "description": "Professional female news anchor",
  "labels": {
    "age": "middle-aged",
    "gender": "female",
    "accent": "British",
    "tone": "authoritative"
  }
}
```

### Generic TTS Format
```
VOICE_PROMPT:
  gender: female
  age_range: 35-45
  pitch: normal-high
  speed: normal
  emotion: authoritative, professional
  style: broadcast
  accent: British RP
  traits: clear, confident, warm
```

## Common Voice Combinations

| Application | Recommended Settings |
|-------------|---------------------|
| Audiobook (Fantasy) | Warm, theatrical, expressive, varied pacing |
| Audiobook (Non-fiction) | Calm, clear, steady pace |
| IVR/Phone System | Neutral, clear, moderate speed |
| Corporate Training | Professional, authoritative, steady |
| Children's Content | Cheerful, warm, animated, age-appropriate |
| Video Game (NPC) | Characterful, distinct personality |
| Podcast Intro | Energetic, engaging, memorable |
| Meditation Guide | Calm, peaceful, slow, breathy |
| News Broadcast | Authoritative, neutral, clear |
| ASMR | Soft, whisper, intimate, breathy |
