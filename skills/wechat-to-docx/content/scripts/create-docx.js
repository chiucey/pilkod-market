const { Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, BorderStyle } = require('docx');
const fs = require('fs');
const path = require('path');

/**
 * 解码 HTML 实体
 */
function decodeEntities(str) {
  return str
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCharCode(parseInt(d, 10)));
}

/**
 * 从 style 字符串提取属性值
 */
function getStyleVal(styleStr, prop) {
  if (!styleStr) return '';
  const m = new RegExp(prop + '\\s*:\\s*([^;]+)', 'i').exec(styleStr);
  return m ? m[1].trim() : '';
}

/**
 * 判断一段文字是否是 attribution（文稿/编辑/审核 等元信息）
 */
function isAttributionText(text) {
  return /^(撰稿|图片|编辑|一审|二审|三审|终审|审核|校对|排版)[|：:]/.test(text.trim());
}

/**
 * 判断一段文字是否像小标题（短且居中/大字号）
 */
function isHeading(text, style) {
  if (!text || text.length > 60 || text.length < 2) return false;
  const align = getStyleVal(style, 'text-align');
  const fontSize = getStyleVal(style, 'font-size');
  const fontSizeNum = parseFloat(fontSize);
  if (align === 'center' && text.replace(/\s/g, '').length < 20) return true;
  if (fontSizeNum >= 20) return true;
  return false;
}

/**
 * CSS 颜色转 6位 hex
 */
function cssColorToHex(color) {
  if (!color) return '';
  const c = color.trim();
  if (c.startsWith('#')) {
    const h = c.slice(1);
    if (h.length === 3) return h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
    if (h.length === 6) return h;
  }
  const named = { 'red':'FF0000','blue':'0000FF','green':'008000','black':'000000',
    'white':'FFFFFF','gray':'808080','grey':'808080','orange':'FFA500','purple':'800080' };
  return named[c.toLowerCase()] || '';
}

/**
 * 对齐方式转换
 */
function getAlignment(align) {
  if (!align) return AlignmentType.LEFT;
  const a = align.toLowerCase().trim();
  if (a === 'center') return AlignmentType.CENTER;
  if (a === 'right') return AlignmentType.RIGHT;
  if (a === 'justify') return AlignmentType.BOTH;
  return AlignmentType.LEFT;
}

/**
 * 计算图片显示尺寸（适配 A4 宽度 500pt）
 */
function calcImageSize(origW, origH) {
  const maxW = 500, maxH = 400;
  let w = origW || 400, h = origH || 300;
  if (w <= 100 && h <= 100) return { width: 80, height: 80 };
  if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
  if (h > maxH) { w = Math.round(w * maxH / h); h = maxH; }
  return { width: Math.max(w, 50), height: Math.max(h, 30) };
}

/**
 * 获取图片类型
 */
function getImageType(url, filename) {
  const src = (filename || url || '');
  if (src.includes('wx_fmt=gif') || src.endsWith('.gif')) return 'gif';
  if (src.includes('wx_fmt=png') || src.endsWith('.png')) return 'png';
  return 'jpg';
}

/**
 * 解析 HTML，按 DOM 顺序提取所有图片和文字节点
 * 返回 [{type:'img'|'text', ...}]
 *
 * 支持两种 HTML 格式：
 * A. <span leaf=""> 格式（微信旧版编辑器）
 * B. <p><span style="">...</span></p> 格式（微信 新版/96编辑器）
 */
