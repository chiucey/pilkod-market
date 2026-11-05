#!/usr/bin/env node
'use strict';
// shenzhen-tender-info MCP server — 深圳公共资源交易网（szggzy.com）项目进度查询与评标资料下载
// 接口经实测：POST /cms/api/v1/trade/content/page、GET /cms/api/v1/trade/content/detail
// 附件直链 file.szggzy.com/tradeapi/file/gd-file/unified_download（免登录，实测返回 application/pdf）。
// 仅覆盖深圳本地平台，不接入其他地区或全国性交易平台。

import fs from 'node:fs';
import path from 'node:path';

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36';
const CMS = 'https://www.szggzy.com/cms';
const SITE = 'https://www.szggzy.com';

// 渠道 id 取自网站 config.js 的 channel 映射
const CHANNELS = {
  jsgc: { id: '2851', label: '建设工程' },
  zfcg: { id: '2850', label: '政府采购' },
  tdky: { id: '2852', label: '土地矿业' },
  cqjy: { id: '2853', label: '产权交易' },
  ygcg: { id: '4161', label: '阳光采购' },
  yyhc: { id: '2856', label: '医用耗材' },
  ypjy: { id: '3496', label: '药品交易' }
};

// 阶段表：按公告类型代码前缀匹配，order 越大越靠后
const STAGE_TABLE = [
  { code: 'jsgc_zbgg_bggg', label: '答疑、补遗', stage: '投标中', order: 0 },
  { code: 'jsgc_zbkzjgs', label: '最高投标限价公示', stage: '投标中', order: 0 },
  { code: 'jsgc_zbgg', label: '招标公告', stage: '投标中', order: 0 },
  { code: 'jsgc_kbgs_jbxx', label: '截标信息', stage: '已截标', order: 1 },
  { code: 'jsgc_kbgs_kbqkgs', label: '开标情况公示', stage: '已开标', order: 2 },
  { code: 'jsgc_zsjyjgs', label: '资审及业绩公示', stage: '评标中', order: 3 },
  { code: 'jsgc_pbgs_pbwyhgs', label: '评标委员会公示', stage: '评标中', order: 3 },
  { code: 'jsgc_pbgs_pbbggs', label: '评标报告公示', stage: '评标完成', order: 4 },
  { code: 'jsgc_dbgs_dbjggs', label: '定标结果公示', stage: '已定标', order: 5 },
  { code: 'jsgc_dbgs_zbjggs', label: '中标结果公示', stage: '已中标', order: 6 },
  { code: 'jsgc_qtgs_qtlgs', label: '其他类公示', stage: '公告', order: 0 },
  { code: 'zfcg_zbcjjggs', label: '中标（成交）结果公示', stage: '已中标', order: 6 },
  { code: 'zfcggggg', label: '采购结果公告', stage: '已中标', order: 6 },
  { code: 'zfcg_zbcg', label: '采购公告', stage: '投标中', order: 0 },
  { code: 'zfcg_zxcg', label: '采购意向公开', stage: '意向阶段', order: 0 },
  { code: 'zfcg_qtgg', label: '其他公告', stage: '公告', order: 0 }
];

const STAGE_NAMES = ['意向阶段', '投标中', '已截标', '已开标', '评标中', '评标完成', '已定标', '已中标'];

// 附件用途分类
const DOC_CLASS = [
  { key: 'kbreport', label: '开标报告', match: ['开标情况记录', '开标记录表', '开标一览表', '开标情况', '开标记录'] },
  { key: 'pingbiao', label: '评标报告', match: ['评标报告', '评标汇总', '技术组评标', '商务组评标', '评分结果表', '评审报告', '评标委员会名单'] },
  { key: 'zhongbiao', label: '中标信息', match: ['中标结果公告', '中标结果公示', '定标结果', '中标（成交）结果', '采购结果公告', '中标通知书', '定标结果表'] },
  { key: 'zixing', label: '资信与资格文件', match: ['资信标文件', '资格审查文件', '资格性审查表', '符合性审查表', '业绩文件', '投标文件资格性', '投标文件符合性'] },
  { key: 'qita', label: '其他附件', match: [] }
];

