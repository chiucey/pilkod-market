const https = require('https');
const fs = require('fs');
const path = require('path');
const { parseQuery, formatReport } = require('./formatter');
const { downloadAllAttachments, formatDownloadReport } = require('./downloader');

const SEARCH_URL = 'https://vip.qianlima.com/rest/service/website/search/solr/tender';

// 基础cookies
const BASE_COOKIES = 'qlm_visitor_id=3579584701; guest_id=04159b9f-d933-4d73-81cd-7c49155e077a; seo_curUrl=www.qianlima.com; Hm_lvt_0a38bdb0467f2ce847386f381ff6c0e8=1774157328; Hm_lvt_5dc1b78c0ab996bd6536c3a37f9ceda7=1774106989,1774157316,1775363399; seo_refUrl=; qlm_referrer=; delClose200811=firstGoIn; HMACCOUNT=F0EB2C128756D543; source=1; useragent_hash=d18e73137d21a5f9c90eef45302b8ff1';

/**
 * 加载.env配置
 */
function loadEnv() {
  const envPath = path.join(__dirname, '..', '.env');
  try {
    if (fs.existsSync(envPath)) {
      const content = fs.readFileSync(envPath, 'utf-8');
      content.split('\n').forEach(line => {
        line = line.trim();
        if (line && !line.startsWith('#')) {
          const [key, ...vals] = line.split('=');
          if (key && vals.length > 0) {
            process.env[key.trim()] = vals.join('=').trim();
          }
        }
      });
    }
  } catch (e) {}
}

loadEnv();

/**
 * 使用curl执行HTTP请求
 */
function curlExec(cmd) {
  const { execSync } = require('child_process');
  try {
    return execSync(`bash -c '${cmd.replace(/'/g, "'\\''")}'`, { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 });
  } catch (e) {
    return e.stdout || '';
  }
}

/**
 * 确保有有效会话
 */
async function ensureSession() {
  const sessionFile = path.join(__dirname, 'session.json');

  // 读取现有session
  let session = null;
  try {
    if (fs.existsSync(sessionFile)) {
      session = JSON.parse(fs.readFileSync(sessionFile, 'utf-8'));
    }
  } catch (e) {}

  // 检查session是否有效（5分钟内有效）
  if (session && session.token && session.loginTime && (Date.now() - session.loginTime < 5 * 60 * 1000)) {
    return session;
  }

  const username = process.env.QIANLIMA_ACCOUNT || '18883372900';
  const password = process.env.QIANLIMA_PASSWD || '';

  // 登录
  console.error('正在登录千里马...');
  const loginCmd = `curl -s -L "https://vip.qianlima.com/rest/u/api/user/new/web/login?psw=${encodeURIComponent(password)}&username=${encodeURIComponent(username)}&source=&remLogin=1" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"`;
  const loginResult = curlExec(loginCmd);

  let passwordFromLogin = password;
  try {
    const loginData = JSON.parse(loginResult);
    if (loginData.data && loginData.data.password) {
      passwordFromLogin = loginData.data.password;
    }
  } catch (e) {
    console.error('登录解析失败:', e.message);
  }

  // 获取token
  console.error('正在获取Token...');
  const allCookies = `${BASE_COOKIES}; qlm_username=${username}; qlm_password=${passwordFromLogin}`;
  const tokenCmd = `curl -s -i "https://vip.qianlima.com/rest/u/loginController/user/logintime" -H "Accept: application/json, text/plain, */*" -H "Content-Type: application/json" -H "Cookie: ${allCookies}" -H "Referer: https://vip.qianlima.com/login/" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0" -H "X-Auth-Token: None" -H "Origin: https://vip.qianlima.com"`;
  const tokenResult = curlExec(tokenCmd);

  const tokenMatch = tokenResult.match(/X-Auth-Token:\s*(.+)/i);
  if (!tokenMatch) {
    throw new Error('获取Token失败');
  }
  const token = tokenMatch[1].trim();

  // 提取新的HWWAF cookies
  const sesIdMatch = tokenResult.match(/Set-Cookie: HWWAFSESID=([^;]+)/i);
  const sesTimeMatch = tokenResult.match(/Set-Cookie: HWWAFSESTIME=([^;]+)/i);
  const sesId = sesIdMatch ? sesIdMatch[1] : '';
  const sesTime = sesTimeMatch ? sesTimeMatch[1] : '';

  session = {
    username,
    password: passwordFromLogin,
    token,
    sesId,
    sesTime,
    loginTime: Date.now()
  };

  // 保存session
  fs.writeFileSync(sessionFile, JSON.stringify(session, null, 2));
  console.error('登录成功!');
  return session;
}

