import argparse
import json
import os
import urllib.request


def build_message(args):
    """构建飞书富文本消息"""
    status_color = {
        "通过": "green",
        "不通过": "red",
        "材料待补充": "orange",
    }.get(args.status, "grey")

    content_blocks = [
        [{"tag": "text", "text": f"审核类别：{args.category}\n"}],
        [{"tag": "text", "text": f"HSK：{args.hsk}  "}],
        [{"tag": "text", "text": f"HSKK：{args.hskk}\n"}],
        [{"tag": "text", "text": f"\n{args.summary}"}],
    ]

    if args.nomination:
        content_blocks.append([
            {"tag": "text", "text": "\n"},
            {"tag": "text", "text": "我校将于近期给申请者邮箱发送海外学生在线提名邮件，请根据要求尽快填写提交为盼。"}
        ])

    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"【{args.status}】{args.student_name}",
                    "content": content_blocks,
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description="推送奖学金审核结果到飞书")
    parser.add_argument("--student-name", required=True, help="申请者姓名")
    parser.add_argument("--category", required=True, help="申请类别")
    parser.add_argument(
        "--status", required=True,
        choices=["通过", "不通过", "材料待补充"],
        help="审核状态"
    )
    parser.add_argument("--hsk", required=True, help="HSK成绩")
    parser.add_argument("--hskk", required=True, help="HSKK成绩")
    parser.add_argument("--summary", required=True, help="审核摘要/评语")
    parser.add_argument(
        "--nomination", action="store_true",
        help="是否需发送提名信提醒（一学期/一学年项目）"
    )
    args = parser.parse_args()

    skill_id = "7640355907481731124"
    token = os.getenv(f"COZE_FEISHU_WEBHOOK_{skill_id}")
    if not token:
        print(json.dumps(
            {"status": "error", "message": "缺少飞书Webhook凭证，请先配置"},
            ensure_ascii=False
        ))
        return

    url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{token}"
    message = build_message(args)

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(message, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        if data.get("code", 0) != 0:
            result = {
                "status": "error",
                "message": f"飞书API错误: {data.get('msg', '未知错误')}",
                "detail": data,
            }
        else:
            result = {
                "status": "success",
                "message": "推送成功",
                "student": args.student_name,
                "status": args.status,
            }
    except Exception as e:
        result = {"status": "error", "message": f"请求失败: {str(e)}"}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
