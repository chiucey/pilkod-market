#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jack Stock Pick - 杨永兴隔夜套利法八步筛选脚本
支持多数据源：AKShare / 新浪财经 / Tushare

核心逻辑：
1. 尾盘2:30后筛选，规避日内风险
2. 八步筛选，环环相扣
3. 次日早盘必须清仓，除非缩量/一字涨停
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# ==================== 数据源配置 ====================
# 可选: "akshare"(推荐,免费), "sina"(稳定,无需安装), "tushare"(需Token)
# 如果 AKShare 连接失败，请改为 "sina"
DATA_SOURCE = "sina"

# Tushare Token（如果选择 tushare，需要从 https://tushare.pro/register 注册获取）
TUSHARE_TOKEN = ""
# ===================================================

# 设置标准输出编码为UTF-8，确保Windows控制台正常显示中文和emoji
if sys.stdout.encoding != 'UTF-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def is_main_board(ts_code):
    """判断是否主板股票（60开头-上海，00开头-深圳）"""
    code = str(ts_code).split('.')[0]
    # 上海主板：60xxxx
    if code.startswith('60'):
        return True
    # 深圳主板：00xxxx
    if code.startswith('00'):
        return True
    return False


def get_last_trade_date(target_date=None):
    """
    获取最近一个交易日的日期
    如果target_date是交易日则返回当天，否则向前查找最近交易日
    """
    if target_date is None:
        target_date = datetime.now()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y%m%d")
    
    # 尝试获取交易日历（仅AKShare可用时使用）
    if DATA_SOURCE == "akshare":
        try:
            import akshare as ak
            trade_cal = ak.tool_trade_date_hist_sina()
            if 'trade_date' in trade_cal.columns:
                trade_dates = set(pd.to_datetime(trade_cal['trade_date']).dt.strftime('%Y%m%d').tolist())
            else:
                trade_dates = set()
            
            # 向前查找最多30天
            for i in range(30):
                check_date = target_date - timedelta(days=i)
                date_str = check_date.strftime("%Y%m%d")
                if date_str in trade_dates:
                    return date_str
        except Exception as e:
            pass  # 静默失败，使用fallback
    
    # fallback: 跳过周末
    weekday = target_date.weekday()
    if weekday == 5:  # 周六
        fallback_date = target_date - timedelta(days=1)
    elif weekday == 6:  # 周日
        fallback_date = target_date - timedelta(days=2)
    else:
        fallback_date = target_date
    
    return fallback_date.strftime("%Y%m%d")


def fetch_daily_data_akshare():
    """使用AKShare获取当日A股行情数据"""
    import akshare as ak
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            df = ak.stock_zh_a_spot_em()
            
            df = df.rename(columns={
                '代码': 'ts_code',
                '名称': 'name',
                '最新价': 'close',
                '涨跌幅': 'pct_chg',
                '成交量': 'vol',
                '成交额': 'amount',
                '换手率': 'turnover_rate',
                '量比': 'volume_ratio',
                '总市值': 'total_mv',
                '流通市值': 'circ_mv',
                '所属行业': 'industry'
            })
            
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['pct_chg'] = pd.to_numeric(df['pct_chg'], errors='coerce')
            df['turnover_rate'] = pd.to_numeric(df['turnover_rate'], errors='coerce')
            df['volume_ratio'] = pd.to_numeric(df['volume_ratio'], errors='coerce')
            df['total_mv'] = pd.to_numeric(df['total_mv'], errors='coerce') / 10000
            df['circ_mv'] = pd.to_numeric(df['circ_mv'], errors='coerce') / 10000
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   AKShare获取失败，第{attempt + 1}次重试...")
                import time
                time.sleep(2)
            else:
                raise e


