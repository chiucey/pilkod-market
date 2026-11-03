#!/usr/bin/env python3
"""
百度网盘 OAuth2.0 授权 URL 生成脚本
用法: python3 baidu_auth.py <API_KEY> <SECRET_KEY> [REDIRECT_URI]
"""
import sys
import urllib.parse

def gen_auth_url(api_key, secret_key, redirect_uri="oob", scope="netdisk"):
    params = {
        "client_id": api_key,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    url = "https://openapi.baidu.com/oauth/2.0/authorize?" + urllib.parse.urlencode(params)
    return url

def exchange_code_for_token(code, api_key, secret_key, redirect_uri="oob"):
    import urllib.request
    import urllib.parse
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": api_key,
        "client_secret": secret_key,
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        "https://openapi.baidu.com/oauth/2.0/token",
        data=data,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        import json
        return json.loads(resp.read().decode())

def refresh_token(refresh_token, api_key, secret_key):
    import urllib.request
    import urllib.parse
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": api_key,
        "client_secret": secret_key,
    }).encode()
    req = urllib.request.Request(
        "https://openapi.baidu.com/oauth/2.0/token",
        data=data,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        import json
        return json.loads(resp.read().decode())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 baidu_auth.py <API_KEY> <SECRET_KEY>")
        sys.exit(1)

    api_key = sys.argv[1]
    secret_key = sys.argv[2]

    url = gen_auth_url(api_key, secret_key)
    print("=" * 50)
    print("请访问以下 URL 完成授权：")
    print(url)
    print("=" * 50)
    code = input("粘贴 Authorization Code: ").strip()
    print("\n正在交换 Token...\n")
    result = exchange_code_for_token(code, api_key, secret_key)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
