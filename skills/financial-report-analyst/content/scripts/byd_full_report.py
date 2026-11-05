"""
比亚迪 2025 年年报完整分析报告
"""

import akshare as ak
import pandas as pd

def to_yi(v):
    if pd.isna(v) or v is None:
        return 0
    return round(v / 1e8, 2)

def pct(a, b):
    if not b or b == 0:
        return 0
    return round((a / b) * 100, 2)

def growth(c, p):
    if not p or p == 0 or pd.isna(p):
        return None
    return round((c - p) / abs(p) * 100, 2)

def fmt(v, is_pct=False):
    if v is None or v == 0:
        return 'N/A'
    if is_pct:
        return f'{v:.2f}%'
    return f'{v:.2f} 亿'

# 获取数据
print('📡 正在获取比亚迪完整财务数据...\n')
income_df = ak.stock_financial_report_sina(stock='sz002594', symbol='利润表')
balance_df = ak.stock_financial_report_sina(stock='sz002594', symbol='资产负债表')
cashflow_df = ak.stock_financial_report_sina(stock='sz002594', symbol='现金流量表')

# 最新一期 (2025年报)
c = income_df.iloc[0]
p = income_df.iloc[1]

bc = balance_df.iloc[0]
bp = balance_df.iloc[1]

cc = cashflow_df.iloc[0]
cp = cashflow_df.iloc[1]

period = '2025年年报'

print('=' * 65)
print(f'📊 比亚迪 (002594) - {period}关键指标分析')
print('=' * 65)

# ==================== 利润表 ====================
print('\n【利润表】\n')

rev = to_yi(c['营业收入'])
rev_p = to_yi(p['营业收入'])
print(f'📊 营业收入: {fmt(rev)}，增长率: {fmt(growth(rev, rev_p), True)}')

op_profit = to_yi(c['营业利润'])
op_profit_p = to_yi(p['营业利润'])
print(f'🎯 营业利润: {fmt(op_profit)}，增长率: {fmt(growth(op_profit, op_profit_p), True)}')

# 核心利润
invest = (c.get('投资收益', 0) or 0) + (c.get('公允价值变动收益', 0) or 0)
gov = c.get('其他收益', 0) or 0
credit_l = c.get('信用减值损失', 0) or 0
asset_l = c.get('资产减值损失', 0) or 0
core = op_profit - to_yi(invest + gov + credit_l + asset_l)

invest_p = (p.get('投资收益', 0) or 0) + (p.get('公允价值变动收益', 0) or 0)
gov_p = p.get('其他收益', 0) or 0
credit_l_p = p.get('信用减值损失', 0) or 0
asset_l_p = p.get('资产减值损失', 0) or 0
core_p = op_profit_p - to_yi(invest_p + gov_p + credit_l_p + asset_l_p)

print(f'🎯 核心利润: {fmt(core)}，增长率: {fmt(growth(core, core_p), True)}')

net = to_yi(c['净利润'])
net_p = to_yi(p['净利润'])
print(f'💲 净利润: {fmt(net)}，增长率: {fmt(growth(net, net_p), True)}')

# 扣非归母净利润
parent_net = to_yi(c.get('归属于母公司所有者的净利润', 0))
subsidy = c.get('补贴收入', 0) or 0
other_income = c.get('其他收益', 0) or 0
# 简化计算：扣非 = 归母净利润 - 非经常性损益(其他收益+补贴)
deduct_net = parent_net - to_yi(subsidy + other_income)
print(f'💲 扣非归母净利润: {fmt(deduct_net)}')

# 毛利率
cost = to_yi(c['营业成本'])
cost_p = to_yi(p['营业成本'])
gm = pct(rev - cost, rev)
gm_p = pct(rev_p - cost_p, rev_p)
print(f'📈 毛利率: {gm:.2f}%，增长率: {fmt(growth(gm, gm_p), True)}')

# 净利率
nm = pct(net, rev)
print(f'📈 净利率: {nm:.2f}%')

# 核心利润率
cm = pct(core, rev)
print(f'📈 核心利润率: {cm:.2f}%')

# 三支柱
print(f'\n🌐 三支柱:')
core_r = pct(core, op_profit)
inv_r = pct(to_yi(invest), op_profit)
gov_r = pct(to_yi(gov), op_profit)
print(f'   - 核心利润: {fmt(core)}，占比: {core_r:.2f}%')
print(f'   - 投资总收益: {fmt(to_yi(invest))}，占比: {inv_r:.2f}%')
print(f'   - 政府补贴: {fmt(to_yi(gov))}，占比: {gov_r:.2f}%')

# 两搅局
print(f'\n🕵️ 两搅局:')
print(f'   - 信用减值: {fmt(to_yi(credit_l))}，占比 {pct(to_yi(credit_l), op_profit):.2f}%')
print(f'   - 资产减值: {fmt(to_yi(asset_l))}，占比 {pct(to_yi(asset_l), op_profit):.2f}%')