function classifyDoc(name) {
  const n = String(name || '');
  for (let i = 0; i < DOC_CLASS.length; i++) {
    const m = DOC_CLASS[i].match;
    for (let j = 0; j < m.length; j++) {
      if (n.indexOf(m[j]) >= 0) return DOC_CLASS[i].key;
    }
  }
  return 'qita';
}

function htmlToText(html) {
  if (!html) return '';
  return String(html)
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#(\d+);/g, function (m, c) { return String.fromCharCode(Number(c)); })
    .replace(/\s+/g, ' ')
    .trim();
}

function extractLinks(html) {
  const out = [];
  if (!html) return out;
  const re = /href="([^"]+)"[^>]*>([^<]*)<\/a>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const href = m[1].replace(/&amp;/g, '&');
    const label = htmlToText(m[2]);
    if (/unified_download|\.pdf|\.zip|\.doc|\.xls/i.test(href) || /\.(pdf|zip|doc|docx|xls|xlsx)$/i.test(label)) {
      out.push({ href: href, label: label || decodeURIComponent(href.split('?')[0].split('/').pop()) });
    }
  }
  return out;
}

// 政府采购静态站：附件受图形验证码保护，无法程序化下载
const ZFCG_BASE = 'http://zfcg.szggzy.com:8081';
const ZFCG_ATTACH = '/EpointWebBuilder/pages/webbuildermis/attach/downloadztbattach';

function extractZfcgAttachments(html) {
  const out = [];
  const re = /<a[^>]*onclick="[^"]*downloadztbattach[^"]*"[^>]*>([^<]*)<\/a>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const oc = /onclick="([^"]*)"/.exec(m[0]);
    const pm = /['"](\/EpointWebBuilder\/[^'"]+)['"]/.exec(oc ? oc[1] : '');
    const label = htmlToText(m[1]);
    out.push({
      name: label,
      url: pm ? (ZFCG_BASE + pm[1].replace(/&amp;/g, '&')) : '',
      docClass: classifyDoc(label),
      captchaProtected: true
    });
  }
  return out;
}
function attrMap(attrs) {
  const m = {};
  (attrs || []).forEach(function (a) { m[a.attrName] = a.attrValue; });
  return m;
}

async function httpJson(url, method, body) {
  const ctl = new AbortController();
  const timer = setTimeout(function () { ctl.abort(); }, 25000);
  try {
    const opt = {
      method: method || 'GET',
      headers: { 'User-Agent': UA, 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'zh-CN,zh;q=0.9', Referer: SITE + '/' },
      signal: ctl.signal
    };
    if (body) { opt.headers['Content-Type'] = 'application/json;charset=UTF-8'; opt.body = JSON.stringify(body); }
    const res = await fetch(url, opt);
    const text = await res.text();
    let json = null;
    try { json = JSON.parse(text); } catch (e) { json = null; }
    if (!json) throw new Error('接口返回非 JSON (HTTP ' + res.status + '): ' + text.slice(0, 120));
    if (json.code !== 200) throw new Error('接口 code=' + json.code + ' message=' + (json.message || ''));
    return json;
  } finally { clearTimeout(timer); }
}

async function searchPage(opts) {
  const body = { channelId: String(opts.channelId), current: opts.current || 1, size: opts.size || 20 };
  if (opts.title) body.title = opts.title;
  if (opts.jsgcProjectType) body.jsgcProjectType = opts.jsgcProjectType;
  const j = await httpJson(CMS + '/api/v1/trade/content/page', 'POST', body);
  const d = j.data || {};
  return { content: d.content || [], totalElements: d.totalElements, totalPages: d.totalPages, size: d.size };
}

async function fetchDetail(contentId) {
  const j = await httpJson(CMS + '/api/v1/trade/content/detail?contentId=' + encodeURIComponent(contentId), 'GET');
  return j.data || {};
}

function stageOf(item) {
  const code = String(item.noticeTypeCode || '');
  const name = String(item.noticeTypeName || '');
  for (let i = 0; i < STAGE_TABLE.length; i++) {
    if (code && code.indexOf(STAGE_TABLE[i].code) === 0) return STAGE_TABLE[i];
  }
  for (let i = 0; i < STAGE_TABLE.length; i++) {
    if (name && name === STAGE_TABLE[i].label) return STAGE_TABLE[i];
  }
  return { code: code, label: name || '其他公告', stage: '公告', order: 0 };
}

