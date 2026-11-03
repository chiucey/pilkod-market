#!/usr/bin/env python3
"""
浙江光伏出力计算器
根据天气情况和太阳等级计算光伏预测出力
"""

# 太阳等级到出力系数的映射
SUN_COEFFICIENTS = {
    "晴": 1.0,
    "太阳": 1.0,
    "晴朗": 1.0,
    "阳光充足": 1.0,
    "多云": 0.7,
    "晴间多云": 0.7,
    "阴": 0.4,
    "阴天": 0.4,
    "小雨": 0.15,
    "中雨": 0.15,
    "大雨": 0.05,
    "暴雨": 0.05,
    "雪": 0.05,
    "雷阵雨": 0.05,
}

# 各区域光伏基准出力（kW）
BASE_OUTPUT = {
    "hangzhou_ningbo": 15000,  # 杭州+宁波
    "wenzhou": 15000,          # 温州
    "jiaxing": 18000           # 嘉兴
}


def get_coefficient(weather: str) -> float:
    """
    根据天气情况获取出力系数

    Args:
        weather: 天气情况字符串

    Returns:
        出力系数（0.0 - 1.0）
    """
    for key, coef in SUN_COEFFICIENTS.items():
        if key in weather:
            return coef
    return 0.5  # 默认中等系数


def calculate_pv_output(region: str, weather: str) -> dict:
    """
    计算指定区域的光伏出力

    Args:
        region: 区域名称 ("hangzhou_ningbo", "wenzhou", "jiaxing")
        weather: 天气情况

    Returns:
        包含计算结果的字典
    """
    base = BASE_OUTPUT.get(region, 0)
    coef = get_coefficient(weather)
    output = base * coef

    return {
        "region": region,
        "weather": weather,
        "coefficient": coef,
        "base_output": base,
        "predicted_output": round(output, 2)
    }


def analyze_weather_image(weather_data: dict) -> dict:
    """
    分析天气图片数据并生成光伏出力报告

    Args:
        weather_data: 包含四地天气信息的字典
            {
                "hangzhou": {"weather": "晴", "morning_min": -5, "noon_max": 8, "night_min": 2},
                "ningbo": {"weather": "晴", ...},
                "wenzhou": {"weather": "多云", ...},
                "jiaxing": {"weather": "阴", ...}
            }

    Returns:
        完整的分析报告字典
    """
    results = []

    # 杭州+宁波区域（取杭州的天气作为代表）
    hangningbo_weather = weather_data.get("hangzhou", {}).get("weather", "未知")
    results.append(calculate_pv_output("hangzhou_ningbo", hangningbo_weather))

    # 温州
    wenzhou_weather = weather_data.get("wenzhou", {}).get("weather", "未知")
    results.append(calculate_pv_output("wenzhou", wenzhou_weather))

    # 嘉兴
    jiaxing_weather = weather_data.get("jiaxing", {}).get("weather", "未知")
    results.append(calculate_pv_output("jiaxing", jiaxing_weather))

    # 计算总出力
    total_output = sum(r["predicted_output"] for r in results)
    max_possible = sum(BASE_OUTPUT.values())
    compliance_rate = (total_output / max_possible) * 100 if max_possible > 0 else 0

    return {
        "area_results": results,
        "total_output": round(total_output, 2),
        "max_possible": max_possible,
        "compliance_rate": round(compliance_rate, 2)
    }


def format_report(analysis_result: dict) -> str:
    """
    格式化分析报告为可读字符串

    Args:
        analysis_result: analyze_weather_image 返回的结果

    Returns:
        格式化的报告字符串
    """
    region_names = {
        "hangzhou_ningbo": "杭州+宁波",
        "wenzhou": "温州",
        "jiaxing": "嘉兴"
    }

    lines = [
        "| 区域分类 | 太阳情况 | 出力系数 | 预测出力（kW） |",
        "|----------|----------|---------|---------------|"
    ]

    for r in analysis_result["area_results"]:
        region_name = region_names.get(r["region"], r["region"])
        lines.append(
            f"| {region_name} | {r['weather']} | {r['coefficient']:.1f} | {r['predicted_output']:,.0f} |"
        )

    lines.append("")
    lines.append(f"**全省光伏预测总出力**：{analysis_result['total_output']:,.0f} kW")
    lines.append(f"**出力达标率**：{analysis_result['compliance_rate']:.1f}%")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试数据
    test_data = {
        "hangzhou": {"weather": "晴", "morning_min": -5, "noon_max": 8, "night_min": 2},
        "ningbo": {"weather": "晴", "morning_min": -4, "noon_max": 9, "night_min": 3},
        "wenzhou": {"weather": "多云", "morning_min": 2, "noon_max": 12, "night_min": 6},
        "jiaxing": {"weather": "阴", "morning_min": -3, "noon_max": 6, "night_min": 1}
    }

    result = analyze_weather_image(test_data)
    print(format_report(result))