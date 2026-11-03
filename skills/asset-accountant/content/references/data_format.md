# 资产数据存储格式说明

## 文件位置

所有资产数据存储在：`/memories/asset_accounts.json`

## 数据结构

```json
{
  "version": "1.0",
  "last_updated": "2024-01-01T12:00:00",
  "settings": {
    "currency": "CNY",
    "display_precision": 2
  },
  "accounts": {
    "[account_id]": {
      "id": "account_id",
      "name": "账户显示名称",
      "type": "account_type_code",
      "platform": "所属平台/机构",
      "category": "asset | liability",
      "balance": 12345.67,
      "currency": "CNY",
      "notes": "备注信息",
      "tags": ["tag1", "tag2"],
      "created_at": "2024-01-01",
      "updated_at": "2024-01-01",
      "history": [
        {"date": "2024-01-01", "balance": 12345.67, "note": "初始记录"},
        {"date": "2024-01-02", "balance": 12400.00, "note": "工资到账"}
      ]
    }
  },
  "summary": {
    "total_assets": 100000.00,
    "total_liabilities": 30000.00,
    "net_worth": 70000.00,
    "asset_count": 5,
    "liability_count": 2
  }
}
```

## 账户类型代码 (type)

| 代码 | 名称 | 说明 |
|------|------|------|
| bank_savings | 银行存款 | 储蓄卡、定期存款 |
| credit_card | 信用卡 | 信用卡欠款 |
| securities | 证券账户 | 股票、基金、债券 |
| wealth_mgmt | 理财产品 | 银行理财、净值型理财 |
| loan | 贷款 | 房贷、车贷、信用贷 |
| housing_fund | 公积金 | 住房公积金 |
| payment_asset | 支付余额 | 支付宝/微信余额 |
| payment_liability | 信用支付 | 花呗、借呗、白条 |
| cash | 现金 | 现金资产 |
| other | 其他 | 其他类型账户 |

## 操作命令

### 读取所有账户
```
读取 /memories/asset_accounts.json
```

### 添加新账户
```
在 accounts 对象中添加新键值对
更新 summary 中的计数
重新计算 total_assets / total_liabilities / net_worth
```

### 更新账户余额
```
更新对应账户的 balance 字段
在 history 数组中添加新记录
更新 updated_at 时间戳
重新计算汇总数据
```

### 删除账户
```
从 accounts 对象中删除对应键
更新 summary 中的计数
重新计算汇总数据
```

## 计算公式

```python
# 总资产 = 所有 category="asset" 的账户余额之和
total_assets = sum(acc.balance for acc in accounts.values() if acc.category == "asset")

# 总负债 = 所有 category="liability" 的账户余额之和
total_liabilities = sum(acc.balance for acc in accounts.values() if acc.category == "liability")

# 净资产 = 总资产 - 总负债
net_worth = total_assets - total_liabilities
```

## 数据备份

每次重大更新前自动备份到 `/memories/asset_accounts_backup.json`
