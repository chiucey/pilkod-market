---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 72b79177dd85deee6540000d9a9c9a5a
    PropagateID: 72b79177dd85deee6540000d9a9c9a5a
    ReservedCode1: 3044022004657d9eba965a9b0fca5242d459c3a3d31d2fa27c36e246f3483a9eb89bfb6f0220585738d2d7cedbdda89a91958c43ad7fbeb1c1b4ad7643ee4b304270365bbea7
    ReservedCode2: 30450220398d4d6acb8b6ca529fe6c3f8673b2582d3dc1bb1c694d4c6ec640718911a47e022100d8e50b0c92366e13b4f4a978234a928329e54b8a3727549dfb822e7f9ab39383
description: WeChat public account content creation assistant for tracking hot topics, organizing reading notes, and generating articles. Use when users need help writing WeChat public account posts, combining hot topics with reading insights, or managing reading notes.
name: wechat-content-assistant
---

# WeChat Content Assistant

## Overview

This is an intelligent assistant designed for WeChat public account creators, featuring:

- 📰 **Hot Topic Tracking**: Real-time monitoring of trending topics across Weibo, Zhihu, Baidu, and more
- 📚 **Reading Notes Management**: Store and organize your reading notes to build a personal knowledge base
- ✍️ **Smart Writing**: Combine hot topics with reading notes to generate high-quality public account articles

## Core Features

### 1. Hot Topic Discovery

**Supported Platforms**:
- Weibo trending searches
- Zhihu hot rankings
- Baidu hot searches
- WeChat Index related topics
- Tech media (36Kr, Huxiu, etc.)

**Usage Examples**:
```
Get today's hot topics
Find recent tech trends
What's worth following recently
```

### 2. Reading Notes Management

**Supported Note Format**:
- Book title, chapter
- Core insights
- Personal reflections
- Keywords and tags
- Related topic connections

**Usage Examples**:
```
Add a reading note: [book title] [content]
View all my reading notes
Search notes about [topic]
Delete note from [date]
Export my reading notes
```

### 3. Article Generation

**Writing Modes**:
- **Hot Topic Hook**: Start with trending topic, naturally introduce reading content
- **Perspective Collision**: Compare viewpoints from different books
- **Deep Analysis**: In-depth exploration of a topic using multiple book sources
- **Practical Tips**: Transform methodologies from books into actionable advice

**Article Structure** (Target: 1500-2000 words):
```
1. Hot Topic Introduction (200-300 words) - Hook readers with a trending topic or relatable story
2. Core Argument (500-600 words) - Present the main insight from books
3. Supporting Points (400-500 words) - 2-3 key examples or evidence
4. Summary & Takeaway (200-300 words) - Conclude with actionable insights
5. Call to Action (100 words) - Engage readers with a question or prompt
```

**IMPORTANT**: Keep articles concise and focused. 1500-2000 words is the optimal length for WeChat public account articles. Quality over quantity - each paragraph should deliver value.

## Workflow

### Complete Creation Process