function parseHtmlNodes(html) {
  const items = [];

  // ── 1. 提取所有图片（两种格式通用） ──
  const imgRe = /<img[^>]*data-src="([^"]+)"[^>]*/gi;
  let m;
  while ((m = imgRe.exec(html)) !== null) {
    const tag = m[0];
    // 跳过装饰性小图标（宽度 < 100px 的通常是小图标）
    const wMatch = tag.match(/data-w="(\d+)"/);
    const ratioMatch = tag.match(/data-ratio="([\d.]+)"/);
    const w = wMatch ? parseInt(wMatch[1]) : 400;
    const ratio = ratioMatch ? parseFloat(ratioMatch[1]) : 0.6;
    items.push({
      pos: m.index,
      type: 'img',
      url: m[1].replace(/&amp;/g, '&'),
      origW: w,
      origH: Math.round(w * ratio)
    });
  }

  // ── 2. 判断格式：是否有 leaf 属性 ──
  const hasLeaf = /<span[^>]*leaf[^>]*>/i.test(html);

  if (hasLeaf) {
    // ── 格式A：<span leaf=""> ──（旧版微信编辑器）
    extractLeafFormat(html, items);
  } else {
    // ── 格式B：<p><span style="">...</span></p>（新版/96编辑器）──
    extractPlainHtmlFormat(html, items);
  }

  // ── 3. 按位置排序 ──
  items.sort((a, b) => a.pos - b.pos);

  // ── 4. 合并相邻文字节点 ──
  const merged = [];
  let lastText = null;

  for (const item of items) {
    if (item.type === 'img') {
      if (lastText) { merged.push(lastText); lastText = null; }
      merged.push(item);
    } else {
      const dist = item.pos - (lastText ? lastText._endPos : 0);
      const sizeDiff = Math.abs((lastText?.fontSize || 0) - (item.fontSize || 0));
      // attribution 行强制分段，不与前文合并
      const isAttr = isAttributionText(item.text);
      const shouldMerge = lastText &&
        !isAttr &&  // attribution 不合并
        dist < 500 &&
        lastText.align === item.align &&
        sizeDiff < 4 &&
        (dist < 50 || (sizeDiff < 2 && lastText.isBold === item.isBold));

      if (shouldMerge) {
        if (lastText._parts) {
          lastText._parts.push(item);
        } else {
          lastText._parts = [item];
        }
        lastText.text += item.text;
        lastText._endPos = item.pos + item.text.length;
        if (item.color) lastText.color = item.color;
        if (item.fontSize) lastText.fontSize = item.fontSize;
        if (item.isBold) lastText.isBold = true;
      } else {
        if (lastText) merged.push(lastText);
        lastText = { ...item, _endPos: item.pos + item.text.length, _parts: null };
      }
    }
  }
  if (lastText) merged.push(lastText);

  // ── 5. 标记小标题 ──
  merged.forEach(node => {
    if (node.type === 'text') {
      node._isHeading = isHeading(node.text, node.style || '');
    }
  });

  return merged;
}

/**
 * 格式A：提取 <span leaf=""> 中的文字
 */
