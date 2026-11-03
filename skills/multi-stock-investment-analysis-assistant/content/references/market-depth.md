# 美股与港股买卖盘、订单簿及主动成交分析

## 目录

- 能力边界
- 数据层级与来源
- 时点、口径与质量门槛
- 标准指标
- 盘口与交易策略的结合
- 数据不足与降级
- 脚本输入输出
- 报告与图表规范

## 能力边界

把“买盘卖盘”拆成三类不同证据，不得混用：

1. **Level 1 / 最佳买卖价**：美国市场在来源确认为NBBO时才称NBBO；港股使用HKEX交易所簿或实际提供商明确的范围口径。可分析价差、一档数量不平衡和执行成本，但不能代表完整订单簿。
2. **Level 2 / Market Depth**：多档买卖委托价格与显示数量。可分析1/5/10档深度、距离加权不平衡、价格带内累计深度和模拟扫单成本。
3. **逐笔成交 / Time & Sales**：已经成交的交易。只有数据源提供可靠的主动买卖方向时，才计算主动买入量、主动卖出量和成交量差；方向未知的成交不得强行分类。

日线成交量、MAVOL、OBV和盘口不是同一种数据。前者描述已经成交的历史行为；挂单可以撤销、隐藏或转移，不能被写成“主力一定买入/卖出”。盘口只用于短线执行和流动性判断，不改变长期企业价值。

## 数据层级与来源

按以下顺序选择实际可用来源：

1. **带权限的券商或交易所实时行情**：优先获取带时间戳的市场适用Level 1、Level 2和逐笔成交；美国核对NBBO，香港核对HKEX订单簿范围。
2. **专业市场数据提供商**：必须保留是否实时、延迟秒数、SIP/直连/单交易所口径及字段单位。
3. **公开或延迟报价源**：只能分析历史/延迟的一档价差，不能支撑“现在下单”的盘口结论。
4. **未取得可靠买卖盘**：明确写N/A，继续使用可靠OHLCV完成趋势分析，但不把日线成交量伪装成实时买卖盘。

不得把搜索摘要、截图OCR、随机种子、默认价格、演示数据或合成订单簿用于真实证券结论。来源含 `synthetic`、`simulated`、`demo`、`mock`、`random`、`placeholder` 或 `init` 时，盘口数据门槛失败。

美国股票分散在多个交易场所。单一交易所订单簿只能称“该场所显示深度”，不能称“全市场买盘/卖盘”。NBBO只覆盖最佳价格，不等于全市场多档深度。暗池、隐藏单、冰山单、零股、撤单和场外成交会使显示数量与实际可成交流动性不同。

港股先读 [hong-kong-market.md](hong-kong-market.md)。HKEX授权订单簿使用 `exchange_book`，不得称NBBO；Level 1/2取决于OMD-C或券商许可。竞价阶段需要IEP/IEV等竞价专用数据，不能把连续盘微价格与不平衡公式直接套用。每手股数按证券取得，禁止默认100股。

## 时点、口径与质量门槛

盘口快照独立于当前成交价和完整日线，至少保存：

| 字段 | 要求 |
|---|---|
| 标的 | ticker、交易所、币种 |
| 时间 | `captured_at`与`analysis_timestamp`，均含时区 |
| 市场状态 | 美股使用regular/pre_market/post_market等；港股使用morning/extended_morning/afternoon/pre_opening/midday_break/closing_auction等 |
| 来源 | 提供商名称、source_kind、是否延迟及延迟秒数 |
| 范围 | 美国：nbbo/aggregated/single_venue；香港：exchange_book/aggregated/unknown |
| 数量单位 | shares或round_lots；使用round_lots时必须显式提供当前round_lot_size，不设市场默认值 |
| 买卖档位 | 价格、显示数量；可选venue与order_count |

活跃时段的执行时点门槛：

