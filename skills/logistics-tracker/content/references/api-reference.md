# Logistics Tracker Skill - API Integration Reference

## Workflow

### 1. Number Identification Phase

```
User Input → Extract Number → Rule Matching → Identify Company
```

### 2. Logistics Query Phase

```
Identification Result → Call API → Get Logistics Data → Format Output
```

## Recommended API Services

### Juhe Data (Recommended)
- **Website**: https://www.juhe.cn
- **Free Quota**: 100 requests/day
- **Features**: Real-time query for multiple express companies

### Kuaidi100
- **Website**: https://www.kuaidi100.com
- **Features**: Comprehensive coverage, timely updates

### Aikuaidi
- **Website**: https://www.aikuaidi.cn
- **Features**: Affordable pricing

## API Call Examples

### Python Example

```python
import requests
import os

def query_express(track_no: str, company_code: str = None):
    """Query express logistics information

    Args:
        track_no: Tracking number
        company_code: Express company code (auto-detect if not provided)

    Returns:
        dict: Logistics information dictionary
    """
    api_key = os.environ.get("EXPRESS_API_KEY")
    base_url = "https://v.juheapi.com/express/query"

    params = {
        "key": api_key,
        "com": company_code,
        "no": track_no
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        result = response.json()

        if result.get("error_code") == 0:
            return {
                "success": True,
                "data": result.get("result", {})
            }
        else:
            return {
                "success": False,
                "error": result.get("reason", "Query failed")
            }
    except requests.Timeout:
        return {
            "success": False,
            "error": "API request timeout, please try again later"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"System error: {str(e)}"
        }

def format_tracking_output(data: dict) -> str:
    """Format logistics tracking output

    Args:
        data: Logistics data dictionary

    Returns:
        str: Formatted output text
    """
    company = data.get("company", "Unknown")
    number = data.get("number", "")
    status = data.get("status", "Unknown")
    traces = data.get("list", [])

    output = [
        f"📦 Logistics Tracking Information",
        "",
        f"🏢 Company: {company}",
        f"🔢 Tracking Number: {number}",
        f"📍 Current Status: {status}",
        ""
    ]

    if traces:
        output.append("━━━━━━━━━━━━━━━━━━━━━━")
        output.append("📍 Tracking History")
        output.append("━━━━━━━━━━━━━━━━━━━━━━")

        for trace in traces:
            time = trace.get("time", "")
            location = trace.get("location", "")
            context = trace.get("context", "")
            output.append(f"🕐 {time} | {location} | {context}")

    return "\n".join(output)
```

### JavaScript Example

```javascript
async function queryExpress(trackNo, companyCode) {
    const apiKey = process.env.EXPRESS_API_KEY;
    const baseUrl = 'https://v.juheapi.com/express/query';

    try {
        const response = await fetch(
            `${baseUrl}?key=${apiKey}&com=${companyCode}&no=${trackNo}`
        );
        const result = await response.json();

        if (result.error_code === 0) {
            return {
                success: true,
                data: result.result
            };
        } else {
            return {
                success: false,
                error: result.reason
            };
        }
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

function formatTrackingOutput(data) {
    const { company, number, status, list = [] } = data;

    let output = [
        '📦 Logistics Tracking Information',
        '',
        `🏢 Company: ${company}`,
        `🔢 Tracking Number: ${number}`,
        `📍 Current Status: ${status}`,
        ''
    ];

    if (list.length > 0) {
        output.push('━━━━━━━━━━━━━━━━━━━━━━');
        output.push('📍 Tracking History');
        output.push('━━━━━━━━━━━━━━━━━━━━━━');

        list.forEach(trace => {
            output.push(
                `🕐 ${trace.time} | ${trace.location} | ${trace.context}`
            );
        });
    }

    return output.join('\n');
}
```

## Environment Variables Configuration

```bash
# API Key Configuration
EXPRESS_API_KEY=your_api_key_here

# Backup API Configuration
EXPRESS_API_KEY_BACKUP=backup_api_key
```

## Error Code Handling

| Error Code | Description | Handling |
|-----------|-------------|----------|
| 10001 | Invalid API key | Check API key configuration |
| 10002 | Daily quota exceeded | Suggest user try tomorrow or upgrade plan |
| 10003 | Rate limit exceeded | Add request delay, retry later |
| 20001 | Express company not found | Return manual selection interface |
| 20002 | Tracking number not found | Prompt user to verify number |
| 20003 | Express company not supported | Return list of supported companies |
