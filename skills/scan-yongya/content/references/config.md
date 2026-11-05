# Yongya Scanner - Technical Reference

## Platform URL Configuration

### Android (Lingxi)
- Base URL: `https://www.jiaoyimao.com/lingxi/g1009207/`
- enforcePlat: `2`

### iOS
- Base URL: `https://www.jiaoyimao.com/lingxi/g1009207-3/`
- enforcePlat: `3`

## Search Condition

```json
{
  "s3_equip_skill": {
    "selectType": 1,
    "conditionList": ["7018093469081410054@雍雅"],
    "conditionId": "7018093469081410054",
    "statConditionList": ["雍雅"],
    "conditionType": 103
  }
}
```

## Price Tier Conditions

| Name | Condition JSON |
|------|---------------|
| 50000+ | `{"price":{"conditionList":["50000"],"groupName":"价格范围","statConditionList":["50000"]}}` |
| 40000+ | `{"price":{"conditionList":["40000"],"groupName":"价格范围","statConditionList":["40000"]}}` |
| 30000+ | `{"price":{"conditionList":["30000"],"groupName":"价格范围","statConditionList":["30000"]}}` |
| 20000+ | `{"price":{"conditionList":["20000"],"groupName":"价格范围","statConditionList":["20000"]}}` |
| 10000+ | `{"price":{"conditionList":["10000"],"groupName":"价格范围","statConditionList":["10000"]}}` |

## DOM Selectors

### Account Cards
- `[data-goodsid]` - All product cards
- `[data-goods_name]` - Product name
- `[data-price]` - Price
- `[data-game_os]` - Operating system

### Scroll Containers
- `.list-container` - List container
- `.goods-list-dom` - Product list DOM
- `document.scrollingElement` - Scrollable element
- `document.body` - Page body

## Yongya Equipment Recognition

Regex pattern: `雍雅\*(\d+)`

Examples:
- `雍雅*3` → 3 Yongya pieces
- `雍雅*5` → 5 Yongya pieces

## Scroll Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| MAX_SCROLL | 80 | Max scroll attempts |
| STABLE_STOP | 4 | Stable stop condition (4 consecutive no new) |
| SCROLL_WAIT | 2.0 | Wait seconds after each scroll |
