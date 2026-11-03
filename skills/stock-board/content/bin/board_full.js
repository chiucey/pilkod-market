#!/usr/bin/env node
const https = require('https');

function fetchStockList(type = 'zt') {
  return new Promise((resolve, reject) => {
    let url;
    switch (type) {
      case 'strong':
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=200&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f12,f13,f14';
        break;
      default:
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=300&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f12,f13,f14';
    }
    const req = https.get(url, {
      headers: {
        'Referer': 'https://finance.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const json = JSON.parse(data);
        const stocks = (json.data?.diff || []).map(item => ({
          code: item.f12, name: item.f14, price: item.f2, change: item.f4, percent: item.f3
        })).filter(s => s.price > 0 && s.percent >= (type === 'strong' ? 7 : 9.9));
        resolve(stocks);
      });
    });
    req.on('error', reject);
    setTimeout(() => reject(new Error('timeout')), 15000);
  });
}

async function main() {
  const type = process.argv[2] || 'zt';
  const stocks = await fetchStockList(type);
  const title = type === 'strong' ? '🔥 强势股 (≥7%)' : '📈 涨停板全部';
  console.log(`${title} - 共 ${stocks.length} 只`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  stocks.forEach((s, i) => {
    console.log(`${String(i+1).padStart(3)}. ${s.name.padEnd(8)} ${s.code}  ${s.price}  +${s.percent}%`);
  });
}

main().catch(e => console.error(e.message));
