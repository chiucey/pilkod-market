# Screenplay Format Specification

## Scene Header Format

```
### X-X DAY/NIGHT INT/EXT Location

**Characters:** Character Name (Character Role)
```

Example:
```
### 3-1 DAY EXT Ancient Street

**Characters:** Qin Jie (Jiang Zhen), Maid, Young Lord (Fei Yan), Attendant
```

## Action Description

- Use `△` symbol at the beginning
- Describe character actions, expressions, scene environment
- Keep concise and clear

Example:
```
△Busy ancient street, an ornate black horse pulling a delicate sedan slowly approaches.

△Young Lord wearing red dragon-embroidered robes, golden crown on head, riding black horse, arrogant expression.
```

## Dialogue Format

### Normal Dialogue
```
**Character**：（tone/state）：Dialogue content
```

Example:
```
**Young Lord**：（shouting）：Sister Zhen!!!
```

### Inner Monologue (OS)
```
**CharacterOS**：Inner monologue content
```

Example:
```
**Qin JieOS**：I will settle the original body's debts. But the most urgent matter is to quickly find news about the other three people.
```

### Voiceover (OV)
```
**Character**（OV）：Voiceover content
```

### Breaking Fourth Wall
```
**Character**（breaking fourth wall）：Dialogue content
```

Example:
```
**Young Lord**（breaking fourth wall）：Family, I finally found my family!
```

## Storyboard Format

### Shot List Table Header

| Shot # | Duration | Shot Type | Description | Dialogue/Voiceover | Notes |
|--------|----------|-----------|-------------|-------------------|-------|
| 1 | 3s | Close-up | Character expression | "Line..." | - |

### Shot Type Definitions

| Term | Description |
|------|-------------|
| Wide Shot | Full scene with all characters |
| Medium Shot | Character from knees up |
| Close-up | Character from waist up |
| Extreme Close-up | Character face or detail |

### Duration Format

Use seconds, e.g., `3s`

## Video Analysis Prompt Template

```
Please analyze every frame of this video in extreme detail, strictly following time sequence:

1) Specific visual content of each shot
2) Accurate character dialogue (complete transcription, do not add content not in the video)
3) Each action and expression change
4) Scene transition time points
5) Distinguish: dialogue, inner monologue (OS), voiceover (OV), or breaking fourth wall

Only record content that actually exists in the video. Do not add any speculation or content not in the source.
```
