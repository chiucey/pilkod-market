// boss.mjs —— Boss直聘岗位抓取（单一入口，零配置）
//
// 合并自：boss_paths.mjs + boss.mjs + boss_harvest.mjs
//
// 用法：
//   node boss.mjs harvest --query 内容运营 [--city 北京] [--rounds 12]
//   node boss.mjs harvest --queries 内容生态,创作者运营,社区运营 --city 北京
//   node boss.mjs harvest --url "<完整Boss搜索页URL>"
//   node boss.mjs help
//
// 兼容旧写法：node boss.mjs --query 内容运营（无子命令时默认 harvest）
//
// 为什么不用浏览器点「查看更多信息」翻页：
//   实测该按钮 rect.top ≈ 1408（在视口外），而 Boss 这版布局里
//   window.scrollBy **完全无效**（实测 top 1408→1405），滚不过去；
//   于是 .click() 与 CDP 真实鼠标点击都落在空白处，列表永远停在 15 条。
//   （这就是"同一个脚本，'内容运营'出 150 条、'社区运营'只出 15 条"的原因——
//     其实后者是真实结果就这么少，前者是接口翻页拿到的。）
//   所以翻页改走**页面自身的搜索接口**（同源 + credentials:'include'），
//   返回的 salaryDesc 还是明文，连 PUA 解码都不需要。
//
// 单次上限：服务端 total≈300，但第 6 页触发风控（code 37），
//   单查询实际最多约 5 页 × 30 = 150 条。想更多请换关键词多轮抓后合并：
//   python main.py bossmerge
//
// 依赖：Node 18+ 内置 fetch / WebSocket，无需 npm install。

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(HERE, '..');

/* ═══════════════════ 通用工具（原 boss_paths.mjs） ═══════════════════ */

/** 判断某路径是否落在 skill 包内（含 tools/ 与包根）。
 *  用途：cwd 顺位必须排除 skill 目录本身 —— 文档教用户先 `cd tools` 再跑，
 *  那样 cwd 恰好就是 skill 内部，登录态会写进要分发给别人的包里。 */
function insideSkill(p) {
  try {
    const abs = path.resolve(p);
    const root = SKILL_ROOT;                       // <pkg>/tools 的上一级 = 包根
    return abs === root || abs.startsWith(root + path.sep);
  } catch { return false; }
}

/** 数据目录解析：**永远不写进 skill 目录**（skill 要分发给别人）。
 *  顺序：--data-dir > BOSS_DATA_DIR > cwd/.boss > skill同级/boss_data > 临时目录
 *
 *  ⚠️ cwd 顺位必须做 insideSkill 检查。旧版没有检查，而文档（BOSS.md / SKILL.md）
 *  恰恰教用户先 `cd tools` 再执行 node —— 此时 process.cwd() 就是 <pkg>/tools，
 *  于是 dataDir() 解析成 <pkg>/tools/.boss，浏览器登录态（= 你的 Boss 账号 Cookie）
 *  被写进 skill 包内。这与本函数"永不写进 skill"的承诺直接矛盾。
 *  实测确认过该路径确实会被选中并创建。
 */
export function dataDir(override) {
  const cands = [];
  if (override) cands.push(override);
  if (process.env.BOSS_DATA_DIR) cands.push(process.env.BOSS_DATA_DIR);
  const cwdCand = path.join(process.cwd(), '.boss');
  if (!insideSkill(cwdCand)) cands.push(cwdCand);
  cands.push(path.resolve(SKILL_ROOT, '..', 'boss_data'));
  cands.push(path.join(os.tmpdir(), 'boss-data'));
  for (const d of cands) {
    try { fs.mkdirSync(d, { recursive: true }); return d; } catch { /* 试下一个 */ }
  }
  throw new Error('无法创建数据目录，请用 --data-dir 指定可写路径');
}

/** 数据目录下的文件路径（boss_jd.mjs 共用）。 */
export function dataFile(name, override) {
  return path.join(dataDir(override), name);
}

export function profileDir(dataDirPath, override) {
  if (override) return override;
  if (process.env.BOSS_PROFILE_DIR) return process.env.BOSS_PROFILE_DIR;
  return path.join(dataDirPath, 'browser_profile');
}

