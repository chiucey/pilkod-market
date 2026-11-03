/**
 * Cache Manager - Smart Cache Management
 * Uses Ring Buffer for fixed memory, with safe key generation
 */
const fs = require('fs');
const path = require('path');

/**
 * Ring Buffer - Fixed-size circular buffer
 */
class RingBuffer {
  constructor(maxSize) {
    this.maxSize = maxSize;
    this.buffer = [];
    this.index = 0;
  }

  push(item) {
    if (this.buffer.length < this.maxSize) {
      this.buffer.push(item);
    } else {
      this.buffer[this.index] = item;
    }
    this.index = (this.index + 1) % this.maxSize;
  }

  toArray() {
    if (this.buffer.length < this.maxSize) {
      return [...this.buffer];
    }
    return [...this.buffer.slice(this.index), ...this.buffer.slice(0, this.index)];
  }

  get length() {
    return Math.min(this.buffer.length, this.maxSize);
  }
}

class CacheManager {
  constructor(config = {}) {
    this.maxSize = config.maxSize || 10000;
    this.ttl = config.ttl || 1800; // 30 minutes
    this.cache = new Map();
    this.stats = new RingBuffer(1000);
    this.dataDir = config.dataDir || path.join(__dirname, '..', '.openclaw', 'data');
    this.cacheFile = path.join(this.dataDir, 'cache.json');

    this.loadFromDisk();
  }

  /**
   * Generate safe cache key - Object key sorting
   */
  generateKey(data) {
    return JSON.stringify(data, Object.keys(data).sort());
  }

  /**
   * Check if cache exists and is valid
   */
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    const now = Date.now();
    if (now - item.timestamp > this.ttl * 1000) {
      this.cache.delete(key);
      return null;
    }

    // Record hit
    this.stats.push({ hit: true, timestamp: now });
    return item.value;
  }

  /**
   * Set cache
   */
  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      // Use LRU strategy to delete oldest
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });

    this.stats.push({ hit: false, timestamp: Date.now() });
    this.saveToDisk();
  }

  /**
   * Get cache hit rate
   */
  getHitRate() {
    const arr = this.stats.toArray();
    if (arr.length === 0) return 0;
    const hits = arr.filter(s => s.hit).length;
    return (hits / arr.length * 100).toFixed(1);
  }

  /**
   * Load cache from disk
   */
  loadFromDisk() {
    try {
      if (fs.existsSync(this.cacheFile)) {
        const data = JSON.parse(fs.readFileSync(this.cacheFile, 'utf8'));
        const now = Date.now();

        for (const [key, item] of Object.entries(data)) {
          if (now - item.timestamp < this.ttl * 1000) {
            this.cache.set(key, item);
          }
        }
      }
    } catch (e) {
      // Ignore load errors
    }
  }

  /**
   * Save cache to disk
   */
  saveToDisk() {
    try {
      const data = Object.fromEntries(this.cache);
      fs.mkdirSync(path.dirname(this.cacheFile), { recursive: true });
      fs.writeFileSync(this.cacheFile, JSON.stringify(data));
    } catch (e) {
      // Ignore save errors
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate: this.getHitRate() + '%'
    };
  }
}

module.exports = CacheManager;