function normalizeItem(x) {
  const s = stageOf(x);
  return {
    contentId: x.id,
    title: x.noticeTitle || x.title,
    noticeType: x.noticeTypeName,
    noticeTypeCode: x.noticeTypeCode,
    stage: s.stage,
    stageOrder: s.order,
    projectCode: x.projectCode || '',
    bidSectionNumber: x.bidSectionNumber || '',
    region: x.projectRegion || '',
    releaseTime: x.releaseTime,
    winningBidder: x.winningBidder || x.winnerName || '',
    purchaseCom: x.purchaseCom || '',
    tenderer: x.tenderer || '',
    constructCompany: x.constructCompany || '',
    projectType: x.projectType || '',
    tradeType: x.tradeType || '',
    url: SITE + '/jygg/details.html?contentId=' + x.id,
    staticUrl: x.linkTo || '',
    noticeId: x.noticeId || '',
    noticeTypeCode: x.noticeTypeCode || '',
    captchaProtected: /zfcg\.szggzy\.com/.test(x.linkTo || '')
  };
}

async function toolProjectProgress(args) {
  const title = String(args.title || '').trim();
  if (!title) throw new Error('必须提供 title（工程名称关键词）');
  const scope = args.scope === 'zfcg' ? 'zfcg' : (args.scope === 'all' ? 'all' : 'jsgc');
  const size = Math.min(Math.max(Number(args.size) || 30, 1), 100);
  const channels = scope === 'all' ? ['jsgc', 'zfcg'] : [scope];
  const all = [];
  const errors = [];
  for (let i = 0; i < channels.length; i++) {
    const key = channels[i];
    try {
      const res = await searchPage({ channelId: CHANNELS[key].id, title: title, size: size });
      (res.content || []).forEach(function (x) {
        const n = normalizeItem(x);
        n.scope = key;
        n.scopeLabel = CHANNELS[key].label;
        all.push(n);
      });
    } catch (e) {
      errors.push(CHANNELS[key].label + ': ' + String(e && e.message || e));
    }
  }
  if (!all.length && errors.length) throw new Error(errors.join('; '));

  // 按项目编号聚合，同一工程可能有多个标段
  const groups = {};
  all.forEach(function (n) {
    const key = n.projectCode || n.bidSectionNumber || ('_' + n.title);
    if (!groups[key]) {
      groups[key] = { projectCode: n.projectCode, bidSectionNumber: n.bidSectionNumber, projectName: n.title, region: n.region, scope: n.scope, scopeLabel: n.scopeLabel, items: [] };
    }
    groups[key].items.push(n);
  });

  const projects = Object.keys(groups).map(function (k) {
    const g = groups[k];
    g.items.sort(function (a, b) { return String(a.releaseTime || '').localeCompare(String(b.releaseTime || '')); });
    // 当前阶段 = 该项目到达过的最深阶段
    let deepest = g.items[0];
    g.items.forEach(function (it) { if (it.stageOrder > deepest.stageOrder) deepest = it; });
    g.currentStage = deepest.stage;
    g.stageIndex = STAGE_NAMES.indexOf(deepest.stage);
    g.stageTotal = STAGE_NAMES.length;
    g.bidClosed = deepest.stageOrder >= 1;
    g.enteredEvaluation = deepest.stageOrder >= 2;
    g.timeline = g.items.map(function (it) {
      return { stage: it.stage, noticeType: it.noticeType, title: it.title, releaseTime: it.releaseTime, contentId: it.contentId, url: it.url };
    });
    g.availableDocs = g.items.filter(function (it) {
      return /评标报告|开标情况|中标结果|定标结果|采购结果|中标（成交）结果/.test(it.noticeType || '');
    }).map(function (it) {
      let dc = 'zhongbiao';
      if (it.noticeType.indexOf('开标') >= 0) dc = 'kbreport';
      else if (it.noticeType.indexOf('评标') >= 0) dc = 'pingbiao';
      return {
        docClass: dc,
        contentId: it.contentId,
        noticeType: it.noticeType,
        noticeTypeCode: it.noticeTypeCode,
        title: it.title,
        releaseTime: it.releaseTime,
        url: it.url,
        staticUrl: it.staticUrl,
        noticeId: it.noticeId,
        captchaProtected: it.captchaProtected
      };
    });
    return g;
  });
  projects.sort(function (a, b) { return (b.stageIndex - a.stageIndex) || String(b.timeline[b.timeline.length - 1].releaseTime || '').localeCompare(String(a.timeline[a.timeline.length - 1].releaseTime || '')); });

  return {
    query: title,
    scope: scope,
    platform: '深圳公共资源交易网 szggzy.com',
    fetchedAt: new Date().toISOString(),
    matchCount: all.length,
    projectCount: projects.length,
    errors: errors,
    projects: projects
  };
}

