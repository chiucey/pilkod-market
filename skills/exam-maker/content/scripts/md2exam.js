/**
 * md2exam.js — Markdown 试卷 → Word 转换器
 *
 * 输出两份独立文件（均用英文文件名，避免 Unicode 导致 CDN 下载失败）：
 *   exam-questions.docx  — 学生用试卷（不含答案）
 *   exam-answers.docx    — 教师用答案册
 *
 * 用法：
 *   node md2exam.js <输入.md>
 *   node md2exam.js <输入.md> --name <输出名前缀>
 */

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, PageOrientation,
  ShadingType, TableLayoutType, VerticalAlign,
} = require('docx');

// ════════════════════════════════════════════════════════════
// 工具函数
// ════════════════════════════════════════════════════════════

function bold(text, opts = {}) {
  return new TextRun({ text, bold: true, font: '宋体', size: 21, ...opts });
}
function normal(text, opts = {}) {
  return new TextRun({ text, font: '宋体', size: 21, ...opts });
}
function italic(text, color = '7B2D8B') {
  return new TextRun({ text, italics: true, color, font: '楷体', size: 18 });
}
function gray(text) {
  return new TextRun({ text, font: '宋体', size: 21, color: '888888' });
}
function para(children, opts = {}) {
  return new Paragraph({ children, spacing: { before: 60, after: 60 }, ...opts });
}
function divider() {
  return new Paragraph({
    children: [],
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'DDDDDD' } },
    spacing: { before: 160, after: 160 },
  });
}
function emptyLine(spacing = 80) {
  return new Paragraph({ children: [new TextRun('')], spacing: { before: spacing, after: spacing } });
}

// ════════════════════════════════════════════════════════════
// 信息答题纸表格
// ════════════════════════════════════════════════════════════

function infoTable(meta) {
  function cell(text, isHead = false) {
    return new TableCell({
      children: [new Paragraph({
        children: [new TextRun({ text, font: '宋体', size: 20, bold: isHead })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 60, after: 60 },
      })],
      verticalAlign: VerticalAlign.CENTER,
      shading: isHead ? { fill: 'F0F0F0', type: ShadingType.CLEAR } : undefined,
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
    });
  }
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 12, color: '333333' },
      bottom: { style: BorderStyle.SINGLE, size: 12, color: '333333' },
      left:   { style: BorderStyle.SINGLE, size: 12, color: '333333' },
      right:  { style: BorderStyle.SINGLE, size: 12, color: '333333' },
      insideH:{ style: BorderStyle.SINGLE, size: 6,  color: '333333' },
      insideV:{ style: BorderStyle.SINGLE, size: 6,  color: '333333' },
    },
    rows: [
      new TableRow({ children: [
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: `\u2605 【${meta.subject || '考试'}】考生答题信息栏（考生必填）\u2605`, font: '宋体', size: 22, bold: true })], alignment: AlignmentType.CENTER })],
          columnSpan: 4,
          shading: { fill: 'F0F0F0', type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 80, right: 80 },
        }),
      ]}),
      new TableRow({ children: [
        cell('班级：_______________'),
        cell('姓名：_______________'),
        cell('学号：_______________'),
        cell('得分：_______________'),
      ]}),
    ],
  });
}

// ════════════════════════════════════════════════════════════
// 试卷标题段落
// ════════════════════════════════════════════════════════════

function examTitle(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, font: '黑体', size: 36, color: '111111' })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 160 },
  });
}
function examMetaLine(meta) {
  return new Paragraph({
    children: [new TextRun({ text: `满分：${meta.total || 150}分  \u2502  时间：${meta.time || 120}分钟  \u2502  科目：${meta.subject || ''}  \u2502  年级：${meta.grade || ''}  \u2502  ${meta.book ? '\u6559\u6750：' + meta.book : ''}`, font: '宋体', size: 20, color: '555555' })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 200 },
  });
}
function sectionTitle(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, font: '黑体', size: 28, color: '1A60C0' })],
    spacing: { before: 280, after: 120 },
  });
}
function sealLine() {
  return new Paragraph({
    children: [new TextRun({ text: '\u5c01\u95ed\u7ebf \u2014 \u8bf7\u52ff\u5728\u5c01\u95ed\u533a\u57df\u5185\u4f5c\u7b54 \u2014', font: '宋体', size: 18, color: 'BBBBBB' })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 280, after: 0 },
  });
}

// ════════════════════════════════════════════════════════════
// Markdown 解析
// ════════════════════════════════════════════════════════════

