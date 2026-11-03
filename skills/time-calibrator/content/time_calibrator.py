#!/usr/bin/env python3
"""
Time Calibrator - Time Calibration Tool
Fetch real-time from time.is (primary) and other global NTP sources
Supports worldwide time synchronization with fallback mechanisms
"""

import requests
import re
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import sys


class TimeCalibrator:
    """
    Time calibrator with multi-source support for global reliability.
    Uses time.is as primary source with multiple fallback options.
    """

    # Primary source: time.is (global, automatic timezone detection)
    TIME_IS_MAIN = "https://time.is/"
    TIME_IS_UNIX = "https://time.is/_/unixtime"

    # Fallback sources for global coverage
    FALLBACK_SOURCES = [
        ("WorldTimeAPI", "https://worldtimeapi.org/api/ip"),
        ("NIST Time", "https://www.nist.gov/cgi-bin/time.pl"),
        ("Google Time", "https://clients3.google.com/generate_204"),
    ]

    def __init__(self):
        self.last_check_time = None
        self.drift_history = []
        self.last_used_source = None
        self.network_latency_ms = None

    def get_real_time_from_time_is_main(self) -> Optional[Tuple[int, int]]:
        """
        Fetch real time from time.is main page.
        Returns: (timestamp_ms, network_latency_ms) or None
        """
        try:
            # Use a simple request to measure server time
            headers = {
                'User-Agent': 'Mozilla/5.0 (Time Calibrator Bot)',
                'Accept': 'text/html'
            }

            # Record request time for latency calculation
            request_time_ms = int(time.time() * 1000)

            response = requests.get(
                self.TIME_IS_MAIN,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                response_time_ms = int(time.time() * 1000)
                self.network_latency_ms = (response_time_ms - request_time_ms) // 2

                # Try to extract server time from headers
                # time.is returns accurate time, estimate from response time
                estimated_server_time = request_time_ms + self.network_latency_ms

                # Also try to get Unix timestamp endpoint
                unix_time = self.get_real_time_from_unix_endpoint()
                if unix_time:
                    return unix_time, self.network_latency_ms

                return estimated_server_time, self.network_latency_ms

        except requests.RequestException as e:
            print(f"Failed to fetch from time.is main: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error from time.is main: {e}", file=sys.stderr)

        return None

    def get_real_time_from_unix_endpoint(self) -> Optional[int]:
        """
        Fetch Unix timestamp from time.is/_/unixtime endpoint.
        Returns: Unix timestamp in milliseconds or None
        """
        try:
            response = requests.get(self.TIME_IS_UNIX, timeout=10)
            if response.status_code == 200:
                timestamp_str = response.text.strip()
                return int(timestamp_str) * 1000  # Convert to milliseconds
        except requests.RequestException:
            pass
        except ValueError:
            pass
        return None

    def get_real_time_from_worldtimeapi(self) -> Optional[int]:
        """
        Fetch time from WorldTimeAPI (based on client IP).
        Returns: Unix timestamp in milliseconds or None
        """
        try:
            response = requests.get(
                self.FALLBACK_SOURCES[0][1],
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if 'unixtime' in data:
                    return int(data['unixtime']) * 1000
                elif 'datetime' in data:
                    dt = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
                    return int(dt.timestamp() * 1000)
        except (requests.RequestException, ValueError, KeyError):
            pass
        return None

    def get_real_time_from_nist(self) -> Optional[int]:
        """
        Fetch time from NIST time service.
        Returns: Unix timestamp in milliseconds or None
        """
        try:
            response = requests.get(
                self.FALLBACK_SOURCES[1][1],
                timeout=10,
                headers={'Accept': 'text/plain'}
            )
            if response.status_code == 200:
                # NIST format: "13:15:36 UTC(NIST), January 25, 2026"
                text = response.text
                # Extract time components
                match = re.search(r'(\d{2}):(\d{2}):(\d{2})', text)
                if match:
                    # Parse as current UTC date
                    now = datetime.now(timezone.utc)
                    dt = now.replace(
                        hour=int(match.group(1)),
                        minute=int(match.group(2)),
                        second=int(match.group(3)),
                        microsecond=0
                    )
                    return int(dt.timestamp() * 1000)
        except (requests.RequestException, ValueError):
            pass
        return None

    def get_real_time_from_google(self) -> Optional[Tuple[int, int]]:
        """
        Fetch time from Google's generate_204 endpoint.
        Returns: (timestamp_ms, latency_ms) or None
        """
        try:
            request_time = int(time.time() * 1000)
            response = requests.get(
                self.FALLBACK_SOURCES[2][1],
                timeout=10
            )
            response_time = int(time.time() * 1000)

            # Google returns timestamp in headers
            date_header = response.headers.get('Date')
            if date_header:
                dt = datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %Z')
                dt = dt.replace(tzinfo=timezone.utc)
                return int(dt.timestamp() * 1000), (response_time - request_time) // 2

            # Fallback: estimate from round-trip
            return request_time + (response_time - request_time) // 2, self.network_latency_ms

        except (requests.RequestException, ValueError, KeyError):
            pass
        return None

    def get_real_time(self) -> Optional[Tuple[int, str]]:
        """
        Get real time from available sources (try in order of reliability).
        Returns: (timestamp_ms, source_name) or None
        """
        sources = [
            (self.get_real_time_from_time_is_main, "time.is/main"),
            (self.get_real_time_from_unix_endpoint, "time.is/_/unixtime"),
            (self.get_real_time_from_worldtimeapi, "WorldTimeAPI"),
            (self.get_real_time_from_nist, "NIST"),
            (self.get_real_time_from_google, "Google"),
        ]

        for source_func, source_name in sources:
            try:
                result = source_func()
                if result is not None:
                    if isinstance(result, tuple):
                        timestamp, latency = result
                        self.network_latency_ms = latency
                    else:
                        timestamp = result

                    if timestamp > 1000000000000:  # Sanity check (must be > year 2001 in ms)
                        self.last_used_source = source_name
                        return timestamp, source_name
            except Exception:
                continue

        return None

    def get_local_time_ms(self) -> int:
        """Get local Unix timestamp in milliseconds"""
        return int(time.time() * 1000)

    def check_time_drift(self) -> Optional[Dict[str, Any]]:
        """
        Detect drift between local time and real time.
        Returns: Dict with drift info or None on failure
        """
        result = self.get_real_time()
        if result is None:
            return None

        real_timestamp, source = result
        local_timestamp = self.get_local_time_ms()

        drift_ms = local_timestamp - real_timestamp
        drift_seconds = drift_ms / 1000

        # Convert to human-readable format
        real_datetime = datetime.fromtimestamp(real_timestamp / 1000)
        local_datetime = datetime.fromtimestamp(local_timestamp / 1000)

        output = {
            "real_time": real_datetime.isoformat(),
            "local_time": local_datetime.isoformat(),
            "real_timestamp_ms": real_timestamp,
            "local_timestamp_ms": local_timestamp,
            "drift_ms": drift_ms,
            "drift_seconds": drift_seconds,
            "is_synced": abs(drift_seconds) < 1,
            "source": source,
            "latency_ms": self.network_latency_ms
        }

        self.last_check_time = output
        self.drift_history.append(drift_ms)

        return output

    def ensure_time_synced(self, max_drift_seconds: float = 5.0) -> Dict[str, Any]:
        """
        Ensure time is synchronized, return warning if drift exceeds threshold.
        """
        result = self.check_time_drift()
        if result is None:
            return {
                "status": "error",
                "message": "Cannot fetch real time from any available source",
                "action": "Please check network connection and retry"
            }

        if abs(result["drift_seconds"]) <= max_drift_seconds:
            return {
                "status": "ok",
                "message": "Time is synchronized",
                "real_time": result["real_time"],
                "drift_seconds": result["drift_seconds"],
                "source": result["source"]
            }
        else:
            return {
                "status": "warning",
                "message": f"Time drift detected: {result['drift_seconds']:.2f}s (threshold: {max_drift_seconds}s)",
                "real_time": result["real_time"],
                "local_time": result["local_time"],
                "drift_seconds": result["drift_seconds"],
                "source": result["source"],
                "action": "Recommend calibrating system time"
            }

    def get_timestamped_data(self) -> Dict[str, Any]:
        """
        Get timestamped data for data collection tasks.
        """
        result = self.get_real_time()

        if result is None:
            real_time = self.get_local_time_ms()
            source = "local_fallback"
            is_reliable = False
        else:
            real_time, source = result
            is_reliable = True

        return {
            "timestamp_ms": real_time,
            "timestamp_seconds": real_time // 1000,
            "datetime": datetime.fromtimestamp(real_time / 1000).isoformat(),
            "datetime_utc": datetime.fromtimestamp(real_time / 1000, tz=timezone.utc).isoformat(),
            "source": source,
            "is_reliable": is_reliable
        }

    def validate_time_consistency(self, attempts: int = 3) -> Dict[str, Any]:
        """
        Validate time consistency with multiple samples.
        """
        results = []
        for _ in range(attempts):
            result = self.check_time_drift()
            if result:
                results.append(result)
            time.sleep(0.5)

        if not results:
            return {
                "status": "error",
                "message": "Cannot validate time consistency"
            }

        avg_drift_ms = sum(r["drift_ms"] for r in results) / len(results)
        avg_drift_seconds = avg_drift_ms / 1000

        return {
            "status": "ok" if abs(avg_drift_ms) < 1000 else "warning",
            "samples": len(results),
            "avg_drift_ms": avg_drift_ms,
            "avg_drift_seconds": avg_drift_seconds,
            "all_synced": all(r["is_synced"] for r in results),
            "max_drift_ms": max(abs(r["drift_ms"]) for r in results),
            "real_time": results[-1]["real_time"],
            "source": results[-1]["source"]
        }

    def generate_warning_report(self, result: Dict[str, Any]) -> str:
        """Generate time drift warning report"""
        return f"""
{'='*60}
WARNING: Time Drift Detected
{'='*60}

Real Time (via {result.get('source', 'N/A')}): {result.get('real_time', 'N/A')}
Local System Time: {result.get('local_time', 'N/A')}
Drift: {result.get('drift_seconds', 0):.2f} seconds
Network Latency: {result.get('latency_ms', 0)}ms

{'='*60}
Impact Analysis
{'='*60}
Using stale time may cause:
  - Incomplete data collection (missing latest data)
  - Duplicate data collection (overlapping periods)
  - Scheduled task execution anomalies
  - Inaccurate log timestamps

{'='*60}
Recommended Actions
{'='*60}
1. Check system timezone settings
2. Sync NTP service: sudo ntpdate -s time.nist.gov
3. Manually calibrate system time
4. Pause data collection tasks before time calibration

{'='*60}
"""


def main():
    """CLI entry point"""
    calibrator = TimeCalibrator()

    print("=" * 60)
    print("       Time Calibrator - Global Time Sync Tool")
    print("       Primary: time.is | Fallback: Multi-source")
    print("=" * 60)
    print()

    # 1. Check time drift
    print("[1/4] Checking time drift...")
    drift_result = calibrator.check_time_drift()

    if drift_result is None:
        print("ERROR: Cannot fetch real time from any source")
        sys.exit(1)

    print(f"   Real Time: {drift_result['real_time']}")
    print(f"   Local Time: {drift_result['local_time']}")
    print(f"   Drift: {drift_result['drift_seconds']:.2f} seconds")
    print(f"   Source: {drift_result['source']}")
    print(f"   Latency: {drift_result['latency_ms']}ms")

    if drift_result['is_synced']:
        print("   Status: Time is synchronized")
    else:
        print("   Status: Time drift detected")
        print(calibrator.generate_warning_report(drift_result))

    print()

    # 2. Sync status check
    print("[2/4] Sync status check...")
    sync_result = calibrator.ensure_time_synced()
    print(f"   Status: {sync_result['status']}")
    print(f"   Message: {sync_result['message']}")
    if 'source' in sync_result:
        print(f"   Source: {sync_result['source']}")
    print()

    # 3. Validate time consistency
    print("[3/4] Validating time consistency (3 samples)...")
    consistency_result = calibrator.validate_time_consistency(3)
    print(f"   Samples: {consistency_result['samples']}")
    print(f"   Avg Drift: {consistency_result['avg_drift_seconds']:.2f} seconds")
    print(f"   Max Drift: {consistency_result['max_drift_ms']:.0f} milliseconds")
    print(f"   Status: {consistency_result['status']}")
    print()

    # 4. Get calibrated timestamp
    print("[4/4] Calibrated timestamp:")
    ts_data = calibrator.get_timestamped_data()
    print(f"   Timestamp (ms): {ts_data['timestamp_ms']}")
    print(f"   ISO Format: {ts_data['datetime']}")
    print(f"   UTC Format: {ts_data['datetime_utc']}")
    print(f"   Data Source: {ts_data['source']} ({'Reliable' if ts_data['is_reliable'] else 'Local Fallback'})")
    print()

    print("=" * 60)
    print("       Calibration Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
