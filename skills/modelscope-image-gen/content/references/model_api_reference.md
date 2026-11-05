# ModelScope 图片生成 API 参考

## API 端点

**基础 URL**: `https://api-inference.modelscope.cn/`

## 端点

### 1. 提交图片生成任务

**端点**: `POST https://api-inference.modelscope.cn/v1/images/generations`

**请求头**:
```python
{
    "Authorization": "Bearer <API_TOKEN>",
    "Content-Type": "application/json",
    "X-ModelScope-Async-Mode": "true"  # 异步模式
}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `model` | string | 是 | `Devilworld/YL_qwen2512` | ModelScope 模型 ID |
| `prompt` | string | 是 | - | 正向提示词，建议英文，最大 2000 字符 |
| `negative_prompt` | string | 否 | 空 | 负向提示词 |
| `size` | string | 否 | `1024x1536` | 分辨率，如 `1024x1536`（竖版Portrait） |
| `seed` | int | 否 | 随机 | 随机种子 [0, 2147483647] |
| `steps` | int | 否 | 50 | 采样步数 [1, 100] |
| `guidance` | float | 否 | 4.0 | 引导系数 [1.5, 20] |

**分辨率范围**:
- SD 系列：[64x64, 2048x2048]
- FLUX：[64x64, 1024x1024]
- Qwen-Image：[64x64, 1664x1664]
- Z-Image-Turbo：[512x512, 2048x2048]

**请求示例**:
```json
{
    "model": "Devilworld/YL_qwen2512",
    "prompt": "A mysterious girl walking down the corridor",
    "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers",
    "size": "1024x1536",
    "seed": 12345,
    "steps": 50,
    "guidance": 4.0
}
```

**响应**:
```json
{
    "task_id": "abc123xyz"
}
```

### 2. 查询任务状态

**端点**: `GET https://api-inference.modelscope.cn/v1/tasks/{task_id}`

**请求头**:
```python
{
    "Authorization": "Bearer <API_TOKEN>",
    "X-ModelScope-Task-Type": "image_generation"
}
```

**响应状态**:

| 状态 | 含义 |
|-----|------|
| `PENDING` | 任务等待中 |
| `PROCESSING` | 正在生成 |
| `SUCCEED` | 生成成功 |
| `FAILED` | 生成失败 |

**成功响应**:
```json
{
    "task_id": "abc123xyz",
    "task_status": "SUCCEED",
    "output_images": ["https://cdn.modelscope.cn/xxx.jpg"]
}
```

## 常用模型

| 模型 ID | 说明 | 推荐分辨率 |
|--------|------|----------|
| `Devilworld/YL_qwen2512` | 默认模型 | 1024x1536 |
| `MAILAND/majicflus_v1` | 魔幻风格模型 | 1024x1536 |
| `AI-ModelScope/stable-diffusion-xl-base-1.0` | SD XL | 1024x1024 |
| `FLUX` 系列 | FLUX 模型 | 最大 1024x1024 |
| `Qwen-Image` 系列 | 通义图像模型 | 最大 1664x1664 |

## 获取 API Token (Access Token)

1. 访问 https://modelscope.cn/my/myaccesstoken
2. 点击"创建 Access Token"
3. 选择适当的权限范围
4. 复制生成的 Token（格式为 `ms-xxxxxxxxxxxx`）

**注意**：必须先完成阿里云账号绑定才能获取 Token

## Python SDK 方式（替代方案）

```python
from modelscope import snapshot_download

# 下载模型到本地
model_dir = snapshot_download('Devilworld/YL_qwen2512')
```

## 完整示例代码

```python
import requests
import json
import time
from PIL import Image
from io import BytesIO

def generate_image(
    api_token: str,
    model: str = "Devilworld/YL_qwen2512",
    prompt: str = "A beautiful landscape",
    negative_prompt: str = "",
    size: str = "1024x1536",
    seed: int = None,
    steps: int = 50,
    guidance: float = 4.0
) -> str:
    """
    使用 ModelScope API 生成图片

    Args:
        api_token: ModelScope Access Token
        model: 模型 ID
        prompt: 正向提示词
        negative_prompt: 负向提示词
        size: 分辨率
        seed: 随机种子
        steps: 采样步数
        guidance: 引导系数

    Returns:
        生成图片的路径
    """
    base_url = "https://api-inference.modelscope.cn/"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    # 构建请求参数
    request_params = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "steps": steps,
        "guidance": guidance
    }

    # 添加可选参数
    if negative_prompt:
        request_params["negative_prompt"] = negative_prompt
    if seed is not None:
        request_params["seed"] = seed

    # 提交异步任务
    response = requests.post(
        f"{base_url}v1/images/generations",
        headers={**headers, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps(request_params, ensure_ascii=False).encode('utf-8')
    )
    response.raise_for_status()
    task_id = response.json()["task_id"]

    print(f"任务已提交，Task ID: {task_id}")

    # 轮询任务状态
    while True:
        result = requests.get(
            f"{base_url}v1/tasks/{task_id}",
            headers={**headers, "X-ModelScope-Task-Type": "image_generation"},
        )
        result.raise_for_status()
        data = result.json()

        status = data.get("task_status")
        print(f"当前状态: {status}")

        if status == "SUCCEED":
            # 下载图片
            image_url = data["output_images"][0]
            image = Image.open(BytesIO(requests.get(image_url).content))
            output_path = f"generated_{task_id}.jpg"
            image.save(output_path)
            print(f"图片已保存: {output_path}")
            return output_path
        elif status == "FAILED":
            raise Exception(f"生成失败: {data.get('error', '未知错误')}")

        time.sleep(5)

# 使用示例
if __name__ == "__main__":
    API_TOKEN = "your_token_here"

    result = generate_image(
        api_token=API_TOKEN,
        model="Devilworld/YL_qwen2512",
        prompt="A mysterious girl walking down the corridor",
        negative_prompt="lowres, bad anatomy, bad hands",
        size="1024x1536"
    )
    print(f"生成完成: {result}")
```

## 限制说明

- 免费用户有 API 调用频率限制
- 图片生成通常需要 10-60 秒
- 建议使用英文提示词获得最佳效果
- 不同模型支持的分辨率范围不同
