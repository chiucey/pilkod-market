/**
 * keyword-counter.js
 * 统计文章关键词词频，返回 Top N 高频词。
 * 纯本地确定性计算，无需 LLM 介入。
 *
 * 用法: node keyword-counter.js <article-queue.json> [topN]
 *   topN 默认为 20
 */

const fs = require('fs');
const path = require('path');

// 停用词列表（法学文本常用但无分析价值的虚词/结构词）
const STOP_WORDS = new Set([
  '的', '了', '和', '与', '在', '为', '对', '以', '及', '或', '而', '等',
  '可以', '应当', '必须', '可以', '属于', '关于', '对于', '以及', '基于',
  '本文', '笔者', '本文认为', '首先', '其次', '最后', '综上所述',
  '第一', '第二', '第三', '第四', '第五',
  '其中', '此外', '因此', '但是', '然而', '如果', '则', '即', '则',
  '一个', '这种', '这样', '那种', '相关', '不同', '主要', '重要',
  '研究', '分析', '问题', '发展', '完善', '建议', '我国', '我国',
  '法律', '规定', '制度', '规定', '法律制度',
]);

function tokenize(text) {
  // 简单中文分词：按标点和空格切分，再按字符 n-gram 提取 2-4 字词
  const tokens = [];
  // 先做简单的 2-gram 和 3-gram 提取
  for (let i = 0; i < text.length - 1; i++) {
    const bigram = text.slice(i, i + 2);
    if (!STOP_WORDS.has(bigram)) tokens.push(bigram);
  }
  for (let i = 0; i < text.length - 2; i++) {
    const trigram = text.slice(i, i + 3);
    if (!STOP_WORDS.has(trigram)) tokens.push(trigram);
  }
  return tokens;
}

function countKeywords(articles, topN = 20) {
  const freq = {};
  for (const article of articles) {
    const text = `${article.title} ${article.summary} ${(article.keywords || []).join(' ')}`;
    const tokens = tokenize(text);
    for (const token of tokens) {
      // 过滤纯数字/英文单字符
      if (/^[a-zA-Z0-9]+$/.test(token)) continue;
      if (/^\d+$/.test(token)) continue;
      // 过滤过短或过长
      if (token.length < 2) continue;
      freq[token] = (freq[token] || 0) + 1;
    }
  }
  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN)
    .map(([word, count]) => ({ word, count }));
}

if (require.main === module) {
  const queuePath = process.argv[2];
  const topN = parseInt(process.argv[3] || '20', 10);

  if (!queuePath) {
    console.error('用法: node keyword-counter.js <article-queue.json> [topN]');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
  const topKeywords = countKeywords(data.articles || [], topN);
  console.log(JSON.stringify(topKeywords, null, 2));
}