function parseMd(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  const meta = { title: '\u672a\u547d\u540d\u8bd5\u5377', subject: '', grade: '\u9ad8\u4e8c', total: 150, time: 120, book: '' };
  const body = [];
  let i = 0;

  // YAML 头
  if (lines[0].trim() === '---') {
    let j = 1;
    while (j < lines.length && lines[j].trim() !== '---') {
      const m = lines[j].match(/-\s*([^：:]+)[:：]\s*(.+)/);
      if (m) {
        const k = m[1].trim(), v = m[2].trim();
        if (k === '\u79d1\u76ee') meta.subject = v;
        if (k === '\u5e74\u7ea7') meta.grade = v;
        if (k === '\u6ee1\u5206') meta.total = parseInt(v) || 150;
        if (k === '\u65f6\u95f4') meta.time = parseInt(v) || 120;
        if (k === '\u6559\u6750\u7248\u672c' || k === '\u7248\u672c') meta.book = v;
      }
      j++;
    }
    i = j + 1;
  }
  // # 标题行
  while (i < lines.length) {
    const m = lines[i].match(/^#\s+(.+)/);
    if (m) { meta.title = m[1].trim(); i++; break; }
    i++;
  }
  if (i < lines.length && !lines[i].startsWith('##') && !lines[i].startsWith('#')) i--;
  while (i < lines.length) body.push(lines[i++]);
  return { meta, body };
}

// ════════════════════════════════════════════════════════════
// 核心：构建题目列表（不含答案）和答案列表
// ════════════════════════════════════════════════════════════

function buildBlocks(body) {
  const blocks = [];       // { type, num, score, lines[], answer? }
  let currentSection = '';
  let qNum = 0;
  let i = 0;

  function stripAnswer(line) {
    // 去掉 **答案：xxx** / **答案：xxx** / **答案：xxx**
    return line
      .replace(/\*\*答案[：:]\s*\s*\*\*/g, '')
      .replace(/\*\*答案[：:]\s*/g, '')
      .replace(/^答案[：:]\s*/, '');
  }

  while (i < body.length) {
    let line = body[i];

    // 题型标题
    const secMatch = line.match(/^#{1,2}\s+(.+)/);
    if (secMatch) {
      currentSection = secMatch[1].trim();
      blocks.push({ type: 'section', text: currentSection });
      i++; continue;
    }

    // 分割线
    if (line.trim() === '---') { i++; continue; }

    // 空行
    if (!line.trim()) { i++; continue; }

    // 检测答案行（积累到当前题目的 answer）
    let answerText = null;
    if (line.includes('**答案') || (line.trim().startsWith('**') && line.includes('\u7b54\u6848'))) {
      answerText = line.replace(/\*\*/g, '').replace(/\u7b54\u6848[：:]\s*/, '').trim();
      // 看看这行是否只是纯答案（很短），否则把答案抽出来
      const hasOnlyAnswer = /^\(?[A-Z][\u0020-\u007E\u4e00-\u9fa5]*\)?$/.test(answerText) || /^[A-Z]{1,4}$/.test(answerText) || /^\u2713$|^\u2717$|^\u2713\u3001/.test(answerText) || /^[\u4e00-\u9fa5\uff08\uff09\u3000-\u303f\u0020-\u007E]+$/.test(answerText);
      if (hasOnlyAnswer && answerText.length < 30) {
        // 纯答案行，跳过（不加入题目）
        // 但先看看前一坨有没有被归到题目里
      }
    }

    // 题号行（选择题、填空题、解答题、多选、判断通用）
    const qMatch = line.match(/^(\d+)\.\s*（(\d+)\u5206）\s*(.*)/);
    if (qMatch) {
      qNum = parseInt(qMatch[1]);
      const score = parseInt(qMatch[2]);
      const rest = qMatch[3].trim();
      const qLines = [];
      if (rest) qLines.push(rest);
      // 收集后续内容直到下一个题号或答案行或题型标题
      let j = i + 1;
      let pendingAnswer = null;
      while (j < body.length) {
        const next = body[j];
        if (/^#{1,2}\s+/.test(next) || next.trim() === '---') break;
        const ansMatch = next.match(/^\s*\*\*答案[：:]\s*(.+)\*\*/);
        if (ansMatch) { pendingAnswer = ansMatch[1].trim(); j++; continue; }
        if (/^[A-D]\.\s/.test(next.trim())) { qLines.push(next.trim()); j++; continue; }
        if (!next.trim()) { j++; continue; }
        // 填空题或解答题含 ____
        if (next.includes('______') || next.includes('\u3000\u3000')) { qLines.push(next); j++; continue; }
        // 纯短答案行（如 ✓ ✗ 或 答案文字）
        if ((/^[\u2713\u2717]\s*/.test(next.trim()) || /^\u7b54\uff1a/.test(next.trim())) && next.trim().length < 20) {
          pendingAnswer = next.replace(/^\s*\u7b54[：:]\s*/, '').trim();
          j++; continue;
        }
        break;
      }
      blocks.push({ type: 'question', num: qNum, score, lines: qLines, answer: pendingAnswer, section: currentSection });
      i = j; continue;
    }

    // 选项行（A. B. C. D.）
    if (/^[A-D]\.\s/.test(line.trim())) {
      blocks.push({ type: 'option', text: line.trim() });
      i++; continue;
    }

    // 多选/判断题额外选项
    if (/^[A-D]\.\s/.test(line.trim()) || /^[\u2713\u2717]\s/.test(line.trim())) {
      blocks.push({ type: 'option', text: line.trim() });
      i++; continue;
    }

    // 填空下划线行（独立成行）
    if (line.includes('______') || line.includes('\u3000\u3000')) {
      blocks.push({ type: 'fill', text: line });
      i++; continue;
    }

    // 答案块（独立段落）
    if (line.trim().startsWith('**') && line.includes('\u7b54\u6848')) {
      const aText = line.replace(/\*\*/g, '').replace(/\u7b54\u6848[：:]\s*/, '').trim();
      blocks.push({ type: 'answer-only', text: aText });
      i++; continue;
    }

    i++;
  }
  return blocks;
}

// ════════════════════════════════════════════════════════════
// 生成试卷文档（不含答案）
// ════════════════════════════════════════════════════════════

function buildQuestionsDoc(meta, blocks) {
  const children = [];

  // 标题
  children.push(examTitle(meta.title));
  children.push(examMetaLine(meta));
  children.push(infoTable(meta));
  children.push(emptyLine(160));
  children.push(divider());

  let inSection = false;

  for (const blk of blocks) {
    if (blk.type === 'section') {
      children.push(emptyLine(160));
      children.push(sectionTitle(blk.text));
      children.push(divider());
      inSection = true;
      continue;
    }

    if (blk.type === 'answer-only') continue; // 跳过纯答案行

    if (blk.type === 'fill') {
      // 填空题题干行
      children.push(para([bold(blk.num + '. '), normal(blk.text, { size: 21 })], { indent: { left: 0 }, spacing: { before: 80, after: 40 } }));
      // 空格留给学生写
      children.push(para([normal('\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000', { color: 'CCCCCC' })]));
      continue;
    }

    if (blk.type === 'option') {
      // 选项缩进
      children.push(para([normal('    ' + blk.text, { size: 21 })], { indent: { left: 360 }, spacing: { before: 20, after: 20 } }));
      continue;
    }

    if (blk.type === 'question') {
      // 题号+分值+题干
      const runs = [bold(blk.num + '. '), new TextRun({ text: `\uff08${blk.score}\u5206\uff09`, font: '宋体', size: 20, color: 'C0392B' })];
      if (blk.lines.length > 0) {
        runs.push(normal(blk.lines.join(' '), { size: 21 }));
      }
      children.push(para(runs, { indent: { left: 0 }, spacing: { before: 100, after: 40 } }));
      // 选择题的选项在下一个 option block 里，跟在题目后面
      continue;
    }
  }

  children.push(emptyLine(200));
  children.push(sealLine());

  return new Document({
    sections: [{
      properties: {
        page: {
          size: { orientation: PageOrientation.PORTRAIT, width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
        },
      },
      children,
    }],
  });
}

// ════════════════════════════════════════════════════════════
// 生成答案文档（含完整参考答案）
// ════════════════════════════════════════════════════════════

function buildAnswersDoc(meta, blocks) {
  const children = [];

  // 标题
  children.push(new Paragraph({
    children: [new TextRun({ text: meta.title + ' \u7b54\u6848\u518c\uff08\u6559\u5e08\u7528\uff09', bold: true, font: '\u9ed1\u4f53', size: 32, color: '111111' })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 160 },
  }));
  children.push(new Paragraph({
    children: [new TextRun({ text: `\u6ce8\u610f\uff1a\u6b64\u6587\u4ef6\u4ec5\u6559\u5e08\u8054\u5408\u8bdd\u9898\u5b57\u8bc6\u5220\uff0c\u52ff\u5206\u53d1\u7ed9\u5b66\u751f\u3002\u6240\u6709\u9898\u76ee\u5747\u6709\u5b8c\u6574\u53c2\u8003\u7b54\u6848\u3002`, font: '\u5b8b\u4f53', size: 18, color: '888888', italics: true })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 200 },
  }));
  children.push(infoTable(meta));
  children.push(emptyLine(160));
  children.push(divider());

  let qNum = 0;

  for (const blk of blocks) {
    if (blk.type === 'section') {
      children.push(emptyLine(160));
      children.push(new Paragraph({
        children: [new TextRun({ text: blk.text, bold: true, font: '\u9ed1\u4f53', size: 28, color: '1A60C0' })],
        spacing: { before: 280, after: 120 },
      }));
      children.push(divider());
      continue;
    }

    if (blk.type === 'option') {
      children.push(para([normal('    ' + blk.text, { size: 21, color: '666666' })], { indent: { left: 360 }, spacing: { before: 20, after: 20 } }));
      continue;
    }

    if (blk.type === 'fill') {
      // 填空题干 + 答案
      children.push(para([bold(blk.num + '. '), normal(blk.text.replace(/______+/g, '______'), { size: 21, color: '333333' })]));
      if (blk.answer) {
        children.push(para([italic('\u7b54\uff1a' + blk.answer)]));
      } else {
        children.push(para([italic('\u7b54\uff1a' + '(参考答案)')]));
      }
      children.push(emptyLine(60));
      continue;
    }

    if (blk.type === 'question') {
      qNum = blk.num;
      // 题号+分值+题干
      const runs = [bold(blk.num + '. '), new TextRun({ text: `\uff08${blk.score}\u5206\uff09`, font: '\u5b8b\u4f53', size: 20, color: 'C0392B' })];
      if (blk.lines.length > 0) runs.push(normal(blk.lines.join(' '), { size: 21 }));
      children.push(para(runs, { indent: { left: 0 }, spacing: { before: 100, after: 40 } }));
      // 答案
      if (blk.answer) {
        children.push(para([italic('\u7b54\uff1a' + blk.answer)]));
      } else {
        children.push(para([italic('\u7b54\uff1a' + '(\u8be5\u9898\u6682\u65e0\u7b54\u6848)')]));
      }
      children.push(emptyLine(60));
      continue;
    }

    if (blk.type === 'answer-only') {
      children.push(para([italic(blk.text)]));
      continue;
    }
  }

  children.push(emptyLine(200));
  children.push(sealLine());

  return new Document({
    sections: [{
      properties: {
        page: {
          size: { orientation: PageOrientation.PORTRAIT, width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
        },
      },
      children,
    }],
  });
}

// ════════════════════════════════════════════════════════════
// 主入口
// ════════════════════════════════════════════════════════════

function main() {
  const mdFile = process.argv[2];
  if (!mdFile) {
    console.error('\u7528\u6cd5: node md2exam.js <input.md> [--name <output-prefix>]');
    console.error('\u4f8b: node md2exam.js exam.md --name math-midterm');
    process.exit(1);
  }

  const nameArg = process.argv.indexOf('--name');
  const prefix = nameArg !== -1 && process.argv[nameArg + 1]
    ? process.argv[nameArg + 1].replace(/\s+/g, '-')
    : 'exam';

  // 用英文文件名输出，避免 Unicode CDN 问题
  const outQuestions = path.join(path.dirname(mdFile), 'exam-questions.docx');
  const outAnswers    = path.join(path.dirname(mdFile), 'exam-answers.docx');

  const { meta, body } = parseMd(mdFile);
  const blocks = buildBlocks(body);

  console.log(`\u5373\u5c06\u751f\u6210\u4e24\u4efd docx...`);
  console.log(`  \u8bd5\u5377: ${outQuestions}`);
  console.log(`  \u7b54\u6848: ${outAnswers}`);

  // 并行生成两份文档
  Promise.all([
    Packer.toBuffer(buildQuestionsDoc(meta, blocks)),
    Packer.toBuffer(buildAnswersDoc(meta, blocks)),
  ]).then(([qBuf, aBuf]) => {
    fs.writeFileSync(outQuestions, qBuf);
    fs.writeFileSync(outAnswers, aBuf);
    console.log(`\u2705 \u8bd5\u5377\u5df2\u751f\u6210: ${outQuestions}`);
    console.log(`\u2705 \u7b54\u6848\u5df2\u751f\u6210: ${outAnswers}`);
  }).catch(err => {
    console.error('\u751f\u6210\u5931\u8d25:', err.message);
    process.exit(1);
  });
}

main();
