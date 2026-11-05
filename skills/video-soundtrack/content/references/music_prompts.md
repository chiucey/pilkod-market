# MiniMax Music 2.6 提示词模板

## 音乐生成提示词结构

```
[情绪类型], [乐器配置], [节奏], [氛围], [时长], [特殊要求]
```

## 情绪类型提示词

### Suspenseful (悬疑)
```
A suspenseful orchestral track with strings, low brass, and tension-building 
percussion. Minimalist approach with occasional sudden accents. Dark, mysterious 
atmosphere. Loop-friendly.
```
中文版：
```
悬疑风格管弦乐，弦乐低沉铜管，营造紧张氛围的打击乐。简约手法，偶尔突然强调。黑暗神秘感。
```

### Warm (温馨)
```
Warm acoustic track with gentle piano, soft strings, and light percussion. 
Heartfelt melody with a cozy, nostalgic feeling. Perfect for emotional moments.
```
中文版：
```
温暖的原声曲目，柔和钢琴、柔软弦乐、轻柔打击乐。真诚的旋律，舒适怀旧的感觉。
```

### Epic (史诗)
```
Epic orchestral anthem with full symphony orchestra, powerful choir, brass 
fanfares, and driving percussion. Heroic and grand, cinematic trailer music.
```
中文版：
```
史诗般管弦乐颂歌，完整交响乐团，有力合唱，铜管号角，驱动打击乐。英雄气概，宏大，电影预告片音乐。
```

### Cheerful (欢快)
```
Upbeat pop track with bright synths, acoustic guitar, light drums, and 
bouncy bass. Happy, energetic, perfect for lifestyle content.
```
中文版：
```
轻快流行曲目，明亮合成器，原声吉他，轻快鼓点，跃动贝斯。快乐活力，适合生活方式内容。
```

### Melancholic (悲伤)
```
Melancholic piano solo with subtle string accompaniment. Deeply emotional, 
reflective, and introspective. Minor key with gentle dynamics.
```
中文版：
```
忧郁钢琴独奏，微妙弦乐伴奏。深刻情感，反思内省。小调，柔和动态。
```

### Romantic (浪漫)
```
Romantic orchestral piece with lush strings, soft piano, and delicate 
woodwinds. Tender and loving, perfect for intimate moments.
```
中文版：
```
浪漫管弦乐，丰富的弦乐、柔和钢琴、精致木管。温柔有爱，适合亲密时刻。
```

### Tense (紧张)
```
Tense action music with fast-paced drums, aggressive strings, and urgent 
electronic elements. High energy, anxiety-inducing.
```
中文版：
```
紧张动作音乐，快节奏鼓点，激进弦乐，急促电子元素。高能量，焦虑诱发。
```

### Inspirational (励志)
```
Inspirational cinematic music with uplifting piano, soaring strings, and 
hopeful brass. Building to a triumphant climax. Motivational.
```
中文版：
```
励志电影音乐，振奋钢琴，高飞弦乐，希望铜管。走向胜利高潮。激励人心。
```

## 混合情绪提示词

### Epic + Romantic
```
Epic romantic orchestral track combining grand symphonic arrangements with 
tender, loving melodies. Both powerful and delicate.
```

### Warm + Cheerful
```
Warm cheerful acoustic pop with ukulele, gentle drums, and heartfelt lyrics.
Cozy yet upbeat.
```

### Suspenseful + Tense
```
Highly tense suspenseful track with aggressive strings, heartbeats, and 
shocking sound effects. Maximum tension.
```

## 时长适配提示词

| 视频长度 | 音乐建议 |
|----------|----------|
| < 30秒 | 使用单一情绪片段，可循环 |
| 30秒-2分钟 | 一首完整曲子，根据需要淡入淡出 |
| 2-5分钟 | 多段情绪音乐，中间有自然过渡 |
| > 5分钟 | 动态音乐，根据视频节奏变化 |

## 场景转换提示词

### 过渡类型 → 音乐处理

| 过渡类型 | 音乐处理 |
|----------|----------|
| 硬切 | 音乐同步切换 |
| 淡入淡出 | 音乐同步淡入淡出 (2-3秒) |
| 溶解 | 音乐交叉淡化 |
| 跳切 | 使用音乐重音点匹配 |
