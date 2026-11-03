#!/usr/bin/env node
/**
 * 投研研报下载工具 v3 - 东方财富公开API版
 * 
 * 功能：从东方财富研报页面抓取标题/机构/日期
 * 特点：无需登录/Selenium/ChromeDriver，完全公开可用
 * 
 * 使用方法：
 *   node research_emf.js 光模块              # 搜索关键词
 *   node research_emf.js 光模块 2            # 指定页数
 *   node research_emf.js AI算力 3            # 最多取3页
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// ============ 配置 ============
const SAVE_DIR = '/workspace/research_pdf';
const RESULTS_FILE = '/workspace/emf_search_results.json';
if (!fs.existsSync(SAVE_DIR)) fs.mkdirSync(SAVE_DIR, { recursive: true });

// ============ HTTP工具 ============
function httpsGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname,
      path: u.pathname + u.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://data.eastmoney.com/',
        'Accept': 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        ...headers
      }
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject);
    req.setTimeout(20000, () => { req.destroy(); reject(new Error('请求超时')); });
    req.end();
  });
}

// ============ 东方财富研报搜索 ============
async function searchEMFReports(keyword, page = 1) {
  console.log(`\n[东方财富] 搜索关键词: "${keyword}" 第${page}页`);
  
  // 方式1: 直接访问研报列表页（支持关键词筛选）
  const listUrl = `https://data.eastmoney.com/report/stock.jshtml?keyword=${encodeURIComponent(keyword)}&page=${page}`;
  const { status, body } = await httpsGet(listUrl);
  
  if (status !== 200) {
    console.log(`  ⚠ HTTP状态: ${status}`);
    return [];
  }
  
  // 提取研报信息（多种正则模式）
  const reports = [];
  
  // 模式1: 标准JSON格式 "title":"xxx"
  const titleMatches = body.match(/"title"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"/g) || [];
  // 模式2: 提取发布时间 publishDate
  const dateMatches = body.match(/"publishDate"\s*:\s*"([^"]+)"/g) || [];
  // 模式3: 提取机构名 orgName
  const orgMatches = body.match(/"orgName"\s*:\s*"([^"]+)"/g) || [];
  // 模式4: 提取研报ID用于生成链接
  const idMatches = body.match(/"id"\s*:\s*"?([a-zA-Z0-9_\-]+)"?/g) || [];
  
  const count = Math.min(titleMatches.length, 50);
  
  for (let i = 0; i < count; i++) {
    const title = (titleMatches[i] || '').match(/"title"\s*:\s*"([^"]+)"/)?.[1] || '';
    const publishDate = (dateMatches[i] || '').match(/"publishDate"\s*:\s*"([^"]+)"/)?.[1] || '';
    const orgName = (orgMatches[i] || '').match(/"orgName"\s*:\s*"([^"]+)"/)?.[1] || '';
    const id = (idMatches[i] || '').match(/"id"\s*:\s*"?([a-zA-Z0-9_\-]+)"?/)?.[1] || '';
    
    if (title) {
      reports.push({
        title: title.replace(/\\\"/g, '"').replace(/\\/g, '/'),
        publishDate,
        orgName,
        url: id ? `https://data.eastmoney.com/report/stock/${id}.jshtml` : ''
      });
    }
  }
  
  // 去重
  const seen = new Set();
  const unique = reports.filter(r => {
    if (seen.has(r.title)) return false;
    seen.add(r.title);
    return true;
  });
  
  console.log(`  ✅ 获取 ${unique.length} 条研报信息`);
  return unique;
}

// ============ 多页下载 ============
async function downloadAll(keyword, maxPage = 2) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`📥 投研研报下载 | 关键词: ${keyword} | 最多${maxPage}页`);
  console.log(`=${'='.repeat(50)}`);
  
  const allReports = [];
  
  for (let page = 1; page <= maxPage; page++) {
    const reports = await searchEMFReports(keyword, page);
    
    if (reports.length === 0) {
      console.log(`  ⏭ 第${page}页无结果，停止`);
      break;
    }
    
    // 只打印前10条作为预览
    reports.slice(0, 10).forEach((r, i) => {
      console.log(`  ${(page-1)*20+i+1}. [${r.publishDate || '无日期'}] ${r.title}`);
      console.log(`     机构: ${r.orgName || '未知'} ${r.url ? '🔗' : ''}`);
    });
    
    if (reports.length < 20) {
      console.log(`  （第${page}页不满20条，已到末尾）`);
      break;
    }
    
    // 东方财富限制，最快间隔1秒
    await new Promise(r => setTimeout(r, 1000));
    allReports.push(...reports);
  }
  
  // 保存到JSON文件
  const saveData = {
    keyword,
    total: allReports.length,
    pages: maxPage,
    savedAt: new Date().toISOString(),
    reports: allReports
  };
  
  fs.writeFileSync(RESULTS_FILE, JSON.stringify(saveData, null, 2));
  const size = (fs.statSync(RESULTS_FILE).size / 1024).toFixed(1);
  
  console.log(`\n${'='.repeat(50)}`);
  console.log(`✅ 下载完成！共获取 ${allReports.length} 条研报`);
  console.log(`📁 结果文件: ${RESULTS_FILE} (${size}KB)`);
  console.log(`${'='.repeat(50)}`);
  console.log(`\n💡 提示: 文件已保存，可用以下命令查看:`);
  console.log(`   cat ${RESULTS_FILE}`);
  
  return allReports;
}

// ============ 入口 ============
const keyword = process.argv[2] || process.argv[3] || '光模块';
const pageArg = process.argv.find(arg => !isNaN(parseInt(arg)) && arg.length === 1) || '1';
const maxPage = parseInt(process.argv[process.argv.length - 1]) || 2;

if (process.argv[2] === '--help' || process.argv[2] === '-h') {
  console.log(`
📥 投研研报下载工具 v3（东方财富公开API）

用法:
  node research_emf.js <关键词> [最大页数]
  
示例:
  node research_emf.js 光模块              # 搜索光模块，最多2页
  node research_emf.js AI算力 3            # 搜索AI算力，最多3页  
  node research_emf.js 机器人 1            # 搜索机器人，1页
  node research_emf.js                    # 默认搜索"光模块"

输出:
  研报标题、发布机构、发布日期、链接
  结果保存到 /workspace/emf_search_results.json

说明:
  ✅ 无需登录/注册/付费
  ✅ 无需Selenium/ChromeDriver
  ✅ 完全免费，完全公开
  ⚠  仅限东方财富平台
  `);
  process.exit(0);
}

downloadAll(keyword, Math.min(maxPage, 5))
  .then(() => process.exit(0))
  .catch(e => { console.error('\n❌ 错误:', e.message); process.exit(1); });