- 正常连续交易时段：快照年龄与已知延迟中的较大者不超过60秒；港股对应morning、适用的extended_morning和afternoon。
- 盘前/盘后：不超过300秒，并明确流动性通常弱于正常时段。
- 延迟行情、休市快照和超时快照：仍可计算价差与历史盘口，但 `execution_timing_eligible=false`，不得据此写“当前买盘占优，立即买入”。
- 美股NBBO/聚合、港股HKEX `exchange_book`/明确聚合口径可用于相应市场范围的最佳价或显示深度；single_venue和unknown只能给范围受限结论。
- 港股pre_opening、midday_break和closing_auction不具备普通连续盘口执行资格；竞价必须另用专用字段和规则。
- 只有 `source_kind=broker_exchange` 或 `professional_vendor` 且其余门槛通过时，脚本才把快照视为执行级；public_vendor、user_provided或unknown仍可作研究快照，但不能仅凭标签假定实时完整。

检查并处理：

- 价格和数量必须为正数且有限。
- 买价按高到低、卖价按低到高排序；重复价位按显示股数合并。
- 最佳买价高于最佳卖价属于交叉簿，数据不可用；买卖价相同属于锁定市场，保留但警告。
- 买卖任一侧缺失时不计算中间价、价差或不平衡。
- 数量单位不明时默认shares并警告；不能无说明地把“手/lot”当成股数。

## 标准指标

### 一档

- 中间价：`mid = (best_bid + best_ask) / 2`
- 绝对价差：`spread = best_ask - best_bid`
- 价差基点：`spread_bps = spread / mid × 10,000`
- 一档数量不平衡：`(bid_size - ask_size) / (bid_size + ask_size)`，范围-1至+1。
- 微价格：`(ask × bid_size + bid × ask_size) / (bid_size + ask_size)`。它只表示一档数量权重下的短时价格倾斜，不是预测目标价。

### 多档深度

至少在可得范围内计算：

- 1档、5档、10档累计买卖股数与名义金额。
- 距离加权不平衡：越接近最佳价权重越高，脚本使用 `size / level_number`。
- 中间价上下5、10、25个基点内的累计显示深度。
- 用户给出计划股数时，模拟按显示订单簿扫单的平均价格、最差显示价格、相对中间价滑点和显示深度是否足够。

### 主动成交

只有逐笔数据提供 `aggressor_side` 时计算：

- 主动买入量、主动卖出量、未知方向量。
- 净主动成交差：主动买入量减主动卖出量。
- 成交不平衡：`(buy_volume - sell_volume) / (buy_volume + sell_volume)`。
- 方向分类覆盖率低于70%时，不把逐笔成交合并进综合战术分。

显示订单簿综合分只作启发式整理：多档深度占65%，分类覆盖充分的主动成交占35%。绝对值达到0.20才写“显示买档较重”或“显示卖档较重”，否则写“平衡/混合”。不得把该分数直接映射为买入、卖出或价格方向概率。

## 盘口与交易策略的结合

盘口证据只能影响五维系统中的“资金与量价”和短线执行：

- **顺向确认**：价格结构、成交量/MAVOL与MACD已经形成信号，实时多档深度和主动成交同向时，提高执行确认度。
- **背离降级**：价格突破但卖档快速补充、主动卖出占优或模拟扫单滑点明显时，降低仓位、等待回踩或使用限价思维。
- **流动性门槛**：价差过宽、计划股数超过显示深度、单一场所或延迟快照时，将交易计划的流动性门槛设为false或仅允许条件方案。
- **不替代结构**：即使买档显示数量较大，也不能跳过收盘确认、支撑/压力、ATR、第一目标盈亏比和事件风险校验。
- **不提升长期评级**：一个或数个盘口快照不改变基本面、估值或长期投资结论。

只有Level 1时，资金与量价评分最多把已有判断提高或降低一档，并且必须有OHLCV证据支持；只有单个延迟快照时不调整评分。可靠Level 2加逐笔成交仍不能单独获得±2，必须与价格结构、MAVOL、OBV和动量同向。

## 数据不足与降级

