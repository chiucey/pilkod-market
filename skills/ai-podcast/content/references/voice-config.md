# Voice Configuration Reference

## Complete Voice Library

### English Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `English_expressive_narrator` | Expressive Narrator | Storytelling, audiobooks |
| `English_radiant_girl` | Radiant Girl | Youth content, casual topics |
| `English_magnetic_voiced_man` | Magnetic-voiced Male | Charismatic presentations |
| `English_compelling_lady1` | Compelling Lady | Persuasive content, interviews |
| `English_Aussie_Bloke` | Aussie Bloke | Australian dialect content |
| `English_captivating_female1` | Captivating Female | Engaging narratives |
| `English_Upbeat_Woman` | Upbeat Woman | Energetic, positive content |
| `English_Trustworth_Man` | Trustworthy Man | News, professional content |
| `English_CalmWoman` | Calm Woman | Meditation, educational |
| `English_PlayfulGirl` | Playful Girl | Children's content, casual |
| `English_ManWithDeepVoice` | Man With Deep Voice | Authority, deep discussions |
| `English_Wiselady` | Wise Lady | Advice, life tips |
| `English_CaptivatingStoryteller` | Captivating Storyteller | Stories, narratives |
| `English_Comedian` | Comedian | Humor, entertainment |
| `English_BossyLeader` | Bossy Leader | Commanding, directive |
| `English_AnimeCharacter` | Female Narrator | Anime-style narration |

### Chinese (Mandarin) Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `Chinese (Mandarin)_Reliable_Executive` | Reliable Executive | Business, news |
| `Chinese (Mandarin)_News_Anchor` | News Anchor | News broadcasts |
| `Chinese (Mandarin)_Mature_Woman` | Mature Woman | Experienced perspectives |
| `Chinese (Mandarin)_Kind-hearted_Antie` | Kind-hearted Antie | Warm, friendly content |
| `Chinese (Mandarin)_HK_Flight_Attendant` | HK Flight Attendant | Professional service |
| `Chinese (Mandarin)_Gentleman` | Gentleman | Formal, respectful |
| `Chinese (Mandarin)_Warm_Bestie` | Warm Bestie | Casual, friendly |
| `Chinese (Mandarin)_Wise_Women` | Wise Women | Advice columns |
| `Chinese (Mandarin)_Radio_Host` | Radio Host | Entertainment, talk shows |
| `Chinese (Mandarin)_Lyrical_Voice` | Lyrical Voice | Poetry, music related |
| `Chinese (Mandarin)_Cute_Spirit` | Cute Spirit | Playful, light content |

### Cantonese Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `Cantonese_ProfessionalHost（F)` | Professional Female Host | Formal presentations |
| `Cantonese_ProfessionalHost（M)` | Professional Male Host | Formal presentations |
| `Cantonese_GentleLady` | Gentle Lady | Calm, soothing content |
| `Cantonese_PlayfulMan` | Playful Man | Casual entertainment |
| `Cantonese_CuteGirl` | Cute Girl | Youth content |

### Japanese Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `Japanese_LoyalKnight` | Loyal Knight | Heroic narratives |
| `Japanese_DecisivePrincess` | Decisive Princess | Strong female leads |
| `Japanese_GentleButler` | Gentle Butler | Polished, refined |
| `Japanese_KindLady` | Kind Lady | Warm, caring |
| `Japanese_SeriousCommander` | Serious Commander | Military, authority |
| `Japanese_ColdQueen` | Cold Queen | Dramatic, intense |
| `Japanese_OptimisticYouth` | Optimistic Youth | Youthful energy |

### Korean Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `Korean_CalmGentleman` | Calm Gentleman | Professional |
| `Korean_GentleWoman` | Gentle Woman | Soft, caring |
| `Korean_CharmingElderSister` | Charming Elder Sister | Friendly advice |
| `Korean_BraveFemaleWarrior` | Brave Female Warrior | Action, heroism |
| `Korean_SweetGirl` | Sweet Girl | Light, romantic |
| `Korean_ColdGirl` | Cold Girl | Dramatic, tsundere |
| `Korean_WiseTeacher` | Wise Teacher | Educational |

