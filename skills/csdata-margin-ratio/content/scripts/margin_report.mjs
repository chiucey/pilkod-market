#!/usr/bin/env node
// margin_report.mjs — 融资融券市场每日平均维持担保比例：抓取 → 增量补数 → 生成 Excel + HTML
//
// 用法：
//   node margin_report.mjs --start 2024-01-01 --end 2026-10-27
//   node margin_report.mjs --start 2026-01-01 --end 2026-12-31 --outdir ./out
//   node margin_report.mjs --start 2024-01-01 --end 2026-10-27 --rebuild-only
//
// 参数：
//   --start / --end    起始 / 截止日期（YYYY-MM-DD），end 省略 = 今天
//   --outdir           输出目录（默认 ./output）
//   --cache            缓存目录（默认 ./cache 或 $CSDATA_MARGIN_CACHE）
//   --rebuild-only     不联网，仅用缓存里的数据重建 Excel/HTML
//   --no-index         不抓上证指数（Excel 里不写该列）
import fs from 'node:fs';
import path from 'node:path';
import { Cache } from './lib/cache.mjs';
import { scrapeIndex, downloadFile, fetchShanghaiIndex, ensureDir } from './lib/sources.mjs';
import { extractFromBuffer } from './lib/extract.mjs';
import { writeXlsx, STYLES } from './lib/xlsx-write.mjs';
import { buildHtml, resolvePlotly } from './lib/html-report.mjs';
import { mean, median, corr, linreg, round } from './lib/stats.mjs';

const SRC_LABEL = {
  daily: '融资融券市场每日数据统计',
  hist: '融资融券历史数据-日度历史数据统计',
};

function parseArgs(argv) {
  const a = { start: null, end: null, outdir: 'output', cache: null, rebuildOnly: false, withIndex: true };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--start') a.start = argv[++i];
    else if (k === '--end') a.end = argv[++i];
    else if (k === '--outdir') a.outdir = argv[++i];
    else if (k === '--cache') a.cache = argv[++i];
    else if (k === '--rebuild-only') a.rebuildOnly = true;
    else if (k === '--no-index') a.withIndex = false;
    else if (k === '--help' || k === '-h') { a.help = true; }
  }
  return a;
}

const todayStr = () => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};

