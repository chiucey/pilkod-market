#!/usr/bin/env python3
"""
website-testing skill — Core Audit Script
Usage: python audit.py <url> [--output <path>]

Runs first-principles checks across 5 dimensions:
  1. Infrastructure & SSL
  2. Performance (TTFB, response size)
  3. SEO (meta tags, headings, alt attributes, sitemap, robots)
  4. Security headers
  5. Content integrity (placeholder text, broken links, email consistency)

Outputs a structured JSON report to stdout or --output file.
"""

import sys
import json
import time
import socket
import argparse
import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing deps. Run: sudo pip3 install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

PLACEHOLDER_PATTERNS = [
    r"lorem ipsum",
    r"dolor sit amet",
    r"consectetur adipiscing",
    r"placeholder text",
    r"sample text",
    r"your text here",
    r"coming soon",
    r"under construction",
]

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
]


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def check_infrastructure(url: str, session: requests.Session) -> dict:
    result = {"https_redirect": False, "www_redirect": False, "ssl_issuer": None,
              "tls_version": None, "ip_address": None, "cdn_detected": None,
              "http2": False, "issues": []}
    parsed = urlparse(url)
    domain = parsed.netloc.lstrip("www.")

    # DNS
    try:
        result["ip_address"] = socket.gethostbyname(parsed.netloc)
    except Exception:
        result["issues"].append("DNS resolution failed")

    # HTTP → HTTPS redirect
    try:
        r = session.get(f"http://{parsed.netloc}", allow_redirects=True, timeout=10)
        result["https_redirect"] = r.url.startswith("https://")
        if not result["https_redirect"]:
            result["issues"].append("HTTP does not redirect to HTTPS")
    except Exception:
        result["issues"].append("HTTP redirect check failed")

    # Main request
    try:
        t0 = time.time()
        r = session.get(url, timeout=15)
        result["response_time_s"] = round(time.time() - t0, 3)
        result["status_code"] = r.status_code

        # CDN detection
        server = r.headers.get("server", "").lower()
        via = r.headers.get("via", "").lower()
        cf = r.headers.get("cf-ray", "")
        if cf:
            result["cdn_detected"] = "Cloudflare"
        elif "cloudfront" in server or "cloudfront" in via:
            result["cdn_detected"] = "CloudFront"
        elif "fastly" in server or "fastly" in via:
            result["cdn_detected"] = "Fastly"

        # HTTP/2
        result["http2"] = r.raw.version == 20 if hasattr(r.raw, "version") else False

        # SSL issuer (from headers hint)
        result["ssl_issuer"] = r.headers.get("x-ssl-issuer") or "TLS (check manually)"
    except Exception as e:
        result["issues"].append(f"Main request failed: {e}")

    return result


def check_performance(url: str, session: requests.Session) -> dict:
    result = {"ttfb_s": None, "total_s": None, "html_size_kb": None,
              "css_count": 0, "js_count": 0, "img_count": 0, "issues": []}
    try:
        t0 = time.time()
        r = session.get(url, timeout=20, stream=True)
        ttfb = time.time() - t0
        content = r.content
        total = time.time() - t0

        result["ttfb_s"] = round(ttfb, 3)
        result["total_s"] = round(total, 3)
        result["html_size_kb"] = round(len(content) / 1024, 1)
        result["status_code"] = r.status_code

        if result["ttfb_s"] > 0.8:
            result["issues"].append(
                f"TTFB {result['ttfb_s']}s exceeds 0.8s benchmark — likely no HTML caching"
            )
        if result["html_size_kb"] > 100:
            result["issues"].append(
                f"HTML size {result['html_size_kb']} KB exceeds 100 KB — check inline CSS from page builders"
            )

        soup = BeautifulSoup(content, "html.parser")
        result["css_count"] = len(soup.find_all("link", rel=lambda v: v and "stylesheet" in v))
        result["js_count"] = len(soup.find_all("script", src=True))
        result["img_count"] = len(soup.find_all("img"))

        if result["css_count"] > 10:
            result["issues"].append(f"{result['css_count']} CSS files — merge/minify recommended")
        if result["js_count"] > 10:
            result["issues"].append(f"{result['js_count']} JS files — merge/minify recommended")
    except Exception as e:
        result["issues"].append(f"Performance check failed: {e}")
    return result


