const { extract } = require('C:\\Users\\ET\\.workbuddy\\skills\\wechat-article-extractor-skill\\scripts\\extract.js');
const fs = require('fs');
const https = require('https');
const path = require('path');

/**
 * 解析微信公众号文章
 * @param {string} url - 文章URL
 * @returns {Promise<Object>} 解析结果
 */
async function extractArticle(url) {
  try {
    const result = await extract(url, { shouldReturnContent: true });
    return result;
  } catch (error) {
    console.error('解析文章失败:', error.message);
    throw error;
  }
}

/**
 * 下载图片
 * @param {string} url - 图片URL
 * @param {string} outputPath - 保存路径
 * @returns {Promise<void>}
 */
function downloadImage(url, outputPath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(outputPath);
    https.get(url.replace(/&amp;/g, '&'), (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(outputPath, () => {});
      reject(err);
    });
  });
}

/**
 * 从文章内容中提取所有图片URL
 * @param {string} content - HTML内容
 * @returns {string[]} 图片URL数组
 */
function extractImageUrls(content) {
  const imgRegex = /data-src="([^"]+)"/g;
  const urls = [];
  let match;
  while ((match = imgRegex.exec(content)) !== null) {
    if (!urls.includes(match[1])) {
      urls.push(match[1]);
    }
  }
  return urls;
}

/**
 * 获取图片文件扩展名
 * @param {string} url - 图片URL
 * @returns {string} 扩展名
 */
function getImageExtension(url) {
  if (url.includes('wx_fmt=gif')) return 'gif';
  if (url.includes('wx_fmt=png')) return 'png';
  return 'jpg';
}

module.exports = {
  extractArticle,
  downloadImage,
  extractImageUrls,
  getImageExtension
};
