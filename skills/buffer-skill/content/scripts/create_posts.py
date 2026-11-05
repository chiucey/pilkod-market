#!/usr/bin/env python3
import subprocess
import json
import base64

API_KEY = "PJAEvErdDANBjKFerDhF81fQPa1-GcK3lneeP1-uJnq"
URL = "https://api.buffer.com"
DUE_AT = "2026-05-09T10:00:00.000Z"

TEXT = """🌸 生命的奇迹，从选择开始 🌸

宝乐惠 —— 专注试管代孕与全球医旅服务，为每一个渴望家庭的你，提供专业、安心、全链路的贴心服务。

✦ 资深医疗团队
✦ 全程一对一服务
✦ 全球顶级资源对接

愿每个家庭，都能圆梦。
📩 联系我们，了解更多"""

IMAGE_PATH = "/workspace/buffer_post_image.png"

channels = [
    ("Twitter", "69fed1bc5c4c051afa282701"),
    ("Facebook", "69fed2a95c4c051afa2829e0"),
    ("Instagram", "69fed3385c4c051afa282b64"),
]

with open(IMAGE_PATH, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

for name, channel_id in channels:
    payload = {
        "query": f''' mutation {{ createPost(input: {{ text: "{TEXT}", channelId: "{channel_id}", schedulingType: automatic, mode: customScheduled, dueAt: "{DUE_AT}", media: {{ data: "{image_data}", mimeType: "image/png" }} }}) {{ ... on PostActionSuccess {{ post {{ id text dueAt }} }} ... on MutationError {{ message }} }} }} '''
    }

    # 写入临时文件避免命令行过长
    payload_file = f"/tmp/buffer_payload_{name}.json"
    with open(payload_file, "w") as f:
        json.dump(payload, f)

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", URL,
         "-H", "Content-Type: application/json",
         "-H", f"Authorization: Bearer {API_KEY}",
         "--data", f"@{payload_file}"],
        capture_output=True, text=True
    )

    print(f"=== {name} ===")
    try:
        data = json.loads(result.stdout)
        if "errors" in data:
            print(f"❌ 错误: {data['errors']}")
        else:
            create_post = data.get("data", {}).get("createPost", {})
            if "post" in create_post:
                post = create_post["post"]
                print(f"✅ 成功！帖子ID: {post['id']}")
                print(f"   定时发布时间: {post['dueAt']}")
            elif "message" in create_post:
                print(f"❌ 发布失败: {create_post['message']}")
    except Exception as e:
        print(f"解析响应失败: {e}")
        print(f"原始响应前200字: {result.stdout[:200]}")
    print()