def check_seo(url: str, session: requests.Session) -> dict:
    result = {"title": None, "meta_description": None, "h1_count": 0,
              "img_missing_alt": 0, "img_total": 0, "og_tags": False,
              "twitter_card": False, "canonical": None, "lang": None,
              "sitemap_found": False, "robots_found": False,
              "schema_org": False, "issues": []}
    try:
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")

        # Title
        t = soup.find("title")
        result["title"] = t.get_text(strip=True) if t else None
        if not result["title"]:
            result["issues"].append("CRITICAL: Missing <title> tag")

        # Meta description
        md = soup.find("meta", attrs={"name": "description"})
        result["meta_description"] = md["content"] if md and md.get("content") else None
        if not result["meta_description"]:
            result["issues"].append("CRITICAL: Missing meta description — hurts CTR in search results")

        # H1
        h1s = soup.find_all("h1")
        result["h1_count"] = len(h1s)
        if result["h1_count"] == 0:
            result["issues"].append("CRITICAL: No H1 tag — search engines cannot determine page topic")
        elif result["h1_count"] > 1:
            result["issues"].append(f"WARNING: {result['h1_count']} H1 tags — should have exactly one")

        # Images alt
        imgs = soup.find_all("img")
        result["img_total"] = len(imgs)
        missing_alt = [i for i in imgs if not i.get("alt")]
        result["img_missing_alt"] = len(missing_alt)
        if result["img_missing_alt"] > 0:
            result["issues"].append(
                f"HIGH: {result['img_missing_alt']}/{result['img_total']} images missing alt attribute"
            )

        # OG tags
        og = soup.find("meta", property="og:title") or soup.find("meta", attrs={"property": "og:title"})
        result["og_tags"] = og is not None
        if not result["og_tags"]:
            result["issues"].append("HIGH: Missing Open Graph tags — poor social media sharing")

        # Twitter card
        tc = soup.find("meta", attrs={"name": "twitter:card"})
        result["twitter_card"] = tc is not None

        # Canonical
        canon = soup.find("link", rel="canonical")
        result["canonical"] = canon["href"] if canon and canon.get("href") else None

        # Lang
        html_tag = soup.find("html")
        result["lang"] = html_tag.get("lang") if html_tag else None

        # Schema.org
        schemas = soup.find_all("script", type="application/ld+json")
        result["schema_org"] = len(schemas) > 0
        if not result["schema_org"]:
            result["issues"].append("MEDIUM: No Schema.org JSON-LD — missing rich snippets opportunity")

        # Sitemap
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        for path in ["/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml"]:
            try:
                sr = session.get(base + path, timeout=8)
                if sr.status_code == 200 and ("xml" in sr.headers.get("content-type", "") or "<urlset" in sr.text[:200] or "<sitemapindex" in sr.text[:200]):
                    result["sitemap_found"] = True
                    result["sitemap_url"] = base + path
                    break
            except Exception:
                pass
        if not result["sitemap_found"]:
            result["issues"].append("MEDIUM: No sitemap.xml found")

        # Robots.txt
        try:
            rr = session.get(base + "/robots.txt", timeout=8)
            result["robots_found"] = rr.status_code == 200 and "User-agent" in rr.text
            if not result["robots_found"]:
                result["issues"].append("MEDIUM: No valid robots.txt")
        except Exception:
            result["issues"].append("MEDIUM: robots.txt check failed")

    except Exception as e:
        result["issues"].append(f"SEO check failed: {e}")
    return result


def check_security(url: str, session: requests.Session) -> dict:
    result = {"headers_present": {}, "headers_missing": [], "issues": []}
    try:
        r = session.get(url, timeout=15)
        resp_headers_lower = {k.lower(): v for k, v in r.headers.items()}
        for h in SECURITY_HEADERS:
            if h in resp_headers_lower:
                result["headers_present"][h] = resp_headers_lower[h]
            else:
                result["headers_missing"].append(h)
                severity = "CRITICAL" if h in ("content-security-policy", "strict-transport-security") else "HIGH"
                result["issues"].append(f"{severity}: Missing {h}")
    except Exception as e:
        result["issues"].append(f"Security check failed: {e}")
    return result


