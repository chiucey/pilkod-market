#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from urllib import request, error


def get_tenant_access_token(base_url: str, app_id: str, app_secret: str) -> str:
    url = f"{base_url}/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("code") != 0:
        raise RuntimeError(f"token error: {body}")
    token = body.get("tenant_access_token")
    if not token:
        raise RuntimeError("missing tenant_access_token in response")
    return token


def api_request(method: str, url: str, token: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"http {e.code}: {raw}") from e


def build_children(lines: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    children: List[Dict[str, Any]] = []
    for kind, text in lines:
        if kind == "heading1":
            children.append({"block_type": 3, "heading1": {"elements": [{"text_run": {"content": text}}]}})
        else:
            children.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": text}}]}})
    return children


def parse_text_to_lines(text: str) -> List[Tuple[str, str]]:
    raw_lines = [line.rstrip() for line in text.splitlines()]
    lines = [line for line in raw_lines if line.strip()]
    if not lines:
        raise RuntimeError("content is empty after stripping blank lines")
    result: List[Tuple[str, str]] = [("heading1", lines[0])]
    for line in lines[1:]:
        result.append(("text", line))
    return result


def load_content(args: argparse.Namespace) -> List[Tuple[str, str]]:
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return parse_text_to_lines(f.read())
    if args.content:
        return parse_text_to_lines(args.content)
    raise RuntimeError("set requires one of: --preset bot-intro, --file, or --content")


def get_meta(base_url: str, token: str, chat_id: str) -> Dict[str, Any]:
    return api_request("GET", f"{base_url}/open-apis/docx/v1/chats/{chat_id}/announcement", token)


def list_blocks(base_url: str, token: str, chat_id: str) -> Dict[str, Any]:
    return api_request("GET", f"{base_url}/open-apis/docx/v1/chats/{chat_id}/announcement/blocks", token)


def list_children(base_url: str, token: str, chat_id: str, block_id: str) -> Dict[str, Any]:
    return api_request("GET", f"{base_url}/open-apis/docx/v1/chats/{chat_id}/announcement/blocks/{block_id}/children", token)


def delete_children(base_url: str, token: str, chat_id: str, root_block_id: str, child_ids: List[str]) -> Optional[Dict[str, Any]]:
    if not child_ids:
        return None
    body = {"children_ids": child_ids}
    return api_request(
        "DELETE",
        f"{base_url}/open-apis/docx/v1/chats/{chat_id}/announcement/blocks/{root_block_id}/children/batch_delete",
        token,
        body,
    )


def create_children(base_url: str, token: str, chat_id: str, root_block_id: str, lines: List[Tuple[str, str]]) -> Dict[str, Any]:
    body = {"children": build_children(lines), "index": 0}
    return api_request(
        "POST",
        f"{base_url}/open-apis/docx/v1/chats/{chat_id}/announcement/blocks/{root_block_id}/children",
        token,
        body,
    )


def set_announcement(base_url: str, token: str, chat_id: str, lines: List[Tuple[str, str]]) -> Dict[str, Any]:
    blocks = list_blocks(base_url, token, chat_id)
    items = blocks.get("data", {}).get("items", [])
    if not items:
        raise RuntimeError("no root announcement block found")
    root_block_id = items[0]["block_id"]
    children = list_children(base_url, token, chat_id, root_block_id)
    child_ids = [item["block_id"] for item in children.get("data", {}).get("items", [])]
    delete_res = delete_children(base_url, token, chat_id, root_block_id, child_ids)
    create_res = create_children(base_url, token, chat_id, root_block_id, lines)
    return {
        "delete_result": delete_res,
        "create_result": create_res,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Feishu DOCX chat announcements")
    parser.add_argument("action", choices=["get-meta", "list-blocks", "set"], help="Action")
    parser.add_argument("--chat-id", required=True, help="Feishu chat id, e.g. oc_xxx")
    parser.add_argument("--base-url", default=os.environ.get("FEISHU_BASE_URL", "https://open.feishu.cn"))
    parser.add_argument("--app-id", default=os.environ.get("FEISHU_APP_ID"))
    parser.add_argument("--app-secret", default=os.environ.get("FEISHU_APP_SECRET"))
    parser.add_argument("--content", help="Raw text content. First non-empty line becomes heading1, remaining lines become paragraphs.")
    parser.add_argument("--file", help="Read announcement text from a UTF-8 file")
    args = parser.parse_args()

    if not args.app_id or not args.app_secret:
        print("Missing FEISHU_APP_ID / FEISHU_APP_SECRET (or --app-id / --app-secret)", file=sys.stderr)
        return 2

    token = get_tenant_access_token(args.base_url, args.app_id, args.app_secret)

    if args.action == "get-meta":
        result = get_meta(args.base_url, token, args.chat_id)
    elif args.action == "list-blocks":
        result = list_blocks(args.base_url, token, args.chat_id)
    else:
        lines = load_content(args)
        result = set_announcement(args.base_url, token, args.chat_id, lines)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
