#!/usr/bin/env node
/**
 * generate_report_pdf.js — 5AI选股报告 PDF 生成器（pdf-lib）
 * 用法: node generate_report_pdf.js
 * 输出: /workspace/股票分析/5AI超短线选股分析报告_YYYYMMDD.pdf
 */
const PDFLib = require('/workspace/node_modules/pdf-lib');
const {
  PDFDocument, StandardFonts, rgb, PageSizes
} = PDFLib;

const W = PageSizes.A4[0]; // 595.28
const H = PageSizes.A4[1]; // 841.89
const MARGIN = 50;
const CONTENT_W = W - 2 * MARGIN;

// 颜色
const C = {
  darkBlue:   rgb(0.12, 0.28, 0.49),
  mediumBlue: rgb(0.20, 0.40, 0.70),
  lightBlue:  rgb(0.86, 0.93, 1.0),
  green:      rgb(0.13, 0.55, 0.13),
  lightGreen: rgb(0.85, 0.97, 0.85),
  red:        rgb(0.70, 0.0,  0.0),
  lightRed:   rgb(1.0,  0.90, 0.90),
  yellow:     rgb(1.0,  0.97, 0.80),
  gray:       rgb(0.5,  0.5,  0.5),
  lightGray:  rgb(0.95, 0.95, 0.95),
  white:      rgb(1, 1, 1),
  black:      rgb(0, 0, 0),
  gold:       rgb(0.83, 0.64, 0.0),
};

// ==================== 核心绘图函数 ====================

function drawRect(page, x, y, w, h, color) {
  page.drawRectangle({ x, y, width: w, height: h, color });
}

function drawText(page, text, x, y, font, size, color) {
  if (!color) color = C.black;
  page.drawText(String(text || ''), { x, y, size, font, color });
}

function wrapChars(text, maxChars) {
  text = String(text || '');
  const lines = [];
  let cur = '';
  let count = 0;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const cw = (ch >= '\u4e00' && ch <= '\u9fff') ? 2 : 1;
    if (count + cw > maxChars) { lines.push(cur); cur = ch; count = cw; }
    else { cur += ch; count += cw; }
  }
  if (cur) lines.push(cur);
  return lines.length ? lines : [''];
}

function drawHeading1(page, text, y, boldFont, font) {
  drawRect(page, MARGIN, y - 4, CONTENT_W, 1.5, C.darkBlue);
  drawText(page, text, MARGIN, y, boldFont, 15, C.darkBlue);
  return y - 28;
}

function drawHeading2(page, text, y, boldFont, font) {
  drawText(page, text, MARGIN, y, boldFont, 12, C.mediumBlue);
  return y - 20;
}

function drawTable(page, headers, rows, colWidths, x, y, boldFont, font, hbc) {
  hbc = hbc || C.darkBlue;
  const rowH = 16, hdrH = 19;
  const n = headers.length;
  const cws = colWidths || headers.map(() => Math.floor(CONTENT_W / n));
  let cx = x;
  for (let i = 0; i < n; i++) {
    drawRect(page, cx, y - hdrH, cws[i], hdrH, hbc);
    drawText(page, String(headers[i] || '').substring(0, 12), cx + 3, y - hdrH + 5, boldFont, 8.5, C.white);
    cx += cws[i];
  }
  let cy = y - hdrH;
  for (let ri = 0; ri < rows.length; ri++) {
    const row = rows[ri];
    const bg = ri % 2 === 0 ? C.white : C.lightGray;
    cx = x;
    for (let ci = 0; ci < n; ci++) {
      const lines = wrapChars(String(row[ci] || ''), Math.floor(cws[ci] / 6));
      drawRect(page, cx, cy - rowH, cws[ci], rowH, bg);
      drawText(page, lines[0] || '', cx + 3, cy - rowH + 4, font, 7.5, C.black);
      cx += cws[ci];
    }
    cy -= rowH;
  }
  // 表边框
  cx = x;
  const tableH = y - hdrH - rows.length * rowH;
  for (let i = 0; i < n; i++) {
    page.drawRectangle({ x: cx, y: cy, width: cws[i], height: y - cy,
      borderColor: hbc, borderWidth: 0.5 });
    cx += cws[i];
  }
  return cy - 8;
}

function drawWarningBox(page, lines, y, boldFont, font) {
  const boxH = lines.length * 13 + 8;
  drawRect(page, MARGIN, y - boxH, CONTENT_W, boxH, C.lightRed);
  drawRect(page, MARGIN, y - boxH, 4, boxH, C.red);
  let ly = y - 7;
  for (const line of lines) {
    drawText(page, line, MARGIN + 10, ly, font, 7.5, C.red);
    ly -= 13;
  }
  return y - boxH - 10;
}

