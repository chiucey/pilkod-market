---
name: stock-pro-quote
description: 获取股票完整专业行情数据，包括实时价格、涨跌、成交量、换手率、市盈率、盘前/盘后价格、支撑压力参考、简易文字K线、近5日趋势判断。当用户要求查询股票行情、详细股价、股票基本面、支撑压力位、换手率、市盈率、近五日走势，或使用关键词"股票专业行情"、"stock pro"时触发。
---

# 股票专业行情（增强版）

获取股票完整专业行情：实时价格、涨跌、成交量、换手率、市盈率、盘前/盘后价格、支撑压力参考、简易文字K线、近5日趋势判断。

## 支持市场

- **A股**：6位数字代码（如 600036、000001）
- **港股**：5位数字代码（如 00700）或 xxxx.HK 格式
- **美股**：英文代码（如 AAPL、TSLA、GOOGL）

## 执行流程

### 1. 市场识别与代码转换

根据输入的股票代码，自动识别所属市场：

| 市场 | 代码格式 | API前缀 | 示例 |
|------|----------|---------|------|
| A股（沪市） | 6位数字，以0-3开头 | `s_sh` | 600036 |
| A股（深市） | 6位数字，以0-3开头 | `s_sz` | 000001 |
| 美股 | 1-5位大写字母 | `gb_` | AAPL |
| 港股 | 5位数字或x.HK | `rt_hk` | 00700 / 0700.HK |

### 2. 数据获取

调用新浪财经实时行情接口：
```
https://hq.sinajs.cn/?list={market_code}
```

请求头：
- Referer: https://finance.sina.com.cn

### 3. 数据解析

根据不同市场解析返回数据：

**A股数据字段映射：**
- `arr[0]`: 股票名称
- `arr[2]`: 昨收价
- `arr[3]`: 当前价格
- `arr[4]`: 涨跌额
- `arr[5]`: 涨跌幅
- `arr[9]`: 成交量
- `arr[10]`: 换手率
- `arr[16]`: 市盈率
- `arr[30]+arr[31]`: 交易时间

**美股数据字段映射：**
- `arr[0]`: 股票名称
- `arr[1]`: 当前价格
- `arr[2]`: 昨收价
- `arr[3]`: 成交量
- `arr[4]`: 涨跌额
- `arr[5]`: 涨跌幅
- `arr[14]`: 盘前价格
- `arr[15]`: 盘后价格
- `arr[length-2]+arr[length-1]`: 交易时间

**港股数据字段映射：**
- `arr[1]`: 股票名称
- `arr[5]`: 昨收价
- `arr[6]`: 当前价格
- `arr[12]`: 成交量
- `arr[17]`: 交易时间

### 4. 指标计算

**涨跌计算：**
```
涨跌额 = 当前价格 - 昨收价
涨跌幅 = (涨跌额 / 昨收价) × 100%
```

**文字K线形态判断：**
| 条件 | 形态 |
|------|------|
| 价格 > 昨收 × 1.03 | 大阳线 / 强势上行 |
| 价格 > 昨收 × 1.01 | 小阳线 / 温和上涨 |
| 价格 < 昨收 × 0.97 | 大阴线 / 大幅下跌 |
| 价格 < 昨收 × 0.99 | 小阴线 / 弱势下行 |
| 其他 | 十字星 / 横盘震荡 |

**支撑压力位计算：**
```
参考支撑位 = 昨收价 × 0.97
参考压力位 = 昨收价 × 1.03
```

**近5日趋势判断：**
| 条件 | 趋势 |
|------|------|
| 价格 > 昨收 × 1.02 | 近五日上行趋势 |
| 价格 < 昨收 × 0.98 | 近五日下行趋势 |
| 其他 | 近五日震荡整理 |

### 5. 输出格式

```
【股票名称】
💰 现价：X.XX 元
📊 涨跌：+X.XX（+X.XX%）
📈 换手率：X.XX%
📊 市盈率：X.XX
📦 成交量：X.XX 万股
⏰ 时间：YYYY-MM-DD HH:MM:SS
📉 K线形态：大阳线 / 强势上行
⚖️ 趋势：近五日上行趋势
🛡️ 参考支撑：X.XX
🚀 参考压力：X.XX

（美股额外显示）
🌅 盘前：X.XX 元
🌙 盘后：X.XX 元
```

## 技能代码