async function toolListNotices(args) {
  const channelId = args.channelId || CHANNELS.jsgc.id;
  const size = Math.min(Math.max(Number(args.size) || 20, 1), 100);
  const current = Math.max(Number(args.current) || 1, 1);
  const res = await searchPage({ channelId: channelId, title: args.title || '', current: current, size: size, jsgcProjectType: args.jsgcProjectType });
  return {
    channelId: channelId,
    current: current,
    size: size,
    totalElements: res.totalElements,
    totalPages: res.totalPages,
    fetchedAt: new Date().toISOString(),
    items: (res.content || []).map(normalizeItem)
  };
}

// 政府采购公告在 zfcg 静态站，附件列表需从静态页解析
async function httpText(url) {
  const ctl = new AbortController();
  const timer = setTimeout(function () { ctl.abort(); }, 25000);
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9', Referer: ZFCG_BASE + '/' },
      signal: ctl.signal,
      redirect: 'follow'
    });
    const buf = Buffer.from(await res.arrayBuffer());
    let text;
    try { text = new TextDecoder('utf-8').decode(buf); } catch (e) { text = buf.toString('utf8'); }
    return { status: res.status, text: String(text) };
  } finally { clearTimeout(timer); }
}

async function fetchZfcgAttachments(staticUrl) {
  if (!staticUrl) return [];
  let html = '';
  try {
    const r = await httpText(staticUrl);
    if (r.status !== 200) return [];
    html = r.text;
  } catch (e) {
    return [];
  }
  return extractZfcgAttachments(html);
}
// 政府采购静态页地址：详情接口不返回 linkTo，用 noticeId + 发布日期按站点路径规则构造
// 路径规则（实测 8/8 命中）：/gsgg/002001/002001004/<栏目>/<YYYYMMDD>/<noticeId>.html
function buildZfcgStaticUrl(noticeId, releaseTime, noticeTypeCode) {
  if (!noticeId) return '';
  const m = /(\d{4})-(\d{2})-(\d{2})/.exec(String(releaseTime || ''));
  if (!m) return '';
  const ymd = m[1] + m[2] + m[3];
  let cat = '002001004001';
  if (String(noticeTypeCode || '').indexOf('zfcggggg') >= 0) cat = '002001004003';
  return ZFCG_BASE + '/gsgg/002001/002001004/' + cat + '/' + ymd + '/' + noticeId + '.html';
}

// 从列表接口取该 contentId 的 noticeId / 发布时间 / 栏目
async function resolveZfcgMeta(contentId) {
  try {
    const res = await searchPage({ channelId: CHANNELS.zfcg.id, size: 60 });
    const hit = (res.content || []).find(function (x) { return String(x.id) === String(contentId); });
    if (!hit) return null;
    if (hit.linkTo) return hit.linkTo;
    return buildZfcgStaticUrl(hit.noticeId, hit.releaseTime, hit.noticeTypeCode);
  } catch (e) {
    return null;
  }
}

