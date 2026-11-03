// boss_jd.mjs —— 批量抓取 Boss 职位 JD 正文
//
// 背景：列表页只能拿到职位名/薪资/公司/标签，拿不到 JD 正文。
// 但列表数据里每个岗位都带 href（/job_detail/xxx.html），顺着它抓详情页即可。
//
// 详情接口 /wapi/zpgeek/job/detail.json 需要额外参数（返回 code 17 缺少必要参数），
// 所以这里直接读**渲染后的 DOM**：JD 正文在 `.job-sec-text` 的第 0 个节点，
// 第 1 个节点是公司介绍（用文本特征区分）。
//
// 用法：
//   node boss_jd.mjs --file ../boss_jobs.json [--out ../boss_jd.json]
//                    [--limit 30] [--sleep 2500]
//
//   零配置：自动探测浏览器；profile 默认用 <skill根>/.boss_profile
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { dataDir, dataFile, profileDir, findBrowser, isLoginPath, makeCleanup,
         parseArgs as parseCli } from './boss.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));

const args = parseCli(process.argv.slice(2), ['limit', 'sleep', 'port']);
args.limit = args.limit ?? 30;
args.sleep = args.sleep ?? 2500;
args.port = args.port ?? 19987;

if (!args.file) {
  console.error('用法: node boss_jd.mjs --file <boss_jobs.json> [--out boss_jd.json] [--limit 30] [--data-dir <目录>] [--keep-browser]');
  console.error('  --keep-browser  抓完不关浏览器（调试用；默认会关掉自己启动的浏览器）');
  process.exit(2);
}
// 数据一律写到 skill 之外
const OUT = args.out || dataFile('boss_jd.json', args['data-dir']);
const PROFILE = args.profile || profileDir(dataDir(args['data-dir']));
if (!args.bin) {
  args.bin = findBrowser();
  if (!args.bin) { console.error('未找到 Chrome/Edge，请用 --bin 指定'); process.exit(2); }
}

const src = JSON.parse(fs.readFileSync(args.file, 'utf8'));
const jobs = (src.jobs || src).filter((j) => j.href).slice(0, args.limit);
if (!jobs.length) { console.error('输入里没有带 href 的岗位'); process.exit(2); }

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

fs.mkdirSync(PROFILE, { recursive: true });
for (const f of ['SingletonLock', 'SingletonSocket', 'SingletonCookie', 'DevToolsActivePort']) {
  try { fs.rmSync(path.join(PROFILE, f), { force: true }); } catch {}
}

const child = spawn(args.bin, [
  `--user-data-dir=${PROFILE}`,
  `--remote-debugging-port=${args.port}`,
  '--no-first-run', '--no-default-browser-check', '--disable-extensions',
  '--window-size=1500,950',
  'https://www.zhipin.com/web/geek/job',
], { stdio: 'ignore', detached: true });
child.unref();
// 自己 spawn 的浏览器要自己关 —— 与 boss.mjs 共用同一个幂等清理器。
// （旧版从不 kill，跑完留下常驻浏览器占着 profile，下次只能靠强删 SingletonLock 兜底）
let ws = null;
const cleanup = makeCleanup(child.pid, () => { try { if (ws) ws.close(); } catch {} },
                            !!args['keep-browser']);
console.log('浏览器:', path.basename(args.bin), '| 待抓 JD:', jobs.length, '条');

async function findPage(t = 45000) {
  const dl = Date.now() + t;
  while (Date.now() < dl) {
    try {
      const l = await (await fetch(`http://127.0.0.1:${args.port}/json/list`)).json();
      const p = l.find((x) => x.type === 'page' && x.url.includes('zhipin'));
      if (p) return p;
    } catch {}
    await sleep(1500);
  }
  return null;
}
const target = await findPage();
if (!target) { console.error('浏览器未就绪（profile 可能被占用）'); cleanup(1); }

ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0; const pend = new Map();
ws.addEventListener('message', (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
});
const send = (me, pa = {}, ms = 45000) => new Promise((res) => {
  const my = ++id;
  const tm = setTimeout(() => { pend.delete(my); res({}); }, ms);
  pend.set(my, (m) => { clearTimeout(tm); res(m); });
  ws.send(JSON.stringify({ id: my, method: me, params: pa }));
});
await new Promise((r) => ws.addEventListener('open', r));
await send('Page.enable');
const ev = async (x, ms) => {
  const r = await send('Runtime.evaluate', { expression: x, returnByValue: true, awaitPromise: true }, ms);
  return r?.result?.result?.value;
};

