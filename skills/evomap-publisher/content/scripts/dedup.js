/**
 * 相似度去重模块
 * 
 * EvoMap规则:
 * - 同作者相似度 >= 0.80 触发隔离
 * - 跨作者相似度 >= 0.95 触发警告
 * - 24小时内相同trigger最多5个
 */

const crypto = require('crypto');

// ========== MinHash 实现 ==========

class MinHash {
  constructor(numHashes = 128) {
    this.numHashes = numHashes;
    this.hashParams = [];
    for (let i = 0; i < numHashes; i++) {
      this.hashParams.push({
        a: Math.floor(Math.random() * 1000000) + 1,
        b: Math.floor(Math.random() * 1000000)
      });
    }
  }

  tokenize(text, n = 3) {
    const tokens = new Set();
    const words = text.toLowerCase().split(/\s+/);
    for (let i = 0; i <= words.length - n; i++) {
      tokens.add(words.slice(i, i + n).join(' '));
    }
    const chars = text.toLowerCase();
    for (let i = 0; i <= chars.length - n; i++) {
      tokens.add(chars.slice(i, i + n));
    }
    return Array.from(tokens);
  }

  signature(tokens) {
    const sig = [];
    for (let i = 0; i < this.numHashes; i++) {
      let minHash = Infinity;
      for (const token of tokens) {
        const hash = this._hash(token, this.hashParams[i]);
        if (hash < minHash) minHash = hash;
      }
      sig.push(minHash);
    }
    return sig;
  }

  _hash(str, params) {
    const h = crypto.createHash('sha256').update(str).digest();
    const val = h.readUInt32LE(0);
    return (params.a * val + params.b) % 4294967296;
  }

  similarity(sig1, sig2) {
    let matches = 0;
    for (let i = 0; i < this.numHashes; i++) {
      if (sig1[i] === sig2[i]) matches++;
    }
    return matches / this.numHashes;
  }
}

// ========== 去重管理器 ==========

class DedupManager {
  constructor(options = {}) {
    this.minHash = new MinHash(options.numHashes || 128);
    this.maxHistory = options.maxHistory || 1000;
    this.signatures = [];
    this.contentHashes = new Set();
    this.triggerUsage = new Map();
    this.lastResetDate = new Date().toDateString();
  }

  checkDailyReset() {
    const today = new Date().toDateString();
    if (today !== this.lastResetDate) {
      this.triggerUsage.clear();
      this.lastResetDate = today;
    }
  }

  computeContentHash(gene, capsule) {
    const content = JSON.stringify({
      summary: gene.summary,
      strategy: gene.strategy,
      capsuleContent: capsule.content
    });
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  check(gene, capsule) {
    this.checkDailyReset();
    
    const trigger = gene.signals_match[0];
    const triggerBase = trigger.split('_').slice(0, -2).join('_');
    const usageCount = this.triggerUsage.get(triggerBase) || 0;
    
    if (usageCount >= 5) {
      return { isDuplicate: true, reason: `trigger_dedup: 已发布${usageCount}个相同trigger (上限5个)` };
    }

    const contentHash = this.computeContentHash(gene, capsule);
    if (this.contentHashes.has(contentHash)) {
      return { isDuplicate: true, reason: 'content_hash_duplicate: 内容完全相同' };
    }

    const text = `${gene.summary} ${gene.strategy.join(' ')} ${capsule.content}`;
    const tokens = this.minHash.tokenize(text);
    const sig = this.minHash.signature(tokens);

    for (const { signature } of this.signatures) {
      const sim = this.minHash.similarity(sig, signature);
      if (sim >= 0.80) {
        return { isDuplicate: true, similarity: sim, reason: `similarity_too_high: ${(sim * 100).toFixed(1)}% >= 80%阈值` };
      }
    }

    this.signatures.push({ signature: sig });
    this.contentHashes.add(contentHash);
    this.triggerUsage.set(triggerBase, usageCount + 1);

    if (this.signatures.length > this.maxHistory) {
      this.signatures.shift();
    }

    return { isDuplicate: false };
  }
}

// ========== 内容验证 ==========

function validateContent(gene, capsule) {
  const issues = [];
  if (!gene.summary || gene.summary.length < 20) issues.push('gene.summary 必须>=20字符');
  if (!gene.strategy || gene.strategy.length < 2) issues.push('gene.strategy 必须至少2步');
  for (const step of gene.strategy || []) {
    if (step.length < 15) { issues.push('gene.strategy 每步必须>=15字符'); break; }
  }
  if (!capsule.content || capsule.content.length < 50) issues.push('capsule.content 必须>=50字符');
  if (capsule.confidence < 0.5) issues.push('capsule.confidence 必须>=0.5');
  if (!capsule.blast_radius || typeof capsule.blast_radius.files !== 'number') {
    issues.push('capsule.blast_radius.files 必须是数字');
  }
  return { valid: issues.length === 0, issues };
}

module.exports = { MinHash, DedupManager, validateContent };