/** 判断一个 URL 是否是 Boss 的**登录/注册页**。
 *
 *  只解析 pathname + search 里的显式跳转参数，**绝不**用无锚定子串去扫整个 URL。
 *  原因（实测踩到）：/login|sign/ 这种无锚定匹配会把普通职位页的查询串也吃掉 ——
 *    https://www.zhipin.com/web/geek/job?query=designer  （"designer" 含 "sign"）
 *    https://www.zhipin.com/web/geek/job?query=sign
 *  两者都会被误判为"未登录"，于是脚本让已登录的用户白等 5 分钟扫码、最后退出码 3。
 *
 *  真登录页的形态是 **pathname 落在 /web/user/ 下**（例如 /web/user/login、
 *  /web/user/register、或未登录时被重定向到的 /web/user/），与查询串无关。
 *  boss_jd.mjs 里有一份同样的判断，两份必须保持一致 —— 所以放这里共用。
 */
export function isLoginPath(u) {
  try {
    const url = new URL(String(u));
    if (!/(^|\.)zhipin\.com$/.test(url.hostname)) return false;
    if (/^\/web\/user(\/|$)/.test(url.pathname)) return true;
    // 少数情况下会带 ?redirect=<登录页> 回来，顺带认一下
    const rd = url.searchParams.get('redirect') || url.searchParams.get('returnUrl') || '';
    return /\/web\/user(\/|$)/.test(rd);
  } catch {
    // 不是合法 URL（比如刚启动时的 about:blank）→ 当作未登录，让上层去等
    return false;
  }
}

