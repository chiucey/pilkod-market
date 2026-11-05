---
name: zhejiang-pv-analysis-48point
description: Zhejiang PV output 48-point analysis skill. Used when users send weather images of Zhejiang province (containing temperature and weather for Hangzhou, Ningbo, Wenzhou, and Jiaxing) to predict PV output for 48 time points. Trigger phrases include: "48-point PV analysis", "PV output curve", "period-based prediction", "Zhejiang PV 48 points", etc.
---

# Zhejiang PV Output Analysis - 48-Point Skill

## Overview

Based on weather images of Zhejiang province, identify temperature and weather conditions for four cities (Hangzhou, Ningbo, Wenzhou, Jiaxing), and predict 96-point PV output curves (30-minute intervals covering 24 hours).

## Core Concepts

### 48-Point and 96-Point Definitions

| Point Type | Time Interval | Coverage | Points |
|------------|---------------|----------|--------|
| 48-point | 30 minutes | 00:00-23:30 | 48 |
| 96-point | 15 minutes | 00:00-23:45 | 96 |

### Time Period Definitions

| Period | Time Range | Description |
|--------|------------|-------------|
| Early Morning Low | 00:00-06:00 | PV output is 0 |
| Gradual Rise | 06:00-09:00 | Sunrise to morning, output gradually increases |
| Peak Period | 09:00-15:00 | Strongest sunlight, highest output |
| Gradual Decline | 15:00-18:00 | Afternoon to evening, output gradually decreases |
| Evening Low | 18:00-19:30 | Around sunset, output drops quickly |
| Night Low | 19:30-24:00 | PV output is 0 |

## Temperature Period Definitions

| Period | Time Range | Value Rule |
|--------|------------|------------|
| Early Morning | 00:00-08:00 | Minimum temperature |
| Noon | 09:00-17:00 | Maximum temperature |
| Night | 18:00-23:00 | Minimum temperature |

**Baseline Rule**: Use Hangzhou temperature as the provincial temperature baseline.

## PV Output Baseline Values

| Region Classification | Cities | Baseline Output (kW) |
|---------------------|--------|---------------------|
| Hangzhou-Ningbo Type | Hangzhou + Ningbo | 15,000 |
| Wenzhou Type | Wenzhou | 15,000 |
| Jiaxing Type | Jiaxing | 18,000 |

## Sun Condition Evaluation Standards

Determine sun level based on weather icons:

| Sun Level | Applicable Icons | Output Coefficient |
|-----------|------------------|-------------------|
| Best/Sunny | Sun, Clear | 1.0 (100%) |
| Good/Cloudy | Cloudy, Partly Cloudy | 0.7 (70%) |
| Average/Overcast | Overcast | 0.4 (40%) |
| Poor/Rain | Light Rain, Moderate Rain | 0.15 (15%) |
| Worst/Snow/Storm | Heavy Rain, Snow, Storm | 0.05 (5%) |

## 48-Point Output Curve Model

### Standard Sunny Day Output Curve (Normalized Coefficients)

| Period | Time Points | Output Coefficient |
|--------|-------------|-------------------|
| Night | 00:00-05:30 | 0.00 |
| Early Morning Rise | 06:00-06:30 | 0.10 |
| Morning Rise | 07:00-08:00 | 0.30 |
| Morning | 08:30-09:00 | 0.60 |
| Morning Peak | 09:30-11:00 | 0.85 |
| Noon Peak | 11:30-12:30 | 1.00 |
| Afternoon Peak | 13:00-14:00 | 0.95 |
| Afternoon | 14:30-15:30 | 0.80 |
| Late Afternoon Decline | 16:00-17:00 | 0.60 |
| Evening Decline | 17:30-18:30 | 0.30 |
| Twilight | 19:00-19:30 | 0.05 |
| Night | 20:00-24:00 | 0.00 |

### Weather Correction Coefficient Matrix

| Sun Level | Period Correction |
|-----------|-------------------|
| Sunny | × 1.0 |
| Cloudy | × 0.7 |
| Overcast | × 0.4 |
| Rain | × 0.15 |
| Snow/Storm | × 0.05 |

## Output Format

### 1. Temperature Statistics Table

| City | Early Morning Min | Noon Max | Night Min |
|------|------------------|----------|-----------|
| Hangzhou | -°C | -°C | -°C |
| Ningbo | -°C | -°C | -°C |
| Wenzhou | -°C | -°C | -°C |
| Jiaxing | -°C | -°C | -°C |

### 2. PV Output Summary Table

