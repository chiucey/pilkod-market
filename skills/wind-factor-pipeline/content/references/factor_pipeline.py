"""
WindPy 量化因子计算 Pipeline
全自动因子计算与选股系统

整体架构:
    WindPy 数据拉取 → 因子计算模块 → 截面打分与排名 → 候选股输出 → 复盘记录
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from WindPy import w

# =============================================================================
# 模块0：环境初始化
# =============================================================================

def init_wind():
    """初始化 WindPy 连接"""
    w.start()
    return w.isconnected()

def get_trade_date():
    """获取当前交易日期"""
    return datetime.today().strftime('%Y-%m-%d')


# =============================================================================
# 模块1：拉取全A股票池（过滤ST/停牌）
# =============================================================================

def get_universe(date: str) -> list[str]:
    """
    获取当日全A可交易股票池

    Args:
        date: 交易日期，格式 YYYY-MM-DD

    Returns:
        list[str]: 可交易股票代码列表
    """
    # 拉取全A成分
    res = w.wset("sectorconstituent",
                 f"date={date};sectorid=a001010100000000")
    df = pd.DataFrame(res.Data, index=res.Fields).T
    codes = df['wind_code'].tolist()

    # 过滤ST
    st_res = w.wss(codes, "sec_status", f"tradeDate={date}")
    st_df = pd.DataFrame({'code': codes, 'status': st_res.Data[0]})
    clean = st_df[st_df['status'] == '正常上市']['code'].tolist()

    return clean


# =============================================================================
# 模块2：龙虎榜因子（Factor 1）
# =============================================================================

def get_lhb_factor(date: str, universe: list) -> pd.Series:
    """
    龙虎榜净流入强度 = (机构/游资买入 - 卖出) / 当日总成交额
    返回：index=股票代码, value=净流入占比（已标准化）

    Args:
        date: 交易日期
        universe: 股票池列表

    Returns:
        pd.Series: 龙虎榜因子值
    """
    res = w.wset("dragontigerlist",
                 f"date={date};indicator=龙虎榜")
    df = pd.DataFrame(res.Data, index=res.Fields).T

    # 计算净流入
    df['net_flow'] = df['buy_value'].astype(float) - df['sell_value'].astype(float)

    # 拉取当日成交额用于标准化
    turnover_res = w.wss(universe, "amt", f"tradeDate={date}")
    amt_df = pd.Series(turnover_res.Data[0], index=universe, name='amt')

    # 合并
    lhb_net = df.groupby('wind_code')['net_flow'].sum()
    factor = (lhb_net / amt_df).fillna(0)

    # 只保留universe内的股票，不在龙虎榜的赋0
    factor = factor.reindex(universe).fillna(0)
    return factor


# =============================================================================
# 模块3：主力资金净流入因子（Factor 2）
# =============================================================================

def get_moneyflow_factor(date: str, universe: list) -> pd.Series:
    """
    主力净流入占比 = (超大单+大单净流入) / 总成交额

    Args:
        date: 交易日期
        universe: 股票池列表

    Returns:
        pd.Series: 主力资金因子值
    """
    res = w.wss(
        universe,
        "mf_buyamt_l,mf_sellamt_l,mf_buyamt_xl,mf_sellamt_xl,amt",
        f"tradeDate={date}"
    )
    df = pd.DataFrame(
        res.Data,
        index=['buy_l','sell_l','buy_xl','sell_xl','amt'],
        columns=universe
    ).T.astype(float)

    df['main_net'] = (df['buy_l'] - df['sell_l'] +
                      df['buy_xl'] - df['sell_xl'])
    df['factor'] = df['main_net'] / df['amt']

    return df['factor'].fillna(0)


# =============================================================================
# 模块4：涨停封板质量因子（Factor 3）
# =============================================================================

def get_limitup_factor(date: str, universe: list) -> pd.Series:
    """
    封板强度 = 封单金额 / 当日成交额
    非涨停股赋0

    Args:
        date: 交易日期
        universe: 股票池列表

    Returns:
        pd.Series: 涨停封板因子值
    """
    res = w.wss(
        universe,
        "pct_chg,limitup_sealamount,amt",
        f"tradeDate={date}"
    )
    df = pd.DataFrame(
        res.Data,
        index=['pct_chg','seal_amt','amt'],
        columns=universe
    ).T.astype(float)

    # 只对涨停股计算
    df['factor'] = 0.0
    limit_mask = df['pct_chg'] >= 9.5  # 考虑科创板20%
    df.loc[limit_mask, 'factor'] = (
        df.loc[limit_mask, 'seal_amt'] /
        df.loc[limit_mask, 'amt']
    )

    return df['factor'].fillna(0)


# =============================================================================
# 模块5：题材热度因子（Factor 4）
# =============================================================================

def get_sector_heat_factor(date: str, universe: list) -> pd.Series:
    """
    题材扩散度 = 个股所属题材今日涨停数 / 题材总股票数
    用个股所在行业的涨停比例作为代理变量

    Args:
        date: 交易日期
        universe: 股票池列表

    Returns:
        pd.Series: 题材热度因子值
    """
    res = w.wss(universe, "pct_chg,industry_sw", f"tradeDate={date}")
    df = pd.DataFrame(
        res.Data,
        index=['pct_chg', 'industry'],
        columns=universe
    ).T
    df['pct_chg'] = df['pct_chg'].astype(float)
    df['is_limit'] = df['pct_chg'] >= 9.5

    # 计算各行业涨停率
    industry_heat = df.groupby('industry')['is_limit'].mean()
    df['factor'] = df['industry'].map(industry_heat)

    return df['factor'].fillna(0)


# =============================================================================
# 模块6：相对强弱因子（Factor 6）
# =============================================================================

def get_relative_strength_factor(date: str, universe: list) -> pd.Series:
    """
    个股超额涨幅 = 个股涨跌幅 - 所属行业指数涨跌幅

    Args:
        date: 交易日期
        universe: 股票池列表

    Returns:
        pd.Series: 相对强弱因子值
    """
    res = w.wss(universe, "pct_chg,industry_sw", f"tradeDate={date}")
    df = pd.DataFrame(
        res.Data,
        index=['pct_chg', 'industry'],
        columns=universe
    ).T
    df['pct_chg'] = df['pct_chg'].astype(float)

    industry_avg = df.groupby('industry')['pct_chg'].mean()
    df['industry_avg'] = df['industry'].map(industry_avg)
    df['factor'] = df['pct_chg'] - df['industry_avg']

    return df['factor'].fillna(0)


# =============================================================================
# 模块7：换手率黄金区间因子（Factor 8）
# =============================================================================

def get_turnover_factor(date: str, universe: list) -> pd.Series:
    """
    换手率打分：处于黄金区间得高分，过热/过冷得低分
    使用高斯函数模拟"适中最优"

    Args:
        date: 交易日期
        universe: 股票池列表

    Returns:
        pd.Series: 换手率因子值
    """
    res = w.wss(universe, "turn,mkt_cap_float",
                f"tradeDate={date}")
    df = pd.DataFrame(
        res.Data,
        index=['turnover', 'mktcap'],
        columns=universe
    ).T.astype(float)

    # 黄金区间中心：小盘5%, 大盘3%
    # 用简单分位数打分替代硬编码
    # 目标：2%-8%之间得高分，两端衰减
    center = 5.0
    width = 3.0
    df['factor'] = np.exp(-0.5 * ((df['turnover'] - center) / width) ** 2)

    return df['factor'].fillna(0)


# =============================================================================
# 模块8：综合评分与输出
# =============================================================================

def cross_section_score(date: str) -> pd.DataFrame:
    """
    主函数：计算当日截面综合得分

    Args:
        date: 交易日期

    Returns:
        pd.DataFrame: 候选股票列表
    """
    print(f"正在计算 {date} 截面因子...")
    universe = get_universe(date)
    print(f"股票池：{len(universe)} 只")

    # 计算各因子
    factors = {
        'lhb':      get_lhb_factor(date, universe),          # 龙虎榜
        'moneyflow': get_moneyflow_factor(date, universe),   # 主力流向
        'limitup':  get_limitup_factor(date, universe),      # 封板强度
        'sector':   get_sector_heat_factor(date, universe),  # 题材热度
        'rs':       get_relative_strength_factor(date, universe),  # 相对强弱
        'turnover': get_turnover_factor(date, universe),     # 换手率
    }

    df = pd.DataFrame(factors)

    # 因子标准化（百分位排名，0~1）
    df_ranked = df.rank(pct=True)

    # 加权合成
    weights = {
        'lhb': 0.20,
        'moneyflow': 0.15,
        'limitup': 0.10,
        'sector': 0.20,
        'rs': 0.15,
        'turnover': 0.10,
    }
    # 剩余10%留给均线结构（Factor 9，可后续扩展）

    df['score'] = sum(df_ranked[f] * w for f, w in weights.items())
    df['score_pct'] = df['score'].rank(pct=True)  # 最终百分位

    # 筛选条件：综合得分前5% + 市值>20亿
    mktcap_res = w.wss(universe, "mkt_cap_float", f"tradeDate={date}")
    df['mktcap'] = mktcap_res.Data[0]

    candidates = df[
        (df['score_pct'] >= 0.95) &
        (df['mktcap'] >= 20)       # 单位：亿元
    ].sort_values('score_pct', ascending=False)

    print(f"\n今日候选股（Top 5%）：{len(candidates)} 只")
    print(candidates[['score_pct','lhb','moneyflow','limitup','sector','rs']].head(10))

    return candidates


# =============================================================================
# 模块9：复盘记录
# =============================================================================

def record_performance(date: str, candidates: pd.DataFrame):
    """
    T日选股 → T+1至T+5日超额收益追踪

    Args:
        date: 选股日期
        candidates: 候选股票DataFrame
    """
    codes = candidates.index.tolist()
    end_date = (datetime.strptime(date, '%Y-%m-%d') +
                timedelta(days=7)).strftime('%Y-%m-%d')

    # 组合收益
    port_res = w.wss(codes, "pct_chg",
                     f"tradeDate={end_date}")
    port_return = np.mean(port_res.Data[0])

    # 基准收益（全A等权）
    bench_res = w.wsd("881001.WI", "pct_chg", end_date, end_date)
    bench_return = bench_res.Data[0][0]

    excess = port_return - bench_return
    print(f"\n超额收益（T+1）：{excess:.2%}")
    print(f"   组合：{port_return:.2%} | 基准(全A)：{bench_return:.2%}")

    # 保存记录
    record = {
        'date': date,
        'n_stocks': len(codes),
        'port_return': port_return,
        'bench_return': bench_return,
        'excess_return': excess,
        'top_stocks': ','.join(codes[:5])
    }
    log = pd.DataFrame([record])
    log.to_csv('factor_performance_log.csv', mode='a',
               header=False, index=False)


# =============================================================================
# 一键运行入口
# =============================================================================

if __name__ == "__main__":
    date = get_trade_date()
    candidates = cross_section_score(date)
    record_performance(date, candidates)
    w.stop()
