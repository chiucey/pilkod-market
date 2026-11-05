/**
 * A股均线趋势量化分析
 *
 * 功能：
 * - 通过新浪财经API获取真实K线数据（含预计算均线）
 * - 计算真实MA5/MA10/MA20/MA60均线
 * - 趋势判断与操作策略建议
 */

const https = require('https');
const zlib = require('zlib');

/**
 * HTTP请求封装 - 增强版（支持gzip/br解压）
 * @param {string} url - 请求URL
 * @param {number} retries - 重试次数
 * @returns {Promise<string>} 响应内容
 */
async function httpGet(url, retries = 2) {
  const request = () => {
    return new Promise((resolve, reject) => {
      const request = https.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Referer': 'https://finance.sina.com.cn/',
          'Accept': 'text/javascript, application/javascript, */*; q=0.01',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Connection': 'keep-alive'
        },
        timeout: 15000
      }, (response) => {
        // 处理重定向
        if (response.statusCode === 301 || response.statusCode === 302) {
          if (response.headers.location) {
            httpGet(response.headers.location, retries).then(resolve).catch(reject);
            return;
          }
        }

        if (response.statusCode !== 200) {
          reject(new Error(`HTTP ${response.statusCode}`));
          return;
        }

        const encoding = response.headers['content-encoding'];
        let data = [];

        if (encoding === 'gzip') {
          const gunzip = zlib.createGunzip();
          response.pipe(gunzip);
          gunzip.on('data', chunk => data.push(chunk));
          gunzip.on('end', () => resolve(Buffer.concat(data).toString()));
          gunzip.on('error', reject);
        } else if (encoding === 'br') {
          const brotli = zlib.createBrotliDecompress();
          response.pipe(brotli);
          brotli.on('data', chunk => data.push(chunk));
          brotli.on('end', () => resolve(Buffer.concat(data).toString()));
          brotli.on('error', reject);
        } else {
          response.on('data', chunk => data.push(chunk));
          response.on('end', () => resolve(Buffer.concat(data).toString()));
        }
      });

      request.on('error', reject);
      request.on('timeout', () => {
        request.destroy();
        reject(new Error('Request timeout'));
      });
    });
  };

  try {
    return await request();
  } catch (err) {
    if (retries > 0) {
      await new Promise(r => setTimeout(r, 500));
      return httpGet(url, retries - 1);
    }
    throw err;
  }
}

/**
 * 解析股票代码
 * @param {string} userInput - 用户输入
 * @returns {{code: string, symbol: string}|null}
 */
function parseStockCode(userInput) {
  const codeMatch = userInput.match(/\d{6}/);
  if (!codeMatch) return null;

  const code = codeMatch[0];
  const prefix = /^[0123]/.test(code) ? 'sz' : 'sh';
  return { code, symbol: prefix + code };
}

/**
 * 获取实时行情数据（新浪）
 * @param {string} symbol - 股票代码
 * @returns {Promise<Object>}
 */
async function getRealtimeQuote(symbol) {
  const url = `https://hq.sinajs.cn/rn=${Date.now()}&list=${symbol}`;

  const response = await httpGet(url);
  const match = response.match(/="([^"]+)"/);
  if (!match) {
    throw new Error('行情数据解析失败');
  }

  const fields = match[1].split(',');
  if (fields.length < 32) {
    throw new Error('行情数据格式异常');
  }

  return {
    name: fields[0],
    code: symbol.slice(2),
    price: parseFloat(fields[3]),
    open: parseFloat(fields[1]),
    close: parseFloat(fields[2]),
    high: parseFloat(fields[4]),
    low: parseFloat(fields[5]),
    volume: parseInt(fields[8], 10),
    amount: parseFloat(fields[9]),
    date: fields[30],
    time: fields[31]
  };
}

/**
 * 获取历史K线数据（含预计算均线）
 * @param {string} symbol - 股票代码
 * @param {number} days - 获取天数
 * @returns {Promise<Object>}
 */
async function getKlineData(symbol, days = 70) {
  const url = `https://quotes.sina.cn/cn/api/jsonp_v2.php/var _${symbol}_kliness=/CN_MarketDataService.getKLineData?symbol=${symbol}&scale=240&datalen=${days}&_${Date.now()}`;

  const response = await httpGet(url);

  // 解析JSONP - 提取数组
  const jsonStart = response.indexOf('[');
  const jsonEnd = response.lastIndexOf(']');

  if (jsonStart === -1 || jsonEnd === -1) {
    throw new Error('K线数据解析失败：未找到数据');
  }

  const jsonStr = response.substring(jsonStart, jsonEnd + 1);

  try {
    var data = JSON.parse(jsonStr);
  } catch (e) {
    throw new Error('K线数据JSON解析失败');
  }

  if (!Array.isArray(data) || data.length === 0) {
    throw new Error('K线数据为空，请检查股票代码是否正确');
  }

  return {
    klines: data.map(item => ({
      date: item.day,
      open: parseFloat(item.open),
      high: parseFloat(item.high),
      low: parseFloat(item.low),
      close: parseFloat(item.close),
      volume: parseFloat(item.volume)
    })),
    precalculatedMA: {
      ma5: data.map(item => item.ma_price5),
      ma10: data.map(item => item.ma_price10),
      ma30: data.map(item => item.ma_price30)
    }
  };
}

