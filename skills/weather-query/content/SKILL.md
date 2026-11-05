---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 39293512d7c988dbf40f111613d85912
    PropagateID: 39293512d7c988dbf40f111613d85912
    ReservedCode1: 30460221008ece580944ae022ce8cf0084cd9f389b256ca5a210bfadf80c4bd3807894c6e50221008d3d7b54c59a612723214078e88215bb635450beaff349964ae3931756c5e087
    ReservedCode2: 3045022100e3765ad2859aacccea3e5ed92bedb919d11351874fe306431ae331c19a52a57602201e89b4ba8ffaa953ecf2087830ec0d91c94ffc1613bfa79a00c4d63ccc71783b
description: 查询指定日期和城市的天气信息。当用户请求查询天气、询问某地温度、想知道明天/后天天气时使用。支持全球城市查询，包括国内城市（北京、上海、广州、深圳、香港、台北）和国际城市（东京、纽约、伦敦、巴黎、新加坡、首尔）。
name: weather-query
---

# 天气查询技能

## 功能概述

此技能用于查询指定日期和城市的天气信息，支持全球范围内的城市天气查询。

## 核心能力

1. **日期选择**：支持查询今天及未来 7 天的天气
2. **城市查询**：支持全球任何城市的天气查询
3. **天气数据**：显示最高温度、最低温度、湿度、风速和天气状况

## 热门城市列表

### 国内城市
- 北京、上海、广州、深圳
- 香港、台北

### 国际城市
- 东京、纽约、伦敦、巴黎
- 新加坡、首尔

## API 集成

### 数据来源
天气数据使用 **Open-Meteo API**（免费，无需 API Key）

### 地址编码 API
```
GET https://geocoding-api.open-meteo.com/v1/search
Parameters:
  - name: 城市名称
  - count: 返回数量
  - language: 语言 (zh/en)
```

### 天气数据 API
```
GET https://api.open-meteo.com/v1/forecast
Parameters:
  - latitude: 纬度
  - longitude: 经度
  - daily: 天气字段 (temperature_2m_max, temperature_2m_min, weathercode, windspeed_10m_max, precipitation_sum)
  - hourly: 详细小时数据
  - timezone: 时区 (auto)
  - start_date: 开始日期
  - end_date: 结束日期
```

## 执行流程

### 1. 解析用户请求
- 提取城市名称
- 提取日期（如有）
- 默认日期为今天

### 2. 获取城市坐标
调用地理编码 API 获取城市的纬度和经度

### 3. 获取天气数据
使用坐标调用天气 API 获取对应日期的天气信息

### 4. 格式化输出
将天气数据格式化为易读的报告格式

## 输出格式

天气查询结果应包含：
- 城市名称
- 查询日期
- 天气状况（文字描述）
- 最高/最低温度
- 湿度
- 风速
- 降水概率

## 注意事项

1. API 限制：Open-Meteo 提供免费天气数据，有请求频率限制
2. 数据延迟：天气预报数据可能有轻微延迟
3. 日期范围：仅支持查询今天及未来 7 天的天气
4. 城市名称：尽量使用标准城市名称以提高搜索准确性

## 天气代码对应表

| 代码 | 描述 |
|------|------|
| 0 | 晴朗 |
| 1-3 | 多云 |
| 45-48 | 雾 |
| 51-55 | 毛毛雨 |
| 61-65 | 雨 |
| 71-77 | 雪 |
| 80-82 | 阵雨 |
| 95-99 | 雷暴 |