| 可得数据 | 可以输出 | 禁止输出 |
|---|---|---|
| 实时美股NBBO或港股HKEX一档 | 买卖价、显示数量、价差、中间价、一档不平衡 | 五档/十档深度、全市场挂单墙 |
| 实时聚合Level 2 | 多档深度、价格带深度、显示不平衡、扫单估算 | 隐藏流动性、真实主力意图、确定方向 |
| 单交易所Level 2 | 该场所多档显示深度 | 全市场买卖盘结论 |
| 延迟盘口 | 历史/延迟快照描述 | 当前执行时点建议 |
| 只有OHLCV | 成交量、MAVOL、OBV与量价结构 | 实时买一卖一、委托深度 |
| 合成/演示数据 | 仅可用于脚本测试并明确标记 | 任何真实证券投资结论 |

若用户要求实时买卖盘但当前环境没有带权限的数据源，直接说明需要接入券商/交易所或专业行情API；不要安装无关插件，也不要用网页显示的最后价格补齐缺失字段。

## 脚本输入输出

将实际快照保存为JSON后运行：

~~~bash
python3 scripts/analyze_order_book.py \
  --input order-book.json --output order-book-result.json \
  --chart-output order-book-depth.png --chart-levels 10
~~~

最小Level 1输入（以下为美股NBBO示例；港股输入见 `hong-kong-market.md`）：

~~~json
{
  "market": "US",
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "currency": "USD",
  "captured_at": "2026-08-18T10:15:05-04:00",
  "analysis_timestamp": "2026-08-18T10:15:10-04:00",
  "market_state": "regular",
  "source": "actual provider name",
  "source_kind": "broker_exchange",
  "quote_scope": "nbbo",
  "is_delayed": false,
  "size_unit": "shares",
  "bid": 305.58,
  "bid_size": 800,
  "ask": 305.59,
  "ask_size": 600
}
~~~

Level 2使用 `bids`、`asks` 数组；逐笔成交可添加 `trades`；扫单情景可添加 `sweep_sizes_shares`：

~~~json
{
  "bids": [{"price": 305.58, "size": 800, "venue": "XNAS"}],
  "asks": [{"price": 305.59, "size": 600, "venue": "XNAS"}],
  "trades": [{"price": 305.59, "size": 100, "aggressor_side": "buy"}],
  "sweep_sizes_shares": [100, 500, 1000]
}
~~~

先检查输出中的：

- `data_quality.status`
- `execution_timing_eligible`
- `synthetic_data_detected`
- `errors`与`warnings`
- `quote_scope`、`is_delayed`和快照年龄

只有 `usable_current_snapshot` 且 `execution_timing_eligible=true` 时，才可把盘口用于当前交易触发。其他状态只作历史、范围受限或条件化参考。香港竞价即使时间新鲜，普通连续盘脚本也不得将其升级为当前执行级。

## 报告与图表规范

默认在技术走势图之后增加紧凑盘口表：

| 盘口快照 | 数值 |
|---|---|
| 数据层级/范围 | Level 1或Level 2；美股NBBO/聚合/单场所，港股exchange_book/聚合/未知 |
| 时间/状态/延迟 | 含时区 |
| 买一 × 股数 | |
| 卖一 × 股数 | |
| 价差/基点 | |
| 一档、五档、十档不平衡 | 可得时填写 |
| 主动买卖量差 | 有可靠逐笔方向时填写 |
| 计划股数扫单估算 | 用户股数或明确示例 |
| 执行资格 | 当前可用/延迟历史/范围受限/不可用 |

取得Level 2时可展示脚本生成的深度图。图题和脚注必须包含标的、快照时间、来源与“显示订单可撤销、隐藏流动性未计入”的限制。Level 1只有一档时优先用表格，避免用两根柱制造虚假深度感。

图表或表格后用最多三句话说明：显示哪一侧较重、主动成交是否确认、它对当前入场/限价/仓位有什么影响。不得重复日线技术结论，也不得使用“主力吸筹、庄家压盘、必然突破”等无法核验表述。
