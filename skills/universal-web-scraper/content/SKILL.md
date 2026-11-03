---
name: universal-web-scraper
description: |
  AI-driven data extraction from 55+ Actors across all major platforms. Automatically selects the best Actor for your scraping task.

  Use when users ask to:
  - "scrape", "extract data from", "crawl" any social media or website
  - "get followers", "posts", "comments", "likes" from Instagram/Facebook/TikTok/YouTube
  - "find business listings", "reviews", "contact info" from Google Maps
  - "scrape hotel data", "reviews" from Booking.com or TripAdvisor
  - "track competitors", "monitor brands", "analyze trends" on social platforms
  - "generate leads", "find emails", "contact enrichment"
  - "analyze influencer metrics", "engagement rates", "follower counts"
  - "extract search results", "trend data", "hashtag performance"
  - Any request involving web scraping, data extraction, or social media analytics
---

# Universal Web Scraper

AI-driven data extraction from 55+ Actors across all major platforms. This skill automatically selects the best Actor for your task.

## Prerequisites

- `.env` file with `APIFY_TOKEN` (get from [apify.com](https://apify.com))
- Node.js 20.6+ (for native `--env-file` support)

## Workflow

### Step 1: Understand User Goal and Select Actor

First, understand what the user wants to achieve. Then select the best Actor from the options below.

#### Instagram Actors (12)

| Actor ID | Best For |
|----------|----------|
| `apify/instagram-profile-scraper` | Profile data, follower counts, bio info |
| `apify/instagram-post-scraper` | Individual post details, engagement metrics |
| `apify/instagram-comment-scraper` | Comment extraction, sentiment analysis |
| `apify/instagram-hashtag-scraper` | Hashtag content, trending topics |
| `apify/instagram-hashtag-stats` | Hashtag performance metrics |
| `apify/instagram-reel-scraper` | Reels content and metrics |
| `apify/instagram-search-scraper` | Search users, places, hashtags |
| `apify/instagram-tagged-scraper` | Posts tagged with specific accounts |
| `apify/instagram-followers-count-scraper` | Follower count tracking |
| `apify/instagram-scraper` | Comprehensive Instagram data |
| `apify/instagram-api-scraper` | API-based Instagram access |
| `apify/export-instagram-comments-posts` | Bulk comment/post export |

#### Facebook Actors (14)

| Actor ID | Best For |
|----------|----------|
| `apify/facebook-pages-scraper` | Page data, metrics, contact info |
| `apify/facebook-page-contact-information` | Emails, phones, addresses from pages |
| `apify/facebook-posts-scraper` | Post content and engagement |
| `apify/facebook-comments-scraper` | Comment extraction |
| `apify/facebook-likes-scraper` | Reaction analysis |
| `apify/facebook-reviews-scraper` | Page reviews |
| `apify/facebook-groups-scraper` | Group content and members |
| `apify/facebook-events-scraper` | Event data |
| `apify/facebook-ads-scraper` | Ad creative and targeting |
| `apify/facebook-search-scraper` | Search results |
| `apify/facebook-reels-scraper` | Reels content |
| `apify/facebook-photos-scraper` | Photo extraction |
| `apify/facebook-marketplace-scraper` | Marketplace listings |
| `apify/facebook-followers-following-scraper` | Follower/following lists |

#### TikTok Actors (14)

| Actor ID | Best For |
|----------|----------|
| `clockworks/tiktok-scraper` | Comprehensive TikTok data |
| `clockworks/free-tiktok-scraper` | Free TikTok extraction |
| `clockworks/tiktok-profile-scraper` | Profile data |
| `clockworks/tiktok-video-scraper` | Video details and metrics |
| `clockworks/tiktok-comments-scraper` | Comment extraction |
| `clockworks/tiktok-followers-scraper` | Follower lists |
| `clockworks/tiktok-user-search-scraper` | Find users by keywords |
| `clockworks/tiktok-hashtag-scraper` | Hashtag content |
| `clockworks/tiktok-sound-scraper` | Trending sounds |
| `clockworks/tiktok-ads-scraper` | Ad content |
| `clockworks/tiktok-discover-scraper` | Discover page content |
| `clockworks/tiktok-explore-scraper` | Explore content |
| `clockworks/tiktok-trends-scraper` | Trending content |
| `clockworks/tiktok-live-scraper` | Live stream data |

#### YouTube Actors (5)

| Actor ID | Best For |
|----------|----------|
| `streamers/youtube-scraper` | Video data and metrics |
| `streamers/youtube-channel-scraper` | Channel information |
| `streamers/youtube-comments-scraper` | Comment extraction |
| `streamers/youtube-shorts-scraper` | Shorts content |
| `streamers/youtube-video-scraper-by-hashtag` | Videos by hashtag |

#### Google Maps Actors (4)

| Actor ID | Best For |
|----------|----------|
| `compass/crawler-google-places` | Business listings, ratings, contact info |
| `compass/google-maps-extractor` | Detailed business data |
| `compass/Google-Maps-Reviews-Scraper` | Review extraction |
| `poidata/google-maps-email-extractor` | Email discovery from listings |

#### Other Actors (6)

| Actor ID | Best For |
|----------|----------|
| `apify/google-search-scraper` | Google search results |
| `apify/google-trends-scraper` | Google Trends data |
| `voyager/booking-scraper` | Booking.com hotel data |
| `voyager/booking-reviews-scraper` | Booking.com reviews |
| `maxcopell/tripadvisor-reviews` | TripAdvisor reviews |
| `vdrmota/contact-info-scraper` | Contact enrichment from URLs |

#### Actor Selection by Use Case

| Use Case | Primary Actors |
|----------|----------------|
| Lead Generation | `compass/crawler-google-places`, `poidata/google-maps-email-extractor`, `vdrmota/contact-info-scraper` |
| Influencer Discovery | `apify/instagram-profile-scraper`, `clockworks/tiktok-profile-scraper`, `streamers/youtube-channel-scraper` |
| Brand Monitoring | `apify/instagram-tagged-scraper`, `apify/instagram-hashtag-scraper`, `compass/Google-Maps-Reviews-Scraper` |
| Competitor Analysis | `apify/facebook-pages-scraper`, `apify/facebook-ads-scraper`, `apify/instagram-profile-scraper` |
| Content Analytics | `apify/instagram-post-scraper`, `clockworks/tiktok-scraper`, `streamers/youtube-scraper` |
| Trend Research | `apify/google-trends-scraper`, `clockworks/tiktok-trends-scraper`, `apify/instagram-hashtag-stats` |
| Review Analysis | `compass/Google-Maps-Reviews-Scraper`, `voyager/booking-reviews-scraper`, `maxcopell/tripadvisor-reviews` |
| Audience Analysis | `apify/instagram-followers-count-scraper`, `clockworks/tiktok-followers-scraper`, `apify/facebook-followers-following-scraper` |

#### Can't Find a Suitable Actor?

If none of the Actors above match the user's request, search the Apify Store directly:

```bash
node ${CLAUDE_PLUGIN_ROOT}/reference/scripts/search_actors.js --query "SEARCH_KEYWORDS"
```

Replace `SEARCH_KEYWORDS` with 1-3 simple terms (e.g., "LinkedIn profiles", "Amazon products", "Twitter").

---

### Step 2: Fetch Actor Schema

Fetch the Actor's input schema and details:

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/fetch_actor_details.js --actor "ACTOR_ID"
```

Replace `ACTOR_ID` with the selected Actor (e.g., `compass/crawler-google-places`).

This returns:
- Actor info (title, description, URL, categories, stats, rating)
- README summary
- Input schema (required and optional parameters)

---

### Step 3: Ask User Preferences

**Skip this step** for simple lookups (e.g., "what's Nike's follower count?", "find me 5 coffee shops in Prague") — just use quick answer mode and move to Step 4.

For larger scraping tasks, ask:

#### Output Format Options

| Format | Use Case |
|--------|----------|
| Quick answer | Display top few results in chat (no file saved) |
| CSV | Full export with all fields |
| JSON | Full export in JSON format |

#### Number of Results

Set a sensible result limit based on use case. Default to 100 results unless the user explicitly asks for more.

**⚠️ Cost Warning**: Warn the user before running large scrapes (1000+ results) as they consume more Apify credits.

---

### Step 4: Run the Script

#### Quick Answer (display in chat, no file)

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT'
```

#### CSV Export

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_OUTPUT_FILE.csv \
  --format csv
```

#### JSON Export

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_OUTPUT_FILE.json \
  --format json
```

---

### Step 5: Summarize Results and Offer Follow-ups

After completion, report:
- Number of results found
- File location and name
- Key fields available
- Suggested follow-up workflows based on results

| If User Got | Suggested Next Steps |
|-------------|----------------------|
| Business listings | Enrich with `vdrmota/contact-info-scraper` or get reviews |
| Influencer profiles | Analyze engagement with comment scrapers |
| Competitor pages | Deep-dive with post/ad scrapers |
| Trend data | Validate with platform-specific hashtag scrapers |

---

## Usage Examples

### Example 1: Quick Instagram Profile Lookup

**User**: "What's Nike's follower count on Instagram?"

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/instagram-profile-scraper" \
  --input '{"usernames": ["nikesbc"], "resultsLimit": 1}'
```

**Output**: Display follower count directly in chat.

---

### Example 2: Lead Generation for Local Businesses

**User**: "Find 50 coffee shops in Berlin with their contact info"

1. Fetch Google Maps listings:
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "compass/crawler-google-places" \
  --input '{"searchQuery": "coffee shops Berlin", "maxResults": 50}' \
  --output 2024-01-15_berlin_coffee_shops.csv \
  --format csv
```

2. Enrich with emails:
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "poidata/google-maps-email-extractor" \
  --input '{"maxResults": 50}' \
  --output 2024-01-15_berlin_coffee_emails.csv \
  --format csv
```

---

### Example 3: Influencer Research

**User**: "Analyze engagement rate for tech influencers with 100k+ followers"

1. Scrape profile data:
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/instagram-profile-scraper" \
  --input '{"usernames": ["username1", "username2"], "resultsLimit": 20}' \
  --output 2024-01-15_influencer_profiles.json \
  --format json
```

2. Analyze comments:
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/instagram-comment-scraper" \
  --input '{"maxResults": 100}' \
  --output 2024-01-15_influencer_comments.json \
  --format json
```

---

### Example 4: Competitor Analysis on Facebook

**User**: "Compare follower counts and engagement for Apple, Samsung, and Google Facebook pages"

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/facebook-pages-scraper" \
  --input '{"pages": ["Apple", "Samsung", "Google"], "resultsLimit": 3}' \
  --output 2024-01-15_competitor_analysis.csv \
  --format csv
```

---

### Example 5: TikTok Trend Analysis

**User**: "What are the top trending hashtags on TikTok this week?"

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "clockworks/tiktok-trends-scraper" \
  --input '{"resultsLimit": 50}' \
  --output 2024-01-15_tiktok_trends.json \
  --format json
```

---

### Example 6: Review Monitoring

**User**: "Get TripAdvisor reviews for restaurants in Paris"

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "maxcopell/tripadvisor-reviews" \
  --input '{"searchQuery": "restaurants Paris", "maxResults": 100}' \
  --output 2024-01-15_paris_reviews.csv \
  --format csv
```

---

### Example 7: Multi-Platform Brand Monitoring

**User**: "Monitor brand mentions for 'Tesla' across Instagram and TikTok"

1. Instagram hashtag monitoring:
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/instagram-hashtag-scraper" \
  --input '{"hashtag": "tesla", "resultsLimit": 50}' \
  --output 2024-01-15_instagram_tesla.json \
  --format json
```

2. TikTok hashtag monitoring:
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "clockworks/tiktok-hashtag-scraper" \
  --input '{"hashtag": "tesla", "resultsLimit": 50}' \
  --output 2024-01-15_tiktok_tesla.json \
  --format json
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| `APIFY_TOKEN not found` | Ask user to create `.env` with `APIFY_TOKEN=your_token` |
| `Actor not found` | Check Actor ID spelling, try searching with `search_actors.js` |
| `Run FAILED` | Ask user to check Apify console link in error output |
| `Timeout` | Reduce input size or increase `--timeout` |

---

## Multi-Actor Workflows

For complex tasks, chain multiple Actors:

| Workflow | Step 1 | Step 2 |
|----------|--------|--------|
| Lead enrichment | `compass/crawler-google-places` → | `vdrmota/contact-info-scraper` |
| Influencer vetting | `apify/instagram-profile-scraper` → | `apify/instagram-comment-scraper` |
| Competitor deep-dive | `apify/facebook-pages-scraper` → | `apify/facebook-posts-scraper` |
| Local business analysis | `compass/crawler-google-places` → | `compass/Google-Maps-Reviews-Scraper` |
