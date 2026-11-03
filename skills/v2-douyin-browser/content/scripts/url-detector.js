/**
 * Douyin URL Type Detector
 *
 * Detects and categorizes Douyin URL types for proper extraction strategy selection.
 *
 * Usage:
 *   const { detectUrlType, extractUrlParts } = require('./url-detector.js');
 *   const type = detectUrlType("https://www.douyin.com/video/734276823912...");
 */

/**
 * URL Types Enum
 */
const URL_TYPES = {
    VIDEO: 'video',
    USER: 'user',
    HASHTAG: 'hashtag',
    LIVE: 'live',
    COLLECTION: 'collection',
    SEARCH: 'search',
    UNKNOWN: 'unknown'
};

/**
 * Douyin URL Patterns
 */
const URL_PATTERNS = {
    video: [
        /douyin\.com\/video\/(\w+)/i,
        /v\.douyin\.com\/(\w+)/i,
        /www\.douyin\.com\/(\d{18,19})/i
    ],
    user: [
        /douyin\.com\/user\/([A-Za-z0-9_-]+)/i,
        /douyin\.com\/user$/i
    ],
    hashtag: [
        /douyin\.com\/tag\/([^/?]+)/i,
        /douyin\.com\/topic\/([^/?]+)/i
    ],
    live: [
        /douyin\.com\/live\/([^/?]+)/i
    ],
    collection: [
        /douyin\.com\/collection\/([^/?]+)/i
    ],
    search: [
        /douyin\.com\/search\/([^/?]+)/i
    ]
};

/**
 * Detect URL type from input
 *
 * @param {string} input - User input (may contain URL)
 * @returns {object} { type: string, url: string|null, confidence: number }
 */
function detectUrlType(input) {
    if (!input || typeof input !== 'string') {
        return { type: URL_TYPES.UNKNOWN, url: null, confidence: 0 };
    }

    // Trim and clean input
    const cleaned = input.trim();

    // Try to extract URL from mixed text
    const url = extractUrl(cleaned);

    if (!url) {
        // No URL found - might be a search query
        return {
            type: URL_TYPES.UNKNOWN,
            url: null,
            confidence: 0,
            note: 'No URL detected, treat as search query'
        };
    }

    // Detect URL type
    const type = detectFromUrl(url);

    return {
        type: type,
        url: url,
        confidence: type !== URL_TYPES.UNKNOWN ? 1 : 0.5,
        originalInput: cleaned
    };
}

/**
 * Extract URL from mixed text
 *
 * @param {string} text - Text that may contain URL
 * @returns {string|null} Extracted URL or null
 */
