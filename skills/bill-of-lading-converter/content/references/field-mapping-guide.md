# 提单字段映射指南

## 标准提单字段

| 字段英文名 | 字段中文名 | 描述 | 示例 |
|-----------|-----------|------|------|
| shipper | 发货人/托运人 | 货物的发送方，通常为出口商 | ABC Trading Co., Ltd. |
| shipper_address | 发货人地址 | 发货人的完整地址 | 123 Main St, Hong Kong |
| consignee | 收货人 | 货物的接收方 | XYZ Import Inc. |
| consignee_address | 收货人地址 | 收货人的完整地址 | 456 Trade Ave, Los Angeles |
| notify_party | 通知方 | 货物到达时通知的对象 | Same as Consignee |
| notify_address | 通知方地址 | 通知方的完整地址 | - |
| vessel | 船名 | 运输货物的船舶名称 | EVER GIVEN |
| voyage | 航次 | 船舶的航次编号 | 0234E |
| port_of_loading | 装货港 | 货物装船的港口 | Shanghai, China |
| port_of_discharge | 卸货港 | 货物卸船的港口 | Los Angeles, USA |
| place_of_receipt | 收货地 | 承运人开始接管货物的地点 | Shanghai |
| place_of_delivery | 交货地 | 承运人交付货物的地点 | Chicago |
| container_no | 集装箱号 | 集装箱的唯一编号 | MSKU1234567 |
| seal_no | 封条号 | 集装箱封条编号 | SL123456 |
| container_type | 箱型 | 集装箱类型和尺寸 | 40HQ |
| description | 货物描述 | 货物的详细描述 | Electronic Components |
| gross_weight | 毛重 | 货物及其包装的总重量 | 15000 KGS |
| net_weight | 净重 | 货物的实际重量 | 14500 KGS |
| measurement | 体积 | 货物的体积尺寸 | 50 CBM |
| quantity | 件数 | 货物的总件数 | 500 CTNS |
| sailing_date | 开船日期 | 船舶预计开航日期 | 2024-01-15 |
| etd | 预计离港时间 | Estimated Time of Departure | 2024-01-15 |
| eta | 预计到港时间 | Estimated Time of Arrival | 2024-02-01 |
| bl_no | 提单号 | Bill of Lading Number | BL20240115001 |
| booking_no | 订舱号 | 订舱确认编号 | BK20240001 |
| freight_terms | 运费条款 | 运费支付方式 | Freight Prepaid |
| marks | 唛头 | 货物标识 | N/M |
| hs_code | HS编码 | 海关商品编码 | 8542.31 |

## 字段映射规则

### 从识别结果到模板的映射

```json
{
  "recognition_to_template": {
    "发货人": "shipper",
    "托运人": "shipper",
    "Shipper": "shipper",
    "Exporter": "shipper",
    "收货人": "consignee",
    "Consignee": "consignee",
    "通知方": "notify_party",
    "Notify Party": "notify_party",
    "Notify": "notify_party",
    "船名": "vessel",
    "Vessel": "vessel",
    "Ship": "vessel",
    "航次": "voyage",
    "Voyage": "voyage",
    "Voyage No.": "voyage",
    "装货港": "port_of_loading",
    "Port of Loading": "port_of_loading",
    "POL": "port_of_loading",
    "卸货港": "port_of_discharge",
    "Port of Discharge": "port_of_discharge",
    "POD": "port_of_discharge",
    "集装箱号": "container_no",
    "Container No.": "container_no",
    "封条号": "seal_no",
    "Seal No.": "seal_no",
    "货物描述": "description",
    "Description": "description",
    "Description of Goods": "description",
    "毛重": "gross_weight",
    "Gross Weight": "gross_weight",
    "G.W.": "gross_weight",
    "体积": "measurement",
    "Measurement": "measurement",
    "体积尺码": "measurement",
    "开船日期": "sailing_date",
    "Sailing Date": "sailing_date",
    "提单号": "bl_no",
    "B/L No.": "bl_no",
    "BL No.": "bl_no",
    "运费条款": "freight_terms",
    "Freight": "freight_terms"
  }
}
```

## 识别质量标准

### 高置信度字段（>90%）
- 提单号 (BL Number)
- 集装箱号 (Container Number)
- 船名 (Vessel Name)
- 港口名称 (Port Names)

### 中置信度字段（70-90%）
- 发货人/收货人名称
- 货物描述
- 日期信息

### 低置信度字段（<70%）
- 地址详情
- 封条号（手写或模糊）
- 重量和体积数值

## 常见问题

### Q: 如果提单是手写的怎么办？
A: 图片识别工具对印刷体识别效果最佳，手写内容识别准确率会降低。建议用户上传清晰的扫描件或电子提单。

### Q: 如何处理多个集装箱的情况？
A: 在JSON中使用数组格式存储多个集装箱信息：
```json
{
  "containers": [
    {"container_no": "MSKU1234567", "seal_no": "SL001", "gross_weight": "15000 KGS"},
    {"container_no": "MSKU7654321", "seal_no": "SL002", "gross_weight": "12000 KGS"}
  ]
}
```

### Q: 模板中没有某些字段怎么办？
A: 在模板的field_mapping.json中标记为可选字段，转换时跳过该字段并保留模板原样。