### Spanish Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `Spanish_Narrator` | Narrator | General narration |
| `Spanish_WiseScholar` | Wise Scholar | Educational |
| `Spanish_CaptivatingStoryteller` | Captivating Storyteller | Stories |
| `Spanish_Comedian` | Comedian | Entertainment |
| `Spanish_SantaClaus` | Santa Claus | Holiday content |
| `Spanish_BossyLeader` | Bossy Leader | Directive content |

### Portuguese Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `Portuguese_Narrator` | Narrator | General narration |
| `Portuguese_Comedian` | Comedian | Humor |
| `Portuguese_Godfather` | Godfather | Authoritative |
| `Portuguese_Steadymentor` | Steady Mentor | Guidance |

### French Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `French_Male_Speech_New` | Level-Headed Man | Balanced, calm |
| `French_Female_News Anchor` | Patient Female Presenter | News, presentations |
| `French_MovieLeadFemale` | Movie Lead Female | Dramatic narration |

### Other Languages

| Language | Voice ID | Description |
|----------|----------|-------------|
| German | `German_FriendlyMan` | Friendly Man |
| German | `German_SweetLady` | Sweet Lady |
| Russian | `Russian_ReliableMan` | Reliable Man |
| Italian | `Italian_Narrator` | Narrator |
| Hindi | `hindi_male_1_v2` | Trustworthy Advisor |
| Hindi | `hindi_female_1_v2` | News Anchor |

## Voice Parameter Configuration

### Speed Settings

| Speed Value | Effect | Use Case |
|-------------|--------|----------|
| 0.5 | Half speed, slow | Educational, language learning |
| 0.75 | Slightly slower | Clear explanations |
| 1.0 | Normal speed | Standard podcasts |
| 1.25 | Slightly faster | Energetic content |
| 1.5 | Fast pace | Summary, highlights |
| 2.0 | Double speed | Time-compressed |

### Pitch Settings

| Pitch Value | Effect |
|-------------|--------|
| -12 | Very low pitch |
| -6 | Lower pitch |
| 0 | Natural pitch |
| +6 | Higher pitch |
| +12 | Very high pitch |

### Emotion Settings

| Emotion | Description | Best For |
|---------|-------------|----------|
| `happy` | Positive, cheerful tone | Celebrations, good news |
| `sad` | Melancholic, somber | Serious topics, condolences |
| `angry` | Frustrated, intense | Dramatic moments |
| `fearful` | Anxious, worried | Suspense, concern |
| `disgusted` | Disapproval | Criticism, reviews |
| `surprised` | Astonished | Reveals, twists |
| `neutral` | Balanced, calm | General content |

## Configuration Examples

### Interview Podcast
```json
{
  "host": {
    "voice": "English_Trustworth_Man",
    "speed": 1.0,
    "pitch": 0,
    "emotion": "neutral"
  },
  "guest": {
    "voice": "English_Compelling_lady1",
    "speed": 1.0,
    "pitch": 0,
    "emotion": "neutral"
  }
}
```

### News Broadcast
```json
{
  "anchor": {
    "voice": "Chinese (Mandarin)_News_Anchor",
    "speed": 0.9,
    "pitch": 0,
    "emotion": "neutral"
  }
}
```

### Storytelling
```json
{
  "narrator": {
    "voice": "English_CaptivatingStoryteller",
    "speed": 1.1,
    "pitch": 2,
    "emotion": "surprised"
  }
}
```

### Educational
```json
{
  "teacher": {
    "voice": "English_CalmWoman",
    "speed": 0.85,
    "pitch": 0,
    "emotion": "neutral"
  },
  "student": {
    "voice": "English_PlayfulGirl",
    "speed": 1.0,
    "pitch": 4,
    "emotion": "happy"
  }
}
```
