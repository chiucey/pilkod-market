---
name: weather-ascii
description: Generate ASCII weather art and display real-time weather information. Use when users request weather ASCII art, city weather queries with icons, or weather visualization.
---

# Weather ASCII Generator

Query real-time weather for any city and generate ASCII weather icons.

## Workflow

### 1. Auto-detect User Location

Use the following API to automatically detect user location:

```bash
curl -s "wttr.in/?format=j1" | python3 -c "import sys, json; data = json.loads(sys.stdin.read()); nearest = data.get('nearest_area', [{}])[0]; print(nearest.get('areaName', [{}])[0].get('value', 'Beijing'))"
```

### 2. Location Confirmation Form

Show a GenUI form for user to confirm or modify the city:

```
<genui-form-wizard title="Location Confirmation" action-id="weather_location_confirm">
<genui-form-page title="Step 1: Location (Confirmation)">
<genui-radio-group name="location_confirm">
<genui-radio value="confirm_auto">Auto-detected City</genui-radio>
<genui-radio value="custom">Enter a different city</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="custom_city" placeholder="Enter city name..."></genui-input>
</genui-form-page>
</genui-form-wizard>
```

### 3. Query Real-time Weather

Use wttr.in API to fetch weather data:

```bash
curl -s "https://wttr.in/{city_name}?format=j1"
```

### 4. Generate ASCII Weather Icons

Select the appropriate ASCII art based on weather condition:

| Weather Keywords | ASCII Art | Emoji |
|-----------------|----------|-------|
| clear, sunny | Sun pattern | ☀️ |
| partly cloud | Partial sun/cloud | ⛅ |
| cloudy, overcast | Cloud pattern | ☁️ |
| rain, drizzle | Rain pattern | 🌧️ |
| snow, sleet | Snowflake pattern | ❄️ |
| thunder, storm | Thunder pattern | ⛈️ |
| fog, mist, haze | Fog pattern | 🌫️ |

### 5. Output Complete Weather Report

Include the following information:
- City name
- Temperature (actual + feels like)
- Weather condition (Chinese + English)
- Wind speed and direction
- Humidity
- Visibility
- Pressure
- UV index

## Execution Script

Run `python scripts/weather_realtime.py {city_name}` to generate ASCII weather output.

## Quality Standards

- All API calls must successfully retrieve real-time data
- ASCII icons must match weather conditions
- Output must include complete weather information
- Users must have the opportunity to confirm or modify city selection
