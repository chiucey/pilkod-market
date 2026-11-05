#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股历史K线数据获取脚本
使用新浪财经API获取历史数据，计算涨跌幅
"""

import urllib.request
import json
import sys
import argparse
import ssl

# 忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

def get_sina_code(code):
    """转换股票代码为新浪格式"""
    if code.startswith('6'):
        return f"sh{code}"
    elif code.startswith('0') or code.startswith('3'):
        return f"sz{code}"
    return f"sz{code}"

def get_stock_history(code, days=30):
    """获取股票历史数据"""
    try:
        sina_code = get_sina_code(code)
        
        # 新浪财经K线接口
        # scale: 240=日线, 60=60分钟, 5=5分钟
        # datalen: 获取的数据条数
        url = f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_code}&scale=240&ma=5&datalen={days+10}'
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
            
            if not content or content == 'null':
                return None
            
            data = json.loads(content)
            
            if not data or len(data) < 2:
                return None
            
            # data是列表，最早的数据在前面，最新的在最后
            earliest = data[0]    # N天前
            latest = data[-1]     # 最新
            
            latest_close = float(latest['close'])
            earliest_close = float(earliest['close'])
            
            if earliest_close == 0:
                return None
            
            change_pct = ((latest_close - earliest_close) / earliest_close) * 100
            
            # 获取股票名称
            name_url = f'https://hq.sinajs.cn/list={sina_code}'
            name_req = urllib.request.Request(name_url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            name = code
            try:
                with urllib.request.urlopen(name_req, timeout=5) as name_resp:
                    name_content = name_resp.read().decode('gb2312', errors='ignore')
                    if '=' in name_content:
                        name = name_content.split('=')[1].split(',')[0].strip('"')
            except:
                pass
            
            return {
                'code': code,
                'name': name,
                'latest_price': latest_close,
                'earliest_price': earliest_close,
                'change_pct': change_pct,
                'latest_date': earliest['day'],
                'earliest_date': latest['day']
            }
            
    except Exception as e:
        print(f"Error for {code}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='获取A股股票历史涨跌幅')
    parser.add_argument('--codes', type=str, required=True, help='股票代码，用逗号分隔，如: 300757,300394,300308')
    parser.add_argument('--days', type=int, default=30, help='获取天数，默认30天')
    
    args = parser.parse_args()
    
    codes = [c.strip() for c in args.codes.split(',')]
    days = args.days
    
    print(f"\n{'='*70}")
    print(f"A股股票历史涨跌幅数据 ({days}个交易日)")
    print(f"{'='*70}\n")
    print(f"{'代码':<10} {'名称':<12} {'N日前价格':<14} {'当前价格':<14} {'涨跌幅':<12}")
    print("-" * 70)
    
    results = []
    
    for code in codes:
        data = get_stock_history(code, days)
        
        if data:
            change_str = f"{data['change_pct']:+.2f}%"
            print(f"{code:<10} {data['name']:<12} {data['earliest_price']:<14.2f} {data['latest_price']:<14.2f} {change_str:<12}")
            results.append(data)
        else:
            print(f"{code:<10} {'获取失败':<12}")
    
    print("-" * 70)
    print(f"\n数据来源: 新浪财经")
    
    # 按涨跌幅排序
    if results:
        results.sort(key=lambda x: x['change_pct'], reverse=True)
        print(f"\n涨跌幅排名 (从高到低):")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['name']} ({r['code']}): {r['change_pct']:+.2f}%")
    
    return results

if __name__ == '__main__':
    main()