function drawRanking(page, ranked, y, boldFont, font) {
  let ly = y;
  for (let i = 0; i < ranked.length; i++) {
    const [name, score, avg, votes, tag, tagColor] = ranked[i];
    const medal = i === 0 ? '\u1F947' : i === 1 ? '\u1F948' : i === 2 ? '\u1F949' : ' ' + (i+1);
    const bg = i === 0 ? C.lightGreen : i === 1 ? C.lightBlue : i === 2 ? C.yellow : C.white;
    const lh = 20;
    drawRect(page, MARGIN, ly - lh, CONTENT_W, lh, bg);
    drawRect(page, MARGIN, ly - lh, 4, lh, tagColor || C.darkBlue);
    drawText(page, medal + ' ' + name, MARGIN + 10, ly - lh + 6, boldFont, 11, tagColor || C.black);
    drawText(page, '\u5747\u5206' + avg.toFixed(2) + ' | \u79D1\u79EF' + score + ' | ' + votes + '\u7968 | ' + tag,
             MARGIN + 160, ly - lh + 6, font, 8.5, C.gray);
    ly -= lh;
  }
  return ly - 10;
}

// ==================== 主报告生成 ====================

async function generateReport(data, outPath) {
  const {
    title = '5AI\u8D85\u77ED\u7EBF\u9009\u80A1\u5206\u6790\u62A5\u544A',
    date = '',
    subtitle = '',
    stocks = [], codes = [], prices = [], fundamentals = [],
    aiNames = [], aiScores = [],
    m1Result = [], m2Result = [], m3Result = [],
    finalRank = [],
    champion = [],
    riskLines = [],
  } = data;

  const doc = PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const boldFont = await doc.embedFont(StandardFonts.HelveticaBold);

  // ===== 封面 =====
  const cover = doc.addPage([W, H]);
  cover.drawRectangle({ x: 0, y: 0, width: W, height: H, color: C.darkBlue });
  cover.drawRectangle({ x: 0, y: H - 18, width: W, height: 18, color: C.mediumBlue });
  cover.drawRectangle({ x: 0, y: 0, width: W, height: 28, color: rgb(0.05, 0.12, 0.28) });
  cover.drawText(title, { x: MARGIN, y: H - 140, size: 26, font: boldFont, color: C.white });
  if (subtitle) cover.drawText(subtitle, { x: MARGIN, y: H - 172, size: 12, font, color: rgb(0.7, 0.85, 1) });
  cover.drawText(date, { x: MARGIN, y: H - 200, size: 10, font, color: rgb(0.5, 0.7, 1) });
  cover.drawRectangle({ x: MARGIN, y: H - 220, width: CONTENT_W, height: 1.5, color: C.gold });
  cover.drawText('5AI\u8054\u5408\u5206\u6790\u7CFB\u7EDF  |  DeepSeek \u00B7 Kimi \u00B7 \u8C46\u5305AI \u00B7 \u5343\u95EE \u00B7 MiniMax', {
    x: MARGIN, y: 55, size: 9, font, color: rgb(0.4, 0.6, 1),
  });
  cover.drawText('\u672C\u62A5\u544A\u4EC5\u4F9B\u7814\u7A76\u53C2\u8003\uFF0C\u4E0D\u6784\u6210\u6295\u8D44\u5EFA\u8BAE', {
    x: MARGIN, y: 40, size: 8.5, font, color: rgb(0.3, 0.5, 0.8),
  });

  // ===== 内容页 =====
  const page = doc.addPage([W, H]);
  let y = H - MARGIN;

  // 一、原始数据表
  y = drawHeading1(page, '\u4E00\u30016\u53EA\u80A1\u7968\u539F\u59CB\u6570\u636E\u4E00\u89C8', y, boldFont, font);
  y = drawTable(page,
    ['\u80A1\u7968', '\u4EE3\u7801', '\u6700\u65B0\u4EF7', '\u57FA\u672C\u9762', '\u7F3A\u9677'],
    stocks.map((s, i) => [s, codes[i] || '---', prices[i] || '---', (fundamentals[i] || '').substring(0, 25), '']),
    [65, 58, 60, 210, 75], MARGIN, y, boldFont, font, C.darkBlue);

  // 二、AI评分
  y -= 8;
  y = drawHeading1(page, '\u4E8C\u3001\u4E94\u8DEFAI\u72EC\u7ACB\u8BC4\u5206\uFF081-10\u5206\uFF09', y, boldFont, font);
  y = drawHeading2(page, '\u7F3A\u9677\u6743\u91CD\uFF1A\u57FA\u672C\u976210%\uFF08\u8D22\u52A1\u589E\u901F\uFF09\u4E49\u8D8B\u52BF20%\uFF08\u8D44\u91D1\u52A8\u80FD\uFF09\u4E49\u8D8B\u52BF20%\uFF08\u60C5\u7EEA\u70B9\u7B49\uFF09', y, boldFont, font);
  y -= 5;
  const colW = 60, nameW = 72;
  const totalW = nameW + stocks.length * colW;
  const hdrH2 = 22, rowH2 = 18;

  drawRect(page, MARGIN, y - hdrH2, totalW, hdrH2, C.darkBlue);
  drawText(page, 'AI', MARGIN + 3, y - hdrH2 + 7, boldFont, 9, C.white);
  let tx2 = MARGIN + nameW;
  for (let si = 0; si < stocks.length; si++) {
    drawRect(page, tx2, y - hdrH2, colW, hdrH2, C.mediumBlue);
    for (let ci = 0; ci < stocks[si].length; ci++) {
      drawText(page, stocks[si][ci] || '', tx2 + colW/2 - 4, y - hdrH2 + 14 - ci * 8.5, boldFont, 8, C.white);
    }
    tx2 += colW;
  }
  for (let ai = 0; ai < aiNames.length; ai++) {
    const ry = y - hdrH2 - (ai + 1) * rowH2;
    const bg = ai % 2 === 0 ? C.white : C.lightGray;
    drawRect(page, MARGIN, ry, nameW, rowH2, C.lightBlue);
    drawText(page, aiNames[ai], MARGIN + 3, ry + 5, boldFont, 8.5, C.darkBlue);
    tx2 = MARGIN + nameW;
    for (let si = 0; si < stocks.length; si++) {
      drawRect(page, tx2, ry, colW, rowH2, bg);
      const sc = aiScores[ai] ? aiScores[ai][si] : 5;
      const scColor = sc >= 8 ? C.green : sc >= 6 ? C.darkBlue : sc >= 4 ? C.black : C.red;
      drawText(page, sc + '\u5206', tx2 + colW/2 - 10, ry + 5, font, 9, scColor);
      tx2 += colW;
    }
  }
  page.drawRectangle({ x: MARGIN, y: y - hdrH2 - aiNames.length * rowH2,
    width: totalW, height: hdrH2 + aiNames.length * rowH2, borderColor: C.darkBlue, borderWidth: 0.5 });
  y = y - hdrH2 - aiNames.length * rowH2 - 15;

  // 三、三种方法排名
  y = drawHeading1(page, '\u4E09\u3001\u4E09\u79CD\u65B9\u6CD5\u7EFC\u5408\u6392\u540D', y, boldFont, font);
  y = drawTable(page, ['\u65B9\u6CD5', '\u7EFC\u5408\u6392\u540D\u7ED3\u679C'], [
    ['\u65B9\u6CD5\u4E00\uFF08\u5747\u5206\u6CD5\uFF09', m1Result.join(' > ')],
    ['\u65B9\u6CD5\u4E8C\uFF08\u79EF\u5206\u6CD5\uFF09', m2Result.join(' > ')],
    ['\u65B9\u6CD5\u4E09\uFF08\u6295\u7968\u6CD5\uFF09', m3Result.join(' > ')],
  ], [90, CONTENT_W - 90], MARGIN, y, boldFont, font, C.mediumBlue);
  y -= 12;

  // 四、综合排名结论
  y = drawHeading1(page, '\u56DB\u3001\u7EFC\u5408\u6392\u540D\u7ED3\u8BBA', y, boldFont, font);
  y = drawRanking(page, finalRank, y, boldFont, font);
  y -= 10;

  // 五、各维度冠军
  y = drawHeading1(page, '\u4E94\u3001\u5404\u7EF4\u5EA6\u51A0\u519B', y, boldFont, font);
  y = drawTable(page, ['\u7EF4\u5EA6', '\u6700\u4F18\u80A1\u7968', '\u6570\u636E'],
    champion, [80, 110, CONTENT_W - 190], MARGIN, y, boldFont, font, C.darkBlue);
  y -= 10;

  // 六、风险提示
  y = drawHeading1(page, '\u516D\u3001\u98CE\u9669\u63D0\u793A', y, boldFont, font);
  y = drawWarningBox(page, riskLines, y, boldFont, font);

  const bytes = await doc.save();
  require('fs').writeFileSync(outPath, bytes);
  console.log('PDF saved:', outPath, '(' + bytes.length + ' bytes)');
  return outPath;
}