def check_content(url: str, session: requests.Session) -> dict:
    result = {"placeholder_found": [], "broken_links": [], "emails_found": [], "issues": []}
    try:
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        # Placeholder detection
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                result["placeholder_found"].append(pattern)
        if result["placeholder_found"]:
            result["issues"].append(
                f"CRITICAL: Placeholder text found ({len(result['placeholder_found'])} patterns) — unprofessional"
            )

        # Email extraction (consistency check)
        emails = list(set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", r.text)))
        result["emails_found"] = emails
        if len(emails) > 1:
            result["issues"].append(
                f"WARNING: Multiple email addresses found ({emails}) — check consistency"
            )

        # Broken link sampling (first 20 internal links)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        links = [a["href"] for a in soup.find_all("a", href=True)]
        internal = []
        for lnk in links:
            if lnk.startswith("/") and not lnk.startswith("//"):
                internal.append(base + lnk)
            elif lnk.startswith(base):
                internal.append(lnk)
        seen = set()
        checked = 0
        for lnk in internal:
            if lnk in seen or checked >= 20:
                break
            seen.add(lnk)
            try:
                lr = session.head(lnk, timeout=8, allow_redirects=True)
                if lr.status_code in (403, 404, 410, 500):
                    result["broken_links"].append({"url": lnk, "status": lr.status_code})
            except Exception:
                result["broken_links"].append({"url": lnk, "status": "timeout"})
            checked += 1
        if result["broken_links"]:
            result["issues"].append(
                f"HIGH: {len(result['broken_links'])} broken/forbidden links found"
            )
    except Exception as e:
        result["issues"].append(f"Content check failed: {e}")
    return result


def score(checks: dict) -> int:
    """Compute 0-100 score from issue counts across all dimensions."""
    all_issues = []
    for v in checks.values():
        if isinstance(v, dict):
            all_issues.extend(v.get("issues", []))
    critical = sum(1 for i in all_issues if i.startswith("CRITICAL"))
    high     = sum(1 for i in all_issues if i.startswith("HIGH"))
    medium   = sum(1 for i in all_issues if i.startswith("MEDIUM"))
    warning  = sum(1 for i in all_issues if i.startswith("WARNING"))
    deductions = critical * 12 + high * 6 + medium * 3 + warning * 1
    return max(0, 100 - deductions)


def main():
    parser = argparse.ArgumentParser(description="First-principles website audit")
    parser.add_argument("url", help="Target URL (e.g. https://example.com)")
    parser.add_argument("--output", help="Write JSON report to this file path")
    args = parser.parse_args()

    url = normalize_url(args.url)
    print(f"[website-testing] Testing: {url}", file=sys.stderr)

    session = requests.Session()
    session.headers.update(HEADERS)

    report = {
        "url": url,
        "test_date": datetime.now(timezone.utc).isoformat(),
        "infrastructure": check_infrastructure(url, session),
        "performance": check_performance(url, session),
        "seo": check_seo(url, session),
        "security": check_security(url, session),
        "content": check_content(url, session),
    }
    report["overall_score"] = score(report)

    # Summary
    all_issues = []
    for dim in ("infrastructure", "performance", "seo", "security", "content"):
        for issue in report[dim].get("issues", []):
            all_issues.append({"dimension": dim, "issue": issue})
    report["all_issues"] = all_issues
    report["issue_counts"] = {
        "critical": sum(1 for i in all_issues if i["issue"].startswith("CRITICAL")),
        "high":     sum(1 for i in all_issues if i["issue"].startswith("HIGH")),
        "medium":   sum(1 for i in all_issues if i["issue"].startswith("MEDIUM")),
        "warning":  sum(1 for i in all_issues if i["issue"].startswith("WARNING")),
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[website-testing] Report saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