/**
 * 计算简单移动平均线
 * @param {Array} klines - K线数据
 * @param {number} period - 周期
 * @returns {Array} 均值数组
 */
function calculateMA(klines, period) {
  const result = [];
  for (let i = 0; i < klines.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += klines[i - j].close;
      }
      result.push(sum / period);
    }
  }
  return result;
}

/**
 * 获取最新的均线值
 */
function getLatestMA(maArray) {
  if (!maArray || maArray.length === 0) return null;
  return maArray[maArray.length - 1];
}

/**
 * 计算MA20和MA60
 */
function calculateExtraMA(klines) {
  const ma20Array = calculateMA(klines, 20);
  const ma60Array = calculateMA(klines, 60);
  return {
    ma20: ma20Array[ma20Array.length - 1],
    ma60: ma60Array.length > 0 ? ma60Array[ma60Array.length - 1] : null
  };
}

/**
 * 判断趋势
 */
function analyzeTrend(quote, ma) {
  const { price } = quote;
  const { ma5, ma10, ma20, ma60 } = ma;

  const hasAllMA = ma5 !== null && ma10 !== null && ma20 !== null && ma60 !== null;

  let trend = { code: 'UNKNOWN', text: '', strength: '', direction: '' };

  if (!hasAllMA) {
    trend.code = 'DATA_INSUFFICIENT';
    trend.text = '数据不足，无法判断趋势';
    trend.strength = '需至少60个交易日数据';
    trend.direction = 'neutral';
    return trend;
  }

  const bullishArrangement = price > ma5 && ma5 > ma10 && ma10 > ma20 && ma20 > ma60;
  const mediumBullish = price > ma5 && ma5 > ma10 && ma10 > ma20;
  const shortTermBullish = price > ma5 && ma5 > ma10;

  const bearishArrangement = price < ma5 && ma5 < ma10 && ma10 < ma20 && ma20 < ma60;
  const mediumBearish = price < ma5 && ma5 < ma10 && ma10 < ma20;
  const shortTermBearish = price < ma5 && ma5 < ma10;

  if (bullishArrangement) {
    trend = { code: 'STRONG_BULL', text: '强势多头排列（上升趋势）', strength: '中长期上升趋势，趋势强劲', direction: 'bullish' };
  } else if (mediumBullish) {
    trend = { code: 'MEDIUM_BULL', text: '中期多头（短线强势）', strength: '中短期上升，但需关注长期均线支撑', direction: 'bullish' };
  } else if (shortTermBullish) {
    trend = { code: 'SHORT_BULL', text: '短期反弹', strength: '短线走强，但中期趋势仍需观察', direction: 'bullish' };
  } else if (bearishArrangement) {
    trend = { code: 'STRONG_BEAR', text: '完整空头排列（下降趋势）', strength: '中长期下降趋势，注意风险', direction: 'bearish' };
  } else if (mediumBearish) {
    trend = { code: 'MEDIUM_BEAR', text: '中期空头（短线弱势）', strength: '中短期下降，需等待企稳信号', direction: 'bearish' };
  } else if (shortTermBearish) {
    trend = { code: 'SHORT_BEAR', text: '短期回调', strength: '短线走弱，可能震荡或继续调整', direction: 'bearish' };
  } else {
    const aboveMA = [price > ma5, price > ma10, price > ma20, price > ma60].filter(Boolean).length;
    const belowMA = [price < ma5, price < ma10, price < ma20, price < ma60].filter(Boolean).length;

    trend.code = 'CONSOLIDATION';
    trend.direction = 'neutral';

    if (aboveMA > belowMA) {
      trend = { code: 'CONSOLIDATION', text: '震荡偏强', strength: '价格在均线间震荡，偏向上运行', direction: 'neutral' };
    } else if (belowMA > aboveMA) {
      trend = { code: 'CONSOLIDATION', text: '震荡偏弱', strength: '价格在均线间震荡，偏向下运行', direction: 'neutral' };
    } else {
      trend = { code: 'CONSOLIDATION', text: '震荡整理（无明确趋势）', strength: '多空博弈，等待方向选择', direction: 'neutral' };
    }
  }

  return trend;
}

/**
 * 生成操作策略
 */
