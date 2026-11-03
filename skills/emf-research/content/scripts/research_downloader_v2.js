// 投研研报下载工具 v2 - 纯Node.js实现（无需Selenium/浏览器）
// 运行方式:
//   node research_downloader_v2.js --keyword 光模块 --page 1
//   node research_downloader_v2.js --keyword AI算力 --page 2 --source emf
//   node research_downloader_v2.js --keyword 机器人 --source all --page 1

const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ============ 配置区 ============
const SAVE_DIR = path.join(__dirname, 'research_pdf');
if (!fs.existsSync(SAVE_DIR)) fs.mkdirSync(SAVE_DIR, { recursive: true });

// 你的Cookie（用于萝卜投研，可选）
const ROBO_COOKIE = 'gr_user_id=a6af9f3d-bc7c-4e71-882e-42be9c459e12; ba895d61f7404b76_gr_session_id=9e6f4e82-a38d-4f2d-8b8d-a1502e77bd2e; _ga=GA1.2.1660388408.1778556084; _gid=GA1.2.484039999.1778556084; cloud-anonymous-token=3541b62d06864e12901556af677d169c; _DA_pingback=063b2f4b-9803-4a80-ab6f-7057ac9276ac; _ga_YBHR4XSTK7=GS2.2.s1778556084$o1$g1$t1778556143$j1$l0$h0; ba895d61f7404b76_gr_last_sent_sid_with_cs1=9e6f4e82-a38d-4f2d-8b8d-a1502e77bd2e; ba895d61f7404b76_gr_last_sent_cs1=8826561@wmcloud.com; ba895d61f7404b76_gr_cs1=8826561@wmcloud.com';

// ============ 工具函数 ============
function httpGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const opts = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        ...headers
      }
    };
    const req = https.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.setTimeout(20000, () => { req.destroy(); reject(new Error('请求超时')); });
    req.end();
  });
}

