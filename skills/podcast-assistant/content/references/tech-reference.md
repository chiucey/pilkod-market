# 播客助手 - 技术参考文档

## 核心技术栈

### 1. RSS 解析
使用 Python `feedparser` 库解析播客 RSS/Atom Feed。

```python
import feedparser

def parse_rss(url: str) -> dict:
    feed = feedparser.parse(url)
    return {
        'title': feed.feed.title,
        'author': feed.feed.author,
        'episodes': [
            {
                'title': entry.title,
                'audio_url': entry.enclosures[0]['href'],
                'duration': entry.get('itunes_duration', 'Unknown'),
                'pub_date': entry.published
            }
            for entry in feed.entries
            if entry.enclosures
        ]
    }
```

### 2. 音频下载
使用 `requests` 流式下载，FFmpeg 格式转换。

```python
import requests

def download_audio(url: str, output_path: str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
```

### 3. Whisper 转录
使用 OpenAI Whisper 模型进行语音识别。

```python
import whisper

def transcribe_audio(audio_path: str, model_size: str = "base") -> dict:
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, word_timestamps=True)
    return {
        'text': result['text'],
        'segments': [
            {
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            }
            for segment in result['segments']
        ]
    }
```

### 4. 摘要生成
使用 LLM 基于转录内容生成智能摘要。

```python
def generate_summary(transcript: str, llm_client) -> dict:
    prompt = f"""请为以下播客转录内容生成结构化摘要：

    {transcript[:4000]}

    输出格式：
    - 摘要（200字内）
    - 3-5个关键要点
    - 重要时间戳
    """

    response = llm_client.complete(prompt)
    return parse_summary_response(response)
```

### 5. 向量搜索
使用向量数据库实现语义搜索。

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

def setup_search_index(transcripts: list):
    embeddings = OpenAIEmbeddings()
    texts = [t['text'] for t in transcripts]
    metadatas = [{'episode': t['episode'], 'timestamp': t['timestamp']} for t in transcripts]

    return Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

def search_podcast(query: str, index, top_k: int = 5):
    results = index.similarity_search(query, k=top_k)
    return [
        {
            'text': doc.page_content,
            'metadata': doc.metadata
        }
        for doc in results
    ]
```

## 文件格式说明

### SRT 字幕格式
```
1
00:00:00,000 --> 00:00:05,000
这是第一段字幕内容

2
00:00:05,000 --> 00:00:10,000
这是第二段字幕内容
```

### VTT 字幕格式
```
WEBVTT

00:00:00.000 --> 00:00:05.000
这是第一段字幕内容

00:00:05.000 --> 00:00:10.000
这是第二段字幕内容
```

## 环境依赖

```
feedparser>=6.0.0
requests>=2.28.0
openai-whisper>=20231117
langchain>=0.0.200
chromadb>=0.4.0
ffmpeg>=5.0
```

## 注意事项

1. **音频格式**: Whisper 对 MP3、WAV、FLAC 支持最好，避免使用 OGG/Opus
2. **长音频**: 超过1小时的音频建议分段处理
3. **API限制**: LLM 调用需注意 token 限制
4. **存储管理**: 定期清理下载的音频文件
