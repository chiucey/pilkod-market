# 数据结构参考

## 饮食记录数据格式

```json
{
  "date": "2025-06-20",
  "meals": [
    {
      "type": "breakfast",
      "time": "07:30",
      "foods": ["鸡蛋", "牛奶", "全麦面包"],
      "calories": 450,
      "macronutrients": {
        "protein_g": 20,
        "carbs_g": 55,
        "fat_g": 15,
        "fiber_g": 5,
        "saturated_fat_g": 5,
        "monounsaturated_fat_g": 6,
        "polyunsaturated_fat_g": 3,
        "trans_fat_g": 0.1
      },
      "micronutrients": {
        "vitamin_a_mcg": 150,
        "vitamin_c_mg": 5,
        "vitamin_d_mcg": 1.5,
        "vitamin_e_mg": 1,
        "vitamin_k_mcg": 5,
        "thiamine_mg": 0.3,
        "riboflavin_mg": 0.4,
        "niacin_mg": 4,
        "vitamin_b6_mg": 0.1,
        "folate_mcg": 30,
        "vitamin_b12_mcg": 0.6,
        "calcium_mg": 250,
        "iron_mg": 2,
        "magnesium_mg": 40,
        "phosphorus_mg": 200,
        "zinc_mg": 2,
        "selenium_mcg": 10,
        "potassium_mg": 350,
        "sodium_mg": 300
      },
      "special_nutrients": {
        "omega_3_g": 0.1,
        "choline_mg": 150
      }
    }
  ],
  "daily_summary": {
    "total_calories": 2000,
    "total_macronutrients": {
      "protein_g": 80,
      "carbs_g": 250,
      "fat_g": 65,
      "fiber_g": 30
    },
    "rda_achievement": {
      "protein": 100,
      "vitamin_c": 85,
      "vitamin_d": 35,
      "calcium": 90,
      "iron": 75
    },
    "goal_achieved": true
  }
}
```

## 营养素参考值 (RDA/AI)

### 成人男性（18-65岁）

| 营养素 | 单位 | RDA | UL |
|--------|------|-----|-----|
| 蛋白质 | g | 65 | - |
| 维生素A | mcg | 800 | 3000 |
| 维生素C | mg | 100 | 2000 |
| 维生素D | mcg | 15 | 100 |
| 维生素E | mg | 14 | 1000 |
| 钙 | mg | 800 | 2000 |
| 铁 | mg | 12 | 45 |
| 锌 | mg | 12.5 | 40 |
| 钾 | mg | 2000 | - |
| 钠 | mg | 1500 | 2300 |
| 膳食纤维 | g | 30 | - |

### 成人女性（18-65岁）

| 营养素 | 单位 | RDA | UL |
|--------|------|-----|-----|
| 蛋白质 | g | 55 | - |
| 维生素A | mcg | 700 | 3000 |
| 维生素C | mg | 100 | 2000 |
| 维生素D | mcg | 15 | 100 |
| 维生素E | mg | 14 | 1000 |
| 钙 | mg | 800 | 2000 |
| 铁 | mg | 20 | 45 |
| 锌 | mg | 7.5 | 40 |
| 钾 | mg | 2000 | - |
| 钠 | mg | 1500 | 2300 |
| 膳食纤维 | g | 30 | - |
