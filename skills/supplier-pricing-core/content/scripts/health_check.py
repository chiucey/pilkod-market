import json
import urllib.request


def main() -> int:
    url = "http://127.0.0.1:3001/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            if data.get("status") == "ok":
                print("OK: backend health is ok")
                return 0
            print(f"WARN: unexpected health payload: {data}")
            return 1
    except Exception as e:
        print(f"ERROR: health check failed: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

