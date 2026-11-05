# ModelScope 图片生成 API 参考

## API 端点

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

**请求体**:
```json
{
    "model": "Devilworld/YL_qwen2512",
    "prompt": "A golden cat",
    "negative_prompt": "",  // 可选，负面提示词
    "width": 1024,          // 可选，图片宽度
    "height": 1024,         // 可选，图片高度
    "num_inference_steps": 20,  // 可选，推理步数
    "guidance_scale": 7.5       // 可选，引导强度
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

| 模型 ID | 说明 |
|--------|------|
| `Devilworld/YL_qwen2512` | 本技能使用的主力模型 |
| `AI-ModelScope/stable-diffusion-xl-base-1.0` | Stable Diffusion XL |

## 获取 API Token

1. 访问 https://modelscope.cn/my/settings/tokens
2. 点击"创建 Token"
3. 选择适当的权限范围
4. 复制生成的 Token

## Python SDK 方式（替代方案）

```python
from modelscope import snapshot_download

# 下载模型到本地
model_dir = snapshot_download('Devilworld/YL_qwen2512')
```

## 限制说明

- 免费用户有 API 调用频率限制
- 图片生成通常需要 10-60 秒
- 建议使用英文提示词获得最佳效果
