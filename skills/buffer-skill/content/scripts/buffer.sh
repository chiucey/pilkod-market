#!/usr/bin/env bash
# Buffer Skill - 多账号版（自动读取 vault）
# 用法:
#   export BUFFER_VAULT_KEY='加密密钥'    # 只需设置一次
#
#   # 账号管理
#   python3 vault.py add <账号名> <API Key>   # 添加账号 + 自动注册 MCP
#   python3 vault.py list                       # 列出账号
#   python3 vault.py remove <账号名>            # 删除账号
#   python3 vault.py channels <账号名>            # 查看账号下的渠道
#
#   # 发布
#   buffer.sh post <账号名> <channel_id> <text> [due_at] [img_url]
#   buffer.sh post buffer1 69fed1bc... "文案" "2026-05-20T15:30:00.000Z" "https://..."
#   buffer.sh post buffer2 6a0a7b6d... "文案"
#
# 不需要传 API Key，脚本自动从 vault 解密读取

VAULT_SCRIPT="$(cd "$(dirname "$0")" && pwd)/vault.py"

# ---------------------------------------------------------------------------
# 从 vault 获取 API Key
# ---------------------------------------------------------------------------
get_key() {
    local account="$1"
    python3 "$VAULT_SCRIPT" get "$account" 2>/dev/null
}

# ---------------------------------------------------------------------------
# 从账号名 → MCP Server 名
# ---------------------------------------------------------------------------
to_server() {
    local account="$1"
    echo "buf_${account}"
}

# ---------------------------------------------------------------------------
# 解析 Buffer post 结果
# ---------------------------------------------------------------------------
parse_result() {
    python3 -c "
import sys, json
d = json.load(sys.stdin)
r = d.get('result', [])
if isinstance(r, list) and len(r):
    text = r[0].get('text', '{}')
    data = json.loads(text)
else:
    data = {}
p = data.get('data', {}).get('createPost', {})
if 'post' in p:
    p = p['post']
    print('SUCCESS ID=' + p['id'])
    print('TIME=' + p.get('dueAt', 'now'))
    print('STATUS=' + p.get('status', ''))
else:
    print('ERROR=' + p.get('message', 'unknown'))
"
}

# ---------------------------------------------------------------------------
# 发布
# ---------------------------------------------------------------------------
do_post() {
    local account="$1"; shift
    local cid="${1:-}"; shift
    local text="${1:-}"; shift
    local due="${1:-}"; shift
    local img="${1:-}"

    if [ -z "$cid" ]; then
        echo "用法: buffer post <账号名> <channel_id> <text> [due_at] [img_url]" >&2
        return 1
    fi

    api_key=$(get_key "$account")
    if [ -z "$api_key" ]; then
        echo "错误: 未找到账号 [$account]，请先添加: python3 vault.py add $account '<API Key>'" >&2
        return 1
    fi
    server=$(to_server "$account")

    # 排程模式
    [ -n "$due" ] && mode='"customScheduled"' || mode='"addToQueue"'

    # metadata（按 channel ID 匹配）
    meta='{}'
    case "$cid" in
        69fed2a95c4c051afa2829e0)  meta='{"facebook":{"type":"post"}}' ;;
        69fed3385c4c051afa282b64)  meta='{"instagram":{"type":"post","shouldShareToFeed":true}}' ;;
        6a0a7b6d090476fb992fc107)  meta='{"youtube":{"type":"video"}}' ;;
        6a0a7b9e090476fb992fc16e)  meta='{"threads":{}}' ;;
        6a0a7c85090476fb992fc392)  meta='{"bluesky":{}}' ;;
    esac

    # assets
    [ -n "$img" ] && assets="{\"images\":[{\"url\":\"$img\"}]}" || assets='null'

    # variables
    vars="{\"text\":\"$(echo "$text" | sed 's/"/\\"/g')\",\"channelId\":\"$cid\",\"schedulingType\":\"automatic\",\"mode\":$mode"
    [ -n "$due" ] && vars="$vars,\"dueAt\":\"$due\""
    [ "$assets" != "null" ] && vars="$vars,\"assets\":$assets"
    [ "$meta" != "{}" ] && vars="$vars,\"metadata\":$meta"
    vars="$vars}"

    args="{\"summary\":\"Create post\",\"mutation\":\"mutation CreatePost(\$input:CreatePostInput!){createPost(input:\$input){...on PostActionSuccess{post{id dueAt status}}...on MutationError{message}}},\"variables\":$vars}"

    echo "  [$account → $server] 发布到 channel $cid ..."
    result=$(npx -y mcporter@latest --root /root/.mcporter call "$server.execute_mutation" --args "$args" 2>/dev/null)
    parse_result <<< "$result"
}

# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
if [ "${1:-}" = "post" ]; then
    shift
    account="${1:-}"; shift
    do_post "$account" "$@"
else
    echo "Buffer Skill (多账号加密版)"
    echo ""
    echo "用法:"
    echo "  python3 vault.py add <账号名> <API Key>   # 添加账号 + 自动注册 MCP"
    echo "  python3 vault.py list                       # 列出账号"
    echo "  python3 vault.py remove <账号名>            # 删除账号"
    echo "  python3 vault.py channels <账号名>          # 查看渠道"
    echo "  buffer.sh post <账号名> <channel_id> <text> [due_at] [img_url]"
    echo ""
    export BUFFER_VAULT_KEY="${BUFFER_VAULT_KEY:-}"
    if [ -n "$BUFFER_VAULT_KEY" ]; then
        python3 "$VAULT_SCRIPT" list 2>/dev/null
    else
        echo "  BUFFER_VAULT_KEY 未设置，无法列出账号"
    fi
fi