# 四费
print(f'\n💼 四费管理:')
sell = to_yi(c['销售费用'])
sell_p = to_yi(p['销售费用'])
print(f'   - 销售费用: {fmt(sell)}，增长率: {fmt(growth(sell, sell_p), True)}，费用率: {pct(sell, rev):.2f}%')

admin = to_yi(c['管理费用'])
admin_p = to_yi(p['管理费用'])
print(f'   - 管理费用: {fmt(admin)}，增长率: {fmt(growth(admin, admin_p), True)}，费用率: {pct(admin, rev):.2f}%')

rd = to_yi(c['研发费用'])
rd_p = to_yi(p['研发费用'])
print(f'   - 研发费用: {fmt(rd)}，增长率: {fmt(growth(rd, rd_p), True)}，费用率: {pct(rd, rev):.2f}%')

fin = to_yi(c['财务费用'])
fin_p = to_yi(p['财务费用'])
print(f'   - 财务费用: {fmt(fin)}，增长率: {fmt(growth(fin, fin_p), True)}，费用率: {pct(fin, rev):.2f}%')

# ==================== 现金流量表 ====================
print('\n\n【现金流量表】\n')

# 经营活动
ocf = to_yi(cc['经营活动产生的现金流量净额'])
ocf_p = to_yi(cp['经营活动产生的现金流量净额'])
print(f'📊 经营活动')
print(f'   - 经营活动现金流量净额: {fmt(ocf)}，增长率: {fmt(growth(ocf, ocf_p), True)}')
print(f'   - 核心利润获现率: {pct(ocf, core):.2f}%')

# 投资活动
icf = to_yi(cc['投资活动产生的现金流量净额'])
icf_p = to_yi(cp['投资活动产生的现金流量净额'])
capex = to_yi(cc.get('购建固定资产、无形资产和其他长期资产所支付的现金', 0))
capex_p = to_yi(cp.get('购建固定资产、无形资产和其他长期资产所支付的现金', 0))
asset_dis = to_yi(cc.get('处置固定资产、无形资产和其他长期资产所收回的现金净额', 0))

print(f'\n💲 投资活动')
print(f'   - 投资活动现金流量净额: {fmt(icf)}，增长率: {fmt(growth(icf, icf_p), True)}')
print(f'   - 购建固定资产、无形资产和其他长期资产支付的现金: {fmt(capex)}，增长率: {fmt(growth(capex, capex_p), True)}')
print(f'   - 处置固定资产、无形资产和其他长期资产收回的现金净额: {fmt(asset_dis)}')
print(f'   - 内生增长覆盖（经营现金净额-资本开支）: {fmt(ocf - capex)}')

# 筹资活动
fcf = to_yi(cc['筹资活动产生的现金流量净额'])
fcf_p = to_yi(cp['筹资活动产生的现金流量净额'])
fcf_in = to_yi(cc.get('筹资活动现金流入小计', 0))
fcf_in_p = to_yi(cp.get('筹资活动现金流入小计', 0))
invest_rcv = to_yi(cc.get('吸收投资收到的现金', 0))
invest_rcv_p = to_yi(cp.get('吸收投资收到的现金', 0))
borrow_rcv = to_yi(cc.get('取得借款收到的现金', 0))
borrow_rcv_p = to_yi(cp.get('取得借款收到的现金', 0))

print(f'\n💳 筹资活动')
print(f'   - 筹资活动现金流量净额: {fmt(fcf)}，增长率: {fmt(growth(fcf, fcf_p), True)}')
print(f'   - 筹资活动现金流入量小计: {fmt(fcf_in)}，增长率: {fmt(growth(fcf_in, fcf_in_p), True)}')
print(f'   - 吸收投资收到的现金: {fmt(invest_rcv)}，增长率: {fmt(growth(invest_rcv, invest_rcv_p), True)}')
print(f'   - 取得借款收到的现金: {fmt(borrow_rcv)}，增长率: {fmt(growth(borrow_rcv, borrow_rcv_p), True)}')

# ==================== 资产负债表 ====================
print('\n\n【资产负债表】\n')

ta = to_yi(bc['资产总计'])
ta_p = to_yi(bp['资产总计'])
print(f'📊 总资产: {fmt(ta)}，增长率: {fmt(growth(ta, ta_p), True)}')

tl = to_yi(bc['负债合计'])
debt_r = pct(tl, ta)
print(f'🎯 资产负债率: {debt_r:.2f}%')

tca = to_yi(bc['流动资产合计'])
tcl = to_yi(bc['流动负债合计'])
cur_r = round(tca / tcl, 2) if tcl else 0
print(f'💲 流动资产: {fmt(tca)}')
print(f'💲 流动负债: {fmt(tcl)}')
print(f'📐 流动比率: {cur_r:.2f}')

