---
name: time-calibrator
description: Time calibration expert skill for global use. Use when users need to sync system time, check time drift, calibrate Agent operation time, or ensure accurate real-world time. Trigger keywords: calibrate time, sync time, time check, real time, time drift, time calibration, time sync, time drift detection.
---

# Time Calibrator - Global Time Calibration Expert

## Core Capabilities

This skill fetches real-time from **time.is** (primary source) with multiple global fallback sources, ensuring reliable time synchronization worldwide. It prevents Agent operations from using stale system time.

### 1. Multi-Source Time Providers

**Primary Source**: `https://time.is/`
- Global coverage with automatic timezone detection
- High-precision Unix timestamp endpoint: `https://time.is/_/unixtime`

**Fallback Sources** (in order of fallback):
1. `WorldTimeAPI` - `https://worldtimeapi.org/api/ip`
2. `NIST Time` - `https://www.nist.gov/cgi-bin/time.pl`
3. `Google Time` - `https://clients3.google.com/generate_204`

### 2. Time Drift Detection

```python
import requests
import re
import time
from datetime import datetime, timezone

class TimeCalibrator:
    """Multi-source time calibrator for global reliability"""

    TIME_IS_MAIN = "https://time.is/"
    TIME_IS_UNIX = "https://time.is/_/unixtime"

    FALLBACK_SOURCES = [
        ("WorldTimeAPI", "https://worldtimeapi.org/api/ip"),
        ("NIST Time", "https://www.nist.gov/cgi-bin/time.pl"),
        ("Google Time", "https://clients3.google.com/generate_204"),
    ]

    def get_real_time(self):
        """
        Get real time from available sources.
        Returns: (timestamp_ms, source_name) or None
        """
        # Try time.is main page first
        unix_time = self.get_from_time_is()
        if unix_time:
            return unix_time, "time.is"

        # Try fallback sources
        for name, url in self.FALLBACK_SOURCES:
            timestamp = self.get_from_source(name, url)
            if timestamp:
                return timestamp, name

        return None

    def check_time_drift(self):
        """Detect drift between local and real time"""
        result = self.get_real_time()
        if result is None:
            return None

        real_timestamp, source = result
        local_timestamp = int(time.time() * 1000)
        drift_ms = local_timestamp - real_timestamp

        return {
            "real_time": datetime.fromtimestamp(real_timestamp / 1000).isoformat(),
            "local_time": datetime.fromtimestamp(local_timestamp / 1000).isoformat(),
            "drift_ms": drift_ms,
            "drift_seconds": drift_ms / 1000,
            "is_synced": abs(drift_ms / 1000) < 1,
            "source": source
        }
```

### 3. Time Calibration Flow

```
+-------------------------------------------------------------+
|              Global Time Calibration Flow                   |
+-------------------------------------------------------------+
|                                                              |
|  1. [Try time.is Main] -> https://time.is/               |
|           ↓ (fallback)                                       |
|  2. [Try time.is Unix] -> https://time.is/_/unixtime     |
|           ↓ (fallback)                                       |
|  3. [Try WorldTimeAPI] -> worldtimeapi.org/api/ip        |
|           ↓ (fallback)                                       |
|  4. [Try NIST] -> nist.gov/cgi-bin/time.pl              |
|           ↓ (fallback)                                       |
|  5. [Try Google] -> clients3.google.com/generate_204    |
|                                                              |
+-------------------------------------------------------------+
|                          ↓                                   |
|  6. [Calculate Drift] -> drift = local - real              |
|                          ↓                                   |
|  7. [Decision] -> |drift| < 1s?                            |
|      ↓                    ↓                                 |
|    Yes                  No                                  |
|    ↓                     ↓                                  |
|  [OK]           [WARNING + Recommend Calibration]           |
+-------------------------------------------------------------+
```

## Use Cases

### Scenario 1: Periodic Time Sync Check

Before any critical operation, check time drift:

