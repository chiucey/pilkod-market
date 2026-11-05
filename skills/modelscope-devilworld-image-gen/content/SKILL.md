---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 39b515a604e50b8e15330a855b910e67
    PropagateID: 39b515a604e50b8e15330a855b910e67
    ReservedCode1: 304502202c46fdca28732d7ecd08ccd1b595683fe65dbbb97cc72ef2b889f8274d6efe5e022100834ec0b183031087f649d1a0b64d590ce4a1a2cece02fd750e4be37815cc266c
    ReservedCode2: 304402205238040a59140f1c5161594b84311564d409446e2105182f997026122d7a3a7d02202b3908ab898b5b9768ffa18649c7304bb526c1db41e6ed420b308afbb5fde8f5
description: 调用魔搭社区 Devilworld/YL_qwen2512 模型生成图片。当用户要求使用魔搭社区 API 生成图片、使用 ModelScope 的图片生成功能、或需要调用 Devilworld 模型生成图像时使用。
name: modelscope-devilworld-image-gen
---

# 魔搭社区图片生成技能

## 触发条件

当用户请求以下场景时自动触发：
- 使用魔搭社区 ModelScope API 生成图片
- 调用 Devilworld/YL_qwen2512 模型生成图像
- 需要通过异步方式生成图片并轮询任务状态

## 工作流程

### 1. 验证环境

检查必要的 Python 包是否已安装：
```bash
pip install requests Pillow
```

### 2. 获取 API Token

提醒用户从 https://modelscope.cn/my/settings/tokens 获取 ModelScope API Token

### 3. 构建 API 请求

使用异步模式提交图片生成任务：

```python
import requests
import json
import time
from PIL import Image
from io import BytesIO

base_url = "https://api-inference.modelscope.cn/"
api_key = "<USER_API_KEY>"  # 用户提供的 Token

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# 提交异步任务
response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps({
        "model": "Devilworld/YL_qwen2512",
        "prompt": "<USER_PROMPT>"  # 用户提供的提示词
    }, ensure_ascii=False).encode('utf-8')
)

task_id = response.json()["task_id"]
```

### 4. 轮询任务状态

持续检查任务状态直到完成或失败：

```python
while True:
    result = requests.get(
        f"{base_url}v1/tasks/{task_id}",
        headers={**headers, "X-ModelScope-Task-Type": "image_generation"},
    )
    data = result.json()

    if data["task_status"] == "SUCCEED":
        # 下载并保存图片
        image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
        image.save("generated_image.jpg")
        break
    elif data["task_status"] == "FAILED":
        print("生成失败")
        break

    time.sleep(5)
```

### 5. 返回结果

向用户返回：
- 生成成功：图片文件路径 + 预览
- 生成失败：错误信息

## 参数收集

使用 GenUI 表单收集用户输入：

1. **ModelScope Token**：用户的 API Token
2. **图片描述**：英文提示词（如 "A golden cat"）
3. **输出文件名**：保存的图片文件名（可选，默认 `generated_image.jpg`）

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| Token 无效 | 提示用户检查 Token 权限 |
| 网络超时 | 重试 3 次，每次间隔 5 秒 |
| 生成失败 | 显示错误信息，建议更换提示词 |
| 任务超时 | 等待超过 5 分钟则提示用户 |

## 依赖项

- Python 3.8+
- requests
- Pillow

## 参考文档

详细 API 文档：`references/model_api_reference.md`