```
┌─────────────────────────────────────────────────────────────┐
│                  Creation Workflow                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣ Hot Topics ──→ 2️⃣ Notes Search ──→ 3️⃣ Content ──→ 4️⃣ Article │
│       ↓              ↓              ↓              ↓        │
│   Real-time      Related       Material        WeChat      │
│   Trends         Notes         Organization    Article      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Specific Steps

**Step 1: Hot Topic Discovery**
- Use `batch_web_search` to get latest trends
- Use `extract_content_from_websites` for deeper background research
- Filter topics related to your reading interests

**Step 2: Notes Search**
- Search reading notes based on hot topic themes
- Organize core insights and examples from notes
- Mark reusable quotes and passages

**Step 3: Content Organization**
- Build connections between hot topics and reading notes
- Design article framework and logical structure
- Prepare opening, transition, and closing materials

**Step 4: Article Generation**
- Write each section according to structure
- Ensure clear arguments with sufficient evidence
- Add personal insights and reflections

## Tool Usage Strategy

### Hot Topic Discovery
```python
# Batch search trending topics
batch_web_search(queries=[
    {"query": "Weibo trending today", "num_results": 10},
    {"query": "Zhihu hot list", "num_results": 10},
    {"query": "Baidu hot searches", "num_results": 10}
])
```

### Content Deep Dive
```python
# In-depth topic research
extract_content_from_websites(tasks=[
    {"url": "news_link", "prompt": "Extract key points and background"},
    {"url": "article_link", "prompt": "Extract core arguments and data"}
])
```

### Notes Storage Format
```json
{
    "id": "unique_note_id",
    "book_title": "Book Title",
    "chapter": "Chapter",
    "content": "Note content",
    "tags": ["tag1", "tag2"],
    "created_at": "timestamp",
    "related_topics": ["related", "topics"],
    "source_url": "source_link"
}
```

## Best Practices

### 1. Hot Topic Awareness
- Check hot topics at fixed times daily (e.g., 9 AM, 3 PM)
- Follow the development and public opinion changes of trends
- Record trending events related to your content area

### 2. Reading Notes Tips
- Read with questions: What do you want to learn today?
- Keep notes concise: Core insight + personal reflection
- Capture immediately: Note moments that resonate
- Regular review: Revisit notes weekly, update tags

### 3. Article Topic Strategy
- **Timely Topics**: Follow trends, produce quickly
- **Deep Topics**: Explore one perspective into a series
- **Evergreen Topics**: Classic themes for repeated engagement
- **Audience Needs**: Topics based on follower feedback

### 4. Content Quality Control
- Catchy titles without clickbait
- Substantive content with unique insights
- Clear logic and structured presentation
- Actionable takeaways or engagement prompts

## Advanced Features

### Auto-Tracking
```python
# Set up periodic hot topic notifications
create_cron_job(
    job_title="Daily Hot Topic Push",
    job_instruction="Get today's trends, analyze relevance to user interests, send relevant topic reminders",
    cron_expression="0 9 * * *"  # Daily at 9 AM
)
```

### Knowledge Base Building
- 100+ notes form a personal knowledge system
- Quick search via tag system
- Build connection maps between insights

### Multi-Platform Distribution
- Adapt content style for different platforms
- Adjust for Toutiao, Baijiahao, Jianshu, etc.
- Optimize titles and openings per platform

## FAQ

**Q: How to choose the right hot topic?**
A: Selection criteria: ① Relevant to target audience ② Sufficient discussion ③ Can connect with reading notes ④ Has unique angle to explore

**Q: What if reading notes are insufficient?**
A: Suggestions: ① Increase reading and note-taking frequency ② Use book cases and quotes effectively ③ Explore different angles from the same book

**Q: How to maintain content differentiation?**
A: Key is adding your unique perspective and experience - not just repeating book content, but expressing YOUR understanding and thoughts

**Q: What update frequency to maintain?**
A: Suggestions: Hot topic articles should be fast (within 1-2 days), deep articles can be slower (1-2 weeks), maintain 2-3 articles per week

## Usage Examples

### Example 1: Quick Hot Topic Article
```
User: Help me write an article about "AI Era" for WeChat, combining with "A Brief History of AI" I read

Assistant:
1. Get latest AI trends
2. Search reading notes about AI
3. Generate article framework
4. Output complete article
```

### Example 2: Add Reading Notes
```
User: Add a reading note
Book: Thinking, Fast and Slow
Chapter: Chapter 15
Content: Peak-End Rule - our memory of experiences depends on the peak moment and ending
Tags: psychology, behavioral_economics, user_experience
Related topics: user_research, product_design

Assistant: Note saved, ready to use
```

### Example 3: Track Trends
```
User: Any tech trends recently?

Assistant:
1. Weibo Top 10
2. Zhihu Hot List Top 10
3. Tech Media Headlines
4. Filter topics related to reading/content creation
```

## Continuous Improvement

1. **Build Topic Pool**: Record inspirations anytime, form a topic reserve
2. **Build Material Library**: Categorize cases, quotes, images
3. **Regular Review**: Analyze engagement metrics, optimize direction
4. **Learn from Peers**: Follow quality accounts in your niche, learn writing techniques

---

**Skill Maintenance**: Regularly update hot topic strategies, optimize article templates, expand reading notes features