| Region Classification | Sun Condition | Output Coefficient | Predicted Output (kW) |
|----------------------|---------------|-------------------|---------------------|
| Hangzhou+Ningbo | Sunny | 1.0 | 15,000 |
| Wenzhou | Cloudy | 0.7 | 10,500 |
| Jiaxing | Overcast | 0.4 | 7,200 |

### 3. 48-Point Output Curve (96-Point Format)

```
| Time Point | Hangzhou+Ningbo(kW) | Wenzhou(kW) | Jiaxing(kW) | Provincial Total(kW) |
|------------|---------------------|-------------|-------------|---------------------|
| 00:00 | 0 | 0 | 0 | 0 |
| 00:30 | 0 | 0 | 0 | 0 |
| ... | ... | ... | ... | ... |
| 12:00 | 15,000 | 10,500 | 7,200 | 32,700 |
| ... | ... | ... | ... | ... |
| 23:30 | 0 | 0 | 0 | 0 |
```

### 4. Period Statistics

| Period | Time Range | Average Output (kW) | Output Ratio |
|--------|------------|---------------------|--------------|
| Early Morning | 00:00-06:00 | 0 | 0% |
| Morning | 06:00-12:00 | XX,XXX | XX% |
| Afternoon | 12:00-18:00 | XX,XXX | XX% |
| Night | 18:00-24:00 | XX,XXX | XX% |

### 5. Summary Information

- **Provincial PV Predicted Total Output**: XX,XXX kW
- **Daily Output Total**: XX,XXX kWh
- **Output Compliance Rate**: XX%
- **Peak Period**: XX:00 - XX:00
- **Recommended Actions**: Adjust bidding strategy based on output prediction

## Execution Flow

1. **Image Recognition**: Parse weather images, extract four cities' temperatures and weather icons
2. **Temperature Extraction**: Record each city's early morning minimum, noon maximum, and night minimum temperatures
3. **Sun Evaluation**: Determine sun level for each region based on weather icons
4. **Coefficient Calculation**: Convert sun level to output coefficient
5. **Curve Generation**: Calculate 96-point output for each region based on 48-point model
6. **Summary Output**: Generate complete analysis report including 96-point data

## 48-Point Detailed Schedule

| Point # | Time | Output Coefficient (Sunny) |
|---------|------|---------------------------|
| 1 | 00:00 | 0.00 |
| 2 | 00:30 | 0.00 |
| 3 | 01:00 | 0.00 |
| 4 | 01:30 | 0.00 |
| 5 | 02:00 | 0.00 |
| 6 | 02:30 | 0.00 |
| 7 | 03:00 | 0.00 |
| 8 | 03:30 | 0.00 |
| 9 | 04:00 | 0.00 |
| 10 | 04:30 | 0.00 |
| 11 | 05:00 | 0.00 |
| 12 | 05:30 | 0.00 |
| 13 | 06:00 | 0.10 |
| 14 | 06:30 | 0.25 |
| 15 | 07:00 | 0.40 |
| 16 | 07:30 | 0.55 |
| 17 | 08:00 | 0.65 |
| 18 | 08:30 | 0.75 |
| 19 | 09:00 | 0.82 |
| 20 | 09:30 | 0.88 |
| 21 | 10:00 | 0.92 |
| 22 | 10:30 | 0.95 |
| 23 | 11:00 | 0.97 |
| 24 | 11:30 | 1.00 |
| 25 | 12:00 | 1.00 |
| 26 | 12:30 | 0.98 |
| 27 | 13:00 | 0.95 |
| 28 | 13:30 | 0.92 |
| 29 | 14:00 | 0.88 |
| 30 | 14:30 | 0.82 |
| 31 | 15:00 | 0.75 |
| 32 | 15:30 | 0.65 |
| 33 | 16:00 | 0.55 |
| 34 | 16:30 | 0.45 |
| 35 | 17:00 | 0.35 |
| 36 | 17:30 | 0.22 |
| 37 | 18:00 | 0.10 |
| 38 | 18:30 | 0.05 |
| 39 | 19:00 | 0.00 |
| 40 | 19:30 | 0.00 |
| 41 | 20:00 | 0.00 |
| 42 | 20:30 | 0.00 |
| 43 | 21:00 | 0.00 |
| 44 | 21:30 | 0.00 |
| 45 | 22:00 | 0.00 |
| 46 | 22:30 | 0.00 |
| 47 | 23:00 | 0.00 |
| 48 | 23:30 | 0.00 |

## Notes

- Temperature data is used for trend analysis and does not directly affect PV output calculation
- Sun condition is the core determinant of PV output
- Output curves are based on standard sunny day models; actual weather affects curve shape
- For special weather (typhoons, storms, etc.), manual calibration is required
- 48-point data can be used as reference for day-ahead market bidding