async function toolGetNotice(args) {
  const contentId = String(args.contentId || '').trim();
  if (!contentId) throw new Error('必须提供 contentId');
  const argNoticeId = String(args.noticeId || '').trim();
  const argRelease = String(args.releaseTime || '').trim();
  const argTypeCode = String(args.noticeTypeCode || '').trim();
  const d = await fetchDetail(contentId);
  const attrs = attrMap(d.attrs);
  const links = extractLinks(d.txt);
  let files = links.map(function (l) {
    return { name: l.label, url: l.href, docClass: classifyDoc(l.label), captchaProtected: false };
  });
  // 政府采购公告的附件挂在 zfcg 静态站，需另行解析
  let staticUrl = d.linkTo || '';
  if (!staticUrl && argNoticeId) staticUrl = buildZfcgStaticUrl(argNoticeId, argRelease, argTypeCode);
  if (!staticUrl) staticUrl = (await resolveZfcgMeta(contentId)) || '';
  let zfcgAttachments = [];
  if (/zfcg\.szggzy\.com/.test(staticUrl)) {
    zfcgAttachments = await fetchZfcgAttachments(staticUrl);
    files = files.concat(zfcgAttachments);
  }
  return {
    contentId: contentId,
    title: d.title,
    releaseTime: d.releaseTime,
    nodeList: d.nodeList,
    source: d.source,
    url: SITE + '/jygg/details.html?contentId=' + contentId,
    staticUrl: staticUrl,
    projectCode: attrs.jygg_xmbh || '',
    projectName: attrs.jygg_xmmc || '',
    region: attrs.jygg_xmqy || '',
    projectType: attrs.jygg_gclx || '',
    constructCompany: attrs.jygg_jgbm || '',
    tradeType: attrs.jygg_jyfs || '',
    bodyText: htmlToText(d.txt).slice(0, 6000),
    attachments: files,
    captchaRequired: zfcgAttachments.length > 0
  };
}

async function downloadFile(url, destDir, fileName, maxBytes) {
  const ctl = new AbortController();
  const timer = setTimeout(function () { ctl.abort(); }, 180000);
  try {
    const res = await fetch(url, { headers: { 'User-Agent': UA, Referer: SITE + '/' }, signal: ctl.signal, redirect: 'follow' });
    if (!res.ok) throw new Error('下载失败 HTTP ' + res.status);
    const cd = res.headers.get('content-disposition') || '';
    let name = fileName;
    const star = /filename\*=UTF-8''([^;]+)/i.exec(cd);
    const plain = /filename="?([^";]+)"?/i.exec(cd);
    if (!name && star) name = decodeURIComponent(star[1]);
    if (!name && plain) name = decodeURIComponent(plain[1]);
    if (!name) name = path.basename(new URL(url).pathname) || 'download.bin';
    name = name.replace(/[\\/:*?"<>|]/g, '_');
    const buf = Buffer.from(await res.arrayBuffer());
    const limit = maxBytes || 300 * 1024 * 1024;
    if (buf.length > limit) throw new Error('文件过大 ' + buf.length + ' 字节，超过上限 ' + limit);
    await fs.promises.mkdir(destDir, { recursive: true });
    const dest = path.join(destDir, name);
    await fs.promises.writeFile(dest, buf);
    return { name: name, path: dest, bytes: buf.length, contentType: res.headers.get('content-type') };
  } finally { clearTimeout(timer); }
}

