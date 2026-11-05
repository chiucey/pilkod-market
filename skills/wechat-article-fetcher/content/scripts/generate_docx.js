// Word文档生成脚本 - 最终修复版
// 使用顺序匹配，图片按HTML中出现顺序与正文穿插
const { 
    Document, Packer, Paragraph, TextRun, ImageRun, 
    HeadingLevel, AlignmentType 
} = require('docx');
const fs = require('fs');
const path = require('path');

async function generateDocx(dataPath, outputPath) {
    const articleData = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
    
    console.log('========================================');
    console.log('Word 文档生成器 - 最终修复版');
    console.log('========================================');
    console.log('\n文章:', articleData.title);
    
    const children = [];
    
    // 标题
    children.push(
        new Paragraph({
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: articleData.title, bold: true, size: 36, font: 'Microsoft YaHei' })],
            spacing: { after: 400 }
        })
    );
    
    // 元信息
    if (articleData.publish_time) {
        children.push(new Paragraph({
            children: [new TextRun({ text: `📅 发布时间：${articleData.publish_time}`, size: 20, color: '666666', font: 'Microsoft YaHei' })],
            spacing: { after: 100 }
        }));
    }
    if (articleData.author) {
        children.push(new Paragraph({
            children: [new TextRun({ text: `✍️ 作者：${articleData.author}`, size: 20, color: '666666', font: 'Microsoft YaHei' })],
            spacing: { after: 100 }
        }));
    }
    children.push(new Paragraph({
        children: [new TextRun({ text: '━'.repeat(40), color: 'CCCCCC' })],
        spacing: { after: 400 }
    }));
    
    // 解析HTML，找出图片位置
    const html = articleData.content_html || '';
    const images = articleData.images || [];
    
    // 找出每个<img>标签在HTML中的位置
    const imgRegex = /<img[^>]*>/gi;
    const imgPositions = [];
    let match;
    while ((match = imgRegex.exec(html)) !== null) {
        imgPositions.push({
            position: match.index,
            tag: match[0]
        });
    }
    
    console.log(`找到 ${imgPositions.length} 个图片位置`);
    
    // 找出正文段落
    const content = articleData.content || '';
    const lines = content.split('\n');
    
    // 过滤非正文行
    const paragraphs = lines.filter(line => {
        const text = line.trim();
        if (!text || text.length < 3) return false;
        if (text === '三联生活周刊') return false;
        if (text.includes('公众号') && text.includes('原创内容')) return false;
        if (text.includes('篇原创内容')) return false;
        if (text.startsWith('扫码添加')) return false;
        if (text.includes('企业微信')) return false;
        if (text === '"点赞""在看"，让更多人看到') return false;
        if (text === '排版：球球 / 审核：小风') return false;
        if (text.includes('招聘｜撰稿人')) return false;
        if (text.includes('点击跳转')) return false;
        if (text === '本文为原创内容') return false;
        if (text.includes('欢迎文末分享')) return false;
        if (text === '大家都在看') return false;
        if (text === '一本杂志和他倡导的生活。') return false;
        return true;
    });
    
    console.log(`有效段落: ${paragraphs.length}`);
    
    // 关键：根据HTML中的图片位置，判断图片应该插入在哪些段落之间
    // 方法：找到每个<img>标签后面的第一个文字内容
    
    // 简化策略：微信文章中，图片通常是独立成段的，前后有"《XX》剧照"等说明
    // 或者穿插在正文段落之间
    
    // 更精确的方法：分析HTML结构
    // 微信文章通常是：<p>文字</p><p><img></p><p>文字</p>
    
    // 找出每个段落和图片在原始内容中的相对位置
    const contentItems = [];
    
    // 按段落处理
    let textIndex = 0;
    for (let i = 0; i < paragraphs.length; i++) {
        const text = paragraphs[i];
        // 在HTML中查找这段文字
        const searchText = text.substring(0, 30);
        const pos = html.indexOf(searchText, textIndex);
        
        if (pos >= 0) {
            contentItems.push({
                type: 'text',
                position: pos,
                text: text,
                index: i
            });
            textIndex = pos + searchText.length;
        } else {
            // 文字可能在中间位置，给一个估算位置
            contentItems.push({
                type: 'text',
                position: textIndex,
                text: text,
                index: i
            });
        }
    }
    
    // 添加图片（按顺序匹配）
    for (let i = 0; i < imgPositions.length && i < images.length; i++) {
        contentItems.push({
            type: 'image',
            position: imgPositions[i].position,
            imgIndex: i,
            img: images[i]
        });
    }
    
    // 按位置排序
    contentItems.sort((a, b) => a.position - b.position);
    
    console.log(`内容项: ${contentItems.length} (文字: ${contentItems.filter(c => c.type === 'text').length}, 图片: ${contentItems.filter(c => c.type === 'image').length})`);
    
    // 渲染
    let lastType = null;
    for (const item of contentItems) {
        if (item.type === 'text') {
            const text = item.text;
            
            // 判断是否是图片说明（通常包含"剧照"）
            const isImageCaption = text.includes('剧照') || text.includes('图：') || text.length < 20;
            
            // 判断是否是小标题
            const isSubtitle = text.length < 30 && !text.includes('，') && !text.includes('。') && item.index < 15;
            
            if (isSubtitle) {
                children.push(new Paragraph({
                    children: [new TextRun({ text: text, bold: true, size: 24, font: 'Microsoft YaHei' })],
                    spacing: { before: 300, after: 150 }
                }));
            } else if (isImageCaption && lastType === 'image') {
                // 图片说明，居中显示
                children.push(new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [new TextRun({ text: text, size: 18, color: '666666', font: 'Microsoft YaHei', italics: true })],
                    spacing: { after: 200 }
                }));
            } else {
                // 普通段落
                children.push(new Paragraph({
                    children: [new TextRun({ text: text, size: 22, font: 'Microsoft YaHei' })],
                    spacing: { after: 150 },
                    indent: { firstLine: 440 }
                }));
            }
            lastType = 'text';
            
        } else if (item.type === 'image') {
            try {
                const img = item.img;
                const imgBuffer = fs.readFileSync(img.path);
                const maxWidth = 450;
                const scale = img.width > maxWidth ? maxWidth / img.width : 1;
                
                children.push(new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [new ImageRun({
                        type: img.format || 'jpg',
                        data: imgBuffer,
                        transformation: {
                            width: Math.round(img.width * scale),
                            height: Math.round(img.height * scale)
                        }
                    })],
                    spacing: { before: 200, after: 100 }
                }));
                
                lastType = 'image';
            } catch (e) {
                console.log(`图片加载失败: ${e.message}`);
            }
        }
    }
    
    // 文档信息
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: '─'.repeat(40), color: 'CCCCCC' })],
        spacing: { before: 400, after: 200 }
    }));
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: `抓取时间：${articleData.fetch_time}`, color: '999999', font: 'Microsoft YaHei', size: 18 })],
        spacing: { after: 100 }
    }));
    
    // 创建文档
    const doc = new Document({
        styles: { default: { document: { run: { font: 'Microsoft YaHei', size: 22 } } } },
        sections: [{
            properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
            children: children
        }]
    });
    
    // 保存
    const desktop = 'C:\\Users\\Administrator\\Desktop';
    const title = articleData.title.replace(/[\\/:*?"<>|]/g, '_');
    const finalOutputPath = outputPath || path.join(desktop, `${title}.docx`);
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(finalOutputPath, buffer);
    
    console.log('\n========================================');
    console.log('✓ Word 文档生成成功');
    console.log('========================================');
    console.log(`文件: ${finalOutputPath}`);
    console.log(`大小: ${(buffer.length / 1024).toFixed(2)} KB`);
    
    return finalOutputPath;
}

if (require.main === module) {
    const dataPath = process.argv[2];
    generateDocx(dataPath).catch(err => {
        console.error('错误:', err);
        process.exit(1);
    });
}

module.exports = { generateDocx };