def fetch_daily_data_sina():
    """使用新浪财经接口获取当日A股行情数据"""
    import requests
    
    # 新浪财经API获取所有A股实时行情
    url = "http://hq.sinajs.cn/list=hs_a"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://finance.sina.com.cn'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'gb2312'
    
    # 解析返回数据
    data_list = []
    lines = response.text.strip().split(';')
    
    for line in lines:
        if not line.strip() or 'var hq_str_' not in line:
            continue
        
        try:
            # 提取股票代码和数据
            code_part = line.split('=')[0].replace('var hq_str_', '')
            data_part = line.split('=')[1].strip().strip('"')
            
            if not data_part:
                continue
            
            fields = data_part.split(',')
            if len(fields) < 30:
                continue
            
            # 新浪财经数据格式：
            # 0:名称, 1:今日开盘价, 2:昨日收盘价, 3:当前价, 4:今日最高价, 5:今日最低价
            # 6:竞买价, 7:竞卖价, 8:成交股数, 9:成交金额, 10:买一量, 11:买一价...
            
            name = fields[0]
            open_price = float(fields[1])
            pre_close = float(fields[2])
            close = float(fields[3])
            high = float(fields[4])
            low = float(fields[5])
            volume = float(fields[8])
            amount = float(fields[9])
            
            # 计算涨跌幅
            pct_chg = ((close - pre_close) / pre_close * 100) if pre_close > 0 else 0
            
            # 确定交易所
            if code_part.startswith('sh'):
                ts_code = code_part.replace('sh', '') + '.SH'
            elif code_part.startswith('sz'):
                ts_code = code_part.replace('sz', '') + '.SZ'
            else:
                continue
            
            data_list.append({
                'ts_code': ts_code,
                'name': name,
                'close': close,
                'pct_chg': pct_chg,
                'vol': volume,
                'amount': amount,
                'turnover_rate': None,  # 新浪接口不提供
                'volume_ratio': None,   # 新浪接口不提供
                'total_mv': None,       # 新浪接口不提供
                'circ_mv': None,
                'industry': None
            })
        except Exception as e:
            continue
    
    df = pd.DataFrame(data_list)
    
    # 新浪接口缺少部分字段，打印提示
    if len(df) > 0:
        print("   提示：新浪接口不提供换手率/量比/市值数据，这些条件将被跳过")
    
    return df


def fetch_daily_data_tushare():
    """使用Tushare获取当日A股行情数据"""
    import tushare as ts
    
    if not TUSHARE_TOKEN:
        raise ValueError("请先在脚本中设置 TUSHARE_TOKEN")
    
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    # 获取当日所有股票行情
    trade_date = datetime.now().strftime('%Y%m%d')
    df = pro.daily(trade_date=trade_date)
    
    # 获取每日指标（换手、量比、市值）
    df_basic = pro.daily_basic(trade_date=trade_date)
    
    # 合并数据
    df = pd.merge(df, df_basic[['ts_code', 'turnover_rate', 'volume_ratio', 'total_mv', 'circ_mv']], 
                  on='ts_code', how='left')
    
    # 获取股票基本信息
    df_stock = pro.stock_basic(exchange='', list_status='L')
    df_stock = df_stock[['ts_code', 'name', 'industry']]
    
    df = pd.merge(df, df_stock, on='ts_code', how='left')
    
    return df


def fetch_daily_data(trade_date):
    """
    获取当日A股行情数据，根据配置选择数据源
    """
    try:
        if DATA_SOURCE == "akshare":
            print("   使用数据源: AKShare (东方财富)")
            return fetch_daily_data_akshare()
        elif DATA_SOURCE == "sina":
            print("   使用数据源: 新浪财经")
            return fetch_daily_data_sina()
        elif DATA_SOURCE == "tushare":
            print("   使用数据源: Tushare")
            return fetch_daily_data_tushare()
        else:
            print(f"   错误：未知的数据源 {DATA_SOURCE}")
            return None
    except Exception as e:
        print(f"   获取数据失败: {e}")
        if DATA_SOURCE == "akshare":
            print("   提示：AKShare连接失败，可尝试修改 DATA_SOURCE = 'sina' 使用新浪财经接口")
        elif DATA_SOURCE == "tushare":
            print("   提示：请确保已设置正确的 TUSHARE_TOKEN")
        return None