async function toolDownloadDocs(args) {
  const contentId = String(args.contentId || '').trim();
  const destDir = String(args.destDir || '').trim();
  const argNoticeId = String(args.noticeId || '').trim();
  const argRelease = String(args.releaseTime || '').trim();
  const argTypeCode = String(args.noticeTypeCode || '').trim();
  if (!contentId) throw new Error('必须提供 contentId');
  if (!destDir) throw new Error('必须提供 destDir（下载保存目录）');
  const wanted = Array.isArray(args.docClass) && args.docClass.length ? args.docClass : null;
  const d = await fetchDetail(contentId);
  const links = extractLinks(d.txt);
  let files = links.map(function (l) {
    return { name: l.label, url: l.href, docClass: classifyDoc(l.label), captchaProtected: false };
  });
  let staticUrl = d.linkTo || '';
  if (!staticUrl && argNoticeId) staticUrl = buildZfcgStaticUrl(argNoticeId, argRelease, argTypeCode);
  if (!staticUrl) staticUrl = (await resolveZfcgMeta(contentId)) || '';
  let zfcgAttachments = [];
  if (/zfcg\.szggzy\.com/.test(staticUrl)) {
    zfcgAttachments = await fetchZfcgAttachments(staticUrl);
    files = files.concat(zfcgAttachments);
  }
  const picked = wanted ? files.filter(function (f) { return wanted.indexOf(f.docClass) >= 0; }) : files;
  if (!picked.length) {
    return { contentId: contentId, title: d.title, destDir: destDir, downloaded: [], available: files, note: '该公告没有可下载附件' };
  }
  // 政府采购附件受图形验证码保护，程序无法直接下载，改为返回人工下载入口
  const captcha = picked.filter(function (f) { return f.captchaProtected; });
  const direct = picked.filter(function (f) { return !f.captchaProtected; });
  if (captcha.length && !direct.length) {
    return {
      contentId: contentId,
      title: d.title,
      destDir: destDir,
      downloaded: [],
      manualRequired: captcha,
      staticUrl: staticUrl,
      note: '政府采购公告附件受图形验证码保护，无法程序化下载。请打开 staticUrl 页面，在弹出的验证码框输入验证码后下载，或把附件另存后放到 destDir。',
      available: files
    };
  }
  const maxBytes = Number(args.maxMB || 300) * 1024 * 1024;
  const downloaded = [];
  const failed = [];
  for (let i = 0; i < direct.length; i++) {
    try {
      const r = await downloadFile(direct[i].url, destDir, direct[i].name, maxBytes);
      r.docClass = direct[i].docClass;
      r.sourceUrl = direct[i].url;
      downloaded.push(r);
    } catch (e) {
      failed.push({ name: direct[i].name, docClass: direct[i].docClass, error: String(e && e.message || e) });
    }
  }
  return {
    contentId: contentId,
    title: d.title,
    destDir: destDir,
    downloadedAt: new Date().toISOString(),
    downloaded: downloaded,
    failed: failed,
    manualRequired: captcha,
    staticUrl: staticUrl,
    note: captcha.length ? (captcha.length + ' 个附件受图形验证码保护，需人工在公告页面下载') : undefined,
    totalBytes: downloaded.reduce(function (a, b) { return a + b.bytes; }, 0)
  };
}

function toolListChannels() {
  return {
    platform: '深圳公共资源交易网 szggzy.com',
    channels: Object.keys(CHANNELS).map(function (k) { return { id: k, channelId: CHANNELS[k].id, label: CHANNELS[k].label }; }),
    stageOrder: STAGE_NAMES,
    stageTable: STAGE_TABLE.map(function (s) { return { noticeType: s.label, stage: s.stage }; }),
    docClasses: DOC_CLASS.map(function (d) { return { key: d.key, label: d.label }; })
  };
}

const TOOLS = [
  {
    name: 'project_progress',
    description: '按工程名称关键词查询深圳公共资源交易网上的项目全流程进度。返回该项目所有阶段公告（招标公告、最高投标限价、截标信息、开标情况公示、资审及业绩公示、评标委员会公示、评标报告公示、定标结果公示、中标结果公示）、当前所处阶段、是否已截标/已进入评标，以及可下载报告入口。',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', description: '工程名称关键词，如 院容院貌提升改造工程' },
        scope: { type: 'string', description: 'jsgc=建设工程(默认)，zfcg=政府采购，all=两者都查' },
        size: { type: 'integer', description: '每个渠道最多返回条数，默认 30，最大 100' }
      },
      required: ['title']
    }
  },
  {
    name: 'get_notice',
    description: '按 contentId 获取单条公告详情：标题、发布时间、项目编号、区域、正文纯文本，以及全部附件直链（已按用途分类 docClass：kbreport 开标报告 / pingbiao 评标报告 / zhongbiao 中标信息 / zixing 资信资格文件）。',
    inputSchema: {
      type: 'object',
      properties: { contentId: { type: 'string', description: 'contentId，来自 project_progress 或 list_notices' }, noticeId: { type: 'string', description: '政府采购公告的 noticeId（可选）' }, releaseTime: { type: 'string', description: '公告发布时间（可选）' }, noticeTypeCode: { type: 'string', description: '公告类型代码（可选）' } },
      required: ['contentId']
    }
  },
  {
    name: 'download_docs',
    description: '下载指定公告的附件到本地目录。docClass 可只下载某类：kbreport=开标报告，pingbiao=评标报告，zhongbiao=中标信息，zixing=资信/资格文件；留空表示下载全部附件。',
    inputSchema: {
      type: 'object',
      properties: {
        contentId: { type: 'string', description: '公告 contentId' },
        destDir: { type: 'string', description: '本地保存目录（绝对路径）' },
        docClass: { type: 'array', items: { type: 'string' }, description: '只下载指定类别；留空表示全部' },
        noticeId: { type: 'string', description: '政府采购公告的 noticeId（可选，来自 project_progress，用于定位静态页）' },
        releaseTime: { type: 'string', description: '公告发布时间（可选，来自 project_progress）' },
        maxMB: { type: 'integer', description: '单文件大小上限 MB，默认 300' }
      },
      required: ['contentId', 'destDir']
    }
  },
  {
    name: 'list_notices',
    description: '按渠道列出公告，可选标题关键词过滤，用于按时间浏览或补充 project_progress 未覆盖的公告。',
    inputSchema: {
      type: 'object',
      properties: {
        channelId: { type: 'string', description: '渠道 id，默认 2851（建设工程）；用 list_channels 查看全部' },
        title: { type: 'string', description: '标题关键词，留空返回最新公告' },
        current: { type: 'integer', description: '页码，默认 1' },
        size: { type: 'integer', description: '每页条数，默认 20，最大 100' }
      }
    }
  },
  {
    name: 'list_channels',
    description: '返回可用渠道、阶段顺序表与附件分类定义。',
    inputSchema: { type: 'object', properties: {} }
  }
];

