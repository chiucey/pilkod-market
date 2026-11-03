# Ricequant API 文档索引

> 文档来源：https://www.ricequant.com/doc/
> 下载时间：2026-03-24
> 路径：skills/ricequant/docs/

## 文档列表

| 文件 | 内容 | 大小 |
|------|------|------|
| stock-mod.md | A股财务数据、EPS、股本、分红派息等 | 496KB |
| generic-api.md | 跨品种通用API（get_price等） | 101KB |
| futures-mod.md | 期货、期权API | 62KB |
| options-mod.md | 期权希腊字母、主力月份等 | - |
| fund-mod.md | 公募基金ETF | - |
| risk-factors-mod.md | 风险因子模型 | - |
| convertible-mod.md | 可转债 | - |
| indices-mod.md | 指数、场内基金 | - |

## 关键API速查

### EPS（财报）→ stock-mod.md
```python
rd.get_pit_financials_ex(
    order_book_ids='000001.XSHE',
    fields=['basic_eps', 'eps_weighted', 'eps_cut_eps'],
    start_quarter='2021q1',
    end_quarter='2026q1'
)
```

### 股本 → stock-mod.md
```python
rd.get_shares('000001.XSHE', start_date='2026-03-24', end_date='2026-03-24')
```

### 行情 → generic-api.md
```python
rd.get_price('000001.XSHE', start_date='2026-01-01', end_date='2026-03-24', frequency='1d')
```

## 查询命令
```bash
curl -s "https://www.ricequant.com/doc/sources/rqdata/python/stock-mod.md" | grep -i "eps"
curl -s "https://www.ricequant.com/doc/sources/rqdata/python/generic-api.md" | grep -i "get_price"
```