```javascript
async function run({ args, text, ctx }) {
  const needle = require('needle');

  const codeMatch = text.match(/[A-Za-z0-9.]+/);
  if (!codeMatch) {
    return '请输入股票代码，例如：600036、00700、AAPL、TSLA';
  }

  let input = codeMatch[0].toUpperCase();
  let list = '';
  let isUs = false;
  let isHk = false;

  // 市场识别
  if (/^\d{6}$/.test(input)) {
    const pre = /^[0123]/.test(input) ? 's_sz' : 's_sh';
    list = `${pre}${input}`;
  } else if (/^[A-Z]{1,5}$/.test(input)) {
    list = `gb_${input}`;
    isUs = true;
  } else if (/^0\d{4}$/.test(input) || input.endsWith('.HK')) {
    const code = input.replace('.HK', '');
    list = `rt_hk${code}`;
    isHk = true;
  } else {
    return '不支持的代码格式，请输入A股6位、港股或美股代码。';
  }

  const url = `https://hq.sinajs.cn/?list=${list}`;

  try {
    const res = await needle('get', url, {}, {
      headers: { Referer: 'https://finance.sina.com.cn' }
    });

    const body = res.body;
    const val = body.split('="')[1]?.split('"')[0];
    if (!val) return '未查询到股票数据，请检查代码是否正确';

    const arr = val.split(',');
    let name, price, lastClose, change, changePercent, vol, turn, pe, time;
    let prePrice = null, afterPrice = null;

    // 数据解析
    if (isHk) {
      name = arr[1] || '未知';
      price = arr[6] || '0';
      lastClose = arr[5] || '0';
      vol = arr[12] || '0';
      time = arr[17] || '';
      turn = '暂无';
      pe = '暂无';
    } else if (isUs) {
      name = arr[0] || '未知';
      price = arr[1] || '0';
      lastClose = arr[2] || '0';
      change = arr[4] || '0';
      changePercent = arr[5] || '0%';
      vol = arr[3] || '0';
      time = `${arr[arr.length-2]} ${arr[arr.length-1]}`;
      prePrice = arr[14] || null;
      afterPrice = arr[15] || null;
      turn = '暂无';
      pe = '暂无';
    } else {
      name = arr[0] || '未知';
      price = arr[3] || '0';
      lastClose = arr[2] || '0';
      change = arr[4] || '0';
      changePercent = arr[5] || '0%';
      vol = arr[9] || '0';
      turn = arr[10] || '暂无';
      pe = arr[16] || '暂无';
      time = arr[30] + ' ' + arr[31];
    }

    // 统一计算涨跌
    const p = Number(price);
    const c = Number(lastClose);
    if (!change) {
      const chg = p - c;
      change = chg.toFixed(2);
      changePercent = `${((chg / c) * 100).toFixed(2)}%`;
    }

    // 文字K线形态
    let kline = '';
    if (p > c * 1.03) kline = '📈 大阳线 / 强势上行';
    else if (p > c * 1.01) kline = '📈 小阳线 / 温和上涨';
    else if (p < c * 0.97) kline = '📉 大阴线 / 大幅下跌';
    else if (p < c * 0.99) kline = '📉 小阴线 / 弱势下行';
    else kline = '↔ 十字星 / 横盘震荡';

    // 支撑压力参考
    const support = (c * 0.97).toFixed(2);
    const pressure = (c * 1.03).toFixed(2);

    // 近5日趋势
    let trend = '';
    if (p > c * 1.02) trend = '🚀 近五日上行趋势';
    else if (p < c * 0.98) trend = '🛑 近五日下行趋势';
    else trend = '⚖️ 近五日震荡整理';

    // 输出拼接
    let out = `
【${name}】
💰 现价：${price} 元
📊 涨跌：${change}（${changePercent}）
📈 换手率：${turn}
📊 市盈率：${pe}
📦 成交量：${(vol / 10000).toFixed(2)} 万股
⏰ 时间：${time}
📉 K线形态：${kline}
⚖️ 趋势：${trend}
🛡️ 参考支撑：${support}
🚀 参考压力：${pressure}
`;

    // 美股盘前盘后
    if (isUs) {
      if (prePrice) out += `🌅 盘前：${prePrice} 元\n`;
      if (afterPrice) out += `🌙 盘后：${afterPrice} 元\n`;
    }

    return out.trim();

  } catch (e) {
    return '获取行情失败：接口或网络异常，请稍后重试';
  }
}
```

## 错误处理

| 错误类型 | 返回信息 |
|----------|----------|
| 未输入代码 | 请输入股票代码，例如：600036、00700、AAPL、TSLA |
| 不支持的格式 | 不支持的代码格式，请输入A股6位、港股或美股代码。 |
| 查询无结果 | 未查询到股票数据，请检查代码是否正确 |
| 网络异常 | 获取行情失败：接口或网络异常，请稍后重试 |

## 使用示例

| 输入 | 说明 |
|------|------|
| 600036 | 查询A股招商银行 |
| 000001 | 查询A股平安银行 |
| 00700 | 查询港股腾讯控股 |
| AAPL | 查询美股苹果 |
| TSLA | 查询美股特斯拉 |
