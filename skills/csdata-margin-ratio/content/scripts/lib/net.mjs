// net.mjs — HTTP 抓取：gzip 解压、重试、缓存破坏参数
// 缓存破坏很关键：中证数据列表页在带 Accept-Encoding: gzip 时会命中陈旧缓存，
// 返回缺少最新条目的旧版本；加随机 query 可稳定拿到新版本。
import https from 'node:https';
import zlib from 'node:zlib';
import { gunzipSync, inflateSync } from 'node:zlib';

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

function request(url, { headers = {}, timeout = 45000, redirects = 5 } = {}) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers: { 'User-Agent': UA, ...headers } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        if (redirects <= 0) return reject(new Error('too many redirects'));
        return resolve(request(new URL(res.headers.location, url).toString(), { headers, timeout, redirects: redirects - 1 }));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const buf = Buffer.concat(chunks);
        const enc = String(res.headers['content-encoding'] || '').toLowerCase();
        let body = buf;
        try {
          if (enc === 'gzip') body = gunzipSync(buf);
          else if (enc === 'deflate') body = inflateSync(buf);
        } catch { /* 解压失败就用原始字节 */ }
        resolve({ status: res.statusCode, headers: res.headers, body });
      });
    });
    req.setTimeout(timeout, () => { req.destroy(new Error('timeout ' + url)); });
    req.on('error', reject);
  });
}

export async function fetchBuffer(url, { headers = {}, tries = 4, timeout = 45000 } = {}) {
  let last;
  for (let i = 0; i < tries; i++) {
    try {
      const r = await request(url, { headers, timeout });
      if (r.status !== 200) throw new Error('HTTP ' + r.status);
      return r.body;
    } catch (e) {
      last = e;
      await new Promise((r) => setTimeout(r, 800 * (i + 1)));
    }
  }
  throw new Error(`抓取失败 ${url}: ${last && last.message}`);
}

/** 抓文本（默认 utf-8） */
export async function fetchText(url, opts = {}) {
  const buf = await fetchBuffer(url, opts);
  return buf.toString('utf8');
}

/**
 * 抓列表页：显式声明 Accept-Encoding: identity（带 gzip 会命中陈旧缓存）
 * 并追加随机 query 破缓存。
 */
export async function fetchFresh(url, opts = {}) {
  const sep = url.includes('?') ? '&' : '?';
  const busted = `${url}${sep}t=${Date.now().toString(36)}${Math.floor(Math.random() * 1e6)}`;
  return fetchText(busted, {
    headers: { 'Accept-Encoding': 'identity', 'Accept-Language': 'zh-CN,zh;q=0.9', Referer: 'https://www.csdata.cn/' },
    ...opts,
  });
}
