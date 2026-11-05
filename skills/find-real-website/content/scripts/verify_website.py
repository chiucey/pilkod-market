#!/usr/bin/env python3
"""
官方网站验证脚本
用于验证搜索到的网站是否为真正的官方网站
"""

import sys
import re
import json
from typing import Dict, List, Tuple, Optional

# 可信的官方域名后缀
TRUSTED_TLDS = {'.com', '.cn', '.org', '.net', '.gov', '.edu', '.io', '.co'}

# 需要排除的域名模式
SUSPICIOUS_PATTERNS = [
    r'-download',
    r'-free',
    r'-crack',
    r'\.tk$',
    r'\.ml$',
    r'\.ga$',
    r'\.cf$',
    r'\.gq$',
    r'\.top$',
    r'\.win$',
    r'\.click$',
]

# 常见仿冒关键词
COUNTERFEIT_KEYWORDS = ['crack', 'serial', 'keygen', 'patch', 'torrent']


def extract_domain(url: str) -> Optional[str]:
    """从URL中提取域名"""
    match = re.search(r'https?://([^/]+)', url)
    return match.group(1) if match else None


def check_domain_suspicious(domain: str) -> Tuple[bool, str]:
    """检查域名是否可疑"""
    domain_lower = domain.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, domain_lower):
            return True, f"域名包含可疑模式: {pattern}"

    return False, ""


def analyze_domain_brand_match(domain: str, brand_name: str) -> float:
    """分析域名与品牌的匹配度 (0-1)"""
    domain_lower = domain.lower()
    brand_lower = brand_name.lower()

    # 移除常见后缀和前缀
    clean_domain = re.sub(r'\.(com|cn|org|net|io|co|gov|edu)', '', domain_lower)
    clean_domain = re.sub(r'^(www\.|m\.|mobile\.)', '', clean_domain)

    # 完全匹配
    if brand_lower in clean_domain:
        return 1.0

    # 部分匹配
    brand_chars = set(brand_lower.replace(' ', ''))
    domain_chars = set(clean_domain.replace(' ', '').replace('-', '').replace('_', ''))

    overlap = len(brand_chars & domain_chars)
    if overlap > 0:
        return overlap / len(brand_chars) * 0.8

    return 0.0


def get_tld_info(domain: str) -> Tuple[str, bool]:
    """获取域名后缀信息和可信度"""
    for tld in sorted(TRUSTED_TLDS, key=len, reverse=True):
        if domain.lower().endswith(tld):
            return tld, True

    return "", False


def verify_website(url: str, brand_name: str = "") -> Dict:
    """
    验证网站是否为官方网站

    返回格式:
    {
        "is_official": bool,
        "confidence": float,  # 0-100
        "reasons": List[str],
        "warnings": List[str]
    }
    """
    result = {
        "is_official": False,
        "confidence": 0,
        "reasons": [],
        "warnings": []
    }

    if not url:
        result["warnings"].append("URL为空")
        return result

    domain = extract_domain(url)
    if not domain:
        result["warnings"].append("无法提取域名")
        return result

    # 检查1: 域名可疑性
    is_suspicious, reason = check_domain_suspicious(domain)
    if is_suspicious:
        result["warnings"].append(f"可疑域名: {reason}")
        result["confidence"] = max(0, result["confidence"] - 30)

    # 检查2: 域名后缀可信度
    tld, is_trusted = get_tld_info(domain)
    if is_trusted:
        result["reasons"].append(f"使用可信域名后缀: {tld}")
        result["confidence"] += 20
    else:
        result["warnings"].append(f"域名后缀 {tld} 可信度较低")
        result["confidence"] -= 10

    # 检查3: 品牌匹配度
    if brand_name:
        match_score = analyze_domain_brand_match(domain, brand_name)
        if match_score >= 0.8:
            result["reasons"].append(f"域名与品牌名高度匹配 (相似度: {match_score:.0%})")
            result["confidence"] += 40
        elif match_score >= 0.4:
            result["reasons"].append(f"域名与品牌名部分匹配 (相似度: {match_score:.0%})")
            result["confidence"] += 20
        elif match_score > 0:
            result["reasons"].append(f"域名与品牌名有少量关联 (相似度: {match_score:.0%})")
            result["confidence"] += 10
        else:
            result["warnings"].append("域名与品牌名不匹配")

    # 检查4: HTTPS验证
    if url.startswith('https'):
        result["reasons"].append("使用HTTPS安全连接")
        result["confidence"] += 15
    else:
        result["warnings"].append("未使用HTTPS连接")

    # 检查5: 关键词检查
    domain_lower = domain.lower()
    for keyword in COUNTERFEIT_KEYWORDS:
        if keyword in domain_lower:
            result["warnings"].append(f"域名包含可疑关键词: {keyword}")
            result["confidence"] = max(0, result["confidence"] - 25)

    # 最终判定
    result["confidence"] = max(0, min(100, result["confidence"]))
    result["is_official"] = result["confidence"] >= 60 and len(result["warnings"]) <= 1

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python verify_website.py <URL> [品牌名]")
        print("示例: python verify_website.py https://nodejs.org nodejs")
        sys.exit(1)

    url = sys.argv[1]
    brand_name = sys.argv[2] if len(sys.argv) > 2 else ""

    result = verify_website(url, brand_name)

    print("\n" + "="*50)
    print(f"网站验证结果: {url}")
    if brand_name:
        print(f"品牌名: {brand_name}")
    print("="*50)

    print(f"\n可信度评分: {result['confidence']}/100")
    print(f"是否为官方网站: {'✅ 是' if result['is_official'] else '❌ 否'}")

    if result["reasons"]:
        print("\n✅ 可信依据:")
        for reason in result["reasons"]:
            print(f"   • {reason}")

    if result["warnings"]:
        print("\n⚠️ 风险提示:")
        for warning in result["warnings"]:
            print(f"   • {warning}")

    print()


if __name__ == "__main__":
    main()
