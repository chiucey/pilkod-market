#!/usr/bin/env python3
"""
Real-time Weather ASCII Art Generator
Query real-time weather data for any city and display ASCII art
"""

import urllib.request
import json
import sys
import os

def get_weather_emoji(condition):
    """Get emoji based on weather condition"""
    condition_lower = condition.lower()
    if 'clear' in condition_lower or 'sunny' in condition_lower:
        return '☀️'
    elif 'cloud' in condition_lower:
        if 'part' in condition_lower:
            return '⛅'
        return '☁️'
    elif 'rain' in condition_lower or 'drizzle' in condition_lower:
        return '🌧️'
    elif 'snow' in condition_lower or 'sleet' in condition_lower:
        return '❄️'
    elif 'thunder' in condition_lower or 'storm' in condition_lower:
        return '⛈️'
    elif 'fog' in condition_lower or 'mist' in condition_lower:
        return '🌫️'
    elif 'haze' in condition_lower:
        return '🌫️'
    else:
        return '🌤️'

def sunny_ascii():
    return """
        \\   |   /
          .---.
     '-.  |   |  .-
  _  .-  ---  -.  -.
 (_) '-.  |  .-  (_)
      '-. | .-'
        '---'
          |
      .---'---.
     '---'---'
    """

def cloudy_ascii():
    return """
      .--.
   .-(    ).
  (___.__)__)
   .--.  .--.
  (    )(    )
  (__)  (__)
    """

def rainy_ascii():
    return """
      .--.
   .-(    ).
  (___.__)__)
   ' ' ' ' '
  ' ' ' ' '
  ' ' ' ' '
    """

def snowy_ascii():
    return """
       .--.
    .-(    ).
   (___.__)__)
    *  *  *
   *  *  *
    *  *
    """

def partly_cloudy_ascii():
    return """
          \\   |   /
            .---.
       '-.  |   |  .-
     _  .-  ---  -.  -.
    (_) '-.  |  .-  (_)
     .--.  '---'  .--.
    (    )       (    )
     '--'         '--'
    """

def storm_ascii():
    return """
      .--.
   .-(    ).
  (___.__)__)
   ' ' ' ' '
  .' '. ' ' '.
   '  '  '  '
    """

def foggy_ascii():
    return """
  ~~~~~~~~~~~~
  ~~~~~~~~~~~~
  ~~~~~~~~~~~~
  ~~~~~~~~~~~~
    """

def get_ascii_art(condition):
    """Get ASCII art based on weather condition"""
    condition_lower = condition.lower()

    if 'clear' in condition_lower or 'sunny' in condition_lower:
        return sunny_ascii()
    elif 'part' in condition_lower and 'cloud' in condition_lower:
        return partly_cloudy_ascii()
    elif 'cloud' in condition_lower or 'overcast' in condition_lower:
        return cloudy_ascii()
    elif 'rain' in condition_lower or 'drizzle' in condition_lower:
        return rainy_ascii()
    elif 'snow' in condition_lower or 'sleet' in condition_lower:
        return snowy_ascii()
    elif 'storm' in condition_lower or 'thunder' in condition_lower:
        return storm_ascii()
    elif 'fog' in condition_lower or 'mist' in condition_lower or 'haze' in condition_lower:
        return foggy_ascii()
    else:
        return sunny_ascii()

def get_weather_from_wttr(city="Beijing"):
    """Get real-time weather from wttr.in API"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        # Extract current weather
        current = data['current_condition'][0]

        weather = {
            'city': city,
            'temperature': current['temp_C'] + '°C',
            'feels_like': current['FeelsLikeC'] + '°C',
            'condition': current['weatherDesc'][0]['value'],
            'humidity': current['humidity'] + '%',
            'wind_speed': current['windspeedKmph'] + ' km/h',
            'wind_dir': current['winddir16Point'],
            'visibility': current['visibility'] + ' km',
            'pressure': current['pressure'] + ' mbar',
            'uv_index': current['uvIndex']
        }

        return weather, None
    except Exception as e:
        return None, str(e)

def main():
    # Get city from command line argument or use default
    city = sys.argv[1] if len(sys.argv) > 1 else "Beijing"

    print("\n" + "=" * 60)
    print("    🌤️  REAL-TIME WEATHER ASCII GENERATOR  🌤️")
    print("=" * 60)
    print(f"\n🔍 Querying weather for: {city}...")
    print()

    # Get real-time weather data
    weather, error = get_weather_from_wttr(city)

    if error:
        print(f"❌ Error: {error}")
        print("   Using demo data instead...")
        print()
        weather = {
            'city': city,
            'temperature': '15°C',
            'feels_like': '14°C',
            'condition': 'Clear',
            'humidity': '45%',
            'wind_speed': '12 km/h',
            'wind_dir': 'NE',
            'visibility': '10 km',
            'pressure': '1015 mbar',
            'uv_index': '5'
        }

    # Display weather information
    emoji = get_weather_emoji(weather['condition'])

    print(f"{'=' * 60}")
    print(f"📍 城市: {weather['city']}")
    print(f"{'=' * 60}")
    print(f"🌡️  温度: {weather['temperature']} (体感 {weather['feels_like']})")
    print(f"{emoji} 天气: {weather['condition']}")
    print(f"💨 风速: {weather['wind_speed']} ({weather['wind_dir']})")
    print(f"💧 湿度: {weather['humidity']}")
    print(f"👁️ 能见度: {weather['visibility']}")
    print(f"📊 气压: {weather['pressure']}")
    print(f"☀️ UV指数: {weather['uv_index']}")
    print(f"{'=' * 60}")
    print()

    # Generate and display ASCII art
    ascii_art = get_ascii_art(weather['condition'])
    print(f"{ascii_art}")
    print(f"    {emoji}  {weather['condition']}  {emoji}")
    print()

    # Add Chinese translation
    translations = {
        'Clear': '晴朗',
        'Sunny': '晴天',
        'Partly cloudy': '多云转晴',
        'Cloudy': '多云',
        'Overcast': '阴天',
        'Light rain': '小雨',
        'Moderate rain': '中雨',
        'Heavy rain': '大雨',
        'Light snow': '小雪',
        'Moderate snow': '中雪',
        'Heavy snow': '大雪',
        'Thunderstorm': '雷暴',
        'Fog': '雾',
        'Mist': '薄雾',
        'Haze': '霾'
    }

    chinese_name = translations.get(weather['condition'], weather['condition'])
    print(f"    {emoji}  {chinese_name}  {emoji}")
    print()

    print("=" * 60)
    from datetime import datetime
    print(f"🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
