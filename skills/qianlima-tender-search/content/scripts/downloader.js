/**
 * 附件下载模块
 * 负责从千里马详情页获取附件列表并下载为 PDF/DOCX
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { formatAmount, getTypeInfo } = require('./formatter');

const DETAIL_API_BASE = 'https://detail.vip.qianlima.com/rest/detail/alltypesdetail/detail';

/**
 * 确保目录存在
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  return dirPath;
}

/**
 * 获取今天的日期目录名
 */
function getTodayDir() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * 清理文件名中的非法字符
 */
function sanitizeFilename(filename) {
  if (!filename) return '未命名';
  return filename.replace(/[\\/:*?"<>|]/g, '_').trim();
}

/**
 * 将URL转为合适的文件名后缀
 */
function getExtFromUrl(url) {
  if (!url) return '.pdf';
  const lowerUrl = url.toLowerCase();
  if (lowerUrl.endsWith('.doc')) return '.doc';
  if (lowerUrl.endsWith('.docx')) return '.docx';
  if (lowerUrl.endsWith('.pdf')) return '.pdf';
  if (lowerUrl.endsWith('.xls') || lowerUrl.endsWith('.xlsx')) return '.xlsx';
  if (lowerUrl.endsWith('.zip')) return '.zip';
  if (lowerUrl.endsWith('.rar')) return '.rar';
  if (lowerUrl.endsWith('.jpg')) return '.jpg';
  if (lowerUrl.endsWith('.jpeg')) return '.jpeg';
  if (lowerUrl.endsWith('.png')) return '.png';
  return '.pdf'; // 默认pdf
}

/**
 * 从千里马详情API获取附件列表
 */
async function getAttachmentList(itemId, session, keyWord = '') {
  const detailUrl = `${DETAIL_API_BASE}/${itemId}`;

  const body = `keyWord=${encodeURIComponent(keyWord + ',')}&attachmentList`;

  return new Promise((resolve, reject) => {
    const cookies = [
      `qlm_visitor_id=3579584701`,
      `guest_id=04159b9f-d933-4d73-81cd-7c49155e077a`,
      `seo_curUrl=www.qianlima.com`,
      `qlm_username=${session.username}`,
      `qlm_password=${session.password}`,
      `xAuthToken=${session.token}`,
      `HWWAFSESID=${session.sesId}`,
      `HWWAFSESTIME=${session.sesTime}`
    ].join('; ');

    const options = {
      hostname: 'detail.vip.qianlima.com',
      port: 443,
      path: `/rest/detail/alltypesdetail/detail/${itemId}`,
      method: 'POST',
      headers: {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body),
        'Cookie': cookies,
        'Origin': 'https://www.qianlima.com',
        'Referer': 'https://www.qianlima.com/',
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
          if (data.code === 200 || data.code === 0) {
            resolve(data);
          } else {
            resolve(null); // 非200也返回null，不拒绝
          }
        } catch (e) {
          resolve(null);
        }
      });
    });

    req.on('error', () => resolve(null));
    req.write(body);
    req.end();
  });
}

/**
 * 从HTML content中提取附件下载链接
 */
function extractAttachmentsFromContent(content) {
  if (!content) return [];

  const attachments = [];
  // 匹配 <a href="http://www.qianlima.com/downloads/agent.jsp?req=...">文件名.pdf</a>
  const pattern = /<a\s+href=["']([^"']+)["'][^>]*>([^<]+)<\/a>/gi;
  let match;

  while ((match = pattern.exec(content)) !== null) {
    const url = match[1];
    const name = match[2].trim();
    // 检查是否是千里马的下载链接
    if (url && url.includes('qianlima.com/downloads/')) {
      attachments.push({ name, url });
    }
  }

  return attachments;
}

/**
 * 从详情响应中提取附件列表
 */
