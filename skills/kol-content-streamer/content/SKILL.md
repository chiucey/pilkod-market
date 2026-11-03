---
name: kol-content-streamer
description: KOL information flow content streamer and knowledge base builder. Used when users require scraping celebrity information, KOL social media content from X/Twitter, Weibo, Xiaohongshu, Douyin, TikTok, aggregating interview content, TV documentaries, film clips, and building personalized knowledge bases for persona simulation.
---

# KOL Information Flow Content Streamer

## Overview

This skill enables comprehensive KOL (Key Opinion Leader) and celebrity content streaming, aggregation, and knowledge base construction. It supports multi-platform content scraping, structured knowledge extraction, and persona-aware knowledge storage.

## Supported Platforms

### Social Media Platforms

| Platform | Handle/ID Format | Content Types |
|----------|------------------|--------------|
| **X (Twitter)** | @username, user_id | Tweets, threads, media, replies |
| **Weibo** | @username, uid | Posts, images, videos, reposts |
| **Xiaohongshu (RED)** | @username, note_id | Notes, images, videos, comments |
| **Douyin** | @username, aweme_id | Short videos, images, comments |
| **TikTok** | @username, video_id | Videos, images, comments |
| **Bilibili** | @username, bvid | Videos, subtitles, comments |

### Traditional Media

| Source Type | Content Types |
|-------------|--------------|
| **Interviews** | Modern talk shows, news interviews, podcasts |
| **TV Programs** | Documentaries, news features, reality shows |
| **Films** | Movie scripts, subtitles, behind-the-scenes |
| **Documentaries** | Full episodes, clips, transcripts |

## Core Features

### 1. Multi-Platform Content Aggregation

**Supported Content Streams:**

```yaml
platforms:
  - x_twitter
  - weibo
  - xiaohongshu
  - douyin
  - tiktok
  - bilibili
  - news_feeds
```

**Data Collection Methods:**

| Method | Description |
|--------|-------------|
| RSS Feeds | Standard RSS/Atom subscription |
| API Scraping | Platform-specific API endpoints |
| Web Scraping | HTML parsing with rate limiting |
| Media Download | Video/image asset extraction |

### 2. Celebrity & KOL Profile Building

**Profile Structure:**

```json
{
  "profile": {
    "platform_id": "unique_identifier",
    "display_name": "Name",
    "bio": "Biography",
    "verified": true,
    "followers": 1000000,
    "categories": ["tech", "business"],
    "verified_facts": []
  },
  "content_sources": [
    {
      "platform": "x_twitter",
      "handle": "@username",
      "url": "https://x.com/username"
    }
  ],
  "verified_events": [
    {
      "date": "2024-01-15",
      "source": "Press Conference",
      "content": "Statement about..."
    }
  ]
}
```

### 3. Content Type Classification

**Classification Schema:**

| Category | Examples |
|----------|----------|
| `opinion` | Personal views, commentary |
| `factual` | News sharing, event updates |
| `promotional` | Ads, sponsored content |
| `personal` | Daily life, casual posts |
| `professional` | Work-related, industry insights |
| `controversial` | Debatable statements |

### 4. Fact Verification Pipeline

**Verification Levels:**

| Level | Description | Confidence |
|-------|-------------|------------|
| `verified` | Cross-referenced with official sources | 95%+ |
| `likely` | Consistent with known facts | 80-95% |
| `unverified` | Single source, no confirmation | <80% |
| `disputed` | Contradictory sources | N/A |

### 5. Knowledge Base Integration

**Integration with Private AI Knowledge Base:**

```yaml
integration:
  auto_ingest: true
  persona_training: true
  fact_separation: true
  source_attribution: mandatory
```

## Usage Operations

### Subscribe to KOL Content

```yaml
operation: subscribe_kol
parameters:
  kol_id: "unique_kol_identifier"
  platforms:
    - x_twitter
    - weibo
  update_interval: "1h"  # 15m, 1h, 6h, daily
  content_filters:
    include_types: ["opinion", "factual", "professional"]
    exclude_types: ["promotional"]
  max_posts_per_update: 50
```

### Aggregate Topic Content

```yaml
operation: aggregate_topic
parameters:
  topic: "artificial_intelligence"
  languages: ["en", "zh"]
  sources:
    - kol_feeds
    - news_aggregators
    - video_platforms
  quality_threshold: 0.7
  deduplication: true
  time_range:
    start: "2024-01-01"
    end: "now"
```

### Scrape Celebrity Interview

```yaml
operation: scrape_interview
parameters:
  source_type: "talk_show"  # interview, podcast, documentary
  source_url: "https://example.com/interview"
  include_transcript: true
  include_video_clips: false
  extract_key_moments: true
  verify_facts: true
```

