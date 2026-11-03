# AI API 配置教程

## 支持的AI图像生成API

### 1. Midjourney API

**获取API Key:**
1. 访问 [Midjourney API](https://www.midjourney.com/)
2. 注册/登录账号
3. 进入Dashboard获取API Key

**配置方式:**
```python
from scripts.main import GameArtGenerator

generator = GameArtGenerator(
    midjourney_key="your_midjourney_api_key"
)
```

**推荐使用场景:**
- 游戏图标（高细节、高品质）
- 角色立绘（精美、艺术感强）
- 特殊道具（复杂设计）

### 2. Stable Diffusion API

**获取API Key:**
1. 访问 [Stability AI](https://stability.ai/)
2. 注册/登录DreamStudio
3. 获取API Key

**配置方式:**
```python
from scripts.main import GameArtGenerator

generator = GameArtGenerator(
    stable_diffusion_key="your_sd_api_key"
)
```

**推荐使用场景:**
- 背景图（效率高、支持大尺寸）
- UI组件（足够清晰、生成快）
- 简单道具

### 3. 双API配置（推荐）

```python
generator = GameArtGenerator(
    midjourney_key="your_mj_key",
    stable_diffusion_key="your_sd_key"
)
```

系统会自动根据素材类型选择最优API。

## API密钥安全存储

### 环境变量方式

```bash
# Linux/macOS
export MIDJOURNEY_KEY="your_key"
export SD_KEY="your_key"

# Windows
set MIDJOURNEY_KEY=your_key
set SD_KEY=your_key
```

### 配置文件方式

创建 `config/api_keys.json`:
```json
{
    "midjourney_key": "your_mj_key",
    "stable_diffusion_key": "your_sd_key"
}
```

## API调用优化

### 1. 素材类型自动选择

| 素材类型 | 推荐API | 原因 |
|---------|---------|------|
| 游戏图标 | Midjourney | 高细节、高品质 |
| 角色 | Midjourney | 艺术感强 |
| 道具 | SD/MJ都行 | 复杂度适中 |
| 背景 | Stable Diffusion | 支持大尺寸 |
| UI | Stable Diffusion | 效率高 |

### 2. 请求重试机制

内置自动重试，支持：
- 429限流自动等待重试
- 网络错误自动重试
- 超时自动重试

### 3. 批量生成优化

```python
# 批量生成时添加延迟避免限流
generator.image_generator.generate_batch(
    asset_list=[...],
    output_dir="./output",
    on_progress=lambda i, total, result: print(f"{i}/{total}")
)
```

## 成本优化建议

1. **角色图标用MJ，背景用SD**
2. **UI组件先生成低分辨率确认效果**
3. **批量生成使用SD提高效率**
4. **缓存已生成的素材避免重复调用**

## 常见问题

**Q: API调用失败怎么办？**
A: 系统会自动重试3次，如仍失败会使用备用API

**Q: 如何提高生成成功率？**
A: 使用详细prompt、避免歧义词、添加风格标签

**Q: 如何控制成本？**
A: 配置双API，根据素材类型自动选择性价比最高的API
