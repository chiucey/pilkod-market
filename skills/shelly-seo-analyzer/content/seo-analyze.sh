#!/usr/bin/env bash
# SEO Analyzer - based on shelly-seo-analyzer skill
# Usage: curl -sL <URL> | ./seo-analyze.sh -
# Or: ./seo-analyze.sh <URL>

set -e

Analyze_URL() {
  local url="$1"
  echo "=========================================="
  echo "🔍 SEO Analysis Report"
  echo "URL: $url"
  echo "=========================================="
  echo ""

  # Fetch content
  content=$(curl -sL "$url" --max-time 15 -A "SEO-Agent/1.0")
  
  Analyze_Stdin "$content"
}

Analyze_Stdin() {
  local content="$1"
  
  if [ -z "$content" ]; then
    echo "❌ Failed to fetch page or no content received."
    exit 1
  fi

  echo "✅ Page fetched successfully"
  echo ""
  echo "=========================================="
  echo "1. TITLE TAG"
  echo "=========================================="
  title=$(echo "$content" | grep -iE '<title[^>]*>[^<]+</title>' | sed -E 's/.*<title[^>]*>([^<]+)<\/title>.*/\1/' | head -1 | xargs)
  if [ -n "$title" ]; then
    echo "✅ Title found: $title"
    len=${#title}
    echo "   Length: $len chars"
    if [ "$len" -ge 50 ] && [ "$len" -le 60 ]; then
      echo "   ✅ Ideal length (50-60 chars)"
    else
      echo "   ⚠️  Recommended: 50-60 chars"
    fi
  else
    echo "❌ No title tag found!"
  fi
  echo ""

  echo "=========================================="
  echo "2. META DESCRIPTION"
  echo "=========================================="
  desc=$(echo "$content" | grep -iE '<meta[^>]+name=["\x27]description["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*content=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  if [ -z "$desc" ]; then
    desc=$(echo "$content" | grep -iE '<meta[^>]+content=["\x27]([^"\x27]+)["\x27][^>]+name=["\x27]description["\x27]' | sed -E 's/.*content=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  fi
  if [ -n "$desc" ]; then
    echo "✅ Meta description found: ${desc:0:80}..."
    len=${#desc}
    echo "   Length: $len chars"
    if [ "$len" -ge 150 ] && [ "$len" -le 160 ]; then
      echo "   ✅ Ideal length (150-160 chars)"
    else
      echo "   ⚠️  Recommended: 150-160 chars"
    fi
  else
    echo "❌ No meta description found!"
  fi
  echo ""

  echo "=========================================="
  echo "3. HEADING STRUCTURE (H1-H6)"
  echo "=========================================="
  h1_count=$(echo "$content" | grep -cE '<h1[^>]*>' | head -1)
  h2_count=$(echo "$content" | grep -cE '<h2[^>]*>' | head -1)
  h3_count=$(echo "$content" | grep -cE '<h3[^>]*>' | head -1)
  h4_count=$(echo "$content" | grep -cE '<h4[^>]*>' | head -1)
  echo "H1: $h1_count | H2: $h2_count | H3: $h3_count | H4: $h4_count"
  if [ "$h1_count" -eq 1 ]; then
    echo "✅ Exactly one H1 (ideal)"
  elif [ "$h1_count" -eq 0 ]; then
    echo "❌ No H1 tag found!"
  else
    echo "⚠️  Multiple H1 tags found (should be exactly 1)"
  fi
  echo "H1 content:"
  echo "$content" | grep -iE '<h1[^>]*>[^<]+</h1>' | sed -E 's/.*<h1[^>]*>([^<]+)<\/h1>/  - \1/' | head -5
  echo ""

  echo "=========================================="
  echo "4. KEYWORD DENSITY (Top 10 words)"
  echo "=========================================="
  # Strip HTML, get text, count words
  words=$(echo "$content" \
    | sed 's/<[^>]*>//g' \
    | tr -cs '[:alnum:]' '\n' \
    | tr '[:upper:]' '[:lower:]' \
    | grep -E '^.{3,}$' \
    | sort \
    | uniq -c \
    | sort -rn \
    | head -10)
  if [ -n "$words" ]; then
    total_words=$(echo "$content" | sed 's/<[^>]*>//g' | wc -w)
    echo "Total words on page: ~$total_words"
    echo "Top keywords:"
    echo "$words" | awk '{printf "  %4d — %s\n", $1, $2}' | head -10
  else
    echo "⚠️  Could not extract text content"
  fi
  echo ""

  echo "=========================================="
  echo "5. IMAGE ALT TAGS"
  echo "=========================================="
  total_imgs=$(echo "$content" | grep -cE '<img[^>]+>' | head -1)
  missing_alt=$(echo "$content" | grep -E '<img[^>]+>' | grep -vcE '<img[^>]+alt=["\x27][^"\x27]*["\x27][^>]*>' | head -1)
  echo "Total images: $total_imgs"
  echo "Missing alt attributes: $missing_alt"
  if [ "$missing_alt" -eq 0 ]; then
    echo "✅ All images have alt text"
  else
    echo "⚠️  $missing_alt images missing alt attributes"
    echo "Examples (first 3):"
    echo "$content" | grep -E '<img[^>]+>' | grep -vE 'alt=["\x27][^"\x27]*["\x27]' | head -3 \
      | sed -E 's/<img([^>]*).*/  <img\1/' | head -3
  fi
  echo ""

  echo "=========================================="
  echo "6. OPEN GRAPH & SOCIAL TAGS"
  echo "=========================================="
  og_title=$(echo "$content" | grep -iE '<meta[^>]+property=["\x27]og:title["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*content=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  og_desc=$(echo "$content" | grep -iE '<meta[^>]+property=["\x27]og:description["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*content=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  og_image=$(echo "$content" | grep -iE '<meta[^>]+property=["\x27]og:image["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*content=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  twitter_card=$(echo "$content" | grep -iE '<meta[^>]+name=["\x27]twitter:card["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*content=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  
  [ -n "$og_title" ] && echo "✅ og:title: $og_title" || echo "❌ og:title: missing"
  [ -n "$og_desc" ] && echo "✅ og:description: ${og_desc:0:70}..." || echo "❌ og:description: missing"
  [ -n "$og_image" ] && echo "✅ og:image: $og_image" || echo "❌ og:image: missing"
  [ -n "$twitter_card" ] && echo "✅ twitter:card: $twitter_card" || echo "❌ twitter:card: missing"
  echo ""

  echo "=========================================="
  echo "7. CANONICAL URL"
  echo "=========================================="
  canonical=$(echo "$content" | grep -iE '<link[^>]+rel=["\x27]canonical["\x27][^>]+href=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*href=["\x27]([^"\x27]+)["\x27].*/\1/' | head -1 | xargs)
  if [ -n "$canonical" ]; then
    echo "✅ Canonical URL: $canonical"
  else
    echo "⚠️  No canonical URL — may cause duplicate content issues"
  fi
  echo ""

  echo "=========================================="
  echo "8. WORD COUNT & CONTENT THICKNESS"
  echo "=========================================="
  word_count=$(echo "$content" | sed 's/<[^>]*>//g' | wc -w | xargs)
  echo "Approximate word count: $word_count"
  if [ "$word_count" -lt 300 ]; then
    echo "⚠️  Thin content detected (< 300 words). Google may deprioritize."
  elif [ "$word_count" -lt 600 ]; then
    echo "⚠️  Content could be improved (recommended: 600+ words)"
  else
    echo "✅ Good content depth"
  fi
  echo ""

  echo "=========================================="
  echo "9. ADDITIONAL CHECKS"
  echo "=========================================="
  # viewport
  viewport=$(echo "$content" | grep -iE '<meta[^>]+name=["\x27]viewport["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | head -1)
  [ -n "$viewport" ] && echo "✅ viewport: found" || echo "⚠️  viewport meta missing (mobile issues)"
  
  # robots
  robots=$(echo "$content" | grep -iE '<meta[^>]+name=["\x27]robots["\x27][^>]+content=["\x27]([^"\x27]+)["\x27]' | head -1)
  [ -n "$robots" ] && echo "⚠️  robots meta: $robots" || echo "✅ No robots restrictions"
  
  # lang attribute
  lang=$(echo "$content" | head -1 | grep -iE '<html[^>]+lang=["\x27]([^"\x27]+)["\x27]' | sed -E 's/.*lang=["\x27]([^"\x27]+)["\x27].*/\1/')
  [ -n "$lang" ] && echo "✅ html lang=\"$lang\"" || echo "⚠️  html lang attribute missing"

  echo ""
  echo "=========================================="
  echo "✅ SEO Analysis Complete"
  echo "=========================================="
}

# Main
if [ "$#" -eq 0 ] || [ "$1" = "-" ]; then
  # Read from stdin
  content=$(cat)
  Analyze_Stdin "$content"
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  echo "Usage:"
  echo "  curl -sL <URL> | $0 -"
  echo "  $0 <URL>"
  echo ""
  echo "Examples:"
  echo "  curl -sL https://example.com | $0 -"
  echo "  $0 https://example.com"
else
  Analyze_URL "$1"
fi