```python
def ensure_time_synced(max_drift_seconds=5):
    """Ensure time is synchronized"""
    calibrator = TimeCalibrator()
    result = calibrator.check_time_drift()

    if result is None:
        return {"status": "error", "message": "Cannot get real time"}

    if not result["is_synced"]:
        return {
            "status": "warning",
            "message": f"Time drift: {result['drift_seconds']:.2f}s",
            "source": result["source"],
            "action": "Calibrate system time"
        }

    return {
        "status": "ok",
        "message": "Time is synced",
        "real_time": result["real_time"],
        "source": result["source"]
    }
```

### Scenario 2: Timestamped Data Collection

```python
def get_timestamped_data():
    """Get data with calibrated timestamp"""
    calibrator = TimeCalibrator()
    ts_data = calibrator.get_timestamped_data()

    return {
        "timestamp_ms": ts_data["timestamp_ms"],
        "datetime": ts_data["datetime"],
        "datetime_utc": ts_data["datetime_utc"],
        "source": ts_data["source"],
        "is_reliable": ts_data["is_reliable"]
    }
```

### Scenario 3: Batch Time Validation

```python
def validate_time_consistency(attempts=3):
    """Validate time with multiple samples"""
    calibrator = TimeCalibrator()
    result = calibrator.validate_time_consistency(attempts)

    return {
        "status": result["status"],
        "samples": result["samples"],
        "avg_drift_seconds": result["avg_drift_seconds"],
        "max_drift_ms": result["max_drift_ms"],
        "all_synced": result["all_synced"]
    }
```

## Real-World Application Examples

### Example 1: Data Collection Task

```
Task: Collect stock data for the past 24 hours

1. Call ensure_time_synced() to verify time
2. If drift > 5 seconds, emit warning and pause
3. Use get_timestamped_data() to get calibrated timestamp
4. Calculate 24-hour window based on real time
5. Execute data collection with reliable timestamps
```

### Example 2: Scheduled Task Verification

```
Task: Verify scheduled task timing accuracy

1. Get real time from time.is
2. Compare with expected execution time
3. Calculate drift between actual and expected
4. If abnormal, log and alert
```

### Example 3: Cross-Region Data Correlation

```
Task: Correlate events across different time zones

1. Get unified timestamp from time.is
2. Convert to various timezone representations
3. Ensure all data uses common time reference
4. Validate temporal consistency
```

## API Reference

### TimeCalibrator Class

#### `get_real_time() -> Tuple[int, str] | None`
Get real time from available sources. Returns `(timestamp_ms, source_name)` or None.

#### `check_time_drift() -> dict | None`
Detect drift between local and real time. Returns dict with:
- `real_time`: ISO format real time
- `local_time`: ISO format local time
- `drift_ms`: Drift in milliseconds
- `drift_seconds`: Drift in seconds
- `is_synced`: True if synced (drift < 1 second)
- `source`: Time source used
- `latency_ms`: Network latency estimate

#### `ensure_time_synced(max_drift_seconds=5) -> dict`
Ensure time is synchronized. Returns status and recommendations.

#### `get_timestamped_data() -> dict`
Get timestamped data for collection tasks with source tracking.

#### `validate_time_consistency(attempts=3) -> dict`
Multi-sample validation with average drift analysis.

## Warning Message Template

When time drift is detected:

```
WARNING: Time Drift Detected

Real Time (via {source}): {real_time}
Local System Time: {local_time}
Drift: {drift_seconds} seconds
Network Latency: {latency_ms}ms

Impact: Using stale time may cause:
  - Incomplete data collection (missing latest data)
  - Duplicate data collection (overlapping periods)
  - Scheduled task execution anomalies

Recommended Actions:
1. Check system timezone settings
2. Sync NTP service: sudo ntpdate -s time.nist.gov
3. Manually calibrate system time
```

## Best Practices

1. **Check Before Critical Operations**: Call `ensure_time_synced()` before data collection, scheduled tasks
2. **Alert on Anomaly**: When drift > 5 seconds, halt operation and alert
3. **Log Source**: Record which time source was used for traceability
4. **Multi-Validation**: Use `validate_time_consistency()` for important tasks
5. **Fault Tolerance**: Automatic fallback to multiple sources ensures global reliability
6. **Latency Awareness**: Monitor network latency to account for delays
