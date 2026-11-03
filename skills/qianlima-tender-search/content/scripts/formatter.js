/**
 * 格式化金额
 */
function formatAmount(number, unit) {
  if (!number) return '-';
  unit = unit || '元';

  if (unit === '元') {
    if (number >= 10000) {
      return `${(number / 10000).toFixed(2)}万${unit}`;
    }
    return `${number.toLocaleString()}${unit}`;
  }
  return `${number}${unit}`;
}

/**
 * 类型映射表
 * noticeSegmentType -> { name, category }
 * category: bidding=招标, won=中标, change=变更
 */
const TYPE_MAP = {
  2:  { name: '招标预告', category: 'bidding' },
  3:  { name: '招标公告', category: 'bidding' },
  5:  { name: '信息变更', category: 'change' },
  10: { name: '候选人公示', category: 'won' },
  11: { name: '中标结果', category: 'won' },
  12: { name: '合同公告', category: 'won' },
  // 其他常见类型
  1:  { name: '预告', category: 'bidding' },
  4:  { name: '变更', category: 'change' },
  6:  { name: '废标公告', category: 'change' },
  7:  { name: '资格预审', category: 'bidding' },
  8:  { name: '询价公告', category: 'bidding' },
  9:  { name: '竞争性谈判', category: 'bidding' },
  13: { name: '单一来源', category: 'bidding' },
  14: { name: '补充公告', category: 'change' }
};

/**
 * 获取类型信息
 */
function getTypeInfo(noticeSegmentType, noticeSegmentTypeName, progName) {
  const info = TYPE_MAP[noticeSegmentType];
  if (info) {
    return info;
  }
  // 未知类型，根据progName判断
  if (progName === '结果') {
    return { name: noticeSegmentTypeName || '中标结果', category: 'won' };
  } else if (progName === '公告' || progName === '预告') {
    return { name: noticeSegmentTypeName || progName, category: 'bidding' };
  }
  return { name: noticeSegmentTypeName || progName || '-', category: 'bidding' };
}

/**
 * 格式化招标类型（兼容旧接口）
 */
function formatType(noticeSegmentType, noticeSegmentTypeName, progName) {
  return getTypeInfo(noticeSegmentType, noticeSegmentTypeName, progName).name;
}

/**
 * 解析用户输入为搜索参数
 */
function parseQuery(userInput) {
  const params = {
    keyword: '',
    newAreas: '',
    timeType: '',
    beginAmount: '',
    endAmount: '',
    biddingType: ''
  };

  // 解析地区（支持多个，用逗号分隔）
  const areaMap = {
    '北京': '0', '天津': '1', '河北': '2', '山西': '3', '内蒙古': '4',
    '辽宁': '5', '吉林': '6', '黑龙江': '7', '上海': '8', '江苏': '9',
    '浙江': '10', '安徽': '11', '福建': '12', '江西': '13', '山东': '14',
    '河南': '15', '湖北': '16', '湖南': '17', '广东': '18', '广西': '19',
    '海南': '20', '重庆': '31', '四川': '21', '贵州': '22', '云南': '23',
    '西藏': '24', '陕西': '25', '甘肃': '26', '青海': '27', '宁夏': '28',
    '新疆': '29', '台湾': '30',
    '全国': ''
  };

  // 解析金额（注意顺序：范围匹配要优先于单个匹配）
  const amountPatterns = [
    { pattern: /(\d+)万以上/, type: 'min', key: 'beginAmount' },
    { pattern: /(\d+)万以下/, type: 'max', key: 'endAmount' },
    { pattern: /(\d+)万[-到](\d+)万/, type: 'range', key1: 'beginAmount', key2: 'endAmount' },
    { pattern: /(\d+)-(\d+)万/, type: 'range', key1: 'beginAmount', key2: 'endAmount' },
    { pattern: /(\d+)万/, type: 'single', key: 'beginAmount' }
  ];

  // 解析时间（按长度降序排列，优先匹配更长的词）
  const timeMap = {
    '近三个月': '4', '三个月': '4',
    '近一个月': '3', '近一月': '3', '一个月': '3', '近30天': '3',
    '近半年': '5', '半年': '5',
    '近一年': '6', '一年': '6',
    '近一周': '2', '一周': '2',
    '近7天': '2', '七天': '2',
    '近3天': '1', '三天': '1'
  };

  let input = userInput;

  // 提取金额
  for (const p of amountPatterns) {
    const match = input.match(p.pattern);
    if (match) {
      if (p.type === 'range') {
        params[p.key1] = parseInt(match[1]) * 10000;
        params[p.key2] = parseInt(match[2]) * 10000;
      } else if (p.type === 'min') {
        params[p.key] = parseInt(match[1]) * 10000;
      } else if (p.type === 'max') {
        params[p.key] = parseInt(match[1]) * 10000;
      } else if (p.type === 'single') {
        params.beginAmount = parseInt(match[1]) * 10000;
        params.endAmount = parseInt(match[1]) * 10000;
      }
      input = input.replace(match[0], '');
    }
  }

  // 提取地区
  for (const [name, code] of Object.entries(areaMap)) {
    if (input.includes(name)) {
      if (code) params.newAreas = code;  // 只取第一个地区
      input = input.replace(name, '');
    }
  }

  // 提取时间
  for (const [name, code] of Object.entries(timeMap)) {
    if (input.includes(name)) {
      params.timeType = code;
      input = input.replace(name, '');
      break;
    }
  }

  // 剩余部分作为关键词
  const remaining = input.replace(/[,\s]+/g, ' ').trim();
  params.keyword = remaining;

  // 默认时间
  if (!params.timeType) {
    params.timeType = '7'; // 近一个月
  }

  return params;
}

