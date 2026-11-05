// cache.mjs — 增量缓存：已下载的日期不重复下载
// 目的：同一个区间跑第二次时，只补下载缺失的那些天，并把结果合并进完整区间。
import fs from 'node:fs';
import path from 'node:path';
import { ensureDir } from './sources.mjs';

export class Cache {
  constructor(dir) {
    this.dir = ensureDir(dir);
    this.filesDir = ensureDir(path.join(dir, 'files'));
    this.recordsPath = path.join(dir, 'records.jsonl');
    this.indexPath = path.join(dir, 'sse.json');
    this.records = new Map();   // date -> {date, url, src, file, ratio, kind, notes}
    this.sse = new Map();       // date -> close
    this._load();
  }

  _load() {
    if (fs.existsSync(this.recordsPath)) {
      for (const line of fs.readFileSync(this.recordsPath, 'utf8').split('\n')) {
        if (!line.trim()) continue;
        try {
          const r = JSON.parse(line);
          if (r && r.date) this.records.set(r.date, r);
        } catch { /* 跳过坏行 */ }
      }
    }
    if (fs.existsSync(this.indexPath)) {
      try {
        const o = JSON.parse(fs.readFileSync(this.indexPath, 'utf8'));
        for (const [k, v] of Object.entries(o)) this.sse.set(k, v);
      } catch { /* 忽略损坏的索引缓存 */ }
    }
  }

  has(date) { return this.records.has(date); }
  get(date) { return this.records.get(date); }
  hasIndex(date) { return this.sse.has(date); }
  indexDates() { return [...this.sse.keys()].sort(); }

  setIndex(date, close) { this.sse.set(date, close); }

  setRecord(rec) { this.records.set(rec.date, rec); }

  /** 源文件在缓存里的路径（按 url 哈希命名，避免同名冲突） */
  filePath(url) {
    const h = hash(url);
    return path.join(this.filesDir, h);
  }

  save() {
    const lines = [...this.records.values()]
      .sort((a, b) => (a.date < b.date ? -1 : 1))
      .map((r) => JSON.stringify(r));
    fs.writeFileSync(this.recordsPath, lines.join('\n') + '\n');
    const obj = {};
    for (const [k, v] of [...this.sse.entries()].sort()) obj[k] = v;
    fs.writeFileSync(this.indexPath, JSON.stringify(obj));
  }
}

export function hash(s) {
  let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
  for (let i = 0; i < s.length; i++) {
    const ch = s.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
}
