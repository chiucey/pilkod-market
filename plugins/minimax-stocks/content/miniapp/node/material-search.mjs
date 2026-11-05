// @ts-check
// 个股资料匹配的正文检索：文本类文件直接读、Office 文档抽取 XML 文本（带缓存）；macOS 另用 Spotlight（mdfind）
// 覆盖 PDF 等自己读不了的格式。只读、限时、限量；只返回关键词命中，不判断相关度（相关度交给 Agent）。
import { execFile } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { MAX_OFFICE_BYTES, extractOfficeText } from './office-text.mjs';

const TEXT_EXT = new Set(['.md', '.markdown', '.txt', '.csv', '.html', '.htm', '.rtf']);
const OFFICE_EXT = new Set(['.docx', '.pptx', '.xlsx']);
const MAX_TEXT_FILE = 4 * 1024 * 1024;
const CACHE_LIMIT = 60_000_000;
const SPOTLIGHT_TIMEOUT_MS = 5_000;

/**
 * @param {{ platform?: string, run?: (command: string, args: string[]) => Promise<{ code: number | string, stdout: string }> }} [options]
 */
export function createMaterialSearch({ platform = process.platform, run } = {}) {
  /** @type {Map<string, string>} */
  const cache = new Map();
  let cacheSize = 0;
  /** @type {Set<import('node:child_process').ChildProcess>} */
  const children = new Set();
  let spotlightOk = platform === 'darwin';
  const exec = run ?? ((command, args) => new Promise((resolve) => {
    const child = execFile(command, args, { timeout: SPOTLIGHT_TIMEOUT_MS, maxBuffer: 8 * 1024 * 1024 }, (error, stdout) => {
      children.delete(child);
      resolve({ code: error ? (/** @type {any} */ (error).code ?? 1) : 0, stdout: String(stdout ?? '') });
    });
    children.add(child);
  }));

  async function fileText(file) {
    const cacheKey = file.path + '|' + file.size + '|' + file.mtimeMs;
    const cached = cache.get(cacheKey);
    if (cached !== undefined) { cache.delete(cacheKey); cache.set(cacheKey, cached); return cached; }
    let text = '';
    if (TEXT_EXT.has(file.ext) && file.size <= MAX_TEXT_FILE) text = await readFile(file.path, 'utf8').catch(() => '');
    else if (OFFICE_EXT.has(file.ext) && file.size <= MAX_OFFICE_BYTES) text = await extractOfficeText(file.path, file.ext).catch(() => '');
    text = text.normalize('NFKC').toLowerCase();
    cache.set(cacheKey, text);
    cacheSize += text.length;
    for (const [key, value] of cache) {
      if (cacheSize <= CACHE_LIMIT) break;
      cache.delete(key);
      cacheSize -= value.length;
    }
    return text;
  }

  /** @param {string[]} roots @param {string[]} keys @returns {Promise<Map<string, Set<string>>>} */
  async function spotlight(roots, keys) {
    /** @type {Map<string, Set<string>>} */
    const hits = new Map();
    if (!spotlightOk || !roots.length || !keys.length) return hits;
    const jobs = roots.flatMap((root) => keys.map((key) => ({ root, key })));
    for (let i = 0; i < jobs.length; i += 4) {
      const results = await Promise.all(jobs.slice(i, i + 4).map(async ({ root, key }) => ({ key, result: await exec('mdfind', ['-onlyin', root, key]) })));
      for (const { key, result } of results) {
        if (result.code === 'ENOENT') { spotlightOk = false; return hits; }
        if (result.code !== 0) continue;
        for (const line of result.stdout.split('\n')) {
          const path = line.trim();
          if (!path) continue;
          if (!hits.has(path)) hits.set(path, new Set());
          hits.get(path).add(key);
        }
      }
    }
    return hits;
  }

  /**
   * @param {{ files: { path: string, ext: string, size: number, mtimeMs: number }[], roots: string[], keys: string[], spotlightKeys?: string[], deadlineMs?: number }} input
   * @returns {Promise<{ hits: Map<string, { key: string, count: number, via: 'text' | 'spotlight' }[]>, scanned: number, readable: number, partial: boolean, spotlight: boolean }>}
   */
  async function search({ files, roots, keys, spotlightKeys = keys, deadlineMs = 3500 }) {
    const deadline = Date.now() + deadlineMs;
    const lowered = keys.map((key) => key.normalize('NFKC').toLowerCase()).filter(Boolean);
    /** @type {Map<string, { key: string, count: number, via: 'text' | 'spotlight' }[]>} */
    const hits = new Map();
    const readable = files.filter((file) => TEXT_EXT.has(file.ext) || OFFICE_EXT.has(file.ext));
    let scanned = 0;
    let partial = false;
    for (const file of readable) {
      if (Date.now() > deadline) { partial = true; break; }
      const text = await fileText(file);
      scanned += 1;
      if (!text) continue;
      for (let i = 0; i < lowered.length; i += 1) {
        const needle = lowered[i];
        let count = 0;
        let at = text.indexOf(needle);
        while (at !== -1 && count < 50) { count += 1; at = text.indexOf(needle, at + needle.length); }
        if (count) {
          if (!hits.has(file.path)) hits.set(file.path, []);
          hits.get(file.path).push({ key: keys[i], count, via: 'text' });
        }
      }
    }
    const known = new Set(files.map((file) => file.path));
    // Spotlight 每个关键词起一个 mdfind，关键词多时只用最重要的几个。
    const spotted = await spotlight(roots, spotlightKeys);
    for (const [path, found] of spotted) {
      if (!known.has(path) || hits.has(path)) continue;
      hits.set(path, [...found].map((key) => ({ key, count: 1, via: 'spotlight' })));
    }
    return { hits, scanned, readable: readable.length, partial, spotlight: spotlightOk };
  }

  return {
    search,
    get spotlightAvailable() { return spotlightOk; },
    dispose() {
      for (const child of children) child.kill('SIGTERM');
      children.clear();
      cache.clear();
    },
  };
}
