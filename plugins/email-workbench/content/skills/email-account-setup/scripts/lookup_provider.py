#!/usr/bin/env python3
"""Look up built-in provider steps and constraints without accepting credentials."""

import argparse
import json
from pathlib import Path
import re


CATALOG = Path(__file__).resolve().parents[1] / "references" / "providers.json"


def normalize_domain(value):
    value = value.strip().lower()
    if any(char in value for char in "@/:?#\\"):
        raise ValueError("仅传入邮箱域名，例如 qq.com；不要传入地址、URL 或凭据。")
    try:
        domain = value.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("无法解析邮箱域名。") from exc
    labels = domain.split(".")
    pattern = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    if len(domain) > 253 or len(labels) < 2 or not all(
        re.fullmatch(pattern, label) for label in labels
    ):
        raise ValueError("域名格式无效，请核对拼写。")
    return domain


def lookup_domain(catalog, domain):
    for provider in catalog["providers"]:
        if domain in provider["domains"]:
            return {
                "status": "matched",
                "domain": domain,
                "provider": provider,
                "nextAction": "先阅读内置 steps、prerequisites、missingEntryHelp、credentialLifecycle 和 stopConditions；按 credentialSurface 导航，部分核实或现场不符时再查官方来源。",
            }
    for entry in catalog["recognizedButUnsupportedInWorkbench"]:
        if domain in entry["domains"]:
            return {
                "status": "unsupported_in_snapshot",
                "domain": domain,
                "snapshotDate": catalog["snapshotDate"],
                **entry,
                "nextAction": entry.get("nextAction", "检查目标产品当前认证能力；未支持前不要生成或索取授权码。"),
            }
    return {
        "status": "unknown",
        "domain": domain,
        "nextAction": "核对拼写或由用户确认实际托管商。未知域名不代表地址错误；不要猜服务器或套用相近域名。",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--domain", help="邮箱域名，不含 @ 或用户名")
    group.add_argument("--provider", help="用户已确认的 providerId")
    group.add_argument("--list", action="store_true", help="列出快照中的服务商")
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if args.list:
        result = {
            "snapshotDate": catalog["snapshotDate"],
            "providers": [
                {key: provider[key] for key in ("id", "name", "domains", "selection", "evidence", "credentialSurface", "verificationStatus")}
                for provider in catalog["providers"]
            ],
        }
    elif args.provider is not None:
        match = next((p for p in catalog["providers"] if p["id"] == args.provider), None)
        if match is None:
            print(json.dumps({"status": "invalid_provider", "message": "使用 --list 查看有效的 providerId。"}, ensure_ascii=False))
            return 2
        result = {
            "status": "selected",
            "provider": match,
            "nextAction": "此结果基于指定服务商，不是自定义域名托管证明。先阅读内置步骤和约束，按 credentialSurface 操作；部分核实或现场不符时再查官方来源。",
        }
    else:
        try:
            domain = normalize_domain(args.domain)
        except ValueError as exc:
            # Do not echo untrusted input; it might have contained a credential.
            print(json.dumps({"status": "invalid_domain", "message": str(exc)}, ensure_ascii=False))
            return 2
        result = lookup_domain(catalog, domain)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