def fetch_limit_stocks_akshare(start_date, end_date):
    """使用AKShare获取涨停股票列表"""
    import akshare as ak
    
    limit_stocks = set()
    
    try:
        trade_cal = ak.tool_trade_date_hist_sina()
        trade_dates = pd.to_datetime(trade_cal['trade_date']).dt.strftime('%Y%m%d').tolist()
        
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")
        
        valid_dates = []
        for date_str in trade_dates:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            if start_dt <= date_obj <= end_dt:
                valid_dates.append(date_str)
        
        for date_str in valid_dates:
            try:
                df_zt = ak.stock_zt_pool_em(date=date_str)
                if df_zt is not None and len(df_zt) > 0:
                    codes = df_zt['代码'].tolist()
                    limit_stocks.update(codes)
            except Exception as e:
                continue
        
        return limit_stocks
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return set()


def fetch_limit_stocks_tushare(start_date, end_date):
    """使用Tushare获取涨停股票列表"""
    import tushare as ts
    
    if not TUSHARE_TOKEN:
        raise ValueError("请先在脚本中设置 TUSHARE_TOKEN")
    
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    limit_stocks = set()
    
    # 获取交易日历
    trade_cal = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date, is_open='1')
    trade_dates = trade_cal['cal_date'].tolist()
    
    for date_str in trade_dates:
        try:
            df_zt = pro.limit_list(trade_date=date_str, limit_type='U')
            if df_zt is not None and len(df_zt) > 0:
                codes = df_zt['ts_code'].str.split('.').str[0].tolist()
                limit_stocks.update(codes)
        except Exception as e:
            continue
    
    return limit_stocks


def fetch_limit_stocks(start_date, end_date):
    """
    获取指定日期范围内的涨停股票列表
    根据配置选择数据源
    """
    try:
        if DATA_SOURCE == "akshare":
            return fetch_limit_stocks_akshare(start_date, end_date)
        elif DATA_SOURCE == "tushare":
            return fetch_limit_stocks_tushare(start_date, end_date)
        elif DATA_SOURCE == "sina":
            # 新浪接口不提供历史涨停数据，跳过此条件
            print("   提示：新浪接口不提供历史涨停数据，跳过该筛选条件")
            return None  # 返回None表示跳过此条件
        else:
            return set()
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return set()


def check_screening_time():
    """检查筛选时间，建议在14:30后执行"""
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    
    if current_hour < 14 or (current_hour == 14 and current_minute < 30):
        print("注意：当前时间早于14:30，建议尾盘时段（14:30后）执行筛选")
        print("   早盘波动大，量化资金搅局，尾盘才是黄金窗口")
    else:
        print("时间窗口合适，尾盘筛选已开启")


