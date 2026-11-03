#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { extractArticle, downloadImage, extractImageUrls, getImageExtension } = require('./extract');
const { createDocx } = require('./create-docx');

/**
 * 主函数：将微信公众号文章转换为Word文档
 * @param {string} articleUrl - 文章URL
 * @param {string} outputDir - 输出目录
 * @param {string} filename - 文件名（可选）
 */
async function convertWechatToDocx(articleUrl, outputDir, filename = null) {
  console.log('开始解析文章:', articleUrl);
  
  // 1. 解析文章
  const result = await extractArticle(articleUrl);
  
  if (!result.done) {
    throw new Error('文章解析失败: ' + result.msg);
  }
  
  const articleData = result.data;
  console.log('文章标题:', articleData.msg_title);
  console.log('公众号:', articleData.account_name);
  
  // 2. 创建输出目录
  const safeTitle = filename || articleData.msg_title.replace(/[\\/:*?"<>|]/g, '_').substring(0, 50);
  const articleDir = path.join(outputDir, safeTitle);
  const imagesDir = path.join(articleDir, 'images');
  
  if (!fs.existsSync(articleDir)) {
    fs.mkdirSync(articleDir, { recursive: true });
  }
  if (!fs.existsSync(imagesDir)) {
    fs.mkdirSync(imagesDir, { recursive: true });
  }
  
  // 3. 下载图片
  console.log('提取图片...');
  const imageUrls = extractImageUrls(articleData.msg_content);
  console.log('发现', imageUrls.length, '张图片');
  
  if (imageUrls.length > 0) {
    console.log('开始下载图片...');
    let downloaded = 0;
    
    for (let i = 0; i < imageUrls.length; i++) {
      const url = imageUrls[i];
      const ext = getImageExtension(url);
      const imgFilename = `img_${String(i + 1).padStart(2, '0')}.${ext}`;
      const imgPath = path.join(imagesDir, imgFilename);
      
      try {
        await downloadImage(url, imgPath);
        downloaded++;
        console.log(`下载完成: ${imgFilename}`);
      } catch (err) {
        console.error(`下载失败: ${imgFilename}`, err.message);
      }
    }
    
    console.log(`图片下载完成: ${downloaded}/${imageUrls.length}`);
  }
  
  // 4. 生成Word文档
  console.log('生成Word文档...');
  const docxPath = path.join(articleDir, `${safeTitle}.docx`);
  await createDocx(articleData, imagesDir, docxPath);
  
  // 5. 保存文章元数据
  const metaPath = path.join(articleDir, 'metadata.json');
  fs.writeFileSync(metaPath, JSON.stringify({
    title: articleData.msg_title,
    description: articleData.msg_desc,
    author: articleData.msg_author,
    publishTime: articleData.msg_publish_time_str,
    accountName: articleData.account_name,
    accountId: articleData.account_id,
    url: articleUrl,
    imageCount: imageUrls.length
  }, null, 2));
  
  console.log('转换完成!');
  console.log('输出目录:', articleDir);
  console.log('Word文档:', docxPath);
  
  return {
    articleDir,
    docxPath,
    imagesDir,
    imageCount: imageUrls.length
  };
}

// 命令行调用
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.log('用法: node main.js <文章URL> [输出目录] [文件名]');
    console.log('示例: node main.js https://mp.weixin.qq.com/s/xxx ./output');
    process.exit(1);
  }
  
  const url = args[0];
  const outputDir = args[1] || './output';
  const filename = args[2] || null;
  
  convertWechatToDocx(url, outputDir, filename)
    .then(() => process.exit(0))
    .catch(err => {
      console.error('错误:', err.message);
      process.exit(1);
    });
}

module.exports = { convertWechatToDocx };