function extractUrl(text) {
    // Common URL patterns
    const urlPattern = /(?:https?:\/\/)?(?:www\.)?douyin\.com\/[^\s<>"]+/gi;
    const matches = text.match(urlPattern);

    if (matches && matches.length > 0) {
        // Return the longest match (most likely the full URL)
        let url = matches.reduce((a, b) => a.length > b.length ? a : b);

        // Add protocol if missing
        if (!url.startsWith('http')) {
            url = 'https://' + url;
        }

        return url;
    }

    // Check for bare video ID (18-19 digits)
    const videoIdPattern = /^(\d{18,19})$/;
    if (videoIdPattern.test(text)) {
        return `https://www.douyin.com/video/${text}`;
    }

    return null;
}

/**
 * Detect URL type from URL string
 *
 * @param {string} url - Clean URL
 * @returns {string} URL type
 */
function detectFromUrl(url) {
    const urlLower = url.toLowerCase();

    // Video detection (most common)
    if (urlLower.includes('/video/') || urlLower.includes('v.douyin')) {
        return URL_TYPES.VIDEO;
    }

    // User profile detection
    if (urlLower.includes('/user/')) {
        return URL_TYPES.USER;
    }

    // Hashtag/Topic detection
    if (urlLower.includes('/tag/') || urlLower.includes('/topic/')) {
        return URL_TYPES.HASHTAG;
    }

    // Live stream detection
    if (urlLower.includes('/live/')) {
        return URL_TYPES.LIVE;
    }

    // Collection detection
    if (urlLower.includes('/collection/')) {
        return URL_TYPES.COLLECTION;
    }

    // Search detection
    if (urlLower.includes('/search/')) {
        return URL_TYPES.SEARCH;
    }

    return URL_TYPES.UNKNOWN;
}

/**
 * Extract parts from URL
 *
 * @param {string} url - Douyin URL
 * @returns {object} Extracted parts
 */
function extractUrlParts(url) {
    if (!url) return null;

    const parts = {
        fullUrl: url,
        type: detectFromUrl(url),
        id: null,
        slug: null,
        params: {}
    };

    // Extract path segments
    try {
        const urlObj = new URL(url.startsWith('http') ? url : 'https://' + url);
        const path = urlObj.pathname;

        // Extract video ID
        const videoMatch = path.match(/\/video\/(\w+)/);
        if (videoMatch) {
            parts.id = videoMatch[1];
        }

        // Extract user ID
        const userMatch = path.match(/\/user\/([A-Za-z0-9_-]+)/);
        if (userMatch) {
            parts.id = userMatch[1];
        }

        // Extract hashtag/topic
        const tagMatch = path.match(/\/(?:tag|topic)\/([^/?]+)/);
        if (tagMatch) {
            parts.slug = decodeURIComponent(tagMatch[1]);
        }

        // Extract query parameters
        urlObj.searchParams.forEach((value, key) => {
            parts.params[key] = value;
        });

    } catch (e) {
        // URL parsing failed, return basic info
    }

    return parts;
}

/**
 * Validate if URL is accessible Douyin URL
 *
 * @param {string} url - URL to validate
 * @returns {boolean} True if valid
 */
function isValidDouyinUrl(url) {
    if (!url) return false;

    const urlLower = url.toLowerCase();
    return urlLower.includes('douyin.com');
}

/**
 * Convert short URL to full URL (placeholder for URL expansion)
 *
 * @param {string} shortUrl - Shortened URL
 * @returns {string} Expanded URL
 */
async function expandUrl(shortUrl) {
    // This would typically use a URL expander service
    // For now, return as-is
    return shortUrl;
}

/**
 * Get extraction strategy for URL type
 *
 * @param {string} type - URL type
 * @returns {object} Strategy configuration
 */
function getStrategy(type) {
    const strategies = {
        [URL_TYPES.VIDEO]: {
            primary: 'extract_content',
            mode: 'browser_only',
            prompt: 'Extract video metadata including title, author, stats, description, hashtags',
            fallback: 'batch_web_search',
            fallbackPrompt: 'Search for video title and basic info'
        },
        [URL_TYPES.USER]: {
            primary: 'extract_content',
            mode: 'browser_only',
            prompt: 'Extract user profile including nickname, bio, follower count, video count',
            fallback: 'batch_web_search',
            fallbackPrompt: 'Search for user info by name'
        },
        [URL_TYPES.HASHTAG]: {
            primary: 'extract_content',
            mode: 'browser_only',
            prompt: 'Extract hashtag info including name, video count, trending status',
            fallback: 'batch_web_search',
            fallbackPrompt: 'Search for hashtag topic'
        },
        [URL_TYPES.LIVE]: {
            primary: null,
            mode: null,
            unsupported: true,
            message: 'Live streams are not supported for extraction'
        },
        [URL_TYPES.SEARCH]: {
            primary: 'extract_content',
            mode: 'browser_only',
            prompt: 'Extract search results including video titles, authors, links',
            fallback: null
        },
        [URL_TYPES.UNKNOWN]: {
            primary: 'batch_web_search',
            fallback: null,
            note: 'Try as search query'
        }
    };

    return strategies[type] || strategies[URL_TYPES.UNKNOWN];
}

// Export for use in skill
module.exports = {
    URL_TYPES,
    detectUrlType,
    extractUrl,
    detectFromUrl,
    extractUrlParts,
    isValidDouyinUrl,
    expandUrl,
    getStrategy
};

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log('Usage: node url-detector.js <douyin-url-or-text>');
        console.log('');
        console.log('Examples:');
        console.log('  node url-detector.js https://www.douyin.com/video/734276823912');
        console.log('  node url-detector.js "Check this: https://douyin.com/user/abc123"');
        console.log('  node url-detector.js 734276823912');
        process.exit(0);
    }

    const input = args.join(' ');
    const result = detectUrlType(input);
    const parts = extractUrlParts(result.url || input);
    const strategy = getStrategy(result.type);

    console.log('URL Detection Result:');
    console.log(JSON.stringify({
        input: input,
        detection: result,
        parts: parts,
        strategy: strategy
    }, null, 2));
}
