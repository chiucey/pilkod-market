---
name: english-vocab-scene
description: 生成英语学习场景图（如樱花树等自然场景），包含英文、音标和中文翻译的标注。**图片比例固定为 3:4，音标必须正确。** 触发词：英语学习图、英语场景图、英语词汇图、樱花树英语、树叶英语等。
---

# 英语学习场景图 Skill

生成分辨率 2K、16:9 比例的英语学习场景图，主体为动漫风格自然场景，配有英文单词、音标和中文翻译的标注。

## 触发条件

用户请求生成英语学习场景图时使用，例如：
- "制作一张英语学习场景图"
- "樱花树英语学习图"
- "树叶英语词汇图"

## 生成步骤

### 1. 确定场景和词汇

根据用户提供的词汇确定：
- **场景主题**（如：樱花树、森林、海洋、厨房等）
- **词汇列表**（英文 + 音标 + 中文翻译）
- **风格**（默认宫崎骏动漫风格 / 迪士尼风格 / 写实风格）

### 2. 构建提示词模板

```
A beautiful [STYLE] style illustration of [SCENE] for English vocabulary learning. The scene shows [DESCRIPTION]. Around the scene, there are labeled annotations pointing to different parts with English words, IPA phonetics, and Chinese translations in elegant handwritten style text:

- 'word1 /phonetic/ translation' - pointing to [location]
- 'word2 /phonetic/ translation' - pointing to [location]
... (all vocabulary items)

The annotations should be like elegant chalk drawings or handwritten notes with soft arrows pointing to the relevant parts. [STYLE DETAILS]. Text should be clear and readable.
```

### 3. 生成图片

使用 `image_synthesize` 工具生成，参数：
- `aspect_ratio`: "3:4"（**必须使用 3:4 比例**）
- `resolution`: "2K"
- `prompt`: 构建好的提示词，包含正确的 IPA 音标

### 4. 重要：确保音标正确

在提示词中明确使用正确的 IPA 音标，不要让 AI 自动生成。常用音标参考：
- frog: /frɒɡ/
- lake: /leɪk/
- fish: /fɪʃ/
- river: /ˈrɪvər/
- pond: /pɒnd/
- duck: /dʌk/
- shark: /ʃɑːrk/
- sea: /siː/
- leaf: /liːf/
- flower: /ˈflaʊər/
- tree: /triː/
- grass: /ɡrɑːs/
- trunk: /trʌŋk/
- root: /ruːt/
- branch: /brɑːntʃ/

### 4. 输出结果

上传到 CDN 并展示给用户，同时提供词汇表格。

## 常用词汇参考

### 樱花树场景
| 英文 | 音标 | 中文 |
|------|------|------|
| leaf | /liːf/ | 叶子 |
| flower | /ˈflaʊə/ | 花 |
| tree | /triː/ | 树 |
| grass | /ɡrɑːs/ | 草 |
| trunk | /trʌŋk/ | 树干 |
| root | /ruːt/ | 根 |
| branch | /brɑːntʃ/ | 树枝 |

### 房间场景
| 英文 | 音标 | 中文 |
|------|------|------|
| window | /ˈwɪndəʊ/ | 窗户 |
| door | /dɔː/ | 门 |
| bed | /bed/ | 床 |
| table | /ˈteɪbl/ | 桌子 |
| chair | /tʃeə/ | 椅子 |
| lamp | /læmp/ | 灯 |
| clock | /klɒk/ | 时钟 |

### 厨房场景
| 英文 | 音标 | 中文 |
|------|------|------|
| pot | /pɒt/ | 锅 |
| pan | /pæn/ | 平底锅 |
| knife | /naɪf/ | 刀 |
| fork | /fɔːk/ | 叉子 |
| spoon | /spuːn/ | 勺子 |
| bowl | /bəʊl/ | 碗 |
| cup | /kʌp/ | 杯子 |

## 注意事项

1. **比例**：默认 16:9，如需其他比例在 prompt 中指定
2. **分辨率**：设置为 2K 确保清晰度
3. **风格描述**：使用具体的动漫风格名称（如 Miyazaki、Ghibli）效果更好
4. **检查遗漏**：生成后确认所有词汇都在图上，如有遗漏重新生成
5. **字体风格**：提示词中强调"handwritten style"可获得手写字体效果