function extractLeafFormat(html, items) {
  const leafRe = /<span[^>]*leaf[^>]*>([\s\S]*?)<\/span>/gi;
  let m;
  while ((m = leafRe.exec(html)) !== null) {
    const inner = m[1];
    const pos = m.index;
    const before = html.substring(Math.max(0, pos - 400), pos);
    const styleMatch = before.match(/style="([^"]*)"\s*>[^<]*$/);

    const hasImg = /<img[^>]*>/i.test(inner);
    const textRaw = inner
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<img[^>]*>/gi, '')
      .replace(/<[^>]+>/g, '')
      .trim();

    if (hasImg) {
      const inlineImgs = [...inner.matchAll(/<img[^>]*data-src="([^"]+)"[^>]*data-w="(\d+)"[^>]*data-ratio="([\d.]+)"[^>]*/gi)];
      inlineImgs.forEach(imgMatch => {
        items.push({
          pos,
          type: 'img',
          url: imgMatch[1].replace(/&amp;/g, '&'),
          origW: parseInt(imgMatch[2]),
          origH: Math.round(parseInt(imgMatch[2]) * parseFloat(imgMatch[3]))
        });
      });
      if (textRaw && textRaw !== '\n') {
        const style = styleMatch ? styleMatch[1] : '';
        const isBold = /font-weight\s*:\s*(bold|700|900)/i.test(style);
        const colorMatch = style.match(/color\s*:\s*(#[0-9a-fA-F]{3,6}|rgb[^;]+)/i);
        const fsMatch = style.match(/font-size\s*:\s*([\d.]+)/i);
        const alignMatch = before.match(/text-align\s*:\s*(center|left|right|justify)/gi);
        items.push({
          pos, type: 'text',
          text: decodeEntities(textRaw), style,
          isBold,
          color: colorMatch ? colorMatch[1] : '',
          fontSize: fsMatch ? parseFloat(fsMatch[1]) : 14,
          align: alignMatch ? alignMatch[alignMatch.length - 1].replace('text-align:', '').trim() : 'left'
        });
      }
    } else {
      if (textRaw && textRaw !== '\n') {
        const style = styleMatch ? styleMatch[1] : '';
        const isBold = /font-weight\s*:\s*(bold|700|900)/i.test(style) || /<strong\b/i.test(inner) || /<b\b[^>]*>/i.test(inner);
        const colorMatch = style.match(/color\s*:\s*(#[0-9a-fA-F]{3,6}|rgb[^;]+)/i);
        const fsMatch = style.match(/font-size\s*:\s*([\d.]+)/i);
        const alignMatch = before.match(/text-align\s*:\s*(center|left|right|justify)/gi);
        items.push({
          pos, type: 'text',
          text: decodeEntities(textRaw), style,
          isBold,
          color: colorMatch ? colorMatch[1] : '',
          fontSize: fsMatch ? parseFloat(fsMatch[1]) : 14,
          align: alignMatch ? alignMatch[alignMatch.length - 1].replace('text-align:', '').trim() : 'left'
        });
      }
    }
  }
}

/**
 * 格式B：提取普通 HTML 中的 <span> 文字（微信新版编辑器/96编辑器）
 * 策略：
 * 1. 提取所有文字 span（含内联样式）
 * 2. 从 span 向外查找最近的 align/style 属性
 * 3. 排除明显是装饰性的文字（分隔符、空标签等）
 * 4. 排除 SVG 内的 foreignObject 文字（装饰图片）
 */
function extractPlainHtmlFormat(html, items) {
  // 提取所有 <span style="...">文字</span> 文字片段
  // 匹配带内联样式的 span，避免匹配无样式空 span
  const spanRe = /<span(?:\s+[^>]*)?>([\s\S]*?)<\/span>/gi;
  let m;
  while ((m = spanRe.exec(html)) !== null) {
    const outerTag = m[0]; // 完整标签（含属性）
    const inner = m[1];
    const pos = m.index;

    // 跳过无内容的
    const textRaw = inner
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<img[^>]*>/gi, '')
      .replace(/<[^>]+>/g, '')
      .replace(/\xA0/g, ' ')  // &nbsp;
      .trim();
    if (!textRaw || textRaw === '\n') continue;

    // 提取 inline style（从 <span style="..."> 中取）
    const inlineStyleMatch = outerTag.match(/style="([^"]*)"/);
    const inlineStyle = inlineStyleMatch ? inlineStyleMatch[1] : '';
    // 也向前找父级 p/section 的 style
    const before = html.substring(Math.max(0, pos - 300), pos);
    const parentStyleMatch = before.match(/style="([^"]*)"[^>]*>(?:\s*<[^>]+>)*\s*$/);

    const combinedStyle = inlineStyle + ';' + (parentStyleMatch ? parentStyleMatch[1] : '');

    // 提取样式属性
    const isBold = /font-weight\s*:\s*(bold|700|900|\d{3,})/i.test(combinedStyle) ||
                   /<strong\b/i.test(inner) || /<b\b[^>]*>/i.test(inner);
    const colorMatch = combinedStyle.match(/color\s*:\s*(#[0-9a-fA-F]{3,6}|rgb[^;)]+)/i);
    const fsMatch = combinedStyle.match(/font-size\s*:\s*([\d.]+)/i);
    // 对齐：优先取 <span> 所在 <p> 的 align，或 inline style 中的
    const pAlignMatch = before.match(/<p[^>]*style="[^"]*text-align\s*:\s*(center|left|right|justify)[^"]*"[^>]*>/i);
    const inlineAlignMatch = inlineStyle.match(/text-align\s*:\s*(center|left|right|justify)/i);
    const align = pAlignMatch ? pAlignMatch[1] : (inlineAlignMatch ? inlineAlignMatch[1] : 'left');

    // ── 过滤掉装饰性内容 ──
    // 1. 纯空白字符 + 短分隔符（---、===、空白行）
    if (/^[\s·\-–=:~\\|\u2500-\u257F\u2500-\u257F*#●○■□◆◇★☆]+$/.test(textRaw)) continue;
    // 2. 极短的无意义碎片（1-2个字的非中文）
    if (textRaw.length <= 2 && !/[\u4e00-\u9fa5]/.test(textRaw)) continue;
    // 3. 明显是 SVG foreignObject 装饰内容（如编辑器水印）
    if (before.includes('foreignobject') || before.includes('svg')) continue;
    // 4. 纯 emoji/符号（不含中文）
    if (/^[^\u4e00-\u9fa5a-zA-Z0-9]{1,5}$/.test(textRaw) && textRaw.length < 6) continue;

    // 排除 attribution 前的纯分割内容（撰稿|编辑|审核 等后面单独处理）
    // 不在格式B里处理 attribution，让它们自然分段即可

    const fontSize = fsMatch ? parseFloat(fsMatch[1]) : 14;

    items.push({
      pos,
      type: 'text',
      text: decodeEntities(textRaw),
      style: combinedStyle,
      isBold,
      color: colorMatch ? colorMatch[1] : '',
      fontSize,
      align
    });
  }

  // ── 补充：提取纯 <p> 中没有 <span> 包裹的文字（如标题段落） ──
  // 匹配 <p style="...">纯文字</p>（无子 span）
  const pPlainRe = /<p(?:\s[^>]*)?>((?:(?!<span).)*?)<\/p>/gi;
  while ((m = pPlainRe.exec(html)) !== null) {
    const inner = m[1];
    const pos = m.index;
    const textRaw = inner
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<img[^>]*>/gi, '')
      .replace(/<[^>]+>/g, '')
      .replace(/\xA0/g, ' ')
      .trim();
    if (!textRaw || textRaw === '\n' || textRaw.length < 3) continue;
    // 跳过纯装饰
    if (/^[\s·\-–=:~\\|\u2500-\u257F*#●○■□◆◇★☆]+$/.test(textRaw)) continue;

    const styleMatch = m[0].match(/style="([^"]*)"/);
    const style = styleMatch ? styleMatch[1] : '';
    const alignMatch = style.match(/text-align\s*:\s*(center|left|right|justify)/i);
    const fsMatch = style.match(/font-size\s*:\s*([\d.]+)/i);
    const isBold = /font-weight\s*:\s*(bold|700|900|\d{3,})/i.test(style);
    const colorMatch = style.match(/color\s*:\s*(#[0-9a-fA-F]{3,6}|rgb[^;)]+)/i);

    items.push({
      pos,
      type: 'text',
      text: decodeEntities(textRaw),
      style,
      isBold,
      color: colorMatch ? colorMatch[1] : '',
      fontSize: fsMatch ? parseFloat(fsMatch[1]) : 14,
      align: alignMatch ? alignMatch[1] : 'left'
    });
  }
}

/**
 * 创建 Word 文档
 */
async function createDocx(articleData, imageDir, outputPath) {
  const { msg_title, msg_desc, msg_content, msg_publish_time_str, account_name } = articleData;

  const nodes = parseHtmlNodes(msg_content || '');
  console.log('解析节点数:', nodes.length,
    '(文字:', nodes.filter(n => n.type === 'text').length,
    '图片:', nodes.filter(n => n.type === 'img').length, ')');

  // 读取图片文件（按文件名排序，确保与节点顺序对应）
  const imageFiles = fs.existsSync(imageDir)
    ? fs.readdirSync(imageDir).filter(f => /\.(jpg|jpeg|png|gif)$/i.test(f)).sort()
    : [];

  let imgFileIdx = 0;
  const children = [];

  // ── 封面区 ──
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 280 },
    children: [new TextRun({ text: msg_title, bold: true, size: 36, color: '1a1a1a', font: '微软雅黑' })]
  }));

  if (msg_desc && msg_desc !== msg_title && msg_desc.trim()) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
      children: [new TextRun({ text: msg_desc.length > 120 ? msg_desc.substring(0, 120) + '…' : msg_desc, size: 20, color: '666666', font: '微软雅黑', italics: true })]
    }));
  }

  const metaParts = [];
  if (account_name) metaParts.push(new TextRun({ text: '来源：' + account_name, size: 18, color: '888888', font: '微软雅黑' }));
  if (msg_publish_time_str) {
    if (metaParts.length) metaParts.push(new TextRun({ text: '　　', size: 18, font: '微软雅黑' }));
    metaParts.push(new TextRun({ text: '发布：' + msg_publish_time_str, size: 18, color: '888888', font: '微软雅黑' }));
  }
  if (metaParts.length) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: metaParts
    }));
  }

  // 分隔线
  children.push(new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'DDDDDD', space: 1 } },
    spacing: { after: 360 }
  }));

  // ── 正文区 ──
  let consecutiveBreaks = 0;

  for (const node of nodes) {
    if (node.type === 'img') {
      const imgFile = imageFiles[imgFileIdx];
      if (imgFile) {
        const imgPath = path.join(imageDir, imgFile);
        if (fs.existsSync(imgPath)) {
          const imgData = fs.readFileSync(imgPath);
          const size = calcImageSize(node.origW, node.origH);
          try {
            children.push(new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { before: 160, after: 120 },
              children: [new ImageRun({
                type: getImageType('', imgFile),
                data: imgData,
                transformation: { width: size.width, height: size.height },
                altText: { title: imgFile, description: imgFile, name: imgFile }
              })]
            }));
          } catch (e) {
            console.warn('图片插入失败:', imgFile, e.message);
          }
        }
      }
      imgFileIdx++;
      consecutiveBreaks = 0;

    } else if (node.type === 'text') {
      const raw = node.text.trim();
      if (!raw) continue;

      // 清理多余空白
      const text = raw.replace(/\n{3,}/g, '\n\n').trim();
      if (!text) continue;

      // 控制连续空行
      if (text === '' || text === '　') {
        consecutiveBreaks++;
        if (consecutiveBreaks > 1) continue;
      } else {
        consecutiveBreaks = 0;
      }

      // 判断样式
      const isTitle = node._isHeading;
      const hexColor = cssColorToHex(node.color);
      const isBold = node.isBold || isTitle;

      // 字号映射：微信 px → Word half-points
      let wordSize = 24;
      if (node.fontSize && node.fontSize > 0) {
        const pt = node.fontSize * 0.75;
        wordSize = Math.round(Math.max(16, Math.min(pt * 2, 56)));
      }
      if (isTitle) wordSize = Math.max(wordSize, 32);

      // 构建 runs（支持分段换行）
      const runs = [];
      // 先处理 attribution 行（文稿|...编辑|...一审|...二审|...三审）
      // 把 "文稿|包洋  王静雯      图片|党  倩" 这类粘连项拆成独立行
      const isAttributionLine = /文稿\|/.test(text) && /一审|二审|三审/.test(text);
      if (isAttributionLine) {
        // 按 关键字| 分割
        const attrParts = text.split(/(文稿\|)|(图片\|)|(编辑\|)|(一审[^|二二三审]*)|(二审[^|三审]*)|(三审[^|]*)/g).filter(Boolean).map(s => s.trim()).filter(Boolean);
        attrParts.forEach((part, idx) => {
          if (!part) return;
          if (idx > 0) runs.push(new TextRun({ break: 1 }));
          runs.push(new TextRun({ text: part, bold: false, size: wordSize, color: hexColor || '555555', font: '微软雅黑' }));
        });
      } else {
        // 普通段落：按 \n 分行
        const lines = text.split('\n');
        lines.forEach((line, idx) => {
          if (idx > 0) runs.push(new TextRun({ break: 1 }));
          const trimmed = line.trim();
          if (trimmed) {
            runs.push(new TextRun({
              text: trimmed,
              bold: isBold,
              size: wordSize,
              color: hexColor || (isTitle ? '1a1a1a' : '333333'),
              font: '微软雅黑'
            }));
          }
        });
      }

      if (runs.length === 0) continue;

      children.push(new Paragraph({
        alignment: getAlignment(node.align),
        spacing: {
          before: isTitle ? 240 : 60,
          after: isTitle ? 200 : 80,
          line: isTitle ? 400 : 360,
          lineRule: 'auto'
        },
        children: runs
      }));
    }
  }

  // 追加剩余图片
  while (imgFileIdx < imageFiles.length) {
    const imgFile = imageFiles[imgFileIdx];
    const imgPath = path.join(imageDir, imgFile);
    if (fs.existsSync(imgPath)) {
      const imgData = fs.readFileSync(imgPath);
      try {
        children.push(new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 120, after: 120 },
          children: [new ImageRun({
            type: getImageType('', imgFile),
            data: imgData,
            transformation: { width: 480, height: 300 },
            altText: { title: imgFile, description: imgFile, name: imgFile }
          })]
        }));
      } catch (e) {
        console.warn('追加图片失败:', imgFile, e.message);
      }
    }
    imgFileIdx++;
  }

  // 页脚
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 480 },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: 'EEEEEE', space: 1 } },
    children: [new TextRun({ text: '— 本文档由微信公众号文章自动生成 —', size: 16, color: 'AAAAAA', font: '微软雅黑' })]
  }));

  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: '微软雅黑', size: 24, color: '333333' } }
      }
    },
    sections: [{
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      children: children.filter(Boolean)
    }]
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log('Word 文档已生成:', outputPath);
}

module.exports = { createDocx, parseHtmlNodes };