### Build Persona Knowledge Base

```yaml
operation: build_persona_kb
parameters:
  kol_id: "target_kol"
  knowledge_types:
    - opinions
    - expertise_areas
    - communication_style
    - verified_facts
    - content_patterns
  personality_analysis:
    enabled: true
    dimensions:
      - formality
      - emotion_tone
      - argument_style
```

### Continuous Content Stream

```yaml
operation: setup_content_stream
parameters:
  stream_config:
    sources:
      - type: "kol_following"
        kol_ids: ["kol_1", "kol_2"]
      - type: "topic_tracking"
        keywords: ["AI", "tech news"]
      - type: "trending"
        platforms: ["x_twitter", "weibo"]

    schedule:
      frequency: "15m"
      batch_size: 100
      priority_queue: true

    storage:
      encrypted: true
      dedup_enabled: true
      version_tracking: true
```

## Data Structures

### KOL Profile

```json
{
  "kol_id": "uuid",
  "name": "Display Name",
  "alt_names": ["Alias1", "Alias2"],
  "platforms": {
    "x_twitter": {
      "handle": "@username",
      "url": "https://x.com/username",
      "verified": true,
      "followers": 100000
    }
  },
  "categories": ["technology", "business"],
  "verified_bio": "Official biography",
  "key_dates": {
    "birth": "1990-01-01",
    "milestones": []
  },
  "persona_profile": {
    "communication_style": "formal",
    "common_topics": [],
    "typical_opinions": {}
  }
}
```

### Content Entry

```json
{
  "entry_id": "uuid",
  "source": {
    "platform": "x_twitter",
    "kol_id": "kol_uuid",
    "original_url": "https://...",
    "post_id": "original_post_id"
  },
  "content": {
    "original_text": "...",
    "translated_text": "...",
    "media_urls": [],
    "hashtags": [],
    "mentions": []
  },
  "metadata": {
    "posted_at": "2024-01-01T12:00:00Z",
    "collected_at": "2024-01-01T12:05:00Z",
    "engagement": {
      "likes": 1000,
      "retweets": 500,
      "replies": 100
    }
  },
  "classification": {
    "type": "opinion",
    "topics": ["AI", "ethics"],
    "sentiment": "positive",
    "verified_claims": []
  }
}
```

### Celebrity Fact Record

```json
{
  "fact_id": "uuid",
  "subject_id": "celebrity_uuid",
  "fact_type": "statement",
  "content": "What was said/done",
  "sources": [
    {
      "type": "interview",
      "url": "https://...",
      "timestamp": "2024-01-01",
      "context": "Full context..."
    }
  ],
  "verification": {
    "status": "verified",
    "cross_references": [],
    "discrepancies": []
  },
  "related_knowledge": {
    "entities": [],
    "events": [],
    "timeline_position": "2024-Q1"
  }
}
```

## Platform-Specific Notes

### X (Twitter)

```yaml
x_twitter:
  scraping_methods:
    - type: "api_v2"
      requires_auth: true
      rate_limit: "180 requests/15min"
    - type: "rss_feed"
      endpoint: "https://nitter.net/{username}/rss"
    - type: "web_scraper"
      user_agent_rotation: true

  content_extraction:
    - tweets
    - threads (recursive)
    - retweets (original content only)
    - media (images, videos)
    - quoted_tweets
```

### Weibo

```yaml
weibo:
  scraping_methods:
    - type: "api"
      requires_auth: true
    - type: "rss"
      endpoint: "https://rsshub.app/weibo/user/{uid}"

  content_extraction:
    - posts
    - long_text (article extension)
    - images
    - videos
    - reposts
```

### Xiaohongshu (RED)

```yaml
xiaohongshu:
  scraping_methods:
    - type: "api"
      requires_auth: true
    - type: "web_scraper"
      requires_proxy: true

  content_extraction:
    - notes (articles)
    - images
    - videos
    - comments
    - likes

  note_format:
    title: "required"
    body: "rich_text"
    tags: ["discovery_tag"]
```

### Douyin/TikTok

```yaml
douyin_tiktok:
  scraping_methods:
    - type: "api"
      requires_auth: true
    - type: "web_downloader"
      tool: "yt-dlp"

  content_extraction:
    - videos (with subtitles)
    - descriptions
    - comments
    - music_info

  output_formats:
    - video_file
    - audio_only
    - subtitles_only
    - description_text
```

### Bilibili

```yaml
bilibili:
  scraping_methods:
    - type: "api"
      public_endpoints: true
    - type: "subtitles"
      auto_generated: true
      user_uploaded: true

  content_extraction:
    - videos
    - subtitles (ass/srt/json)
    - danmaku (comments)
    - descriptions
    - tags
```