function extractAttachments(detailData) {
  if (!detailData) return [];

  // 附件可能在多个位置
  let attachments = [];

  // 首先尝试 attachmentList 字段（包含filepathId）
  if (detailData.data && detailData.data.attachmentList) {
    attachments = detailData.data.attachmentList;
  } else if (detailData.attachmentList) {
    attachments = detailData.attachmentList;
  } else if (detailData.data && detailData.data.attachments) {
    attachments = detailData.data.attachments;
  } else if (detailData.data && Array.isArray(detailData.data)) {
    attachments = detailData.data;
  }

  // 如果有attachmentList，尝试从中提取并补充URL
  if (Array.isArray(attachments) && attachments.length > 0) {
    // 从HTML content中提取agent.jsp URLs
    const content = detailData.data?.content || detailData.content;
    const contentUrls = extractUrlsFromContent(content);

    return attachments.filter(att => {
      return att && (att.fileName || att.filepathId);
    }).map(att => {
      // 尝试匹配content中的URL
      let url = att.url || att.downLinkUrl || null;
      if (!url && att.fileName && contentUrls) {
        // 查找文件名对应的URL
        const match = contentUrls.find(u => u.name.includes(att.fileName?.replace('.pdf', '').replace('.doc', '').replace('.docx', '')));
        if (match) {
          url = match.url;
        }
      }
      // 如果还是没有，取第一个contentUrl
      if (!url && contentUrls && contentUrls.length > 0) {
        url = contentUrls[0].url;
      }

      return {
        name: att.fileName || att.name || '附件',
        filepathId: att.filepathId || null,
        size: att.fileSize || att.size || 0,
        url: url
      };
    });
  }

  // 如果没有attachmentList，尝试从HTML content中提取（备选方案）
  const content = detailData.data?.content || detailData.content;
  if (content) {
    return extractAttachmentsFromContent(content);
  }

  return [];
}

/**
 * 从HTML content中提取下载URL列表
 */
function extractUrlsFromContent(content) {
  if (!content) return null;

  const urls = [];
  // 匹配千里马下载链接
  const pattern = /<a\s+href=["']([^"']*qianlima\.com\/downloads\/[^"']+)["'][^>]*>([^<]+)<\/a>/gi;
  let match;

  while ((match = pattern.exec(content)) !== null) {
    urls.push({
      url: match[1],
      name: match[2].trim()
    });
  }

  return urls.length > 0 ? urls : null;
}

/**
 * 从HTML内容中提取真实下载链接（外部URL）
 */