function saveFile(content, filename) {
  const safe = filename.replace(/[\\/:*?"<>|]/g, '_').trim().substring(0, 200);
  const fp = path.join(SAVE_DIR, safe);
  if (fs.existsSync(fp)) { console.log(`  ⏭ 已存在: ${safe}`); return false; }
  fs.writeFileSync(fp, content);
  console.log(`  ✅ 已保存: ${safe} (${(content.length/1024).toFixed(0)}KB)`);
  return true;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ============ 东方财富研报API（公开，无需登录） ============
async function searchEMF(keyword, pageNo = 1, pageSize = 20) {
  // industryCode=* 为全行业，可换成具体行业代码如 01(银行)、02(保险)等
  const beginTime = '2024-01-01'; // 尽量拉回溯时间，获取更多数据
  const endTime = '2026-12-31';
  const encodedKw = encodeURIComponent(keyword);
  const url = `https://reportapi.eastmoney.com/report/list?industryCode=*&pageSize=${pageSize}&pageNo=${pageNo}&beginTime=${beginTime}&endTime=${endTime}&column=*&type=1&cb=datatable`;
  
  console.log(`  [东方财富] 关键词: "${keyword}" 第${pageNo}页`);
  const { status, body } = await httpGet(url, { 'Referer': 'https://data.eastmoney.com/' });
  
  if (status !== 200) {
    console.log(`  ⚠ API状态: ${status}`);
    return { total: 0, reports: [] };
  }
  
  const clean = body.replace(/^datatable\(/, '').replace(/\);?\s*$/, '').trim();
  try {
    const json = JSON.parse(clean);
    const records = json.data || [];
    const reports = records.map(item => ({
      title: (item.title || '无标题').trim(),
      url: `https://data.eastmoney.com/report/stock/${item.id}.jshtml`,
      orgName: item.orgName || item.industryName || '',
      publishDate: item.publishDate || '',
      rating: item.buyIn || item.rating || '',
      industry: item.industryName || '',
      id: item.id || ''
    }));
    console.log(`  ✅ 获取 ${reports.length} 条（总计 ${json.total || 0} 条）`);
    return { total: json.total || 0, reports };
  } catch(e) {
    console.log(`  ❌ 解析失败: ${e.message}，响应前200字符: ${body.substring(0,200)}`);
    return { total: 0, reports: [] };
  }
}

// ============ 萝卜投研（Cookie版） ============
async function searchRobo(keyword, page = 1) {
  const encodedKw = encodeURIComponent(keyword);
  const { status, body } = await httpGet(
    `https://robo.datayes.com/v2/research/report/search?keyword=${encodedKw}&page=${page}&size=20`,
    { 'Cookie': ROBO_COOKIE, 'Referer': 'https://robo.datayes.com/' }
  );
  
  if (status !== 200 || !body.includes('"data"')) {
    // 降级：尝试直接抓搜索页HTML
    console.log(`  [萝卜投研] API失效(${status})，尝试HTML搜索...`);
    return await searchRoboHTML(keyword, page);
  }
  
  try {
    const json = JSON.parse(body);
    const records = json.data?.records || [];
    return {
      total: json.data?.total || records.length,
      reports: records.map(item => ({
        title: item.title || '无标题',
        url: `https://robo.datayes.com/research/report/${item.id}`,
        orgName: item.orgName || '',
        publishDate: item.publishDate || item.createdAt || '',
        id: item.id || ''
      }))
    };
  } catch(e) {
    console.log(`  ❌ 萝卜投研解析失败: ${e.message}`);
    return { total: 0, reports: [] };
  }
}

async function searchRoboHTML(keyword, page) {
  const { status, body } = await httpGet(
    `https://robo.datayes.com/v2/research/report/search?keyword=${encodeURIComponent(keyword)}&page=${page}&size=20`,
    { 'Accept': 'text/html, */*' }
  );
  // 如果还是跳转到登录页，返回空
  if (body.includes('login') || body.includes('登录')) {
    console.log(`  ⚠ 萝卜投研需要登录，Cookie已过期`);
    return { total: 0, reports: [] };
  }
  return { total: 0, reports: [] };
}

// ============ 同花顺iFinD（需Cookie，降级用） ============
async function searchTHS(keyword, page = 1) {
  // 同花顺的研报搜索（部分公开）
  const { status, body } = await httpGet(
    `https://data.10jqka.com.cn/funds/research/`,
    { 'Referer': 'https://data.10jqka.com.cn/' }
  );
  return { total: 0, reports: [] };
}

// ============ 主流程 ============
async function downloadReports(source, keyword, maxPage = 1) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`📥 开始下载 | 来源: ${source} | 关键词: ${keyword} | 最大${maxPage}页`);
  console.log(`📁 保存目录: ${SAVE_DIR}`);
  console.log(`=${'='.repeat(50)}\n`);

  let totalSaved = 0;

  for (let page = 1; page <= maxPage; page++) {
    console.log(`\n--- 第 ${page}/${maxPage} 页 ---`);

    if (source === 'emf' || source === 'all') {
      const result = await searchEMF(keyword, page);
      if (result.reports.length > 0) {
        console.log(`  研报列表:`);
        result.reports.forEach((r, i) => {
          console.log(`  ${i+1}. [${r.publishDate}] ${r.title}`);
          console.log(`     机构: ${r.orgName} | 行业: ${r.industry}`);
        });
      }
      if (result.reports.length < 20) break; // 最后一页
    }

    if (source === 'robo' || source === 'all') {
      const result = await searchRobo(keyword, page);
      if (result.reports.length > 0) {
        result.reports.forEach(r => {
          console.log(`  📄 [${r.publishDate}] ${r.title} (${r.orgName})`);
        });
      }
      await sleep(1500);
    }
  }

  console.log(`\n✅ 完成！共获取 ${totalSaved} 份研报信息`);
  console.log(`📁 文件保存在: ${SAVE_DIR}`);
  return totalSaved;
}

// ============ 命令行入口 ============
const args = process.argv.slice(2);
let source = 'emf', keyword = '', maxPage = 1;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--source' || args[i] === '-s') { source = args[i+1]; i++; }
  else if (args[i] === '--keyword' || args[i] === '-k') { keyword = args[i+1]; i++; }
  else if (args[i] === '--page' || args[i] === '-p') { maxPage = parseInt(args[i+1]) || 1; i++; }
  else if (args[i] === '--all') { source = 'all'; }
  else if (args[i] === '--dir') { i++; }
}

if (!keyword) {
  console.log(`
📥 投研研报下载工具 v2（Node.js版）

用法:
  node research_downloader_v2.js --keyword 光模块 --page 2
  node research_downloader_v2.js --keyword AI算力 --source emf --page 3
  node research_downloader_v2.js --keyword --source all --page 1  # 同时搜东方财富+萝卜

参数:
  --keyword/-k   搜索关键词（必填）
  --source/-s    emf | robo | all（默认: emf）
  --page/-p      下载页数（默认: 1，最多3页）
  --all          等同于 --source all

说明:
  emf（东方财富）: 无需Cookie，完全公开可用
  robo（萝卜投研）: 需要有效Cookie，当前可能已过期
  `);
  process.exit(0);
}

downloadReports(source, keyword, maxPage)
  .then(n => { console.log(`\n🎉 完成，共 ${n} 条记录`); process.exit(0); })
  .catch(e => { console.error('\n❌ 错误:', e.message); process.exit(1); });