function die(msg) {
  console.error(`错误: ${msg}`);
  process.exit(1);
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log('用法: node margin_report.mjs --start YYYY-MM-DD [--end YYYY-MM-DD] [--outdir DIR] [--cache DIR] [--rebuild-only] [--no-index]');
    return;
  }
  const start = args.start || die('缺少 --start');
  const end = args.end || todayStr();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(start) || !/^\d{4}-\d{2}-\d{2}$/.test(end)) die('日期格式应为 YYYY-MM-DD');
  if (start > end) die('--start 不能晚于 --end');

  const outdir = path.resolve(args.outdir);
  const cacheDir = path.resolve(args.cache || process.env.CSDATA_MARGIN_CACHE || path.join(process.cwd(), 'cache'));
  ensureDir(outdir);

  const cache = new Cache(cacheDir);
  console.log(`区间 ${start} ~ ${end}｜输出 ${outdir}｜缓存 ${cacheDir}`);

  // ---------- 1. 上证指数（同时提供交易日历） ----------
  let tradingDates = [];
  if (args.withIndex) {
    const need = cache.indexDates().filter((d) => d >= start && d <= end);
    const needAll = cache.indexDates().filter((d) => d <= end);
    const covered = needAll.length > 0 && needAll[needAll.length - 1] >= addDays(end, -3);
    if (!args.rebuildOnly && (!covered || need.length < 3)) {
      console.log('抓取上证指数日线（搜狐主源 + 新浪校验）…');
      const r = await fetchShanghaiIndex(addDays(start, -10), addDays(end, 5));
      for (const [d, c] of Object.entries(r.closes)) cache.setIndex(d, c);
      if (r.mismatched.length) {
        console.warn(`警告: 指数双源不一致 ${r.mismatched.length} 天（如 ${r.mismatched.slice(0, 3).join(', ')}）`);
      } else {
        console.log(`  指数获取 ${Object.keys(r.closes).length} 天，双源校验一致`);
      }
    }
    tradingDates = cache.indexDates().filter((d) => d >= start && d <= end);
  }

  // ---------- 2. 确定目标交易日 ----------
  // 上证指数没抓时，退化为"所有缓存中已知的日期"
  const targets = tradingDates.length ? tradingDates : cache.indexDates().filter((d) => d >= start && d <= end);

  // ---------- 3. 找源文件 URL（缺失才去抓列表页） ----------
  let urlIndex = new Map();   // date -> [{url, src}]
  const needUrls = targets.filter((d) => !cache.has(d));
  let listIndex = null;
  if (!args.rebuildOnly && needUrls.length) {
    console.log(`抓取中证数据列表页（缓存缺失 ${needUrls.length} 天）…`);
    listIndex = await scrapeIndex({ onProgress: (m) => console.log('  ' + m) });
  }
  const findEntries = (d) => {
    if (cache.get(d)?.url) return [{ url: cache.get(d).url, src: cache.get(d).src }];
    const l = listIndex && listIndex.get(d);
    return l ? l : [];
  };

  // ---------- 4. 下载并解析缺失的日期 ----------
  let downloaded = 0, failed = [], skipped = 0;
  for (const d of targets) {
    if (cache.has(d)) { skipped++; continue; }
    const entries = findEntries(d);
    if (!entries.length) { failed.push({ date: d, reason: '官网列表页无该日期' }); continue; }
    // 同一天官网可能发多个版本：优先机器格式 .xlsx（数值+百分比格式，精度更高），
    // 老的 .xls 是文本百分数（如 "249.8%"），同等条件下以后者为准会与主流口径差 0.2pp
    const ordered = [...entries].sort((a, b) => rankEntry(a.url) - rankEntry(b.url));
    let ok = false, lastErr = '', note = '';
    for (const e of ordered) {
      try {
        const buf = await downloadFile(e.url);
        const fp = cache.filePath(e.url);
        fs.writeFileSync(fp, buf);
        const parsed = extractFromBuffer(buf, path.basename(e.url));
        if (parsed.date && parsed.date !== d) {
          lastErr = `文件内日期 ${parsed.date} 与标题日期 ${d} 不一致`;
          continue;
        }
        if (ordered.length > 1) {
          note = `官网同日发布 ${ordered.length} 个版本，已取 ${path.basename(e.url).match(/\.xlsx_b?$|\.xlsx$/i) ? 'xlsx 机器格式' : 'xls 文本格式'}版本`;
        }
        cache.setRecord({
          date: d, url: e.url, src: e.src, file: path.basename(fp),
          ratio: parsed.ratio, kind: parsed.kind, fmt: parsed.fmt,
          inFileDate: parsed.date || d, note,
          fetchedAt: new Date().toISOString(),
        });
        downloaded++; ok = true; break;
      } catch (err) { lastErr = err.message; }
    }
    if (!ok) failed.push({ date: d, reason: lastErr || '未知错误' });
  }
  cache.save();
  console.log(`下载新数据 ${downloaded} 天｜命中缓存 ${skipped} 天｜失败 ${failed.length} 天`);
  failed.slice(0, 10).forEach((f) => console.warn(`  失败 ${f.date}: ${f.reason}`));

  // ---------- 5. 组装数据集 ----------
  const rows = [];
  for (const d of targets) {
    const rec = cache.get(d);
    if (!rec) continue;
    const sse = args.withIndex ? cache.sse.get(d) : null;
    if (args.withIndex && sse == null) continue;   // 指数缺失的日期先跳过，避免出残缺表
    rows.push({ date: d, ratio: rec.ratio, index: sse, rec });
  }
  if (!rows.length) die('该区间没有可用数据');

  const values = rows.map((r) => r.ratio);
  const dates = rows.map((r) => r.date);
  const idxArr = rows.map((r) => (r.index == null ? null : r.index));
  const hasIndex = idxArr.every((v) => v != null);

  const reg = linreg(values);
  const trend = values.map((_, i) => round(reg.at(i)));
  let peak = -Infinity;
  const drawdown = values.map((v) => { peak = Math.max(peak, v); return round((v / peak - 1) * 100); });

  const firstRatio = values[0], firstIdx = hasIndex ? idxArr[0] : 1;
  const normRatio = values.map((v) => round((v / firstRatio) * 100));
  const normIndex = hasIndex ? idxArr.map((v) => round((v / firstIdx) * 100)) : [];

  const byYear = new Map();
  rows.forEach((r, i) => {
    const y = r.date.slice(0, 4);
    if (!byYear.has(y)) byYear.set(y, []);
    byYear.get(y).push({ ...r, i });
  });
  const years = [...byYear.entries()].sort().map(([y, arr]) => {
    const vs = arr.map((a) => a.ratio);
    const hi = Math.max(...vs), lo = Math.min(...vs);
    const ss = arr.map((a) => a.index).filter((v) => v != null);
    return {
      year: y, n: arr.length, start: arr[0].date, end: arr[arr.length - 1].date,
      first: vs[0], last: vs[vs.length - 1], mean: round(mean(vs)),
      high: round(hi), low: round(lo),
      high_date: arr[vs.indexOf(hi)].date, low_date: arr[vs.indexOf(lo)].date,
      sse_first: ss[0], sse_last: ss[ss.length - 1],
    };
  });

  const byMonth = new Map();
  rows.forEach((r) => {
    const m = r.date.slice(0, 7);
    if (!byMonth.has(m)) byMonth.set(m, []);
    byMonth.get(m).push(r.ratio);
  });
  const months = [...byMonth.entries()].sort().map(([m, vs]) => ({
    m, v: round(mean(vs)), hi: round(Math.max(...vs)), lo: round(Math.min(...vs)),
  }));

  const idxMax = hasIndex ? idxArr.indexOf(Math.max(...idxArr)) : -1;
  const idxMin = hasIndex ? idxArr.indexOf(Math.min(...idxArr)) : -1;
  const maxI = values.indexOf(Math.max(...values));
  const minI = values.indexOf(Math.min(...values));
  const diffs = values.slice(1).map((v, i) => v - values[i]);
  const sseDiffs = hasIndex ? idxArr.slice(1).map((v, i) => v - idxArr[i]) : [];

  const stats = {
    n: rows.length, start: dates[0], end: dates[dates.length - 1],
    latest: round(values[values.length - 1]), mean: round(mean(values)), median: round(median(values)),
    max: round(values[maxI]), max_date: dates[maxI],
    min: round(values[minI]), min_date: dates[minI],
    total_change: round(values[values.length - 1] - values[0]),
    total_pct: round(((values[values.length - 1] / values[0]) - 1) * 100, 2),
    trend_slope: reg.slope, trend_desc: reg.slope > 0 ? '上升' : '下降',
    max_dd: Math.min(...drawdown), max_dd_date: dates[drawdown.indexOf(Math.min(...drawdown))],
    sse_latest: hasIndex ? round(idxArr[idxArr.length - 1], 2) : null,
    sse_first: hasIndex ? round(idxArr[0], 2) : null,
    sse_max: hasIndex ? round(idxArr[idxMax], 2) : null, sse_max_date: hasIndex ? dates[idxMax] : null,
    sse_min: hasIndex ? round(idxArr[idxMin], 2) : null, sse_min_date: hasIndex ? dates[idxMin] : null,
    sse_pct: hasIndex ? round(((idxArr[idxArr.length - 1] / idxArr[0]) - 1) * 100, 2) : null,
    corr_level: hasIndex ? round(corr(values, idxArr)) : null,
    corr_ret: hasIndex ? round(corr(diffs, sseDiffs)) : null,
  };

  // ---------- 6. 生成 Excel ----------
  const s1 = [], s2 = [];
  s1.push([
    { v: '序号', s: STYLES.HEADER }, { v: '交易日', s: STYLES.HEADER },
    { v: '平均维持担保比例(%)', s: STYLES.HEADER },
    ...(hasIndex ? [{ v: '上证指数(收盘)', s: STYLES.HEADER }] : []),
    { v: '备注', s: STYLES.HEADER },
  ]);
  rows.forEach((r, i) => {
    const note = r.rec.note || '';
    s1.push([
      { v: i + 1, s: STYLES.CENTER },
      { v: r.date, s: STYLES.DATE },
      { v: r.ratio, s: STYLES.RATIO },
      ...(hasIndex ? [{ v: r.index, s: STYLES.INDEX }] : []),
      { v: note, s: STYLES.NOTE },
    ]);
  });
  s2.push([
    { v: '交易日', s: STYLES.HEADER }, { v: '平均维持担保比例(%)', s: STYLES.HEADER },
    ...(hasIndex ? [{ v: '上证指数(收盘)', s: STYLES.HEADER }] : []),
    { v: '来源栏目', s: STYLES.HEADER }, { v: '官网源文件', s: STYLES.HEADER },
    { v: '文件内统计日期', s: STYLES.HEADER }, { v: '原始存储形式', s: STYLES.HEADER },
    { v: '备注', s: STYLES.HEADER },
  ]);
  rows.forEach((r) => {
    s2.push([
      { v: r.date, s: STYLES.DATE },
      { v: r.ratio, s: STYLES.RATIO },
      ...(hasIndex ? [{ v: r.index, s: STYLES.INDEX }] : []),
      { v: SRC_LABEL[r.rec.src] || r.rec.src, s: STYLES.DEFAULT },
      { v: r.rec.file || '', s: STYLES.DEFAULT },
      { v: r.rec.inFileDate || r.date, s: STYLES.DEFAULT },
      { v: r.rec.kind === 'text' ? '文本(百分数字符串)' : '数值(百分比格式)', s: STYLES.DEFAULT },
      { v: r.rec.note || '', s: STYLES.NOTE },
    ]);
  });

  const xlsxBuf = writeXlsx([
    {
      name: '每日平均维持担保比例',
      cols: [{ w: 7 }, { w: 13 }, { w: 21 }, ...(hasIndex ? [{ w: 15 }] : []), { w: 38 }],
      rows: s1, freeze: { row: 1, col: 0 }, autoFilter: `A1:${colLetter(s1[0].length)}${s1.length}`,
    },
    {
      name: '数据源明细',
      cols: [{ w: 13 }, { w: 21 }, ...(hasIndex ? [{ w: 15 }] : []), { w: 30 }, { w: 30 }, { w: 16 }, { w: 20 }, { w: 44 }],
      rows: s2, freeze: { row: 1, col: 0 }, autoFilter: `A1:${colLetter(s2[0].length)}${s2.length}`,
    },
  ]);
  const xlsxPath = path.join(outdir, `融资融券市场每日平均维持担保比例_${start.replace(/-/g, '')}-${end.replace(/-/g, '')}.xlsx`);
  fs.writeFileSync(xlsxPath, xlsxBuf);

  // ---------- 7. 生成 HTML ----------
  const chartData = {
    dates, values, index: hasIndex ? idxArr : [], index_chg: hasIndex ? idxArr.map((v, i) => (i ? round((v / idxArr[i - 1] - 1) * 100, 3) : 0)) : [],
    norm_ratio: normRatio, norm_index: normIndex, trend, drawdown, months, years, stats,
  };
  const plotly = await resolvePlotly(cacheDir);
  const html = buildHtml(chartData, { plotly });
  const htmlPath = path.join(outdir, `平均维持担保比例分析_${start.replace(/-/g, '')}-${end.replace(/-/g, '')}.html`);
  fs.writeFileSync(htmlPath, html);

  console.log('\n完成:');
  console.log(`  Excel: ${xlsxPath}`);
  console.log(`  HTML : ${htmlPath}`);
  console.log(`  数据 : ${rows.length} 个交易日 (${dates[0]} ~ ${dates[dates.length - 1]})`);
  console.log(`  比例 : 最新 ${stats.latest}% | 均值 ${stats.mean}% | 最高 ${stats.max}%(${stats.max_date}) | 最低 ${stats.min}%(${stats.min_date})`);
  if (hasIndex) console.log(`  指数 : 最新 ${stats.sse_latest} | 区间 ${stats.sse_pct}% | 日变化相关性 ${stats.corr_ret}`);
  if (plotly.mode === 'cdn') console.warn('  提示: plotly.js 下载失败，HTML 退回 CDN 引用（需联网打开）');
  if (failed.length) console.warn(`  提示: ${failed.length} 个交易日未能取到数据（详见上方失败列表）`);
}

/** 同日多版本排序权重：.xlsx 机器格式优先，.xls 文本格式次之 */
function rankEntry(url) {
  const u = url.toLowerCase();
  if (u.endsWith('.xlsx') || u.endsWith('.xlsx_bak')) return 0;
  if (u.endsWith('.xls')) return 1;
  return 2;
}

function colLetter(n) {
  let s = '';
  n += 1;
  while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
function addDays(dateStr, n) {
  const d = new Date(dateStr + 'T00:00:00Z');
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

main().catch((e) => { console.error(e); process.exit(1); });