function extractExternalUrl(htmlContent) {
  if (!htmlContent) return null;

  // 查找所有HTTP(S) URL，找到第一个非qianlima的外部链接
  const urlMatches = htmlContent.match(/https?:\/\/[^\s<>"']+/g);
  if (urlMatches) {
    for (const url of urlMatches) {
      // 过滤掉qianlima自己的URL和w3.org等资源链接
      if (!url.includes('qianlima.com') && !url.includes('w3.org')) {
        // 优先返回包含文件扩展名的URL（pdf、doc、zip等）
        if (url.includes('.pdf') || url.includes('.doc') || url.includes('.zip') || url.includes('.rar') || url.includes('.xls')) {
          return url;
        }
        // 或者是外部政府文档平台链接
        if (url.includes('jxemall') || url.includes('gov-open-doc') || url.includes('.gov.')) {
          return url;
        }
      }
    }
  }

  return null;
}

/**
 * 获取千里马agent.jsp的HTML内容
 */
async function fetchAgentJspPage(agentJspUrl, session) {
  return new Promise((resolve) => {
    const { execSync } = require('child_process');
    const cookies = [
      `qlm_visitor_id=3579584701`,
      `guest_id=04159b9f-d933-4d73-81cd-7c49155e077a`,
      `seo_curUrl=www.qianlima.com`,
      `qlm_username=${session.username}`,
      `qlm_password=${session.password}`,
      `xAuthToken=${session.token}`,
      `HWWAFSESID=${session.sesId}`,
      `HWWAFSESTIME=${session.sesTime}`
    ].join('; ');

    // 拼接完整URL
    const fullUrl = agentJspUrl.startsWith('http')
      ? agentJspUrl
      : `http://www.qianlima.com/downloads/agent.jsp?req=${agentJspUrl}`;

    try {
      const cmd = `curl -s -L "${fullUrl}" --cookie "${cookies}" -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0" --max-time 30`;
      const result = execSync(cmd, { encoding: 'utf-8', maxBuffer: 5 * 1024 * 1024 });
      resolve(result);
    } catch (e) {
      resolve('');
    }
  });
}

/**
 * 使用curl直接下载文件
 */
function curlDownload(url, outputPath) {
  const { execSync } = require('child_process');
  const cmd = `curl -s -L "${url}" -o "${outputPath}" -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0" --max-time 60`;
  try {
    execSync(cmd, { encoding: 'utf-8', maxBuffer: 50 * 1024 * 1024 });
    return fs.existsSync(outputPath);
  } catch (e) {
    return false;
  }
}

/**
 * 使用千里马 getZBFileStreamByPathId 接口下载文件
 */
function downloadByZBFileStream(contentId, filepathId, outputPath, cookies) {
  const { execSync } = require('child_process');
  const url = `https://detail.vip.qianlima.com/rest/detail/alltypesdetail/getZBFileStreamByPathId?contentId=${contentId}&filepathId=${filepathId}`;

  // 构建curl命令
  const cmdParts = [
    'curl -s -L',
    `"${url}"`,
    '-o', `"${outputPath}"`,
    '--cookie', `"${cookies}"`,
    '-A', '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"',
    '--max-time', '60'
  ];

  const cmd = cmdParts.join(' ');
  try {
    execSync(cmd, { encoding: 'utf-8', maxBuffer: 50 * 1024 * 1024 });

    // 检查是否返回HTML错误页面
    if (fs.existsSync(outputPath)) {
      const stats = fs.statSync(outputPath);
      if (stats.size < 1000) {
        try {
          const content = fs.readFileSync(outputPath, 'utf-8');
          if (content.includes('<html') || content.includes('DOCTYPE')) {
            return false;
          }
        } catch (e) {}
      }
      return true;
    }
    return false;
  } catch (e) {
    return false;
  }
}

/**
 * 下载单个附件
 */
async function downloadAttachment(attachment, outputPath, session, contentId) {
  // 构建完整cookie
  const cookies = [
    `qlm_visitor_id=3579584701`,
    `guest_id=04159b9f-d933-4d73-81cd-7c49155e077a`,
    `seo_curUrl=www.qianlima.com`,
    `qlm_username=${session.username}`,
    `qlm_password=${session.password}`,
    `xAuthToken=${session.token}`,
    `HWWAFSESID=${session.sesId}`,
    `HWWAFSESTIME=${session.sesTime}`
  ].join('; ');

  // 确保目录存在
  ensureDir(path.dirname(outputPath));

  // 如果有filepathId，使用 getZBFileStreamByPathId 接口下载
  if (attachment.filepathId) {
    const downloadContentId = contentId || attachment.contentId || attachment.filepathId;
    return downloadByZBFileStream(downloadContentId, attachment.filepathId, outputPath, cookies);
  }

  // 如果有直接URL，尝试直接下载
  if (attachment.url && attachment.url.startsWith('http')) {
    return curlDownload(attachment.url, outputPath);
  }

  return false;
}

/**
 * 为项目生成文件名
 */
function generateFilename(item, attachment) {
  const title = sanitizeFilename(item.showTitle || item.popTitle || '未命名');
  const typeInfo = getTypeInfo(item.noticeSegmentType, item.noticeSegmentTypeName, item.progName);
  const typeName = sanitizeFilename(typeInfo.name);

  // 从附件URL获取扩展名
  const ext = getExtFromUrl(attachment.url || attachment.name);

  return `${title}_${typeName}${ext}`;
}

/**
 * 处理单个招标项目：获取附件并下载
 */
async function processItem(item, session, saveDir, keyWord) {
  const results = {
    itemTitle: item.showTitle || item.popTitle || '未知',
    itemId: item.id || item.contentid || item.mysqlId,
    attachments: [],
    downloaded: [],
    failed: []
  };

  if (!results.itemId) {
    return results;
  }

  // 获取详情页附件列表
  const detailData = await getAttachmentList(results.itemId, session, keyWord);
  const attachments = extractAttachments(detailData);

  results.attachments = attachments;

  if (attachments.length === 0) {
    return results;
  }

  // 下载每个附件
  for (const att of attachments) {
    const filename = generateFilename(item, att);
    const outputPath = path.join(saveDir, filename);

    const success = await downloadAttachment(att, outputPath, session, results.itemId);

    if (success) {
      results.downloaded.push({
        name: att.name,
        filename: filename,
        size: att.size,
        path: outputPath
      });
    } else {
      results.failed.push({
        name: att.name,
        url: att.url
      });
    }
  }

  return results;
}

/**
 * 批量处理搜索结果，下载所有附件
 */
async function downloadAllAttachments(items, session, baseDir, keyWord) {
  // 创建日期目录
  const todayDir = getTodayDir();
  const saveDir = ensureDir(path.join(baseDir, todayDir));

  console.error(`\n📁 附件保存目录: ${saveDir}`);
  console.error(`📥 开始下载 ${items.length} 个项目的附件...\n`);

  const summary = {
    totalItems: items.length,
    itemsWithAttachments: 0,
    totalAttachments: 0,
    downloadedFiles: [],
    failedFiles: [],
    errors: []
  };

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const title = item.showTitle || item.popTitle || '未知';

    process.stdout.write(`\r  [${i + 1}/${items.length}] 正在处理: ${title.substring(0, 30)}${'...'.substring(title.length > 30)}`);

    try {
      const result = await processItem(item, session, saveDir, keyWord);

      if (result.attachments.length > 0) {
        summary.itemsWithAttachments++;
        summary.totalAttachments += result.attachments.length;

        for (const downloaded of result.downloaded) {
          summary.downloadedFiles.push(downloaded);
        }

        for (const failed of result.failed) {
          summary.failedFiles.push({
            ...failed,
            itemTitle: result.itemTitle
          });
        }
      }
    } catch (e) {
      summary.errors.push({
        itemTitle: title,
        error: e.message
      });
    }

    // 添加延迟避免请求过快
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.error('\n');
  return summary;
}

/**
 * 生成下载报告
 */
function formatDownloadReport(summary, query) {
  let md = `\n---\n\n## 附件下载报告\n\n`;
  md += `**查询条件**: ${query}\n`;
  md += `**下载时间**: ${new Date().toLocaleString('zh-CN')}\n\n`;

  md += `### 下载统计\n\n`;
  md += `- **处理项目数**: ${summary.totalItems}\n`;
  md += `- **含附件项目**: ${summary.itemsWithAttachments}\n`;
  md += `- **附件总数**: ${summary.totalAttachments}\n`;
  md += `- **下载成功**: ${summary.downloadedFiles.length}\n`;
  md += `- **下载失败**: ${summary.failedFiles.length}\n`;

  if (summary.errors.length > 0) {
    md += `- **处理错误**: ${summary.errors.length}\n`;
  }

  if (summary.downloadedFiles.length > 0) {
    md += `\n### 已下载文件\n\n`;
    md += `| 序号 | 文件名 | 项目名称 | 保存路径 |\n`;
    md += `| --- | --- | --- | --- |\n`;

    for (let i = 0; i < summary.downloadedFiles.length; i++) {
      const f = summary.downloadedFiles[i];
      const relPath = f.path.replace(/\\/g, '/');
      md += `| ${i + 1} | ${f.name} | ${f.path.split('/').pop().split('_').slice(0, -1).join('_') || '-'} | ${relPath} |\n`;
    }
    md += `\n`;
  }

  if (summary.failedFiles.length > 0) {
    md += `\n### 下载失败\n\n`;
    md += `| 项目 | 附件名 | 链接 |\n`;
    md += `| --- | --- | --- |\n`;

    for (const f of summary.failedFiles) {
      md += `| ${f.itemTitle} | ${f.name} | [打开链接](${f.url}) |\n`;
    }
    md += `\n`;
  }

  if (summary.errors.length > 0) {
    md += `\n### 处理错误\n\n`;
    for (const e of summary.errors) {
      md += `- **${e.itemTitle}**: ${e.error}\n`;
    }
    md += `\n`;
  }

  return md;
}

module.exports = {
  downloadAllAttachments,
  formatDownloadReport,
  getAttachmentList,
  extractAttachments,
  processItem,
  getTodayDir,
  ensureDir,
  sanitizeFilename,
  generateFilename
};