// ==================== 测试运行 ====================

const DATA = {
  title: '5AI\u8D85\u77ED\u7EBF\u9009\u80A1\u5206\u6790\u62A5\u544A',
  date: '\u62A5\u544A\u65E5\u671F\uFF1A2026\u5E744\u670827\u65E5',
  subtitle: '\u5C71\u901A\u65B0\u6750 | \u534E\u9633\u56FD\u9645 | \u9752\u677E\u80A1\u4EFD | \u683C\u6797\u7F8E | \u767E\u5927\u96C6\u56E2 | \u9F99\u5174\u79D1\u6280',
  stocks: ['\u5C71\u901A\u65B0\u6750', '\u534E\u9633\u56FD\u9645', '\u9752\u677E\u80A1\u4EFD', '\u683C\u6797\u7F8E', '\u767E\u5927\u96C6\u56E2', '\u9F99\u5174\u79D1\u6280'],
  codes:  ['300930', '002949', '300132', '002340', '600865', '002442'],
  prices: ['\u7EA632\u5143', '\u7EA614.10\u5143', '\u7EA68.70\u5143', '\u7EA68.43\u5143', '\u7EA611.45\u5143', '\u7EA65.70\u5143'],
  fundamentals: [
    'Q1\u8425\u65362.53\u4EBF(+62%)\uFF0C\u51C0\u52291560\u4E07(+33%)',
    '2025\u5E74\u62A5\u8425\u653612.03\u4EBF\uFF0C\u51C0\u52299059\u4E07(-27.7%)',
    '\u6A2A\u76D8\u6574\u7406\uFF0C\u6570\u636E\u5F85\u5E74\u62A5\u786E\u8BA4',
    '2025\u5E74\u62A5\u8425\u6536371\u4EBF(+11.8%)\uFF0C\u51C0\u522915.8\u4EBF(+54.9%)',
    '\u672C\u5468\u6DA8\u8D8550%\uFF0C2024\u5E74\u8425\u653611.3\u4EBF',
    'TTM\u8425\u653644.7\u4EBF\uFF0C\u80A1\u4EF7\u4ECE6.62\u5143\u56DE\u843D\u81F35.7\u5143',
  ],
  aiNames: ['DeepSeek', 'Kimi', '\u8C46\u5305AI', '\u5343\u95EE', 'MiniMax'],
  aiScores: [
    [7, 4, 5, 9, 8, 6],
    [8, 4, 4, 9, 7, 7],
    [6, 3, 4, 8, 9, 5],
    [7, 5, 4, 8, 8, 6],
    [7, 4, 5, 8, 7, 5],
  ],
  m1Result: ['\u683C\u6797\u7F8E', '\u767E\u5927\u96C6\u56E2', '\u5C71\u901A\u65B0\u6750', '\u9F99\u5174\u79D1\u6280', '\u9752\u677E\u80A1\u4EFD', '\u534E\u9633\u56FD\u9645'],
  m2Result: ['\u683C\u6797\u7F8E', '\u767E\u5927\u96C6\u56E2', '\u5C71\u901A\u65B0\u6750', '\u9F99\u5174\u79D1\u6280', '\u9752\u677E\u80A1\u4EFD', '\u534E\u9633\u56FD\u9645'],
  m3Result: ['\u683C\u6797\u7F8E(5\u7968)', '\u767E\u5927\u96C6\u56E2(3\u7968)', '\u5C71\u901A\u65B0\u6750(2\u7968)', '\u9752\u677E\u80A1\u4EFD(0\u7968)', '\u534E\u9633\u56FD\u9645(0\u7968)', '\u9F99\u5174\u79D1\u6280(0\u7968)'],
  finalRank: [
    ['\u683C\u6797\u7F8E',    3,  8.40, 5, '\u5F3A\u70C8\u63A8\u8350', C.green],
    ['\u767E\u5927\u96C6\u56E2', 6,  7.80, 3, '\u503C\u5F97\u5173\u6CE8', C.mediumBlue],
    ['\u5C71\u901A\u65B0\u6750',  9,  7.00, 2, '\u8C28\u614E\u5173\u6CE8', C.gold],
    ['\u9F99\u5174\u79D1\u6280', 14,  5.80, 0, '\u4E00\u822C',     C.gray],
    ['\u9752\u677E\u80A1\u4EFD', 15,  4.40, 0, '\u56DE\u907F',     C.red],
    ['\u534E\u9633\u56FD\u9645', 16,  4.00, 0, '\u56DE\u907F',     C.red],
  ],
  champion: [
    ['\u51C0\u5229\u6DA8\u901F\u589E\u738B', '\u683C\u6797\u7F8E', '2025\u5E74\u51C0\u5229\u6DA8+54.87%\uFF0C\u89C4\u6A215.8\u4EBF'],
    ['\u4F4E\u4F30\u738B',       '\u767E\u5927\u96C6\u56E2', 'PE\u7EA621\uFF0C\u672C\u5468\u6DA850%+\uFF0C\u5F3A\u52BF\u52A8\u80FD'],
    ['\u6210\u957F\u6027\u738B',   '\u5C71\u901A\u65B0\u6750', 'Q1\u8425\u6536+62.52%\uFF0C\u8D85\u9AD8\u901F\u589E\u957F'],
    ['\u884C\u4E1A\u5730\u4F4D\u738B', '\u683C\u6797\u7F8E', '\u52A8\u529B\u7535\u6C60\u56DE\u6536\u9F99\u5934\uFF0C\u5168\u7403\u5E03\u5C40'],
    ['\u6280\u672F\u9762\u5F3A\u52BF', '\u767E\u5927\u96C6\u56E2', '\u672C\u5468\u6DA8\u5E45\u8D8550%+\uFF0C\u4E3B\u529B\u8D44\u91D1\u5173\u6CE8'],
    ['\u4F4E\u4EF7\u6F5C\u529B\u80A1', '\u9F99\u5174\u79D1\u6280', '\u80A1\u4EF75.7\u5143\uFF0CPE\u4EC520\uFF0C\u4F4E\u4EF7\u4F4D'],
  ],
  riskLines: [
    '\u672C\u62A5\u544A\u4EC5\u4F9B\u7814\u7A76\u53C2\u8003\uFF0C\u4E0D\u6784\u6210\u6295\u8D44\u5EFA\u8BAE\u3002',
    '\u8D85\u77ED\u7EBF\u6301\u4ED34\u5929\u5185\uFF0C\u6700\u5927\u6B69\u635550%\uFF0C\u6700\u5927\u6B69\u635510%\u3002',
    '\u534E\u9633\u56FD\u9645\uFF1A\u51C0\u5229\u6DA8\u540C\u6BD4-27.7%\uFF0C\u57FA\u672C\u9762\u8F83\u5F31\uFF0C\u56DE\u907F\u8D85\u77ED\u7EBF\u3002',
    '\u5C71\u901A\u65B0\u6750\uFF1APE\u9AD8\u8FBE59\u500D\uFF0C\u4F30\u503C\u8F83\u8D35\uFF0C\u987F\u8B66\u56DE\u8C03\u98CE\u9669\u3002',
    '\u767E\u5927\u96C6\u56E2\uFF1A\u672C\u5468\u6DA8\u8D8550%\u4E3A\u5F02\u52A8\uFF0C\u5FC5\u987B\u4E25\u683C\u6B69\u6355\uFF084%\u5185\uFF09\u3002',
    '\u9752\u677E\u80A1\u4EFD\uFF1A\u6570\u636E\u6709\u9650\uFF0C\u5E74\u62A5\u5C1A\u672A\u5B8C\u6574\u83B7\u53D6\uFF0C\u5206\u6790\u7F6E\u4FE1\u5EA6\u8F83\u4F4E\u3002',
    '\u683C\u6797\u7F8E\uFF1A\u77ED\u671F\u6DA8\u5E45\u5DF2\u5927\uFF0C\u6CE8\u610F\u83B7\u5229\u56DE\u5413\u98CE\u9669\u3002',
    '\u5E02\u573A\u6709\u98CE\u9669\uFF0C\u6295\u8D44\u9700\u8C28\u614E\uFF0C\u8BF7\u4EE5\u5B9E\u76D8\u4E3A\u51C6\u3002',
  ],
};

generateReport(DATA, '/workspace/\u80A1\u7968\u5206\u6790/5AI\u8D85\u77ED\u7EBF\u9009\u80A1\u5206\u6790\u62A5\u544A_20260427.pdf')
  .then(() => console.log('Done!'))
  .catch(e => { console.error(e); process.exit(1); });

// 同步测试
async function testDoc() {
  const doc = await PDFDocument.create();
  console.log('doc created ok, type:', typeof doc, Object.keys(doc).slice(0,5).join(','));
}
testDoc().catch(console.error);