/**
 * 执行搜索
 */
async function search(params) {
  // 确保有有效会话
  const session = await ensureSession();

  const body = JSON.stringify({
    T: Date.now(),
    beginAmount: params.beginAmount || '',
    beginTime: params.beginTime || '',
    biddingType: params.biddingType || '',
    endAmount: params.endAmount || '',
    endTime: params.endTime || '',
    excludeWord: params.excludeWord || '',
    filterMode: '2,1',
    fundsSourceList: '',
    hasAgent: '',
    hasLinkName: '',
    hasPhone: '',
    keyword: params.keyword || '',
    keywordsAndOr: '|',
    newAreas: params.newAreas || '',
    progIdAndNoticeSegmentTypeMaps: { 0: [], 3: [] },
    purchasingUnitIdList: '',
    registrationStatus: '',
    searchMode: '',
    sortType: '2',
    summaryType: '1',
    threeClassifyTagStr: '',
    timeType: params.timeType || '7',
    numPerPage: params.numPerPage || 20,
    currentPage: params.currentPage || 1,
    keywords: params.keyword || ''
  });

  // 构建完整cookies
  const searchCookies = `${BASE_COOKIES}; qlm_username=${session.username}; qlm_password=${session.password}; HWWAFSESID=${session.sesId}; HWWAFSESTIME=${session.sesTime}`;

  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'vip.qianlima.com',
      port: 443,
      path: '/rest/service/website/search/solr/tender',
      method: 'POST',
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'Cookie': searchCookies,
        'Origin': 'https://vip.qianlima.com',
        'Referer': 'https://vip.qianlima.com/business-opportunity/bidding-info',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        'X-Auth-Token': session.token
      }
    };

    const req = https.request(options, (res) => {
      let responseBody = '';
      res.on('data', chunk => responseBody += chunk);
      res.on('end', () => {
        try {
          const data = JSON.parse(responseBody);
          if (data.code === 200) {
            resolve(data.data);
          } else if (data.code === 200503) {
            reject(new Error('服务器繁忙，请稍后重试'));
          } else if (data.code === 401) {
            reject(new Error('认证失效，请重新登录'));
          } else {
            reject(new Error(`搜索失败: ${data.msg}`));
          }
        } catch (e) {
          reject(new Error(`响应解析失败: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

/**
 * 主查询函数
 * @param {string} userInput - 用户输入的查询条件
 * @param {Object} options - 可选参数
 * @param {boolean} options.downloadAttachments - 是否下载附件，默认false
 * @param {string} options.downloadDir - 附件保存目录，默认'./downloads'
 */
async function query(userInput, options = {}) {
  const { downloadAttachments = false, downloadDir = './downloads' } = options;

  const params = parseQuery(userInput);
  console.error('搜索参数:', JSON.stringify(params, null, 2));

  const data = await search(params);
  const report = formatReport(data, userInput);
  console.log(report);

  // 下载附件
  if (downloadAttachments && data.data && data.data.length > 0) {
    const session = await ensureSession();
    const downloadSummary = await downloadAllAttachments(data.data, session, downloadDir, params.keyword);
    const downloadReport = formatDownloadReport(downloadSummary, userInput);
    console.log(downloadReport);
    return report + downloadReport;
  }

  return report;
}

// 命令行执行
if (require.main === module) {
  const args = process.argv.slice(2);

  // 解析参数
  let userInput = args.join(' ');
  let downloadEnabled = false;

  // 检查是否启用下载
  if (userInput.includes('--download') || userInput.includes('-d')) {
    downloadEnabled = true;
    userInput = userInput.replace(/--download/gi, '').replace(/-d/gi, '').trim();
  }

  if (!userInput) {
    userInput = '软件开发';
  }

  query(userInput, { downloadAttachments: downloadEnabled }).catch(e => {
    console.error('Error:', e.message);
    process.exit(1);
  });
}

module.exports = {
  search,
  query
};