/**
 * 智能汇总结果
 */
function summarizeResults(items) {
  const stats = {
    total: items.length,
    bidding: 0,      // 招标相关
    won: 0,          // 中标相关
    change: 0,       // 变更
    totalAmount: 0,
    hasAmount: 0,
    areas: {},
    types: {}        // 详细类型统计
  };

  // 按详细类型分组
  const biddingList = [];  // 招标公告、预告等
  const wonList = [];      // 中标结果、候选人公示、合同公告
  const changeList = [];   // 变更、澄清等

  for (const item of items) {
    const typeInfo = getTypeInfo(item.noticeSegmentType, item.noticeSegmentTypeName, item.progName);

    // 统计
    if (typeInfo.category === 'won') {
      stats.won++;
      const amount = item.bidderAmountNumber || item.tenderAmountNumber;
      if (amount) {
        stats.totalAmount += amount;
        stats.hasAmount++;
      }
      wonList.push(item);
    } else if (typeInfo.category === 'change') {
      stats.change++;
      changeList.push(item);
    } else {
      stats.bidding++;
      const amount = item.tenderAmountNumber;
      if (amount) {
        stats.totalAmount += amount;
        stats.hasAmount++;
      }
      biddingList.push(item);
    }

    // 地区统计
    const area = item.areaName || '-';
    stats.areas[area] = (stats.areas[area] || 0) + 1;

    // 类型统计
    stats.types[typeInfo.name] = (stats.types[typeInfo.name] || 0) + 1;
  }

  return {
    stats,
    biddingList,
    wonList,
    changeList
  };
}

/**
 * 格式化单条结果
 */
function formatItem(item, index) {
  const typeInfo = getTypeInfo(item.noticeSegmentType, item.noticeSegmentTypeName, item.progName);
  const amount = item.bidderAmountNumber || item.tenderAmountNumber;
  const amountStr = formatAmount(amount, item.bidderAmountUnit || item.tenderAmountUnit);

  return {
    index: index + 1,
    title: item.showTitle || item.popTitle || '-',
    type: typeInfo.name,
    category: typeInfo.category,
    area: item.areaName || '-',
    amount: amountStr,
    amountRaw: amount,
    date: item.updateTime || '-',
    url: item.url || '-',
    bidder: item.bidder || '-',
    tenderees: item.tenderees || '-'
  };
}

/**
 * 生成Markdown格式的报告
 */
