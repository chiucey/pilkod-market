---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 197a8f321474b2ed4e59087fb9acd79a
    PropagateID: 197a8f321474b2ed4e59087fb9acd79a
    ReservedCode1: 3045022100b77c299e948fa0ba0fae1f57080c6cc0ec664bd81b020eae79caa03918a07c3c0220405f9e82f2b9ac6dcb06338519d12c3cfd0acf0b476ae508bc59cbfc429fcd44
    ReservedCode2: 3045022042e54940fe81abb38062a212b59cf51184ad922faf8000157e767b42989c1def022100d465c4da6b5faaeea5d0b66973810928b16c32fb47789205efa0a7dfa5ef3185
description: 调用魔搭社区模型生成图片。当用户要求使用魔搭社区 API 生成图片、使用 ModelScope 的图片生成功能、或需要调用 AIGC 模型生成图像时使用。
name: modelscope-image-gen
---

# 魔搭社区图片生成技能

## 触发条件

当用户请求以下场景时自动触发：
- 使用魔搭社区 ModelScope API 生成图片
- 调用 AIGC 模型（如 Devilworld/YL_qwen2512）生成图像
- 需要通过异步方式生成图片并轮询任务状态

## API 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `model` | string | 是 | `Devilworld/YL_qwen2512` | ModelScope 模型 ID，如 `MAILAND/majicflus_v1` |
| `prompt` | string | 是 | - | 正向提示词，建议使用英文，最大长度 2000 字符 |
| `negative_prompt` | string | 否 | 空 | 负向提示词，如 `lowres, bad anatomy, bad hands` |
| `size` | string | 否 | `1024x1536` | 生成图像分辨率（竖版Portrait） |
| `seed` | int | 否 | 随机 | 随机种子，范围 [0, 2^31-1] |
| `steps` | int | 否 | 50 | 采样步数，范围 [1, 100] |
| `guidance` | float | 否 | 4.0 | 提示词引导系数，范围 [1.5, 20] |

**分辨率说明**：
- SD 系列：[64x64, 2048x2048]
- FLUX：[64x64, 1024x1024]
- Qwen-Image：[64x64, 1664x1664]
- Z-Image-Turbo：[512x512, 2048x2048]

## 工作流程

### 1. 验证环境

检查必要的 Python 包是否已安装：
```bash
pip install requests Pillow
```

### 2. 获取 API Token

提醒用户从 https://modelscope.cn/my/myaccesstoken 获取 ModelScope Access Token（格式：`ms-xxxxxxxxxxxx`）

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

# 构建请求参数（所有参数可选）
request_params = {
    "model": "Devilworld/YL_qwen2512",  # 默认模型，可更改
    "prompt": "A mysterious girl walking down the corridor",  # 必填
    # 以下为可选参数（更新后的默认值）
    # "negative_prompt": "lowres, bad anatomy",
    # "size": "1024x1536",          # 竖版Portrait
    # "seed": 12345,
    # "steps": 50,                  # 采样步数
    # "guidance": 4.0              # 引导系数
}

# 提交异步任务
response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps(request_params, ensure_ascii=False).encode('utf-8')
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
        image_url = data["output_images"][0]
        image = Image.open(BytesIO(requests.get(image_url).content))
        image.save("generated_image.jpg")
        print(f"图片已保存: generated_image.jpg")
        break
    elif data["task_status"] == "FAILED":
        print("生成失败")
        break
    elif data["task_status"] in ["PENDING", "PROCESSING"]:
        print(f"状态: {data['task_status']}, 等待中...")

    time.sleep(5)
```

### 5. 返回结果

向用户返回：
- 生成成功：图片文件路径 + 预览
- 生成失败：错误信息

## 参数收集

使用 GenUI 表单收集用户输入：

1. **ModelScope Token**：用户的 API Token
2. **模型选择**：选择 AIGC 模型（默认 Devilworld/YL_qwen2512）
3. **正向提示词**：图片描述（必填，建议英文）
4. **负向提示词**：不希望出现的元素（可选）
5. **分辨率**：图片大小（可选，默认 1024x1536 竖版Portrait）
6. **采样步数**：steps 参数（可选，默认 50）
7. **引导系数**：guidance 参数（可选，默认 4.0）
8. **随机种子**：seed 参数（可选）

## 常用模型推荐

| 模型 ID | 说明 | 推荐分辨率 |
|--------|------|----------|
| `Devilworld/YL_qwen2512` | 默认模型 | 1024x1536 |
| `MAILAND/majicflus_v1` | 魔幻风格模型 | 1024x1536 |
| `AI-ModelScope/stable-diffusion-xl-base-1.0` | SD XL | 1024x1024 |

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| Token 无效 | 提示用户检查 Token 权限和格式 |
| 网络超时 | 重试 3 次，每次间隔 5 秒 |
| 生成失败 | 显示错误信息，建议更换提示词 |
| 任务超时 | 等待超过 5 分钟则提示用户 |

## 依赖项

- Python 3.8+
- requests
- Pillow

## 参考文档

详细 API 文档：`references/model_api_reference.md`