def run_eight_step_filter(trade_date=None):
    """执行八步筛选法"""
    if trade_date is None:
        trade_date = datetime.now().strftime("%Y%m%d")
    
    # 初始化筛选步骤结果列表
    step_results = []
    
    print("=" * 70)
    print("Jack Stock Pick - 杨永兴隔夜套利法八步筛选")
    print(f"筛选日期：{trade_date}")
    print(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 检查筛选时间
    check_screening_time()
    
    # 第一步：获取日线数据（包含涨幅、换手、量比、市值等）
    print("\n[1/3] 获取A股实时行情数据...")
    df_daily = fetch_daily_data(trade_date)
    
    if df_daily is None or len(df_daily) == 0:
        print("获取日线数据失败")
        return None, step_results
    
    print(f"   共获取 {len(df_daily)} 条数据")
    
    # 第二步：获取近20个交易日涨停股票
    print("\n[2/3] 获取近20个交易日涨停股票...")
    
    end_date = datetime.strptime(trade_date, "%Y%m%d")
    # 涨停筛选不应包含今天
    end_date_limit = end_date - timedelta(days=1)
    start_date = end_date - timedelta(days=30)  # 预留足够天数
    
    limit_stocks = fetch_limit_stocks(
        start_date.strftime("%Y%m%d"),
        end_date_limit.strftime("%Y%m%d")
    )
    
    if len(limit_stocks) > 0:
        print(f"   近期涨停股票数: {len(limit_stocks)} 只")
    else:
        # 涨停数据是核心筛选条件，失败时不应静默跳过
        print("   警告：未能获取近20日涨停数据！")
        print("   涨停筛选是判断股票活跃度的重要条件")
        print("   建议：稍后重试")
        print("   本次筛选将返回空结果，避免选出不符合条件的股票")
        return None, step_results
    
    # 第三步：执行八步筛选
    print("\n[3/3] 执行八步筛选...")
    
    df = df_daily.copy()
    print(f"   初始数据: {len(df)} 条")
    
    step_results.append(len(df))
    
    # 条件1：主板股票
    df = df[df['ts_code'].apply(is_main_board)]
    step_results.append(len(df))
    print(f"   主板股票: {len(df)} 只")
    
    # 条件2：涨幅3%~5%
    df = df[(df['pct_chg'] >= 3) & (df['pct_chg'] <= 5)]
    step_results.append(len(df))
    print(f"   涨幅3%-5%: {len(df)} 只")
    
    # 条件3：近20个交易日有涨停（如果数据可用）
    if limit_stocks is not None and len(limit_stocks) > 0:
        # 从ts_code中提取纯代码（去除.SZ/.SH后缀）进行匹配
        df['code_pure'] = df['ts_code'].str.split('.').str[0]
        df = df[df['code_pure'].isin(limit_stocks)]
        df = df.drop(columns=['code_pure'])  # 删除临时列
        step_results.append(len(df))
        print(f"   近期有涨停: {len(df)} 只")
    else:
        step_results.append(len(df))
        print(f"   近期有涨停: 跳过（数据源不支持）")
    
    # 条件4：量比 > 1（如果数据可用）
    if 'volume_ratio' in df.columns and df['volume_ratio'].notna().any():
        df = df[df['volume_ratio'] > 1]
        step_results.append(len(df))
        print(f"   量比>1: {len(df)} 只")
    else:
        step_results.append(len(df))
        print(f"   量比>1: 跳过（数据源不支持）")
    
    # 条件5：换手率5%~10%（如果数据可用）
    if 'turnover_rate' in df.columns and df['turnover_rate'].notna().any():
        df = df[(df['turnover_rate'] >= 5) & (df['turnover_rate'] <= 10)]
        step_results.append(len(df))
        print(f"   换手率5%-10%: {len(df)} 只")
    else:
        step_results.append(len(df))
        print(f"   换手率5%-10%: 跳过（数据源不支持）")
    
    # 条件6：市值50亿~200亿（如果数据可用）
    if 'total_mv' in df.columns and df['total_mv'].notna().any():
        # total_mv单位是万元，500000万元=50亿，2000000万元=200亿
        df = df[(df['total_mv'] >= 500000) & (df['total_mv'] <= 2000000)]
        step_results.append(len(df))
        print(f"   市值50-200亿: {len(df)} 只")
    else:
        step_results.append(len(df))
        print(f"   市值50-200亿: 跳过（数据源不支持）")
    
    # 整理结果
    if len(df) > 0:
        # 添加市值（亿元）字段
        if 'total_mv' in df.columns and df['total_mv'].notna().any():
            df['total_mv_yi'] = df['total_mv'] / 10000
        else:
            df['total_mv_yi'] = None
        
        # 成交额转为亿元
        if 'amount' in df.columns:
            df['成交额_亿元'] = df['amount'] / 100000000
        else:
            df['成交额_亿元'] = None
        
        return df, step_results
    
    return None, step_results


def format_output(df_result, step_results, trade_date):
    """格式化输出结果，生成完整筛选报告"""
    
    # 筛选步骤描述
    steps = [
        "初始数据",
        "主板股票",
        "涨幅3%-5%",
        "近期有涨停",
        "量比>1",
        "换手率5%-10%",
        "市值50-200亿"
    ]
    
    output = "=" * 70 + "\n"
    output += "JACK STOCK PICK 筛选报告\n"
    output += f"日期：{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}\n"
    output += "执行时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    output += "=" * 70 + "\n\n"
    
    # 筛选过程统计
    output += "八步筛选过程统计\n"
    output += "-" * 50 + "\n"
    
    for i, (step_name, count) in enumerate(zip(steps, step_results)):
        arrow = "->" if i < len(step_results)-1 else "OK"
        output += f"{arrow} {step_name}: {count} 只\n"
    
    output += "\n"
    
    # 结果展示
    if df_result is None or len(df_result) == 0:
        output += "今日无符合条件的股票\n\n"
        output += "操作建议：\n"
        output += "1. 严格执行筛选规则，宁可空仓不做错仓\n"
        output += "2. 超短线最忌讳为了买而买，空仓也是一种操作\n"
        output += "3. 等待下一次符合八步筛选的黄金机会\n"
        output += "4. 保持纪律，复利才是短线的王道\n"
    else:
        output += f"共筛选出 {len(df_result)} 只符合条件的股票：\n\n"
        
        # 股票详情表格
        output += "符合条件的股票清单\n"
        output += "-" * 90 + "\n"
        
        for idx, row in df_result.iterrows():
            output += f"{row['name']} ({row['ts_code']})\n"
            industry = row.get('industry', '未知')
            output += f"   行业：{industry}\n"
            output += f"   收盘：{row['close']:.2f}元 | 涨幅：{row['pct_chg']:.2f}%\n"
            output += f"   换手：{row['turnover_rate']:.2f}% | 量比：{row['volume_ratio']:.2f}\n"
            output += f"   市值：{row['total_mv_yi']:.2f}亿元\n\n"
        
        output += "尾盘操作建议：\n"
        output += "1. 观察分时走势，确保全天运行在分时均价线之上\n"
        output += "2. 选择走势最强、强于大盘甚至逆势的个股\n"
        output += "3. 等待创当天新高后回踩分时均线不破时进场\n"
        output += "4. 尾盘果断进场，规避日内波动风险\n\n"
    
    # 生死铁律提醒
    output += "生死铁律（刻进骨子里）\n"
    output += "-" * 50 + "\n"
    output += "次日早盘必须清仓，除非：\n"
    output += "   * 缩量涨停（成交量减少，但股价涨停）\n"
    output += "   * 一字涨停（开盘即涨停，全天封死）\n"
    output += "其余情况必须离场，哪怕：\n"
    output += "   * 赚七八个点\n"
    output += "   * 盈亏平衡\n"
    output += "   * 亏点手续费\n\n"
    
    output += "战法精髓：把A股的T+1做成T+0，只赚确定的惯性溢价，不赌未知的行情\n"
    output += "=" * 70
    
    return output


def save_results(df_result, trade_date):
    """保存筛选结果到CSV文件"""
    if df_result is None or len(df_result) == 0:
        return None
    
    try:
        # 从环境变量读取输出目录，默认使用当前目录下的results文件夹
        output_dir = os.environ.get('STOCK_PICK_OUTPUT_DIR', 
                                    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results'))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_file = os.path.join(output_dir, f"jack_stock_pick_{trade_date}.csv")
        
        # 保存关键字段
        save_cols = ['ts_code', 'name', 'industry', 'close', 'pct_chg', 
                    'turnover_rate', 'volume_ratio', 'total_mv_yi', '成交额_亿元']
        df_save = df_result[save_cols].copy()
        df_save.columns = ['股票代码', '股票名称', '行业', '收盘价', '涨幅%', 
                          '换手率%', '量比', '总市值(亿元)', '成交额(亿元)']
        
        df_save.to_csv(output_file, index=False, encoding='utf-8-sig')
        return output_file
    except Exception as e:
        print(f"保存结果失败: {e}")
        return None


def main():
    """主函数"""
    try:
        # 获取最近交易日（自动跳过周末/节假日）
        today = get_last_trade_date()
        print(f"自动定位到最近交易日: {today}\n")
        
        # 执行八步筛选
        result = run_eight_step_filter(today)
        
        # 检查返回结果
        if result is None or result[0] is None:
            print("\n筛选未能完成，请检查：")
            print("   1. 网络连接是否正常")
            print("   2. AKShare是否安装正确 (pip install akshare)")
            print("   3. 当前是否为交易日")
            return None
        
        df_result, step_results = result
        
        # 格式化输出
        output = format_output(df_result, step_results, today)
        print("\n" + output)
        
        # 保存结果
        if df_result is not None and len(df_result) > 0:
            saved_file = save_results(df_result, today)
            if saved_file:
                print(f"\n结果已保存至: {saved_file}")
        
        return output
        
    except Exception as e:
        print(f"程序执行异常: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