async function callTool(name, args) {
  if (name === 'project_progress') return toolProjectProgress(args || {});
  if (name === 'get_notice') return toolGetNotice(args || {});
  if (name === 'download_docs') return toolDownloadDocs(args || {});
  if (name === 'list_notices') return toolListNotices(args || {});
  if (name === 'list_channels') return toolListChannels();
  throw new Error('未知工具: ' + name);
}

function send(obj) { process.stdout.write(JSON.stringify(obj) + '\n'); }
function reply(id, result) { send({ jsonrpc: '2.0', id: id, result: result }); }
function replyError(id, code, message) { send({ jsonrpc: '2.0', id: id, error: { code: code, message: message } }); }

const PROTOCOLS = ['2024-11-05', '2025-06-18'];

async function handle(msg) {
  const id = msg.id;
  const method = msg.method;
  const params = msg.params || {};
  if (method === 'initialize') {
    const v = PROTOCOLS.indexOf(params.protocolVersion) >= 0 ? params.protocolVersion : PROTOCOLS[0];
    reply(id, { protocolVersion: v, capabilities: { tools: { listChanged: false } }, serverInfo: { name: 'shenzhen-tender-info', version: '1.0.0' } });
    return;
  }
  if (method === 'notifications/initialized' || method === 'initialized') return;
  if (method === 'ping') { reply(id, {}); return; }
  if (method === 'tools/list') { reply(id, { tools: TOOLS }); return; }
  if (method === 'resources/list') { reply(id, { resources: [] }); return; }
  if (method === 'prompts/list') { reply(id, { prompts: [] }); return; }
  if (method === 'tools/call') {
    try {
      const data = await callTool(params.name, params.arguments || {});
      reply(id, { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }], isError: false });
    } catch (e) {
      reply(id, { content: [{ type: 'text', text: '工具执行失败: ' + String(e && e.message || e) }], isError: true });
    }
    return;
  }
  if (id === undefined || id === null) return;
  replyError(id, -32601, 'Method not found: ' + method);
}

let buffer = '';
function handleLine(line) {
  const s = line.trim();
  if (!s) return;
  let msg = null;
  try { msg = JSON.parse(s); } catch (e) { return; }
  Promise.resolve(handle(msg)).catch(function (e) {
    if (msg && msg.id !== undefined && msg.id !== null) replyError(msg.id, -32603, String(e && e.message || e));
  });
}

process.stdin.setEncoding('utf8');
process.stdin.on('data', function (chunk) {
  buffer += chunk;
  let idx;
  while ((idx = buffer.indexOf('\n')) >= 0) {
    const line = buffer.slice(0, idx);
    buffer = buffer.slice(idx + 1);
    handleLine(line);
  }
});
process.stdin.on('end', function () {
  if (buffer.trim()) handleLine(buffer);
});