function generateStrategy(trend, quote, ma) {
  let strategy = { mainAction: '', suggestions: [], riskLevel: '', notes: '' };

  switch (trend.code) {
    case 'STRONG_BULL':
      strategy = { mainAction: '持股待涨', suggestions: ['持有底仓，不轻易卖出', '回调至MA5附近可考虑加仓', '收盘跌破MA20考虑减仓'], riskLevel: '低', notes: '顺势而为，不逆势操作' };
      break;
    case 'MEDIUM_BULL':
      strategy = { mainAction: '逢低做多', suggestions: ['可在MA5支撑位附近介入', '止损设置在MA10下方', '关注MA20能否有效突破'], riskLevel: '中低', notes: '短线操作为主，注意止损' };
      break;
    case 'SHORT_BULL':
      strategy = { mainAction: '谨慎追涨', suggestions: ['短线快进快出为主', '严格设置止损位', '突破MA20后再考虑加仓'], riskLevel: '中', notes: '趋势不明，不宜重仓' };
      break;
    case 'STRONG_BEAR':
      strategy = { mainAction: '减仓观望', suggestions: ['及时减仓或清仓', '不要盲目抄底', '等待企稳信号再入场'], riskLevel: '高', notes: '规避为主，控制风险' };
      break;
    case 'MEDIUM_BEAR':
      strategy = { mainAction: '逢高减仓', suggestions: ['趁反弹减仓', '不急于补仓', '等待缩量止跌信号'], riskLevel: '中高', notes: '控制仓位，谨慎操作' };
      break;
    case 'SHORT_BEAR':
      strategy = { mainAction: '观望等待', suggestions: ['保持轻仓或空仓', '等待趋势明朗', '不盲目补仓'], riskLevel: '中', notes: '耐心等待方向明确' };
      break;
    case 'CONSOLIDATION':
      strategy = { mainAction: '高抛低吸', suggestions: ['区间震荡操作策略', '压力位减仓，支撑位加仓', '设置好止盈止损'], riskLevel: '中', notes: '控制仓位，避免追涨杀跌' };
      break;
    default:
      strategy = { mainAction: '等待数据', suggestions: ['数据加载中或不足'], riskLevel: '未知', notes: '' };
  }

  return strategy;
}

/**
 * 格式化数字显示
 */
function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || isNaN(value)) return '--';
  return value.toFixed(decimals);
}

/**
 * 主执行函数
 */
async function execute({ userInput, userInfo }) {
  try {
    const stockInfo = parseStockCode(userInput);
    if (!stockInfo) {
      return '请输入6位A股股票代码，例如：600036 趋势判断 或 000001 均线分析';
    }

    const { code, symbol } = stockInfo;

    const [quote, klineResult] = await Promise.all([
      getRealtimeQuote(symbol),
      getKlineData(symbol, 70)
    ]);

    const { klines, precalculatedMA } = klineResult;
    const extraMA = calculateExtraMA(klines);

    const ma = {
      ma5: getLatestMA(precalculatedMA.ma5),
      ma10: getLatestMA(precalculatedMA.ma10),
      ma20: extraMA.ma20,
      ma60: extraMA.ma60
    };

    const trend = analyzeTrend(quote, ma);
    const strategy = generateStrategy(trend, quote, ma);

    const priceChange = quote.price - quote.close;
    const priceChangePercent = quote.close > 0 ? (priceChange / quote.close * 100) : 0;
    const changeSymbol = priceChange >= 0 ? '+' : '';
    const trendIcon = trend.direction === 'bullish' ? '📈' : (trend.direction === 'bearish' ? '📉' : '↔');
    const marketName = symbol.startsWith('sh') ? '沪市' : '深市';

    return `
【${quote.name}｜${code}｜${marketName}】

┌─ 实时行情 ─────────────────────────
│ 现价：${formatNumber(quote.price)} 元
│ 涨跌：${changeSymbol}${formatNumber(priceChange)} (${changeSymbol}${priceChangePercent.toFixed(2)}%)
│ 今开：${formatNumber(quote.open)}　昨收：${formatNumber(quote.close)}
│ 最高：${formatNumber(quote.high)}　最低：${formatNumber(quote.low)}
│ 成交：${(quote.volume / 10000).toFixed(2)}万手
└────────────────────────────────────

┌─ 均线系统（数据更新：${klines[klines.length - 1].date}）────────
│ MA5：${formatNumber(ma.ma5)}　MA10：${formatNumber(ma.ma10)}
│ MA20：${formatNumber(ma.ma20)}　MA60：${formatNumber(ma.ma60)}
└────────────────────────────────────

┌─ 趋势研判 ${trendIcon} ─────────────────────────
│ ${trend.text}
│ ${trend.strength}
└────────────────────────────────────

┌─ 操作建议 ─────────────────────────
│ 策略：${strategy.mainAction}
│ 风险等级：${strategy.riskLevel}
│
│ ${strategy.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n│ ')}
│
│ 💡 ${strategy.notes}
└────────────────────────────────────

──────────────────────────────
⚠️ 免责声明：本内容仅供技术分析参考，不构成任何投资建议。
股市有风险，投资需谨慎。
`;

  } catch (error) {
    console.error('Stock analysis error:', error);
    return `分析失败：${error.message}`;
  }
}

module.exports = { execute };