## Fact Extraction & Verification

### Extraction Pipeline

```
Raw Content → Cleaning → NLP Processing → Fact Extraction → Verification → Storage
     ↓            ↓             ↓                ↓               ↓          ↓
  Platform    HTML/JSON    Sentence      Claim Detection   Cross-ref   Encrypted
  Response    Parsing      Splitting     Entity Linking     Sources     Storage
```

### Verification Sources

| Source Type | Examples |
|-------------|----------|
| Official Archives | Press releases, official statements |
| News Archives | Major news outlets |
| Video Archives | Official uploads, documentaries |
| Court Records | Legal documents (if applicable) |
| Academic Sources | Peer-reviewed content |

## Quality Control

### Content Quality Metrics

```yaml
quality_assessment:
  originality_score: 0.0-1.0
  engagement_ratio: likes/views
  source_reliability: verified/partial/unverified
  factual_density: claims_per_post
  topic_relevance: keyword_match_score
```

### Filtering Rules

```yaml
filters:
  exclude:
    - promotional_content
    - spam
    - duplicate_content
    - low_quality_media
    - age_restricted

  include:
    - verified_accounts
    - high_engagement
    - relevant_topics
    - recent_content
```

## Scheduling & Automation

### Cron Expressions

| Schedule | Expression | Use Case |
|----------|------------|----------|
| Real-time | `*/15 * * * *` | Breaking news, urgent updates |
| Hourly | `0 * * * *` | Regular content sync |
| Daily | `0 6 * * *` | Summary updates |
| Weekly | `0 6 * * 0` | Weekly digest |

### Task Configuration

```yaml
scheduled_tasks:
  - name: "kol_daily_sync"
    schedule: "0 6 * * *"
    actions:
      - sync_all_subscribed_kols
      - generate_activity_summary
      - update_persona_models

  - name: "topic_hourly_aggregate"
    schedule: "0 * * * *"
    actions:
      - fetch_topic_updates
      - filter_quality_content
      - add_to_knowledge_base

  - name: "trending_15min"
    schedule: "*/15 * * * *"
    actions:
      - fetch_trending
      - extract_key_claims
      - flag_important_updates
```

## Security & Privacy

### Data Protection

- All scraped content encrypted at rest (AES-256-GCM)
- API credentials stored securely
- Rate limiting to respect platform terms
- User isolation for multi-tenant deployments

### Platform Compliance

```yaml
compliance:
  respect_robots_txt: true
  rate_limiting:
    x_twitter: "respect_api_limits"
    weibo: "respect_api_limits"
    custom_delay: 2s

  content_usage:
    personal_knowledge: allowed
    distribution: prohibited
    commercial_use: prohibited
```

## Configuration Example

```yaml
# kol-streamer-config.yaml
kol_streamer:
  general:
    output_base_path: "/data/kol-content"
    encryption_enabled: true
    parallel_scraping: 3

  platforms:
    x_twitter:
      enabled: true
      method: "rss"  # api, rss, scraper
      accounts:
        - handle: "@elonmusk"
          sync: true
        - handle: "@sama"
          sync: true

    weibo:
      enabled: true
      method: "rss"
      accounts:
        - uid: "1195230310"
          sync: true

    xiaohongshu:
      enabled: true
      method: "scraper"
      accounts:
        - user_id: "user123"
          sync: true

    douyin:
      enabled: true
      method: "api"
      download_subtitles: true

    tiktok:
      enabled: true
      method: "api"
      download_subtitles: true

    bilibili:
      enabled: true
      method: "api"
      download_subtitles: true

  traditional_media:
    interview_sources:
      - name: "60 Minutes"
        url_pattern: "https://cbsnews.com/60-minutes/*"
      - name: "TED Talks"
        url_pattern: "https://ted.com/talks/*"

    documentary_sources:
      - platform: "netflix"
        categories: ["nature", "science"]
      - platform: "youtube"
        channels: ["Documentary", "National Geographic"]

  knowledge_base:
    integration:
      target_kb: "private-ai-knowledge-base"
      auto_ingest: true
      persona_enabled: true

    fact_separation:
      verified_facts: "verified-store"
      unverified_claims: "unverified-store"
      opinions: "opinion-store"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Rate limited | Too many requests | Reduce frequency, add delays |
| Auth failed | Token expired | Refresh API credentials |
| Content missing | Platform change | Update scraping method |
| Duplicate entries | Re-scraping | Enable dedup, check timestamps |
| Fact verification failed | Insufficient sources | Add more reference sources |

---

**Author**: MiniMax Agent
**Version**: 1.0.0
**Last Updated**: 2026-03-27
