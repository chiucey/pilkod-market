# Express Company Identification Rules and Code Reference

## Major Chinese Express Companies

### SF Express (SF)
- **Number Format**: SF + 12 digits or 15 digits (starting with SF)
- **Example**: SF1234567890123, SF9934567891234
- **Regex**: `^SF\d{12}$|^\d{15}$`
- **API Code**: SF

### YTO Express (YTO)
- **Number Format**: YT/YT + digits or 10-12 digits (starting with YT)
- **Example**: YT1234567890, YT0001234567
- **Regex**: `^YT\d{10,12}$`
- **API Code**: YTO

### ZTO Express (ZTO)
- **Number Format**: ZTO + 12 digits or starting with 2005/6887
- **Example**: ZTO123456789012, 2005123456789016
- **Regex**: `^(ZTO|2005|6887)\d{10,12}$`
- **API Code**: ZTO

### Yunda Express (YD)
- **Number Format**: YD + 10-13 digits or 10-13 digits
- **Example**: YD10001234567, 10001234567
- **Regex**: `^(YD|1[3-9])\d{9,12}$`
- **API Code**: YD

### STO Express (STO)
- **Number Format**: STO + digits or 12 digits
- **Example**: STO123456789012, 333123456789
- **Regex**: `^STO\d{8,}$|^3\d{11}$`
- **API Code**: STO

### China Post EMS
- **Number Format**: EMS/EA/EB + 10-13 digits
- **Example**: EMS1234567890, EA1234567890
- **Regex**: `^(EMS|EA|EB)\d{10,13}$`
- **API Code**: EMS

### JD Logistics (JD)
- **Number Format**: JD + 12 digits or JDV + digits or 16-20 digits
- **Example**: JD123456789012, JDAB1234567890
- **Regex**: `^(JD|JDAB|JDAD)\d{10,}$|^\d{16,20}$`
- **API Code**: JD

### Debang Express (DB)
- **Number Format**: DB + 12 digits
- **Example**: DB123456789012
- **Regex**: `^DB\d{12}$`
- **API Code**: DB

### J&T Express (JTSD)
- **Number Format**: JT + 10-15 digits
- **Example**: JT1234567890, JTTM123456789
- **Regex**: `^(JT|JTTM)\d{8,15}$`
- **API Code**: JTSD

### Cainiao/Daniao
- **Number Format**: CN + digits or similar patterns
- **Regex**: `^CN\d{10,}$`

### ANE Logistics (ANE)
- **Number Format**: ANE + 12 digits
- **Regex**: `^ANE\d{12}$`

## International Express Companies

### DHL
- **Number Format**: 10 digits or JD + digits
- **Regex**: `^\d{10,}$|^JD\d{18}$`

### FedEx
- **Number Format**: 12 digits or 4 digits + 10 digits
- **Regex**: `^\d{12}$|^\d{4}\d{10}$`

### UPS
- **Number Format**: 1Z + 16 alphanumeric
- **Regex**: `^1Z[A-Z0-9]{16}$`

### TNT
- **Number Format**: 3 letters + 9 digits
- **Regex**: `^[A-Z]{3}\d{9}$`

## Status Codes

| Code | Status | Description |
|-----|--------|-------------|
| 0 | No Info | Tracking just created, info pending |
| 1 | Picked Up | Package picked up by courier |
| 2 | In Transit | Being delivered |
| 3 | Out for Delivery | Courier out for delivery |
| 4 | Delivered | Successfully delivered |
| 5 | Rejected | Recipient rejected |
| 6 | Returning | Returning to sender |
| 7 | Return Received | Returned and received |
| 8 | Exception | Contact customer service |
| 9 | Returned | Returned to sender |

## API Reference

### Kuaidi100 API
```
GET https://api.kuaidi100.com/api?id={API_KEY}&com={company}&nu={number}&show=0&muti=1
```

### Juhe Data Logistics API
```
GET https://v.juheapi.com/express/query?key={API_KEY}&com={company}&no={number}
```

### Response Fields
```json
{
  "company": "SF Express",
  "number": "SF1234567890123",
  "status": "In Transit",
  "state": "2",
  "list": [
    {
      "time": "2026-04-10 18:30:00",
      "location": "Shanghai Pudong",
      "context": "Package dispatched, in transit"
    }
  ]
}
```