/** 自动探测本机浏览器。 */
export function findBrowser() {
  const p = process.platform;
  const cands = [];
  if (p === 'win32') {
    const pf = process.env['ProgramFiles'] || 'C:\\Program Files';
    const pf86 = process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)';
    const local = process.env['LOCALAPPDATA'] || '';
    cands.push(
      path.join(pf86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      path.join(pf, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      path.join(pf, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(pf86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      local && path.join(local, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(pf, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
    );
  } else if (p === 'darwin') {
    cands.push(
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
    );
  } else {
    cands.push('/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium', '/usr/bin/chromium-browser',
      '/usr/bin/microsoft-edge', '/snap/bin/chromium');
  }
  for (const c of cands) if (c && fs.existsSync(c)) return c;
  return null;
}

export function parseArgs(argv, numeric = []) {
  const o = {};
  for (let i = 0; i < argv.length; i += 2) {
    const k = argv[i].replace(/^--/, '');
    const v = argv[i + 1];
    o[k] = numeric.includes(k) ? Number(v) : v;
  }
  return o;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ═══════════════════ 城市码 ═══════════════════ */

const CITY_CODES = {
  全国: '100010000', 北京: '101010100', 上海: '101020100', 广州: '101280100',
  深圳: '101280600', 杭州: '101210100', 成都: '101270100', 武汉: '101200100',
  南京: '101190100', 西安: '101110100', 苏州: '101190400', 长沙: '101250100',
};

/* ═══════════════════ CDP ═══════════════════ */

/** 生成一个幂等的清理函数：关浏览器 + 关 WebSocket，然后以 code 退出。
 *
 *  为什么必须显式关：浏览器是 detached 启动的，不 kill 就会一直常驻。
 *  为什么要幂等：正常路径、早退路径、异常路径、以及用户 Ctrl+C
 *  都会调它，重复调用不能报错、也不能重复 exit。
 *  为什么要挂 process.on：Ctrl+C / 未捕获异常时 node 直接退出，
 *  光靠 return 路径兜不住，浏览器还是会被留下。
 *
 *  导出给 boss_jd.mjs 共用 —— 那份脚本同样 spawn 了浏览器，
 *  同样需要负责关掉，不能各写一份。
 */
export function makeCleanup(pid, closeWs, keepBrowser) {
  let done = false;
  const kill = () => {
    try { if (closeWs) closeWs(); } catch {}
    if (!keepBrowser && pid) {
      try { process.kill(pid, 'SIGTERM'); } catch {}
    }
  };
  const handlers = [];
  const onSignal = (sig) => {
    kill();
    // 用信号语义的退出码，而不是伪装成成功
    process.exit(sig === 'SIGINT' ? 130 : 143);
  };
  const onExit = () => kill();
  for (const [ev, fn] of [['SIGINT', onSignal], ['SIGTERM', onSignal], ['exit', onExit]]) {
    try { process.on(ev, fn); handlers.push([ev, fn]); } catch {}
  }
  return (code) => {
    if (done) return;
    done = true;
    kill();
    for (const [ev, fn] of handlers) {
      try { process.removeListener(ev, fn); } catch {}
    }
    if (keepBrowser && pid) {
      console.log(`[提示] --keep-browser：浏览器仍在运行（pid ${pid}），需自行关闭`);
    }
    process.exit(code ?? 0);
  };
}

function launch(port, bin, profile, url) {
  fs.mkdirSync(profile, { recursive: true });
  for (const f of ['SingletonLock', 'SingletonSocket', 'SingletonCookie', 'DevToolsActivePort']) {
    try { fs.rmSync(path.join(profile, f), { force: true }); } catch {}
  }
  const child = spawn(bin, [
    `--user-data-dir=${profile}`, `--remote-debugging-port=${port}`,
    '--no-first-run', '--no-default-browser-check', '--disable-extensions',
    '--window-size=1500,950', url,
  ], { stdio: 'ignore', detached: true });
  child.unref();
  return child.pid;
}



async function findPage(port, timeoutMs = 45000) {
  const deadline = Date.now() + timeoutMs;
  let seen = [];
  while (Date.now() < deadline) {
    try {
      const l = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      seen = l.map((x) => `${x.type} ${x.url}`.slice(0, 90));
      const p = l.find((x) => x.type === 'page' && x.url.includes('zhipin'));
      if (p) return p;
    } catch { /* 浏览器还没起来 */ }
    await sleep(1500);
  }
  console.error('未找到 zhipin 页面。CDP 目标：');
  console.error(seen.length ? seen.join('\n') : '(CDP 不可达：浏览器没起来，通常是 profile 被占用)');
  return null;
}

function connect(target) {
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  const send = (method, params = {}, ms = 20000) => new Promise((res) => {
    const my = ++id;
    const tm = setTimeout(() => { pending.delete(my); res({}); }, ms);
    pending.set(my, (m) => { clearTimeout(tm); res(m); });
    ws.send(JSON.stringify({ id: my, method, params }));
  });
  return { ws, send };
}

/* ═══════════════════ PUA 薪资解码 ═══════════════════ */
// 映射**不是**码位偏移，必须用实测表（曾误用 E030->0，导致薪资整体偏高一位）：
//   \uE031->0 \uE032->1 \uE033->2 \uE034->3 \uE035->4
//   \uE036->5 \uE037->6 \uE038->7 \uE039->8 \uE03A->9
// 切勿 strip 私用区——那会把数字一起删掉。
const PUA_MAP = {
  0xE031: '0', 0xE032: '1', 0xE033: '2', 0xE034: '3', 0xE035: '4',
  0xE036: '5', 0xE037: '6', 0xE038: '7', 0xE039: '8', 0xE03A: '9',
};

export function decodePua(s) {
  let o = '';
  for (const ch of (s || '')) o += (PUA_MAP[ch.codePointAt(0)] ?? ch);
  return o.replace(/\s+/g, ' ').trim();
}

// 注入到页面里的同款解码器
const DECODER_JS = `
  const M = ${JSON.stringify(PUA_MAP)};
  const decode = (s) => {
    let o = '';
    for (const ch of (s || '')) o += (M[ch.codePointAt(0)] ?? ch);
    return o.replace(/\\s+/g, ' ').trim();
  };`;

/* ═══════════════════ harvest ═══════════════════ */

async function cmdHarvest(args) {
  const rounds = args.rounds ?? 12;
  const city = args.city ?? '全国';
  // 提速项（实测标定）：
  //   pageGap      —— 每页间隔。实测正常页响应极快（接口瞬时返回），1.2s 足够；
  //                   调大可降低被风控概率（如 --page-gap 3000）。
  //   fetchTimeout —— 页面内单次请求超时。被风控时 Boss 让请求挂住不返回，
  //                   不设超时的话每页白等 20s（CDP 外层超时）且拿不到数据。
  const pageGap = args.pageGap ?? 1200;
  const fetchTimeout = args.fetchTimeout ?? 4000;
  const dataDirPath = dataDir(args['data-dir']);
  const out = args.out || path.join(dataDirPath, 'boss_jobs.json');
  const profile = profileDir(dataDirPath, args.profile);

  const bin = args.bin || findBrowser();
  if (!bin) { console.error('未找到 Chrome/Edge/Chromium，请用 --bin 指定'); return 2; }

  const queries = (args.queries || args.query || '')
    .split(/[,，]/).map((s) => s.trim()).filter(Boolean);

  const targets = [];
  if (args.url) {
    targets.push({ label: '自定义URL', url: args.url });
  } else if (queries.length) {
    const code = args['city-code'] || CITY_CODES[city] || CITY_CODES['全国'];
    for (const q of queries) {
      targets.push({
        label: q,
        url: `https://www.zhipin.com/web/geek/job?query=${encodeURIComponent(q)}&city=${code}`,
      });
    }
  } else {
    console.log(`用法:
  node boss.mjs harvest --query 内容运营 [--city 北京] [--rounds 12]
  node boss.mjs harvest --queries 内容生态,创作者运营,社区运营 [--city 北京]
  node boss.mjs harvest --url "<完整Boss搜索页URL>"

可选城市: ${Object.keys(CITY_CODES).join(' / ')}
其他选项: --data-dir <数据目录>  --out <输出json>  --bin <浏览器>  --profile <登录态目录>

说明：单次查询最多约 150 条（第 6 页触发 Boss 风控）。
      想更多请换关键词多轮抓，再用 python main.py bossmerge 合并。`);
    return 2;
  }

  console.log('浏览器:', bin);
  console.log('数据目录:', dataDirPath);
  console.log('待抓:', targets.map((t) => t.label).join(', '));

  const port = args.port ?? 19974;
  const browserPid = launch(port, bin, profile, targets[0].url);
  // 浏览器是我们 spawn 的，就必须由我们负责关掉。
  // 旧版 launch() 用了 { detached: true } + unref()，pid 拿到就丢，
  // 结束时只 ws.close()、从不 kill —— 于是每跑一次就留下一个常驻的
  // Edge/Chrome 占着 profile，下次只能靠强删 SingletonLock 兜底。
  // 已实测确认：早退路径（findPage 失败 / 登录超时）连 ws.close() 都不走。
  // --keep-browser 是刻意保留的逃生门（调试用），默认关闭。
  let ws = null;
  const cleanup = makeCleanup(browserPid, () => { try { if (ws) ws.close(); } catch {} },
                              !!args['keep-browser']);

  const target = await findPage(port);
  if (!target) { cleanup(1); return 1; }

  const conn = connect(target);
  ws = conn.ws;
  const send = conn.send;
  await new Promise((r) => ws.addEventListener('open', r));
  await send('Page.enable');
  const ev = async (expr, ms) => {
    const r = await send('Runtime.evaluate',
      { expression: expr, returnByValue: true, awaitPromise: true }, ms);
    return r?.result?.result?.value;
  };

  // 登录检测：未登录会被重定向到 /web/user/。
  // 注意**不要**用"URL 不含 /web/user 就算已登录"来判断——登录页本身就是 /web/user/，
  // 上游 mcp-boss-zp 就在这点上判断反了。
  //
  // ⚠️ 必须只匹配 **pathname**，不能用 /login|sign/ 扫整个 URL：
  //    旧写法 `!/\/web\/user|login|sign/.test(u)` 是**无锚定子串**匹配，
  //    于是 `?query=designer`（含 "sign"）或 `?query=sign` 会被判成"未登录"，
  //    明明已登录却进 5 分钟扫码等待循环、最后 rc=3 —— 一个白等且误导用户的假故障。
  //    实测：?query=designer → NOT-LOGGED（错）；?query=x → LOGGED-IN（对）。
  //    改为只看路径：登录/注册页都在 /web/user/ 下，查询串一律不参与判断。
  const checkLogin = async () => {
    const u = (await ev('location.href')) || '';
    if (!u.includes('zhipin.com')) return false;
    return !isLoginPath(u);
  };

  if (!(await checkLogin())) {
    console.log('='.repeat(64));
    console.log('  未登录 —— 请在弹出的浏览器窗口扫码登录 BOSS 直聘。');
    console.log('  登录态会保存在: ' + profile);
    console.log('  只需登录这一次，之后重跑会直接复用。');
    console.log('='.repeat(64));
    const deadline = Date.now() + 5 * 60 * 1000;
    let ok = false;
    while (Date.now() < deadline) {
      await sleep(3000);
      try { if (await checkLogin()) { ok = true; break; } } catch {}
    }
    if (!ok) { console.error('等待登录超时（5 分钟）。修好后重跑即可。'); cleanup(3); return 3; }
    console.log('登录成功，开始抓取…');
  }

  const seen = new Map();
  const addItems = (items) => {
    let added = 0;
    for (const j of items) {
      const k = `${j.jobName}|${j.company}`;
      if (!seen.has(k)) { seen.set(k, j); added++; }
    }
    return added;
  };

  // 首屏：读 DOM（含 PUA 解码），拿到的 href 可用于后续抓 JD
  const HARVEST = `JSON.stringify((() => {
    ${DECODER_JS}
    const cards = document.querySelectorAll('li.job-card-box');
    const out = [];
    cards.forEach((c) => {
      const g = (s) => { const e = c.querySelector(s); return e ? decode(e.textContent) : ''; };
      const name = g('.job-name');
      if (!name) return;
      const link = c.querySelector('a[href*="/job_detail/"]');
      out.push({
        jobName: name,
        salary: g('.job-salary') || g('.salary'),
        company: g('.boss-name') || g('.company-name') || g('.brand-name'),
        location: g('.company-location') || g('.job-area'),
        tags: Array.from(c.querySelectorAll('.tag-list li, .job-labels span, .tag-list span'))
          .map((e) => decode(e.textContent)).filter(Boolean),
        href: link ? link.getAttribute('href') : '',
      });
    });
    return { domCount: cards.length, items: out };
  })())`;

  const waitForList = async (timeoutMs = 30000) => {
    const dl = Date.now() + timeoutMs;
    while (Date.now() < dl) {
      const n = await ev(`document.querySelectorAll('li.job-card-box').length`, 5000);
      if (typeof n === 'number' && n > 0) return n;
      await sleep(1000);
    }
    return 0;
  };

  // 翻页走接口：返回 salaryDesc 明文，且不受"按钮在视口外点不到"的影响。
  //
  // ⚠️ 必须带【页面内超时】：被风控时 Boss 会让请求挂住不返回，
  //    此时 CDP 的 Runtime.evaluate 会一直等到外层 20s 超时，
  //    每页白等 22s（实测），而且拿不到任何数据。
  //    加上 AbortController 后，4s 内没响应就自己断开，失败即返回。
  const PAGE_API = `(async () => {
    const qs = new URLSearchParams(location.search);
    const q = qs.get('query') || '';
    const city = qs.get('city') || '101010100';
    const u = '/wapi/zpgeek/search/joblist.json?scene=1&query=' + encodeURIComponent(q)
            + '&city=' + city + '&page=__PAGE__&pageSize=30';
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), __TIMEOUT__);
    try {
      const r = await fetch(u, { credentials: 'include', signal: ac.signal });
      const j = await r.json();
      const d = j.zpData || {};
      return JSON.stringify({
        code: j.code, message: j.message, total: d.totalCount,
        items: (d.jobList || []).map((x) => ({
          jobName: x.jobName, salary: x.salaryDesc || '', company: x.brandName || '',
          location: [x.cityName, x.areaDistrict].filter(Boolean).join('·'),
          tags: [x.jobExperience, x.jobDegree].filter(Boolean).concat(x.skills || []),
          href: x.securityId ? ('/job_detail/' + x.securityId + '.html') : '',
        })),
      });
    } catch (e) {
      return JSON.stringify({ code: -2, message: 'timeout/abort: ' + String(e), items: [] });
    } finally { clearTimeout(timer); }
  })()`;

  let grandTotal = null;
  for (const { label, url } of targets) {
    console.log(`\n──── 抓取「${label}」 ────`);
    await ev(`location.href = ${JSON.stringify(url)}`, 15000);
    await sleep(3000);

    const dom = await waitForList();
    if (dom === 0) console.log('  30 秒内未渲染出卡片（该关键词可能无结果，或未登录）');

    const raw = await ev(HARVEST);
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        const n = addItems(parsed.items);
        console.log(`  首屏: DOM ${parsed.domCount}, 新增 ${n}, 累计 ${seen.size}`);
      } catch { /* 忽略解析失败 */ }
    }

    const pages = Math.max(1, Math.ceil(rounds / 2));
    let blocked = 0;
    for (let page = 1; page <= pages; page++) {
      const expr = PAGE_API.replace('__PAGE__', String(page))
                           .replace('__TIMEOUT__', String(fetchTimeout));
      // 外层超时略大于页面内超时，让页面内 AbortController 先触发
      const r1 = await ev(expr, fetchTimeout + 3000);
      let r = {};
      try { r = JSON.parse(r1 || '{}'); } catch {}
      if (r.total) grandTotal = r.total;

      if (r.code === 0 && r.items?.length) {
        blocked = 0;
        const n = addItems(r.items);
        console.log(`  page ${page}: 接口 ${r.items.length} 条, 新增 ${n}, 累计 ${seen.size}`);
      } else {
        blocked++;
        const why = r.code === -2 ? '请求超时（疑似风控）' : (r.message || '');
        console.log(`  page ${page}: code=${r.code} ${why}（被拦 ${blocked}）`);
        // 失败即停：Boss 一旦开始风控，后面几页也会挂，继续等只是浪费时间。
        // 以前是连挂 2 页才停，每页白等 22s —— 现在第 1 次失败就退出。
        if (blocked >= 1) {
          console.log('  已触发风控，停止翻页（继续请求只会更慢且仍拿不到数据）');
          break;
        }
      }
      // 页间隔：前几页实测响应极快，1.2s 足够；可 --page-gap 调整
      await sleep(pageGap);
    }
  }

  if (grandTotal) console.log(`\n  （服务端报告共 ${grandTotal} 条，单次最多可取约 150 条）`);

  const jobs = [...seen.values()];
  fs.writeFileSync(out, JSON.stringify({
    captured_at: new Date().toISOString(),
    city,
    count: jobs.length,
    jobs,
  }, null, 2), 'utf8');

  console.log(`\n${'='.repeat(60)}`);
  console.log(`共 ${jobs.length} 个职位 -> ${out}`);
  if (jobs.length >= 150) {
    console.log('ℹ️  已达单次上限。想更多请换关键词再抓一轮，然后合并：');
    console.log(`   python main.py bossmerge --files "${dataDirPath}/boss_*.json" --out "${path.join(dataDirPath, 'boss_all.json')}"`);
  }
  console.log('下一步筛选分级：');
  console.log(`   python main.py boss filter --file "${out}"`);
  console.log('='.repeat(60));

  cleanup(0);
  return 0;
}

/* ═══════════════════ 入口 ═══════════════════ */
//
// 只有在**直接运行本文件**时才执行 CLI。
// 否则 `import ... from './boss.mjs'`（boss_jd.mjs 就是这么复用的）
// 会把本文件的 CLI 也一起跑起来 —— 那是个真 bug：
// boss_jd.mjs 一启动就打印 boss.mjs 的用法然后 exit(2)，永远走不到自己的逻辑。
import { realpathSync } from 'node:fs';

function isMainModule() {
  const entry = process.argv[1];
  if (!entry) return false;
  try {
    return realpathSync(entry) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
}

if (isMainModule()) {
  const argv = process.argv.slice(2);
  const sub = argv[0];
  const isSub = ['harvest', 'help', '--help', '-h'].includes(sub);
  const rest = isSub ? argv.slice(1) : argv;

  if (['help', '--help', '-h'].includes(sub)) {
    console.log(`Boss直聘岗位抓取（零配置）

  node boss.mjs harvest --query 内容运营 --city 北京
  node boss.mjs harvest --queries 内容生态,创作者运营 --city 北京
  node boss.mjs harvest --url "<完整Boss搜索页URL>"

数据默认写到 skill 之外的目录（--data-dir 可指定），不会污染可分发的 skill。`);
    process.exit(0);
  }

  const code = await cmdHarvest(parseArgs(rest, ['rounds', 'port', 'pageGap', 'fetchTimeout']));
  process.exit(code ?? 0);
}
