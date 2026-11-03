#!/usr/bin/env python3
"""
Buffer Skill - GraphQL API 调用脚本
API: https://api.buffer.com
Key: PJAEvErdDANBjKFerDhF81fQPa1-GcK3lneeP1-uJnq

用法:
  python3 buffer.py organizations                              # 获取组织列表
  python3 buffer.py channels <org_id>                         # 获取频道列表
  python3 buffer.py create <channel_id> <text> [due_at] [img_url]  # 创建帖子
  python3 buffer.py posts <org_id> [channel_id] [status]      # 查询帖子
  python3 buffer.py delete <post_id> <channel_id>             # 删除帖子
"""

import subprocess, json, sys

BUFFER_API_KEY = "PJAEvErdDANBjKFerDhF81fQPa1-GcK3lneeP1-uJnq"
BUFFER_API_URL = "https://api.buffer.com"

# ---------------------------------------------------------------------------
# 核心：发送 GraphQL 请求
# ---------------------------------------------------------------------------
def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    path = "/tmp/buffer_gql_req.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", BUFFER_API_URL,
         "-H", "Content-Type: application/json; charset=utf-8",
         "-H", "Authorization: Bearer " + BUFFER_API_KEY,
         "--data-binary", "@" + path],
        capture_output=True, text=True, encoding="utf-8"
    )
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# 操作层
# ---------------------------------------------------------------------------

def get_organizations():
    """获取组织列表"""
    d = gql('{ account { organizations { id name } } }')
    orgs = d.get("data", {}).get("account", {}).get("organizations", [])
    if not orgs:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return []
    for o in orgs:
        print("  ID: " + o["id"] + "  名称: " + o["name"])
    return orgs


def get_channels(org_id):
    """获取频道列表"""
    d = gql(
        'query($orgId: OrganizationId!) { channels(input: { organizationId: $orgId }) '
        '{ id name service } }',
        {"orgId": org_id}
    )
    channels = d.get("data", {}).get("channels", [])
    if not channels:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return []
    print("  " + "名称".ljust(30) + " 服务      ID")
    for c in channels:
        print("  " + c["name"].ljust(30) + " " + c["service"].ljust(10) + " " + c["id"])
    return channels


def create_post(channel_id, text, due_at=None, image_url=None):
    """
    创建帖子（支持文字 + 图片 URL）

    参数:
      channel_id  频道 ID
      text         帖文内容
      due_at       定时 UTC 时间（ISO 8601），None = addToQueue
      image_url    公开图片 URL（可选）

    返回: {"success": True, "post": {...}} 或 {"success": False, "message": "..."}
    """
    # GraphQL 字符串中换行符必须编码为 \n（而非真实换行）
    # 先将真实换行符替换为 \n 字符串，再转义引号
    text_for_gql = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    # 动态组装字段片段
    assets_part = (
        ', assets: { images: [{ url: "' + image_url + '" }] }'
        if image_url else ""
    )
    due_part = (
        ', dueAt: "' + due_at + '", mode: customScheduled'
        if due_at else ""
    )

    mutation = (
        "mutation { "
        "  createPost(input: { "
        "    text: \"" + text_for_gql + "\", "
        "    channelId: \"" + channel_id + "\", "
        "    schedulingType: automatic"
        + assets_part
        + due_part
        + " }) { "
        "    ... on PostActionSuccess { post { id text dueAt status } } "
        "    ... on MutationError { message } "
        "  } "
        "}"
    )

    d = gql(mutation)
    create_data = d.get("data", {}).get("createPost", {})

    if "post" in create_data:
        post = create_data["post"]
        return {
            "success": True,
            "post": {
                "id": post["id"],
                "dueAt": post.get("dueAt"),
                "status": post.get("status"),
            }
        }
    else:
        return {
            "success": False,
            "message": create_data.get("message", "未知错误"),
            "_raw": d,
        }


def get_posts(org_id, channel_id=None, status=None, first=20):
    """查询帖子"""
    parts = []
    if channel_id:
        parts.append('channelIds: ["' + channel_id + '"]')
    if status:
        parts.append('status: ["' + status + '"]')
    filter_clause = ("filter: { " + ", ".join(parts) + " }, ") if parts else ""

    query = (
        "query($orgId: OrganizationId!, $first: Int!) { "
        "  posts(first: $first, input: { "
        "    organizationId: $orgId, " + filter_clause
        + "  }) { "
        "    edges { node { id text dueAt channelId status } } "
        "    pageInfo { hasNextPage endCursor } "
        "  } "
        "}"
    )
    d = gql(query, {"orgId": org_id, "first": first})
    edges = d.get("data", {}).get("posts", {}).get("edges", [])
    if not edges:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return
    for e in edges:
        n = e["node"]
        print(
            "  " + n["id"]
            + "  " + str(n.get("status", "")).ljust(12)
            + "  " + str(n.get("dueAt", "")).ljust(30)
            + "  " + n.get("channelId", "")
        )
    return edges


def delete_post(post_id, channel_id):
    """删除帖子"""
    mutation = (
        "mutation { "
        "  deletePost(input: { postId: \"" + post_id + "\", channelId: \"" + channel_id + "\" }) { "
        "    ... on PostActionSuccess { success } "
        "    ... on MutationError { message } "
        "  } "
        "}"
    )
    d = gql(mutation)
    del_data = d.get("data", {}).get("deletePost", {})
    if del_data.get("success"):
        return {"success": True}
    return {"success": False, "message": del_data.get("message", "未知错误")}


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    argv = sys.argv
    cmd = argv[1] if len(argv) > 1 else "help"

    if cmd == "organizations":
        get_organizations()

    elif cmd == "channels" and len(argv) > 2:
        get_channels(argv[2])

    elif cmd == "create" and len(argv) > 3:
        channel_id = argv[2]
        text = argv[3]
        due_at = argv[4] if len(argv) > 4 else None
        image_url = argv[5] if len(argv) > 5 else None

        # Facebook / Instagram 频道 ID（供判断用）
        fb_ig_ids = [
            "69fed2a95c4c051afa2829e0",   # Facebook
            "69fed3385c4c051afa282b64",   # Instagram
        ]

        if channel_id in fb_ig_ids and image_url:
            print(
                "⚠️  注意: Facebook / Instagram 频道需手动在 Buffer 后台上传图片。\n"
                "   API 暂不支持自动发图到这两个平台。",
                file=sys.stderr
            )

        result = create_post(channel_id, text, due_at, image_url)
        if result["success"]:
            p = result["post"]
            due_str = p.get("dueAt") or "立即入队列"
            print(
                "✅ 成功! ID=" + p["id"]
                + " | 定时=" + str(due_str)
                + " | 状态=" + str(p.get("status", ""))
            )
        else:
            msg = result["message"]
            print("❌ 失败: " + msg, file=sys.stderr)
            if "require a type" in msg:
                print(
                    "   → Facebook / Instagram 必须设置 type 参数（post/story/reel），\n"
                    "     该参数未在 Buffer 公开 API 中开放，请到后台操作。",
                    file=sys.stderr
                )

    elif cmd == "posts" and len(argv) > 2:
        org_id = argv[2]
        channel_id = argv[3] if len(argv) > 3 else None
        status = argv[4] if len(argv) > 4 else None
        get_posts(org_id, channel_id, status)

    elif cmd == "delete" and len(argv) > 4:
        result = delete_post(argv[2], argv[3])
        if result["success"]:
            print("✅ 删除成功")
        else:
            print("❌ 删除失败: " + result["message"], file=sys.stderr)

    else:
        print(__doc__)