function formatReport(data, query) {
  const { rowCount, data: items } = data;
  const { stats, biddingList, wonList, changeList } = summarizeResults(items);

  let md = `# 招标中标查询结果\n\n`;
  md += `**查询条件**: ${query}\n\n`;
  md += `**搜索结果**: 共 ${rowCount} 条，当前展示 ${items.length} 条\n\n`;

  // 统计摘要
  md += `## 统计摘要\n\n`;
  md += `- **招标公告/预告**: ${stats.bidding} 条\n`;
  md += `- **中标候选人/结果**: ${stats.won} 条\n`;
  if (stats.change > 0) {
    md += `- **变更/澄清**: ${stats.change} 条\n`;
  }
  if (stats.hasAmount > 0) {
    md += `- **平均金额**: ${formatAmount(Math.round(stats.totalAmount / stats.hasAmount), '元')}\n`;
  }

  // 详细类型分布
  const typeEntries = Object.entries(stats.types).sort((a, b) => b[1] - a[1]);
  if (typeEntries.length > 0) {
    md += `\n**类型分布**: ${typeEntries.map(([k, v]) => `${k}(${v}条)`).join('、')}\n`;
  }

  // 地区分布
  const topAreas = Object.entries(stats.areas)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  if (topAreas.length > 0) {
    md += `**热门地区**: ${topAreas.map(([k, v]) => `${k}(${v}条)`).join('、')}\n`;
  }

  md += `\n---\n\n`;

  // 中标候选人信息
  if (wonList.length > 0) {
    md += `## 中标候选人/结果 (${wonList.length}条)\n\n`;
    md += `| 序号 | 类型 | 项目名称 | 中标单位 | 金额 | 地区 | 日期 |\n`;
    md += `| --- | --- | --- | --- | --- | --- | --- |\n`;

    for (let i = 0; i < Math.min(wonList.length, 10); i++) {
      const item = wonList[i];
      const formatted = formatItem(item, i);
      md += `| ${formatted.index} | ${formatted.type} | [${formatted.title}](${formatted.url}) | ${formatted.bidder} | ${formatted.amount} | ${formatted.area} | ${formatted.date} |\n`;
    }
    if (wonList.length > 10) {
      md += `\n*仅展示前10条，完整结果请访问千里马平台*\n`;
    }
    md += `\n`;
  }

  // 招标公告信息
  if (biddingList.length > 0) {
    md += `## 招标公告/预告 (${biddingList.length}条)\n\n`;
    md += `| 序号 | 类型 | 项目名称 | 采购单位 | 金额 | 地区 | 日期 |\n`;
    md += `| --- | --- | --- | --- | --- | --- | --- |\n`;

    for (let i = 0; i < Math.min(biddingList.length, 10); i++) {
      const item = biddingList[i];
      const formatted = formatItem(item, i);
      md += `| ${formatted.index} | ${formatted.type} | [${formatted.title}](${formatted.url}) | ${formatted.tenderees} | ${formatted.amount} | ${formatted.area} | ${formatted.date} |\n`;
    }
    if (biddingList.length > 10) {
      md += `\n*仅展示前10条，完整结果请访问千里马平台*\n`;
    }
    md += `\n`;
  }

  // 变更信息
  if (changeList.length > 0) {
    md += `## 变更/澄清信息 (${changeList.length}条)\n\n`;
    md += `| 序号 | 类型 | 项目名称 | 金额 | 地区 | 日期 |\n`;
    md += `| --- | --- | --- | --- | --- | --- |\n`;

    for (let i = 0; i < Math.min(changeList.length, 10); i++) {
      const item = changeList[i];
      const formatted = formatItem(item, i);
      md += `| ${formatted.index} | ${formatted.type} | [${formatted.title}](${formatted.url}) | ${formatted.amount} | ${formatted.area} | ${formatted.date} |\n`;
    }
    if (changeList.length > 10) {
      md += `\n*仅展示前10条，完整结果请访问千里马平台*\n`;
    }
  }

  return md;
}

module.exports = {
  formatAmount,
  formatType,
  getTypeInfo,
  parseQuery,
  summarizeResults,
  formatItem,
  formatReport,
  TYPE_MAP
};