await sleep(5000);
// 登录判断统一走 boss.mjs 的 isLoginPath —— 只解析 pathname。
// 旧写法在这里复制了一份无锚定的 /\/web\/user|login|sign/ 子串匹配，
// 会把 ?query=designer / ?query=sign 这类普通职位页误判成"未登录"，
// 让已登录的用户白等 5 分钟。两份逻辑必须共用同一个实现，否则会各自漂移。
const stillLoggedIn = (u) => u && String(u).includes('zhipin.com') && !isLoginPath(u);
const loggedIn = stillLoggedIn(await ev('location.href'));
if (!loggedIn) {
  console.log('='.repeat(60));
  console.log('  未登录 —— 请在浏览器窗口扫码，登录后会自动继续');
  console.log('='.repeat(60));
  const dl = Date.now() + 5 * 60 * 1000;
  let ok = false;
  while (Date.now() < dl) {
    await sleep(3000);
    if (stillLoggedIn(await ev('location.href'))) { ok = true; break; }
  }
  if (!ok) { console.error('等待登录超时'); cleanup(3); }
  console.log('登录成功，开始抓 JD…');
}

// JD 正文提取：以 .job-sec-text 为主，用文本特征把"公司介绍"剔除。
const EXTRACT = `(() => {
  const clean = (s) => (s || '').replace(/\\u00a0/g, ' ').replace(/[ \\t]+/g, ' ').trim();
  const secs = [...document.querySelectorAll('.job-sec-text')].map((e) => clean(e.innerText)).filter((t) => t.length > 30);
  const isCompany = (t) => /^(我们|公司|成立于|是一家|愿景|欢迎|团队|总部)/.test(t)
    || /有限公司|科技有限|成立于\\d{4}/.test(t.slice(0, 60));
  const jd = secs.find((t) => !isCompany(t)) || secs[0] || '';
  const company = secs.find((t) => isCompany(t)) || '';
  const title = (document.querySelector('.job-name, h1') || {}).innerText || '';
  const sal = (document.querySelector('.job-salary, .salary') || {}).innerText || '';
  const meta = [...document.querySelectorAll('.job-primary .text, .job-info .text, .tag-all .tag-item')]
    .map((e) => clean(e.innerText)).filter(Boolean);
  return JSON.stringify({ title: clean(title), salaryRaw: clean(sal), meta, jd, companyIntro: company,
                          jdLen: jd.length });
})()`;

const results = [];
for (let i = 0; i < jobs.length; i++) {
  const j = jobs[i];
  const url = j.href.startsWith('http') ? j.href : 'https://www.zhipin.com' + j.href;
  process.stdout.write(`[${i + 1}/${jobs.length}] ${j.jobName.slice(0, 26)} … `);
  await ev(`location.href = ${JSON.stringify(url)}`, 15000);
  await sleep(args.sleep);

  let raw = await ev(EXTRACT);
  // 页面可能还在加载，重试一次
  if (!raw) { await sleep(2500); raw = await ev(EXTRACT); }
  let parsed = null;
  try { parsed = JSON.parse(raw || 'null'); } catch {}
  const jd = parsed?.jd || '';
  console.log(jd ? `${jd.length} 字` : '未取到');
  results.push({
    jobName: j.jobName,
    company: j.company,
    salary: j.salary,
    href: j.href,
    jd,
    jdLen: jd.length,
    companyIntro: parsed?.companyIntro || '',
    meta: parsed?.meta || [],
  });
}

const withJD = results.filter((r) => r.jdLen > 50);
fs.writeFileSync(OUT, JSON.stringify({
  captured_at: new Date().toISOString(),
  source_file: args.file,
  total: results.length,
  withJD: withJD.length,
  jobs: results,
}, null, 2), 'utf8');

console.log(`\n共 ${results.length} 条，成功取到 JD ${withJD.length} 条 -> ${OUT}`);
cleanup(0);