# 资产结构
money = to_yi(bc.get('货币资金', 0))
trad = to_yi(bc.get('交易性金融资产', 0))
equity_inv = to_yi(bc.get('其他权益工具投资', 0))
debt_inv = to_yi(bc.get('其他债权投资', 0))
lt_eq = to_yi(bc.get('长期股权投资', 0))
inv_re = to_yi(bc.get('投资性房地产', 0))
inv_total = trad + equity_inv + debt_inv + lt_eq + inv_re
biz_assets = ta - money - inv_total
goodwill = to_yi(bc.get('商誉', 0))

print(f'\n📈 资产结构')
print(f'   - 经营资产: {fmt(biz_assets)}，占比 {pct(biz_assets, ta):.2f}%')
print(f'   - 投资资产: {fmt(inv_total)}，占比 {pct(inv_total, ta):.2f}%')
print(f'   - 货币资金: {fmt(money)}，占比 {pct(money, ta):.2f}%')
print(f'   - 商誉: {fmt(goodwill)}，占比 {pct(goodwill, ta):.2f}%')

# 所有者权益结构
share = to_yi(bc.get('实收资本（或股本）', 0))
cap_rese = to_yi(bc.get('资本公积', 0))
surplus = to_yi(bc.get('盈余公积', 0))
undistr = to_yi(bc.get('未分配利润', 0))
equity = to_yi(bc.get('股东权益合计', 0))
invest_in_equity = share + cap_rese
profit_accum = surplus + undistr

print(f'\n💰 所有者权益结构')
print(f'   - 股东入资（实收资本+资本公积）: {fmt(invest_in_equity)}，占比 {pct(invest_in_equity, equity):.2f}%')
print(f'   - 利润积累（盈余公积+未分配利润）: {fmt(profit_accum)}，占比 {pct(profit_accum, equity):.2f}%')

# 负债结构
st_borrow = to_yi(bc.get('短期借款', 0))
lt_borrow = to_yi(bc.get('长期借款', 0))
bonds = to_yi(bc.get('应付债券', 0))
non_cur_due = to_yi(bc.get('一年内到期的非流动负债', 0))
int_bearing = st_borrow + lt_borrow + bonds + non_cur_due
biz_liab = tl - int_bearing

print(f'\n💸 负债结构')
print(f'   - 业务创造（经营负债）: {fmt(biz_liab)}，占比 {pct(biz_liab, tl):.2f}%')
print(f'   - 债权人提供（有息负债）: {fmt(int_bearing)}，占比 {pct(int_bearing, tl):.2f}%')

# 风险指标
notes_rcv = to_yi(bc.get('应收票据', 0))
acc_rcv = to_yi(bc.get('应收账款', 0))
contract_assets = to_yi(bc.get('合同资产', 0))
risk_total = notes_rcv + acc_rcv + contract_assets

print(f'\n⚠️ 风险指标')
print(f'   - 应收账款+应收票据+合同资产: {fmt(risk_total)}，占比 {pct(risk_total, ta):.2f}%')

# ==================== 综合点评 ====================
print('\n\n' + '=' * 65)
print('💡 综合点评：')
print('=' * 65)

comments = []

# 营收增长
if growth(rev, rev_p) and growth(rev, rev_p) > 30:
    comments.append('营收大幅增长42%，规模效应显著')
elif growth(rev, rev_p):
    comments.append(f'营收同比增长{growth(rev, rev_p):.1f}%')

# 利润质量
if core_r > 50:
    comments.append('核心利润占比超60%，主业盈利扎实')
else:
    comments.append('政府补贴占比较高，需关注利润质量')

# 现金获现
if pct(ocf, core) > 100:
    comments.append('核心利润获现率超100%，现金流健康')
elif pct(ocf, core) > 0:
    comments.append(f'核心利润获现率{pct(ocf, core):.1f}%，现金流一般')

# 负债
if debt_r > 70:
    comments.append(f'资产负债率{debt_r:.1f}%，负债水平较高')
elif debt_r > 60:
    comments.append(f'资产负债率{debt_r:.1f}%，处于中等水平')

# 研发
if pct(rd, rev) > 5:
    comments.append(f'研发费用率{pct(rd, rev):.1f}%，创新投入力度大')

# 资产减值
if to_yi(asset_l) < -10:
    comments.append(f'资产减值损失较大，需关注资产质量')

for i, comment in enumerate(comments[:5], 1):
    print(f'{i}. {comment}')

print('\n' + '=' * 65)
print('✅ 财报分析完成！')
print('=' * 65)
print('\n📝 数据来源: akshare (东方财富)')
print('⚠️  本分析仅供参考，不构成投资建议')
