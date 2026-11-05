// sources.mjs — 中证数据列表页/文件下载 + 上证指数
import fs from 'node:fs';
import path from 'node:path';
import { fetchFresh, fetchBuffer } from './net.mjs';

export const BASE = 'https://www.csdata.cn';
export const DAILY_LIST = `${BASE}/cmsmc/cgfb/rzrqsj/rzrqscmrsjtj/d2bb5c19-%d.html`;
export const HIST_LIST = `${BASE}/cmsmc/cgfb/rzrqsj/rzrqsclssj/rzrqscmrsjtj/5cb2feab-%d.html`;

/**
 * 解析列表页 → [{date, src, url}]
 * 来源归属取自「列表页所在栏目」，不是文件 URL：
 * 文件路径统一是 /cmsmc/articleFileDir/...，里面没有任何栏目名，从 URL 猜栏目必然全错。
 */
export function parseListPage(html, src) {
  const out = [];
  const liRe = /<li>([\s\S]*?)<\/li>/g;
  let m;
  while ((m = liRe.exec(html))) {
    const blk = m[1];
    const title = /融资融券市场每日数据统计(\d{8})/.exec(blk);
    const href = /<a[^>]*href="([^"]+)"/.exec(blk);
    if (!title || !href) continue;
    const t = title[1];
    const date = `${t.slice(0, 4)}-${t.slice(4, 6)}-${t.slice(6, 8)}`;
    const url = href[1].startsWith('/') ? BASE + href[1] : href[1];
    out.push({ date, src, url, tdate: t });
  }
  return out;
}

/**
 * 抓两个栏目的列表页，多轮取并集。
 * 站点列表页有多个缓存节点，同一 URL 不同次返回的条目数可能不同（甚至缺最新几条），
 * 所以要多轮 + 取并集；缺哪条后面会用交易日历再兜底校验。
 */
export async function scrapeIndex({ rounds = 3, onProgress } = {}) {
  const jobs = [];
  for (let p = 1; p <= 41; p++) jobs.push({ src: 'daily', page: p, url: DAILY_LIST.replace('%d', p) });
  for (let p = 1; p <= 14; p++) jobs.push({ src: 'hist', page: p, url: HIST_LIST.replace('%d', p) });

  const byDate = new Map();
  for (let round = 1; round <= rounds; round++) {
    const results = await Promise.all(jobs.map(async (j) => {
      try {
        const html = await fetchFresh(j.url);
        return { j, items: parseListPage(html, j.src) };
      } catch {
        return { j, items: [] };
      }
    }));
    let added = 0;
    for (const { items } of results) {
      for (const it of items) {
        if (!byDate.has(it.date)) { byDate.set(it.date, []); added++; }
        const list = byDate.get(it.date);
        if (!list.some((x) => x.url === it.url)) list.push(it);
      }
    }
    if (onProgress) onProgress(`第 ${round} 轮列表抓取：累计 ${byDate.size} 个日期（新增 ${added}）`);
    if (added === 0) break;
  }

  const index = new Map();
  for (const [date, list] of byDate) index.set(date, list);
  return index;
}

/** 下载单个源文件 */
export async function downloadFile(url) {
  const buf = await fetchBuffer(url, { headers: { 'Accept-Encoding': 'identity', Referer: BASE + '/' } });
  if (buf.length < 500) throw new Error(`文件过小(${buf.length}B)，可能下载失败: ${url}`);
  return buf;
}

/** 上证指数收盘：搜狐为主源(交易所2位小数)，新浪为校验源(3位) */
export async function fetchShanghaiIndex(from, to) {
  const sohuUrl = `https://q.stock.sohu.com/hisHq?code=zs_000001&start=${from.replace(/-/g, '')}&end=${to.replace(/-/g, '')}&stat=1&order=D&period=d&rt=jsonp`;
  const sohuRaw = (await fetchBuffer(sohuUrl, { headers: { 'Accept-Encoding': 'identity' } })).toString('utf8');
  const m = /hq":\[([\s\S]*?)\],"code/.exec(sohuRaw) || /hq":\[([\s\S]*?)\]/.exec(sohuRaw);
  if (!m) throw new Error('搜狐指数接口返回异常');
  const sohu = {};
  for (const r of m[1].matchAll(/\[("[\d-]+",[^\]]+)\]/g)) {
    const f = [...r[1].matchAll(/"([^"]*)"/g)].map((x) => x[1]);
    sohu[f[0]] = Number(f[2]);
  }

  // 新浪校验
  const sinaUrl = 'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=1400';
  let sina = {};
  try {
    const sinaRaw = (await fetchBuffer(sinaUrl, { headers: { 'Accept-Encoding': 'identity', Referer: 'https://finance.sina.com.cn' } })).toString('utf8');
    const arr = JSON.parse(sinaRaw.replace(/(\w+):/g, '"$1":'));
    for (const x of arr) sina[x.day] = Number(x.close);
  } catch { /* 校验源失败不阻断主流程 */ }

  const mismatched = Object.keys(sohu).filter((d) => sina[d] != null && Math.abs(sina[d] - sohu[d]) > 0.011);
  return { closes: sohu, validate: sina, mismatched, validated: Object.keys(sina).length > 0 };
}

export function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
  return d;
}
